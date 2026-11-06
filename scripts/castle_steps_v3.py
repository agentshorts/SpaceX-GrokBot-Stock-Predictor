#!/usr/bin/env python3
"""
Castle steps v3: castle = >=3 up steps to a peak, then pullback.
Reject jumps (largest up step > 50% of rise). SPCX verify Sep11, then multi+trades.
Prior files untouched. Versioned outputs under castle_steps_v3/.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, asdict
from datetime import datetime, time as dtime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import sys

sys.path.insert(0, "/workspace/backtester")
from spcx_dip_scan import load_bars, session_days, unique_path, fmt_pct  # noqa: E402

OUT = Path("/workspace/backtester")
CHART = OUT / "castle_steps_v3"
DATA = OUT / "multi_data"
SPCX_CSV = OUT / "data_bands_SPCX_5m_v5.csv"
COST = 1e-4
PEAK_RISE_CAP = 0.05
NOON = dtime(12, 0)
MATCH_BY = dtime(11, 30)
ENTRY_FALLBACK = dtime(11, 15)
RNG = np.random.default_rng(23)

# Step-castle rules (fixed)
MIN_UP_STEPS = 3
MAX_SMALL_DOWNS_IN_CLIMB = 1
SMALL_DOWN_FRAC = 0.5  # small down < half avg up step
MAX_SINGLE_STEP_FRAC = 0.50  # else false jump
MIN_PULLBACK_FRAC = 0.25  # give back >= 25% of rise (or 1 down bar of meaningful size)
MIN_RISE = 0.003  # 0.3% min tower so noise is ignored


@dataclass
class Castle:
    start_i: int
    peak_i: int
    end_i: int  # pullback end index
    start_px: float
    peak_px: float
    end_px: float
    rise: float
    n_up_steps: int
    max_step_frac: float
    giveback: float
    start_time: str = ""
    peak_time: str = ""
    end_time: str = ""
    up_step_indices: tuple = ()


@dataclass
class FalseJump:
    start_i: int
    peak_i: int
    rise: float
    max_step_frac: float
    reason: str
    start_time: str = ""
    peak_time: str = ""


def slice_to(g: pd.DataFrame, end: dtime) -> pd.DataFrame:
    return g[g.index.time <= end].copy()


def find_castles(closes: np.ndarray, times) -> tuple[list[Castle], list[FalseJump]]:
    """
    Scan close path for step-castles and false jumps.
    Climb: sequence with >=3 up diffs, allowing <=1 small down (< 0.5 * mean up).
    Peak = last bar of climb (must be local max vs next bar or end).
    Reject if max up step > 50% of (peak-start).
    Then consume pullback until climb would restart or flat.
    """
    n = len(closes)
    if n < 5:
        return [], []
    diffs = np.diff(closes)  # len n-1; diffs[i] = close[i+1]-close[i]
    castles: list[Castle] = []
    falses: list[FalseJump] = []
    i = 0  # index into closes; we look at diffs starting at i
    while i < n - 3:
        # try to start a climb at bar i (base)
        # collect forward
        up_steps = []  # list of diff indices (into diffs)
        down_small = 0
        j = i  # current close index; next diff is diffs[j] if j < n-1
        last_up_vals = []
        while j < n - 1:
            d = diffs[j]
            if d > 0:
                up_steps.append(j)
                last_up_vals.append(d)
                j += 1
                continue
            if d < 0 and last_up_vals:
                avg_up = float(np.mean(last_up_vals))
                if abs(d) < SMALL_DOWN_FRAC * avg_up and down_small < MAX_SMALL_DOWNS_IN_CLIMB:
                    down_small += 1
                    j += 1
                    continue
                break
            # flat or down before any up
            if not last_up_vals:
                break
            break

        if len(up_steps) < MIN_UP_STEPS:
            # check false jump: 1-2 ups with big concentration
            if len(up_steps) >= 1:
                peak_i = up_steps[-1] + 1
                base = float(closes[i])
                peak = float(closes[peak_i])
                if peak > base:
                    rise = (peak - base) / base
                    ups = np.array([diffs[k] for k in up_steps])
                    max_frac = float(np.max(ups) / (peak - base)) if peak > base else 1.0
                    if rise >= MIN_RISE and (len(up_steps) < MIN_UP_STEPS or max_frac > MAX_SINGLE_STEP_FRAC):
                        falses.append(
                            FalseJump(
                                start_i=i,
                                peak_i=peak_i,
                                rise=rise,
                                max_step_frac=max_frac,
                                reason="too_few_steps" if len(up_steps) < MIN_UP_STEPS else "dominant_bar",
                                start_time=str(times[i]),
                                peak_time=str(times[peak_i]),
                            )
                        )
                        i = peak_i  # skip ahead past this jump
                        continue
            i += 1
            continue

        peak_i = up_steps[-1] + 1
        base = float(closes[i])
        peak = float(closes[peak_i])
        if peak <= base:
            i += 1
            continue
        rise = (peak - base) / base
        ups = np.array([diffs[k] for k in up_steps], float)
        max_frac = float(np.max(ups) / (peak - base))

        # reject giant-bar "castle"
        if max_frac > MAX_SINGLE_STEP_FRAC or rise < MIN_RISE:
            falses.append(
                FalseJump(
                    start_i=i,
                    peak_i=peak_i,
                    rise=rise,
                    max_step_frac=max_frac,
                    reason="dominant_bar" if max_frac > MAX_SINGLE_STEP_FRAC else "tiny",
                    start_time=str(times[i]),
                    peak_time=str(times[peak_i]),
                )
            )
            i = peak_i
            continue

        # require peak is a local high (next bar not higher, if exists)
        if peak_i + 1 < n and closes[peak_i + 1] > peak:
            # climb might continue; let outer loop advance by 1 from base? advance to continue climb
            # Actually we broke because of a down or end. If next is higher we shouldn't be here.
            i += 1
            continue

        # pullback after peak
        end_i = peak_i
        pulled = 0.0
        k = peak_i
        while k < n - 1:
            nd = diffs[k]
            if nd < 0:
                pulled += -nd
                end_i = k + 1
                k += 1
                # stop if we've given back enough and next is up start
                if pulled / (peak - base) >= MIN_PULLBACK_FRAC:
                    # allow continued pullback while downs continue
                    if k < n - 1 and diffs[k] >= 0:
                        break
                    continue
                continue
            if nd >= 0:
                # end pullback at first up after some pullback
                if pulled / (peak - base) >= MIN_PULLBACK_FRAC or end_i > peak_i:
                    break
                # no real pullback yet
                break

        giveback = pulled / (peak - base) if peak > base else 0.0
        if end_i == peak_i or giveback < MIN_PULLBACK_FRAC:
            # no pullback yet - might still be forming; skip as incomplete unless at end of window
            if peak_i >= n - 2:
                i = peak_i + 1
                continue
            i += 1
            continue

        castles.append(
            Castle(
                start_i=i,
                peak_i=peak_i,
                end_i=end_i,
                start_px=base,
                peak_px=peak,
                end_px=float(closes[end_i]),
                rise=rise,
                n_up_steps=len(up_steps),
                max_step_frac=max_frac,
                giveback=giveback,
                start_time=str(times[i]),
                peak_time=str(times[peak_i]),
                end_time=str(times[end_i]),
                up_step_indices=tuple(up_steps),
            )
        )
        i = end_i  # next search after this castle
    return castles, falses


def within_cap(c: Castle) -> bool:
    return c.rise <= PEAK_RISE_CAP


def analyze_day(g: pd.DataFrame, ticker: str) -> dict:
    sub = slice_to(g, NOON)
    closes = sub["Close"].to_numpy(float)
    times = sub.index
    castles, falses = find_castles(closes, times)
    castles_cap = [c for c in castles if within_cap(c)]

    # castles completed by ~11:30 (end_time <= 11:30)
    by_1130 = []
    for c in castles_cap:
        et = times[c.end_i].time()
        if et <= MATCH_BY:
            by_1130.append(c)

    n_castles = len(castles_cap)
    n_by_1130 = len(by_1130)
    n_false = len(falses)

    if n_by_1130 >= 2:
        day_type = "two_plus_castles"
    elif n_by_1130 == 1:
        day_type = "single_castle"
    elif n_false > 0 and n_castles == 0:
        day_type = "false_only"
    elif n_castles == 0 and n_false == 0:
        day_type = "none"
    else:
        # castles exist but end after 11:30 only, or mix
        day_type = "single_castle" if n_castles == 1 else ("two_plus_castles" if n_castles >= 2 else "other")

    # trade entry: after 2nd castle pullback ends (open of next bar), or 11:15 if later
    entry_i = None
    entry_reason = None
    if len(by_1130) >= 2:
        c2 = by_1130[1]
        # entry at open of bar after end_i, mapped back to full day g
        entry_time = times[c2.end_i]
        # next bar in full day
        full_times = list(g.index)
        # find index in full g
        try:
            fi = list(g.index).index(entry_time)
        except ValueError:
            fi = None
        if fi is not None and fi + 1 < len(g):
            entry_i = fi + 1
            entry_reason = "after_2nd_castle"
        # if entry would be before 11:15, still use it; if end after 11:15 use next; fallback 11:15
    # fallback / override if needed
    def bar_i_at(t: dtime):
        m = np.where(g.index.map(lambda x: x.time() == t))[0]
        return int(m[0]) if len(m) else None

    if entry_i is None and len(by_1130) >= 2:
        fb = bar_i_at(ENTRY_FALLBACK)
        entry_i = fb
        entry_reason = "fallback_1115"

    # if 2nd castle ends after 11:15, entry is still next bar after end (may be after 11:15)
    # if somehow entry before we want min 11:15? Spec: enter at open after 2nd ends OR at 11:15 if later
    # "if later" means: entry_time = max(after_2nd, 11:15)
    if len(by_1130) >= 2:
        c2 = by_1130[1]
        try:
            fi = list(g.index).index(times[c2.end_i])
        except ValueError:
            fi = None
        cand = fi + 1 if fi is not None and fi + 1 < len(g) else None
        fb = bar_i_at(ENTRY_FALLBACK)
        if cand is not None and fb is not None:
            entry_i = max(cand, fb)
            entry_reason = "max(after_2nd, 1115)"
        elif cand is not None:
            entry_i = cand
            entry_reason = "after_2nd_castle"

    day_close = float(g["Close"].iloc[-1])
    print_open = float(g["Open"].iloc[0])

    def exit_ret(entry_i, exit_time_or_close):
        if entry_i is None:
            return float("nan")
        entry_px = float(g["Open"].iloc[entry_i]) * (1 + COST)
        if exit_time_or_close == "close":
            exit_px = day_close * (1 - COST)
        else:
            m = g[g.index.time == exit_time_or_close]
            if not len(m):
                return float("nan")
            exit_px = float(m["Close"].iloc[0]) * (1 - COST)
        return (exit_px / entry_px - 1.0) if entry_px > 0 else float("nan")

    # also baseline entries at fixed times for comparison groups
    def ret_from_time(t_entry: dtime, t_exit):
        ei = bar_i_at(t_entry)
        if ei is None:
            return float("nan")
        entry_px = float(g["Open"].iloc[ei]) * (1 + COST)
        if t_exit == "close":
            exit_px = day_close * (1 - COST)
        else:
            m = g[g.index.time == t_exit]
            if not len(m):
                return float("nan")
            exit_px = float(m["Close"].iloc[0]) * (1 - COST)
        return (exit_px / entry_px - 1.0) if entry_px > 0 else float("nan")

    px_1115 = float(g[g.index.time == dtime(11, 15)]["Close"].iloc[0]) if len(g[g.index.time == dtime(11, 15)]) else float("nan")

    return {
        "ticker": ticker,
        "date": str(g.index[0].date()),
        "day_type": day_type,
        "n_castles": n_castles,
        "n_castles_by_1130": n_by_1130,
        "n_false_jumps": n_false,
        "is_match": n_by_1130 >= 2,
        "castles": [asdict(c) for c in castles_cap],
        "castles_by_1130": [asdict(c) for c in by_1130],
        "falses": [asdict(f) for f in falses],
        "print_open": print_open,
        "day_close": day_close,
        "close_vs_open_pct": (day_close / print_open - 1.0) if print_open > 0 else float("nan"),
        "ret_1115_to_close": (day_close / px_1115 - 1.0) if px_1115 > 0 else float("nan"),
        "entry_i": entry_i,
        "entry_reason": entry_reason,
        "entry_time": str(g.index[entry_i]) if entry_i is not None else None,
        "trade_exit_1200": exit_ret(entry_i, dtime(12, 0)) if entry_i is not None else float("nan"),
        "trade_exit_1300": exit_ret(entry_i, dtime(13, 0)) if entry_i is not None else float("nan"),
        "trade_exit_close": exit_ret(entry_i, "close") if entry_i is not None else float("nan"),
        "base_1115_to_1200": ret_from_time(dtime(11, 15), dtime(12, 0)),
        "base_1115_to_1300": ret_from_time(dtime(11, 15), dtime(13, 0)),
        "base_1115_to_close": ret_from_time(dtime(11, 15), "close"),
    }


def verify_sep11(g: pd.DataFrame) -> dict:
    sub = slice_to(g, NOON)
    castles, falses = find_castles(sub["Close"].to_numpy(float), sub.index)
    castles = [c for c in castles if within_cap(c)]
    return {
        "castles": [
            {
                "start": c.start_time,
                "peak": c.peak_time,
                "end": c.end_time,
                "rise": c.rise,
                "n_up": c.n_up_steps,
                "max_step_frac": c.max_step_frac,
            }
            for c in castles
        ],
        "falses": [
            {
                "start": f.start_time,
                "peak": f.peak_time,
                "rise": f.rise,
                "max_step_frac": f.max_step_frac,
                "reason": f.reason,
            }
            for f in falses
        ],
    }


def bootstrap_ci(x, n_boot=5000):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return float("nan"), float("nan"), float("nan")
    means = np.empty(n_boot)
    for i in range(n_boot):
        means[i] = float(np.mean(RNG.choice(x, size=len(x), replace=True)))
    return float(np.mean(x)), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def binomial_p(succ, n, p0):
    if n <= 0 or p0 != p0:
        return float("nan")
    return float(stats.binomtest(succ, n, p0, alternative="two-sided").pvalue)


def pack_rets(vals, label):
    vals = np.asarray(vals, float)
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return {"label": label, "n": 0}
    hits = vals > 0
    mean, lo, hi = bootstrap_ci(vals)
    return {
        "label": label,
        "n": int(len(vals)),
        "hit_rate": float(np.mean(hits)),
        "avg": mean,
        "median": float(np.median(vals)),
        "ci95_lo": lo,
        "ci95_hi": hi,
    }


def plot_spcx_match(g, row, out):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.step(g.index, g["Close"].to_numpy(float), where="post", color="#1e293b", lw=1.2)
    colors = ["#3b82f6", "#f59e0b", "#10b981", "#a855f7"]
    for i, c in enumerate(row["castles_by_1130"]):
        col = colors[i % len(colors)]
        # map times
        t0 = pd.Timestamp(c["start_time"])
        t1 = pd.Timestamp(c["end_time"])
        ax.axvspan(t0, t1, color=col, alpha=0.25, label=f"castle{i+1} rise={100*c['rise']:.2f}%")
        ax.scatter([pd.Timestamp(c["peak_time"])], [c["peak_px"]], color=col, s=40, zorder=5, edgecolors="k", lw=0.4)
        # mark up steps
        sub = slice_to(g, NOON)
        for ui in c.get("up_step_indices") or []:
            if ui + 1 < len(sub):
                ax.plot(
                    [sub.index[ui], sub.index[ui + 1]],
                    [sub["Close"].iloc[ui], sub["Close"].iloc[ui + 1]],
                    color=col,
                    lw=2.2,
                    alpha=0.9,
                )
    for t, lab, col in [(dtime(11, 15), "11:15", "#ea580c"), (dtime(12, 0), "12:00", "#ca8a04")]:
        m = g[g.index.time == t]
        if len(m):
            ax.axvline(m.index[0], color=col, ls="--", lw=1, label=lab)
    rises = ",".join(f"{100*c['rise']:.1f}%" for c in row["castles_by_1130"])
    ax.set_title(
        f"SPCX {row['date']}  castles={row['n_castles_by_1130']} rises=[{rises}]  "
        f"c/o={100*row['close_vs_open_pct']:.2f}%  11:15->close={100*row['ret_1115_to_close']:.2f}%",
        fontsize=9,
    )
    ax.legend(loc="best", fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=g.index.tz))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_grid(pairs, out, title):
    n = len(pairs)
    if n == 0:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, "no matches", ha="center")
        ax.axis("off")
        fig.savefig(out, dpi=120)
        plt.close(fig)
        return
    cols = min(3, n)
    rows_n = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows_n, cols, figsize=(5.2 * cols, 3.3 * rows_n), squeeze=False)
    colors = ["#3b82f6", "#f59e0b", "#10b981"]
    for i, (g, row) in enumerate(pairs):
        r, c = divmod(i, cols)
        ax = axes[r][c]
        ax.step(g.index, g["Close"].to_numpy(float), where="post", color="#1e293b", lw=1.0)
        for j, cas in enumerate(row["castles_by_1130"]):
            col = colors[j % len(colors)]
            ax.axvspan(pd.Timestamp(cas["start_time"]), pd.Timestamp(cas["end_time"]), color=col, alpha=0.25)
            ax.scatter([pd.Timestamp(cas["peak_time"])], [cas["peak_px"]], color=col, s=22, zorder=5)
        for t, col in [(dtime(11, 15), "#ea580c"), (dtime(12, 0), "#ca8a04")]:
            m = g[g.index.time == t]
            if len(m):
                ax.axvline(m.index[0], color=col, ls="--", lw=0.7)
        rises = ",".join(f"{100*x['rise']:.1f}" for x in row["castles_by_1130"])
        ax.set_title(
            f"{row.get('ticker','SPCX')} {row['date']} n={row['n_castles_by_1130']} "
            f"r=[{rises}] c/o={100*row['close_vs_open_pct']:.1f}% "
            f"11:15c={100*row['ret_1115_to_close']:.1f}%",
            fontsize=7,
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=g.index.tz))
        ax.tick_params(labelsize=6)
        ax.grid(True, alpha=0.25)
    for j in range(n, rows_n * cols):
        r, c = divmod(j, cols)
        axes[r][c].axis("off")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def trade_table(rows, key_trade, key_base, label):
    trades = [r[key_trade] for r in rows if r.get("is_match") and r.get(key_trade) == r.get(key_trade)]
    bases = [r[key_base] for r in rows]
    pt = pack_rets(trades, f"match_{label}")
    pb = pack_rets(bases, f"all_{label}")
    # binomial: match hit vs all hit
    t = np.asarray(trades, float)
    t = t[~np.isnan(t)]
    b = np.asarray(bases, float)
    b = b[~np.isnan(b)]
    p0 = float(np.mean(b > 0)) if len(b) else float("nan")
    pval = binomial_p(int(np.sum(t > 0)), len(t), p0) if len(t) else float("nan")
    return {"trade": pt, "baseline": pb, "binomial_p": pval}


def main():
    t0 = time.time()
    CHART.mkdir(parents=True, exist_ok=True)

    # ----- SPCX -----
    print("=== SPCX ===")
    spcx = load_bars(SPCX_CSV)
    sessions = session_days(spcx)
    sep11_g = None
    for day, g in sessions:
        if str(pd.Timestamp(day).date()) == "2026-09-11":
            sep11_g = g
            break
    verify = verify_sep11(sep11_g)
    print("VERIFY Sep11 castles:", json.dumps(verify["castles"], indent=2, default=str))
    print("VERIFY Sep11 falses:", json.dumps(verify["falses"], indent=2, default=str))

    spcx_rows = []
    spcx_matches = []
    for day, g in sessions:
        row = analyze_day(g, "SPCX")
        spcx_rows.append(row)
        if row["is_match"]:
            spcx_matches.append((g, row))

    print(f"SPCX matches 2+ by 11:30: {len(spcx_matches)} / {len(spcx_rows)}")

    for g, row in spcx_matches:
        p = unique_path(CHART / f"spcx_{row['date']}.png")
        plot_spcx_match(g, row, p)
        row["chart"] = str(p)

    grid = unique_path(CHART / "spcx_matches_grid_v3.png")
    plot_grid(spcx_matches, grid, "SPCX step-castle matches (2+ castles by 11:30, rise<=5%)")

    # ----- MULTI -----
    print("=== MULTI ===")
    screen = pd.read_csv(OUT / "multi_universe_screen.csv")
    universe = screen[screen["pass_price"] & screen["pass_vol"]]["ticker"].tolist()
    paths = {}
    for t in universe:
        p = DATA / f"{t}_5m.csv"
        if p.exists() and p.stat().st_size > 1000:
            paths[t] = p
    paths["SPCX"] = SPCX_CSV
    print(f"tickers with 5m: {len(paths)}")

    multi_rows = []
    multi_matches = []
    for ti, (ticker, path) in enumerate(paths.items()):
        if ti % 10 == 0:
            print(f"  {ti}/{len(paths)} {ticker}")
        try:
            df = load_bars(path)
        except Exception as e:
            print(f"  skip {ticker}: {e}")
            continue
        for day, g in session_days(df):
            row = analyze_day(g, ticker)
            multi_rows.append(row)
            if row["is_match"]:
                multi_matches.append((g, row))

    print(f"MULTI matches: {len(multi_matches)} / {len(multi_rows)}")

    # sample grid of multi matches (up to 12)
    multi_grid = unique_path(CHART / "multi_matches_grid_v3.png")
    plot_grid(multi_matches[:12], multi_grid, "Multi step-castle matches sample (2+ by 11:30)")

    # type counts
    def type_counts(rows):
        s = pd.Series([r["day_type"] for r in rows]).value_counts().to_dict()
        return s

    # trades
    trade_keys = [
        ("trade_exit_1200", "base_1115_to_1200", "exit_1200"),
        ("trade_exit_1300", "base_1115_to_1300", "exit_1300"),
        ("trade_exit_close", "base_1115_to_close", "exit_close"),
    ]

    def all_trade_stats(rows):
        out = {}
        for tk, bk, lab in trade_keys:
            out[lab] = trade_table(rows, tk, bk, lab)
        # half split on matches
        dates = sorted({r["date"] for r in rows})
        mid = dates[len(dates) // 2] if dates else None
        first = [r for r in rows if r["date"] <= mid]
        second = [r for r in rows if r["date"] > mid]
        out["half"] = {
            "mid": mid,
            "first_close": trade_table(first, "trade_exit_close", "base_1115_to_close", "first_close"),
            "second_close": trade_table(second, "trade_exit_close", "base_1115_to_close", "second_close"),
        }
        # by day type: use 11:15->close descriptive
        by_type = {}
        for typ in ["two_plus_castles", "single_castle", "false_only", "none", "other"]:
            subset = [r for r in rows if r["day_type"] == typ]
            by_type[typ] = pack_rets([r["ret_1115_to_close"] for r in subset], typ)
            by_type[typ]["n_days"] = len(subset)
        out["by_type_1115_to_close"] = by_type
        return out

    spcx_stats = all_trade_stats(spcx_rows)
    multi_stats = all_trade_stats(multi_rows)

    # save csvs
    def flat(row):
        d = {k: v for k, v in row.items() if k not in ("castles", "castles_by_1130", "falses")}
        d["rises"] = ",".join(f"{c['rise']:.4f}" for c in row.get("castles_by_1130", []))
        d["castle_starts"] = ",".join(c["start_time"] for c in row.get("castles_by_1130", []))
        return d

    spcx_csv = unique_path(OUT / "castle_steps_spcx_v3.csv")
    multi_csv = unique_path(OUT / "castle_steps_multi_v3.csv")
    match_csv = unique_path(OUT / "castle_steps_multi_matches_v3.csv")
    pd.DataFrame([flat(r) for r in spcx_rows]).to_csv(spcx_csv, index=False)
    pd.DataFrame([flat(r) for r in multi_rows]).to_csv(multi_csv, index=False)
    pd.DataFrame([flat(r) for r in multi_rows if r["is_match"]]).to_csv(match_csv, index=False)

    # summary
    md = unique_path(OUT / "castle_steps_summary_v3.md")
    lines = []
    lines.append("# Castle steps v3")
    lines.append("")
    lines.append("## Definition (fixed)")
    lines.append("")
    lines.append(
        "- Castle: run of >= 3 up steps (5m close-to-close), allowing at most 1 small down "
        "(< half the average up step in the run), ending at a local peak, then pullback "
        "giving back >= 25% of the rise."
    )
    lines.append(
        "- NOT a castle if the largest up step is > 50% of the run's rise (jump / false castle)."
    )
    lines.append(
        f"- Cap: castle peak rise from its start <= {100*PEAK_RISE_CAP:.0f}% of start price."
    )
    lines.append(
        "- Match: >= 2 such castles with pullback ending by ~11:30 ET (scan window to 12:00)."
    )
    lines.append(
        "- Trade (fixed): enter at open of the bar after the 2nd castle pullback ends, "
        "but not before 11:15 (entry = max(after_2nd, 11:15)); exit 12:00 / 13:00 / close; 1 bp/side."
    )
    lines.append(
        "- Baseline: buy every day at 11:15 open, same exits."
    )
    lines.append("")
    lines.append("## SPCX Sep 11 verification")
    lines.append("")
    lines.append("Expected: castles near 09:45->10:05 and 10:50->~11:10; reject 09:30 jump and 10:20 bump.")
    lines.append("")
    lines.append("Found castles:")
    for c in verify["castles"]:
        lines.append(
            f"- start {c['start']} peak {c['peak']} end {c['end']} "
            f"rise={fmt_pct(c['rise'])} ups={c['n_up']} max_step_frac={c['max_step_frac']:.2f}"
        )
    lines.append("Found false jumps:")
    for f in verify["falses"]:
        lines.append(
            f"- start {f['start']} peak {f['peak']} rise={fmt_pct(f['rise'])} "
            f"max_step_frac={f['max_step_frac']:.2f} reason={f['reason']}"
        )
    # auto check
    starts = [c["start"][11:16] if len(c["start"]) > 16 else c["start"] for c in verify["castles"]]
    lines.append(f"- castle start clock times: {starts}")
    ok_945 = any("09:45" <= (c["start"][11:16] if " " in c["start"] else "") <= "09:55" for c in verify["castles"]) or any(
        "09:45" in c["start"] or "09:50" in c["start"] for c in verify["castles"]
    )
    ok_1050 = any("10:45" in c["start"] or "10:50" in c["start"] or "10:40" in c["start"] for c in verify["castles"])
    lines.append(f"- approx 09:45 castle found: {ok_945}; approx 10:50 castle found: {ok_1050}")
    lines.append("")
    lines.append(f"## SPCX matches: {len(spcx_matches)} / {len(spcx_rows)}")
    lines.append("")
    lines.append(f"day type counts: {type_counts(spcx_rows)}")
    lines.append("")
    if spcx_matches:
        lines.append("| date | n | rises | c/o | 11:15->close | trade->close |")
        lines.append("|---|---:|---|---:|---:|---:|")
        for _, r in spcx_matches:
            rises = ",".join(fmt_pct(c["rise"]) for c in r["castles_by_1130"])
            lines.append(
                f"| {r['date']} | {r['n_castles_by_1130']} | {rises} | "
                f"{fmt_pct(r['close_vs_open_pct'])} | {fmt_pct(r['ret_1115_to_close'])} | "
                f"{fmt_pct(r['trade_exit_close'])} |"
            )
    lines.append("")
    lines.append("### SPCX trade vs baseline")
    lines.append("")
    for lab, block in spcx_stats.items():
        if lab in ("half", "by_type_1115_to_close"):
            continue
        tr, bl = block["trade"], block["baseline"]
        lines.append(
            f"- {lab}: match n={tr.get('n')} hit {fmt_pct(tr.get('hit_rate'))} avg {fmt_pct(tr.get('avg'))} "
            f"CI [{fmt_pct(tr.get('ci95_lo'))}, {fmt_pct(tr.get('ci95_hi'))}] || "
            f"all n={bl.get('n')} hit {fmt_pct(bl.get('hit_rate'))} avg {fmt_pct(bl.get('avg'))} || "
            f"binom p={block['binomial_p']:.4g}"
        )
    lines.append("")
    lines.append(f"## Multi universe ({len(paths)} tickers)")
    lines.append("")
    lines.append(f"- ticker-days: {len(multi_rows)}; matches: {len(multi_matches)}")
    lines.append(f"- day type counts: {type_counts(multi_rows)}")
    lines.append("")
    lines.append("### Multi trade vs baseline")
    lines.append("")
    for lab, block in multi_stats.items():
        if lab in ("half", "by_type_1115_to_close"):
            continue
        tr, bl = block["trade"], block["baseline"]
        lines.append(
            f"- {lab}: match n={tr.get('n')} hit {fmt_pct(tr.get('hit_rate'))} avg {fmt_pct(tr.get('avg'))} "
            f"CI [{fmt_pct(tr.get('ci95_lo'))}, {fmt_pct(tr.get('ci95_hi'))}] || "
            f"all n={bl.get('n')} hit {fmt_pct(bl.get('hit_rate'))} avg {fmt_pct(bl.get('avg'))} || "
            f"binom p={block['binomial_p']:.4g}"
        )
    lines.append("")
    lines.append("### Multi half split (exit close)")
    lines.append("")
    for which in ("first_close", "second_close"):
        block = multi_stats["half"][which]
        tr, bl = block["trade"], block["baseline"]
        lines.append(
            f"- {which} (mid={multi_stats['half']['mid']}): match n={tr.get('n')} avg {fmt_pct(tr.get('avg'))} "
            f"vs all avg {fmt_pct(bl.get('avg'))} p={block['binomial_p']:.4g}"
        )
    lines.append("")
    lines.append("### Multi by day type (11:15->close, descriptive)")
    lines.append("")
    lines.append("| type | n | hit | avg | median |")
    lines.append("|---|---:|---:|---:|---:|")
    for typ, s in multi_stats["by_type_1115_to_close"].items():
        lines.append(
            f"| {typ} | {s.get('n',0)} | {fmt_pct(s.get('hit_rate'))} | "
            f"{fmt_pct(s.get('avg'))} | {fmt_pct(s.get('median'))} |"
        )
    lines.append("")
    lines.append(
        "SMALL SAMPLE / exploratory: fixed rules, no optimizing, but many comparisons. "
        "do not treat as a green light."
    )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(f"- spcx grid: `{grid}`")
    lines.append(f"- multi grid sample: `{multi_grid}`")
    lines.append(f"- spcx csv: `{spcx_csv}`")
    lines.append(f"- multi csv: `{multi_csv}`")
    lines.append(f"- multi matches csv: `{match_csv}`")
    lines.append("")
    lines.append(
        f"Generated at (America/Chicago): {datetime.now().astimezone().isoformat(timespec='seconds')}"
    )
    md.write_text("\n".join(lines), encoding="utf-8")

    raw = {
        "verify_sep11": verify,
        "spcx_n_match": len(spcx_matches),
        "spcx_type_counts": type_counts(spcx_rows),
        "multi_n_match": len(multi_matches),
        "multi_n_days": len(multi_rows),
        "multi_type_counts": type_counts(multi_rows),
        "spcx_stats": spcx_stats,
        "multi_stats": multi_stats,
        "elapsed_sec": round(time.time() - t0, 1),
        "summary": str(md),
        "grid": str(grid),
    }
    raw_path = unique_path(OUT / "castle_steps_raw_v3.json")
    raw_path.write_text(json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print(f"wrote {md}")
    print(f"elapsed {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
