# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib", "xlrd"]
# ///
"""Figures and life-cycle diagrams for the introduction lecture (slides and /lectures/introduction).

Reads the saved data of the three example projects in su-mt4008/lecture-demos/introduction:

    uv run scripts/introduction_figures.py ../lecture-demos/introduction

Writes SVGs to public/img/introduction/ and prints every number the slides and the post quote.
Charts use transparent backgrounds, grey ink and one red accent, so they read in light and dark
mode. The life-cycle diagrams use the site's colour tokens and are inlined into the pages.
"""

import logging
import sys
from html import escape
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "../lecture-demos/introduction")
OUT = Path("public/img/introduction")
OUT.mkdir(parents=True, exist_ok=True)

RED, GREY, LIGHT, INK = "#d6453d", "#8a8a8a", "#c8c8c8", "#8a8a8a"
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "svg.hashsalt": "mt4008", "font.family": ["IBM Plex Sans", "Helvetica", "Arial", "DejaVu Sans", "sans-serif"],
})
# The SVGs name IBM Plex Sans; matplotlib needn't have it installed to write them.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
rng = np.random.default_rng(4008)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None})  # same file every run
    plt.close(fig)


# ---------------------------------------------------------------------------------------------
# 1. Baby names
raw = pd.read_csv(SRC / "names/data/scb-names-by-birth-year.csv", encoding="latin-1")
raw = raw.rename(columns={raw.columns[0]: "name"})
names = raw.melt(id_vars="name", var_name="year", value_name="people")
names["year"] = names["year"].str[-4:].astype(int)
names["people"] = pd.to_numeric(names["people"], errors="coerce")
names["share"] = names["people"] / names.groupby("year")["people"].transform("sum")
share = names.pivot(index="year", columns="name", values="share").fillna(0)
print("names:", share.shape[1], "names,", share.index.min(), "-", share.index.max(),
      "| suppressed name-years:", int(names["people"].isna().sum()))

fig, axes = plt.subplots(1, 3, figsize=(10, 3), sharey=True)
for ax, name in zip(axes, ["Elsa", "Alice", "Astrid"]):
    ax.axvspan(1960, 1980, color=GREY, alpha=.15, lw=0)
    ax.plot(share.index, share[name] * 100, color=RED, lw=2)
    ax.set_title(name, loc="left", color=INK)
    ax.set_xticks([1925, 1970, 2015])
axes[0].set_ylabel("% of the birth year")
axes[1].text(1970, axes[1].get_ylim()[1] * .92, "1960–80", ha="center", color=GREY, fontsize=10)
save(fig, "names-comebacks")

top10 = share.apply(lambda year: year.nlargest(10).sum(), axis=1)
print(f"names: top-10 share {top10.loc[1922]:.0%} in 1922, {top10.loc[2021]:.0%} in 2021")
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(top10.index, top10 * 100, color=GREY, lw=2)
ax.set_ylabel("% in the top 10")
save(fig, "names-diversity")

# ---------------------------------------------------------------------------------------------
# 2. Electricity
prices = pd.read_csv(SRC / "electricity/data/prices.csv")
prices["start"] = pd.to_datetime(prices["start"], utc=True)
prices["minutes"] = (pd.to_datetime(prices["end"], utc=True) - prices["start"]).dt.total_seconds() / 60
prices["date"] = prices["start"].dt.tz_convert("Europe/Stockholm").dt.tz_localize(None).dt.normalize()
prices["weighted"] = prices["sek_per_kwh"] * prices["minutes"]
g = prices.groupby(["date", "zone"])
daily = (g["weighted"].sum() / g["minutes"].sum()).unstack()


def read_smhi(path):
    with open(path, encoding="utf-8-sig") as f:
        header = next(i for i, line in enumerate(f) if line.startswith(("Datum", "Från Datum")))
    return pd.read_csv(path, sep=";", skiprows=header, usecols=range(4 if "wind" in path.name else 5))


wind = read_smhi(SRC / "electricity/data/smhi-malmo-wind-corrected-archive.csv")
wind["date"] = pd.to_datetime(wind["Datum"])
temp = read_smhi(SRC / "electricity/data/smhi-malmo-temperature-corrected-archive.csv")
temp["date"] = pd.to_datetime(temp["Representativt dygn"])
days = (daily.join(wind.groupby("date")["Vindhastighet"].mean().rename("wind"))
        .join(temp.set_index("date")["Lufttemperatur"].rename("temp")).dropna())
days["gap"] = days["SE4"] - days["SE1"]
print(f"electricity: {len(daily)} days, {len(daily) - len(days)} without weather; "
      f"mean gap {days['gap'].mean():.2f}; SE1 {days['SE1'].mean():.2f}, SE4 {days['SE4'].mean():.2f}")

