# Castle steps v4 (SPCX only, min_up_steps 2 vs 3)

## Definition

- Same as v3 except min_up_steps is parameterized (compare 2 vs 3).
- Castle: run of >= min_up_steps up steps (5m close-to-close), <=1 small down (< half avg up), local peak, pullback >= 25% of rise.
- NOT a castle if largest up step > 50% of rise (jump / false). Cap rise <= 5%.
- Match: >= 2 castles with pullback ending by ~11:30. Entry max(after_2nd, 11:15); exits 12:00 / 13:00 / close; 1 bp/side. Baseline: every day 11:15 open.

## v3 reproduce check (min_up_steps=3)

- ok=True; v4 min3 matches=13 types={'single_castle': 27, 'false_only': 20, 'two_plus_castles': 13}; v3 matches=13 types={'single_castle': 27, 'false_only': 20, 'two_plus_castles': 13}

## Sep 11 verification

### min_up_steps=3
castles:
- start 2026-09-11 09:45:00-04:00 peak 2026-09-11 10:05:00-04:00 end 2026-09-11 10:10:00-04:00 rise=1.22% ups=4 max_step_frac=0.32
- start 2026-09-11 10:35:00-04:00 peak 2026-09-11 11:00:00-04:00 end 2026-09-11 11:10:00-04:00 rise=0.54% ups=4 max_step_frac=0.35
falses:
- start 2026-09-11 09:30:00-04:00 peak 2026-09-11 09:35:00-04:00 rise=0.46% max_step_frac=1.00 reason=too_few_steps
- start 2026-09-11 10:20:00-04:00 peak 2026-09-11 10:25:00-04:00 rise=0.35% max_step_frac=1.00 reason=too_few_steps

### min_up_steps=2
castles:
- start 2026-09-11 09:45:00-04:00 peak 2026-09-11 10:05:00-04:00 end 2026-09-11 10:10:00-04:00 rise=1.22% ups=4 max_step_frac=0.32
- start 2026-09-11 10:35:00-04:00 peak 2026-09-11 11:00:00-04:00 end 2026-09-11 11:10:00-04:00 rise=0.54% ups=4 max_step_frac=0.35
falses:
- start 2026-09-11 09:30:00-04:00 peak 2026-09-11 09:35:00-04:00 rise=0.46% max_step_frac=1.00 reason=too_few_steps
- start 2026-09-11 10:20:00-04:00 peak 2026-09-11 10:25:00-04:00 rise=0.35% max_step_frac=1.00 reason=too_few_steps
- start 2026-09-11 11:30:00-04:00 peak 2026-09-11 11:40:00-04:00 rise=0.28% max_step_frac=0.97 reason=dominant_bar
- start 2026-09-11 11:45:00-04:00 peak 2026-09-11 12:00:00-04:00 rise=0.29% max_step_frac=0.82 reason=dominant_bar

Under min_up=2: 09:30 jump accepted as castle? False (still false? True); 10:20 bump accepted as castle? False (still false? True).
Note: with min_up=2 a single big bar still has max_step_frac=1.0 so dominant_bar rejection still applies to 1-step jumps; 2 equal-ish steps can pass.

## Side-by-side

| metric | min_up=3 | min_up=2 |
|---|---:|---:|
| n days | 60 | 60 |
| matches (2+) | 13 | 13 |
| day_type false_only | 20 | 20 |
| day_type single_castle | 27 | 27 |
| day_type two_plus_castles | 13 | 13 |
| day_type none | 0 | 0 |
| day_type other | 0 | 0 |
| exit_1200 match hit | 76.92% | 76.92% |
| exit_1200 match avg | 0.27% | 0.27% |
| exit_1200 match med | 0.27% | 0.27% |
| exit_1200 match CI | [0.01%, 0.57%] | [0.02%, 0.57%] |
| exit_1200 all avg (same baseline) | 0.17% | 0.17% |
| exit_1200 binom p | 0.1016 | 0.1016 |
| exit_1300 match hit | 61.54% | 61.54% |
| exit_1300 match avg | 0.10% | 0.10% |
| exit_1300 match med | 0.07% | 0.07% |
| exit_1300 match CI | [-0.17%, 0.45%] | [-0.17%, 0.45%] |
| exit_1300 all avg (same baseline) | -0.00% | -0.00% |
| exit_1300 binom p | 0.4115 | 0.4115 |
| exit_close match hit | 53.85% | 53.85% |
| exit_close match avg | 0.24% | 0.24% |
| exit_close match med | 0.01% | 0.01% |
| exit_close match CI | [-0.47%, 1.01%] | [-0.50%, 1.01%] |
| exit_close all avg (same baseline) | -0.19% | -0.19% |
| exit_close binom p | 0.5842 | 0.5842 |

