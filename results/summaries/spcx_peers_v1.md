# SPCX peers v1

SPCX daily sample from 2026-06-12: n_close_bars=103, n_return_bars=102. 5m window ~60 trading days. Correlation is not causation. Small sample.

Candidates tried: 102. Daily failed: ['SATS'].
5m failed: none.

## Top 15 by daily corr

| rank | ticker | daily_corr | beta | same_dir | n | m5_corr |
|---:|---|---:|---:|---:|---:|---:|
| 1 | ARKX | 0.707 | 0.26 | 69.6% | 102 | 0.661 |
| 2 | UFO | 0.605 | 0.23 | 69.6% | 102 | 0.493 |
| 3 | ARKK | 0.560 | 0.27 | 64.7% | 102 | 0.553 |
| 4 | RKLB | 0.514 | 0.51 | 65.7% | 102 | 0.502 |
| 5 | QQQ | 0.484 | 0.14 | 67.6% | 102 | 0.575 |
| 6 | TQQQ | 0.480 | 0.41 | 67.6% | 102 | 0.575 |
| 7 | SPY | 0.456 | 0.08 | 60.8% | 102 | 0.405 |
| 8 | RDW | 0.449 | 0.48 | 59.8% | 102 | 0.434 |
| 9 | ASTS | 0.446 | 0.51 | 64.7% | 102 | 0.339 |
| 10 | XAR | 0.443 | 0.15 | 63.7% | 102 | 0.304 |
| 11 | LUNR | 0.402 | 0.42 | 59.8% | 102 | 0.456 |
| 12 | ORCL | 0.400 | 0.29 | 65.7% | 102 | 0.307 |
| 13 | AVAV | 0.396 | 0.35 | 59.8% | 102 | 0.260 |
| 14 | EEM | 0.390 | 0.13 | 59.8% | 102 | 0.456 |
| 15 | SOXL | 0.374 | 0.75 | 62.7% | 102 | 0.543 |

## Top 15 by 5m corr

| rank | ticker | m5_corr | m5_beta | same_dir | n | best_lag | best_lag_corr |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ARKX | 0.661 | 0.31 | 63.9% | 4649 | 0 | 0.661 |
| 2 | TQQQ | 0.575 | 0.60 | 65.6% | 4679 | 0 | 0.575 |
| 3 | QQQ | 0.575 | 0.20 | 65.9% | 4679 | 0 | 0.575 |
| 4 | ARKK | 0.553 | 0.35 | 64.4% | 4679 | 0 | 0.553 |
| 5 | SOXL | 0.543 | 1.41 | 62.4% | 4679 | 0 | 0.543 |
| 6 | SOXX | 0.543 | 0.46 | 62.5% | 4679 | 0 | 0.543 |
| 7 | RKLB | 0.502 | 0.64 | 62.1% | 4679 | 0 | 0.502 |
| 8 | UFO | 0.493 | 0.28 | 59.5% | 4436 | 0 | 0.493 |
| 9 | LUNR | 0.456 | 0.63 | 60.3% | 4679 | 0 | 0.456 |
| 10 | EEM | 0.456 | 0.18 | 60.1% | 4679 | 0 | 0.456 |
| 11 | TSLA | 0.447 | 0.36 | 59.9% | 4679 | 0 | 0.447 |
| 12 | RDW | 0.434 | 0.57 | 59.4% | 4679 | 0 | 0.434 |
| 13 | INTC | 0.433 | 0.70 | 60.8% | 4679 | 0 | 0.433 |
| 14 | PL | 0.421 | 0.47 | 57.4% | 4679 | 0 | 0.421 |
| 15 | NOK | 0.416 | 0.46 | 54.5% | 4679 | 0 | 0.416 |

## Lead/lag note

lag<0 means peer leads SPCX; lag>0 means SPCX leads peer; lag=0 contemporaneous. Listed if best lag is negative and |corr| beats lag0 by >=0.005.

| ticker | best_lag | best_corr | lag0 |
|---|---:|---:|---:|
| PINS | -2 | 0.065 | 0.041 |
| RTX | -2 | -0.063 | -0.050 |
| UBER | -2 | 0.043 | 0.009 |
| F | -2 | 0.038 | 0.002 |
| NCLH | -2 | 0.035 | 0.019 |
| PYPL | -1 | -0.026 | -0.010 |

- csv: `/workspace/backtester/spcx_peers_v1/spcx_peers_v1.csv`
- chart: `/workspace/backtester/spcx_peers_v1/spcx_peers_top15_m5corr_v1.png`
Generated at (America/Chicago): 2026-11-06T16:11:52-06:00