monthly = days[["SE1", "SE4"]].resample("MS").mean()
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.fill_between(monthly.index, monthly["SE1"], monthly["SE4"], color=RED, alpha=.15, lw=0)
ax.plot(monthly.index, monthly["SE4"], color=RED, lw=2)
ax.plot(monthly.index, monthly["SE1"], color=GREY, lw=2)
ax.text(monthly.index[-1], monthly["SE4"].iloc[-1], "  SE4 Malmö", color=RED, va="center")
ax.text(monthly.index[-1], monthly["SE1"].iloc[-1], "  SE1 Luleå", color=GREY, va="center")
ax.set_ylabel("SEK per kWh")
save(fig, "electricity-zones")

days["group"] = pd.qcut(days["wind"], 4, labels=["calmest", "", " ", "windiest"])
means = days.groupby("group", observed=True)["gap"].mean()
calm = days.loc[days["group"] == "calmest", "gap"].to_numpy()
windy = days.loc[days["group"] == "windiest", "gap"].to_numpy()
boot = [rng.choice(calm, calm.size).mean() - rng.choice(windy, windy.size).mean() for _ in range(10_000)]
lo, hi = np.percentile(boot, [2.5, 97.5])
X = np.column_stack([np.ones(len(days)), days["wind"], days["temp"]])
coef, *_ = np.linalg.lstsq(X, days["gap"], rcond=None)
r2 = 1 - (days["gap"] - X @ coef).var() / days["gap"].var()
print(f"electricity: gap by wind quarter {means.round(2).tolist()}; calm-windy "
      f"{calm.mean() - windy.mean():.2f} (95% {lo:.2f} to {hi:.2f}); R2 {r2:.0%}")
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.bar(range(4), means.to_numpy(), color=[RED, LIGHT, LIGHT, GREY], width=.6)
for i, v in enumerate(means):
    ax.text(i, v + .01, f"{v:.2f}", ha="center", va="bottom")
ax.set_xticks(range(4), ["calmest quarter", "", "", "windiest quarter"])
ax.set_xlabel("Days grouped by mean wind speed in Malmö")
ax.set_ylabel("Malmö minus Luleå\n(SEK per kWh)")
save(fig, "electricity-wind")

# ---------------------------------------------------------------------------------------------
# 3. AI bubble
sh = pd.read_excel(SRC / "ai-bubble/data/shiller-ie_data.xls", sheet_name="Data", header=None, skiprows=8)
sh = sh[pd.to_numeric(sh[0], errors="coerce").notna()]
cape = pd.Series(pd.to_numeric(sh[12], errors="coerce").to_numpy(),
                 index=pd.to_datetime(sh[0].map(lambda x: f"{x:.2f}"), format="%Y.%m")).dropna()
marks = {"1929": cape.loc["1929"].max(), "2000": cape.loc["1999":"2000"].max(), "today": cape.iloc[-1]}
print("ai: CAPE " + ", ".join(f"{k} {v:.1f}" for k, v in marks.items()),
      f"| last month {cape.index[-1]:%Y-%m} | higher than {(cape < cape.iloc[-1]).mean():.0%} of months")
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.plot(cape.index, cape, color=GREY, lw=1)
for label, when in [("1929", cape.loc["1929"].idxmax()), ("2000", cape.loc["1999":"2000"].idxmax()),
                    ("today", cape.index[-1])]:
    ax.plot(when, cape[when], "o", color=RED, ms=6)
    ax.annotate(f"{label}: {cape[when]:.0f}", (when, cape[when]), xytext=(0, 8),
                textcoords="offset points", ha="center", color=RED)
ax.set_ylabel("Price / earnings (CAPE)")
save(fig, "ai-cape")

nq = pd.read_csv(SRC / "ai-bubble/data/fred-nasdaqcom.csv")
nq = pd.Series(pd.to_numeric(nq["NASDAQCOM"], errors="coerce").to_numpy(),
               index=pd.to_datetime(nq["observation_date"])).dropna()
nq = nq.loc[:"2026-10-31"].resample("ME").last()   # complete months only, like the other sources
growth5 = (nq / nq.shift(60)).dropna()
print(f"ai: NASDAQ vs 5 years earlier: peak {growth5.max():.1f}x ({growth5.idxmax():%b %Y}), "
      f"today {growth5.iloc[-1]:.1f}x ({growth5.index[-1]:%b %Y})")
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.plot(growth5.index, growth5, color=GREY, lw=1.5)
ax.axhline(1, color=LIGHT, lw=1)
for when, label, offset in [(growth5.idxmax(), "2000", (0, 8)), (growth5.index[-1], "today", (0, -22))]:
    ax.plot(when, growth5[when], "o", color=RED, ms=6)
    ax.annotate(f"{label}: ×{growth5[when]:.1f}", (when, growth5[when]), xytext=offset,
                textcoords="offset points", ha="center" if label == "2000" else "right", color=RED)
