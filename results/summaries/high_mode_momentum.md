# High-mode momentum backtest summary

## SPCX identity (yfinance)

- symbol: `SPCX`
- longName: Space Exploration Technologies Corp.
- shortName: Space Exploration Technologies 
- quoteType: EQUITY
- exchange: NMS
- currency: USD
- yfinance last close: 134.41000366210938
- Captain chart close (from screenshot): ~134.49
- price match within $1: True
- first available daily bar: 2026-06-12 00:00:00-04:00
- daily bars available (max): 103
- chart note: Captain charts are step charts with H:134.74 L:134.35 C:134.49. yfinance last close is near that level.

History warning: SPCX daily history starts mid-2026, so sample size is short. Intraday 15m/1h are further capped by yfinance limits (~60d for 15m, ~730d for 1h).

## Method

- Strategy: consecutive close diffs; over lookback L, go LONG if positives outweigh negatives by count share > k, or by magnitude sum(pos) > ratio * sum(|neg|).
- Entry: next bar open after signal. Exit: fixed hold H bars at close, or earlier on signal flip.
- Long-only vs flat. No overlapping positions.
- Costs: 1 bp slippage per side, 0 commission (stocks/ETFs). Also report 2x cost stress.
- Sweep size per ticker x bar: 192 configs (lookbacks [4, 8, 12, 24], holds [1, 2, 4, 8], count k [0.5, 0.6, 0.7], mag ratios [1.0, 1.5, 2.0], exits ['fixed_hold', 'signal_flip']). Multiple-testing risk is real.
- Validation: chronological first 70% train / last 30% test. Pick best on TRAIN by total net return requiring >= 30 trades, then report that config on TEST.
- Random baseline: 1000 random-entry runs with same trade count and hold on the test window; report strategy percentile.
- Walk-forward: 4 expanding folds on 1h and 1d where bar count allows.
- Data source: yfinance. SPY/QQQ/SPCX intraday are typically regular hours only.

## Data ranges actually fetched

| ticker | interval | period requested | n_bars | start | end | last_close |
|---|---|---|---:|---|---|---:|
| SPCX | 15m | 60d | 1559 | 2026-08-14 09:30:00-04:00 | 2026-11-06 15:30:00-05:00 | 134.51499938964844 |
| SPCX | 1h | 730d | 699 | 2026-06-12 11:30:00-04:00 | 2026-11-06 15:30:00-05:00 | 134.3800048828125 |
| SPCX | 1d | max | 103 | 2026-06-12 00:00:00-04:00 | 2026-11-06 00:00:00-05:00 | 134.30999755859375 |
| SPY | 15m | 60d | 1559 | 2026-08-14 09:30:00-04:00 | 2026-11-06 15:30:00-05:00 | 737.0449829101562 |
| SPY | 1h | 730d | 5055 | 2023-12-11 09:30:00-05:00 | 2026-11-06 15:30:00-05:00 | 737.0599975585938 |
| SPY | 1d | max | 8502 | 1993-01-29 00:00:00-05:00 | 2026-11-06 00:00:00-05:00 | 737.1400146484375 |
| QQQ | 15m | 60d | 1560 | 2026-08-14 09:30:00-04:00 | 2026-11-06 15:45:00-05:00 | 657.8400268554688 |
| QQQ | 1h | 730d | 5058 | 2023-12-11 09:30:00-05:00 | 2026-11-06 15:30:00-05:00 | 657.8400268554688 |
| QQQ | 1d | max | 6960 | 1999-03-10 00:00:00-05:00 | 2026-11-06 00:00:00-05:00 | 658.114990234375 |

## Results table (chosen on train, reported on test)

