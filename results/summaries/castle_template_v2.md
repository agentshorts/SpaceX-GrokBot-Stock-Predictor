# SPCX castle template match v2 (peak rise <= 5%)

v1 untouched. Same templates Sep 11 + Sep 30. Added Captain peak-size filter.

## Filter interpretation

- **Primary (used to keep/drop):** within 09:30-11:15 BOTH must hold: (1) max local-peak rise from its local base / base <= 5%; (2) max excursion (window max high - first-bar close) / first close <= 5%.
- **Secondary (reported):** the excursion metric alone, plus max-close rise from first close.
- Similarity same as v1: pearson on z-scored pct paths, DTW window=3, match also needs corr >= 0.7.
- Primary drops 1 non-template day in this 60-day sample (local-base alone would drop 0; excursion alone drops the same 1).

## Ranked top after filter (templates + top 10 survivors)

| rank | date | role | tmpl | corr | max castle rise | sec hi rise | c/o | 11:15->close |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 1 | 2026-09-11 | template | 2026-09-11 | 1.000 | 1.22% | 2.47% | 1.04% | 2.82% |
| 2 | 2026-09-30 | template | 2026-09-30 | 1.000 | 0.97% | 1.98% | 1.55% | 0.56% |
| 3 | 2026-11-04 | match | 2026-09-30 | 0.764 | 3.04% | 4.92% | 1.94% | -0.55% |
| 4 | 2026-09-17 | match | 2026-09-30 | 0.763 | 0.93% | 2.01% | 0.67% | 0.48% |
| 5 | 2026-09-15 | top | 2026-09-11 | 0.674 | 1.24% | 1.32% | -3.31% | -1.37% |
| 6 | 2026-10-21 | top | 2026-09-11 | 0.646 | 2.51% | 2.67% | -0.80% | -1.38% |
| 7 | 2026-08-26 | top | 2026-09-11 | 0.588 | 2.44% | 2.85% | 1.90% | 2.66% |
| 8 | 2026-09-09 | top | 2026-09-11 | 0.570 | 0.33% | 0.71% | -2.91% | -0.05% |
| 9 | 2026-10-02 | top | 2026-09-30 | 0.566 | 3.47% | 4.42% | 6.30% | 1.34% |
| 10 | 2026-10-29 | top | 2026-09-30 | 0.564 | 1.47% | 2.18% | 1.06% | -0.26% |
| 11 | 2026-09-03 | top | 2026-09-30 | 0.548 | 2.82% | 3.78% | 5.89% | 0.26% |
| 12 | 2026-10-16 | top | 2026-09-30 | 0.547 | 1.60% | 2.02% | 0.47% | 0.38% |

## Matches (corr>=0.7 and rise<=5%): 2

| date | tmpl | corr | castle rise | 11:15->close | close>11:15 |
|---|---|---:|---:|---:|---|
| 2026-11-04 | 2026-09-30 | 0.764 | 3.04% | -0.55% | False |
| 2026-09-17 | 2026-09-30 | 0.763 | 0.93% | 0.48% | True |

## Dropped by primary 5% filter (1 days)

| date | corr | max castle rise | sec hi rise | note |
|---|---:|---:|---:|---|
| 2026-08-17 | 0.376 | 4.61% | 5.52% |  |

## After 11:15 (descriptive)

| group | n | share close>11:15 | avg 11:15->close | median |
|---|---:|---:|---:|---:|
| templates | 2 | 100.00% | 1.69% | 1.69% |
| matches_corr>=0.7_and_rise<=5pct | 2 | 50.00% | -0.03% | -0.03% |
| top10_survivors | 10 | 50.00% | 0.15% | 0.10% |
| all_survivors | 57 | 42.11% | -0.29% | -0.12% |
| all_nontemplates_unfiltered | 58 | 41.38% | -0.31% | -0.13% |

SMALL SAMPLE: 2 filtered matches in ~60 days. not an edge claim.

## Files

- grid: `/workspace/backtester/castle_template_v2/castle_template_top_grid_v2_final.png`
- ranked survivors csv: `/workspace/backtester/castle_template_ranked_v2_v3.csv`
- dropped csv: `/workspace/backtester/castle_template_dropped_v2_v3.csv`
- day: `/workspace/backtester/castle_template_v2/tmpl2_TEMPLATE_2026-09-11_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_TEMPLATE_2026-09-30_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-11-04_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-09-17_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-09-15_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-10-21_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-08-26_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-09-09_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-10-02_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-10-29_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-09-03_v3.png`
- day: `/workspace/backtester/castle_template_v2/tmpl2_2026-10-16_v3.png`

Generated at (America/Chicago): 2026-11-06T15:48:51-06:00