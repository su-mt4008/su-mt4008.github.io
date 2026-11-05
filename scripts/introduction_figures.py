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
ax.set_ylabel("Prices vs earnings")
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
ax.set_ylabel("% of headlines")
save(fig, "ai-attention")


# ---------------------------------------------------------------------------------------------
# Life-cycle diagrams: the same steps for every project, as in the cycle diagram; data sources
# branch in at "Data" and merge at "Cleaning"; exploration and analysis loop; being reproducible
# is a band under every step, not a last step. The step where the real work was is red.
STEPS = ["Question", "Data", "Cleaning", "Exploration", "Analysis", "Conclusions"]
W, X0, X1 = 1100, 80, 1020
GAPS = np.array([1, 2.2, 1, 1.15, 1])          # Data -> Cleaning is wider: the sources live there
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
.lc .band{fill:var(--c-tint,#f4f4f4);stroke:var(--c-line,#ddd)}
.lc .bandtext{font-size:13px;fill:var(--c-muted,#777)}
.lc .bandtext tspan.head{font-weight:600;letter-spacing:.06em}
.lc .loop{stroke:var(--c-accent,#d6453d);stroke-width:1.6;fill:none}
.lc .looptip{fill:var(--c-accent,#d6453d)}
.lc text.loopnote{font-size:12px;fill:var(--c-accent,#d6453d)}
</style>"""


def band(x0, x1, y, text):
    """The 'reproducible throughout' band under a diagram."""
    return [f'<rect class="band" x="{x0}" y="{y}" width="{x1 - x0}" height="30" rx="15"/>',
            f'<text class="bandtext" x="{(x0 + x1) / 2}" y="{y + 20}" text-anchor="middle">'
            f'<tspan class="head">REPRODUCIBLE THROUGHOUT</tspan>  ·  {escape(text)}</text>']


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
    track = max(top + 26 + SPREAD * (n - 1) + 10, top + 74)  # the main line; room for the loop above
    offsets = [SPREAD * (i - (n - 1)) for i in range(n)]  # sources fan out above the track
    reproduce = " ".join(notes[6])
    notes = list(notes[:6])
    notes_bottom = track + 36 + 20 * (max(len(x) for x in notes) - 1)
    height = notes_bottom + 60
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
    # Exploration <-> analysis: round again, as often as needed.
    xe, xa = xs[3], xs[4]   # exploration, analysis
    out.append(f'<path class="loop" d="M{xa - 9},{track - 9} C{xa - 30},{track - 46} {xe + 30},{track - 46} {xe + 13},{track - 14}"/>')
    out.append(f'<path class="looptip" d="M{xe + 9},{track - 9} L{xe + 19},{track - 15} L{xe + 12},{track - 21} Z"/>')
    out.append(f'<text class="loopnote" x="{(xe + xa) / 2}" y="{track - 42}" text-anchor="middle">round and round</text>')
    out += band(X0 - 50, X1 + 50, notes_bottom + 20, reproduce)
    out.append("</svg>")
    (OUT / f"lifecycle-{name}.svg").write_text("\n".join(out) + "\n")
    lifecycle_tall(name, title, sources, notes + [[reproduce]], hot)


def lifecycle_tall(name, title, sources, notes, hot):
    """The same diagram running down the page, for the post and narrow screens."""
    n = len(sources)
    TX, NX, LINE = 162, 192, 21           # track x, notes x, line height
    rows, y = [], 24
    for i in range(len(STEPS)):
        text = wrap(" ".join(notes[i]), 44) if (i != 1 or n == 1) else []
        lines = n if (i == 1 and n > 1) else len(text)
        rows.append((y, text))
        y += max(1, lines) * LINE + 22
    height = y + 44
    out = [f'<svg class="lc lc-tall" viewBox="0 0 640 {height}" role="img" xmlns="http://www.w3.org/2000/svg">',
           f"<title>{escape(title)}</title>", STYLE,
           f'<path class="line" d="M{TX},{rows[0][0]} V{rows[-1][0]}"/>']
    yc = rows[2][0]
    for i, ((ry, text), step) in enumerate(zip(rows, STEPS)):
        h = " hot" if i == hot else ""
        out.append(f'<text class="step{h}" x="{TX - 36}" y="{ry + 5}" text-anchor="end">{step}</text>')
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
    ye, ya = rows[3][0], rows[4][0]   # exploration, analysis
    out.append(f'<path class="loop" d="M{TX - 9},{ya} C{TX - 28},{ya - 10} {TX - 28},{ye + 10} {TX - 12},{ye + 4}"/>')
    out.append(f'<path class="looptip" d="M{TX - 8},{ye + 2} L{TX - 18},{ye - 1} L{TX - 15},{ye + 9} Z"/>')
    out.append(f'<text class="loopnote" x="{NX}" y="{rows[5][0] - 16}">↻ exploration and analysis, round and round</text>')
    out += band(20, 620, y - 6, " ".join(notes[6]))
    out.append("</svg>")
    (OUT / f"lifecycle-{name}-tall.svg").write_text("\n".join(out) + "\n")


lifecycle("names", "Life cycle of the baby names project", ["SCB: 200 names by year of birth"], [
    ["Do names come", "back after", "three generations?"],
    [],
    ["reshape the table,", "handle gaps,", "counts → shares"],
    ["share of each", "birth year"],
    ["a comeback", "score"],
    ["yes: Elsa, Alice,", "Astrid … but only", "the living are counted"],
    ["fetch.py +", "report.qmd"],
], hot=5)
lifecycle("electricity", "Life cycle of the electricity price project",
          ["Electricity prices, 4 zones", "SMHI wind, Malmö", "SMHI temperature, Malmö"], [
    ["How big is the", "south–north gap,", "and is it the wind?"],
    [],
    ["one price a day,", "clock changes,", "match to weather"],
    ["prices per zone", "over 3 years"],
    ["calm vs windy", "days: how sure,", "how much weather?"],
    ["0.40 kr/kWh more", "on calm days;", "weather explains 18 %"],
    ["two fetch scripts,", "saved raw data"],
], hot=2)
lifecycle("ai-bubble", "Life cycle of the AI bubble project",
          ["Prices vs earnings, since 1871", "The NASDAQ tech index", "Hacker News headlines"], [
    ["“Bubble” is not", "measurable: turn it", "into three signs"],
    [],
    ["line up months,", "careful dates,", "counts → shares"],
    ["each sign against", "its own history"],
    ["compare with 1929,", "2000 and the", "crypto boom"],
    ["2 of 3 signs are", "there; a crash is", "not in the data"],
    ["one fetch script,", "three sources saved"],
], hot=0)
# ---------------------------------------------------------------------------------------------
# Slide diagrams: boxes, arrows and wheels in the site's colours (inlined, like the life cycles).
FLOW_STYLE = """<style>
.fd text{font-family:var(--font-sans,'IBM Plex Sans',system-ui,sans-serif);fill:var(--c-text,#222);font-size:15px}
.fd .muted{fill:var(--c-muted,#777);font-size:13px}
.fd .lg{font-size:19px;font-weight:600}
.fd .lgm{font-size:15px;fill:var(--c-muted,#777)}
.fd .head{fill:var(--c-muted,#777);font-size:12px;font-weight:600;letter-spacing:.07em}
.fd .big{font-family:'IBM Plex Serif',Georgia,serif;font-size:22px}
.fd text.hot,.fd .hot text{fill:var(--c-accent,#d6453d)}
.fd .box{fill:var(--c-tint,#f4f4f4);stroke:var(--c-line,#ddd);stroke-width:1.5}
.fd .box.hot{stroke:var(--c-accent,#d6453d);stroke-width:2}
.fd .box.solid{fill:var(--c-text,#222);stroke:none}
.fd .solid-text{fill:var(--c-bg,#fff)}
.fd .edge{stroke:var(--c-faint,#bbb);stroke-width:2;fill:none}
.fd .edge.hot{stroke:var(--c-accent,#d6453d)}
.fd .edge.dashed{stroke-dasharray:6 5;stroke:var(--c-muted,#888);stroke-width:1.6}
.fd .tip{fill:var(--c-faint,#bbb)}
.fd .tip.hot{fill:var(--c-accent,#d6453d)}
.fd .node{fill:var(--c-bg,#fff);stroke:var(--c-text,#222);stroke-width:2}
.fd .bar{fill:var(--c-faint,#bbb)}
.fd .bar.hot{fill:var(--c-accent,#d6453d)}
</style>"""


class Diagram:
    """A small SVG builder. Arrowheads are drawn as triangles (no <marker> ids, so several
    diagrams can be inlined into one page without clashing)."""

    def __init__(self, w, h, title):
        self.out = [f'<svg class="fd" viewBox="0 0 {w} {h}" role="img" xmlns="http://www.w3.org/2000/svg">',
                    f"<title>{escape(title)}</title>", FLOW_STYLE]

    def text(self, x, y, s, cls="", anchor="start"):
        c = f' class="{cls}"' if cls else ""
        self.out.append(f'<text{c} x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}">{escape(s)}</text>')

    def box(self, x, y, w, h, lines, cls="", first="", anchor="middle"):
        """lines: list of strings; the first can be styled with `first` (e.g. 'head')."""
        self.out.append(f'<rect class="box {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>')
        tx = x + w / 2 if anchor == "middle" else x + 14
        y0 = y + h / 2 - (len(lines) - 1) * 10 + 5
        for k, line in enumerate(lines):
            c = first if k == 0 and first else ("muted" if k > 0 else "")
            if "solid" in cls:
                c = "solid-text"
            if "hot" in cls and k == 0:
                c = (c + " hot").strip()
            self.text(tx, y0 + 20 * k, line, c, anchor)

    def arrow(self, pts, hot=False, curve=False, dashed=False):
        """An arrow through the points [(x, y), ...]; with curve=True, a smooth S-curve
        between the first and last point."""
        h = (" hot" if hot else "") + (" dashed" if dashed else "")
        (x1, y1), (x2, y2) = pts[0], pts[-1]
        if curve:
            mx = (x1 + x2) / 2
            d = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2 - 9},{y2}"
            ang = 0.0
        else:
            d = "M" + " L".join(f"{x},{y}" for x, y in pts[:-1]) + f" L{x2},{y2}"
            (ax, ay) = pts[-2]
            ang = np.arctan2(y2 - ay, x2 - ax)
            x2, y2 = x2 - 9 * np.cos(ang), y2 - 9 * np.sin(ang)
            d = "M" + " L".join(f"{x},{y}" for x, y in pts[:-1]) + f" L{x2:.1f},{y2:.1f}"
        self.out.append(f'<path class="edge{h}" d="{d}"/>')
        tx, ty = pts[-1]
        a = ang if not curve else 0.0
        p1 = (tx - 11 * np.cos(a) + 6 * np.sin(a), ty - 11 * np.sin(a) - 6 * np.cos(a))
        p2 = (tx - 11 * np.cos(a) - 6 * np.sin(a), ty - 11 * np.sin(a) + 6 * np.cos(a))
        self.out.append(f'<path class="tip{h.replace(" dashed", "")}" d="M{tx:.1f},{ty:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z"/>')

    def curve(self, p0, c1, c2, p1, hot=False):
        h = " hot" if hot else ""
        ang = np.arctan2(p1[1] - c2[1], p1[0] - c2[0])
        ex, ey = p1[0] - 9 * np.cos(ang), p1[1] - 9 * np.sin(ang)
        self.out.append(f'<path class="edge{h}" d="M{p0[0]},{p0[1]} C{c1[0]},{c1[1]} {c2[0]},{c2[1]} {ex:.1f},{ey:.1f}"/>')
        tx, ty, a = p1[0], p1[1], ang
        q1 = (tx - 11 * np.cos(a) + 6 * np.sin(a), ty - 11 * np.sin(a) - 6 * np.cos(a))
        q2 = (tx - 11 * np.cos(a) - 6 * np.sin(a), ty - 11 * np.sin(a) + 6 * np.cos(a))
        self.out.append(f'<path class="tip{h}" d="M{tx:.1f},{ty:.1f} L{q1[0]:.1f},{q1[1]:.1f} L{q2[0]:.1f},{q2[1]:.1f} Z"/>')

    def raw(self, s):
        self.out.append(s)

    def save(self, name):
        self.out.append("</svg>")
        (OUT / f"{name}.svg").write_text("\n".join(self.out) + "\n")


# The cycle, after Wickham, Çetinkaya-Rundel & Grolemund, R for Data Science (2e): our own
# drawing of the idea. Exploration and analysis go round and round; to answer more, you go back
# to fetch more data or refine the question; being reproducible frames it all.
d = Diagram(800, 420, "The data science cycle: question, data, cleaning, then exploration and analysis "
                      "round and round, then conclusions; to answer more, back to the data or the question; "
                      "all of it reproducible")
d.raw('<rect class="box" x="6" y="6" width="788" height="408" rx="14" style="fill:none;stroke-width:2"/>')
cy_ = 200
d.box(20, cy_ - 30, 90, 60, ["Question"], first="lg")
d.box(132, cy_ - 30, 90, 60, ["Data"], first="lg")
d.box(244, cy_ - 30, 100, 60, ["Cleaning"], first="lg")
d.raw('<rect class="box" x="370" y="146" width="284" height="182" rx="12" style="fill:none;stroke-dasharray:5 5"/>')
for x, label in [(386, "Exploration"), (526, "Analysis")]:
    d.box(x, cy_ - 30, 112, 60, [label], first="lg")
d.box(684, cy_ - 30, 98, 60, ["Conclusions"], cls="solid")
d.arrow([(110, cy_), (132, cy_)])
d.arrow([(222, cy_), (244, cy_)])
d.arrow([(344, cy_), (386, cy_)])
d.arrow([(498, cy_), (526, cy_)])
d.arrow([(638, cy_), (684, cy_)])
# round and round: analysis back to exploration
d.curve((582, 230), (582, 282), (442, 282), (442, 234), hot=True)
d.text(512, 312, "round and round", "muted hot", "middle")
# to answer more: back for more data, or a refined question
d.arrow([(442, 170), (442, 112), (177, 112), (177, 170)], dashed=True)
d.text(310, 104, "to answer more: fetch more data", "muted", "middle")
d.arrow([(582, 170), (582, 60), (65, 60), (65, 170)], dashed=True)
d.text(324, 52, "refine the question", "muted", "middle")
d.text(400, 366, "REPRODUCIBLE THROUGHOUT", "head", "middle")
d.text(400, 390, "code, not clicks · relative paths · a lockfile · Quarto · Git", "muted", "middle")
d.save("diagram-cycle")

# Survivorship: who the names table can see.
d = Diagram(1100, 300, "Who is counted: of everyone born in a year, only those alive in Sweden in 2021 with one of the 200 most common names")
rows_ = [(1.0, "Everyone born in Sweden in 1925", "the people the question is about", ""),
         (.42, "… still alive and living in Sweden in 2021", "deaths and emigration remove most", ""),
         (.24, "… with one of today's 200 most common names", "what the SCB table counts", "hot")]
for k, (frac, label, sub, hot) in enumerate(rows_):
    y = 20 + k * 92
    w = 1060 * frac
    d.raw(f'<rect class="bar{" hot" if hot else ""}" x="20" y="{y}" width="{w:.0f}" height="58" rx="4" opacity="{1 if hot else .55}"/>')
    d.text(40 if frac > .3 else 20 + w + 16, y + 26, label, "hot" if hot and frac <= .3 else "", "start")
    d.text(40 if frac > .3 else 20 + w + 16, y + 46, sub, "muted", "start")
d.text(1080, 292, "Illustration, not to scale", "muted", "end")
d.save("diagram-survivors")

# Electricity: the four zones, north to south, mean price 2023–2025.
zone_mean = days[["SE1", "SE2", "SE3", "SE4"]].mean()
print("electricity: mean price per zone 2023-2025:", zone_mean.round(2).to_dict())
d = Diagram(640, 330, "Mean spot price per price zone, 2023–2025, from north to south")
cities = {"SE1": "Luleå", "SE2": "Sundsvall", "SE3": "Stockholm", "SE4": "Malmö"}
scale = 330 / zone_mean.max()
for k, (z, v) in enumerate(zone_mean.items()):
    y = 30 + k * 72
    hot = " hot" if z == "SE4" else ""
    d.text(178, y + 34, f"{z}  {cities[z]}", "lg hot" if hot else "lg", "end")
    d.raw(f'<rect class="bar{hot}" x="192" y="{y + 8}" width="{v * scale:.0f}" height="40" rx="3"/>')
    d.text(192 + v * scale + 10, y + 34, f"{v:.2f} kr", "lg hot" if hot else "lg", "start")
d.arrow([(40, 40), (40, 300)])
d.raw('<text class="muted" x="52" y="44">north</text><text class="muted" x="52" y="300">south</text>')
d.save("diagram-zones")

# Electricity: the cleaning pipeline, with the traps.
n_rows = len(prices)
d = Diagram(1180, 330, "Cleaning: three raw files become one table of days")
d.box(10, 14, 250, 92, ["Electricity prices", "4 zones, every hour", "in world time"], first="")
d.box(10, 128, 250, 72, ["SMHI wind, Malmö", "every hour"])
d.box(10, 222, 250, 72, ["SMHI temperature, Malmö", "daily"])
d.box(320, 14, 300, 92, ["One price per zone and day", "hours and quarter-hours counted fairly", "Swedish days: 23 or 25 hours twice a year"], cls="hot")
d.box(320, 128, 300, 72, ["Daily mean wind"])
d.box(680, 118, 170, 92, ["Side by side", "by date", f"{len(daily):,} days"])
d.box(900, 118, 120, 92, ["Drop", f"{len(daily) - len(days)} days", "no weather"])
d.box(1060, 118, 110, 92, [f"{len(days):,}", "days", "to analyse"], cls="solid")
d.arrow([(260, 60), (320, 60)])
d.arrow([(260, 164), (320, 164)])
d.arrow([(620, 60), (680, 145)], curve=True)
d.arrow([(620, 164), (680, 164)])
d.arrow([(260, 258), (680, 183)], curve=True)
d.arrow([(850, 164), (900, 164)])
d.arrow([(1020, 164), (1060, 164)])
d.save("diagram-cleaning")

# AI: from a vague question to things we can measure.
d = Diagram(1180, 360, "Operationalising: from 'Is AI a bubble?' to three measurable signs")
for x, h in [(10, "THE QUESTION"), (300, "A BUBBLE WOULD MEAN …"), (640, "WE MEASURE"), (980, "SOURCE")]:
    d.text(x, 18, h, "head")
d.box(10, 140, 230, 90, ["Is AI a bubble?", "can't be measured directly"], cls="hot", first="big")
signs = [("Valuations", "prices far above earnings", "prices vs 10 years of earnings", "Shiller, since 1871"),
         ("Price growth", "prices rose unusually fast", "tech index vs 5 years before", "FRED, since 1971"),
         ("Attention", "everyone talks about it", "share of headlines saying “AI”", "Hacker News, since 2007")]
for k, (sign, mean, measure, source) in enumerate(signs):
    y = 40 + k * 110
    d.box(300, y, 280, 76, [sign, mean], first="lg")
    d.box(640, y, 300, 76, [measure])
    d.text(980, y + 43, source, "muted")
    d.arrow([(240, 185), (300, y + 38)], curve=True, hot=True)
    d.arrow([(580, y + 38), (640, y + 38)])
d.save("diagram-operationalise")

# How you hand in, with the loop when the check is red.
d = Diagram(1180, 250, "Handing in: branch, work, pull request, the check, review, final version")
steps_ = [("Branch", "hw1 from main"), ("Work", "report.qmd, commit"), ("Pull request", "HW1 · Mon 23:59"),
          ("The check", "renders on a clean PC"), ("Peer review", "by Thu 23:59"), ("Final version", "Fri 23:59 · graded")]
bw, gap = 162, 38
for k, (a, b) in enumerate(steps_):
    x = 10 + k * (bw + gap)
    d.box(x, 50, bw, 86, [a, b], cls="hot" if k == 3 else ("solid" if k == 5 else ""))
    if k:
        d.arrow([(x - gap, 93), (x, 93)])
xc = 10 + 3 * (bw + gap) + bw / 2
xw = 10 + 1 * (bw + gap) + bw / 2
d.arrow([(xc, 136), (xc, 210), (xw, 210), (xw, 136)], hot=True)
d.text((xc + xw) / 2, 236, "red: read the log, fix, push again (as often as you need)", "hot", "middle")
d.text(10 + 3 * (bw + gap) + bw + gap / 2, 82, "green", "muted", "middle")
d.save("diagram-handin")

# Week 1: the Git workflow, as a branch graph.
d = Diagram(1180, 450, "The Git workflow: branch hw1 off main, commit small steps, push and open a pull request, "
                       "the check and review, push fixes, merged into main when accepted; meanwhile hw2 is "
                       "branched off main and worked on in parallel")
ym, yb = 260, 140
node = lambda x, y, hot=False: d.raw(f'<circle class="node" cx="{x}" cy="{y}" r="11"'
                                     + (' style="stroke:var(--c-accent,#d6453d);fill:var(--c-accent,#d6453d)"' if hot else "") + "/>")
d.raw(f'<path class="edge" d="M90,{ym} L1160,{ym}" style="stroke:var(--c-text,#222)"/>')
d.raw(f'<path class="edge" d="M220,{yb} L500,{yb} M700,{yb} L960,{yb}"/>')
d.curve((120, ym), (170, ym), (170, yb), (209, yb))
d.curve((960, yb), (1030, yb), (1030, ym), (1069, ym), hot=True)
d.text(20, ym + 6, "main", "lg")
d.text(20, yb + 6, "hw1", "lg")
d.box(500, yb - 40, 200, 80, ["Pull request", "“HW1”: your hand-in"], cls="hot")
d.arrow([(420, yb), (500, yb)])
d.text(460, yb - 12, "push", "muted", "middle")
for x, label in [(220, "read data"), (320, "plot"), (420, "write up")]:
    node(x, yb)
    d.text(x, yb + 36, label, "muted", "middle")
node(840, yb)
d.text(840, yb + 36, "fixes", "muted", "middle")
d.text(770, yb - 14, "check ✓", "muted", "middle")
node(120, ym)
node(1080, ym, hot=True)
d.text(1080, ym + 38, "merged when accepted", "muted", "middle")
d.text(120, ym + 38, "the accepted version", "muted", "middle")
for x, h in [(170, "1 BRANCH"), (320, "2 COMMIT"), (600, "3 PUSH, OPEN A PR"), (840, "4 CHECK, REVIEW, FIX"), (1080, "5 MERGE")]:
    d.text(x, 40, h, "head", "middle")
# hw2, in parallel: branched off main while hw1 is still in review; its own pull request.
y2 = 380
d.text(20, y2 + 6, "hw2", "lg")
d.text(90, y2 + 6, "starts from main while hw1 is still in review", "muted")
d.curve((560, ym), (610, ym), (610, y2), (649, y2))
d.raw(f'<path class="edge" d="M660,{y2} L860,{y2} M1060,{y2} L1160,{y2}"/>')
for x, label in [(660, "read data"), (760, "plot")]:
    node(x, y2)
    d.text(x, y2 + 36, label, "muted", "middle")
d.arrow([(760, y2), (860, y2)])
d.text(810, y2 - 12, "push", "muted", "middle")
d.box(860, y2 - 36, 200, 72, ["Pull request", "“HW2”: in review"])
d.save("diagram-git")

# ---------------------------------------------------------------------------------------------
# Workflow flowcharts: one per project, read left to right. Question -> the data sources (one box
# each) -> cleaning -> exploration and analysis (round and round) -> conclusions, with the file that
# does each part and the one command that reruns it all. The step where the work was is red.
FC_STYLE = """<style>
.fd .ttl{font-size:16px;font-weight:600}
.fd .det{font-size:13.5px;fill:var(--c-muted,#777)}
.fd text.ttl.hot,.fd text.colhead.hot,.fd text.worknote{fill:var(--c-accent,#d6453d)}
.fd .colhead{fill:var(--c-muted,#777);font-size:12px;font-weight:600;letter-spacing:.07em}
.fd .worknote{font-size:13px;font-weight:600}
.fd .file{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12.5px;fill:var(--c-muted,#777)}
</style>"""
FC_COLS = [(0, 184), (230, 214), (490, 200), (736, 200), (982, 178)]   # (x, width) per column
FC_W, FC_TOP = 1160, 72


def fc_lines(title, details, w):
    """The title's lines, and the detail lines as (text, gap before it): a small gap between items."""
    ds = [(line, 6 if k == 0 and i else 0) for i, d_ in enumerate(details)
          for k, line in enumerate(wrap(d_, int((w - 26) / 7.0)))]
    return wrap(title, int((w - 26) / 8.6)), ds


def fc_height(title, details, w):
    t, ds = fc_lines(title, details, w)
    return 16 + 20 * len(t) + 6 + sum(18 + g for _, g in ds) + 10


def fc_box(d, x, y, w, title, details, hot=False):
    t, ds = fc_lines(title, details, w)
    h = fc_height(title, details, w)
    d.raw(f'<rect class="box{" hot" if hot else ""}" x="{x}" y="{y:.0f}" width="{w}" height="{h}" rx="7"/>')
    for k, line in enumerate(t):
        d.text(x + 13, y + 30 + 20 * k, line, "ttl hot" if hot else "ttl")
    yl = y + 30 + 20 * len(t) + 6
    for line, g in ds:
        yl += g
        d.text(x + 13, yl, line, "det")
        yl += 18
    return h


def flowchart(name, title, question, sources, cleaning, exploration, analysis, conclusions, hot, files):
    """Writes flow-<name>.svg. question/cleaning/exploration/analysis/conclusions: (title, [details]);
    sources: [(name, [details])]; hot: 'question' | 'data' | 'cleaning' | 'analysis' | 'conclusions';
    files: (fetch script, report) shown under the columns they belong to."""
    GAP_S, GAP_EA = 14, 50
    hs = [fc_height(s, ds, FC_COLS[1][1]) for s, ds in sources]
    stack = sum(hs) + GAP_S * (len(hs) - 1)
    he, ha = fc_height(*exploration, FC_COLS[3][1]), fc_height(*analysis, FC_COLS[3][1])
    tall = max(stack, he + GAP_EA + ha, *(fc_height(*b, FC_COLS[i][1]) for i, b in
                                           [(0, question), (2, cleaning), (4, conclusions)]))
    cy = FC_TOP + tall / 2
    bottom = FC_TOP + tall
    height = bottom + 84
    d = Diagram(FC_W, height, title)
    d.raw(FC_STYLE)
    heads = ["1 · QUESTION", "2 · DATA", "3 · CLEANING", "4 · EXPLORATION ⇄ ANALYSIS", "5 · CONCLUSIONS"]
    keys = ["question", "data", "cleaning", "analysis", "conclusions"]
    for (x, w), head, key in zip(FC_COLS, heads, keys):
        d.text(x, 30, head, "colhead hot" if key == hot else "colhead")

    def single(col, box):          # one box, centred on the flow line; returns (top, height)
        x, w = FC_COLS[col]
        h = fc_height(*box, w)
        fc_box(d, x, cy - h / 2, w, *box, hot=keys[col] == hot)
        return cy - h / 2, h

    single(0, question)
    single(2, cleaning)
    single(4, conclusions)
    # Data: one box per source; arrows fan out from the question and merge at cleaning.
    (xq, wq), (xd, wd), (xc, _) = FC_COLS[0], FC_COLS[1], FC_COLS[2]
    y = cy - stack / 2
    for (s, ds), h in zip(sources, hs):
        fc_box(d, xd, y, wd, s, ds, hot=hot == "data")
        ym = y + h / 2
        d.arrow([(xq + wq, cy), (xd, ym)], curve=abs(ym - cy) > 1)
        d.arrow([(xd + wd, ym), (xc, cy)], curve=abs(ym - cy) > 1)
        y += h + GAP_S
    # Exploration above analysis, round and round between them.
    xe, we = FC_COLS[3]
    ye = cy - (he + GAP_EA + ha) / 2
    ya = ye + he + GAP_EA
    fc_box(d, xe, ye, we, *exploration)
    fc_box(d, xe, ya, we, *analysis, hot=hot == "analysis")
    d.arrow([(xc + FC_COLS[2][1], cy), (xe, ye + he / 2)], curve=True)
    d.arrow([(xe + we, ya + ha / 2), (FC_COLS[4][0], cy)], curve=True)
    d.arrow([(xe + 34, ye + he), (xe + 34, ya)], hot=True)
    d.arrow([(xe + we - 34, ya), (xe + we - 34, ye + he)], hot=True)
    d.text(xe + we / 2, ye + he + GAP_EA / 2 + 5, "round and round", "muted hot", "middle")
    # Where the work was: under the red column's heading.
    x, _ = FC_COLS[keys.index(hot)]
    d.text(x, 48, "where the work was", "worknote")
    # The files that do each part, and the one command that reruns everything.
    fetch, report = files
    d.text(xd + wd / 2, bottom + 24, f"{fetch} → data/", "file", "middle")
    d.text((xc + FC_COLS[4][0] + FC_COLS[4][1]) / 2, bottom + 24,
           f"{report} → report.md  (cleaning, analysis, figures, text)", "file", "middle")
    yb = bottom + 40
    d.raw(f'<rect class="box" x="0" y="{yb:.0f}" width="{FC_W}" height="40" rx="8"/>')
    d.text(16, yb + 25, "REPRODUCIBLE THROUGHOUT", "colhead")
    d.text(236, yb + 25, "one command reruns it all:", "det")
    d.text(410, yb + 25, "uv run quarto render", "file")
    d.save(f"flow-{name}")


flowchart("names", "Workflow of the baby names project: one SCB table, cleaned into shares, a comeback score, "
                   "and a conclusion with its limitation",
          ("Are baby names a fashion?", ["Do names come back after three generations?"]),
          [("Statistics Sweden (SCB)", ["the 200 most common names,", "by year of birth 1922–2021"])],
          ("A tidy table", ["reshape to one row per name and year", "handle SCB's hidden small counts",
                            "counts → shares of each year"]),
          ("Each name over 100 years", ["plot the share per birth year"]),
          ("A comeback score", ["common in 1922–35, rare in 1960–80, common again in 2005–21"]),
          ("Yes, with a catch", ["Ella, Elsa, Alice, Astrid top the score",
                                 "limitation: only people alive in 2021 are counted"]),
          hot="conclusions", files=("fetch.py", "report.qmd"))
flowchart("electricity", "Workflow of the electricity price project: prices and weather from two sources, "
                         "cleaned to one row per day, calm and windy days compared",
          ("Why does electricity cost more in Malmö than in Luleå?", ["Is it the wind?"]),
          [("Spot prices", ["4 zones, 2023–2025, every hour (15 min from Oct 2025)"]), ("SMHI wind", ["Malmö, every day"]),
           ("SMHI temperature", ["Malmö, every day"])],
          ("One row per day", ["hourly and 15-minute prices → one per day", "clock changes: 23- and 25-hour days",
                               "match prices to weather: 1,074 days"]),
          ("The gap over time", ["Malmö minus Luleå, month by month"]),
          ("Calm vs windy days", ["how big is the difference?", "how sure are we?"]),
          ("Partly", ["0.40 kr/kWh more on calm days", "but weather explains only 18 %"]),
          hot="cleaning", files=("fetch_prices.py + fetch_weather.py", "report.qmd"))
flowchart("ai-bubble", "Workflow of the AI bubble project: a vague question turned into three measurable signs, "
                       "three sources lined up by month, today compared with past bubbles",
          ("Is AI a bubble?", ["can't be measured directly", "so: three signs we can measure",
                               "valuations, price growth, attention"]),
          [("Robert Shiller", ["prices vs earnings, since 1871"]), ("FRED", ["the NASDAQ index, since 1971"]),
           ("Hacker News", ["4.8 million headlines"])],
          ("Months, comparable", ["line up the sources by month", "Shiller writes October as .1",
                                  "counts → shares of headlines"]),
          ("Each sign over time", ["today against its own history"]),
          ("How unusual is today?", ["compare with 1929, 2000 and the crypto boom"]),
          ("Two of three signs", ["valuations and attention: yes", "price growth: no",
                                  "a crash is not in the data"]),
          hot="question", files=("fetch.py", "report.qmd"))

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
