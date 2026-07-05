#!/usr/bin/env python3
"""
reconcile.py

Reconciles a hand-counted "expected payments" ledger against a messy
digital payment history, using a nickname mapping table to normalize
sender names, and handling combined/split payments (e.g. one person
paying for themself + another, indicated by a "+" in the memo).

Usage:
    python3 reconcile.py --expected expected_payments.csv \
                          --history payment_history.csv \
                          --output report.html

No data is hardcoded in this script. All amounts, names, and mappings
are read from the input CSV files (except the nickname lookup table,
which is a mapping rule provided as part of the task spec, and the
expected total dollar rule).
"""

import argparse
import csv
import sys
import html as html_lib
from datetime import datetime

# --- Nickname mapping (payment-record name -> canonical person name) ---
# Keys are matched case-sensitively against the exact string in the
# Sender column of payment_history.csv.
NICKNAME_MAP = {
    "Alice W.": "Alice",
    "Bobby": "Bob",
    "Charlie": "Charlie",
    "D. Lee": "David",
    "Emma": "Emma",
    "F. Miller": "Frank",
    "Grace": "Grace",
    "Izzy": "Isabella",
    "Unknown User (Jack)": "Jack",
}

EXPECTED_TOTAL_RULE = 200.0  # Stated rule: expected total collected should be $200


def read_expected(path):
    """Read expected_payments.csv -> dict {Person: AmountDue(float)}, plus parse errors."""
    expected = {}
    errors = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 = header
            try:
                person = row["Person"].strip()
                amount = float(row["AmountDue"])
                if not person:
                    raise ValueError("empty Person field")
                expected[person] = amount
            except Exception as e:
                errors.append({"row_num": i, "raw": row, "reason": str(e)})
    return expected, errors


def parse_split_names(memo, sender_canonical):
    """
    Detect combined/split payments from memo text like 'Me + Henry'.
    Returns a list of canonical person names this single payment should
    be credited toward. 'Me' refers to the sender themself.

    This only handles the explicit '+' pattern; anything else is treated
    as a single-person payment for the sender.
    """
    if memo is None:
        return [sender_canonical]
    memo_stripped = memo.strip()
    if "+" not in memo_stripped:
        return [sender_canonical]

    parts = [p.strip() for p in memo_stripped.split("+")]
    names = []
    for p in parts:
        if p.lower() == "me":
            names.append(sender_canonical)
        elif p:
            names.append(p)
    return names if names else [sender_canonical]


def read_history(path, nickname_map):
    """
    Read payment_history.csv, normalize sender names via nickname_map,
    detect split payments, and return:
      - list of parsed payment credit records: {date, raw_sender, canonical, amount, memo, split}
      - list of unparseable/flagged rows
    """
    credits = []
    errors = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            raw_sender = (row.get("Sender") or "").strip()
            raw_amount = (row.get("Amount") or "").strip()
            raw_date = (row.get("Date") or "").strip()
            memo = row.get("Memo") or ""

            # Validate date
            try:
                datetime.strptime(raw_date, "%Y-%m-%d")
            except Exception:
                errors.append({"row_num": i, "raw": row, "reason": f"unparseable date '{raw_date}'"})
                continue

            # Validate amount
            try:
                amount = float(raw_amount)
            except Exception:
                errors.append({"row_num": i, "raw": row, "reason": f"unparseable amount '{raw_amount}'"})
                continue

            # Validate sender maps to a known person
            if raw_sender not in nickname_map:
                errors.append({"row_num": i, "raw": row, "reason": f"unrecognized sender '{raw_sender}' (no nickname mapping)"})
                continue

            canonical_sender = nickname_map[raw_sender]
            names_covered = parse_split_names(memo, canonical_sender)
            is_split = len(names_covered) > 1

            if is_split:
                # Split evenly across the named people
                share = amount / len(names_covered)
                for person in names_covered:
                    credits.append({
                        "date": raw_date,
                        "raw_sender": raw_sender,
                        "canonical": person,
                        "amount": share,
                        "memo": memo,
                        "split": True,
                        "split_group": names_covered,
                        "row_num": i,
                    })
            else:
                credits.append({
                    "date": raw_date,
                    "raw_sender": raw_sender,
                    "canonical": canonical_sender,
                    "amount": amount,
                    "memo": memo,
                    "split": False,
                    "split_group": [canonical_sender],
                    "row_num": i,
                })

    return credits, errors


