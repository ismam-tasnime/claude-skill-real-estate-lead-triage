"""Reference implementation of the lead-triage scoring rules.

The Claude Skill applies these rules in natural language. This script applies the
same rules in plain Python so the expected output can be checked without a chat
session. Run it from the repo root:

    python scripts/score_leads.py

It prints the triage table and exits non-zero if the tier counts drift from the
ones recorded from the live run (4 High, 1 Medium, 5 Low, 1 skipped).
"""
import csv
import re
import sys
from pathlib import Path

MIN_BUDGET = 50_00_000      # ৳50,00,000
MAX_BUDGET = 3_00_00_000    # ৳3,00,00,000
HOT_WORDS = ("referral", "hot")
ORDER = {"High": 0, "Medium": 1, "Low": 2}


def parse_budget(raw):
    """'৳85,00,000' -> 8500000. Blank, N/A or junk -> None."""
    cleaned = re.sub(r"[৳,\s]", "", raw or "")
    return int(cleaned) if cleaned.isdigit() else None


def is_hot(source):
    return any(word in (source or "").lower() for word in HOT_WORDS)


def score(row):
    budget = parse_budget(row["Budget"])
    phone_missing = not row["Phone"].strip()
    if budget is None or phone_missing or not (MIN_BUDGET <= budget <= MAX_BUDGET):
        return "Low"
    return "High" if is_hot(row["Source"]) else "Medium"


def main():
    path = Path(__file__).resolve().parent.parent / "data" / "real_estate_leads_sample.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    new_rows = [r for r in rows if r["Status"].strip().lower() == "new"]
    skipped = len(rows) - len(new_rows)
    scored = sorted(((score(r), i, r) for i, r in enumerate(new_rows)), key=lambda t: (ORDER[t[0]], t[1]))

    print(f"{'Name':<16}{'Priority':<10}{'Budget':<14}{'Source'}")
    for tier, _, r in scored:
        print(f"{r['Name']:<16}{tier:<10}{r['Budget']:<14}{r['Source']}")

    counts = {t: sum(1 for s, _, _ in scored if s == t) for t in ORDER}
    print(f"\n{counts['High']} High, {counts['Medium']} Medium, {counts['Low']} Low, {skipped} skipped (status not New)")

    expected = {"High": 4, "Medium": 1, "Low": 5}
    if counts != expected or skipped != 1:
        print("Counts differ from the recorded run", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
