# Preregistration: docstring format vs tool selection (#226)

Written 2026-11-06 before any model call. Changes after this point go in "Deviations".

## Question
On `main` (77001c96) the SDK puts `fn.__doc__` verbatim into `Tool.description` and puts no
parameter descriptions in `inputSchema`. Does the docstring markup, or moving parameter docs
into the schema (what the #226 PRs do), change which tool a model picks?

## Arms (emitted by the real SDK via `tools/list`, saved in `emitted/`)
- `google`, `numpy`, `rest`, `plain`: same information, four markups, raw docstring (main today).
- `parsed`: description = summary only, parameter docs in `inputSchema.properties.*.description`
  (built from griffe 2.1.0's parse of the Google docstrings).
- `summary_only`: description = summary only, no parameter info anywhere. Sensitivity control.

## Task set
18 tools (6 families x 3 look-alikes) and 36 requests, 2 per tool (`spec.py`):
`summary` requests are answerable from the summary line; `param` requests only from a parameter
description. All 18 tools are offered in every request.

## Procedure
- Models (Groq, OpenAI-compatible API): primary `openai/gpt-oss-20b`; replication
  `openai/gpt-oss-120b` if the free-tier budget allows. `temperature=0`, `seed=0`,
  `tool_choice="required"`, provider-default reasoning effort.
- Each request is run with 2 tool orderings (seeded permutations, seeds 1 and 2), the same
  orderings in every arm. Cell = arm x model: 36 requests x 2 orderings = 72 calls, 36 clusters.
- Every response is cached by request hash (surfacelab `CassetteStore`); nothing is re-rolled.
  A `tool_use_failed` response is scored wrong.

## Metric and analysis
- Correct = name of the first tool call equals the gold tool.
- Accuracy per cell; 95% CI by cluster bootstrap over the 36 requests (both orderings of a
  request resampled together), 10,000 resamples, seed 42.
- Paired differences vs `google` on the same resampled requests.
- Also reported by request kind (`summary` / `param`), exploratory.

## Verdict rules
- H1 (markup matters): a difference vs `google` for `numpy`, `rest` or `plain` whose 95% CI
  excludes 0. Otherwise "no difference detected at this sample size", not "no effect".
- H2 (parsing matters): same rule for `parsed` vs `google`.
- Sensitivity check: if `summary_only` is not below `google` on `param` requests (CI excludes 0),
  the task set cannot detect loss of parameter information and H1/H2 nulls are uninformative.
- Ceiling: if `google` accuracy is >= 0.97, say the comparison is at ceiling.

## Deviations
- Infra: Groq key #13 was revoked (401) mid-run; it was dropped and the run restarted. 17 responses
  recorded before the crash were replayed from cassettes, not re-requested. No design change.
- Post hoc (labelled exploratory): all 22 errors were `tool_use_failed` = the model asked a
  clarifying question instead of calling a tool. Wrong-tool picks were 0/432. Results are reported
  both ways (preregistered "abstain = wrong" and the decomposition).
- Replication on gpt-oss-120b: not run yet (pending Asmit's decision at gate 1).

## Verdicts (gpt-oss-20b)
- H1: no difference detected (numpy/rest/plain vs google: +0.0 pp, CIs [-4.2, +4.2]).
- H2: no difference detected (parsed vs google: +0.0 pp [-5.6, +6.9]).
- Sensitivity: passes on `param` requests (summary_only -13.9 pp [-27.8, -2.8]), but the drop is
  entirely clarifying questions, not wrong tools.
- Ceiling: google 0.958 overall (< 0.97), but wrong-tool rate is 0 in every arm, so selection
  itself is at ceiling.
