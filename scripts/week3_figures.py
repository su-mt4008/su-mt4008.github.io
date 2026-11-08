# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib"]
# ///
"""Figures and numbers for week 3 (/lectures/week-3).

Run from the repository root:  uv run scripts/week3_figures.py
Writes SVGs to public/img/week-3/ and prints every number the page quotes.
The worked example is Skolverket's year-6 grades per municipality, 2018/19, not HW3's data.
The cleaning below is the same code as on the page.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("public/data/week-3/grades-year6-2018-19.csv")
HW3 = Path("public/data/hw3/stroke-data.csv")
OUT = Path("public/img/week-3")
OUT.mkdir(parents=True, exist_ok=True)

RED, GREY, LIGHT, INK = "#d6453d", "#8a8a8a", "#c8c8c8", "#8a8a8a"
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "svg.hashsalt": "mt4008",
})
jitter = np.random.default_rng(4008)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None}, dpi=200)  # same file every run
    plt.close(fig)


# --- Reading: everything as text, our own column names --------------------------
names = ["municipality", "code", "county", "county_code", "provider", "subject",
         "pupils_total", "pupils_girls", "pupils_boys",
         "pass_total", "pass_girls", "pass_boys",
         "points_total", "points_girls", "points_boys"]
raw = pd.read_csv(DATA, sep=";", skiprows=7, header=None, names=names, usecols=range(15),
                  dtype=str, encoding="utf-8-sig")
print("raw shape:", raw.shape)

is_row = raw["code"].str.fullmatch(r"\d{4}", na=False)
print("rows that are not data (notes at the end):", (~is_row).sum())
print("providers:", raw.loc[is_row, "provider"].value_counts().to_dict())
grades = raw[is_row & (raw["provider"] == "Samtliga")]
print("grades shape:", grades.shape, "municipalities:", grades["code"].nunique(),
      "subjects:", grades["subject"].nunique())

# --- Wide to long ----------------------------------------------------------------
long = grades.melt(id_vars=["municipality", "code", "county", "subject"],
                   value_vars=names[6:], var_name="column", value_name="text")
long[["measure", "sex"]] = long["column"].str.split("_", expand=True)
print("long shape:", long.shape)

# --- Text to numbers -------------------------------------------------------------
codes = ["..", ".", "~100"]
long["note"] = long["text"].where(long["text"].isin(codes))
number = long["text"].mask(long["text"].isin(codes)).str.replace(" ", "").str.replace(",", ".")
long["value"] = pd.to_numeric(number)  # fails loudly on anything unexpected
print("cells with a space in the number:", long["text"].str.contains(" ", regex=False, na=False).sum())
print(pd.crosstab(long["measure"], long["note"].fillna("number")))

# --- Checks ----------------------------------------------------------------------
assert grades["code"].nunique() == 289
assert not grades.duplicated(["code", "subject"]).any()
assert (long["value"].isna() == long["note"].notna()).all()
assert long.loc[long["measure"] == "points", "value"].dropna().between(0, 20).all()
assert long.loc[long["measure"] == "pass", "value"].dropna().between(0, 100).all()

tidy = (long.pivot(index=["municipality", "code", "county", "subject", "sex"],
                   columns="measure", values="value")
        .reset_index())
print("tidy shape:", tidy.shape)

wide = tidy.pivot(index=["municipality", "subject"], columns="sex", values=["pupils", "points"])
wide.columns = [f"{m}_{s}" for m, s in wide.columns]
wide = wide.reset_index()
both = wide.dropna(subset=["pupils_total", "pupils_girls", "pupils_boys"])
assert (both["pupils_total"] == both["pupils_girls"] + both["pupils_boys"]).all()
print("rows where total = girls + boys could be checked:", len(both))
wide["gap"] = wide["points_girls"] - wide["points_boys"]

# Which municipality is missing? Compare with the 290 in week 2's election file.
election = pd.read_csv("public/data/week-2/election-2018-municipalities.csv",
                       sep=";", decimal=",", encoding="utf-8-sig")
print("in the election file but not here:",
      sorted(set(election["KOMMUNNAMN"]) - set(grades["municipality"])))

# --- Missing values: why, and what dropping does -----------------------------------
notes = long.pivot(index=["municipality", "subject", "sex"], columns="measure",
                   values="note").reset_index()
m_pass = tidy.query("subject == 'Matematik' and sex == 'total'").merge(
    notes.query("subject == 'Matematik' and sex == 'total'")[["municipality", "pass"]]
    .rename(columns={"pass": "note"}), on="municipality")
hidden = m_pass[m_pass["note"] == "~100"]
low = 100 * (1 - 4 / hidden["pupils"])
high = 100 * (1 - 1 / hidden["pupils"])
shown = m_pass["pass"].dropna()
print(f"math pass, all pupils: {len(shown)} shown, {len(hidden)} hidden as ~100")
print("hidden municipalities:", hidden.sort_values("pupils")[["municipality", "pupils"]]
      .to_dict("records"))
print(f"median pupils: hidden {hidden['pupils'].median():.0f}, shown "
      f"{m_pass.loc[m_pass['pass'].notna(), 'pupils'].median():.0f}")
print(f"mean pass rate, hidden dropped: {shown.mean():.2f}; with the hidden at their lowest "
      f"possible value: {pd.concat([shown, low]).mean():.2f}; at their highest: "
      f"{pd.concat([shown, high]).mean():.2f}")
small = m_pass["pupils"] < 100
for label, sel in [("under 100 pupils", small), ("100 or more", ~small)]:
    s = m_pass[sel]
    h = s[s["note"] == "~100"]
    print(f"  {label}: {len(s)} municipalities, {len(h)} hidden; mean shown "
          f"{s['pass'].mean():.1f}; with hidden at lowest "
          f"{pd.concat([s['pass'].dropna(), 100 * (1 - 4 / h['pupils'])]).mean():.1f}, at highest "
          f"{pd.concat([s['pass'].dropna(), 100 * (1 - 1 / h['pupils'])]).mean():.1f}")

print("points: municipalities missing a gap per subject:",
      wide.groupby("subject")["gap"].apply(lambda s: int(s.isna().sum())).to_dict())

# --- Subjects: leave out the ones few pupils take -----------------------------------
few = ["Modersmål", "Svenska som andraspråk", "Teckenspråk", "Moderna språk som elevens val",
       "Naturorienterande ämnen", "Samhällsorienterande ämnen"]
pupils_per_subject = tidy.query("sex == 'total'").groupby("subject")["pupils"].sum()
print("pupils per subject:", pupils_per_subject.sort_values().astype(int).to_dict())
gaps = wide[~wide["subject"].isin(few)].dropna(subset=["gap"])
print("subjects kept:", gaps["subject"].nunique())

by_subject = (gaps.groupby("subject")["gap"]
              .agg(n="count", mean="mean", median="median",
                   girls_ahead=lambda g: (g > 0).mean(), boys_ahead=lambda g: (g < 0).mean())
              .sort_values("median"))
print(by_subject.round(2).to_string())

math = gaps[gaps["subject"] == "Matematik"].dropna(subset=["gap"])
print("math gap:", math["gap"].describe().round(2).to_dict())
print(f"math: girls ahead in {(math['gap'] > 0).sum()}, boys in {(math['gap'] < 0).sum()}, "
      f"equal in {(math['gap'] == 0).sum()} of {len(math)}")
print("largest math gaps:", math.nlargest(3, "gap")[
    ["municipality", "pupils_girls", "pupils_boys", "points_girls", "points_boys", "gap"]]
    .to_dict("records"))
print("smallest math gaps:", math.nsmallest(3, "gap")[
    ["municipality", "pupils_girls", "pupils_boys", "gap"]].to_dict("records"))
print("biggest municipalities:", math.nlargest(3, "pupils_total")[
    ["municipality", "pupils_total", "gap"]].to_dict("records"))
math_q = math.assign(size=pd.qcut(math["pupils_total"], 4))
print(math_q.groupby("size", observed=True)["gap"].agg(["count", "mean", "std"]).round(2))
weighted = (np.average(math["points_girls"], weights=math["pupils_girls"])
            - np.average(math["points_boys"], weights=math["pupils_boys"]))
print(f"math gap per pupil (weighted by pupils): {weighted:.2f}; per municipality: "
      f"{math['gap'].mean():.2f}")

# --- How sure: bootstrap and sign-flip test (same code and seed as the page) ----------
gap = math["gap"].to_numpy()
rng = np.random.default_rng(1)
boot = [rng.choice(gap, len(gap)).mean() for _ in range(10_000)]
se = gap.std(ddof=1) / np.sqrt(len(gap))
print(f"math mean gap {gap.mean():.2f}, bootstrap 95% {np.percentile(boot, [2.5, 97.5]).round(2)}, "
      f"formula [{gap.mean() - 1.96 * se:.2f}, {gap.mean() + 1.96 * se:.2f}]")
boot_med = [np.median(rng.choice(gap, len(gap))) for _ in range(10_000)]
print(f"math median gap {np.median(gap):.2f}, bootstrap 95% {np.percentile(boot_med, [2.5, 97.5])}")

rng = np.random.default_rng(1)
signs = rng.choice([-1, 1], size=(10_000, len(gap)))
null_math = (signs * gap).mean(axis=1)
print(f"math sign-flip p = {np.mean(np.abs(null_math) >= abs(gap.mean()))}, "
      f"largest |shuffled mean| {np.abs(null_math).max():.2f}")

eng = gaps.query("subject == 'Engelska'")["gap"].dropna().to_numpy()
rng = np.random.default_rng(1)
signs = rng.choice([-1, 1], size=(10_000, len(eng)))
null_eng = (signs * eng).mean(axis=1)
p_eng = np.mean(np.abs(null_eng) >= abs(eng.mean()))
rng = np.random.default_rng(1)
boot_eng = [rng.choice(eng, len(eng)).mean() for _ in range(10_000)]
print(f"English: mean gap {eng.mean():.2f}, sign-flip p = {p_eng:.3f}, "
      f"bootstrap 95% {np.percentile(boot_eng, [2.5, 97.5]).round(2)}, girls ahead in "
      f"{(eng > 0).sum()}, boys in {(eng < 0).sum()}, equal in {(eng == 0).sum()}")

rng = np.random.default_rng(1)
pvals = {}
for subject, g in gaps.groupby("subject"):
    x = g["gap"].dropna().to_numpy()
    s = rng.choice([-1, 1], size=(10_000, len(x)))
    pvals[subject] = np.mean(np.abs((s * x).mean(axis=1)) >= abs(x.mean()))
print("sign-flip p per subject:", pvals)

# --- Figures -------------------------------------------------------------------------
ENGLISH = {
    "Bild": "Art", "Biologi": "Biology", "Engelska": "English", "Fysik": "Physics",
    "Geografi": "Geography", "Hem- och konsumentkunskap": "Home economics", "Historia": "History",
    "Idrott och hälsa": "Physical education", "Kemi": "Chemistry", "Matematik": "Mathematics",
    "Moderna språk som språkval": "Modern languages", "Musik": "Music",
    "Religionskunskap": "Religion", "Samhällskunskap": "Civics", "Slöjd": "Crafts",
    "Svenska": "Swedish", "Teknik": "Technology",
}

# 1. The gap in every subject: a dot per municipality, the median in red
order = by_subject.index
fig, ax = plt.subplots(figsize=(9, 5.6))
for i, s in enumerate(order):
    x = gaps.loc[gaps["subject"] == s, "gap"].dropna()
    ax.plot(x, i + jitter.uniform(-.2, .2, len(x)), "o", color=GREY, ms=2.6, alpha=.55,
            rasterized=True)  # 4 700 dots: an embedded image keeps the SVG small
    ax.plot(x.median(), i, "|", color=RED, ms=14, mew=2.5)
ax.axvline(0, color=INK, lw=.8)
ax.set_yticks(range(len(order)), [ENGLISH[s] for s in order])
ax.set_xlabel("Girls minus boys, mean grade points.  Grey: a municipality.  Red: the median")
save(fig, "gap-by-subject")

# 2. Outliers and size: the math gap against the number of pupils
fig, ax = plt.subplots(figsize=(7.5, 3.8))
ax.plot(math["pupils_total"], math["gap"], "o", color=GREY, ms=3.5, alpha=.7)
ax.axhline(0, color=INK, lw=.8)
ax.set_xscale("log")
for name, dy in [("Arjeplog", 3), ("Överkalix", -12), ("Orsa", 3), ("Åsele", 3),
                 ("Stockholm", 5), ("Göteborg", 5)]:
    r = math.loc[math["municipality"] == name].iloc[0]
    ax.annotate(name, (r["pupils_total"], r["gap"]), xytext=(5, dy), textcoords="offset points",
                color=RED, fontsize=10)
ax.set_xlabel("Pupils in year 6 with a grade in mathematics (log scale)")
ax.set_ylabel("Girls minus boys\n(grade points)")
save(fig, "math-gap-size")

# 3. Missing not at random: the hidden pass rates are small municipalities with high rates
fig, ax = plt.subplots(figsize=(7.5, 3.8))
s = m_pass[m_pass["pass"].notna()]
ax.plot(s["pupils"], s["pass"], "o", color=GREY, ms=3.5, alpha=.7, label="shown in the file")
ax.vlines(hidden["pupils"], low, high, color=RED, lw=2.5, label="hidden as ~100: the possible range")
ax.set_xscale("log")
ax.set_xlabel("Pupils in year 6 with a grade in mathematics (log scale)")
ax.set_ylabel("Passed (E or better), %")
ax.legend(frameon=False, loc="lower right", fontsize=10)
save(fig, "hidden-pass-rates")

# 4. The sign-flip test: what chance alone gives, for English and for mathematics
fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
for ax, null, obs, title in [(axes[0], null_eng, eng.mean(), "English"),
                             (axes[1], null_math, gap.mean(), "Mathematics")]:
    ax.hist(null, bins=np.arange(-.4, .4, .02), color=LIGHT, edgecolor=GREY, lw=.4)
    ax.set_xlim(-.4, .75)
    ax.axvline(obs, color=RED, lw=2.5)
    right = obs < .4
    ax.annotate(f"observed {obs:.2f}", (obs, ax.get_ylim()[1] * .9), xytext=(5 if right else -5, 0),
                textcoords="offset points", color=RED, fontsize=10, ha="left" if right else "right")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Mean gap with random signs (grade points)")
axes[0].set_ylabel("Shuffles")
save(fig, "sign-flip")

# --- HW3 data: only to check what the assignment says about the file ----------------
stroke = pd.read_csv(HW3)
print("HW3:", stroke.shape, "strokes", int(stroke["stroke"].sum()),
      "bmi missing", int(stroke["bmi"].isna().sum()),
      "smoking", stroke["smoking_status"].value_counts().to_dict(),
      "gender", stroke["gender"].value_counts().to_dict(),
      "age range", stroke["age"].min(), stroke["age"].max())
