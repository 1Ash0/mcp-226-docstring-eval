
## openai/gpt-oss-20b  (432 calls, tool_use_failed=22)

### requests: all
| arm | accuracy [95% CI] | n | diff vs google [95% CI] |
|---|---|---|---|
| google | 0.958 [0.889, 1.000] | n=72 | (reference) |
| numpy | 0.958 [0.903, 1.000] | n=72 | +0.0 pp [-4.2, +4.2] |
| rest | 0.958 [0.889, 1.000] | n=72 | +0.0 pp [-4.2, +4.2] |
| plain | 0.958 [0.903, 1.000] | n=72 | +0.0 pp [-4.2, +4.2] |
| parsed | 0.958 [0.917, 1.000] | n=72 | +0.0 pp [-5.6, +6.9] |
| summary_only | 0.903 [0.806, 0.972] | n=72 | -5.6 pp [-13.9, +1.4] |

### requests: summary
| arm | accuracy [95% CI] | n | diff vs google [95% CI] |
|---|---|---|---|
| google | 0.944 [0.833, 1.000] | n=36 | (reference) |
| numpy | 0.972 [0.917, 1.000] | n=36 | +2.8 pp [+0.0, +8.3] |
| rest | 0.972 [0.917, 1.000] | n=36 | +2.8 pp [+0.0, +8.3] |
| plain | 0.972 [0.917, 1.000] | n=36 | +2.8 pp [+0.0, +8.3] |
| parsed | 1.000 [1.000, 1.000] | n=36 | +5.6 pp [+0.0, +16.7] |
| summary_only | 0.972 [0.917, 1.000] | n=36 | +2.8 pp [+0.0, +8.3] |

### requests: param
| arm | accuracy [95% CI] | n | diff vs google [95% CI] |
|---|---|---|---|
| google | 0.972 [0.917, 1.000] | n=36 | (reference) |
| numpy | 0.944 [0.861, 1.000] | n=36 | -2.8 pp [-8.3, +0.0] |
| rest | 0.944 [0.833, 1.000] | n=36 | -2.8 pp [-8.3, +0.0] |
| plain | 0.944 [0.861, 1.000] | n=36 | -2.8 pp [-8.3, +0.0] |
| parsed | 0.917 [0.833, 1.000] | n=36 | -5.6 pp [-13.9, +0.0] |
| summary_only | 0.833 [0.667, 0.972] | n=36 | -13.9 pp [-27.8, -2.8] |

errors (arm, task, gold -> picked):
  parsed       A2p s2 lookup_product -> None
  summary_only B3p s2 disk_stats -> None
  parsed       D2p s2 attach_file -> None
  google       D2s s1 attach_file -> None
  google       D2s s2 attach_file -> None
  numpy        D2s s1 attach_file -> None
  plain        D2s s1 attach_file -> None
  rest         D2s s1 attach_file -> None
  summary_only D2s s1 attach_file -> None
  numpy        D3p s1 share_file -> None
  plain        D3p s2 share_file -> None
  summary_only D3p s1 share_file -> None
  google       F2p s2 convert_units -> None
  numpy        F2p s2 convert_units -> None
  parsed       F2p s2 convert_units -> None
  plain        F2p s2 convert_units -> None
  rest         F2p s1 convert_units -> None
  rest         F2p s2 convert_units -> None
  summary_only F2p s1 convert_units -> None
  summary_only F2p s2 convert_units -> None
  summary_only F3p s1 convert_timezone -> None
  summary_only F3p s2 convert_timezone -> None