| ticker | bar | status | params | train trades | train ret | train MDD | test trades | test hit | test avg win | test avg loss | test ret | test MDD | test B&H | rand pctile | test 2x ret | flags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| SPCX | 15m | ok | L=8 H=8 fixed_hold magnitude@1.0 | 84 | 29.09% | -6.83% | 37 | 37.84% | 1.22% | -1.24% | -11.41% | -17.96% | -14.41% | 36.6 | -12.06% | OVERFIT_WARNING: test net return much worse than train; BELOW_RANDOM_MEDIAN on test (percentile < 50); NEGATIVE_TEST_RETURN |
| SPCX | 1h | ok | L=4 H=1 fixed_hold magnitude@2.0 | 91 | 42.42% | -4.53% | 31 | 32.26% | 0.53% | -0.57% | -6.62% | -6.64% | -9.53% | 17.9 | -7.20% | OVERFIT_WARNING: test net return much worse than train; BELOW_RANDOM_MEDIAN on test (percentile < 50); NEGATIVE_TEST_RETURN |
| SPCX | 1d | no_eligible_config |  |  |  |  |  |  |  |  |  |  | -9.50% |  |  | no config reached >= 30 trades on train (72 bars). Multiple-testing risk still applies to the full sweep of 192 configs. |
| SPY | 15m | ok | L=4 H=8 fixed_hold magnitude@2.0 | 81 | 2.45% | -2.26% | 33 | 42.42% | 0.26% | -0.31% | -2.26% | -3.68% | -5.32% | 70.3 | -2.90% | NEGATIVE_TEST_RETURN |
| SPY | 1h | ok | L=4 H=8 fixed_hold magnitude@2.0 | 287 | 23.68% | -9.40% | 124 | 46.77% | 0.63% | -0.70% | -9.97% | -10.77% | 8.34% | 2.3 | -12.18% | OVERFIT_WARNING: test net return much worse than train; UNDERPERFORMED_BUY_HOLD on test; BELOW_RANDOM_MEDIAN on test (percentile < 50); NEGATIVE_TEST_RETURN |
| SPY | 1d | ok | L=12 H=8 fixed_hold magnitude@1.0 | 513 | 174.07% | -31.86% | 230 | 63.04% | 1.67% | -1.71% | 151.32% | -12.58% | 307.28% | 55.8 | 140.02% | OVERFIT_WARNING: test net return much worse than train; UNDERPERFORMED_BUY_HOLD on test |
| QQQ | 15m | ok | L=12 H=8 fixed_hold count@0.5 | 73 | 9.44% | -1.36% | 25 | 36.00% | 0.30% | -0.36% | -3.06% | -3.07% | -10.88% | 71.1 | -3.55% | OVERFIT_WARNING: test net return much worse than train; NEGATIVE_TEST_RETURN |
| QQQ | 1h | ok | L=4 H=8 fixed_hold magnitude@1.5 | 312 | 50.15% | -15.65% | 131 | 48.85% | 1.00% | -1.01% | -4.40% | -14.41% | 6.60% | 26.1 | -6.87% | OVERFIT_WARNING: test net return much worse than train; UNDERPERFORMED_BUY_HOLD on test; BELOW_RANDOM_MEDIAN on test (percentile < 50); NEGATIVE_TEST_RETURN |
| QQQ | 1d | ok | L=12 H=8 fixed_hold magnitude@1.0 | 406 | 256.60% | -53.11% | 183 | 63.39% | 2.42% | -2.90% | 115.07% | -26.07% | 286.59% | 38.7 | 107.34% | OVERFIT_WARNING: test net return much worse than train; UNDERPERFORMED_BUY_HOLD on test; BELOW_RANDOM_MEDIAN on test (percentile < 50) |

## Walk-forward (1h and 1d)

### SPCX 1h

| fold | train bars | test bars | status | train ret | test ret | test B&H | params |
|---:|---:|---:|---|---:|---:|---:|---|
| 1 | 139 | 139 | ok | 2.72% | 17.02% | 13.88% | L=4 H=1 fixed_hold magnitude@1.0 |
| 2 | 278 | 139 | ok | 37.37% | -6.45% | 3.84% | L=4 H=2 signal_flip count@0.5 |
| 3 | 417 | 139 | ok | 43.93% | -4.57% | 7.86% | L=4 H=1 fixed_hold magnitude@2.0 |
| 4 | 556 | 143 | ok | 41.06% | 0.45% | -16.91% | L=4 H=1 fixed_hold count@0.5 |

