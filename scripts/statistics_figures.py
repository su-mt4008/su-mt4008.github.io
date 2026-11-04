# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib"]
# ///
"""Figures and numbers for the /statistics page.

Run from the repository root:  uv run scripts/statistics_figures.py
Writes SVGs to public/img/statistics/ and prints every number the page quotes.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("public/data/statistics/smhi-lund-daily-temperature.csv")
OUT = Path("public/img/statistics")
OUT.mkdir(parents=True, exist_ok=True)

RED, GREY, LIGHT, INK = "#d6453d", "#8a8a8a", "#c8c8c8", "#8a8a8a"
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "svg.hashsalt": "mt4008",
})
rng = np.random.default_rng(4008)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None})  # same file every run
    plt.close(fig)


# --- Data: annual mean temperature, complete years only -----------------------
raw = pd.read_csv(DATA, sep=";", skiprows=12, header=0, usecols=[2, 3],
                  names=["date", "temp"], parse_dates=["date"])
days = raw.groupby(raw["date"].dt.year)["temp"].agg(["count", "mean"])
complete = days[(days["count"] >= 365)]
years = complete.loc[1997:2025, "mean"]
a = years.loc[:2010]   # 1997–2010
b = years.loc[2011:]   # 2011–2025
print("incomplete years:", days[days["count"] < 365]["count"].to_dict())
print(f"n_a={len(a)} n_b={len(b)}")
print(f"mean_a={a.mean():.2f} median_a={a.median():.2f} sd_a={a.std():.2f}")
print(f"mean_b={b.mean():.2f} median_b={b.median():.2f} sd_b={b.std():.2f}")
diff = b.mean() - a.mean()
print(f"diff={diff:.2f}")

# 1. The data
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(years.index, years.values, "o", color=GREY, ms=5)
ax.hlines(a.mean(), a.index.min() - .4, a.index.max() + .4, color=RED, lw=2)
ax.hlines(b.mean(), b.index.min() - .4, b.index.max() + .4, color=RED, lw=2)
ax.text(a.index.min(), a.mean() + .08, f"1997–2010: {a.mean():.2f} °C", color=RED, va="bottom")
ax.text(b.index.min(), b.mean() + .08, f"2011–2025: {b.mean():.2f} °C", color=RED, va="bottom")
ax.set_ylabel("Mean temperature (°C)")
save(fig, "data")

# 2. Spread: single years vary a lot
fig, ax = plt.subplots(figsize=(7, 2.6))
for i, (s, lab) in enumerate([(a, "1997–2010"), (b, "2011–2025")]):
    jitter = rng.uniform(-.08, .08, len(s))
    ax.plot(s.values, i + jitter, "o", color=GREY, ms=6, alpha=.8)
    ax.plot([s.mean() - s.std(), s.mean() + s.std()], [i + .3, i + .3], color=RED, lw=2)
    ax.plot(s.mean(), i + .3, "|", color=RED, ms=14, mew=2)
ax.set_yticks([0, 1], ["1997–2010", "2011–2025"])
ax.set_ylim(-.4, 1.6)
ax.set_xlabel("Mean temperature of one year (°C).  Red: mean ± one standard deviation")
save(fig, "spread")

# 3. Sampling distribution: means of n years vary much less than single years
mu, sigma, n = a.mean(), a.std(), len(a)
singles = rng.normal(mu, sigma, 100_000)
means = rng.normal(mu, sigma, (100_000, n)).mean(axis=1)
se = sigma / np.sqrt(n)
print(f"se_a={se:.2f} (sd of simulated means={means.std():.2f})")
fig, ax = plt.subplots(figsize=(7, 3))
bins = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 80)
ax.hist(singles, bins, density=True, color=LIGHT, label="one year")
ax.hist(means, bins, density=True, color=RED, alpha=.85, label=f"mean of {n} years")
ax.set_xlabel("°C")
ax.set_yticks([])
ax.legend(frameon=False)
save(fig, "sampling")

# 4. Confidence intervals: about 19 in 20 cover the true value
# Illustration seed: the first one where 1 of 20 intervals misses, as happens on average.
def ci_misses(seed):
    g = np.random.default_rng(seed)
    out = []
    for _ in range(20):
        s = g.normal(mu, sigma, n)
        h = 1.96 * s.std(ddof=1) / np.sqrt(n)
        out.append((s, h))
    return out, sum(not (s.mean() - h <= mu <= s.mean() + h) for s, h in out)
seed = next(k for k in range(1000) if ci_misses(k)[1] == 1)
samples, _ = ci_misses(seed)
fig, ax = plt.subplots(figsize=(7, 3.4))
miss = 0
for i, (s, _) in enumerate(samples):
    m, h = s.mean(), 1.96 * s.std(ddof=1) / np.sqrt(n)
    ok = m - h <= mu <= m + h
    miss += not ok
    ax.plot([m - h, m + h], [i, i], color=GREY if ok else RED, lw=2)
    ax.plot(m, i, "o", color=GREY if ok else RED, ms=4)
ax.axvline(mu, color=INK, ls="--", lw=1)
ax.set_yticks([])
ax.set_xlabel(f"°C.  Dashed: the true mean.  Each line: a 95% interval from a new sample of {n} years")
print("intervals missing the true mean:", miss, "of 20")
save(fig, "intervals")

# Formula interval for the difference (normal approximation)
se_diff = np.sqrt(a.var() / len(a) + b.var() / len(b))
print(f"se_diff={se_diff:.2f} formula 95% CI=({diff - 1.96 * se_diff:.2f}, {diff + 1.96 * se_diff:.2f}) z={diff / se_diff:.2f}")

# 5. Bootstrap
boot = np.array([rng.choice(b.values, len(b)).mean() - rng.choice(a.values, len(a)).mean() for _ in range(10_000)])
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"bootstrap 95% CI=({lo:.2f}, {hi:.2f})")
fig, ax = plt.subplots(figsize=(7, 3))
cnt, edges, patches = ax.hist(boot, 60, color=LIGHT)
for p, left in zip(patches, edges[:-1]):
    if lo <= left <= hi:
        p.set_facecolor(RED)
ax.axvline(0, color=INK, ls="--", lw=1)
ax.set_yticks([])
ax.set_xlabel("Difference 2011–2025 minus 1997–2010 (°C), in 10,000 resampled datasets.  Red: middle 95%")
save(fig, "bootstrap")

# 6. Permutation test
pooled = np.concatenate([a.values, b.values])
perm = np.empty(10_000)
for i in range(perm.size):
    rng.shuffle(pooled)
    perm[i] = pooled[len(a):].mean() - pooled[:len(a)].mean()
p = np.mean(np.abs(perm) >= abs(diff))
print(f"permutation p={p:.3f}")
fig, ax = plt.subplots(figsize=(7, 3))
cnt, edges, patches = ax.hist(perm, 60, color=LIGHT)
for patch, left, right in zip(patches, edges[:-1], edges[1:]):
    if right > abs(diff) or left < -abs(diff):
        patch.set_facecolor(RED)
ax.axvline(diff, color=RED, lw=2)
ax.text(diff, cnt.max() * .9, f"  observed: {diff:.2f} °C", color=RED)
ax.set_yticks([])
ax.set_xlabel("Difference (°C) when the years are shuffled between the periods at random")
save(fig, "permutation")

# 7. Trend
x, yv = years.index.values.astype(float), years.values
coef, cov = np.polyfit(x, yv, 1, cov=True)
slope, slope_se = coef[0], np.sqrt(cov[0, 0])
r = np.corrcoef(x, yv)[0, 1]
print(f"slope={slope * 10:.2f} C/decade, 95% CI=({(slope - 1.96 * slope_se) * 10:.2f}, {(slope + 1.96 * slope_se) * 10:.2f}), r={r:.2f}")
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(x, yv, "o", color=GREY, ms=5)
ax.plot(x, np.polyval(coef, x), color=RED, lw=2)
ax.text(x[0], np.polyval(coef, x[-1]) + .3, f"trend: {slope * 10:.2f} °C per decade", color=RED)
ax.set_ylabel("Mean temperature (°C)")
save(fig, "trend")

# 8. Multiple comparisons: 20 tests on pure noise
from math import erf, sqrt


def noise_pvalues(seed):
    g = np.random.default_rng(seed)
    out = []
    for _ in range(20):
        g1, g2 = g.normal(0, 1, 14), g.normal(0, 1, 14)
        z = (g2.mean() - g1.mean()) / np.sqrt(g1.var(ddof=1) / 14 + g2.var(ddof=1) / 14)
        out.append(2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2)))))
    return np.array(out)


# Illustration seed: the first one where 1 of 20 noise tests is "significant", as happens on average.
pvals = next(p for p in (noise_pvalues(k) for k in range(1000)) if (p < .05).sum() == 1)
print("noise tests with p<0.05:", int((pvals < .05).sum()), "of 20")
fig, ax = plt.subplots(figsize=(7, 2.8))
ax.bar(range(1, 21), pvals, color=[RED if q < .05 else LIGHT for q in pvals])
ax.axhline(.05, color=INK, ls="--", lw=1)
ax.text(20.6, .05, " 0.05", va="center")
ax.set_xticks(range(1, 21))
ax.set_xlabel("20 comparisons of two groups of pure random noise")
ax.set_ylabel("p-value")
save(fig, "many-tests")
