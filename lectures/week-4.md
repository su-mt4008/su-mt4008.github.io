---
outline: 2
---

# Combining Data: Joins and Databases

**This week** you learn to combine tables: to match the rows of one table with the rows of
another, to check that nothing was lost or duplicated on the way, and to ask the same questions
of a database in SQL. Most questions worth asking need more than one table, and joining is where
analyses most often go wrong without any error message. On the statistics side, you measure how
two variables move together, and learn why that alone does not show that one causes the other.

**By the end of the week you can**

- say what a key is, and check that a column really is one;
- make keys from two sources match, for example `"0114"` and `14`;
- choose between an inner, left, right, full and anti join, and say what each keeps;
- check the number of rows before and after every join, and find the rows that did not match;
- write SQL queries with `SELECT`, `WHERE`, `GROUP BY`, `ORDER BY` and `JOIN`, and run them from
  Python or R;
- describe a relationship with a correlation and a slope, and list what else could explain it.

**How to use this page.** Read it from top to bottom with VS Code open, and run the code as you
go. In a scratch folder, download these four files into `data/raw/` first, so the paths below
work:

- [election-2018-municipalities.csv](/data/week-2/election-2018-municipalities.csv), the
  election file from week 2;
- [scb-median-income-2018.csv](/data/week-4/scb-median-income-2018.csv), median income per
  municipality;
- [scb-education-2018.csv](/data/week-4/scb-education-2018.csv), level of education per
  municipality;
- <a href="/data/week-4/municipalities-2018.sqlite" download>municipalities-2018.sqlite</a>, the same data as a
  database, for the SQL part.

Then do [HW4](/homework/4).

