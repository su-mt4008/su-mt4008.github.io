# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib"]
# ///
"""Figures and numbers for week 6 (/lectures/week-6 and slides/week-6).

Run from the repository root:  uv run scripts/week6_figures.py
Reads only saved files: the reviews (scripts/week6_data.py) and the model's labels
(scripts/week6_extract.py). No language model is needed here, just as in a report.
Writes SVGs to public/img/week-6/ and prints every number the page quotes.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("public/data/week-6")
OUT = Path("public/img/week-6")
OUT.mkdir(parents=True, exist_ok=True)

RED, GREY, LIGHT, INK = "#d6453d", "#8a8a8a", "#c8c8c8", "#8a8a8a"
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "svg.hashsalt": "mt4008",
})
FIELDS = ["sentiment", "made_it", "changed_recipe"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None})  # same file every run
    plt.close(fig)


def star_group(stars):
    return np.select([stars <= 2, stars == 3], ["negative", "mixed"], "positive")


def agreement(labels):
    """Agreement with the stars on the clear cases (1-2 and 4-5 stars), with a 95% interval."""
    d = reviews.merge(labels, on="review_id")
    clear = d[d["stars"] != 3]
    hit = clear["sentiment"] == star_group(clear["stars"])
    k, n = int(hit.sum()), len(hit)
    p = k / n
    se = np.sqrt(p * (1 - p) / n)
    return k, n, p, p - 1.96 * se, p + 1.96 * se


reviews = pd.read_csv(DATA / "recipe-reviews.csv")
labels = pd.read_csv(DATA / "llm-labels.csv")
d = reviews.merge(labels, on="review_id")
assert len(d) == len(reviews) == 250

print("LLM sentiment by stars:")
print(pd.crosstab(d["stars"], d["sentiment"])[["negative", "mixed", "positive"]])
d["expected"] = star_group(d["stars"])
print(pd.crosstab(d["expected"], d["sentiment"], margins=True))
print("share made_it:", d["made_it"].mean(), " share changed_recipe:", d["changed_recipe"].mean())
print("LLM said mixed:", (d["sentiment"] == "mixed").sum())

k, n, p, lo, hi = agreement(labels)
print(f"main: {k}/{n} = {p:.3f}, 95% CI [{lo:.3f}, {hi:.3f}], half-width {hi - p:.3f}")
for s in [1, 2, 4, 5]:
    x = d[d["stars"] == s]
    print(f"  {s} stars: {(x['sentiment'] == x['expected']).sum()}/50")
clear = d[d["stars"] != 3]
wrong = clear[clear["sentiment"] != clear["expected"]]
print("disagreements:", len(wrong), "of which the model said mixed:", (wrong["sentiment"] == "mixed").sum())
print(pd.crosstab(wrong["stars"], wrong["sentiment"]))

# What changes between runs?
variants = {
    "rerun": "Same settings, run again",
    "temperature-1": "Temperature 1, seed 4008",
    "temperature-1-seed-4009": "Temperature 1, seed 4009",
    "prompt-b": "Prompt worded differently",
    "llama3.2-1b": "Smaller model (llama3.2:1b)",
}
other = {v: pd.read_csv(DATA / "variants" / f"{v}.csv") for v in variants}
for v, x in other.items():
    assert (x["review_id"] == labels["review_id"]).all()
    changed = {f: int((x[f] != labels[f]).sum()) for f in FIELDS}
    print(f"{v:26s} vs main: {changed}  agreement: {agreement(x)[2]:.3f} CI "
          f"[{agreement(x)[3]:.3f}, {agreement(x)[4]:.3f}]")
t1a, t1b = other["temperature-1"], other["temperature-1-seed-4009"]
print("temperature 1, seed 4008 vs 4009:", {f: int((t1a[f] != t1b[f]).sum()) for f in FIELDS})

# How wide is the interval with n hand-coded texts? (the worst case, p = 0.5)
for m in [20, 40, 100, 200, 400]:
    print(f"n = {m}: at most ±{1.96 * np.sqrt(0.25 / m):.3f}")

# 1. What the model said, for each star rating
tab = pd.crosstab(d["stars"], d["sentiment"])[["negative", "mixed", "positive"]]
colours = {"negative": RED, "mixed": LIGHT, "positive": GREY}
fig, ax = plt.subplots(figsize=(7.5, 3.2))
left = np.zeros(len(tab))
for s in tab.columns:
    ax.barh(tab.index.astype(str), tab[s], left=left, color=colours[s], edgecolor="white", label=s)
    for y, (l, w) in enumerate(zip(left, tab[s])):
        if w >= 4:
            ax.text(l + w / 2, y, str(w), ha="center", va="center",
                    color="white" if s != "mixed" else "#555555", fontsize=10)
    left += tab[s].to_numpy()
ax.set_xlabel("Reviews (50 per star rating). The model's label: negative, mixed, positive")
ax.set_ylabel("Stars the reviewer gave")
ax.set_xlim(0, 50)
ax.legend(ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0))
save(fig, "sentiment-by-stars")

# 2. Agreement with a 95% interval, for the main run and two alternatives
runs = [("llama3.2:3b, prompt A\n(the main run)", labels),
        ("llama3.2:3b, prompt B", other["prompt-b"]),
        ("llama3.2:1b, prompt A", other["llama3.2-1b"])]
fig, ax = plt.subplots(figsize=(7.5, 2.6))
for i, (name, x) in enumerate(runs):
    _, _, p, lo, hi = agreement(x)
    c = RED if i == 0 else GREY
    ax.plot([100 * lo, 100 * hi], [i, i], color=c, lw=2.5)
    ax.plot(100 * p, i, "o", color=c, ms=8)
    ax.text(100 * hi + 1, i, f"{100 * p:.1f}%", va="center", color=c)
ax.set_yticks(range(len(runs)), [r[0] for r in runs])
ax.invert_yaxis()
ax.set_xlim(60, 100)
ax.set_xlabel("Agreement with the stars, 1–2 and 4–5 stars (%), with 95% interval")
save(fig, "agreement-intervals")

# 3. How many of the 250 labels change between two runs that differ in one thing
pairs = [("Same settings,\nrun again", labels, other["rerun"]),
         ("Temperature 1:\nseed 4008 vs 4009", t1a, t1b),
         ("Prompt A vs\nprompt B", labels, other["prompt-b"]),
         ("llama3.2:3b vs\nllama3.2:1b", labels, other["llama3.2-1b"])]
fig, ax = plt.subplots(figsize=(7.5, 3))
w = 0.26
for j, (f, c) in enumerate(zip(FIELDS, [RED, GREY, LIGHT])):
    vals = [int((a[f] != b[f]).sum()) for _, a, b in pairs]
    ax.bar(np.arange(len(pairs)) + (j - 1) * w, vals, w, color=c, label=f)
ax.set_xticks(range(len(pairs)), [name for name, _, _ in pairs])
ax.text(0, 3, "none", ha="center", color=INK)
ax.set_ylabel("Labels that changed\n(of 250)")
ax.legend(ncol=3, frameon=False, loc="upper left")
save(fig, "what-changes")
