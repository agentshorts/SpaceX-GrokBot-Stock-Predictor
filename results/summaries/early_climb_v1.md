# Early-climb scan v1

New versioned scan. Prior dip-scan files untouched.

## Caveat

SPCX Sep 8 / Sep 11 (GOOD) and Oct 12 / Oct 21 (BAD) are the examples used to state these rules, so SPCX classification of those four dates is in-sample. The multi-ticker pool is the honest generalization check.

## Primary rules (fixed)

- Window: 09:30 to 10:30 ET (5m bars with start time in that range).
- Climb measured from the early-window **low** to the subsequent high (Captain GOOD days open with a dip then a ~2% stepped recovery; cropped charts show that climb).
- **GOOD**: rise from low in **[1%, 2.6%]** (~2.5% with 0.1pp tolerance so Sep 8's 2.58% counts); price at 10:30 open keeps >= **50%** of that rise; close-to-close up-step share from the low bar through 10:25 **> 50%**; no single |close step| > **40%** of the total rise.
- **BAD**: rise from low **> 3%**, OR one |close step| > **50%** of the rise (with rise>=1%), OR rise>=1% but keep-frac at 10:30 open **< 30%** (fade).
- Else **NEUTRAL**. BAD wins if both flags fire.
- Trade: **buy 10:30 bar open**, **sell 12:00 bar close**, **1 bp/side**. Classification uses only bars before 10:30 (no lookahead into the entry bar).
- Sensitivity (informational): GOOD rise bands 0.5-1.5%, 1-2.5% (primary), 1.5-3%.

- data window: 2026-08-14 09:30:00-04:00 -> 2026-11-06 15:55:00-05:00; SPCX `/workspace/backtester/data_bands_SPCX_5m_v5.csv`; multi n=73.

## SPCX example verification (in-sample labels)

| date | expected | got | ok | rise from low | keep | up share | max bar frac | ret net |
|---|---|---|---|---:|---:|---:|---:|---:|
| 2026-09-08 | GOOD | GOOD | True | 2.58% | 0.72 | 0.67 | 0.31 | 4.07% |
| 2026-09-11 | GOOD | GOOD | True | 2.47% | 0.62 | 0.60 | 0.24 | 0.30% |
| 2026-10-12 | BAD | BAD | True | 3.86% | 0.51 | 0.64 | 0.28 | 0.17% |
| 2026-10-21 | BAD | BAD | True | 5.04% | 0.44 | 0.44 | 0.50 | 0.91% |

## SPCX alone

| group | n | hit rate (sell>buy) | avg ret net | median ret net |
|---|---:|---:|---:|---:|
| GOOD | 14 | 78.57% | 0.67% | 0.51% |
| BAD | 23 | 47.83% | -0.09% | -0.20% |
| ALL | 60 | 55.00% | 0.12% | 0.06% |

bootstrap 95% CI of avg ret net:
- GOOD: 0.67%  [-0.09%, 1.45%]
- BAD: -0.09%  [-0.40%, 0.22%]
- ALL: 0.12%  [-0.13%, 0.39%]
- binomial GOOD hit rate vs ALL: 11/14 vs baseline 55.00%; two-sided p=0.1058.

time split (mid=2026-09-28):
| half | group | n | hit | avg ret net |
|---|---|---:|---:|---:|
| first | good | 9 | 88.89% | 1.12% |
| first | bad | 10 | 60.00% | -0.00% |
| first | all | 31 | 58.06% | 0.26% |
| second | good | 5 | 60.00% | -0.15% |
| second | bad | 13 | 38.46% | -0.16% |
| second | all | 29 | 51.72% | -0.02% |

## Multi universe (honest test)

| group | n | hit rate (sell>buy) | avg ret net | median ret net |
|---|---:|---:|---:|---:|
| GOOD | 741 | 51.01% | -0.04% | -0.00% |
| BAD | 879 | 48.81% | -0.01% | -0.05% |
| ALL | 4380 | 49.02% | -0.02% | -0.02% |

bootstrap 95% CI of avg ret net:
- GOOD: -0.04%  [-0.11%, 0.03%]
- BAD: -0.01%  [-0.11%, 0.08%]
- ALL: -0.02%  [-0.05%, 0.01%]
- binomial GOOD hit rate vs ALL: 378/741 vs baseline 49.02%; two-sided p=0.2867.

time split (mid=2026-09-28):
| half | group | n | hit | avg ret net |
|---|---|---:|---:|---:|
| first | good | 397 | 49.62% | -0.03% |
| first | bad | 395 | 50.13% | 0.03% |
| first | all | 2263 | 47.86% | -0.02% |
| second | good | 344 | 52.62% | -0.06% |
| second | bad | 484 | 47.73% | -0.05% |
| second | all | 2117 | 50.26% | -0.02% |

## Sensitivity (GOOD rise band only; other rules fixed)

### SPCX
| band | n GOOD | GOOD hit | GOOD avg ret | ALL hit | ALL avg ret |
|---|---:|---:|---:|---:|---:|
| 0.5-1.5% | 3 | 66.67% | -0.21% | 55.00% | 0.12% |
| 1-2.6% | 14 | 78.57% | 0.67% | 55.00% | 0.12% |
| 1.5-3% | 15 | 66.67% | 0.57% | 55.00% | 0.12% |

### Multi
| band | n GOOD | GOOD hit | GOOD avg ret | ALL hit | ALL avg ret |
|---|---:|---:|---:|---:|---:|
| 0.5-1.5% | 594 | 49.83% | -0.00% | 49.02% | -0.02% |
| 1-2.6% | 741 | 51.01% | -0.04% | 49.02% | -0.02% |
| 1.5-3% | 547 | 48.26% | -0.10% | 49.02% | -0.02% |

- GOOD grid png: `/workspace/backtester/early_climb_charts/early_climb_good_grid_v1_v2.png`

## Blunt take

- multi GOOD n=741 hit 51.01% avg -0.04% vs ALL hit 49.02% avg -0.02%.
- binomial p=0.2867; GOOD m2c CI [-0.11%, 0.03%].
- example verification all correct: True.

Generated at (America/Chicago): 2026-11-06T15:30:39-06:00