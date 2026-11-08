# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib", "lxml"]
# ///
"""Figures and numbers for week 5 (/lectures/week-5).

Run from the repository root:  uv run scripts/week5_figures.py
Reads the cached API responses and web page in public/data/week-5/ (it never calls the web),
writes SVGs to public/img/week-5/ and prints every number the page quotes.

The cached files were downloaded on 2026-11-06 with the fetch code on the week 5 page:
  nobel-physics-laureates-{000,100,200}.json  https://api.nobelprize.org/2.1/laureates
      ?nobelPrizeCategory=phy&limit=100&offset=0,100,200   (CC0)
  wikipedia-municipalities-of-sweden.html      https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden
      revision 1362817780                                  (CC BY-SA 4.0)
  scb-population-2025.csv                      https://statistikdatabasen.scb.se/api/v2/tables/TAB628/data
      ?lang=en&valueCodes[Region]=*&valueCodes[Kon]=1+2&valueCodes[ContentsCode]=BE0101U2
      &valueCodes[Tid]=2025&outputFormat=csv               (CC0)
"""

import io
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path("public/data/week-5")
OUT = Path("public/img/week-5")
OUT.mkdir(parents=True, exist_ok=True)

RED, GREY, LIGHT, INK = "#d6453d", "#8a8a8a", "#c8c8c8", "#8a8a8a"
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "svg.hashsalt": "mt4008",
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None})  # same file every run
    plt.close(fig)


# --- The API responses: one row per laureate and physics prize ----------------------
rows, people, pages = [], 0, sorted(DATA.glob("nobel-physics-laureates-*.json"))
for path in pages:
    page = json.loads(path.read_text(encoding="utf-8"))
    print(path.name, "meta:", {k: page["meta"][k] for k in ["offset", "limit", "count"]},
          "laureates on page:", len(page["laureates"]))
    for person in page["laureates"]:
        people += 1
        for prize in person["nobelPrizes"]:
            if prize["category"]["en"] != "Physics":
                print("  not physics:", person["knownName"]["en"], prize["category"]["en"],
                      prize["awardYear"])
                continue
            rows.append({"id": person["id"], "name": person["knownName"]["en"],
                         "birth": person["birth"]["date"], "year": int(prize["awardYear"])})
prizes = pd.DataFrame(rows)
print("people:", people, " rows (laureate x physics prize):", len(prizes),
      " distinct ids:", prizes["id"].nunique())
print("twice:", prizes.loc[prizes["id"].duplicated(keep=False), ["name", "year"]].to_dict("records"))
print("unknown birth day:", prizes.loc[prizes["birth"].str.endswith("00-00"), ["name", "birth"]]
      .to_dict("records"))
print("award years:", prizes["year"].min(), "to", prizes["year"].max(),
      " distinct years:", prizes["year"].nunique())
try:
    pd.to_datetime(prizes["birth"])
except (ValueError, pd.errors.ParserError) as err:
    print("to_datetime fails:", str(err).splitlines()[0][:100])

prizes["age"] = prizes["year"] - prizes["birth"].str[:4].astype(int)
print("age:", prizes["age"].describe().round(1).to_dict())
print("youngest:", prizes.nsmallest(1, "age")[["name", "year", "age"]].to_dict("records"))
print("oldest:", prizes.nlargest(1, "age")[["name", "year", "age"]].to_dict("records"))

prizes["period"] = pd.cut(prizes["year"], bins=[1900, 1950, 2000, 2026],
                          labels=["1901–1950", "1951–2000", "2001–2026"])
summary = prizes.groupby("period", observed=True)["age"].agg(
    n="size", mean="mean", median="median", sd="std")
summary["se"] = summary["sd"] / np.sqrt(summary["n"])
summary["low"] = summary["mean"] - 1.96 * summary["se"]
summary["high"] = summary["mean"] + 1.96 * summary["se"]
print(summary.round(1).to_string())

a = prizes.loc[prizes["year"] <= 1950, "age"]
b = prizes.loc[prizes["year"] > 2000, "age"]
diff = b.mean() - a.mean()
se = np.sqrt(a.var() / len(a) + b.var() / len(b))
print(f"difference 2001–2026 minus 1901–1950: {diff:.1f} years, "
      f"95% CI {diff - 1.96 * se:.1f} to {diff + 1.96 * se:.1f}")
share70 = prizes.groupby("period", observed=True)["age"].apply(lambda x: (x >= 70).mean())
print("share aged 70 or more:", share70.round(2).to_dict())

# Figure: every laureate, with each period's mean and its 95% interval
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.plot(prizes["year"], prizes["age"], "o", color=GREY, ms=3.5, alpha=.7)
edges = {"1901–1950": (1901, 1950), "1951–2000": (1951, 2000), "2001–2026": (2001, 2026)}
for period, r in summary.iterrows():
    lo, hi = edges[period]
    ax.fill_between([lo, hi], r["low"], r["high"], color=RED, alpha=.18, lw=0)
    ax.plot([lo, hi], [r["mean"], r["mean"]], color=RED, lw=2.5)
    ax.annotate(f"{r['mean']:.0f}", (hi, r["mean"]), xytext=(4, -4), textcoords="offset points",
                color=RED, fontsize=10)
ax.set_xlabel("Year of the Nobel Prize in Physics")
ax.set_ylabel("Age that year")
ax.set_ylim(20, 100)
save(fig, "nobel-age")

# --- The scraped table, and the same numbers from the source's API ------------------
html = (DATA / "wikipedia-municipalities-of-sweden.html").read_text(encoding="utf-8")
print("revision:", html.split('"wgRevisionId":')[1].split(",")[0])
tables = pd.read_html(io.StringIO(html), match="Seat", converters={"Code": str})
municipalities = tables[0]
print("tables matching 'Seat':", len(tables), " shape:", municipalities.shape)
print("columns:", municipalities.columns.tolist())
naive = pd.read_html(io.StringIO(html), match="Seat")[0]
print("naive Code column:", naive["Code"].head(3).tolist(), naive["Code"].dtype)
print("Wikipedia total population:", municipalities["Population"].sum())

scb = (
    pd.read_csv(DATA / "scb-population-2025.csv", dtype={"Region": str})
    .query("Region.str.len() == 4")
    .rename(columns={"Region": "Code", "BE0101U2 2025": "scb"})
)
print("SCB municipalities:", len(scb), " total:", scb["scb"].sum())
both = municipalities.merge(scb, on="Code", validate="one_to_one")
print("joined:", len(both))
print(both.loc[both["Population"] != both["scb"], ["Municipality", "Population", "scb"]]
      .to_string())
matched = naive["Code"].astype(str).isin(scb["Code"]).sum()
print("codes read as numbers that still match SCB's codes:", matched, "of", len(naive))
