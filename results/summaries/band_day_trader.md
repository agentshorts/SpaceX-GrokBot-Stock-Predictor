# SPCX band day-trader backtest summary

## Idea

- Band = absolute close-to-close step. Narrow bands stepping up are bullish; wide bands warn of a fall or chop.
- Signal: band_ratio = mean(|diff| last L) / baseline; long when ratio < t_narrow, up-share of steps > 0.5, and optional no-slide (lower highs) filter.
- Exit when ratio > t_wide, or after hold H bars, or at the session close. Long-only. Flat overnight.
- Timing: all RTH bars build the signal and day baseline; entries only at/after 11:00 ET (Captain: morning noise).
- Sweep: 144 configs (L=[3, 6, 10], t_narrow=[0.5, 0.75], t_wide=[1.5, 2.0], H=[2, 4, 6], slide=[False, True], baseline=['day_so_far', 'trail_5d']). Multiple-testing risk is real.
- Validation: chronological 70/30 by day; pick best on train (net return, >= 15 trades); report on test. Costs 1 bp/side (+2x stress). Baselines: buy-and-hold, 11am-to-close every day, random after 11am (1000 runs).
- Data: yfinance SPCX, RTH only, timestamps US/Eastern.

## Data ranges

| interval | period req | n_bars | n_sessions | start | end | last_close | source |
|---|---|---:|---:|---|---|---:|---|
| 5m | 60d | 4680 | 60 | 2026-08-14 09:30:00-04:00 | 2026-11-06 15:55:00-05:00 | 134.19500732421875 | yfinance_live |
| 15m | 60d | 1559 | 60 | 2026-08-14 09:30:00-04:00 | 2026-11-06 15:30:00-05:00 | 134.51499938964844 | /workspace/backtester/data_SPCX_15m.csv |
| 1h | 730d | 699 | 100 | 2026-06-12 11:30:00-04:00 | 2026-11-06 15:30:00-05:00 | 134.3800048828125 | /workspace/backtester/data_SPCX_1h.csv |

## Results (chosen on train days, reported on test days)

| bar | status | train/test days | params | train trades | train ret | test trades | test hit | avg win | avg loss | test ret | test MDD | test B&H | test 11am-close | rand pct | test 2x | flags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 5m | ok | 42/18 | L=6 tn=0.5 tw=2.0 H=6 slide=True base=day_so_far | 35 | 1.33% | 16 | 25.00% | 0.37% | -0.37% | -2.90% | -3.66% | -13.42% | -12.78% | 20.5 | -3.21% | BELOW_RANDOM_MEDIAN on test; NEGATIVE_TEST_RETURN |
| 15m | ok | 42/18 | L=3 tn=0.75 tw=1.5 H=4 slide=True base=trail_5d | 52 | 1.22% | 14 | 35.71% | 0.50% | -0.58% | -2.71% | -2.87% | -13.21% | -12.57% | 37.3 | -2.98% | BELOW_RANDOM_MEDIAN on test; NEGATIVE_TEST_RETURN |
| 1h | ok | 70/30 | L=3 tn=0.75 tw=1.5 H=2 slide=False base=trail_5d | 21 | -0.30% | 4 | 0.00% | n/a | -0.66% | -2.61% | -2.28% | -9.53% | -16.20% | 14.5 | -2.69% | BELOW_RANDOM_MEDIAN on test; NEGATIVE_TEST_RETURN |

## Walk-forward

### 5m

| fold | train days | test days | status | train ret | test ret | test B&H | test 11am | params |
|---:|---:|---:|---|---:|---:|---:|---:|---|
| 1 | 12 | 12 | ok | 5.76% | -3.72% | 9.10% | 2.06% | L=3 tn=0.75 tw=2.0 H=6 slide=False base=trail_5d |
| 2 | 24 | 12 | ok | 3.55% | 0.02% | 10.63% | -2.77% | L=3 tn=0.75 tw=2.0 H=6 slide=False base=day_so_far |
| 3 | 36 | 12 | ok | 3.84% | -9.50% | -7.46% | -9.42% | L=3 tn=0.75 tw=2.0 H=6 slide=True base=day_so_far |
| 4 | 48 | 12 | ok | 1.69% | -3.24% | -12.99% | -9.41% | L=6 tn=0.5 tw=2.0 H=6 slide=True base=day_so_far |

### 15m

| fold | train days | test days | status | train ret | test ret | test B&H | test 11am | params |
|---:|---:|---:|---|---:|---:|---:|---:|---|
| 1 | 12 | 12 | ok | 4.40% | -1.11% | 9.10% | 2.06% | L=3 tn=0.75 tw=1.5 H=4 slide=False base=trail_5d |
| 2 | 24 | 12 | ok | 4.26% | -1.78% | 10.63% | -2.77% | L=3 tn=0.75 tw=2.0 H=4 slide=True base=trail_5d |
| 3 | 36 | 12 | ok | 2.41% | -4.06% | -7.46% | -9.42% | L=3 tn=0.75 tw=2.0 H=4 slide=True base=trail_5d |
| 4 | 48 | 12 | ok | 0.53% | 1.14% | -12.78% | -9.19% | L=3 tn=0.75 tw=1.5 H=2 slide=True base=trail_5d |

### 1h

| fold | train days | test days | status | train ret | test ret | test B&H | test 11am | params |
|---:|---:|---:|---|---:|---:|---:|---:|---|
| 1 | 20 | 20 | no_eligible |  |  |  |  |  |
| 2 | 40 | 20 | no_eligible |  |  |  |  |  |
| 3 | 60 | 20 | ok | -0.30% | -0.34% | 10.40% | -8.23% | L=3 tn=0.75 tw=1.5 H=2 slide=False base=trail_5d |
| 4 | 80 | 20 | ok | -0.64% | -2.28% | -18.43% | -13.12% | L=3 tn=0.75 tw=1.5 H=2 slide=False base=trail_5d |

## Honest verdict

- spcx 5m: 42 train days / 18 test days. train 1.33%, test -2.90%, b&h -13.42%, 11am-close -12.78%, random pctile 20.5. flags: BELOW_RANDOM_MEDIAN on test; NEGATIVE_TEST_RETURN.
- spcx 15m: 42 train days / 18 test days. train 1.22%, test -2.71%, b&h -13.21%, 11am-close -12.57%, random pctile 37.3. flags: BELOW_RANDOM_MEDIAN on test; NEGATIVE_TEST_RETURN.
- spcx 1h: 70 train days / 30 test days. train -0.30%, test -2.61%, b&h -9.53%, 11am-close -16.20%, random pctile 14.5. flags: BELOW_RANDOM_MEDIAN on test; NEGATIVE_TEST_RETURN.
- swept 144 configs per bar size on a short spcx history. picking the best on train invites overfitting. treat as exploratory only.

Generated at (America/Chicago): 2026-11-06T15:06:50-06:00