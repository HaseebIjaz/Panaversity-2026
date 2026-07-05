#!/usr/bin/env python3
"""
analyze_statement.py

Reusable command-line script to analyze a JazzCash-style account statement CSV.

USAGE:
    python3 analyze_statement.py <input_csv> [--output report.html]

WHAT IT DOES (per brief):
  1. Inspects the file: row count, columns, date range.
  2. Applies edge-case filters:
       - Excludes any row where Money In or Money Out > 30,000 Rs.
       - Excludes rows whose description mentions "NADRA".
  3. Computes:
       - Spending patterns (category totals, monthly trend)
       - "Forgotten subscriptions": recurring same-description/similar-amount
         charges appearing in 3+ different calendar months.
       - Duplicate charges: two or more Money-Out rows with identical
         description AND identical amount within a 5-minute window.
       - "Midnight leaks": Money-Out transactions with a timestamp between
         00:00:00 and 05:59:59 (after-midnight spending, per the brief's rule).
  4. Prints verification numbers (manual-checkable):
       - Total donations to date
       - Biggest spending transaction (amount, date, time)
       - Smallest spending transaction (amount, date, time)
  5. Writes a one-page HTML report with a monthly trend chart (pure SVG,
     no external chart library needed), a category table, a duplicates list,
     and three flagged observations.
  6. Lists any row that could not be parsed, at the end.

NO DATA IS EMBEDDED IN THIS SCRIPT. Everything is read from the CSV passed
on the command line.
"""

import argparse
import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter

MIDNIGHT_START = 0   # 00:00
MIDNIGHT_END = 6     # up to but not including 06:00 -> "after midnight" window
AMOUNT_CEILING = 30000.00
DUPLICATE_WINDOW_SECONDS = 5 * 60   # 5 minutes
SUBSCRIPTION_MIN_MONTHS = 3         # must recur in >= 3 distinct months to count


def parse_amount(raw):
    raw = (raw or "").strip().replace(",", "")
    if raw == "":
        return None
    return float(raw)


def parse_datetime(date_str, time_str):
    # Expected formats: Date = "01-Jan-2026", Time = "12:10 AM"
    combined = f"{date_str.strip()} {time_str.strip()}"
    return datetime.strptime(combined, "%d-%b-%Y %I:%M %p")


def categorize(txn_type, description):
    d = description.upper()
    t = txn_type.upper()
    if "DONATION" in t or "DONATION" in d:
        return "Donation"
    if "UTILITY" in t or "BILL" in d:
        return "Utility / Bill Payment"
    if "PREPAID" in d or "BUNDLE" in d.upper() or "MOBILE" in d.upper():
        return "Mobile Load / Bundles"
    if "MERCHANT" in t or "TILL PAYMENT" in d:
        return "Merchant Payment"
    if "IBFT" in t:
        return "IBFT Transfer"
    if "MONEY TRANSFER" in t or "MONEY TRANSFER" in d.upper():
        return "Money Transfer"
    return "Other"


def load_and_filter(path):
    """
    Returns:
        all_rows: list of parsed row dicts (before edge-case filtering)
        kept_rows: list of parsed row dicts (after edge-case filtering)
        unparsed: list of (line_number, raw_row, error) for rows that failed to parse
        raw_row_count: number of data rows in file (excluding header)
        columns: list of column names
    """
    all_rows = []
    kept_rows = []
    unparsed = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        raw_row_count = 0
        for line_no, raw in enumerate(reader, start=2):  # header is line 1
            raw_row_count += 1
            try:
                dt = parse_datetime(raw["Date"], raw["Time"])
                money_in = parse_amount(raw.get("Money In", ""))
                money_out = parse_amount(raw.get("Money Out", ""))
                fee = parse_amount(raw.get("Fee", ""))
                balance = parse_amount(raw.get("Balance", ""))
                txn_type = (raw.get("Transaction Type") or "").strip()
                channel = (raw.get("Channel") or "").strip()
                description = (raw.get("Transaction Description") or "").strip()

                row = {
                    "datetime": dt,
                    "date": dt.date(),
                    "time": dt.time(),
                    "month_key": dt.strftime("%Y-%m"),
                    "txn_type": txn_type,
                    "channel": channel,
                    "description": description,
                    "money_in": money_in,
                    "money_out": money_out,
                    "fee": fee,
                    "balance": balance,
                    "category": categorize(txn_type, description),
                    "raw": raw,
                }
                all_rows.append(row)
            except Exception as e:
                unparsed.append((line_no, raw, str(e)))
                continue

    # ---- Edge-case filters ----
    for row in all_rows:
        # Exclude NADRA billing transactions entirely
        if "NADRA" in row["description"].upper():
            continue
        # Exclude rows where either amount exceeds 30,000 Rs
        if row["money_in"] is not None and row["money_in"] > AMOUNT_CEILING:
            continue
        if row["money_out"] is not None and row["money_out"] > AMOUNT_CEILING:
            continue
        kept_rows.append(row)

    return all_rows, kept_rows, unparsed, raw_row_count, columns


