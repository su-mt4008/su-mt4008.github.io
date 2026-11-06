# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib"]
# ///
"""Figures and numbers for week 2 (/lectures/week-2 and slides/week-2).

Run from the repository root:  uv run scripts/week2_figures.py
Writes SVGs to public/img/week-2/ and prints every number the page quotes.
The worked example is the 2018 Riksdag election by municipality, not HW2's data.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("public/data/week-2/election-2018-municipalities.csv")
OUT = Path("public/img/week-2")
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


# --- Reading: the naive way fails, the right way works --------------------------
try:
    pd.read_csv(DATA)
except pd.errors.ParserError as err:
    print("naive read fails:", str(err).splitlines()[-1])
raw = pd.read_csv(DATA, sep=";", decimal=",", encoding="utf-8-sig")
print("shape:", raw.shape)

votes = (
    raw.rename(columns={
        "LÄNSNAMN": "county", "KOMMUNNAMN": "municipality",
        "RÖSTANDE": "voters", "RÖSTBERÄTTIGADE": "electorate", "VALDELTAGANDE": "turnout",
    })
    [["county", "municipality", "electorate", "voters", "turnout"]]
)
votes["county"] = votes["county"].str.removesuffix(" län")
print(votes.head(3).to_string())
print("turnout describe:", votes["turnout"].describe().round(2).to_dict())

# Mean of municipal turnouts vs the national turnout (weighted by electorate)
print(f"mean of municipalities: {votes['turnout'].mean():.2f}")
print(f"national: {100 * votes['voters'].sum() / votes['electorate'].sum():.2f}")
print("lowest:", votes.nsmallest(3, "turnout")[["municipality", "turnout"]].to_dict("records"))
print("highest:", votes.nlargest(3, "turnout")[["municipality", "turnout"]].to_dict("records"))

by_county = (
    votes.groupby("county")
    .agg(n=("turnout", "size"), mean=("turnout", "mean"), median=("turnout", "median"),
         sd=("turnout", "std"), lowest=("turnout", "min"))
    .sort_values("mean")
)
print(by_county.round(2).to_string())

# 1. Distribution of one variable: histogram and its outliers
fig, ax = plt.subplots(figsize=(7, 3))
ax.hist(votes["turnout"], bins=np.arange(72, 95, 1), color=LIGHT, edgecolor=GREY)
for _, r in votes.nsmallest(3, "turnout").iterrows():
    ax.annotate(r["municipality"], (r["turnout"], 1), xytext=(r["turnout"], 9),
                ha="center", color=RED, arrowprops=dict(arrowstyle="-", color=RED))
ax.set_xlabel("Turnout in the 2018 Riksdag election (%), one municipality per count")
ax.set_ylabel("Municipalities")
save(fig, "turnout-histogram")

# 2. Comparing groups: every municipality, plus the county median
order = by_county.sort_values("median").index
fig, ax = plt.subplots(figsize=(9, 5.2))
for i, c in enumerate(order):
    x = votes.loc[votes["county"] == c, "turnout"]
    ax.plot(x, i + rng.uniform(-.18, .18, len(x)), "o", color=GREY, ms=3.5, alpha=.7)
    ax.plot(x.median(), i, "|", color=RED, ms=14, mew=2.5)
ax.set_yticks(range(len(order)), [f"{c} ({by_county.loc[c, 'n']})" for c in order])
ax.set_xlabel("Turnout (%). Grey: one municipality.  Red: the county median")
save(fig, "turnout-counties")

# 3. A misleading axis: the same three numbers, two y-axes
three = by_county.loc[["Norrbottens", "Stockholms", "Östergötlands"], "mean"]
three.index = ["Norrbotten", "Stockholm", "Östergötland"]
fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
for ax, bottom, title in [(axes[0], 84, "Axis starts at 84%"), (axes[1], 0, "Axis starts at 0%")]:
    ax.bar(three.index, three.values, color=[LIGHT, LIGHT, RED], edgecolor=GREY)
    ax.set_ylim(bottom, 90 if bottom else 100)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Mean turnout (%)")
save(fig, "misleading-axis")
print("three counties:", three.round(2).to_dict())

# 4. Relationship between two numeric variables: log scale for sizes
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(votes["electorate"], votes["turnout"], "o", color=GREY, ms=3.5, alpha=.7)
ax.set_xscale("log")
for name in ["Stockholm", "Göteborg", "Bjurholm", "Haparanda", "Lomma"]:
    r = votes.loc[votes["municipality"] == name].iloc[0]
    ax.annotate(name, (r["electorate"], r["turnout"]), xytext=(5, 3), textcoords="offset points",
                color=RED, fontsize=10)
ax.set_xlabel("People entitled to vote (log scale)")
ax.set_ylabel("Turnout (%)")
save(fig, "turnout-size")
r = np.corrcoef(np.log10(votes["electorate"]), votes["turnout"])[0, 1]
print(f"corr(log10 electorate, turnout) = {r:.2f}")
print("electorate range:", votes["electorate"].min(), votes["electorate"].max())
