"""Stage B (run in the surfacelab venv): ask a model to pick a tool, for every arm x request x ordering.

Reuses surfacelab's OpenAICompatProvider (Groq key rotation, rate-limit cooldown, tool_use_failed
recording) and CassetteStore (every response cached by request hash, never re-rolled).
Tools are sent exactly as the SDK emitted them: name, description, inputSchema -> OpenAI function.

Usage (from findings/task1):
  uv run --project <path-to-surfacelab> --no-sync python run_eval.py --model openai/gpt-oss-20b --dry-run
  uv run --project <path-to-surfacelab> --no-sync python run_eval.py --model openai/gpt-oss-20b
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import dotenv

from spec import TASKS
from surfacelab.providers.cassette import CassetteStore
from surfacelab.providers.openai_compat import OpenAICompatProvider

HERE = Path(__file__).parent
ARMS = ["google", "numpy", "rest", "plain", "parsed", "summary_only"]
ORDER_SEEDS = [1, 2]


def openai_tools(emitted: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    tools = [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""),
                                               "parameters": t["inputSchema"]}} for t in emitted]
    random.Random(seed).shuffle(tools)  # same seed -> same permutation in every arm (same tool names)
    return tools


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    dotenv.load_dotenv(os.environ.get("ENV_FILE", ".env"))  # GROQ_API_KEY or GROQ_API_KEY_1..N
    store = CassetteStore(HERE / "cassettes", mode="record")
    provider = OpenAICompatProvider("groq", args.model, store, temperature=0.0)

    jobs = []
    for arm in ARMS:
        emitted = json.loads((HERE / "emitted" / f"{arm}.json").read_text(encoding="utf-8"))
        for seed in ORDER_SEEDS:
            tools = openai_tools(emitted, seed)
            for task in TASKS:
                req = {"model": args.model, "messages": [{"role": "user", "content": task.request}],
                       "tools": tools, "tool_choice": "required", "temperature": 0.0, "seed": 0}
                jobs.append((arm, seed, task, req))

    cached = sum(store.has(provider._request_bytes(r)) for *_, r in jobs)
    chars = sum(len(json.dumps(r)) for *_, r in jobs)
    print(f"{len(jobs)} calls, {cached} cached, ~{chars / 4 / 1000:.0f}k input tokens total (chars/4)")
    if args.dry_run:
        return

    def run(job: tuple[str, int, Any, dict[str, Any]]) -> dict[str, Any]:
        arm, seed, task, req = job
        rb = provider._request_bytes(req)
        raw = store.call(rb, lambda _b: provider._make_live_call(req))
        msg = (raw.get("choices") or [{}])[0].get("message") or {}
        calls = msg.get("tool_calls") or []
        picked = calls[0]["function"]["name"] if calls else None
        return {"model": args.model, "arm": arm, "order_seed": seed, "task": task.id, "kind": task.kind,
                "gold": task.gold, "picked": picked, "correct": picked == task.gold,
                "tool_use_failed": bool(raw.get("surfacelab_tool_use_failed")),
                "arguments": calls[0]["function"].get("arguments") if calls else None}

    out = HERE / "results" / f"{args.model.replace('/', '_')}.jsonl"
    out.parent.mkdir(exist_ok=True)
    rows = []
    with ThreadPoolExecutor(args.workers) as ex:
        for i, row in enumerate(ex.map(run, jobs), 1):
            rows.append(row)
            if i % 50 == 0:
                print(f"  {i}/{len(jobs)}", file=sys.stderr, flush=True)
    out.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"wrote {out} ({sum(r['correct'] for r in rows)}/{len(rows)} correct)")


if __name__ == "__main__":
    main()
