# Dip-scan check-time compare: 12:00 vs ~11:10 (bar 30 vs bar 20)

Same fixed primary rules as SPCX dip scan. Only check/snap/step timing changes.

## Important caveat

- **check1110 (~11:10 ET, 5m bar index 20)** was picked by eyeballing the same SPCX matching days from the original 12:00 scan. **SPCX results for check1110 are in-sample / look-ahead on the choice of check time.**
- The **multi-stock universe** was not used to pick 11:10, so that pooled compare is the honest test of whether the shift generalizes.
- check1200 outputs are also kept as `*_check1200.*` snapshots from the prior run.

## Timing definition

| variant | check time ET | 5m bar index (from 09:30) | snap deadline |
|---|---|---:|---|
| check1200 | 12:00 | 30 | 12:00 |
| check1110 | 11:10 | 20 | 11:10 |

- universe: 73 tickers with cached 5m under `/workspace/backtester/multi_data`
- SPCX file: `/workspace/backtester/data_bands_SPCX_5m_v5.csv`

## SPCX alone (IN-SAMPLE for check1110 timing choice)

| variant | n matches | share close>open | share close>check | share close>first5m | avg m2c net | median m2c net |
|---|---:|---:|---:|---:|---:|---:|
| check1200 | 5 | 40.00% | 20.00% | 60.00% | -0.41% | -0.47% |
| check1110 | 4 | 75.00% | 75.00% | 75.00% | 0.19% | 0.18% |

all-days baseline (same for both; check metric uses that variant's check):

| variant | n days | share close>check | avg m2c net |
|---|---:|---:|---:|
| check1200 | 60 | 40.00% | -0.38% |
| check1110 | 60 | 46.67% | -0.19% |

SPCX matching dates:
- check1200: 2026-09-02, 2026-09-08, 2026-09-11, 2026-10-12, 2026-10-21
- check1110: 2026-08-26, 2026-08-27, 2026-10-15, 2026-10-21

## Multi-stock universe (HONEST test of the 11:10 shift)

| variant | n matches / all | share close>open | share close>check | share close>first5m | avg m2c net | median m2c net |
|---|---|---:|---:|---:|---:|---:|
| check1200 | 135 / 4380 | 54.07% | 49.63% | 71.85% | -0.03% | -0.02% |
| check1110 | 124 / 4380 | 58.87% | 55.65% | 72.58% | 0.06% | 0.08% |

all-days baselines:

| variant | n | share close>check | avg m2c net |
|---|---:|---:|---:|
| check1200 | 4380 | 46.32% | -0.07% |
| check1110 | 4380 | 47.83% | -0.06% |

### Significance (multi)

- **check1200**: close>check 67/135 vs baseline 46.32%; binomial p=0.4901. bootstrap 95% CI avg m2c net: -0.03% [-0.28%, 0.24%].
- **check1110**: close>check 69/124 vs baseline 47.83%; binomial p=0.08774. bootstrap 95% CI avg m2c net: 0.06% [-0.27%, 0.41%].

### Time split (multi matches)

| variant | half | match n | close>check | avg m2c net |
|---|---|---:|---:|---:|
| check1200 | first_matches (mid=2026-09-28) | 76 | 40.79% | -0.27% |
| check1200 | second_matches (mid=2026-09-28) | 59 | 61.02% | 0.28% |
| check1110 | first_matches (mid=2026-09-28) | 56 | 57.14% | -0.15% |
| check1110 | second_matches (mid=2026-09-28) | 68 | 54.41% | 0.24% |

### Top tickers by matches (multi)

**check1200**

| ticker | matches | close>check | close>first5m | avg m2c net |
|---|---:|---:|---:|---:|
| SOXL | 9 | 55.56% | 77.78% | -0.10% |
| SOFI | 8 | 50.00% | 75.00% | -0.27% |
| HOOD | 7 | 57.14% | 57.14% | -0.20% |
| SOXS | 7 | 28.57% | 71.43% | -0.31% |
| BB | 6 | 16.67% | 66.67% | -0.26% |
| INTC | 5 | 60.00% | 80.00% | 0.14% |
| C | 5 | 60.00% | 60.00% | 0.08% |
| SPCX | 5 | 20.00% | 60.00% | -0.41% |
| NKE | 4 | 75.00% | 100.00% | 0.76% |
| MRK | 4 | 75.00% | 100.00% | 0.51% |
| NOK | 4 | 75.00% | 50.00% | -0.12% |
| TQQQ | 4 | 50.00% | 50.00% | -0.13% |

**check1110**

| ticker | matches | close>check | close>first5m | avg m2c net |
|---|---:|---:|---:|---:|
| INTC | 12 | 41.67% | 58.33% | -0.65% |
| SOXS | 10 | 40.00% | 60.00% | -0.46% |
| SOXL | 9 | 55.56% | 88.89% | -0.16% |
| LCID | 5 | 80.00% | 100.00% | 2.27% |
| RBLX | 5 | 60.00% | 80.00% | 0.99% |
| COIN | 5 | 40.00% | 100.00% | 0.59% |
| HOOD | 5 | 60.00% | 60.00% | 0.09% |
| TQQQ | 4 | 100.00% | 100.00% | 0.77% |
| SPCX | 4 | 75.00% | 75.00% | 0.19% |
| U | 4 | 75.00% | 75.00% | 0.17% |
| BB | 4 | 50.00% | 75.00% | -0.29% |
| PYPL | 4 | 50.00% | 50.00% | -0.41% |

## Files kept

- prior 12:00 snapshots: `*_check1200.*` (from earlier multi/spcx runs)
- this compare summary: `/workspace/backtester/dip_scan_check_compare_summary.md`
- SPCX check1200: `/workspace/backtester/dip_scan_spcx_check1200.csv`
- multi check1200: days `/workspace/backtester/multi_dip_scan_days_check1200_v2.csv`, matches `/workspace/backtester/multi_dip_scan_matches_check1200_v2.csv`, per-ticker `/workspace/backtester/multi_dip_scan_per_ticker_check1200_v2.csv`, grid `/workspace/backtester/multi_dip_charts/multi_matches_grid_check1200_v2.png`
- SPCX check1110: `/workspace/backtester/dip_scan_spcx_check1110.csv`
- multi check1110: days `/workspace/backtester/multi_dip_scan_days_check1110.csv`, matches `/workspace/backtester/multi_dip_scan_matches_check1110.csv`, per-ticker `/workspace/backtester/multi_dip_scan_per_ticker_check1110.csv`, grid `/workspace/backtester/multi_dip_charts/multi_matches_grid_check1110.png`

## Blunt take

- multi check1200: matches 135/4380, close>check 49.63% (all 46.32%), avg m2c -0.03%.
- multi check1110: matches 124/4380, close>check 55.65% (all 47.83%), avg m2c 0.06%.
- binomial p-values vs each variant's own all-day rate: check1200 p=0.4901, check1110 p=0.08774.
- SPCX (in-sample for 11:10 choice): check1200 matches 5 avg m2c -0.41%; check1110 matches 4 avg m2c 0.19%.
- if multi check1110 is not clearly better than check1200 and not above baseline with a small p, the earlier check does not earn a claim.

Generated at (America/Chicago): 2026-11-06T15:21:19-06:00