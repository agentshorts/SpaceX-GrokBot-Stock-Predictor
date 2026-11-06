# SPCX early-dip snap-back midday-step scan

Plain fixed rules. No model. No parameter optimization.
Captain example chart saved at `/workspace/backtester/inputs/captain_dip_example.png`.

## Primary rules (stated up front)

1. Big early dip (first 30 min after 09:30 ET): session low in that window is at least **1.0%** below the open, AND early-window volume ratio >= **2.0x** average bar volume (or the dip bar is top-3 volume of the day). Note if dip bar is red.
2. Snap back by **12:00 ET**: price traded at least halfway back from dip low toward the open (half-dip recovery). Also tracked: recovery back above the open.
3. Midday stepping at **12:00 ET** check: close at/above dip low by **0.2%**, last **6** bars have up-step share **> 50%**, and mean |diff| of those bars <= day median |diff| so far (narrow).
4. Midday-to-close % uses check close -> day close with **1 bp/side** cost.

Sensitivity (not used to pick a winner): dip 0.5%/1.0%/1.5%; check 11:00/12:00/12:30; snap half-dip vs above-open.

## 5m results

- data: `/workspace/backtester/data_bands_SPCX_5m_v5.csv` | bars=4680 | days=60 | 2026-08-14 09:30:00-04:00 -> 2026-11-06 15:55:00-05:00
- SAMPLE SIZE WARNING: only **60** trading days. any hit rate here is fragile.

### Matching days

| date | open | dip low | dip time | dip% | red? | check px | close | close>open | close>check | m2c gross | m2c net |
|---|---:|---:|---|---:|---|---:|---:|---|---|---:|---:|
| 2026-09-02 | 142.66 | 138.62 | 2026-09-02 09:55:00-04:00 | 2.83% | True | 141.36 | 140.72 | False | False | -0.45% | -0.47% |
| 2026-09-08 | 148.99 | 145.14 | 2026-09-08 09:40:00-04:00 | 2.59% | False | 153.87 | 153.46 | True | False | -0.27% | -0.29% |
| 2026-09-11 | 149.59 | 145.92 | 2026-09-11 09:35:00-04:00 | 2.45% | False | 148.62 | 151.14 | True | True | 1.70% | 1.68% |
| 2026-10-12 | 164.70 | 160.85 | 2026-10-12 09:30:00-04:00 | 2.34% | True | 164.30 | 163.48 | False | False | -0.50% | -0.52% |
| 2026-10-21 | 160.56 | 158.20 | 2026-10-21 09:40:00-04:00 | 1.47% | True | 163.25 | 159.28 | False | False | -2.43% | -2.45% |

### Summary vs all-days baseline

| group | n | share close>open | share close>check | avg m2c net | median m2c net |
|---|---:|---:|---:|---:|---:|
| matches | 5 | 40.00% | 20.00% | -0.41% | -0.47% |
| all_days | 60 | 53.33% | 40.00% | -0.38% | -0.30% |
| near_miss_1_2 | 13 | 30.77% | 30.77% | -0.41% | -0.31% |

### Near-miss days (rules 1+2, failed 3)

| date | dip% | snap half | snap>open | above dip | up share | narrow | close>open | m2c net |
|---|---:|---|---|---|---:|---|---|---:|
| 2026-08-21 | 2.30% | True | True | True | 0.67 | False | True | -0.01% |
| 2026-08-26 | 1.34% | True | True | True | 0.67 | False | True | 2.14% |
| 2026-08-27 | 1.08% | True | True | True | 0.83 | False | True | -0.62% |
| 2026-09-09 | 1.30% | True | True | False | 0.50 | False | False | 0.42% |
| 2026-09-15 | 2.85% | True | False | False | 0.17 | False | False | -0.57% |
| 2026-09-24 | 1.58% | True | True | True | 0.67 | False | False | -0.31% |
| 2026-10-08 | 1.31% | True | False | False | 0.33 | True | False | -1.51% |
| 2026-10-09 | 1.93% | True | False | True | 0.33 | True | False | -0.21% |
| 2026-10-14 | 1.91% | True | False | True | 0.50 | True | False | -0.81% |
| 2026-10-15 | 4.24% | True | True | True | 0.17 | True | True | 1.49% |
| 2026-10-19 | 1.10% | True | True | True | 0.50 | True | False | -1.54% |
| 2026-10-22 | 1.91% | True | False | False | 0.33 | True | False | -3.66% |
| 2026-10-23 | 2.60% | True | True | True | 0.50 | True | False | -0.15% |

### Sensitivity (informational only)

dip pct:
| dip pct | n match | match avg m2c net | match share close>check | all-day avg m2c net |
|---:|---:|---:|---:|---:|
| 0.50% | 9 | -0.72% | 33.33% | -0.38% |
| 1.00% | 5 | -0.41% | 20.00% | -0.38% |
| 1.50% | 4 | 0.10% | 25.00% | -0.38% |

check time:
| check | n match | match avg m2c net | match share close>check | all-day avg m2c net |
|---|---:|---:|---:|---:|
| 11:00:00 | 5 | 0.82% | 80.00% | -0.17% |
| 12:00:00 | 5 | -0.41% | 20.00% | -0.38% |
| 12:30:00 | 1 | 1.60% | 100.00% | -0.28% |

