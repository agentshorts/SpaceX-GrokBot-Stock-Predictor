#!/usr/bin/env python3
"""
Castle steps v4: SPCX only. Same detector as v3 but min_up_steps parameterized.
Compare min_up_steps=2 vs 3 side by side. v3 untouched. Outputs under castle_steps_v4/.
"""

from __future__ import annotations

import json
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
CHART = OUT / "castle_steps_v4"
SPCX_CSV = OUT / "data_bands_SPCX_5m_v5.csv"
COST = 1e-4
PEAK_RISE_CAP = 0.05
NOON = dtime(12, 0)
MATCH_BY = dtime(11, 30)
ENTRY_FALLBACK = dtime(11, 15)
RNG = np.random.default_rng(23)

MAX_SMALL_DOWNS_IN_CLIMB = 1
SMALL_DOWN_FRAC = 0.5
MAX_SINGLE_STEP_FRAC = 0.50
MIN_PULLBACK_FRAC = 0.25
MIN_RISE = 0.003


@dataclass
class Castle:
    start_i: int
    peak_i: int
    end_i: int
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


def find_castles(closes: np.ndarray, times, min_up_steps: int = 3) -> tuple[list[Castle], list[FalseJump]]:
    """Same as v3 but min_up_steps is a parameter (default 3)."""
    n = len(closes)
    if n < 5:
        return [], []
    diffs = np.diff(closes)
    castles: list[Castle] = []
    falses: list[FalseJump] = []
    i = 0
    while i < n - 3:
        up_steps = []
        down_small = 0
        j = i
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
            if not last_up_vals:
                break
            break

        if len(up_steps) < min_up_steps:
            if len(up_steps) >= 1:
                peak_i = up_steps[-1] + 1
                base = float(closes[i])
                peak = float(closes[peak_i])
                if peak > base:
                    rise = (peak - base) / base
                    ups = np.array([diffs[k] for k in up_steps])
                    max_frac = float(np.max(ups) / (peak - base)) if peak > base else 1.0
                    if rise >= MIN_RISE and (len(up_steps) < min_up_steps or max_frac > MAX_SINGLE_STEP_FRAC):
                        falses.append(
                            FalseJump(
                                start_i=i,
                                peak_i=peak_i,
                                rise=rise,
                                max_step_frac=max_frac,
                                reason="too_few_steps" if len(up_steps) < min_up_steps else "dominant_bar",
                                start_time=str(times[i]),
                                peak_time=str(times[peak_i]),
                            )
                        )
                        i = peak_i
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

        if peak_i + 1 < n and closes[peak_i + 1] > peak:
            i += 1
            continue

        end_i = peak_i
        pulled = 0.0
        k = peak_i
        while k < n - 1:
            nd = diffs[k]
            if nd < 0:
                pulled += -nd
                end_i = k + 1
                k += 1
                if pulled / (peak - base) >= MIN_PULLBACK_FRAC:
                    if k < n - 1 and diffs[k] >= 0:
                        break
                    continue
                continue
            if nd >= 0:
                if pulled / (peak - base) >= MIN_PULLBACK_FRAC or end_i > peak_i:
                    break
                break

        giveback = pulled / (peak - base) if peak > base else 0.0
        if end_i == peak_i or giveback < MIN_PULLBACK_FRAC:
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
        i = end_i
    return castles, falses


def within_cap(c: Castle) -> bool:
    return c.rise <= PEAK_RISE_CAP


