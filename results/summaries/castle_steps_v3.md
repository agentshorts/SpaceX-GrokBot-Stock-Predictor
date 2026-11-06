# Castle steps v3

## Definition (fixed)

- Castle: run of >= 3 up steps (5m close-to-close), allowing at most 1 small down (< half the average up step in the run), ending at a local peak, then pullback giving back >= 25% of the rise.
- NOT a castle if the largest up step is > 50% of the run's rise (jump / false castle).
- Cap: castle peak rise from its start <= 5% of start price.
- Match: >= 2 such castles with pullback ending by ~11:30 ET (scan window to 12:00).
- Trade (fixed): enter at open of the bar after the 2nd castle pullback ends, but not before 11:15 (entry = max(after_2nd, 11:15)); exit 12:00 / 13:00 / close; 1 bp/side.
- Baseline: buy every day at 11:15 open, same exits.

## SPCX Sep 11 verification

Expected: castles near 09:45->10:05 and 10:50->~11:10; reject 09:30 jump and 10:20 bump.

Found castles:
- start 2026-09-11 09:45:00-04:00 peak 2026-09-11 10:05:00-04:00 end 2026-09-11 10:10:00-04:00 rise=1.22% ups=4 max_step_frac=0.32
- start 2026-09-11 10:35:00-04:00 peak 2026-09-11 11:00:00-04:00 end 2026-09-11 11:10:00-04:00 rise=0.54% ups=4 max_step_frac=0.35
Found false jumps:
- start 2026-09-11 09:30:00-04:00 peak 2026-09-11 09:35:00-04:00 rise=0.46% max_step_frac=1.00 reason=too_few_steps
- start 2026-09-11 10:20:00-04:00 peak 2026-09-11 10:25:00-04:00 rise=0.35% max_step_frac=1.00 reason=too_few_steps
- castle start clock times: ['09:45', '10:35']
- approx 09:45 castle found: True; approx 10:50 castle found: False

## SPCX matches: 13 / 60

day type counts: {'single_castle': 27, 'false_only': 20, 'two_plus_castles': 13}

| date | n | rises | c/o | 11:15->close | trade->close |
|---|---:|---|---:|---:|---:|
| 2026-08-19 | 2 | 1.69%,1.43% | -3.67% | 0.02% | 0.01% |
| 2026-08-21 | 2 | 1.15%,1.56% | 1.95% | 0.82% | 0.89% |
| 2026-08-24 | 2 | 0.88%,1.55% | 0.52% | -0.92% | -0.81% |
| 2026-09-01 | 2 | 1.52%,0.67% | 0.28% | -1.12% | -1.19% |
| 2026-09-11 | 2 | 1.22%,0.54% | 1.04% | 2.82% | 3.19% |
| 2026-09-22 | 2 | 1.94%,0.65% | 2.01% | -0.01% | 0.63% |
| 2026-09-23 | 2 | 0.35%,0.40% | -3.23% | -2.57% | -2.34% |
| 2026-09-29 | 2 | 2.20%,1.27% | 1.71% | 0.48% | 0.50% |
| 2026-10-05 | 3 | 1.64%,1.63%,1.02% | 7.61% | 2.46% | 2.43% |
| 2026-10-12 | 2 | 2.76%,1.23% | -0.74% | -0.12% | -0.01% |
| 2026-10-16 | 2 | 1.60%,0.83% | 0.47% | 0.38% | 0.47% |
| 2026-10-23 | 2 | 0.84%,1.39% | -0.29% | -0.22% | -0.25% |
| 2026-11-04 | 4 | 3.04%,2.44%,0.44%,0.54% | 1.94% | -0.55% | -0.34% |

### SPCX trade vs baseline

- exit_1200: match n=13 hit 76.92% avg 0.27% CI [0.01%, 0.57%] || all n=60 hit 53.33% avg 0.17% || binom p=0.1016
- exit_1300: match n=13 hit 61.54% avg 0.10% CI [-0.17%, 0.45%] || all n=60 hit 48.33% avg -0.00% || binom p=0.4115
- exit_close: match n=13 hit 53.85% avg 0.24% CI [-0.47%, 1.01%] || all n=60 hit 45.00% avg -0.19% || binom p=0.5842

## Multi universe (73 tickers)

- ticker-days: 4380; matches: 222
- day type counts: {'false_only': 2327, 'single_castle': 1745, 'two_plus_castles': 225, 'none': 83}

### Multi trade vs baseline

- exit_1200: match n=222 hit 56.76% avg 0.11% CI [0.03%, 0.18%] || all n=4380 hit 49.00% avg -0.02% || binom p=0.02235
- exit_1300: match n=222 hit 48.20% avg 0.04% CI [-0.08%, 0.15%] || all n=4380 hit 46.44% avg -0.04% || binom p=0.6377
- exit_close: match n=222 hit 45.50% avg -0.01% CI [-0.18%, 0.16%] || all n=4380 hit 47.08% avg -0.06% || binom p=0.6868

### Multi half split (exit close)

- first_close (mid=2026-09-28): match n=118 avg -0.21% vs all avg -0.11% p=0.07851
- second_close (mid=2026-09-28): match n=104 avg 0.22% vs all avg -0.01% p=0.2393

### Multi by day type (11:15->close, descriptive)

| type | n | hit | avg | median |
|---|---:|---:|---:|---:|
| two_plus_castles | 225 | 40.89% | -0.07% | -0.20% |
| single_castle | 1745 | 49.11% | -0.03% | -0.01% |
| false_only | 2327 | 45.94% | -0.06% | -0.05% |
| none | 83 | 42.17% | -0.18% | -0.07% |
| other | 0 | n/a | n/a | n/a |

SMALL SAMPLE / exploratory: fixed rules, no optimizing, but many comparisons. do not treat as a green light.

## Files

- spcx grid: `/workspace/backtester/castle_steps_v3/spcx_matches_grid_v3.png`
- multi grid sample: `/workspace/backtester/castle_steps_v3/multi_matches_grid_v3.png`
- spcx csv: `/workspace/backtester/castle_steps_spcx_v3.csv`
- multi csv: `/workspace/backtester/castle_steps_multi_v3.csv`
- multi matches csv: `/workspace/backtester/castle_steps_multi_matches_v3.csv`

Generated at (America/Chicago): 2026-11-06T15:52:57-06:00