def compute_monthly_trend(rows):
    monthly = defaultdict(float)
    for r in rows:
        if r["money_out"]:
            monthly[r["month_key"]] += r["money_out"]
    return dict(sorted(monthly.items()))


def compute_category_totals(rows):
    cat = defaultdict(lambda: {"total": 0.0, "count": 0})
    for r in rows:
        if r["money_out"]:
            cat[r["category"]]["total"] += r["money_out"]
            cat[r["category"]]["count"] += 1
    # sort by total descending
    return dict(sorted(cat.items(), key=lambda kv: kv[1]["total"], reverse=True))


def compute_midnight_leaks(rows):
    leaks = []
    for r in rows:
        if r["money_out"] and MIDNIGHT_START <= r["time"].hour < MIDNIGHT_END:
            leaks.append(r)
    leaks.sort(key=lambda r: r["datetime"])
    return leaks


def compute_duplicate_charges(rows):
    """
    Groups Money-Out rows by (description, amount). Within each group,
    flags any pair of transactions occurring within DUPLICATE_WINDOW_SECONDS
    of each other as a duplicate-charge event.
    """
    groups = defaultdict(list)
    for r in rows:
        if r["money_out"]:
            groups[(r["description"], round(r["money_out"], 2))].append(r)

    duplicate_events = []
    for (desc, amount), txns in groups.items():
        txns.sort(key=lambda r: r["datetime"])
        for i in range(len(txns) - 1):
            gap = (txns[i + 1]["datetime"] - txns[i]["datetime"]).total_seconds()
            if gap <= DUPLICATE_WINDOW_SECONDS:
                duplicate_events.append({
                    "description": desc,
                    "amount": amount,
                    "first": txns[i],
                    "second": txns[i + 1],
                    "gap_seconds": gap,
                })
    duplicate_events.sort(key=lambda e: e["first"]["datetime"])
    return duplicate_events


def compute_forgotten_subscriptions(rows):
    """
    A "forgotten subscription" candidate = same description AND same amount
    (rounded to nearest rupee) recurring in 3 or more DISTINCT calendar months.
    """
    groups = defaultdict(lambda: {"months": set(), "txns": []})
    for r in rows:
        if r["money_out"]:
            key = (r["description"], round(r["money_out"]))
            groups[key]["months"].add(r["month_key"])
            groups[key]["txns"].append(r)

    subs = []
    for (desc, amount), data in groups.items():
        if len(data["months"]) >= SUBSCRIPTION_MIN_MONTHS:
            subs.append({
                "description": desc,
                "amount": amount,
                "months": sorted(data["months"]),
                "occurrences": len(data["txns"]),
            })
    subs.sort(key=lambda s: len(s["months"]), reverse=True)
    return subs


def compute_verification(rows):
    donations_total = sum(
        r["money_out"] for r in rows
        if r["category"] == "Donation" and r["money_out"]
    )

    spending_rows = [r for r in rows if r["money_out"]]
    biggest = max(spending_rows, key=lambda r: r["money_out"]) if spending_rows else None
    smallest = min(spending_rows, key=lambda r: r["money_out"]) if spending_rows else None

    return {
        "donations_total": donations_total,
        "biggest": biggest,
        "smallest": smallest,
    }


