"""Score baselines from the human-eval CSV exported from the Google Sheet.

Scoring: rank 1 -> 3 points, rank 2 -> 2, rank 3 -> 1.
A/B/C labels are mapped to baselines per-paper using paper_list.json.

Usage:
    python score_human_eval.py "Rebuttal_human_study - Sheet1.csv"
    python score_human_eval.py "Rebuttal_human_study - Sheet1.csv" --by-criterion
    python score_human_eval.py "Rebuttal_human_study - Sheet1.csv" --by-paper
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

RANK_TO_SCORE = {"1": 5, "2": 4, "3": 3, "4": 2, "5": 1}
HERE = Path(__file__).resolve().parent


def load_paper_to_labels(paper_list_path: Path) -> dict:
    """Return {paper_name: {"A": baseline, "B": baseline, "C": baseline}}."""
    with paper_list_path.open() as f:
        sets = json.load(f)
    paper_to_labels = {}
    for s in sets.values():
        for paper in s["papers"]:
            paper_to_labels[paper] = s["labels"]
    return paper_to_labels


def aggregate(csv_path: Path, paper_to_labels: dict):
    """Yield one (evaluator, paper, criterion, baseline, score) per scored cell."""
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("paper") or not row.get("criterion"):
                continue
            paper = row["paper"]
            labels = paper_to_labels.get(paper)
            if not labels:
                print(f"WARN: no label mapping for paper {paper!r}; skipping",
                      file=sys.stderr)
                continue
            for col in ("rank_A", "rank_B", "rank_C", "rank_D", "rank_E"):
                rank = (row.get(col) or "").strip()
                if rank not in RANK_TO_SCORE:
                    continue
                letter = col.split("_")[1]
                baseline = labels[letter]
                yield {
                    "evaluator": row.get("evaluator", ""),
                    "paper": paper,
                    "criterion": row["criterion"],
                    "baseline": baseline,
                    "score": RANK_TO_SCORE[rank],
                }


def summarize(records, group_keys):
    """Sum scores and counts grouped by `group_keys + ('baseline',)`."""
    totals = defaultdict(lambda: {"sum": 0, "n": 0})
    for r in records:
        key = tuple(r[k] for k in group_keys) + (r["baseline"],)
        totals[key]["sum"] += r["score"]
        totals[key]["n"] += 1
    out = []
    for key, agg in totals.items():
        avg = agg["sum"] / agg["n"] if agg["n"] else 0.0
        row = dict(zip(group_keys + ["baseline"], key))
        row["avg_score"] = round(avg, 3)
        row["total_score"] = agg["sum"]
        row["n_rankings"] = agg["n"]
        out.append(row)
    out.sort(key=lambda r: tuple(r[k] for k in group_keys) + (-r["avg_score"],))
    return out


def print_table(rows, columns):
    if not rows:
        print("(no rows)")
        return
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    header = "  ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("  ".join("-" * widths[c] for c in columns))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path, help="Path to the exported CSV")
    ap.add_argument("--paper-list", type=Path,
                    default=HERE / "paper_list.json",
                    help="Path to paper_list.json (default: alongside this script)")
    ap.add_argument("--by-criterion", action="store_true",
                    help="Break down per criterion as well")
    ap.add_argument("--by-paper", action="store_true",
                    help="Break down per paper as well")
    args = ap.parse_args()

    paper_to_labels = load_paper_to_labels(args.paper_list)
    records = list(aggregate(args.csv, paper_to_labels))

    if not records:
        print("No scored rows found in CSV.", file=sys.stderr)
        sys.exit(1)

    print(f"Scored {len(records)} ranking cells "
          f"from {len({r['evaluator'] for r in records})} evaluator(s) "
          f"across {len({r['paper'] for r in records})} paper(s).\n")

    print("=== Overall (avg score per baseline) ===")
    overall = summarize(records, group_keys=[])
    overall.sort(key=lambda r: -r["avg_score"])
    print_table(overall, ["baseline", "avg_score", "total_score", "n_rankings"])

    if args.by_criterion:
        print("\n=== Per criterion ===")
        rows = summarize(records, group_keys=["criterion"])
        print_table(rows, ["criterion", "baseline", "avg_score",
                           "total_score", "n_rankings"])

    if args.by_paper:
        print("\n=== Per paper ===")
        rows = summarize(records, group_keys=["paper"])
        print_table(rows, ["paper", "baseline", "avg_score",
                           "total_score", "n_rankings"])


if __name__ == "__main__":
    main()
