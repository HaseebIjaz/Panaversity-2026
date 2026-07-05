#!/usr/bin/env python3
"""
dedup_photos.py — Duplicate Photo Finder & Checkpointed Cleanup Tool
=====================================================================

USAGE:
    python3 dedup_photos.py /path/to/folder

WHAT IT DOES (in order, with a checkpoint / user-confirmation at each stage):

  CHECKPOINT 1 - ANALYZE
      Scans the target folder (non-recursive, top-level files only) for
      image files, computes a SHA-256 content hash for each readable image,
      groups files that share an identical hash (true byte-for-byte
      duplicates), and decides a "keeper" per group (oldest file by
      modification time; ties broken alphabetically).
      Writes the plan to 'plan.html' and prints a summary to the terminal.
      Any file that cannot be parsed as an image is flagged, skipped, and
      reported separately — it is NEVER included in duplicate groups or
      deleted.
      -> Asks: proceed with backup? (y/n)

  CHECKPOINT 2 - BACKUP
      If the user agrees, copies every file in the target folder into a
      timestamped backup directory (created ALONGSIDE the target folder,
      i.e. as a sibling, not inside it) EXCEPT:
        - plan.html
        - report.html
        - this script itself (dedup_photos.py)
      Notifies the user of the backup path and asks them to confirm they
      have checked it before continuing.

  CHECKPOINT 3 - DELETE (only duplicates, keeper files are never touched)
      Shows the exact list of files that would be deleted (full path,
      size, which file they duplicate) and asks for final confirmation.
        - If YES: deletes the duplicate files, then writes report.html and
          prints a final execution report.
        - If NO: deletes nothing, and writes report.html / prints a report
          stating the deletion phase was skipped by the user.

SAFETY RULES:
  - Never deletes or modifies anything until BOTH explicit confirmations
    (backup, then delete) are given.
  - Never recurses into subfolders (avoids accidentally touching unrelated
    files); only files directly inside the target folder are considered.
  - Backup is mandatory-offered before any destructive step is even shown.
  - Corrupt / unreadable files are flagged and left completely alone.
"""

import sys
import os
import hashlib
import shutil
import datetime
import html as html_lib

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
SCRIPT_NAME = os.path.basename(__file__)
EXCLUDE_FROM_BACKUP = {"plan.html", "report.html", SCRIPT_NAME}