### Detail lines

**min_up_steps=3**
- exit_1200: match n=13 hit 76.92% avg 0.27% med 0.27% CI [0.01%, 0.57%] || all n=60 hit 53.33% avg 0.17% || binom p=0.1016
- exit_1300: match n=13 hit 61.54% avg 0.10% med 0.07% CI [-0.17%, 0.45%] || all n=60 hit 48.33% avg -0.00% || binom p=0.4115
- exit_close: match n=13 hit 53.85% avg 0.24% med 0.01% CI [-0.47%, 1.01%] || all n=60 hit 45.00% avg -0.19% || binom p=0.5842
- first_close (mid=2026-09-28): match n=7 hit 57.14% avg 0.05% vs all avg 0.10% p=1
- second_close (mid=2026-09-28): match n=6 hit 50.00% avg 0.47% vs all avg -0.50% p=0.3827
- first_1200 (mid=2026-09-28): match n=7 hit 85.71% avg 0.36% vs all avg 0.24% p=0.1373
- second_1200 (mid=2026-09-28): match n=6 hit 66.67% avg 0.17% vs all avg 0.09% p=0.6886

**min_up_steps=2**
- exit_1200: match n=13 hit 76.92% avg 0.27% med 0.27% CI [0.02%, 0.57%] || all n=60 hit 53.33% avg 0.17% || binom p=0.1016
- exit_1300: match n=13 hit 61.54% avg 0.10% med 0.07% CI [-0.17%, 0.45%] || all n=60 hit 48.33% avg -0.00% || binom p=0.4115
- exit_close: match n=13 hit 53.85% avg 0.24% med 0.01% CI [-0.50%, 1.01%] || all n=60 hit 45.00% avg -0.19% || binom p=0.5842
- first_close (mid=2026-09-28): match n=7 hit 57.14% avg 0.05% vs all avg 0.10% p=1
- second_close (mid=2026-09-28): match n=6 hit 50.00% avg 0.47% vs all avg -0.50% p=0.3827
- first_1200 (mid=2026-09-28): match n=7 hit 85.71% avg 0.36% vs all avg 0.24% p=0.1373
- second_1200 (mid=2026-09-28): match n=6 hit 66.67% avg 0.17% vs all avg 0.09% p=0.6886

## Days that become matches only under min_up=2

(none)

Both variants: ['2026-08-19', '2026-08-21', '2026-08-24', '2026-09-01', '2026-09-11', '2026-09-22', '2026-09-23', '2026-09-29', '2026-10-05', '2026-10-12', '2026-10-16', '2026-10-23', '2026-11-04']
Only min3 (lost under min2): []

SMALL SAMPLE / exploratory. fixed rules, no optimizing.

## Files

- min3 grid: `/workspace/backtester/castle_steps_v4/spcx_matches_min3_grid_v4.png`
- min2 grid: `/workspace/backtester/castle_steps_v4/spcx_matches_min2_grid_v4.png`
- min2-only grid: `/workspace/backtester/castle_steps_v4/spcx_matches_min2_only_grid_v4.png`
- csv min3: `/workspace/backtester/castle_steps_v4/spcx_min3_v4.csv`
- csv min2: `/workspace/backtester/castle_steps_v4/spcx_min2_v4.csv`
- csv min2-only: `/workspace/backtester/castle_steps_v4/spcx_min2_only_matches_v4.csv`

Generated at (America/Chicago): 2026-11-06T16:05:01-06:00