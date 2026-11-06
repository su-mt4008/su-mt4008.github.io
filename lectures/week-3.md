---
outline: 2
---

# Cleaning and Exploring Messy Data

**This week** you work on a file that was made for people to read, not for a computer:
notes above and below the table, column names split over two rows, codes where numbers should
be, and values hidden on purpose. You learn to turn it into a clean table, to say why values
are missing and what leaving them out does to your answer, and to explore the result
carefully before you conclude anything. These are the **Cleaning** and **Exploration** steps
again, on harder data, with **Analysis** at the end.

**By the end of the week you can**

- read a messy file as text, and decide yourself how each part becomes a number;
- write regular expressions that find and fix text;
- reshape a table between wide and long, and say which shape a task needs;
- say why values are missing, and what dropping them does to the answer;
- write checks in your code that stop it when the data are not what you think;
- write a data dictionary;
- tell an outlier that is an error from one that is real;
- put an interval on an estimate with the bootstrap, and ask whether it could be chance with a
  permutation test.

**How to use this page.** Read it from top to bottom with VS Code open, and run the code as you
go: download [grades-year6-2018-19.csv](/data/week-3/grades-year6-2018-19.csv) (1.6 MB) into
`data/raw/` in a scratch folder first, so the paths below work. Then do [HW3](/homework/3).

