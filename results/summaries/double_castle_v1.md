# SPCX double-castle scan v1

Counts only. No edge claims.

## Rules (fixed)

- Window: 09:30 to 12:00 ET on SPCX 5m close step path.
- One castle from any base bar: span 6-15 bars; peak offset 2-10; rise from base close to peak close in [0.7%, 5%] (floor 0.7% so a smaller second castle can count); up-step share before peak > 55%; max |step| < 45% of rise; give-back >= 60% of rise; down-step share after peak >= 50%.
- Distinct: second base at or after first end; peaks at least 3 bars apart; non-overlapping spans. Do not require second smaller; report rise2/rise1.
- Greedy method: among valid castles, take earliest-base castle (prefer base by ~10:30); then pick highest-scoring valid second castle after the first ends. Score = rise * giveback * up_share * down_share * (1 - max_step_frac).
- Near-miss: one clean castle by noon, and either no valid second or a second that fails exactly one soft condition (up/max_step/giveback/down).
- Data: `/workspace/backtester/data_bands_SPCX_5m_v5.csv`.

## Matches (4 of 60 days)

| date | rise1 | rise2 | ratio | c1 peak | c2 peak | close vs open | 12:00->close | 11:10->close |
|---|---:|---:|---:|---|---|---:|---:|---:|
| 2026-08-19 | 0.94% | 1.31% | 1.39 | 2026-08-19 10:40:00-04:00 | 2026-08-19 11:25:00-04:00 | -3.67% | -0.12% | -0.40% |
| 2026-09-22 | 1.10% | 0.83% | 0.76 | 2026-09-22 09:55:00-04:00 | 2026-09-22 10:50:00-04:00 | 2.01% | 1.30% | 0.66% |
| 2026-10-12 | 2.76% | 1.23% | 0.45 | 2026-10-12 09:55:00-04:00 | 2026-10-12 10:35:00-04:00 | -0.74% | -0.50% | 0.01% |
| 2026-10-16 | 1.28% | 1.02% | 0.80 | 2026-10-16 10:10:00-04:00 | 2026-10-16 11:45:00-04:00 | 0.47% | 0.02% | 0.47% |

## Near-misses (20)

- with almost-second castle: 4; one castle only: 16.

## Files

- grid: `/workspace/backtester/double_castle_charts_v1/double_castle_matches_grid_v1.png`
- near-miss grid: `/workspace/backtester/double_castle_charts_v1/double_castle_nearmiss_grid_v1.png`
- day: `/workspace/backtester/double_castle_charts_v1/double_castle_2026-08-19.png`
- day: `/workspace/backtester/double_castle_charts_v1/double_castle_2026-09-22.png`
- day: `/workspace/backtester/double_castle_charts_v1/double_castle_2026-10-12.png`
- day: `/workspace/backtester/double_castle_charts_v1/double_castle_2026-10-16.png`
- matches csv: `/workspace/backtester/double_castle_matches_v1.csv`
- near csv: `/workspace/backtester/double_castle_nearmiss_v1.csv`

Generated at (America/Chicago): 2026-11-06T15:40:06-06:00