def build_html_report(context, output_path):
    monthly_trend = context["monthly_trend"]
    category_totals = context["category_totals"]
    duplicates = context["duplicates"]
    subscriptions = context["subscriptions"]
    leaks = context["leaks"]
    verification = context["verification"]
    meta = context["meta"]

    # ---- Build simple SVG bar chart for monthly trend ----
    months = list(monthly_trend.keys())
    values = list(monthly_trend.values())
    chart_svg = ""
    if months:
        max_val = max(values) if values else 1
        chart_w, chart_h = 640, 220
        bar_gap = 14
        bar_w = (chart_w - bar_gap * (len(months) + 1)) / len(months)
        bars = []
        for i, (m, v) in enumerate(zip(months, values)):
            bar_h = (v / max_val) * (chart_h - 40) if max_val else 0
            x = bar_gap + i * (bar_w + bar_gap)
            y = chart_h - bar_h - 20
            bars.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
                f'fill="#3b6fd6" rx="3"/>'
                f'<text x="{x + bar_w/2:.1f}" y="{chart_h - 4}" font-size="10" '
                f'text-anchor="middle" fill="#333">{m}</text>'
                f'<text x="{x + bar_w/2:.1f}" y="{y - 4:.1f}" font-size="10" '
                f'text-anchor="middle" fill="#111">{v:,.0f}</text>'
            )
        chart_svg = (
            f'<svg viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(bars) + "</svg>"
        )
    else:
        chart_svg = "<p>No monthly data available.</p>"

    # ---- Category table ----
    cat_rows_html = "".join(
        f"<tr><td>{cat}</td><td>{data['count']}</td>"
        f"<td>Rs {data['total']:,.2f}</td></tr>"
        for cat, data in category_totals.items()
    )

    # ---- Duplicates list ----
    if duplicates:
        dup_rows_html = "".join(
            f"<tr><td>{d['description']}</td><td>Rs {d['amount']:,.2f}</td>"
            f"<td>{d['first']['date']} {d['first']['time'].strftime('%I:%M %p')}</td>"
            f"<td>{d['second']['date']} {d['second']['time'].strftime('%I:%M %p')}</td>"
            f"<td>{int(d['gap_seconds'])}s</td></tr>"
            for d in duplicates
        )
    else:
        dup_rows_html = "<tr><td colspan='5'>No duplicate charges found within a 5-minute window.</td></tr>"

    # ---- Subscriptions list ----
    if subscriptions:
        sub_rows_html = "".join(
            f"<tr><td>{s['description']}</td><td>Rs {s['amount']:,.2f}</td>"
            f"<td>{s['occurrences']}</td><td>{', '.join(s['months'])}</td></tr>"
            for s in subscriptions
        )
    else:
        sub_rows_html = "<tr><td colspan='4'>No recurring charges found in 3+ distinct months.</td></tr>"

    # ---- Midnight leaks summary ----
    leak_total = sum(r["money_out"] for r in leaks)

    # ---- Three observations (data-derived, not guessed) ----
    observations = []
    if category_totals:
        top_cat, top_data = next(iter(category_totals.items()))
        observations.append(
            f"Highest spending category is <b>{top_cat}</b> at Rs {top_data['total']:,.2f} "
            f"across {top_data['count']} transactions."
        )
    if leaks:
        observations.append(
            f"<b>{len(leaks)}</b> transactions occurred between 12:00 AM and 5:59 AM, "
            f"totaling Rs {leak_total:,.2f} in after-midnight spending."
        )
    else:
        observations.append("No after-midnight (12:00 AM - 5:59 AM) spending was found in the filtered data.")
    if duplicates:
        dup_total = sum(d["amount"] for d in duplicates)
        observations.append(
            f"<b>{len(duplicates)}</b> potential duplicate charge(s) detected, "
            f"worth Rs {dup_total:,.2f} combined."
        )
    else:
        observations.append("No duplicate charges (same description/amount within 5 minutes) were detected.")

    biggest = verification["biggest"]
    smallest = verification["smallest"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Spending Pattern Report</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; margin: 24px; color: #1a1a1a; }}
  h1 {{ font-size: 22px; margin-bottom: 4px; }}
  h2 {{ font-size: 16px; margin-top: 28px; border-bottom: 2px solid #3b6fd6; padding-bottom: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 13px; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; }}
  th {{ background: #3b6fd6; color: white; }}
  .meta {{ font-size: 12px; color: #555; margin-bottom: 16px; }}
  ul {{ font-size: 13px; }}
  .verify {{ background: #f5f7fb; padding: 10px 14px; border-radius: 6px; font-size: 13px; }}
</style>
</head>
<body>
<h1>Spending Pattern Report</h1>
<div class="meta">
  Rows analyzed after edge-case filtering: {meta['kept_count']} of {meta['raw_count']} raw rows
  &nbsp;|&nbsp; Date range: {meta['date_min']} to {meta['date_max']}
  &nbsp;|&nbsp; Excluded: NADRA billing rows and amounts &gt; Rs 30,000
</div>

<h2>1-3. Spending Patterns, Forgotten Subscriptions &amp; Duplicate Charges</h2>
<p><b>Category table (spending only):</b></p>
<table>
<tr><th>Category</th><th>Transactions</th><th>Total Spent</th></tr>
{cat_rows_html}
</table>

<p><b>Forgotten subscription candidates</b> (same description + amount recurring in 3+ distinct months):</p>
<table>
<tr><th>Description</th><th>Amount</th><th>Occurrences</th><th>Months seen</th></tr>
{sub_rows_html}
</table>

<p><b>Duplicate charges</b> (identical description + amount within a 5-minute window):</p>
<table>
<tr><th>Description</th><th>Amount</th><th>First charge</th><th>Second charge</th><th>Gap</th></tr>
{dup_rows_html}
</table>

<h2>4. Monthly Spending Trend</h2>
{chart_svg}

<h2>5. Three Observations Worth Your Attention</h2>
<ul>
{''.join(f'<li>{o}</li>' for o in observations)}
</ul>

<h2>Verification (Manual Checks)</h2>
<div class="verify">
  <b>Total Donations to date:</b> Rs {verification['donations_total']:,.2f}<br>
  <b>Biggest spending transaction:</b> Rs {biggest['money_out']:,.2f} on {biggest['date']} at {biggest['time'].strftime('%I:%M %p')} ({biggest['description']})<br>
  <b>Smallest spending transaction:</b> Rs {smallest['money_out']:,.2f} on {smallest['date']} at {smallest['time'].strftime('%I:%M %p')} ({smallest['description']})
</div>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="Analyze account statement CSV for spending patterns.")
    parser.add_argument("input_csv", help="Path to the account statement CSV file")
    parser.add_argument("--output", default="spending_report.html", help="Path to write the HTML report")
    args = parser.parse_args()

    all_rows, kept_rows, unparsed, raw_row_count, columns = load_and_filter(args.input_csv)

    if not all_rows:
        print("ERROR: No rows could be parsed from the input file.")
        sys.exit(1)

    dates = [r["date"] for r in all_rows]
    date_min, date_max = min(dates), max(dates)

    print("=" * 60)
    print("FILE INSPECTION")
    print("=" * 60)
    print(f"Row count (excluding header): {raw_row_count}")
    print(f"Columns: {columns}")
    print(f"Date range: {date_min} to {date_max}")
    print(f"Rows kept after edge-case filtering: {len(kept_rows)} "
          f"(excluded {raw_row_count - len(kept_rows)} rows: NADRA billing / amount > 30,000)")
    print()

    monthly_trend = compute_monthly_trend(kept_rows)
    category_totals = compute_category_totals(kept_rows)
    leaks = compute_midnight_leaks(kept_rows)
    duplicates = compute_duplicate_charges(kept_rows)
    subscriptions = compute_forgotten_subscriptions(kept_rows)
    verification = compute_verification(kept_rows)

    print("=" * 60)
    print("VERIFICATION (MANUAL CHECKS)")
    print("=" * 60)
    print(f"Total Donations to date: Rs {verification['donations_total']:,.2f}")
    b = verification["biggest"]
    s = verification["smallest"]
    print(f"Biggest spending transaction: Rs {b['money_out']:,.2f} on {b['date']} "
          f"at {b['time'].strftime('%I:%M %p')} ({b['description']})")
    print(f"Smallest spending transaction: Rs {s['money_out']:,.2f} on {s['date']} "
          f"at {s['time'].strftime('%I:%M %p')} ({s['description']})")
    print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Monthly trend (spending only): {monthly_trend}")
    print(f"Categories found: {list(category_totals.keys())}")
    print(f"Midnight leak transactions (12AM-5:59AM): {len(leaks)}, total Rs {sum(r['money_out'] for r in leaks):,.2f}")
    print(f"Duplicate charge events: {len(duplicates)}")
    print(f"Forgotten subscription candidates: {len(subscriptions)}")
    print()

    if unparsed:
        print("=" * 60)
        print("UNPARSEABLE ROWS (skipped)")
        print("=" * 60)
        for line_no, raw, err in unparsed:
            print(f"Line {line_no}: {raw} -- Error: {err}")
    else:
        print("No unparseable rows found.")
    print()

    context = {
        "monthly_trend": monthly_trend,
        "category_totals": category_totals,
        "duplicates": duplicates,
        "subscriptions": subscriptions,
        "leaks": leaks,
        "verification": verification,
        "meta": {
            "raw_count": raw_row_count,
            "kept_count": len(kept_rows),
            "date_min": date_min,
            "date_max": date_max,
        },
    }
    build_html_report(context, args.output)
    print(f"HTML report written to: {args.output}")


if __name__ == "__main__":
    main()
