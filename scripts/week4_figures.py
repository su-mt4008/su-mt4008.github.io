# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "pandas", "matplotlib"]
# ///
"""Figures, database and numbers for week 4 (/lectures/week-4).

Run from the repository root:  uv run scripts/week4_figures.py
Writes SVGs to public/img/week-4/, builds public/data/week-4/municipalities-2018.sqlite,
and prints every number the page quotes.
The worked example is Swedish municipalities in 2018 (election, income, education), not HW4's data.
"""

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ELECTION = Path("public/data/week-2/election-2018-municipalities.csv")
INCOME = Path("public/data/week-4/scb-median-income-2018.csv")
EDUCATION = Path("public/data/week-4/scb-education-2018.csv")
DB = Path("public/data/week-4/municipalities-2018.sqlite")
OUT = Path("public/img/week-4")
OUT.mkdir(parents=True, exist_ok=True)

RED, GREY, LIGHT, INK = "#d6453d", "#8a8a8a", "#c8c8c8", "#8a8a8a"
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "svg.hashsalt": "mt4008",
})


def save(fig, name, tight=True):
    if tight:
        fig.tight_layout()
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None})  # same file every run
    plt.close(fig)


# --- Read the three tables ---------------------------------------------------------
raw = pd.read_csv(ELECTION, sep=";", decimal=",", encoding="utf-8-sig")
votes = raw.rename(columns={
    "LÄNSNAMN": "county", "KOMMUNNAMN": "municipality",
    "RÖSTANDE": "voters", "RÖSTBERÄTTIGADE": "electorate", "VALDELTAGANDE": "turnout",
})
votes["code"] = (votes["LÄNSKOD"].astype(str).str.zfill(2)
                 + votes["KOMMUNKOD"].astype(str).str.zfill(2))
votes = votes[["code", "municipality", "county", "electorate", "voters", "turnout"]]
print("election:", votes.shape, "codes unique:", votes["code"].is_unique)
print(votes.head(3).to_string())

income_raw = pd.read_csv(INCOME, encoding="latin-1")
print("income raw:", income_raw.shape, list(income_raw.columns))
print(income_raw.head(4).to_string())
income = income_raw.rename(columns={"kön": "sex", "Medianinkomst, tkr 2018": "median_income"})
income[["code", "name"]] = income["region"].str.split(" ", n=1, expand=True)
print("rows per code in income:", income.groupby("code").size().value_counts().to_dict())
print("sex values:", income["sex"].value_counts().to_dict())

edu_raw = pd.read_csv(EDUCATION, encoding="latin-1")
print("education raw:", edu_raw.shape, list(edu_raw.columns))
edu = edu_raw.rename(columns={"utbildningsnivå": "level", "Antal 2018": "people"})
edu["code"] = edu["region"].str.split(" ", n=1).str[0]
print("rows per code in education:", edu.groupby("code").size().value_counts().to_dict())
print("levels:", edu["level"].unique().tolist())

# --- The duplicated-key trap -------------------------------------------------------
naive = votes.merge(income[["code", "sex", "median_income"]], on="code")
print(f"naive join: {len(votes)} rows before, {len(naive)} after")
naive_edu = votes.merge(edu[["code", "level", "people"]], on="code")
print(f"naive join with education: {len(naive_edu)} rows")

# The fix: one row per key on the right
inc_total = income.loc[income["sex"] == "totalt", ["code", "median_income"]]
print("income rows with sex == totalt:", len(inc_total), "unique:", inc_total["code"].is_unique)
uni_levels = ["eftergymnasial utbildning, 3 år eller mer", "forskarutbildning"]
edu_share = (
    edu.assign(uni=edu["level"].isin(uni_levels) * edu["people"])
    .groupby("code", as_index=False)
    .agg(people=("people", "sum"), uni=("uni", "sum"))
    .assign(uni_share=lambda d: 100 * d["uni"] / d["people"])
    [["code", "uni_share"]]
)
print("edu_share rows:", len(edu_share))

# Unmatched rows, both ways (anti joins)
not_in_income = votes[~votes["code"].isin(inc_total["code"])]
not_in_votes = inc_total[~inc_total["code"].isin(votes["code"])]
print("election rows without income:", len(not_in_income))
print("income rows without election:", len(not_in_votes))
print(income.loc[income["code"].isin(not_in_votes["code"]) & (income["sex"] == "totalt"),
                 "region"].head(4).tolist())

# What goes wrong when the code is read as a number
as_number = income["code"].astype(int)
print("code as number:", income["code"].iloc[9], "->", as_number.iloc[9])

