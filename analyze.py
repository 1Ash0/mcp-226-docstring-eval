"""Accuracy per arm with 95% cluster-bootstrap CIs (clusters = requests), plus paired diffs vs google.

Usage: python analyze.py results/<model>.jsonl [...]   (stdlib only)
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict

ARMS = ["google", "numpy", "rest", "plain", "parsed", "summary_only"]
B, SEED = 10_000, 42


def pct(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def analyze(rows: list[dict], kind: str | None) -> list[str]:
    # per[arm][task] = list of 0/1 over orderings
    per: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if kind is None or r["kind"] == kind:
            per[r["arm"]][r["task"]].append(int(r["correct"]))
    tasks = sorted(per["google"])
    rng = random.Random(SEED)
    samples = [[rng.choice(tasks) for _ in tasks] for _ in range(B)]

    def acc(arm: str, ts: list[str]) -> float:
        vals = [v for t in ts for v in per[arm][t]]
        return sum(vals) / len(vals)

    out = []
    for arm in ARMS:
        if arm not in per:
            continue
        a = acc(arm, tasks)
        boots = [acc(arm, s) for s in samples]
        line = f"| {arm} | {a:.3f} [{pct(boots, .025):.3f}, {pct(boots, .975):.3f}] | n={sum(len(per[arm][t]) for t in tasks)} |"
        if arm != "google":
            d = a - acc("google", tasks)
            db = [acc(arm, s) - acc("google", s) for s in samples]
            line += f" {d * 100:+.1f} pp [{pct(db, .025) * 100:+.1f}, {pct(db, .975) * 100:+.1f}] |"
        else:
            line += " (reference) |"
        out.append(line)
    return out


def main() -> None:
    for path in sys.argv[1:]:
        rows = [json.loads(line) for line in open(path, encoding="utf-8")]
        print(f"\n## {rows[0]['model']}  ({len(rows)} calls, tool_use_failed={sum(r['tool_use_failed'] for r in rows)})")
        for kind in (None, "summary", "param"):
            print(f"\n### requests: {kind or 'all'}\n| arm | accuracy [95% CI] | n | diff vs google [95% CI] |\n|---|---|---|---|")
            print("\n".join(analyze(rows, kind)))
        errs = [r for r in rows if not r["correct"]]
        print("\nerrors (arm, task, gold -> picked):")
        for r in sorted(errs, key=lambda r: (r["task"], r["arm"])):
            print(f"  {r['arm']:12s} {r['task']} s{r['order_seed']} {r['gold']} -> {r['picked']}")


if __name__ == "__main__":
    main()