snap mode:
| mode | n match | match avg m2c net | match share close>check |
|---|---:|---:|---:|
| half_dip | 5 | -0.41% | 20.00% |
| above_open | 3 | -1.09% | 0.00% |

- grid png: `/workspace/backtester/dip_scan_charts/spcx_5m_matches_grid.png`

## 15m results

- data: `/workspace/backtester/data_SPCX_15m.csv` | bars=1559 | days=60 | 2026-08-14 09:30:00-04:00 -> 2026-11-06 15:30:00-05:00
- SAMPLE SIZE WARNING: only **60** trading days. any hit rate here is fragile.

### Matching days

| date | open | dip low | dip time | dip% | red? | check px | close | close>open | close>check | m2c gross | m2c net |
|---|---:|---:|---|---:|---|---:|---:|---|---|---:|---:|
| 2026-08-21 | 134.32 | 131.22 | 2026-08-21 09:30:00-04:00 | 2.30% | True | 136.33 | 136.94 | True | True | 0.45% | 0.43% |
| 2026-09-02 | 142.66 | 138.62 | 2026-09-02 09:45:00-04:00 | 2.83% | True | 141.39 | 140.72 | False | False | -0.47% | -0.49% |
| 2026-10-19 | 149.25 | 147.61 | 2026-10-19 09:45:00-04:00 | 1.10% | True | 150.18 | 147.97 | False | False | -1.47% | -1.49% |

### Summary vs all-days baseline

| group | n | share close>open | share close>check | avg m2c net | median m2c net |
|---|---:|---:|---:|---:|---:|
| matches | 3 | 33.33% | 33.33% | -0.52% | -0.49% |
| all_days | 60 | 53.33% | 38.33% | -0.37% | -0.39% |
| near_miss_1_2 | 16 | 37.50% | 50.00% | -0.13% | -0.05% |

### Near-miss days (rules 1+2, failed 3)

| date | dip% | snap half | snap>open | above dip | up share | narrow | close>open | m2c net |
|---|---:|---|---|---|---:|---|---|---:|
| 2026-08-26 | 1.34% | True | True | True | 0.33 | True | True | 2.26% |
| 2026-08-27 | 1.08% | True | True | True | 0.50 | True | True | -0.14% |
| 2026-09-08 | 2.59% | True | True | True | 0.67 | False | True | 0.32% |
| 2026-09-09 | 1.30% | True | True | False | 0.33 | False | False | 0.55% |
| 2026-09-11 | 2.45% | True | False | True | 0.83 | False | True | 1.71% |
| 2026-09-15 | 2.85% | True | False | False | 0.33 | True | False | -0.24% |
| 2026-09-24 | 1.58% | True | True | True | 0.50 | False | False | 0.04% |
| 2026-10-08 | 1.31% | True | False | False | 0.33 | False | False | -1.53% |
| 2026-10-09 | 1.93% | True | False | False | 0.50 | False | False | 0.10% |
| 2026-10-12 | 2.34% | True | True | True | 0.50 | True | False | -0.45% |
| 2026-10-14 | 1.91% | True | False | True | 0.33 | True | False | -0.62% |
| 2026-10-15 | 4.24% | True | True | True | 0.50 | True | True | 1.54% |
| 2026-10-20 | 1.96% | True | True | True | 0.50 | True | True | 0.33% |
| 2026-10-21 | 1.47% | True | True | True | 0.33 | False | False | -2.24% |
| 2026-10-22 | 1.91% | True | False | False | 0.33 | False | False | -3.35% |
| 2026-10-23 | 2.60% | True | True | True | 0.33 | True | False | -0.27% |

### Sensitivity (informational only)

dip pct:
| dip pct | n match | match avg m2c net | match share close>check | all-day avg m2c net |
|---:|---:|---:|---:|---:|
| 0.50% | 7 | -0.95% | 28.57% | -0.37% |
| 1.00% | 3 | -0.52% | 33.33% | -0.37% |
| 1.50% | 2 | -0.03% | 50.00% | -0.37% |

check time:
| check | n match | match avg m2c net | match share close>check | all-day avg m2c net |
|---|---:|---:|---:|---:|
| 11:00:00 | 3 | 0.37% | 66.67% | -0.18% |
| 12:00:00 | 3 | -0.52% | 33.33% | -0.37% |
| 12:30:00 | 3 | -0.01% | 66.67% | -0.25% |

snap mode:
| mode | n match | match avg m2c net | match share close>check |
|---|---:|---:|---:|
| half_dip | 3 | -0.52% | 33.33% |
| above_open | 2 | -0.53% | 50.00% |

- grid png: `/workspace/backtester/dip_scan_charts/spcx_15m_matches_grid.png`

## Blunt take

- 5m primary: 5 matching days out of 60. that is a tiny sample; do not trust a few winners.
- match avg midday-to-close net -0.41% vs all-days -0.38% (diff -0.03%).
- match share close>check 20.00% vs all-days 40.00%.
- this is a descriptive scan of a hand-stated pattern, not a backtested edge. sensitivity rows are for honesty, not for cherry-picking.

Generated at (America/Chicago): 2026-11-06T15:14:06-06:00