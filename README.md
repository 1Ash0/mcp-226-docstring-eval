# mcp-226-docstring-eval

Data for [modelcontextprotocol/python-sdk#226](https://github.com/modelcontextprotocol/python-sdk/issues/226):
does the docstring format of an `MCPServer` tool, or parsing parameter docs into the schema,
change which tool a model picks?

Setup: SDK `main` @ `77001c96`, Python 3.13.5, pydantic 2.12.5, griffe 2.1.0;
model `openai/gpt-oss-20b` on Groq, temperature 0, seed 0, run 2026-11-06.

## Result

| version | right tool chosen |
|---|---|
| Google / NumPy / reST / plain docstring, as `main` emits them | 69/72 each |
| parsed (parameter docs moved into `inputSchema`) | 69/72 |
| summary line only | 65/72 |

The model never picked a wrong tool. All 22 misses were clarifying questions instead of a tool call.
Confidence intervals and per-request detail are in [`ANALYSIS_gpt-oss-20b.md`](ANALYSIS_gpt-oss-20b.md).
The plan and verdict rules were written before any call: [`PREREG.md`](PREREG.md).

Separately, [`repro_getdoc.py`](repro_getdoc.py) shows the description clients receive
keeps source indentation on Python 3.11/3.12 but not on 3.13 ([`repro_getdoc_output.txt`](repro_getdoc_output.txt)).

## Files

| path | what |
|---|---|
| `spec.py` | the 18 tools and 36 requests |
| `gen_arms.py` | builds each version as real functions, registers them on `MCPServer`, saves `tools/list` output |
| `arms/` | the generated tool modules |
| `emitted/` | exactly what the SDK returned from `tools/list`, per version |
| `griffe_parse.json` | how many parameter descriptions griffe recovers per format |
| `run_eval.py` | sends each request to the model (uses [surfacelab](https://github.com/1Ash0/surfacelab)'s Groq provider and cache) |
| `cassettes/` | every request and response, keyed by request hash (432) |
| `results/` | one row per call: version, request, gold tool, picked tool |
| `analyze.py` | accuracy and cluster-bootstrap CIs (stdlib only) |

## Reproduce

```bash
# re-derive the table from recorded results (no network, stdlib only)
python analyze.py results/openai_gpt-oss-20b.jsonl

# regenerate what the SDK emits (in a python-sdk checkout's environment)
uv run --project <python-sdk> python gen_arms.py

# replay every model call from cassettes; makes no API calls when all 432 are cached
uv run --project <surfacelab> python run_eval.py --model openai/gpt-oss-20b --dry-run
```

## Limits

One small model, one synthetic tool set, and selection was already at ceiling, so this can't show
a selection benefit and doesn't rule one out. Argument quality isn't measured. 36 requests can't
detect effects smaller than about 5–7 percentage points.

Prepared with AI assistance (Claude); I ran and checked the results.