def reconcile(expected, credits):
    """
    Build per-person reconciliation: amount due, amount paid (summed
    across possibly multiple credit rows), balance, and status.
    """
    paid_by_person = {}
    for c in credits:
        paid_by_person.setdefault(c["canonical"], 0.0)
        paid_by_person[c["canonical"]] += c["amount"]

    all_people = sorted(set(expected.keys()) | set(paid_by_person.keys()))
    rows = []
    for person in all_people:
        due = expected.get(person)
        paid = paid_by_person.get(person, 0.0)
        if due is None:
            status = "PAID BUT NOT EXPECTED"
            balance = -paid
        else:
            balance = round(due - paid, 2)
            if balance <= 0.0001 and balance >= -0.0001:
                status = "PAID IN FULL"
            elif paid > 0:
                status = "PARTIAL - FOLLOW UP"
            else:
                status = "NOT PAID - FOLLOW UP"
        rows.append({
            "person": person,
            "due": due,
            "paid": round(paid, 2),
            "balance": balance,
            "status": status,
        })
    return rows


def build_html_report(rows, expected, credits, expected_errors, history_errors, expected_total_rule, out_path):
    total_due = sum(v for v in expected.values())
    total_paid = sum(c["amount"] for c in credits)
    gap = round(expected_total_rule - total_paid, 2)

    followups = [r for r in rows if r["status"] in ("PARTIAL - FOLLOW UP", "NOT PAID - FOLLOW UP")]

    def esc(x):
        return html_lib.escape(str(x))

    rows_html = ""
    for r in rows:
        due_str = f"${r['due']:.2f}" if r["due"] is not None else "—"
        rows_html += f"""
        <tr class="{esc(r['status']).lower().replace(' ', '-')}">
            <td>{esc(r['person'])}</td>
            <td>{due_str}</td>
            <td>${r['paid']:.2f}</td>
            <td>${r['balance']:.2f}</td>
            <td>{esc(r['status'])}</td>
        </tr>"""

    errors_html = ""
    all_errors = [("expected_payments.csv", e) for e in expected_errors] + \
                 [("payment_history.csv", e) for e in history_errors]
    if all_errors:
        for src, e in all_errors:
            errors_html += f"""
        <tr>
            <td>{esc(src)}</td>
            <td>{esc(e['row_num'])}</td>
            <td>{esc(e['raw'])}</td>
            <td>{esc(e['reason'])}</td>
        </tr>"""
    else:
        errors_html = "<tr><td colspan='4'>None — all rows parsed successfully.</td></tr>"

    followup_html = ""
    if followups:
        for r in followups:
            due_str = f"${r['due']:.2f}" if r["due"] is not None else "—"
            followup_html += f"<li><strong>{esc(r['person'])}</strong> — owes ${r['balance']:.2f} (due {due_str}, paid ${r['paid']:.2f})</li>"
    else:
        followup_html = "<li>No follow-ups needed — everyone expected has paid in full.</li>"

    credits_html = ""
    for c in credits:
        split_note = f" (split payment: {', '.join(c['split_group'])})" if c["split"] else ""
        credits_html += f"""
        <tr>
            <td>{esc(c['date'])}</td>
            <td>{esc(c['raw_sender'])}</td>
            <td>{esc(c['canonical'])}</td>
            <td>${c['amount']:.2f}{esc(split_note)}</td>
            <td>{esc(c['memo'])}</td>
        </tr>"""

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Payment Reconciliation Report</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: #1a1a1a; background: #fafafa; }}
  h1 {{ margin-bottom: 4px; }}
  .subtitle {{ color: #666; margin-top: 0; margin-bottom: 24px; }}
  .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 12px 18px; min-width: 140px; }}
  .card .label {{ font-size: 12px; color: #777; text-transform: uppercase; letter-spacing: 0.03em; }}
  .card .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  .gap {{ color: {"#c0392b" if gap != 0 else "#27ae60"}; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 28px; background: white; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; font-size: 14px; }}
  th {{ background: #f0f0f0; }}
  tr.paid-in-full {{ background: #eafaf1; }}
  tr.partial---follow-up {{ background: #fff8e1; }}
  tr.not-paid---follow-up {{ background: #fdecea; }}
  h2 {{ margin-top: 32px; border-bottom: 2px solid #eee; padding-bottom: 6px; }}
  .followups {{ background: #fff8e1; border: 1px solid #f0d97a; border-radius: 8px; padding: 12px 20px; }}
</style>
</head>
<body>
  <h1>Payment Reconciliation Report</h1>
  <p class="subtitle">Generated by reconcile.py — expected_payments.csv vs payment_history.csv</p>

  <div class="summary">
    <div class="card"><div class="label">Expected Total (stated rule)</div><div class="value">${expected_total_rule:.2f}</div></div>
    <div class="card"><div class="label">Sum of AmountDue (ledger)</div><div class="value">${total_due:.2f}</div></div>
    <div class="card"><div class="label">Total Received (parsed credits)</div><div class="value">${total_paid:.2f}</div></div>
    <div class="card"><div class="label">Gap vs Expected Total</div><div class="value gap">${gap:.2f}</div></div>
  </div>

  <h2>Per-Person Reconciliation</h2>
  <table>
    <tr><th>Person</th><th>Amount Due</th><th>Amount Paid</th><th>Balance</th><th>Status</th></tr>
    {rows_html}
  </table>

  <h2>Follow-Up List</h2>
  <div class="followups"><ul>{followup_html}</ul></div>

  <h2>Matched Payment Credits (after nickname normalization &amp; split handling)</h2>
  <table>
    <tr><th>Date</th><th>Raw Sender (payment record)</th><th>Canonical Person</th><th>Credited Amount</th><th>Memo</th></tr>
    {credits_html}
  </table>

  <h2>Flagged / Unparseable Rows (skipped)</h2>
  <table>
    <tr><th>Source File</th><th>Row #</th><th>Raw Row</th><th>Reason</th></tr>
    {errors_html}
  </table>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


def main():
    parser = argparse.ArgumentParser(description="Reconcile expected payments against payment history.")
    parser.add_argument("--expected", required=True, help="Path to expected_payments.csv")
    parser.add_argument("--history", required=True, help="Path to payment_history.csv")
    parser.add_argument("--output", default="report.html", help="Path to write the HTML report")
    args = parser.parse_args()

    expected, expected_errors = read_expected(args.expected)
    credits, history_errors = read_history(args.history, NICKNAME_MAP)
    rows = reconcile(expected, credits)

    build_html_report(rows, expected, credits, expected_errors, history_errors, EXPECTED_TOTAL_RULE, args.output)

    total_paid = sum(c["amount"] for c in credits)
    gap = round(EXPECTED_TOTAL_RULE - total_paid, 2)

    print("=== RECONCILIATION SUMMARY ===")
    print(f"Expected total (rule): ${EXPECTED_TOTAL_RULE:.2f}")
    print(f"Total received (parsed): ${total_paid:.2f}")
    print(f"Gap: ${gap:.2f}")
    print()
    print("Per-person:")
    for r in rows:
        due_str = f"${r['due']:.2f}" if r["due"] is not None else "N/A"
        print(f"  {r['person']:<10} due={due_str:<8} paid=${r['paid']:.2f}  balance=${r['balance']:.2f}  status={r['status']}")
    print()
    if expected_errors or history_errors:
        print("Flagged rows:")
        for e in expected_errors:
            print(f"  [expected_payments.csv row {e['row_num']}] {e['reason']}: {e['raw']}")
        for e in history_errors:
            print(f"  [payment_history.csv row {e['row_num']}] {e['reason']}: {e['raw']}")
    else:
        print("Flagged rows: none")
    print()
    print(f"Report written to: {args.output}")


if __name__ == "__main__":
    main()