**Also read this week:** [Statistics: the basics](/statistics), the bootstrap at the end of
[section 4](/statistics#the-same-idea-by-computer-the-bootstrap), the permutation test in
[section 5](/statistics#the-same-idea-by-computer-the-permutation-test), and the traps in
[section 8](/statistics#_8-traps). This page uses all three, and so does HW3.

## The example: do girls get higher grades than boys?

The whole page uses one dataset: the grades of every pupil in year 6 (the year they turn 12) in
the school year 2018/19, summarised per municipality, type of school and subject, from the
Swedish National Agency for Education (Skolverket). The question:

> **In year 6, do girls get higher grades than boys? In which subjects, and by how much?**

Grades go from A (best) to F (fail). Skolverket turns them into **grade points**: F = 0,
E = 10, D = 12.5, C = 15, B = 17.5 and A = 20. The file gives the mean grade points per group,
so one grade step is 2.5 points.

## A first look at the file

Open the file in a text editor before anything else. The top looks like this:

```text
Statistik från Skolverket, http://www.skolverket.se

Grundskolan - Betyg per ämne årskurs 6
Valt läsår: 2018/19

;;;;;;Antal elever;Antal elever;Antal elever;Andel (%) med A-E;…;Genomsnittlig betygspoäng
Kommun;Kommun-kod;Län;Läns-kod;Typ av huvudman;Ämne;Totalt;Flickor;Pojkar;Totalt;Flickor;Pojkar;…
Ale;1440;Västra Götalands län;14;Samtliga;Bild;415;219;196;98,8;~100;~100;13,8;15,5;11,9;
```

and after the last municipality there are notes:

```text
Om en resultatuppgift baseras på färre än 10 elever, dubbelprickas den av sekretesskäl. …
Om antalet som ej uppnått kunskapskraven är 1-4 elever, så visas andelen … som ~100.
Om data saknas visas en prick (.) istället för utfall.
```

Make a list of everything a reading function would get wrong:

| What you see | What it means | What to do |
|---|---|---|
| four lines of text, then a blank line | a title, not data | skip them |
| two header rows | the column names are split: `Antal elever` above `Totalt`, `Flickor`, `Pojkar` | skip both, and name the columns yourself |
| `98,8` | a decimal comma | replace `,` with `.` |
| `1 154` | a space between thousands | remove the space |
| `..`, `.` and `~100` | codes, not numbers | find out what they mean, and keep track of them |
| notes after the last row | the explanation of the codes | read them, then drop those rows |
| `;` at the end of every line | an empty 16th column | read only the first 15 |

The notes say (translated):

- `..` means the result is based on **fewer than 10 pupils**, and is hidden to protect their
  privacy;
- `~100` means **1 to 4 pupils did not pass**, so the exact share is hidden;
- if the share for girls or for boys is shown as `~100`, the share for the other sex is hidden
  too (`..`), since otherwise you could work it out from the total;
- `.` means there are **no data**.

**Read everything as text first.** If you let the function guess, it reads `98,8` and `~100`
as text anyway, and it may read a column of whole numbers and `..` as text in one file and as
numbers in another. Reading as text and converting yourself means *you* decide what each value
becomes, and you can check it.

:::code-group
```python [Python]
import numpy as np
import pandas as pd

names = ["municipality", "code", "county", "county_code", "provider", "subject",
         "pupils_total", "pupils_girls", "pupils_boys",
         "pass_total", "pass_girls", "pass_boys",
         "points_total", "points_girls", "points_boys"]
raw = pd.read_csv(
    "data/raw/grades-year6-2018-19.csv",
    sep=";", skiprows=7, header=None, names=names, usecols=range(15),
    dtype=str, encoding="utf-8-sig",
)
raw.shape    # (17426, 15)
raw.tail()   # not data: the notes, text in the first columns and missing in the rest
```
```r [R]
library(readr)
library(dplyr)

names <- c("municipality", "code", "county", "county_code", "provider", "subject",
           "pupils_total", "pupils_girls", "pupils_boys",
           "pass_total", "pass_girls", "pass_boys",
           "points_total", "points_girls", "points_boys")
raw <- read_delim("data/raw/grades-year6-2018-19.csv", delim = ";", skip = 7,
                  col_names = names, col_select = 1:15,
                  col_types = cols(.default = col_character()))
dim(raw)     # 17426 15
tail(raw)    # not data: the notes, text in the first columns and NA in the rest
```
:::

`pupils` is the number of pupils with a grade, `pass` the share (%) who passed (E or better),
and `points` the mean grade points. In R, `read_delim` warns about 15 parsing problems. Look at
them with `problems(raw)`: they are the 15 note lines, which have one field instead of 16. A
warning like that is information; read it before you silence it.

## Regular expressions

The notes at the end must go. Every real row has a municipality code of exactly four digits
(`1440`, `0764`); no note does. A **regular expression** (regex) is a small language for
describing patterns in text like that one. The pieces you need most:

| Pattern | Matches | Example |
|---|---|---|
| `a`, `7` | that character | `län` matches the end of `Stockholms län` |
| `.` | **any** character | `A.e` matches `Ale` and `Axe` |
| `\.` | a real dot | `\.\.` matches `..` |
| `\d` | a digit 0–9 | `\d\d` matches `14` |
| `\s` | a space, tab or line break | `\d\s\d` matches `1 1` |
| `[abc]`, `[0-9]` | one of these characters | `[,.]` matches `,` or `.` |
| `x?`, `x*`, `x+` | x zero or one time, any number of times, at least once | `\d+` matches `1154` |
| `x{4}` | x exactly four times | `\d{4}` matches `1440` |
| `^`, `$` | the start, the end of the text | `^\d{4}$` matches `1440` but not `11440` |
| `a\|b` | a or b | `Kommunal\|Enskild` |
| `( )` | a group, to repeat or to extract | `^\d+(,\d+)?$` matches `98,8` and `415` |

So the pattern for a municipality code is `^\d{4}$`: the start, four digits, the end. We also
keep only the rows for `Samtliga`, all schools in the municipality together. (The others split
it by provider: municipal schools, independent schools and state schools.)

:::code-group
```python [Python]
is_row = raw["code"].str.contains(r"^\d{4}$", na=False)   # False for the notes
grades = raw[is_row & (raw["provider"] == "Samtliga")]
grades.shape                  # (6647, 15)
grades["code"].nunique()      # 289 municipalities
grades["subject"].nunique()   # 23 subjects; 289 * 23 = 6647
```
```r [R]
grades <- raw |>
  filter(grepl("^\\d{4}$", code), provider == "Samtliga")
dim(grades)                   # 6647 15
n_distinct(grades$code)       # 289 municipalities
n_distinct(grades$subject)    # 23 subjects; 289 * 23 = 6647
```
:::

In Python, write a pattern as a raw string, `r"\d"`, so that the backslash reaches the regex. In
R you double it: `"\\d"`.

**289 municipalities, but Sweden has 290.** Compare with the election file from week 2:
Dorotea is not in this file, and the file doesn't say why. A missing *row* is harder to spot
than a missing *value*: nothing marks it, and you find it only by counting and comparing with
what you expected. Write it down as a limitation.

The most common regex mistake is the dot. `.` means *any character*, so
`raw["code"].str.contains(".")` is true for every value that is not empty, and
`grepl(".", x)` too. To match a real dot, write `\.` (or `"\\."` in R), or turn regex off with
`regex=False` in pandas and `fixed = TRUE` in R.

**Try it.** Write a regex that matches a Swedish postcode such as `114 18` (three digits, a
space, two digits), and one that matches a year from 2000 to 2029. Test them on
[regex101.com](https://regex101.com) before you use them in code.

## Wide and long

Look at the nine value columns. Each name holds **two** variables: what is measured (`pupils`,
`pass`, `points`) and for whom (`total`, `girls`, `boys`). That is the *wide* shape, from week 2:
the same kind of value spread over many columns.

| municipality | subject | pupils_total | pupils_girls | pupils_boys | pass_total | … | points_boys |
|---|---|---|---|---|---|---|---|
| Ale | Bild | 415 | 219 | 196 | 98,8 | … | 11,9 |

The *long* shape has one row per value, with the two variables in their own columns:

| municipality | subject | measure | sex | text |
|---|---|---|---|---|
| Ale | Bild | pupils | total | 415 |
| Ale | Bild | pupils | girls | 219 |
| Ale | Bild | pupils | boys | 196 |
| Ale | Bild | pass | total | 98,8 |
| … | | | | |

Going from wide to long is called **pivot longer** (`melt` in pandas); going back is **pivot
wider** (`pivot` in pandas).

:::code-group
```python [Python]
long = grades.melt(
    id_vars=["municipality", "code", "county", "subject"],
    value_vars=names[6:], var_name="column", value_name="text",
)
long[["measure", "sex"]] = long["column"].str.split("_", expand=True)
long.shape   # (59823, 8): 6647 rows * 9 value columns
```
```r [R]
library(tidyr)   # not in the template: renv::install("tidyr"), then renv::snapshot()

long <- grades |>
  pivot_longer(pupils_total:points_boys,
               names_to = c("measure", "sex"), names_sep = "_",
               values_to = "text")
dim(long)    # 59823 9: 6647 rows * 9 value columns
```
:::

**Which shape?** Neither is right in general; it depends on the next step.

- **Long** is right when you treat many values the same way. Here every value is now in one
  column, `text`, so we clean it once instead of nine times. Long is also what you want for
  grouping by a variable (`sex`) and for plots that colour or split by it.
- **Wide** is right when you compare columns within a row. To compute *girls minus boys*,
  you need the two side by side, so we will pivot back.

**Check the row count after every reshape.** Wide to long must give exactly rows × columns;
anything else means rows were lost or duplicated.

## Turning text into numbers

Now clean the `text` column: keep the codes in a column of their own, remove the spaces, turn
the decimal comma into a point, and convert.

:::code-group
```python [Python]
codes = ["..", ".", "~100"]
long["note"] = long["text"].where(long["text"].isin(codes))     # the code, or missing
number = (long["text"].mask(long["text"].isin(codes))           # codes become missing
          .str.replace(" ", "")                                 # 1 154 -> 1154
          .str.replace(",", "."))                               # 98,8  -> 98.8
long["value"] = pd.to_numeric(number)
```
```r [R]
codes <- c("..", ".", "~100")
long <- long |>
  mutate(note = if_else(text %in% codes, text, NA),     # the code, or missing
         number = if_else(text %in% codes, NA, text),   # codes become missing
         number = gsub(" ", "", number),                # 1 154 -> 1154
         number = sub(",", ".", number),                # 98,8  -> 98.8
         value = as.numeric(number))
```
:::

`pd.to_numeric` without `errors="coerce"` **stops with an error** if any value is still not a
number. That is what you want: a value you didn't expect (`1.154`, `n/a`, `12*`) should stop
you, not silently become missing. R's `as.numeric` only warns and gives `NA`, so in R the check
in the next section is what catches it.

Keep the `note` column: *why* a value is missing is information. Count the codes per measure:

:::code-group
```python [Python]
pd.crosstab(long["measure"], long["note"].fillna("number"))
```
```r [R]
table(long$measure, coalesce(long$note, "number"))
```
:::

| measure | number | `.` | `..` | `~100` |
|---|---|---|---|---|
| pupils | 15 935 | 2 935 | 1 071 | 0 |
| pass | 10 051 | 3 061 | 2 194 | 4 635 |
| points | 16 026 | 2 996 | 919 | 0 |

A third of the pass shares are hidden behind `~100` or `..`. Before using them, ask why.

Finally, pivot wider by `measure`, so each row is one municipality, subject and sex, with one
column per measure. This is the tidy table we explore.

:::code-group
```python [Python]
tidy = (long.pivot(index=["municipality", "code", "county", "subject", "sex"],
                   columns="measure", values="value")
            .reset_index())
tidy.shape   # (19941, 8): 6647 * 3 sexes
```
```r [R]
tidy <- long |>
  select(municipality, code, county, subject, measure, sex, value) |>
  pivot_wider(names_from = measure, values_from = value)
dim(tidy)    # 19941 8: 6647 * 3 sexes
```
:::

## Why values are missing

There are three kinds of reasons a value can be missing. The names are standard, though not
very clear; the ideas are simple.

| Kind | In plain words | Example | What dropping does |
|---|---|---|---|
| **Missing completely at random** (MCAR) | missing for a reason that has nothing to do with the data | a page of a survey lost in the post | You lose precision, not accuracy: the rest are still a fair sample. |
| **Missing at random** (MAR) | missing for a reason you can **see** in other columns | grade points hidden (`..`) because a group has fewer than 10 pupils | The rest are no longer a fair sample, but you know who is missing (the small groups), so you can check and say what it means. |
| **Missing not at random** (MNAR) | missing **because of the value itself** | a pass share hidden (`~100`) *because* it is high | The rest are biased in a known direction, and the data you keep can’t tell you by how much. |

Most real missing values are not completely at random. Here, both `..` and `~100` are missing on
purpose, for reasons the notes explain.

**What dropping does: an example.** Take the share of pupils who passed mathematics, all pupils
in a municipality. It is shown for 274 municipalities and hidden as `~100` for 15. The 15 are
small: a median of 44 pupils, against 194 for the rest.

![The share who passed mathematics against the number of pupils. The hidden values (red ranges) are all in small municipalities and all high](/img/week-3/hidden-pass-rates.svg)

“Hidden” is not the same as “unknown”. If 1 to 4 of $n$ pupils failed, the share who passed lies
between $1 - 4/n$ and $1 - 1/n$; the red lines in the figure are those ranges. So we can work out
what dropping does:

| Municipalities | Shown | Hidden | Mean share passed, hidden dropped | with the hidden put back |
|---|---|---|---|---|
| under 100 pupils | 48 | 14 | 83.2% | 84.6% to 86.4% |
| 100 pupils or more | 226 | 1 | 86.9% | 86.9% |

For the whole country, dropping the hidden values moves the mean by less than a point. But
compare small and large municipalities: with the hidden values dropped, small municipalities
look **3.7 points** worse; the truth is between 0.5 and 2.3 points. Dropping did not just lose
data; it created most of a difference. That is what “missing not at random” costs.

**What to do with missing values:**

1. **Count** them, per column you use.
2. **Find out why** they are missing: read the documentation and the notes.
3. **Compare** the rows with and without the value: are they different in size, place, time?
4. **Decide:** drop them and say what that does; keep what you do know (here, a range); or
   fill them in with a stated rule. Filling in with the mean is rarely a good idea: it makes the
   data look less spread out and more certain than they are.
5. **Write down** what you did and why, in the report.

## Checks in code

You have made a lot of assumptions about this file. Write them down as **assertions**: a
statement about the data that must be true, which stops the code with an error if it is not.

:::code-group
```python [Python]
assert grades["code"].nunique() == 289                       # Dorotea is missing
assert not grades.duplicated(["code", "subject"]).any()      # one row per municipality and subject
assert (long["value"].isna() == long["note"].notna()).all()  # every value: a number or a known code
assert long.query("measure == 'points'")["value"].dropna().between(0, 20).all()
assert long.query("measure == 'pass'")["value"].dropna().between(0, 100).all()

# girls + boys = total, wherever all three are shown
pupils = tidy.pivot(index=["code", "subject"], columns="sex", values="pupils").dropna()
assert (pupils["total"] == pupils["girls"] + pupils["boys"]).all()
```
```r [R]
stopifnot(
  n_distinct(grades$code) == 289,                       # Dorotea is missing
  !any(duplicated(grades[c("code", "subject")])),       # one row per municipality and subject
  all(is.na(long$value) == !is.na(long$note)),          # every value: a number or a known code
  all(between(long$value[long$measure == "points"], 0, 20), na.rm = TRUE),
  all(between(long$value[long$measure == "pass"], 0, 100), na.rm = TRUE)
)

# girls + boys = total, wherever all three are shown
pupils <- tidy |>
  select(code, subject, sex, pupils) |>
  pivot_wider(names_from = sex, values_from = pupils) |>
  na.omit()
stopifnot(all(pupils$total == pupils$girls + pupils$boys))
```
:::

All six pass; the last one checks 5 243 rows. Good checks come from what you know about the
data: ranges (grade points are 0–20), counts (290 municipalities, minus one), parts that add up to
a total, keys that should be unique. They run every time you render, so if Skolverket fixes the
file, or you download next year's, a broken assumption stops you instead of quietly changing
your numbers.

**Try it.** Grade points for all pupils are an average of girls' and boys' points, so
`points_total` should lie between `points_girls` and `points_boys`. Write that check. (It passes for
all 5 233 rows where the three are shown.)

## A data dictionary

A **data dictionary** says, for every column of your clean table, what it means, its type and
unit, and which values it can take. It is for your reader, your reviewer and future-you; put it
in the Data section of your report, or in `data/raw/README.md`. For the tidy table:

| Column | Meaning | Type, unit | Values |
|---|---|---|---|
| `municipality` | the municipality (kommun) | text | 289 names; Dorotea is missing |
| `code` | the municipality code | text, four digits | `0114` … `2584`; text, so the leading 0 stays |
| `county` | the county (län) | text | 21 counties |
| `subject` | the school subject, in Swedish | text | 23 subjects, such as `Matematik` |
| `sex` | which pupils | text | `total`, `girls`, `boys` |
| `pupils` | pupils with a grade (A–F) or a dash in the subject | number | missing if fewer than 10 (`..`) |
| `pass` | share of those pupils with a pass, E or better | %, 0–100 | missing if hidden: `~100` means 1–4 failed |
| `points` | mean grade points, F = 0 … A = 20 | points, 0–20 | missing if fewer than 10 pupils |

Source: Skolverket, *Betyg per ämne årskurs 6, 2018/19*, all providers (`Samtliga`).

## Exploring the gap

Exploring is asking a series of small questions and answering each with a table or a plot. The
questions to ask of any new dataset:

1. **What is one row?** Here: one municipality, subject and sex.
2. **Who or what is missing?** One municipality; values in small groups; hidden pass shares.
3. **What does each variable look like?** Ranges, distributions, odd values.
4. **How do the variables relate?** Here: the gap against the size of the municipality.
5. **How do the groups differ?** Here: the gap in each subject.
6. **What surprises you?** Follow it up.

To compute the gap, girls and boys must be side by side, so pivot wider by `sex`:

:::code-group
```python [Python]
wide = tidy.pivot(index=["municipality", "subject"], columns="sex",
                  values=["pupils", "points"])
wide.columns = [f"{m}_{s}" for m, s in wide.columns]   # ("points", "girls") -> "points_girls"
wide = wide.reset_index()
wide["gap"] = wide["points_girls"] - wide["points_boys"]
```
```r [R]
wide <- tidy |>
  pivot_wider(id_cols = c(municipality, subject), names_from = sex,
              values_from = c(pupils, points)) |>
  mutate(gap = points_girls - points_boys)
```
:::

A positive gap means girls have higher grades. Six of the 23 subjects are taken by few pupils or
by a selected group: mother-tongue tuition, Swedish as a second language, sign language, an extra
modern language, and the combined science and social-studies grades some schools give instead of
the separate subjects. Each has at most 16 000 pupils, against about 100 000 or more in each of the other 17,
and most of their values are missing. We leave them out, and decided that from the numbers of
pupils, *before* looking at the gaps (see [choosing after looking](#choosing-after-looking)).

:::code-group
```python [Python]
few = ["Modersmål", "Svenska som andraspråk", "Teckenspråk",
       "Moderna språk som elevens val", "Naturorienterande ämnen", "Samhällsorienterande ämnen"]
gaps = wide[~wide["subject"].isin(few)].dropna(subset=["gap"])
by_subject = (
    gaps.groupby("subject")["gap"]
    .agg(n="size", mean="mean", median="median", girls_ahead=lambda g: (g > 0).mean())
    .sort_values("median")
)
```
```r [R]
few <- c("Modersmål", "Svenska som andraspråk", "Teckenspråk",
         "Moderna språk som elevens val", "Naturorienterande ämnen", "Samhällsorienterande ämnen")
gaps <- wide |> filter(!subject %in% few, !is.na(gap))
by_subject <- gaps |>
  group_by(subject) |>
  summarise(n = n(), mean = mean(gap), median = median(gap),
            girls_ahead = mean(gap > 0)) |>
  arrange(median)
```
:::

![The gap in grade points, girls minus boys, in 17 subjects: a dot per municipality, the median in red. Every median is above zero except English](/img/week-3/gap-by-subject.svg)

| Subject | n | median gap | girls ahead in |
|---|---|---|---|
| English | 287 | 0.0 | 47% of municipalities |
| Physical education | 287 | 0.4 | 66% |
| Mathematics | 287 | 0.6 | 74% |
| … | | | |
| Swedish | 285 | 2.6 | 99% |
| Art | 286 | 2.75 | 100% |

Girls have higher grades in 16 of the 17 subjects. The gap is largest in art and Swedish, about
one grade step (2.5 points), and smallest in mathematics, physical education and English. In
English, girls are ahead in 135 municipalities and boys in 142.

### Outliers: errors or real?

Look closer at mathematics. The gap goes from −2.8 to +4.8 points. Are the extremes mistakes?

![The gap in mathematics against the number of pupils: the extreme gaps are all in small municipalities, the large ones are close to zero](/img/week-3/math-gap-size.svg)

:::code-group
```python [Python]
import matplotlib.pyplot as plt

math = gaps[gaps["subject"] == "Matematik"]
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.scatter(math["pupils_total"], math["gap"], alpha=0.6)
ax.axhline(0, color="grey")
ax.set_xscale("log")
ax.set_xlabel("Pupils in year 6 with a grade in mathematics (log scale)")
ax.set_ylabel("Girls minus boys (grade points)")
plt.show()
```
```r [R]
library(ggplot2)

math <- gaps |> filter(subject == "Matematik")
ggplot(math, aes(x = pupils_total, y = gap)) +
  geom_point(alpha = 0.6) +
  geom_hline(yintercept = 0, colour = "grey") +
  scale_x_log10() +
  labs(x = "Pupils in year 6 with a grade in mathematics (log scale)",
       y = "Girls minus boys (grade points)")
```
:::

The largest gap is in Arjeplog, +4.8: 14 girls with a mean of 15.0 points against 11 boys with
10.2. Is that possible? Yes: a mean of 10.2 for 11 boys means most of them got an E. The counts
add up and the values are in range, so nothing says it is an error. It is real, but it rests
on 25 children, and a few of them more or less would change it a lot. The same holds at the
other end: Orsa and Åsele, −2.8, with 70 and 32 pupils. Stockholm, with 10 188 pupils, has a gap
of −0.1.

This funnel shape is typical: **small groups give extreme values**, in both directions, just by
chance. The spread of the gap is 1.6 points among the quarter of municipalities with the fewest
pupils, and 0.4 among the quarter with the most.

How to handle an outlier:

1. **Check whether it is possible**: the range, the unit, whether it agrees with other columns.
   A living area of 3 m², an age of 230, or girls + boys ≠ total are errors.
2. **If it is an error**, fix it in code if you can find the right value, otherwise make it
   missing, and say so in the report.
3. **If it is real**, keep it. Use summaries it can’t drag around (the median), or show the
   result with and without it.
4. **Never drop a value because it is inconvenient.** That is
   [choosing after looking](#choosing-after-looking).

**One municipality, one vote?** The mean gap over the 287 municipalities is 0.58 points. Weighted
by the number of pupils, it is 0.40, because the large municipalities have smaller gaps. Both are
correct answers to different questions: “in a typical municipality” and “for a typical pupil”.
Say which one you report.

## How sure are you?

The file covers every municipality, so why ask about uncertainty? Because the question is about
girls and boys in Swedish schools, not about the particular 117 000 children in the file. Next year's
pupils in the same schools would give somewhat different gaps, most of all in the small
municipalities. So we treat each municipality's gap as an observation of a random variable, and
the municipalities as independent. That is an approximation (neighbouring municipalities share
a lot), and a report should say so.

### An interval with the bootstrap

The mean gap in mathematics is 0.58 points. To see how much it could vary, use the bootstrap
from [statistics section 4](/statistics#the-same-idea-by-computer-the-bootstrap): draw 287
municipalities from the 287 **with replacement**, compute the mean gap, repeat 10 000 times, and
take the middle 95%.

:::code-group
```python [Python]
gap = math["gap"].to_numpy()
rng = np.random.default_rng(1)   # a seed makes the simulation reproducible
boot = [rng.choice(gap, len(gap)).mean() for _ in range(10_000)]
np.percentile(boot, [2.5, 97.5])   # about 0.45 to 0.70
```
```r [R]
gap <- math$gap
set.seed(1)   # a seed makes the simulation reproducible
boot <- replicate(10000, mean(sample(gap, replace = TRUE)))
quantile(boot, c(0.025, 0.975))   # about 0.45 to 0.70
```
:::

The interval is about **0.45 to 0.70 points**, the same as the formula
$\bar x \pm 1.96\, s/\sqrt n$ gives. The bootstrap earns its place when there is no formula:
replace `mean` with `median` in the code, and you get an interval for the median gap, 0.4 to
0.7 points.

### Could it be chance? A sign-flip test

If sex made no difference to grades, then in each municipality the gap would be as likely to
come out negative as positive: whether the girls or the boys happen to be ahead would be a coin
toss. This is the permutation test from
[statistics section 5](/statistics#the-same-idea-by-computer-the-permutation-test) for **paired**
data: swapping the labels “girls” and “boys” within a municipality flips the sign of its gap.
So flip each gap's sign at random, compute the mean, and repeat many times. That shows what
chance alone produces.

:::code-group
```python [Python]
rng = np.random.default_rng(1)
signs = rng.choice([-1, 1], size=(10_000, len(gap)))   # one row of random signs per shuffle
shuffled = (signs * gap).mean(axis=1)
np.mean(np.abs(shuffled) >= abs(gap.mean()))           # the p-value
```
```r [R]
set.seed(1)
shuffled <- replicate(10000, mean(sample(c(-1, 1), length(gap), replace = TRUE) * gap))
mean(abs(shuffled) >= abs(mean(gap)))                  # the p-value
```
:::

![Mean gaps when the signs are flipped at random. English: the observed 0.10 is well inside what chance gives. Mathematics: the observed 0.58 is far outside](/img/week-3/sign-flip.svg)

- **Mathematics:** none of the 10 000 shuffles gives a mean gap as large as 0.58; the largest is
  0.28. So $p < 0.0001$: chance is a very unlikely explanation.
- **English:** the mean gap is 0.10, and about 13% of the shuffles give one at least as large,
  $p \approx 0.13$. The bootstrap interval is about −0.03 to 0.23 points.

What does the English result mean? **Not** that girls and boys get the same grades in English. It
means the data can’t tell: they are consistent with boys ahead by a hair, and with girls ahead by
up to a quarter of a point. A large p-value is an absence of evidence, not evidence of absence.

### Testing 17 subjects

We ran the test in every subject. With 17 tests at the 0.05 level, if no subject had a real gap,
we would expect almost one to come out “significant” by chance ($17 \times 0.05 = 0.85$; see
[statistics section 8](/statistics#_8-traps)). Here 16 of the 17 have $p < 0.0001$, far beyond
what chance among 17 tests gives, so the number of tests does not change the conclusion. It
would if the p-values were near 0.05: then report how many tests you ran, not just the ones that
came out below.

### Choosing after looking

“Arjeplog has the largest gender gap in mathematics” would make a good headline. But we found it
by looking through 287 municipalities for the largest, and the funnel plot shows that the
largest is almost always one of the smallest, where chance alone gives big gaps. A claim picked
out *because* it was extreme needs new data to confirm it.

The same goes for decisions. Leaving out six subjects, choosing the mean or the median, or
calling a value an outlier: decide them for a reason you could state before seeing the result,
and check that the answer doesn't depend on them. Here the six subjects were chosen by their
numbers of pupils, and the median and the mean give the same picture.

### Writing it up

> In year 6 in 2018/19, girls had higher mean grades than boys in 16 of 17 subjects, in a typical
> municipality. The gap was largest in art and Swedish, about one grade step (2.5 points), and
> smallest in English, where the data show no clear difference (mean gap 0.10 points, 95%
> interval −0.03 to 0.23). In mathematics girls were ahead by 0.58 points (95% interval 0.45 to
> 0.70), about a quarter of a grade step. The gaps in single small municipalities vary a lot by
> chance and say little on their own. Grades are teachers' assessments, not test scores, so a
> gap in grades can reflect grading as well as knowledge. The data cover one school year, and
> one municipality, Dorotea, is missing.

## Common pitfalls

- **The dot in a regex.** `.` matches anything. Write `\.`, or use `regex=False` /
  `fixed = TRUE`.
- **Silent conversion.** `errors="coerce"` and `as.numeric` turn anything unexpected into a
  missing value without telling you. Mark the codes you expect, convert the rest, and check that
  nothing else became missing.
- **Losing rows when reshaping.** Check the number of rows after every pivot and filter.
- **Dropping missing values without asking why.** If they are missing for a reason, the rows you
  keep are not a fair sample. Say who you dropped and what it does.
- **Removing outliers because they are inconvenient.** Check whether they are possible; keep the
  real ones.
- **Trusting the extremes of small groups.** The highest and the lowest are often just the
  smallest.

## Check your understanding

1. Which regex matches a value that is exactly two dots? Why does `..` on its own not work?
2. In a survey about income, people with high incomes more often refuse to answer. Which kind
   of missing is that? What happens to the mean income if you drop them?
3. A table has the columns `municipality`, `girls_2018`, `boys_2018`, `girls_2019`,
   `boys_2019`. What are the variables? Sketch the long table.
4. Why is “Arjeplog has the largest gap” a weak headline, even though the number is correct?
5. The sign-flip test gives $p \approx 0.13$ for English. Does that show that girls and boys
   get the same grades in English? What does the interval add?
6. Write an assertion that the column `age` is between 0 and 120, ignoring missing values.

## Your task

Do [HW3](/homework/3): stroke and smoking, a dataset with missing values, an “Unknown” category
and a confounder.

## Further reading

- [R for Data Science (2e)](https://r4ds.hadley.nz): chapters 5 (data tidying, with
  pivoting), 10 (exploratory data analysis), 15 (regular expressions) and 18 (missing values).
- [Python for Data Analysis (3e)](https://wesmckinney.com/book/): chapter 7 (data cleaning:
  missing data, outliers, strings and regular expressions) and section 8.3 (reshaping and
  pivoting).
- [Regular expression HOWTO](https://docs.python.org/3/howto/regex.html) (Python), and
  [regex101.com](https://regex101.com) to try patterns out.
- Stef van Buuren, [Flexible Imputation of Missing Data](https://stefvanbuuren.name/fimd/),
  chapter 1: why missing values matter, and the three kinds.
- Data: [Skolverket, statistics on grades in year 6](https://www.skolverket.se/statistik-och-utvarderingar/statistik-om-forskola-och-skola).
  Skolverket's official statistics are free to use.