ax.set_ylabel("NASDAQ / 5 years earlier")
save(fig, "ai-nasdaq")

hn = pd.read_csv(SRC / "ai-bubble/data/hn-title-mentions.csv", parse_dates=["month"]).set_index("month")
shares = hn[["AI", "bitcoin", "crypto", "blockchain"]].div(hn["all_stories"], axis=0) * 100
smooth = shares.rolling(3, center=True).mean()
print(f"ai: HN AI share today {shares['AI'].iloc[-1]:.1f}% (record {shares['AI'].max():.1f}%), "
      f"bitcoin record {shares['bitcoin'].max():.1f}%, crypto record {shares['crypto'].max():.1f}%")
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.plot(smooth.index, smooth["bitcoin"], color=LIGHT, lw=2)
ax.plot(smooth.index, smooth["crypto"], color=GREY, lw=2)
ax.plot(smooth.index, smooth["AI"], color=RED, lw=2.5)
for col, color in [("AI", RED), ("crypto", GREY), ("bitcoin", LIGHT)]:
    when = smooth[col].idxmax()
    ax.annotate(col if col != "AI" else '"AI"', (when, smooth[col].max()), xytext=(0, 6),
                textcoords="offset points", color=color, ha="center" if col != "crypto" else "left")
ax.set_ylabel("% of story titles")
save(fig, "ai-attention")


# ---------------------------------------------------------------------------------------------
# Life-cycle diagrams: the same seven steps for every project; data sources branch in at
# "Data" and merge at "Cleaning"; the step where the real work was is marked in red.
STEPS = ["Question", "Data", "Cleaning", "Exploration", "Analysis", "Conclusions", "Reproduce"]
W, X0, X1 = 1100, 70, 1030
GAPS = np.array([1, 2.2, 1, 1, 1, 1])          # Data -> Cleaning is wider: the sources live there
xs = X0 + np.concatenate([[0], np.cumsum(GAPS)]) * (X1 - X0) / GAPS.sum()
SPREAD = 30                                     # vertical distance between source lines

STYLE = """<style>
.lc text{font-family:var(--font-sans,'IBM Plex Sans',system-ui,sans-serif);fill:var(--c-text,#222)}
.lc .step{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;fill:var(--c-muted,#777)}
.lc .note{font-size:14px}
.lc .src{font-size:13px;fill:var(--c-muted,#777)}
.lc text.hot{fill:var(--c-accent,#d6453d)}
.lc .line{stroke:var(--c-faint,#bbb);stroke-width:2;fill:none}
.lc .node{fill:var(--c-bg,#fff);stroke:var(--c-text,#222);stroke-width:2}
.lc .node.hot{fill:var(--c-accent,#d6453d);stroke:var(--c-accent,#d6453d)}
.lc .dot{fill:var(--c-text,#222)}
</style>"""


def wrap(text, width=18):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def lifecycle(name, title, sources, notes, hot):
    """Writes lifecycle-<name>.svg. sources: data source labels; notes: lines under each step
    (none under Data, whose sources are drawn instead); hot: index of the step that took the work."""
    n = len(sources)
    top = 30
    track = top + 26 + SPREAD * (n - 1) + 10          # the main line
    offsets = [SPREAD * (i - (n - 1)) for i in range(n)]  # sources fan out above the track
    height = track + 36 + 20 * max(len(x) for x in notes)
    xd, xc = xs[1], xs[2]
    gap = xc - xd
    out = [f'<svg class="lc" viewBox="0 0 {W} {height}" role="img" xmlns="http://www.w3.org/2000/svg">',
           f"<title>{escape(title)}</title>", STYLE,
           f'<path class="line" d="M{X0},{track} H{X1}"/>']
    if n == 1:  # one source: an ordinary step, with the source written under it
        notes = [notes[0], wrap(sources[0])] + list(notes[2:])
    for off, label in zip(offsets, sources if n > 1 else []):
        y = track + off
        if off:
            out.append(f'<path class="line" d="M{xd},{y} H{xd + .45 * gap} '
                       f'C{xd + .75 * gap},{y} {xc - .2 * gap},{track} {xc},{track}"/>')
        out.append(f'<circle class="dot" cx="{xd}" cy="{y}" r="4"/>')
        out.append(f'<text class="src" x="{xd + 12}" y="{y - 8}">{escape(label)}</text>')
    for i, (x, step) in enumerate(zip(xs, STEPS)):
        h = " hot" if i == hot else ""
        out.append(f'<text class="step{h}" x="{x}" y="{top}" text-anchor="{"start" if i == 1 and n > 1 else "middle"}"'
                   f'{f' dx="-8"' if i == 1 and n > 1 else ""}>{step}</text>')
        if i != 1 or n == 1:
            out.append(f'<circle class="node{h}" cx="{x}" cy="{track}" r="7"/>')
        for k, line in enumerate(notes[i]):
            out.append(f'<text class="note{h}" x="{x}" y="{track + 36 + 20 * k}" text-anchor="middle">{escape(line)}</text>')
    out.append("</svg>")
    (OUT / f"lifecycle-{name}.svg").write_text("\n".join(out) + "\n")
    lifecycle_tall(name, title, sources, notes, hot)


