# SPCX castle opening scan v1

Visual detector only. No edge claims beyond counts.

## Rules (fixed)

- Measured on the 5m **close step path**. Base = first bar close (Captain crop starts ~147 after the open print, not the print open).
- Peak = max close among bars **4..15** (0-based).
- Rise base->peak in **[1%, 3.5%]**; up-step share before peak **> 55%**; max |step| before peak **< 45%** of rise.
- By bar **20** (index 19, ~11:05): give-back from peak **>= 60%** of rise; down-step share after peak **>= 50%** (Sep 11 reference descent is jagged at exactly 50%; a strict >55% would exclude it).
- Near-miss: peak+rise ok and at least 4/6 conditions true.
- Data: `/workspace/backtester/data_bands_SPCX_5m_v5.csv` RTH 5m, 2026-08-14 09:30:00-04:00 -> 2026-11-06 15:55:00-05:00.

## Sep 11 verification

- label=MATCH peak_i=7 (2026-09-11 10:05:00-04:00) base=146.96 peak=149.19 rise=1.51% up_share=0.71 max_step_frac=0.30 giveback=1.22 down_share=0.50
- failed: none
- MATCH expected: YES

## Matches (5 of 60 days)

| date | base | peak | peak time | rise | giveback | close | close vs open | 11:10->close | band before | band after |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-26 | 135.65 | 138.97 | 2026-08-26 09:50:00-04:00 | 2.44% | 0.85 | 139.54 | 1.90% | 2.38% | 0.393 | 0.223 |
| 2026-09-10 | 149.52 | 153.90 | 2026-09-10 09:55:00-04:00 | 2.93% | 0.89 | 148.18 | 2.12% | -1.60% | 0.508 | 0.322 |
| 2026-09-11 | 146.96 | 149.19 | 2026-09-11 10:05:00-04:00 | 1.51% | 1.22 | 151.14 | 1.04% | 3.23% | 0.437 | 0.223 |
| 2026-09-30 | 149.29 | 152.10 | 2026-09-30 10:20:00-04:00 | 1.89% | 0.82 | 150.94 | 1.55% | 0.69% | 0.311 | 0.189 |
| 2026-10-01 | 151.82 | 153.66 | 2026-10-01 10:35:00-04:00 | 1.21% | 0.76 | 148.10 | -1.56% | -3.02% | 0.312 | 0.241 |

## Near-misses (19)

| date | rise | giveback | up | down | max_step | failed |
|---|---:|---:|---:|---:|---:|---|
| 2026-08-18 | 1.84% | 0.47 | 0.64 | 0.62 | 0.79 | max_step_ok,giveback_ok |
| 2026-08-25 | 1.50% | 0.68 | 0.62 | 1.00 | 0.55 | max_step_ok |
| 2026-08-28 | 2.36% | 0.08 | 0.67 | 0.50 | 0.52 | max_step_ok,giveback_ok |
| 2026-09-01 | 2.24% | 0.22 | 0.71 | 0.42 | 0.40 | giveback_ok,down_share_ok |
| 2026-09-03 | 3.48% | 0.23 | 0.64 | 0.75 | 0.49 | max_step_ok,giveback_ok |
| 2026-09-08 | 2.14% | 0.04 | 0.78 | 0.50 | 0.37 | giveback_ok |
| 2026-09-17 | 1.26% | 0.75 | 0.62 | 0.45 | 0.47 | max_step_ok,down_share_ok |
| 2026-09-21 | 2.24% | 0.33 | 0.73 | 0.50 | 0.48 | max_step_ok,giveback_ok |
| 2026-09-22 | 2.02% | 0.16 | 0.73 | 0.50 | 0.33 | giveback_ok |
| 2026-09-29 | 1.68% | 0.57 | 0.60 | 0.75 | 0.57 | max_step_ok,giveback_ok |
| 2026-10-12 | 2.76% | 0.53 | 1.00 | 0.64 | 0.39 | giveback_ok |
| 2026-10-16 | 1.66% | 0.83 | 0.60 | 0.75 | 0.60 | max_step_ok |
| 2026-10-20 | 2.67% | 0.21 | 0.71 | 0.60 | 0.23 | giveback_ok |
| 2026-10-21 | 2.12% | 0.98 | 0.57 | 0.67 | 1.17 | max_step_ok |
| 2026-10-23 | 3.13% | 0.46 | 0.69 | 1.00 | 0.30 | giveback_ok |
| 2026-10-26 | 1.24% | -0.27 | 0.67 | 0.50 | 0.56 | max_step_ok,giveback_ok |
| 2026-10-29 | 2.06% | 0.16 | 0.75 | 0.43 | 0.45 | giveback_ok,down_share_ok |
| 2026-11-02 | 3.40% | 0.22 | 0.67 | 0.57 | 0.48 | max_step_ok,giveback_ok |
| 2026-11-03 | 1.84% | 0.33 | 0.75 | 0.57 | 0.30 | giveback_ok |

## Files

- grid: `/workspace/backtester/castle_charts_v1/castle_matches_grid_v1.png`
- near-miss grid: `/workspace/backtester/castle_charts_v1/castle_nearmiss_grid_v1.png`
- day: `/workspace/backtester/castle_charts_v1/castle_2026-08-26.png`
- day: `/workspace/backtester/castle_charts_v1/castle_2026-09-10.png`
- day: `/workspace/backtester/castle_charts_v1/castle_2026-09-11.png`
- day: `/workspace/backtester/castle_charts_v1/castle_2026-09-30.png`
- day: `/workspace/backtester/castle_charts_v1/castle_2026-10-01.png`
- matches csv: `/workspace/backtester/castle_matches_v1.csv`
- near csv: `/workspace/backtester/castle_nearmiss_v1.csv`
- all days csv: `/workspace/backtester/castle_all_days_v1.csv`

Generated at (America/Chicago): 2026-11-06T15:36:07-06:00