def human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def sha256_of_file(path, block_size=65536):
    """Return sha256 hex digest of a file's bytes, or raise on failure."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def is_probably_image(path):
    """Lightweight parse check: verify against known image magic bytes.
    We deliberately avoid a heavy dependency (e.g. Pillow) so the script
    runs anywhere with just the standard library. A file that has an
    image extension but fails this signature check is flagged as
    unparsable rather than guessed at.
    """
    signatures = [
        (b"\xff\xd8\xff", "jpg"),
        (b"\x89PNG\r\n\x1a\n", "png"),
        (b"GIF87a", "gif"),
        (b"GIF89a", "gif"),
        (b"BM", "bmp"),
        (b"RIFF", "webp"),  # WEBP starts with RIFF....WEBP
        (b"II*\x00", "tiff"),
        (b"MM\x00*", "tiff"),
    ]
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return False
    for sig, _ in signatures:
        if head.startswith(sig):
            return True
    return False


def scan_folder(folder):
    """Returns (candidates, unparsable) where candidates is a list of dicts
    with path/size/mtime/hash, and unparsable is a list of (filename, reason).
    """
    candidates = []
    unparsable = []

    try:
        entries = sorted(os.listdir(folder))
    except OSError as e:
        print(f"ERROR: could not list folder '{folder}': {e}")
        sys.exit(1)

    for name in entries:
        full = os.path.join(folder, name)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            continue  # not something we consider a "photo" candidate at all

        if not is_probably_image(full):
            unparsable.append((name, "file extension looks like an image but content signature did not match a known image format"))
            continue

        try:
            digest = sha256_of_file(full)
            size = os.path.getsize(full)
            mtime = os.path.getmtime(full)
        except OSError as e:
            unparsable.append((name, f"could not read file: {e}"))
            continue

        candidates.append({
            "name": name,
            "path": full,
            "size": size,
            "mtime": mtime,
            "hash": digest,
        })

    return candidates, unparsable


def build_duplicate_plan(candidates):
    """Group candidates by hash. For each group with >1 member, choose a
    keeper (oldest mtime, ties broken alphabetically by name) and mark the
    rest for deletion. Returns list of group dicts.
    """
    groups = {}
    for c in candidates:
        groups.setdefault(c["hash"], []).append(c)

    plan = []
    for digest, members in groups.items():
        if len(members) < 2:
            continue
        members_sorted = sorted(members, key=lambda m: (m["mtime"], m["name"]))
        keeper = members_sorted[0]
        duplicates = members_sorted[1:]
        plan.append({
            "hash": digest,
            "keeper": keeper,
            "duplicates": duplicates,
        })
    return plan


def write_plan_html(folder, candidates, unparsable, plan, out_path):
    total_dupes = sum(len(g["duplicates"]) for g in plan)
    reclaimable = sum(d["size"] for g in plan for d in g["duplicates"])

    rows = []
    for g in plan:
        k = g["keeper"]
        rows.append(f"<tr class='keeper'><td>{html_lib.escape(k['name'])}</td>"
                     f"<td>KEEP</td><td>{human_size(k['size'])}</td>"
                     f"<td>{html_lib.escape(g['hash'][:12])}...</td></tr>")
        for d in g["duplicates"]:
            rows.append(f"<tr class='dupe'><td>{html_lib.escape(d['name'])}</td>"
                         f"<td>DELETE (duplicate of {html_lib.escape(k['name'])})</td>"
                         f"<td>{human_size(d['size'])}</td>"
                         f"<td>{html_lib.escape(g['hash'][:12])}...</td></tr>")

    flagged_rows = "".join(
        f"<tr><td>{html_lib.escape(n)}</td><td>{html_lib.escape(r)}</td></tr>"
        for n, r in unparsable
    ) or "<tr><td colspan='2'><em>None</em></td></tr>"

    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Duplicate Photo Plan</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; background:#fafafa; color:#222; }}
h1 {{ font-size: 1.4rem; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; background:#fff; }}
th, td {{ border: 1px solid #ddd; padding: 6px 10px; font-size: 0.9rem; text-align:left; }}
th {{ background:#333; color:#fff; }}
tr.keeper td {{ background:#eaffea; }}
tr.dupe td {{ background:#ffecec; }}
.summary {{ background:#fff; padding:1rem; border:1px solid #ddd; margin-bottom:1.5rem; }}
</style></head>
<body>
<h1>Duplicate Photo Analysis — {html_lib.escape(folder)}</h1>
<div class="summary">
  <p><strong>Total image files scanned:</strong> {len(candidates)}</p>
  <p><strong>Duplicate groups found:</strong> {len(plan)}</p>
  <p><strong>Files planned for deletion:</strong> {total_dupes}</p>
  <p><strong>Space reclaimable:</strong> {human_size(reclaimable)}</p>
  <p><strong>Unparsable / flagged files (skipped, untouched):</strong> {len(unparsable)}</p>
  <p><em>Generated: {datetime.datetime.now().isoformat(timespec='seconds')}</em></p>
</div>

<h2>Deletion Plan</h2>
<table>
<tr><th>File</th><th>Action</th><th>Size</th><th>Content Hash</th></tr>
{''.join(rows) if rows else "<tr><td colspan='4'><em>No duplicates found.</em></td></tr>"}
</table>

<h2>Flagged / Unparsable Files (not touched)</h2>
<table>
<tr><th>File</th><th>Reason</th></tr>
{flagged_rows}
</table>
</body></html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


def print_plan_cli(folder, candidates, unparsable, plan):
    total_dupes = sum(len(g["duplicates"]) for g in plan)
    reclaimable = sum(d["size"] for g in plan for d in g["duplicates"])
    print("=" * 70)
    print("CHECKPOINT 1: ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Folder scanned:            {folder}")
    print(f"Image files scanned:       {len(candidates)}")
    print(f"Duplicate groups found:    {len(plan)}")
    print(f"Files planned for deletion:{total_dupes:>3}")
    print(f"Space reclaimable:         {human_size(reclaimable)}")
    print(f"Flagged/unparsable files:  {len(unparsable)}")
    print("-" * 70)
    for g in plan:
        k = g["keeper"]
        print(f"[KEEP]   {k['name']}  ({human_size(k['size'])})")
        for d in g["duplicates"]:
            print(f"  [DELETE] {d['name']}  ({human_size(d['size'])})  -> duplicate of {k['name']}")
    if unparsable:
        print("-" * 70)
        print("Flagged files (skipped, will NOT be touched):")
        for n, r in unparsable:
            print(f"  - {n}: {r}")
    print("=" * 70)
    print("Full details written to: plan.html")
    print("=" * 70)


def ask_yes_no(prompt):
    while True:
        ans = input(prompt + " [y/n]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")


def do_backup(folder, plan_html_path, report_html_path):
    parent = os.path.dirname(os.path.abspath(folder.rstrip(os.sep)))
    base_name = os.path.basename(os.path.abspath(folder.rstrip(os.sep)))
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(parent, f"{base_name}_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=False)

    exclude_names = set(EXCLUDE_FROM_BACKUP)
    exclude_names.add(os.path.basename(plan_html_path))
    exclude_names.add(os.path.basename(report_html_path))

    copied = 0
    for name in sorted(os.listdir(folder)):
        if name in exclude_names:
            continue
        full = os.path.join(folder, name)
        if os.path.isfile(full):
            shutil.copy2(full, os.path.join(backup_dir, name))
            copied += 1

    return backup_dir, copied


def write_report_html(out_path, folder, plan, deleted, skipped_by_user, unparsable, backup_dir):
    total_dupes = sum(len(g["duplicates"]) for g in plan)
    deleted_size = sum(d["size"] for g in plan for d in g["duplicates"] if d["path"] in deleted)

    rows = []
    for g in plan:
        for d in g["duplicates"]:
            status = "DELETED" if d["path"] in deleted else "SKIPPED (kept)"
            rows.append(f"<tr><td>{html_lib.escape(d['name'])}</td><td>{status}</td>"
                        f"<td>{human_size(d['size'])}</td>"
                        f"<td>duplicate of {html_lib.escape(g['keeper']['name'])}</td></tr>")

    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Execution Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; background:#fafafa; color:#222; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; background:#fff; }}
th, td {{ border: 1px solid #ddd; padding: 6px 10px; font-size: 0.9rem; text-align:left; }}
th {{ background:#333; color:#fff; }}
.summary {{ background:#fff; padding:1rem; border:1px solid #ddd; margin-bottom:1.5rem; }}
</style></head>
<body>
<h1>Duplicate Photo Cleanup — Execution Report</h1>
<div class="summary">
  <p><strong>Folder:</strong> {html_lib.escape(folder)}</p>
  <p><strong>Backup location:</strong> {html_lib.escape(backup_dir) if backup_dir else "N/A"}</p>
  <p><strong>Deletion phase:</strong> {"SKIPPED BY USER" if skipped_by_user else "EXECUTED"}</p>
  <p><strong>Total duplicate files identified:</strong> {total_dupes}</p>
  <p><strong>Files actually deleted:</strong> {len(deleted)}</p>
  <p><strong>Space freed:</strong> {human_size(deleted_size)}</p>
  <p><strong>Flagged/unparsable files (untouched):</strong> {len(unparsable)}</p>
  <p><em>Generated: {datetime.datetime.now().isoformat(timespec='seconds')}</em></p>
</div>
<h2>File-by-file Outcome</h2>
<table>
<tr><th>File</th><th>Status</th><th>Size</th><th>Notes</th></tr>
{''.join(rows) if rows else "<tr><td colspan='4'><em>No duplicates existed.</em></td></tr>"}
</table>
</body></html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dedup_photos.py /path/to/folder")
        sys.exit(1)

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print(f"ERROR: '{folder}' is not a valid directory.")
        sys.exit(1)

    plan_html_path = os.path.join(folder, "plan.html")
    report_html_path = os.path.join(folder, "report.html")

    # ---------- CHECKPOINT 1: ANALYZE ----------
    candidates, unparsable = scan_folder(folder)
    plan = build_duplicate_plan(candidates)
    write_plan_html(folder, candidates, unparsable, plan, plan_html_path)
    print_plan_cli(folder, candidates, unparsable, plan)

    if not plan:
        print("\nNo duplicates found. Nothing further to do. Exiting.")
        sys.exit(0)

    proceed_backup = ask_yes_no("\nProceed with creating a backup of the folder?")
    if not proceed_backup:
        print("Backup declined. Exiting without making any changes.")
        sys.exit(0)

    # ---------- CHECKPOINT 2: BACKUP ----------
    backup_dir, copied = do_backup(folder, plan_html_path, report_html_path)
    print("\n" + "=" * 70)
    print("CHECKPOINT 2: BACKUP COMPLETE")
    print("=" * 70)
    print(f"Backup created at: {backup_dir}")
    print(f"Files copied:      {copied}")
    print("=" * 70)

    confirmed_backup = ask_yes_no("Please check the backup folder now. Confirm it looks correct to continue?")
    if not confirmed_backup:
        print("User did not confirm backup integrity. Halting before any deletion. Exiting.")
        sys.exit(0)

    # ---------- CHECKPOINT 3: DELETE ----------
    print("\n" + "=" * 70)
    print("CHECKPOINT 3: FINAL DELETION PHASE")
    print("=" * 70)
    total_dupes = sum(len(g["duplicates"]) for g in plan)
    reclaimable = sum(d["size"] for g in plan for d in g["duplicates"])
    print(f"The following {total_dupes} file(s) are planned for deletion (total {human_size(reclaimable)}):")
    for g in plan:
        for d in g["duplicates"]:
            print(f"  - {d['path']}  ({human_size(d['size'])})  duplicate of {g['keeper']['name']}")
    print("=" * 70)

    proceed_delete = ask_yes_no("Proceed with deleting the duplicate files listed above?")

    deleted = []
    skipped_by_user = not proceed_delete
    if proceed_delete:
        for g in plan:
            for d in g["duplicates"]:
                try:
                    os.remove(d["path"])
                    deleted.append(d["path"])
                except OSError as e:
                    print(f"  ERROR deleting {d['path']}: {e}")
        print(f"\nDeleted {len(deleted)} file(s).")
    else:
        print("\nDeletion skipped by user. No files were removed.")

    write_report_html(report_html_path, folder, plan, deleted, skipped_by_user, unparsable, backup_dir)

    print("\n" + "=" * 70)
    print("FINAL EXECUTION REPORT")
    print("=" * 70)
    print(f"Backup location:          {backup_dir}")
    print(f"Deletion phase:           {'SKIPPED BY USER' if skipped_by_user else 'EXECUTED'}")
    print(f"Duplicate files found:    {total_dupes}")
    print(f"Files actually deleted:   {len(deleted)}")
    print(f"Space freed:              {human_size(sum(os.path.getsize(p) for p in []) if False else sum(d['size'] for g in plan for d in g['duplicates'] if d['path'] in deleted))}")
    print(f"Flagged/unparsable files: {len(unparsable)}")
    print(f"Full report written to:  {report_html_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