def analyze_day(g: pd.DataFrame, ticker: str, min_up_steps: int) -> dict:
    sub = slice_to(g, NOON)
    closes = sub["Close"].to_numpy(float)
    times = sub.index
    castles, falses = find_castles(closes, times, min_up_steps=min_up_steps)
    castles_cap = [c for c in castles if within_cap(c)]

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
        day_type = "single_castle" if n_castles == 1 else ("two_plus_castles" if n_castles >= 2 else "other")

    entry_i = None
    entry_reason = None

    def bar_i_at(t: dtime):
        m = np.where(g.index.map(lambda x: x.time() == t))[0]
        return int(m[0]) if len(m) else None

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
        elif fb is not None:
            entry_i = fb
            entry_reason = "fallback_1115"

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

    px_1115 = (
        float(g[g.index.time == dtime(11, 15)]["Close"].iloc[0])
        if len(g[g.index.time == dtime(11, 15)])
        else float("nan")
    )

    return {
        "ticker": ticker,
        "date": str(g.index[0].date()),
        "min_up_steps": min_up_steps,
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


def verify_sep11(g: pd.DataFrame, min_up_steps: int) -> dict:
    sub = slice_to(g, NOON)
    castles, falses = find_castles(sub["Close"].to_numpy(float), sub.index, min_up_steps=min_up_steps)
    castles = [c for c in castles if within_cap(c)]
    return {
        "min_up_steps": min_up_steps,
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
            f"SPCX {row['date']} n={row['n_castles_by_1130']} "
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
    t = np.asarray(trades, float)
    t = t[~np.isnan(t)]
    b = np.asarray(bases, float)
    b = b[~np.isnan(b)]
    p0 = float(np.mean(b > 0)) if len(b) else float("nan")
    pval = binomial_p(int(np.sum(t > 0)), len(t), p0) if len(t) else float("nan")
    return {"trade": pt, "baseline": pb, "binomial_p": pval}


def type_counts(rows):
    return pd.Series([r["day_type"] for r in rows]).value_counts().to_dict()


def all_trade_stats(rows):
    trade_keys = [
        ("trade_exit_1200", "base_1115_to_1200", "exit_1200"),
        ("trade_exit_1300", "base_1115_to_1300", "exit_1300"),
        ("trade_exit_close", "base_1115_to_close", "exit_close"),
    ]
    out = {}
    for tk, bk, lab in trade_keys:
        out[lab] = trade_table(rows, tk, bk, lab)
    dates = sorted({r["date"] for r in rows})
    mid = dates[len(dates) // 2] if dates else None
    first = [r for r in rows if r["date"] <= mid]
    second = [r for r in rows if r["date"] > mid]
    out["half"] = {
        "mid": mid,
        "first_close": trade_table(first, "trade_exit_close", "base_1115_to_close", "first_close"),
        "second_close": trade_table(second, "trade_exit_close", "base_1115_to_close", "second_close"),
        "first_1200": trade_table(first, "trade_exit_1200", "base_1115_to_1200", "first_1200"),
        "second_1200": trade_table(second, "trade_exit_1200", "base_1115_to_1200", "second_1200"),
    }
    return out


def flat(row):
    d = {k: v for k, v in row.items() if k not in ("castles", "castles_by_1130", "falses")}
    d["rises"] = ",".join(f"{c['rise']:.4f}" for c in row.get("castles_by_1130", []))
    d["castle_starts"] = ",".join(c["start_time"] for c in row.get("castles_by_1130", []))
    return d


def fmt_line_stats(block, lab):
    tr, bl = block["trade"], block["baseline"]
    return (
        f"- {lab}: match n={tr.get('n')} hit {fmt_pct(tr.get('hit_rate'))} avg {fmt_pct(tr.get('avg'))} "
        f"med {fmt_pct(tr.get('median'))} CI [{fmt_pct(tr.get('ci95_lo'))}, {fmt_pct(tr.get('ci95_hi'))}] || "
        f"all n={bl.get('n')} hit {fmt_pct(bl.get('hit_rate'))} avg {fmt_pct(bl.get('avg'))} || "
        f"binom p={block['binomial_p']:.4g}"
    )


def run_variant(sessions, sep11_g, min_up_steps: int):
    verify = verify_sep11(sep11_g, min_up_steps)
    rows = []
    matches = []
    day_gs = {}
    for day, g in sessions:
        row = analyze_day(g, "SPCX", min_up_steps=min_up_steps)
        rows.append(row)
        day_gs[row["date"]] = g
        if row["is_match"]:
            matches.append((g, row))
    stats_ = all_trade_stats(rows)
    return {
        "min_up_steps": min_up_steps,
        "verify": verify,
        "rows": rows,
        "matches": matches,
        "day_gs": day_gs,
        "stats": stats_,
        "type_counts": type_counts(rows),
        "n_match": len(matches),
        "n_days": len(rows),
    }


def main():
    t0 = time.time()
    CHART.mkdir(parents=True, exist_ok=True)

    print("=== SPCX castle_steps_v4 ===")
    spcx = load_bars(SPCX_CSV)
    sessions = list(session_days(spcx))
    sep11_g = None
    for day, g in sessions:
        if str(pd.Timestamp(day).date()) == "2026-09-11":
            sep11_g = g
            break

    variants = {}
    for mus in (3, 2):
        print(f"--- min_up_steps={mus} ---")
        variants[mus] = run_variant(sessions, sep11_g, mus)
        v = variants[mus]
        print(f"matches {v['n_match']} / {v['n_days']} types {v['type_counts']}")
        print("Sep11 castles:", json.dumps(v["verify"]["castles"], indent=2, default=str))
        print("Sep11 falses:", json.dumps(v["verify"]["falses"], indent=2, default=str))

    # reproduce v3 check
    v3_match_dates = set()
    v3_csv = OUT / "castle_steps_spcx_v3.csv"
    if v3_csv.exists():
        v3df = pd.read_csv(v3_csv)
        v3_match_dates = set(v3df.loc[v3df["is_match"], "date"].astype(str))
        v3_types = v3df["day_type"].value_counts().to_dict()
        v3_n = int(v3df["is_match"].sum())
    else:
        v3_types, v3_n = {}, None

    v3_repro = variants[3]
    repro_dates = {r["date"] for r in v3_repro["rows"] if r["is_match"]}
    repro_ok = (
        v3_repro["n_match"] == v3_n
        and repro_dates == v3_match_dates
        and v3_repro["type_counts"] == v3_types
    )
    print(f"v3 reproduce (min=3): ok={repro_ok} n={v3_repro['n_match']} vs v3 n={v3_n}")
    print(f"  types v4min3={v3_repro['type_counts']} v3={v3_types}")

    # days match only under 2-step
    dates3 = {r["date"] for r in variants[3]["rows"] if r["is_match"]}
    dates2 = {r["date"] for r in variants[2]["rows"] if r["is_match"]}
    only2 = sorted(dates2 - dates3)
    only3 = sorted(dates3 - dates2)
    both = sorted(dates2 & dates3)
    print(f"match both: {len(both)}; only min2: {only2}; only min3: {only3}")

    # sep11 jump check under min=2
    v2 = variants[2]["verify"]
    def clock(s):
        return s[11:16] if len(s) > 16 else s

    castle_starts2 = [clock(c["start"]) for c in v2["castles"]]
    false_starts2 = [clock(f["start"]) for f in v2["falses"]]
    # did 09:30 or 10:20 become castles?
    accepted_0930 = any(c.startswith("09:3") for c in castle_starts2)
    accepted_1020 = any(c.startswith("10:2") for c in castle_starts2)
    still_false_0930 = any(f.startswith("09:3") for f in false_starts2)
    still_false_1020 = any(f.startswith("10:2") for f in false_starts2)

    # grid of 2-step-only new matches
    only2_pairs = [(variants[2]["day_gs"][d], next(r for r in variants[2]["rows"] if r["date"] == d)) for d in only2]
    grid_only2 = unique_path(CHART / "spcx_matches_min2_only_grid_v4.png")
    plot_grid(only2_pairs, grid_only2, "SPCX 2-step-only new matches (not matches under min_up=3)")

    grid3 = unique_path(CHART / "spcx_matches_min3_grid_v4.png")
    plot_grid(variants[3]["matches"], grid3, "SPCX min_up_steps=3 matches (should match v3)")

    grid2 = unique_path(CHART / "spcx_matches_min2_grid_v4.png")
    plot_grid(variants[2]["matches"], grid2, "SPCX min_up_steps=2 matches")

    # csvs
    csv3 = unique_path(CHART / "spcx_min3_v4.csv")
    csv2 = unique_path(CHART / "spcx_min2_v4.csv")
    pd.DataFrame([flat(r) for r in variants[3]["rows"]]).to_csv(csv3, index=False)
    pd.DataFrame([flat(r) for r in variants[2]["rows"]]).to_csv(csv2, index=False)
    only2_csv = unique_path(CHART / "spcx_min2_only_matches_v4.csv")
    pd.DataFrame([flat(r) for r in variants[2]["rows"] if r["date"] in set(only2)]).to_csv(only2_csv, index=False)

    # summary md
    md = unique_path(CHART / "castle_steps_summary_v4.md")
    lines = []
    lines.append("# Castle steps v4 (SPCX only, min_up_steps 2 vs 3)")
    lines.append("")
    lines.append("## Definition")
    lines.append("")
    lines.append(
        "- Same as v3 except min_up_steps is parameterized (compare 2 vs 3)."
    )
    lines.append(
        "- Castle: run of >= min_up_steps up steps (5m close-to-close), <=1 small down "
        "(< half avg up), local peak, pullback >= 25% of rise."
    )
    lines.append(
        "- NOT a castle if largest up step > 50% of rise (jump / false). Cap rise <= 5%."
    )
    lines.append(
        "- Match: >= 2 castles with pullback ending by ~11:30. Entry max(after_2nd, 11:15); "
        "exits 12:00 / 13:00 / close; 1 bp/side. Baseline: every day 11:15 open."
    )
    lines.append("")
    lines.append(f"## v3 reproduce check (min_up_steps=3)")
    lines.append("")
    lines.append(
        f"- ok={repro_ok}; v4 min3 matches={v3_repro['n_match']} types={v3_repro['type_counts']}; "
        f"v3 matches={v3_n} types={v3_types}"
    )
    lines.append("")
    lines.append("## Sep 11 verification")
    lines.append("")
    for mus in (3, 2):
        vv = variants[mus]["verify"]
        lines.append(f"### min_up_steps={mus}")
        lines.append("castles:")
        for c in vv["castles"]:
            lines.append(
                f"- start {c['start']} peak {c['peak']} end {c['end']} "
                f"rise={fmt_pct(c['rise'])} ups={c['n_up']} max_step_frac={c['max_step_frac']:.2f}"
            )
        lines.append("falses:")
        for f in vv["falses"]:
            lines.append(
                f"- start {f['start']} peak {f['peak']} rise={fmt_pct(f['rise'])} "
                f"max_step_frac={f['max_step_frac']:.2f} reason={f['reason']}"
            )
        lines.append("")
    lines.append(
        f"Under min_up=2: 09:30 jump accepted as castle? {accepted_0930} "
        f"(still false? {still_false_0930}); "
        f"10:20 bump accepted as castle? {accepted_1020} "
        f"(still false? {still_false_1020})."
    )
    lines.append(
        "Note: with min_up=2 a single big bar still has max_step_frac=1.0 so dominant_bar "
        "rejection still applies to 1-step jumps; 2 equal-ish steps can pass."
    )
    lines.append("")
    lines.append("## Side-by-side")
    lines.append("")
    lines.append("| metric | min_up=3 | min_up=2 |")
    lines.append("|---|---:|---:|")
    lines.append(f"| n days | {variants[3]['n_days']} | {variants[2]['n_days']} |")
    lines.append(f"| matches (2+) | {variants[3]['n_match']} | {variants[2]['n_match']} |")
    for typ in ("false_only", "single_castle", "two_plus_castles", "none", "other"):
        a = variants[3]["type_counts"].get(typ, 0)
        b = variants[2]["type_counts"].get(typ, 0)
        lines.append(f"| day_type {typ} | {a} | {b} |")
    for lab in ("exit_1200", "exit_1300", "exit_close"):
        for mus in (3, 2):
            pass
        t3 = variants[3]["stats"][lab]["trade"]
        t2 = variants[2]["stats"][lab]["trade"]
        b3 = variants[3]["stats"][lab]["baseline"]
        p3 = variants[3]["stats"][lab]["binomial_p"]
        p2 = variants[2]["stats"][lab]["binomial_p"]
        lines.append(
            f"| {lab} match hit | {fmt_pct(t3.get('hit_rate'))} | {fmt_pct(t2.get('hit_rate'))} |"
        )
        lines.append(
            f"| {lab} match avg | {fmt_pct(t3.get('avg'))} | {fmt_pct(t2.get('avg'))} |"
        )
        lines.append(
            f"| {lab} match med | {fmt_pct(t3.get('median'))} | {fmt_pct(t2.get('median'))} |"
        )
        lines.append(
            f"| {lab} match CI | [{fmt_pct(t3.get('ci95_lo'))}, {fmt_pct(t3.get('ci95_hi'))}] | "
            f"[{fmt_pct(t2.get('ci95_lo'))}, {fmt_pct(t2.get('ci95_hi'))}] |"
        )
        lines.append(
            f"| {lab} all avg (same baseline) | {fmt_pct(b3.get('avg'))} | {fmt_pct(b3.get('avg'))} |"
        )
        lines.append(f"| {lab} binom p | {p3:.4g} | {p2:.4g} |")
    lines.append("")
    lines.append("### Detail lines")
    lines.append("")
    for mus in (3, 2):
        lines.append(f"**min_up_steps={mus}**")
        for lab in ("exit_1200", "exit_1300", "exit_close"):
            lines.append(fmt_line_stats(variants[mus]["stats"][lab], lab))
        h = variants[mus]["stats"]["half"]
        for which in ("first_close", "second_close", "first_1200", "second_1200"):
            block = h[which]
            tr, bl = block["trade"], block["baseline"]
            lines.append(
                f"- {which} (mid={h['mid']}): match n={tr.get('n')} hit {fmt_pct(tr.get('hit_rate'))} "
                f"avg {fmt_pct(tr.get('avg'))} vs all avg {fmt_pct(bl.get('avg'))} p={block['binomial_p']:.4g}"
            )
        lines.append("")
    lines.append("## Days that become matches only under min_up=2")
    lines.append("")
    if only2:
        lines.append("| date | n | rises | c/o | 11:15->close | trade->close | trade->12:00 |")
        lines.append("|---|---:|---|---:|---:|---:|---:|")
        for d in only2:
            r = next(x for x in variants[2]["rows"] if x["date"] == d)
            rises = ",".join(fmt_pct(c["rise"]) for c in r["castles_by_1130"])
            lines.append(
                f"| {d} | {r['n_castles_by_1130']} | {rises} | "
                f"{fmt_pct(r['close_vs_open_pct'])} | {fmt_pct(r['ret_1115_to_close'])} | "
                f"{fmt_pct(r['trade_exit_close'])} | {fmt_pct(r['trade_exit_1200'])} |"
            )
    else:
        lines.append("(none)")
    lines.append("")
    lines.append(f"Both variants: {both}")
    lines.append(f"Only min3 (lost under min2): {only3}")
    lines.append("")
    lines.append("SMALL SAMPLE / exploratory. fixed rules, no optimizing.")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(f"- min3 grid: `{grid3}`")
    lines.append(f"- min2 grid: `{grid2}`")
    lines.append(f"- min2-only grid: `{grid_only2}`")
    lines.append(f"- csv min3: `{csv3}`")
    lines.append(f"- csv min2: `{csv2}`")
    lines.append(f"- csv min2-only: `{only2_csv}`")
    lines.append("")
    lines.append(
        f"Generated at (America/Chicago): {datetime.now().astimezone().isoformat(timespec='seconds')}"
    )
    md.write_text("\n".join(lines), encoding="utf-8")

    raw = {
        "v3_reproduce_ok": repro_ok,
        "v3_n": v3_n,
        "v3_types": v3_types,
        "sep11_min2_accepted_0930": accepted_0930,
        "sep11_min2_accepted_1020": accepted_1020,
        "sep11_min2_still_false_0930": still_false_0930,
        "sep11_min2_still_false_1020": still_false_1020,
        "only_min2_dates": only2,
        "only_min3_dates": only3,
        "both_dates": both,
        "variants": {
            str(mus): {
                "n_match": variants[mus]["n_match"],
                "type_counts": variants[mus]["type_counts"],
                "verify": variants[mus]["verify"],
                "stats": variants[mus]["stats"],
            }
            for mus in (3, 2)
        },
        "elapsed_sec": round(time.time() - t0, 1),
        "summary": str(md),
    }
    raw_path = unique_path(CHART / "castle_steps_raw_v4.json")
    raw_path.write_text(json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print(f"wrote {md}")
    print(f"elapsed {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