df = (
    votes
    .merge(inc_total, on="code", how="left", validate="one_to_one")
    .merge(edu_share, on="code", how="left", validate="one_to_one")
)
print("joined:", df.shape, "missing:", df.isna().sum().to_dict())
print(df.head(3).round(1).to_string())

# Toy example on the page
left = pd.DataFrame({"key": ["A", "B", "C"], "x": [1, 2, 3]})
right = pd.DataFrame({"key": ["B", "C", "D"], "y": [20, 30, 40]})
for how in ["inner", "left", "right", "outer"]:
    print(how, len(left.merge(right, on="key", how=how)))
print(left[~left["key"].isin(right["key"])])
dup = pd.DataFrame({"key": ["B", "B", "C"], "y": [20, 21, 30]})
print("left join with duplicated B:", len(left.merge(dup, on="key", how="left")))

# --- Statistics: correlation and trend ---------------------------------------------
r = np.corrcoef(df["median_income"], df["turnout"])[0, 1]
slope, intercept = np.polyfit(df["median_income"], df["turnout"], 1)
print(f"r(income, turnout) = {r:.2f}; slope = {10 * slope:.2f} points per 10 000 SEK")
print("income range:", df["median_income"].min(), df["median_income"].max(),
      "median", df["median_income"].median())
print(df.nsmallest(3, "median_income")[["municipality", "median_income", "turnout"]].to_string())
print(df.nlargest(3, "median_income")[["municipality", "median_income", "turnout"]].to_string())
print("corr matrix:\n", df[["median_income", "uni_share", "turnout"]].corr().round(2))
print("uni share range:", df["uni_share"].min().round(1), df["uni_share"].max().round(1))
print(df.nlargest(3, "uni_share")[["municipality", "uni_share"]].round(1).to_string())

# 1. Turnout against income, with the least-squares line
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(df["median_income"], df["turnout"], "o", color=GREY, ms=3.5, alpha=.7)
xs = np.array([df["median_income"].min(), df["median_income"].max()])
ax.plot(xs, intercept + slope * xs, color=RED, lw=2)
for name in ["Danderyd", "Lomma", "Haparanda", "Perstorp", "Södertälje"]:
    row = df.loc[df["municipality"] == name].iloc[0]
    ax.annotate(name, (row["median_income"], row["turnout"]), xytext=(5, 3),
                textcoords="offset points", color=RED, fontsize=10)
ax.set_xlabel("Median income, ages 20–64, 2018 (thousand SEK)")
ax.set_ylabel("Turnout 2018 (%)")
save(fig, "income-turnout")

# 2. Income against education: the two travel together
r_ie = np.corrcoef(df["median_income"], df["uni_share"])[0, 1]
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(df["uni_share"], df["median_income"], "o", color=GREY, ms=3.5, alpha=.7)
for name in ["Danderyd", "Lund", "Uppsala", "Perstorp"]:
    row = df.loc[df["municipality"] == name].iloc[0]
    ax.annotate(name, (row["uni_share"], row["median_income"]), xytext=(5, 3),
                textcoords="offset points", color=RED, fontsize=10)
ax.set_xlabel("Share with 3+ years of university, ages 16–74, 2018 (%)")
ax.set_ylabel("Median income (thousand SEK)")
save(fig, "income-education")
print(f"r(income, uni share) = {r_ie:.2f}")


# 3. Join types: two small tables and what each join keeps
def draw_table(ax, x, y, title, header, rows, red_rows=(), na="NA"):
    """Draw a small table with its top-left corner at (x, y)."""
    w, h = 0.55, 0.42
    ax.text(x, y + 0.2, title, fontsize=11, fontweight="bold", va="bottom", color=INK)
    for j, col in enumerate(header):
        ax.text(x + w * (j + .5), y - h / 2, col, ha="center", va="center",
                fontsize=10, fontweight="bold", color=INK)
    ax.plot([x, x + w * len(header)], [y - h, y - h], color=INK, lw=1)
    for i, row in enumerate(rows):
        yy = y - h * (i + 1.5)
        if i in red_rows:
            ax.add_patch(plt.Rectangle((x, yy - h / 2), w * len(header), h,
                                       color=RED, alpha=.18, lw=0))
        for j, v in enumerate(row):
            ax.text(x + w * (j + .5), yy, na if v is None else str(v), ha="center",
                    va="center", fontsize=10, family="monospace",
                    color=GREY if v is None else INK)