def lifecycle_tall(name, title, sources, notes, hot):
    """The same diagram running down the page, for the post and narrow screens."""
    n = len(sources)
    TX, NX, LINE = 150, 182, 21           # track x, notes x, line height
    rows, y = [], 24
    for i in range(len(STEPS)):
        text = wrap(" ".join(notes[i]), 44) if (i != 1 or n == 1) else []
        lines = n if (i == 1 and n > 1) else len(text)
        rows.append((y, text))
        y += max(1, lines) * LINE + 22
    height = y
    out = [f'<svg class="lc lc-tall" viewBox="0 0 640 {height}" role="img" xmlns="http://www.w3.org/2000/svg">',
           f"<title>{escape(title)}</title>", STYLE,
           f'<path class="line" d="M{TX},{rows[0][0]} V{rows[-1][0]}"/>']
    yc = rows[2][0]
    for i, ((ry, text), step) in enumerate(zip(rows, STEPS)):
        h = " hot" if i == hot else ""
        out.append(f'<text class="step{h}" x="{TX - 22}" y="{ry + 5}" text-anchor="end">{step}</text>')
        if i == 1 and n > 1:
            for k, label in enumerate(sources):
                ys = ry + k * LINE
                out.append(f'<path class="line" d="M{NX - 8},{ys} C{NX - 8},{yc - 30} {TX},{yc - 40} {TX},{yc}"/>')
                out.append(f'<circle class="dot" cx="{NX - 8}" cy="{ys}" r="4"/>')
                out.append(f'<text class="src" x="{NX + 4}" y="{ys + 5}">{escape(label)}</text>')
            continue
        out.append(f'<circle class="node{h}" cx="{TX}" cy="{ry}" r="7"/>')
        for k, line in enumerate(text):
            out.append(f'<text class="note{h}" x="{NX}" y="{ry + 5 + LINE * k}">{escape(line)}</text>')
    out.append("</svg>")
    (OUT / f"lifecycle-{name}-tall.svg").write_text("\n".join(out) + "\n")


lifecycle("names", "Life cycle of the baby names project", ["SCB: 200 names by year of birth"], [
    ["Do names come", "back after", "three generations?"],
    [],
    ["wide → long", "'..' means fewer", "than ten people"],
    ["share of each", "birth year"],
    ["a comeback", "score"],
    ["yes: Elsa, Alice,", "Astrid … but only", "the living are counted"],
    ["fetch.py +", "report.qmd"],
], hot=5)
lifecycle("electricity", "Life cycle of the electricity price project",
          ["Spot prices, 4 zones (API)", "SMHI wind, Malmö", "SMHI temperature, Malmö"], [
    ["How big is the", "south–north gap,", "and is it the wind?"],
    [],
    ["15-min vs hourly,", "clock changes,", "join on the date"],
    ["prices per zone", "over 3 years"],
    ["calm vs windy days,", "bootstrap,", "straight-line fit"],
    ["0.40 kr/kWh more", "on calm days;", "weather explains 18 %"],
    ["two fetch scripts,", "saved raw data"],
], hot=2)
lifecycle("ai-bubble", "Life cycle of the AI bubble project",
          ["Shiller: valuations since 1871", "FRED: the NASDAQ index", "Hacker News titles (API)"], [
    ["“Bubble” is not", "measurable: turn it", "into three signs"],
    [],
    ["dates like 2026.1", "mean October;", "counts → shares"],
    ["each sign against", "its own history"],
    ["compare with 1929,", "2000 and the", "crypto boom"],
    ["2 of 3 signs are", "there; a crash is", "not in the data"],
    ["one fetch script,", "three sources saved"],
], hot=0)
print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
