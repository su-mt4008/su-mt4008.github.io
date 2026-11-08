---
outline: 2
---

# Tables and Honest Plots

**This week** you learn to read a real data file correctly, to shape it into a table you can
work with, to summarise groups, and to choose and draw a plot that tells the truth. These are
the **Cleaning** and **Exploration** steps of the cycle, and most of the work in any analysis.

**By the end of the week you can**

- read a file with semicolons, decimal commas and Swedish characters, and check that it was read
  correctly;
- say whether a table is tidy, and why that matters;
- use the five verbs (select, filter, mutate, arrange, group and summarise) in pandas or dplyr;
- summarise each group with its size, centre and spread, and its uncertainty when the data are a
  sample;
- choose a plot that fits the question, and spot a plot that misleads;
- write a review comment that helps the author.

**How to use this page.** Read it from top to bottom with VS Code open, and run the code as you
go: download [election-2018-municipalities.csv](/data/week-2/election-2018-municipalities.csv)
into `data/raw/` in a scratch folder first, so the paths below work. Then do [HW2](/homework/2).

**Also read this week:** [Statistics: the basics](/statistics), sections
[3](/statistics#_3-describe-before-you-test) and
[4](/statistics#_4-how-sure-are-you-standard-errors-and-confidence-intervals) again: describing
groups and putting an interval on a mean. HW2 uses both.

## The example: who voted in 2018?

The whole page uses one dataset: the result of the 2018 Riksdag election in each of Sweden’s
290 municipalities, from the Election Authority (Valmyndigheten). The question:

> **Where in Sweden did people vote least in 2018, and how much does turnout differ between
> counties?**

Turnout is the share of the people entitled to vote who did vote. Each row of the file is one
municipality.

## Reading a real file

Open the file in a text editor before you read it into Python or R. The first lines look like this:

```text
LÄNSKOD;KOMMUNKOD;LÄNSNAMN;KOMMUNNAMN;M;C;L;KD;S;V;MP;SD;…;RÖSTANDE;RÖSTBERÄTTIGADE;VALDELTAGANDE
1;14;Stockholms län;Upplands Väsby;23,11;6,26;5,66;6,71;26,97;…;26036;30740;84,7
```

Three things differ from the “standard” CSV a function expects by default:

| What you see | What it means | How to tell the function |
|---|---|---|
| `;` between values | the separator is a semicolon, not a comma | `sep=";"` / `read_csv2()` |
| `23,11` | a **decimal comma**, as in Swedish | `decimal=","` / `read_csv2()` |
| `Ä`, `Ö` in the names | the text encoding matters | `encoding="utf-8-sig"` / readr reads UTF-8 by default |

If you read it with the defaults, pandas splits on the commas *inside the numbers* and gives up:
`Expected 26 fields in line 6, saw 27`. Worse things can happen silently: with only `sep=";"`,
the file reads without an error, but `84,7` stays text, and every calculation on it is wrong or
fails later.

:::code-group
```python [Python]
import pandas as pd

raw = pd.read_csv(
    "data/raw/election-2018-municipalities.csv",
    sep=";", decimal=",", encoding="utf-8-sig",
)
```
```r [R]
library(readr)

# read_csv2 is read_csv for files with ; and decimal commas
raw <- read_csv2("data/raw/election-2018-municipalities.csv")
```
:::

**Always check what you got.** Three looks catch almost every reading mistake:

:::code-group
```python [Python]
raw.shape          # (290, 45): 290 municipalities, as expected?
raw.dtypes         # are the numbers numbers (float64, int64), not text (object/str)?
raw.head()         # do the first rows look like the file?
```
```r [R]
dim(raw)           # 290 45
glimpse(raw)       # (from dplyr) types: <dbl> and <int> are numbers, <chr> is text
head(raw)
```
:::

::: warning Don’t open it in Excel and save
Excel may change separators, dates and decimal signs when it saves, without telling you. Keep
the raw file exactly as you downloaded it, and fix everything in code (week 1’s first habit).
:::

**Try it.** Read the file with only `sep=";"` (or `read_csv()` in R). What type does the
turnout column get? Then read it correctly and compare.

## Tidy data

Before you analyse a table, check its shape. A table is **tidy** when

1. each **row** is one observation (here: one municipality),
2. each **column** is one variable (county, electorate, turnout, …),
3. each **cell** holds one value.

Tidy tables are what the tools expect: every verb below and every plotting function works on
columns of variables. Most data you download is not tidy: years spread across columns, two
values in one cell (`"12 (3%)"`), notes in the last rows. Our file is nearly tidy for turnout, but
the party results are *wide*: one column per party. That is fine for “the share for S in each
municipality”, but awkward for “compare all parties”, where you would want one row per
municipality and party. Reshaping between wide and long is in [week 3](/lectures/week-3).

## The five verbs

Almost everything you do to a table is a combination of five operations:

| Verb | What it does | pandas | dplyr |
|---|---|---|---|
| **select** | keep some columns | `df[["a", "b"]]` | `select(a, b)` |
| **filter** | keep the rows that satisfy a condition | `df[df["a"] > 1]` or `df.query("a > 1")` | `filter(a > 1)` |
| **mutate** | add a column computed from others | `df.assign(c=df["a"] / df["b"])` | `mutate(c = a / b)` |
| **arrange** | sort the rows | `df.sort_values("a")` | `arrange(a)` |
| **group and summarise** | one row per group, with a summary | `df.groupby("g").agg(...)` | `group_by(g) \|> summarise(...)` |

Here they are on the election file. Select and rename the columns we need, and tidy the county
names:

:::code-group
```python [Python]
votes = (
    raw.rename(columns={
        "LÄNSNAMN": "county", "KOMMUNNAMN": "municipality",
        "RÖSTANDE": "voters", "RÖSTBERÄTTIGADE": "electorate",
        "VALDELTAGANDE": "turnout",
    })
    [["county", "municipality", "electorate", "voters", "turnout"]]          # select
    .assign(county=lambda d: d["county"].str.removesuffix(" län"))           # mutate
)
```
```r [R]
library(dplyr)

votes <- raw |>
  select(county = LÄNSNAMN, municipality = KOMMUNNAMN,
         electorate = RÖSTBERÄTTIGADE, voters = RÖSTANDE,
         turnout = VALDELTAGANDE) |>                       # select and rename
  mutate(county = sub(" län$", "", county))                # mutate
```
:::

Check the mutate by recomputing turnout from its parts: `voters / electorate` should give the
same numbers as the column the file provides. Checks like this cost one line and catch
misread columns.

:::code-group
```python [Python]
votes = votes.assign(check=100 * votes["voters"] / votes["electorate"])
(votes["check"] - votes["turnout"]).abs().max()   # 0.005: they agree, up to rounding
```
```r [R]
votes |> mutate(check = 100 * voters / electorate) |>
  summarise(max_diff = max(abs(check - turnout)))
```
:::

The three municipalities where people voted least (filter and arrange):

:::code-group
```python [Python]
votes.sort_values("turnout").head(3)
```
```r [R]
votes |> arrange(turnout) |> head(3)
```
:::

| municipality | county | turnout |
|---|---|---|
| Haparanda | Norrbotten | 72.8% |
| Södertälje | Stockholm | 77.5% |
| Botkyrka | Stockholm | 78.2% |

Write each step on its own line, as above: a reader can follow the pipeline from top to bottom,
and a reviewer can comment on a single step.

## Summarising groups

**Group and summarise** turns 290 rows into one row per county. Report the same four things for
every group: **how many** observations, a **centre** (mean, and the median, which outliers can’t
drag around), and a **spread** (the standard deviation). See
[statistics section 3](/statistics#_3-describe-before-you-test).

:::code-group
```python [Python]
by_county = (
    votes.groupby("county")["turnout"]
    .agg(n="size", mean="mean", median="median", sd="std")
    .sort_values("mean")
)
```
```r [R]
by_county <- votes |>
  group_by(county) |>
  summarise(n = n(), mean = mean(turnout), median = median(turnout),
            sd = sd(turnout)) |>
  arrange(mean)
```
:::

The lowest and highest counties:

| County | n | mean | median | sd |
|---|---|---|---|---|
| Norrbotten | 14 | 84.3% | 85.3% | 4.3 |
| Västerbotten | 15 | 85.2% | 85.0% | 2.1 |
| Gävleborg | 10 | 85.6% | 85.8% | 1.3 |
| … | | | | |
| Jönköping | 13 | 88.4% | 88.2% | 2.0 |
| Gotland | 1 | 88.8% | 88.8% | – |
| Östergötland | 13 | 88.9% | 89.1% | 1.1 |

Three things to read off a table like this before you write a single conclusion:

- **The group sizes.** Gotland is one municipality, so it has no spread, and its “mean” is
  one number. Small groups give unreliable summaries; say so, or combine them.
- **Mean against median.** Norrbotten’s mean is a point below its median: one municipality
  (Haparanda, 72.8%) pulls it down. When the two disagree, look for outliers.
- **The spread against the differences.** Counties differ by about four points from lowest to
  highest, but municipalities *within* Norrbotten, Stockholm and Skåne differ by 13–17 points. The
  county is not the whole story.

### Sample or population?

Statistics section 4 shows how to put a **95% confidence interval** on a mean,
$\bar x \pm 1.96\, s/\sqrt n$. Whether you need one depends on what the data are.

- **Our 290 municipalities are all of them.** The table *is* the 2018 result; there is no other
  set of municipalities it could have been. There is no sampling uncertainty to report.
- **In HW2, the apartments are a sample.** The 158 sales are some of the sales that could have
  happened in Ekhagen; with other buyers in other months, the mean would have come out
  differently. There, every group mean needs its interval.

:::code-group
```python [Python]
import numpy as np

summary = df.groupby("group")["y"].agg(n="size", mean="mean", sd="std")
summary["se"] = summary["sd"] / np.sqrt(summary["n"])
summary["low"] = summary["mean"] - 1.96 * summary["se"]
summary["high"] = summary["mean"] + 1.96 * summary["se"]
```
```r [R]
summary <- df |>
  group_by(group) |>
  summarise(n = n(), mean = mean(y), sd = sd(y)) |>
  mutate(se = sd / sqrt(n),
         low = mean - 1.96 * se, high = mean + 1.96 * se)
```
:::

With fewer than about 30 observations per group, 1.96 is a little too small; see the tip on the
$t$-distribution in [section 4](/statistics#the-confidence-interval). For HW2, state which you used.

## Choosing a plot

Start from the question, not from the chart types you know:

| Your question is about… | Plot | Avoid |
|---|---|---|
| the **distribution** of one variable | histogram, or a strip of dots | a bar chart of the mean only |
| **comparing groups** | dots for every observation, with the median or the mean ± interval; a boxplot for many points | bars of the mean alone, which hide the spread |
| the **relationship** between two numbers | scatter plot | a line through points that are not in order |
| **change over time** | line chart, time on the x-axis | uneven time steps drawn as even |
| **parts of a whole** | stacked bars, for few parts | pie charts with many slices |

**One variable: the distribution.** A histogram of turnout shows where most municipalities are,
how wide the spread is, and the three that are far below the rest.

![Histogram of turnout: most municipalities between 84 and 91%, with Haparanda, Södertälje and Botkyrka far below](/img/week-2/turnout-histogram.svg)

**Comparing groups.** Show every municipality, not just a bar per county. The median shows the
centre, and the dots show the spread, the group sizes and the outliers, all of which the
table above had to list in words.

![Turnout per county: grey dots for municipalities, a red mark at each county's median; number of municipalities in brackets](/img/week-2/turnout-counties.svg)

**Two numbers: a scatter plot.** Do big municipalities vote differently from small ones? The
electorate runs from 1 886 (Bjurholm) to 704 157 (Stockholm). On an ordinary axis, every
municipality but a handful would be squashed against the left edge. A **log scale**, where each
step is ten times the last, spreads them out. Say on the axis that it is a log scale.

![Turnout against the number of people entitled to vote, on a log scale: no strong pattern](/img/week-2/turnout-size.svg)

There is no strong pattern: size alone says little about turnout (correlation 0.18 with the
log size; more on correlation in [week 4](/lectures/week-4)). The low ones are a mix of
large suburbs and a small border town. “Why” needs other data, such as income or the share
born abroad, and that is joining tables, in week 4.

### Drawing it

:::code-group
```python [Python]
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.scatter(votes["electorate"], votes["turnout"], alpha=0.6)
ax.set_xscale("log")
ax.set_xlabel("People entitled to vote (log scale)")
ax.set_ylabel("Turnout (%)")
plt.show()
```
```r [R]
library(ggplot2)

ggplot(votes, aes(x = electorate, y = turnout)) +
  geom_point(alpha = 0.6) +
  scale_x_log10() +
  labs(x = "People entitled to vote (log scale)", y = "Turnout (%)")
```
:::

In a Quarto report, put the caption in the chunk options (`#| fig-cap: "…"`), so it appears
under the figure and in the rendered `report.md`.

## Honest plots

A plot is an argument. It can be technically correct and still make the reader believe
something the data don’t support. Here are the same three numbers twice:

![The same mean turnouts for Norrbotten, Stockholm and Östergötland: with the axis starting at 84%, Östergötland's bar looks fifteen times Norrbotten's; from 0%, they look almost equal](/img/week-2/misleading-axis.svg)

On the left, Östergötland’s bar is almost fifteen times as tall as Norrbotten’s, but its
turnout is 4.5 points higher, about 5% more. A bar’s *length* is what the eye reads, so **bars must start
at zero**. If the differences are too small to see from zero, that is the honest message; to
show small differences, use dots, whose position rather than length carries the value, and
an axis that says where it starts.

A checklist for every figure you hand in:

1. **Does it answer the question?** Say in the caption what the reader should see.
2. **Axes labelled, with units.** “Turnout (%)”, not `VALDELTAGANDE`.
3. **Bars start at zero.** Dots and lines need not.
4. **Show the data, not just a summary**, when there are not too many points.
5. **The uncertainty is visible** when the data are a sample: an interval around each mean.
6. **Same scale** on panels the reader will compare.
7. **No decoration**: no 3D, no shadows, no second y-axis. Use colour only to highlight.
8. **Transformations are stated**: log scales, removed outliers, filtered groups.

**Try it.** Find a chart in a news article this week. Which of the eight points does it fail?

## Tables and numbers in a report

Tables in a report are for readers, not for the computer:

- **Round** to what matters: 84.3%, not 84.33285714.
- **Name** columns in words, with units.
- **Sort** by something meaningful (here by turnout), not alphabetically by accident.
- **Show** the few rows that matter, not a printout of 290.

Turn a data frame into a table that renders in `report.md` with `df.to_markdown()` in Python
(it needs the `tabulate` package, already in the template), or `knitr::kable(df)` in R.

**Numbers in your text should come from the code**, not be typed by hand, so they can’t drift
from the results when you change something. Quarto runs *inline code* in text:

````markdown
```{python}
low = votes.nsmallest(1, "turnout").iloc[0]
```

Turnout was lowest in `{python} low["municipality"]`, at `{python} f"{low['turnout']:.1f}"`%.
````

In R the same line is ``Turnout was lowest in `r low$municipality` ``.

## Reviewing a pull request well

You review a classmate’s HW2 this week. A review helps when it is **specific** and
**actionable**: it points to a line or a figure and says what would make it better.

| Less helpful | More helpful |
|---|---|
| “The plot is confusing.” | “In the second figure the y-axis starts at 50 000, so the 1-room bar looks twice as tall as the 3-room bar. Starting at zero, or using dots, would show the real difference.” |
| “Good job!” | “The table with n, mean and interval per group made the conclusion easy to check. I’d add one sentence on why you grouped 4 and 5 rooms together.” |
| “Wrong numbers.” | “Line 42 drops every row with any missing value, and that removes all 158 sales: every row misses something, such as `plotArea`. Dropping only rows missing `livingArea` keeps them.” |

On GitHub, comment on a specific line in **Files changed** (click the `+` next to it), and use
**suggestion** blocks for small text fixes: the author can accept them with one click. Finish
with a summary: what works, and the one or two changes that matter most. See
[Review a pull request](/guide#review-a-pull-request).

## Common pitfalls

- **Numbers read as text.** A sum gives `"84,786,5…"` or an error. Check the types right after
  reading.
- **Dropping too much.** `dropna()` without columns drops a row if *any* column is missing. Name
  the columns you need: `dropna(subset=["livingArea"])` or `filter(!is.na(livingArea))`.
- **Means of tiny groups.** A group of one has no spread; a group of three has an unreliable
  one. Report `n` next to every summary.
- **A plot that shows only means.** It hides the spread and the outliers. Show the dots.
- **Copying numbers into the text by hand.** Use inline code.

## Check your understanding

1. A file has `1.234,5` in a column. What are the separator, the decimal mark and the thousands
   mark, and how do you tell your reading function?
2. Is a table with the columns `municipality`, `turnout_2014`, `turnout_2018`, `turnout_2022`
   tidy? What would the tidy version look like?
3. Why does this page report no confidence intervals for county turnout, while HW2 asks for them?
4. A bar chart of average salary by sector has its y-axis from 30 000 to 40 000 SEK. What is
   wrong, and what would you draw instead?
5. Write a helpful review comment for: `ax.set_ylabel("y")`.

## Your task

Do [HW2](/homework/2): the whole cycle on apartment sales, with the focus on tables and plots.

## Further reading

- [R for Data Science (2e)](https://r4ds.hadley.nz): chapters 1 (visualisation), 3 (data
  transformation), 5 (tidy data) and 7 (data import). Written for R, but the ideas are the same
  in Python.
- [Python for Data Analysis (3e)](https://wesmckinney.com/book/): chapters 5, 6.1 and 10 (pandas
  basics, reading files, grouping).
- Claus O. Wilke, [Fundamentals of Data Visualization](https://clauswilke.com/dataviz/): chapter 5
  (a directory of plots) and chapter 17 (the principle of proportional ink).
- Hadley Wickham, [Tidy data](https://www.jstatsoft.org/article/view/v059i10), Journal of
  Statistical Software, 2014.
- Data: [Valmyndigheten, election results 2018](https://www.val.se/valresultat/riksdag-region-och-kommun/2018.html).