fig = plt.figure(figsize=(10, 3.6))
ax = fig.add_axes((0.01, 0.01, 0.98, 0.98))
ax.set_xlim(0, 12.6)
ax.set_ylim(-2.75, 0.7)
ax.axis("off")
draw_table(ax, 0.0, 0, "left table", ["key", "x"], [["A", 1], ["B", 2], ["C", 3]], red_rows=[0])
draw_table(ax, 1.6, 0, "right table", ["key", "y"], [["B", 20], ["C", 30], ["D", 40]], red_rows=[2])
ax.plot([3.15, 3.15], [0.5, -2.2], color=LIGHT, lw=1)
draw_table(ax, 3.4, 0, "inner join", ["key", "x", "y"], [["B", 2, 20], ["C", 3, 30]])
draw_table(ax, 5.4, 0, "left join", ["key", "x", "y"],
           [["A", 1, None], ["B", 2, 20], ["C", 3, 30]], red_rows=[0])
draw_table(ax, 7.4, 0, "right join", ["key", "x", "y"],
           [["B", 2, 20], ["C", 3, 30], ["D", None, 40]], red_rows=[2])
draw_table(ax, 9.4, 0, "full join", ["key", "x", "y"],
           [["A", 1, None], ["B", 2, 20], ["C", 3, 30], ["D", None, 40]], red_rows=[0, 3])
draw_table(ax, 11.4, 0, "anti join", ["key", "x"], [["A", 1]], red_rows=[0])
ax.text(0, -2.6, "Red: rows whose key has no match in the other table. NA: missing value.",
        fontsize=10, color=INK)
save(fig, "join-types", tight=False)

# --- The database ------------------------------------------------------------------
DB.unlink(missing_ok=True)
con = sqlite3.connect(DB)
con.execute("""
    CREATE TABLE election (
        code TEXT PRIMARY KEY, municipality TEXT NOT NULL, county TEXT NOT NULL,
        electorate INTEGER, voters INTEGER, turnout REAL)""")
con.execute("""
    CREATE TABLE income (
        code TEXT NOT NULL, region TEXT NOT NULL, sex TEXT NOT NULL, median_income REAL,
        PRIMARY KEY (code, sex))""")
con.execute("""
    CREATE TABLE education (
        code TEXT NOT NULL, region TEXT NOT NULL, level TEXT NOT NULL, people INTEGER,
        PRIMARY KEY (code, level))""")
con.executemany("INSERT INTO election VALUES (?, ?, ?, ?, ?, ?)",
                votes.itertuples(index=False, name=None))
sex_en = {"totalt": "total", "män": "men", "kvinnor": "women"}
con.executemany("INSERT INTO income VALUES (?, ?, ?, ?)", zip(
    income["code"], income["name"], income["sex"].map(sex_en), income["median_income"]))
con.executemany("INSERT INTO education VALUES (?, ?, ?, ?)", zip(
    edu["code"], edu["region"].str.split(" ", n=1).str[1], edu["level"], edu["people"]))
con.commit()
con.execute("VACUUM")
con.close()

con = sqlite3.connect(DB)
q = lambda sql: pd.read_sql_query(sql, con)
print(q("SELECT name, sql FROM sqlite_master WHERE type = 'table'")["name"].tolist())
print(q("SELECT COUNT(*) AS n FROM election"), q("SELECT COUNT(*) AS n FROM income"),
      q("SELECT COUNT(*) AS n FROM education"))
print(q("""
SELECT municipality, county, turnout
FROM election
WHERE turnout < 80
ORDER BY turnout
"""))
by_county = q("""
SELECT county, COUNT(*) AS n, ROUND(AVG(turnout), 1) AS mean_turnout
FROM election
GROUP BY county
ORDER BY mean_turnout
LIMIT 3
""")
print(by_county)
joined = q("""
SELECT e.municipality, e.turnout, i.median_income
FROM election AS e
JOIN income AS i ON e.code = i.code
WHERE i.sex = 'total'
ORDER BY i.median_income DESC
LIMIT 5
""")
print(joined)
print("sql join without the WHERE:", q("""
SELECT COUNT(*) AS n FROM election AS e JOIN income AS i ON e.code = i.code""")["n"][0])
print(q("""
SELECT e.county, ROUND(AVG(i.median_income), 1) AS mean_income, ROUND(AVG(e.turnout), 1) AS mean_turnout
FROM election AS e
JOIN income AS i ON e.code = i.code
WHERE i.sex = 'total'
GROUP BY e.county
ORDER BY mean_income DESC
LIMIT 3
"""))
print(q("""
SELECT i.region FROM income AS i
LEFT JOIN election AS e ON i.code = e.code
WHERE e.code IS NULL AND i.sex = 'total'
LIMIT 3"""))
try:
    con.execute("INSERT INTO election VALUES ('0114', 'Upplands Väsby', 'Stockholm', 1, 1, 1)")
except sqlite3.IntegrityError as err:
    print("primary key stops a duplicate:", err)
con.close()
print("db size:", DB.stat().st_size)