### SPY 1h

| fold | train bars | test bars | status | train ret | test ret | test B&H | params |
|---:|---:|---:|---|---:|---:|---:|---|
| 1 | 1011 | 1011 | ok | 13.94% | -0.73% | 7.44% | L=12 H=8 fixed_hold count@0.5 |
| 2 | 2022 | 1011 | ok | 19.08% | 5.47% | 7.46% | L=4 H=8 fixed_hold magnitude@1.0 |
| 3 | 3033 | 1011 | ok | 25.89% | -4.25% | 4.88% | L=4 H=8 fixed_hold magnitude@1.0 |
| 4 | 4044 | 1011 | ok | 20.76% | 3.00% | 8.32% | L=4 H=8 fixed_hold magnitude@1.0 |

### SPY 1d

| fold | train bars | test bars | status | train ret | test ret | test B&H | params |
|---:|---:|---:|---|---:|---:|---:|---|
| 1 | 1700 | 1700 | ok | 98.94% | 3.96% | 8.16% | L=12 H=8 fixed_hold magnitude@1.5 |
| 2 | 3400 | 1700 | ok | 99.69% | 25.30% | 44.77% | L=12 H=8 fixed_hold magnitude@1.5 |
| 3 | 5100 | 1700 | ok | 160.15% | 47.14% | 134.97% | L=12 H=8 fixed_hold magnitude@1.0 |
| 4 | 6800 | 1702 | ok | 291.04% | 77.51% | 147.87% | L=12 H=8 fixed_hold magnitude@1.0 |

### QQQ 1h

| fold | train bars | test bars | status | train ret | test ret | test B&H | params |
|---:|---:|---:|---|---:|---:|---:|---|
| 1 | 1011 | 1011 | ok | 24.41% | 2.52% | 4.53% | L=8 H=8 fixed_hold count@0.5 |
| 2 | 2022 | 1011 | ok | 31.89% | 14.30% | 10.04% | L=4 H=8 fixed_hold magnitude@1.5 |
| 3 | 3033 | 1011 | ok | 50.96% | 0.70% | 5.22% | L=4 H=8 fixed_hold magnitude@1.5 |
| 4 | 4044 | 1014 | ok | 52.01% | -5.08% | 7.96% | L=4 H=8 fixed_hold magnitude@1.5 |

### QQQ 1d

| fold | train bars | test bars | status | train ret | test ret | test B&H | params |
|---:|---:|---:|---|---:|---:|---:|---|
| 1 | 1392 | 1392 | ok | 66.08% | 17.12% | 39.89% | L=12 H=8 fixed_hold magnitude@1.0 |
| 2 | 2784 | 1392 | ok | 86.32% | 46.85% | 135.75% | L=12 H=8 fixed_hold magnitude@1.0 |
| 3 | 4176 | 1392 | ok | 181.89% | 88.41% | 234.90% | L=12 H=8 fixed_hold magnitude@1.0 |
| 4 | 5568 | 1392 | ok | 436.98% | 46.75% | 100.04% | L=12 H=8 fixed_hold magnitude@1.0 |

## Honest verdict

- spcx 15m: train 29.09%, test -11.41%, buy-hold -14.41%, random percentile 36.6. flags: OVERFIT_WARNING: test net return much worse than train; BELOW_RANDOM_MEDIAN on test (percentile < 50); NEGATIVE_TEST_RETURN.
- spcx 1h: train 42.42%, test -6.62%, buy-hold -9.53%, random percentile 17.9. flags: OVERFIT_WARNING: test net return much worse than train; BELOW_RANDOM_MEDIAN on test (percentile < 50); NEGATIVE_TEST_RETURN.
- spcx 1d: could not pick a train-eligible config (no config reached >= 30 trades on train (72 bars). Multiple-testing risk still applies to the full sweep of 192 configs.).
- we swept 192 configs per series; picking the best on train invites overfitting. short spcx history makes any edge claim weak. treat this as an exploratory first pass, not a green light.

Generated at (America/Chicago): 2026-11-06T14:45:51-06:00