**Also read this week:** [Statistics: the basics](/statistics), sections
[6](/statistics#_6-relationships-correlation-and-trend) and
[7](/statistics#_7-correlation-is-not-causation): correlation, the least-squares line, and why
a relationship in data is not yet a cause. HW4 uses both.

## The example: do richer municipalities vote more?

In [week 2](/lectures/week-2) we found that turnout in the 2018 Riksdag election varied from
72.8% in Haparanda to 93.9% in Lomma, and that the size of a municipality said little about it.
To ask *why*, we need data the election file does not have. The question for this page:

> **Did municipalities with a higher income have a higher turnout in 2018?**

That needs three tables, from two sources:

| Table | Source | One row is | Rows |
|---|---|---|---|
| election | Valmyndigheten (week 2) | a municipality | 290 |
| income | Statistics Sweden (SCB), median income for ages 20–64, 2018 | a region **and a sex** | 936 |
| education | SCB, highest level of education for ages 16–74, 2018 | a region **and a level of education** | 2 496 |

The last column already shows the problem: 290, 936 and 2 496 rows, for the same 290
municipalities. Before joining anything, find out what one row of each table is.

The SCB files come from SCB’s open API and are encoded in Latin-1, not UTF-8 (week 2 showed
why the encoding matters):

:::code-group
```python [Python]
import pandas as pd

raw = pd.read_csv("data/raw/election-2018-municipalities.csv",
                  sep=";", decimal=",", encoding="utf-8-sig")
income = pd.read_csv("data/raw/scb-median-income-2018.csv", encoding="latin-1")
edu = pd.read_csv("data/raw/scb-education-2018.csv", encoding="latin-1")
income.head(3)
```
```r [R]
library(readr)
library(dplyr)

raw <- read_csv2("data/raw/election-2018-municipalities.csv")
income <- read_csv("data/raw/scb-median-income-2018.csv",
                   locale = locale(encoding = "latin1"))
edu <- read_csv("data/raw/scb-education-2018.csv",
                locale = locale(encoding = "latin1"))
head(income, 3)
```
:::

```text
     region      kön     ålder inkomstklass  Medianinkomst, tkr 2018
0  00 Riket      män  20-64 år       totalt                    363.8
1  00 Riket  kvinnor  20-64 år       totalt                    299.5
2  00 Riket   totalt  20-64 år       totalt                    330.1
```

`Riket` is the whole of Sweden, `kön` is sex (men, women, total), and the income is in thousands
of SEK (`tkr`). Each region has three rows, one per sex.

## Keys

A **key** is a column, or a set of columns, whose value identifies exactly one row. To join two
tables, you match the rows that have the same key value.

- A **primary key** identifies the rows of its own table. In the election table, each
  municipality should have exactly one row, so a municipality code is a candidate.
- A **foreign key** is a column that points to the primary key of *another* table. The `code`
  in the income table points to a municipality in the election table.

A key is only a key if it is **unique**. Don’t assume it; check it. The election file has two
code columns, `LÄNSKOD` (county) and `KOMMUNKOD` (municipality within the county):

:::code-group
```python [Python]
raw["KOMMUNKOD"].is_unique                       # False
raw.duplicated(["LÄNSKOD", "KOMMUNKOD"]).sum()   # 0: together, they are a key
income["region"].is_unique                       # False
income.groupby("region").size().value_counts()   # all 312 regions have 3 rows
```
```r [R]
anyDuplicated(raw$KOMMUNKOD) > 0                       # TRUE
raw |> count(LÄNSKOD, KOMMUNKOD) |> filter(n > 1)      # no rows: together, a key
income |> count(region) |> count(n, name = "regions")  # all 312 regions have 3 rows
```
:::

`KOMMUNKOD` alone is not unique: `80`, for example, is Stockholm in county `1`, Göteborg in
county `14` and Luleå in county `25`.
Only the pair identifies a municipality. In the income table, the key is the pair (region, sex).

## Making the keys match

The two sources write the same municipality differently:

| Source | Upplands Väsby |
|---|---|
| Valmyndigheten | `LÄNSKOD` = `1`, `KOMMUNKOD` = `14`, read as two numbers |
| SCB | `region` = `"0114 Upplands Väsby"`, one text with code and name |

The official municipality code is four characters: two for the county and two for the
municipality, with leading zeros. Build it on both sides, **as text**:

:::code-group
```python [Python]
votes = raw.rename(columns={"KOMMUNNAMN": "municipality", "VALDELTAGANDE": "turnout"})
votes["code"] = (votes["LÄNSKOD"].astype(str).str.zfill(2)
                 + votes["KOMMUNKOD"].astype(str).str.zfill(2))      # 1, 14 -> "0114"
votes = votes[["code", "municipality", "turnout"]]

income = income.rename(columns={"kön": "sex", "Medianinkomst, tkr 2018": "median_income"})
income["code"] = income["region"].str.split(" ").str[0]               # "0114 Upplands Väsby" -> "0114"
```
```r [R]
votes <- raw |>
  mutate(code = sprintf("%02d%02d", LÄNSKOD, KOMMUNKOD)) |>           # 1, 14 -> "0114"
  select(code, municipality = KOMMUNNAMN, turnout = VALDELTAGANDE)

income <- income |>
  rename(sex = kön, median_income = `Medianinkomst, tkr 2018`) |>
  mutate(code = sub(" .*", "", region))                              # "0114 Upplands Väsby" -> "0114"
```
:::

Why text and not numbers? As a number, `"0115"` becomes `115`, and `"01"` (Stockholm county)
becomes `1`. Codes are labels, not quantities: you never add them, and their leading zeros
matter. Read them as text.

**Why codes and not names?** Names are written differently in different places: SCB’s English
tables say “Stockholm county” where the Swedish ones say “Stockholms län”, and some exports from
SCB’s website write “Upplands Väsby” with an invisible soft hyphen instead of the space. Two names
that look the same on screen may not be equal to the computer. Join on a code whenever both
tables have one.

When one table has only names, you have to **harmonise** them: decide on one spelling, and
build a small lookup table from each name to a code. Then check, with an anti join (below),
that every name found its code. Countries are a common case: “Sweden”, “SWE”, “swe” and “SE”
are the same country in four different sources. You will meet this in HW4.

## Join types

A join takes two tables, the **left** and the **right**, and matches their rows on a key. The
join types differ in what they do with rows that have **no match** in the other table:

![Two small tables with keys A, B, C and B, C, D, and the result of each join: inner keeps B and C; left keeps A, B, C; right keeps B, C, D; full keeps all four; anti keeps only A](/img/week-4/join-types.svg)

| Join | Keeps | pandas | dplyr |
|---|---|---|---|
| **inner** | only rows with a match in both | `left.merge(right, on="key", how="inner")` | `inner_join(left, right, by = "key")` |
| **left** | every row of the left table; missing values where the right has no match | `how="left"` | `left_join()` |
| **right** | every row of the right table | `how="right"` | `right_join()` |
| **full** (outer) | every row of both | `how="outer"` | `full_join()` |
| **anti** | the rows of the left table that have **no** match | `left[~left["key"].isin(right["key"])]` | `anti_join()` |

:::code-group
```python [Python]
left = pd.DataFrame({"key": ["A", "B", "C"], "x": [1, 2, 3]})
right = pd.DataFrame({"key": ["B", "C", "D"], "y": [20, 30, 40]})

left.merge(right, on="key", how="inner")   # B, C
left.merge(right, on="key", how="left")    # A, B, C; y is missing for A
left.merge(right, on="key", how="outer")   # A, B, C, D
left[~left["key"].isin(right["key"])]      # anti join: A
```
```r [R]
left <- tibble(key = c("A", "B", "C"), x = c(1, 2, 3))
right <- tibble(key = c("B", "C", "D"), y = c(20, 30, 40))

inner_join(left, right, by = "key")   # B, C
left_join(left, right, by = "key")    # A, B, C; y is missing for A
full_join(left, right, by = "key")    # A, B, C, D
anti_join(left, right, by = "key")    # A
```
:::

Which one to use? Start from the table whose rows you want to keep, and use a **left join**:
here, one row per municipality in the election table, with the income added. An inner join
drops the unmatched rows without telling you, which hides problems. The anti join is for
checking: it lists exactly the rows that didn’t match.

**Try it.** Give `right` a second row with the key `B`. How many rows does the left join give
now? Why?

## Check the number of rows, before and after

A join never complains when the result is wrong. Two things go wrong silently:

1. **Duplicated keys multiply rows.** If a key appears twice in the right table, each matching
   row in the left table appears twice in the result.
2. **Unmatched keys drop rows** (inner join) **or leave holes** (left join): `"0114"` against
   `114`, “Sweden” against “SWE”.

Here is the first one. Join the election and the income tables on `code`:

:::code-group
```python [Python]
both = votes.merge(income, on="code")
len(votes), len(both)            # (290, 870)
```
```r [R]
both <- inner_join(votes, income, by = "code")
c(nrow(votes), nrow(both))       # 290 870
```
:::

290 municipalities went in, 870 rows came out: every municipality three times, once for men,
once for women and once for both. Any mean you compute from `both` counts each municipality
three times, mixed across sexes. Nothing in the output warns you; only the row count does.
(dplyr warns only when keys are duplicated on *both* sides; here they are duplicated on one.)

The fix is to make the key unique in the right table **before** the join: keep the rows for
both sexes together. Then ask the join to check it for you: with `validate="one_to_one"` in
pandas, or `relationship = "one-to-one"` in dplyr, the join stops with an error if a key is
duplicated.

:::code-group
```python [Python]
income_total = income.loc[income["sex"] == "totalt", ["code", "median_income"]]

df = votes.merge(income_total, on="code", how="left", validate="one_to_one")
len(df)                            # 290: one row per municipality, as before
df["median_income"].isna().sum()   # 0: every municipality found its income
```
```r [R]
income_total <- income |>
  filter(sex == "totalt") |>
  select(code, median_income)

df <- left_join(votes, income_total, by = "code", relationship = "one-to-one")
nrow(df)                           # 290: one row per municipality, as before
sum(is.na(df$median_income))       # 0: every municipality found its income
```
:::

Then look the other way, with an anti join: which rows of the income table found no
municipality?

:::code-group
```python [Python]
income_total[~income_total["code"].isin(votes["code"])]   # 22 rows
```
```r [R]
anti_join(income_total, votes, by = "code")               # 22 rows
```
:::

The 22 rows are Sweden as a whole (`00`) and the 21 counties (`01` to `25`). They should not
match a municipality, so this is fine; but now you *know* it, and can say so in your report.

**After every join, check:**

| Check | How |
|---|---|
| Is the key unique where it should be? | `df["key"].is_unique` · `anyDuplicated(df$key)` |
| Rows before and after? | `len()` · `nrow()`; a left join with a unique right key keeps the row count |
| Which rows didn’t match, in each direction? | two anti joins |
| Do a few joined rows look right? | look up one or two by hand |

### When the other table has many rows per key: summarise first

The education table has eight rows per municipality, one per level of education, with the number
of people at that level. We want one number per municipality: the share with at least three
years of university. Group and summarise first (week 2), so the key is unique, then join:

:::code-group
```python [Python]
edu = edu.rename(columns={"utbildningsnivå": "level", "Antal 2018": "people"})
edu["code"] = edu["region"].str.split(" ").str[0]
uni = ["eftergymnasial utbildning, 3 år eller mer", "forskarutbildning"]

edu_share = (
    edu.assign(uni_people=edu["people"].where(edu["level"].isin(uni), 0))
    .groupby("code", as_index=False)
    .agg(people=("people", "sum"), uni_people=("uni_people", "sum"))
    .assign(uni_share=lambda d: 100 * d["uni_people"] / d["people"])
    [["code", "uni_share"]]
)
df = df.merge(edu_share, on="code", how="left", validate="one_to_one")
df.shape                           # (290, 5)
```
```r [R]
uni <- c("eftergymnasial utbildning, 3 år eller mer", "forskarutbildning")

edu_share <- edu |>
  rename(level = utbildningsnivå, people = `Antal 2018`) |>
  mutate(code = sub(" .*", "", region)) |>
  group_by(code) |>
  summarise(uni_share = 100 * sum(people[level %in% uni]) / sum(people))

df <- left_join(df, edu_share, by = "code", relationship = "one-to-one")
dim(df)                            # 290 5
```
:::

(“Eftergymnasial utbildning, 3 år eller mer” is post-secondary education of three years or more;
“forskarutbildning” is doctoral education.) Joining the education table without summarising
would have given 290 × 8 = 2 320 rows.

Join two tables at a time, and check after each join. With three tables, that is two joins and
two checks.

**Try it.** Compute the mean turnout in `both` and in `votes`. They are the same: why? Now
compute the standard error of the mean, $s/\sqrt n$, in both tables. Which one is wrong, and
why is that dangerous when the data are a sample?

## Income and turnout

Now the question. The joined table has one row per municipality, with turnout, median income
and the share with a university degree.

![Turnout against median income in the 290 municipalities, with the least-squares line. Turnout is higher where income is higher; Haparanda and Södertälje are far below the line](/img/week-4/income-turnout.svg)

Median income goes from 274 800 SEK (Perstorp) to 444 200 SEK (Danderyd). Turnout tends to be
higher where income is higher. [Statistics section 6](/statistics#_6-relationships-correlation-and-trend)
gives two numbers to describe this:

:::code-group
```python [Python]
import numpy as np

r = np.corrcoef(df["median_income"], df["turnout"])[0, 1]                 # 0.58
slope, intercept = np.polyfit(df["median_income"], df["turnout"], 1)
10 * slope                                                                # 0.58
```
```r [R]
cor(df$median_income, df$turnout)                   # 0.58
fit <- lm(turnout ~ median_income, data = df)
10 * coef(fit)["median_income"]                     # 0.58
```
:::

- The **correlation** is $r = 0.58$: a clear tendency, but far from a straight line.
- The **slope** says that municipalities with a median income 10 000 SEK higher had, on average,
  a turnout 0.58 percentage points higher. Income is in thousands of SEK, so 10 000 SEK is 10
  units, hence `10 * slope`.

As in week 2, these are all 290 municipalities, not a sample of them, so we don’t put an interval
on the slope: there is no other set of municipalities it could have come from.

Read the plot as well as the numbers. Haparanda and Södertälje lie far below the line. A
correlation of 0.58 leaves a lot unexplained, and a few municipalities that don’t follow the
pattern can tell you as much as the line does.

## Correlation is not causation

Does a higher income *make* people vote? The data cannot say so on their own
([statistics section 7](/statistics#_7-correlation-is-not-causation)). Before concluding
anything, list what else could produce the same pattern:

- **Education.** Municipalities with a higher income also have more people with a university
  degree: the correlation between the two is 0.68. Education is also related to turnout
  ($r = 0.47$). Income and education travel together, so a plot of turnout against income
  cannot tell them apart. A third variable related to both, like this, is a **confounder**.

  ![Median income against the share with three or more years of university: they rise together, except university towns such as Lund and Uppsala, with many students and lower incomes](/img/week-4/income-education.svg)

  The plot also shows where they part: in Lund (43.5%) and Uppsala (34.7%), many people have a
  degree but the median income is low, because many of the adults are students.
- **Age, origin, and the place itself.** Age structure, the share born abroad, and how far it is
  to a polling station all differ between municipalities, and could matter.
- **Municipalities are not people.** Even a perfect correlation between municipalities would not
  show that *richer people* vote more. A municipality with a high median income can have low
  turnout among its richest residents. Data on groups support conclusions about groups.

Separating income from education needs more than a correlation (and more variables); what you
can do already is to say clearly that the two are tangled, and not write “income raises turnout”.

**Try it.** Compute the correlation between `uni_share` and `turnout`, and draw the scatter plot.
Which municipalities are far from the pattern?

## SQL: asking a database

Data in companies and public agencies often lives in a **relational database**: a set of tables
linked by keys, exactly like the three above, managed by a program that many people can query at
the same time. You talk to it in **SQL** (Structured Query Language). SQL describes *what* you
want, and the database works out how to get it.

The file <a href="/data/week-4/municipalities-2018.sqlite" download>municipalities-2018.sqlite</a> is an **SQLite**
database: the whole database in one file, with no server to install. It holds three tables:

| Table | Columns | Key |
|---|---|---|
| `election` | `code`, `municipality`, `county`, `electorate`, `voters`, `turnout` | `code` |
| `income` | `code`, `region`, `sex` (`'men'`, `'women'`, `'total'`), `median_income` | (`code`, `sex`) |
| `education` | `code`, `region`, `level`, `people` | (`code`, `level`) |

### The parts of a query

```sql
SELECT municipality, county, turnout    -- which columns
FROM election                           -- from which table
WHERE turnout < 80                      -- which rows
ORDER BY turnout                        -- in what order
```

| municipality | county | turnout |
|---|---|---|
| Haparanda | Norrbottens län | 72.78 |
| Södertälje | Stockholms län | 77.54 |
| Botkyrka | Stockholms län | 78.24 |

The same verbs you know from week 2, with other names:

| SQL | pandas | dplyr |
|---|---|---|
| `SELECT a, b` | `df[["a", "b"]]` | `select(a, b)` |
| `WHERE a > 1` | `df[df["a"] > 1]` | `filter(a > 1)` |
| `ORDER BY a` (`DESC` for largest first) | `sort_values("a")` | `arrange(a)` |
| `GROUP BY g` with `COUNT(*)`, `AVG(a)` | `groupby("g").agg(...)` | `group_by(g) \|> summarise(...)` |
| `JOIN t ON x.k = t.k` | `merge(..., on="k")` | `inner_join(..., by = "k")` |
| `LEFT JOIN` | `how="left"` | `left_join()` |
| `LIMIT 5` | `head(5)` | `head(5)` |

Group and summarise: the counties with the lowest mean turnout, the table from week 2 again:

```sql
SELECT county, COUNT(*) AS n, AVG(turnout) AS mean_turnout
FROM election
GROUP BY county
ORDER BY mean_turnout
```

Join: the five municipalities with the highest median income. `AS e` and `AS i` give the tables
short names, and `e.code` means “the column `code` of `e`”:

```sql
SELECT e.municipality, e.turnout, i.median_income
FROM election AS e
JOIN income AS i ON e.code = i.code
WHERE i.sex = 'total'
ORDER BY i.median_income DESC
LIMIT 5
```

| municipality | turnout | median_income |
|---|---|---|
| Danderyd | 91.92 | 444.2 |
| Lomma | 93.86 | 432.5 |
| Täby | 91.12 | 422.6 |
| Vaxholm | 92.74 | 406.9 |
| Lidingö | 90.16 | 403.8 |

A join in SQL multiplies rows exactly like one in pandas or dplyr: without the line
`WHERE i.sex = 'total'`, this join gives 870 rows. The same checks apply: count the rows with
`SELECT COUNT(*) FROM …`.

### Running SQL from Python and R

In Python, the `sqlite3` module is part of the standard library, and `pd.read_sql_query()` returns
the result as a data frame. In R, use the packages **DBI** and **RSQLite**. They are not in the
template’s `renv.lock`, so add them once: `renv::install(c("DBI", "RSQLite"))`, then
`renv::snapshot()`, and commit the changed `renv.lock`.

:::code-group
```python [Python]
import sqlite3

con = sqlite3.connect("data/raw/municipalities-2018.sqlite")
top = pd.read_sql_query("""
    SELECT e.municipality, e.turnout, i.median_income
    FROM election AS e
    JOIN income AS i ON e.code = i.code
    WHERE i.sex = 'total'
    ORDER BY i.median_income DESC
    LIMIT 5
""", con)
con.close()
```
```r [R]
library(DBI)

con <- dbConnect(RSQLite::SQLite(), "data/raw/municipalities-2018.sqlite")
top <- dbGetQuery(con, "
  SELECT e.municipality, e.turnout, i.median_income
  FROM election AS e
  JOIN income AS i ON e.code = i.code
  WHERE i.sex = 'total'
  ORDER BY i.median_income DESC
  LIMIT 5
")
dbDisconnect(con)
```
:::

Two more things you will need:

- **What is in the database?** `SELECT name FROM sqlite_master WHERE type = 'table'` lists the
  tables, and `PRAGMA table_info(election)` the columns of one (in R, also `dbListTables(con)`).
- **Putting a data frame into a database**: `df.to_sql("joined", con, index=False)` in Python,
  `dbWriteTable(con, "joined", df)` in R. With `sqlite3.connect(":memory:")` or
  `dbConnect(RSQLite::SQLite(), ":memory:")` the database lives in memory only, and disappears
  when your report has rendered; nothing to commit.

Queries are text, so a value can be pasted into them. Don’t build a query by pasting text in
yourself; pass values as **parameters**, with `?` in the query:
`pd.read_sql_query("SELECT municipality FROM election WHERE turnout < ?", con, params=(80,))`,
or `dbGetQuery(con, "... WHERE turnout < ?", params = list(80))` in R.

### When a database helps

For a few files that fit in memory, as in this course, pandas or dplyr is usually simpler. A
database is worth it when:

- **the data already lives in one**, as it does in most organisations: then SQL is how you get
  it out;
- **the data is too big for memory**: the database reads only the rows and columns a query
  needs, and you fetch the small result;
- **many people read and write the same data**, at the same time;
- **you want the data to stay clean**: a database can refuse bad rows. `code` is the primary key
  of `election`, so adding a second row with `code = '0114'` fails with
  `UNIQUE constraint failed: election.code`. The duplicated key that multiplied our rows above
  can never get into the table.

**Try it.** Write a query that gives the median income of women and of men in Stockholm
municipality (`code = '0180'`). Then one that gives the mean turnout per county together with the
mean median income, by joining `election` and `income` and grouping by `county`.

## Common pitfalls

- **Not counting rows.** Count before and after every join. A left join on a unique key keeps
  the number of rows of the left table; if it changes, a key is duplicated.
- **Joining on names.** Spelling, language and invisible characters differ between sources. Use
  codes; if you must use names, harmonise them and check with an anti join.
- **Codes read as numbers.** `"0114"` becomes `114`, and then nothing matches. Read codes as text.
- **An inner join by default.** It drops unmatched rows silently. Use a left join and look at
  what didn’t match.
- **Joining before summarising.** If the other table has several rows per key (one per sex, per
  level, per year), filter or summarise it to one row per key first.
- **“Correlated, so it causes.”** List the other explanations, and check the ones you can.

## Check your understanding

1. A table of students has the columns `name`, `programme` and `year`. Is `name` a good key? What
   would be better?
2. You left-join a table of 290 municipalities with a table of municipal results for 2014, 2018
   and 2022, on the municipality code. How many rows do you expect, and how do you fix it if you
   wanted one row per municipality?
3. After an inner join you have 280 rows instead of 290. How do you find the 10 that were lost?
4. Write the SQL that gives the number of municipalities in each county with a turnout below 85%.
5. Across countries, the number of TVs per person correlates with life expectancy. Name a
   confounder.

## Your task

Do [HW4](/homework/4): combine three sources on mobile phones, population and income across the
world, and ask the same data a few questions in SQL.

## Further reading

- [R for Data Science (2e)](https://r4ds.hadley.nz): chapter 19 (joins) and chapter 21
  (databases).
- [Python for Data Analysis (3e)](https://wesmckinney.com/book/): section 8.2 (combining and
  merging datasets).
- [SQLite tutorial in the Python documentation](https://docs.python.org/3/library/sqlite3.html#tutorial),
  and [DBI: getting started](https://dbi.r-dbi.org/articles/DBI.html) for R.
- [SQLBolt](https://sqlbolt.com): short interactive SQL lessons in the browser.
- Data: [Statistics Sweden (SCB), Statistical Database](https://www.statistikdatabasen.scb.se),
  tables HE0110 (income, *Sammanräknad förvärvsinkomst*) and UF0506 (education), retrieved
  2026-11-06 through SCB’s open API; licence CC0. Election data: see [week 2](/lectures/week-2).
