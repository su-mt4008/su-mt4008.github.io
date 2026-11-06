---
outline: 2
---

# Data from the Web

**This week** you learn to collect data yourself: from an **API**, a web address that answers
with data instead of a page, and, when there is no API, by **scraping** a table from a web page.
This is the **Data** step of the cycle, and it comes with new duties: download politely, keep a
copy of exactly what you got, write down where it came from and under which licence, and think
about who is in the data and who is not.

**By the end of the week you can**

- read an API's URL, send a request from Python or R, and turn the JSON answer into a table;
- fetch every page of a result that comes in pages;
- download politely, and save the raw responses so your report never needs the internet;
- keep an API key out of Git;
- read a table from a web page, and say when you should not;
- record the source, query, date and licence of every file;
- say who the data leave out, and write that up as a limitation.

**How to use this page.** Read it from top to bottom with VS Code open, and run the code in a
scratch folder. You need two packages that are not in the template. Python: `uv add requests lxml`.
R: `renv::install(c("httr2", "rvest"))`, then `renv::snapshot()` (`jsonlite` is already there).
Every request on this page was made on 6 November 2026, and the files it saved are here too, so
you can follow along without calling anything:
[page 1](/data/week-5/nobel-physics-laureates-000.json),
[page 2](/data/week-5/nobel-physics-laureates-100.json),
[page 3](/data/week-5/nobel-physics-laureates-200.json) of the Nobel data,
<a href="/data/week-5/wikipedia-municipalities-of-sweden.html" download>the Wikipedia page</a> and
[the SCB table](/data/week-5/scb-population-2025.csv). Put them in `data/raw/`. Then do [HW5](/homework/5).

**Also read this week:** [Statistics: the basics](/statistics), sections
[2](/statistics#_2-data-are-observations-of-random-variables) (what it means to treat your data
as observations) and [9](/statistics#_9-writing-it-up) (how to write up an estimate, its
uncertainty and what it can't tell you). In HW5 you choose the data yourself, so you also have to
argue what they stand for.

## The example: how old are Nobel laureates in physics?

Most of this page uses one source, the **Nobel Prize API**, run by Nobel Prize Outreach. The
question:

> **Are physicists older when they receive the Nobel Prize today than a century ago, and by how
> much?**

The Nobel Prize website shows each laureate on a page of its own; nobody wants to copy 230 pages
by hand. The API gives the same facts as data.

## What an API is

An **API** (application programming interface) is, for us, a web address that returns data
instead of a web page. Your code sends a **request**, and the server sends back a **response**.
Paste this into your browser:

```text
https://api.nobelprize.org/2.1/laureates?nobelPrizeCategory=phy&limit=2
```

The address has three parts:

| Part | Here | What it is |
|---|---|---|
| **base URL** | `https://api.nobelprize.org/2.1` | the API, version 2.1 |
| **endpoint** | `/laureates` | which kind of thing you ask for |
| **parameters** | `?nobelPrizeCategory=phy&limit=2` | your query: `name=value` pairs after `?`, joined by `&` |

The API's documentation lists the endpoints and the parameters each one accepts. Read it first:
for this one, it is at [nobelprize.org/about/developer-zone-2](https://www.nobelprize.org/about/developer-zone-2/).

Your browser sent a **GET** request, the kind that only asks for something. Every response starts
with a **status code**, which says whether it worked:

| Code | Meaning | What to do |
|---|---|---|
| **200** | OK | read the body |
| **400** | bad request | a parameter is wrong; read the documentation |
| **401**, **403** | not allowed | you need a key, or the server refuses your kind of request |
| **404** | not found | the endpoint is misspelled, or moved |
| **429** | too many requests | slow down, and wait before trying again |
| **500**–**599** | the server failed | try again later |

The **body** of the response is the data, here as **JSON** (JavaScript Object Notation). This is
the start of what you got, shortened:

```json
{
  "laureates": [
    {
      "id": "102",
      "knownName": {"en": "Aage N. Bohr"},
      "gender": "male",
      "birth": {"date": "1922-06-19", "place": {"…": "…"}},
      "nobelPrizes": [
        {"awardYear": "1975", "category": {"en": "Physics"}, "portion": "1/3", "…": "…"}
      ]
    },
    "…"
  ],
  "meta": {"offset": 0, "limit": 2, "nobelPrizeCategory": "phy", "count": 230, "…": "…"},
  "links": {"…": "…"}
}
```

JSON has only a few building blocks: **objects** `{…}` with named fields, **arrays** `[…]` of
values, and text, numbers, `true`/`false` and `null`. Python reads an object as a dictionary and an
array as a list; R reads both as lists. Note that `"awardYear": "1975"` is **text**, in quotes,
not a number: you will have to convert it.

**Try it.** Change `limit=2` to `limit=5` in the browser. Then misspell the category,
`nobelPrizeCategory=physics`. What happens to `count`?

## One request from code

:::code-group
```python [Python]
import requests

URL = "https://api.nobelprize.org/2.1/laureates"
HEADERS = {"User-Agent": "MT4008 course example (Stockholm University)"}

r = requests.get(URL, params={"nobelPrizeCategory": "phy", "limit": 2},
                 headers=HEADERS, timeout=30)
r.raise_for_status()      # stop with an error if the status is 4xx or 5xx
r.status_code             # 200
r.url                     # the full URL that was sent
page = r.json()           # JSON text -> dictionaries and lists
page["meta"]["count"]     # 230 physics laureates in all
len(page["laureates"])    # 2: this page only
page["laureates"][0]["knownName"]["en"]   # 'Aage N. Bohr'
```
```r [R]
library(httr2)

url <- "https://api.nobelprize.org/2.1/laureates"
resp <- request(url) |>
  req_url_query(nobelPrizeCategory = "phy", limit = 2) |>
  req_user_agent("MT4008 course example (Stockholm University)") |>
  req_perform()                 # stops with an error if the status is 4xx or 5xx
resp_status(resp)               # 200
resp_url(resp)                  # the full URL that was sent
page <- resp_body_json(resp)    # JSON text -> nested lists
page$meta$count                 # 230 physics laureates in all
length(page$laureates)          # 2: this page only
page$laureates[[1]]$knownName$en   # "Aage N. Bohr"
```
:::

Four habits are already in these few lines:

- **Let the library build the URL.** Pass the parameters as a dictionary (`params=`) or with
  `req_url_query()`; it handles spaces, `&` and `å` for you.
- **Stop on errors.** `raise_for_status()` turns a 404 or 500 into an error you see at once,
  instead of an error page that you read as data three steps later. httr2 does this by default.
- **Set a timeout**, so a server that never answers doesn't hang your script forever.
- **Say who you are** with a User-Agent header. More on that [below](#be-polite).

**Check that the API understood you.** If you misspell the category as `physics`, the API does
not complain: it returns status 200 and *all* 1 028 laureates in every category, and
`meta` no longer mentions a category. An unknown parameter value is often silently ignored.
Compare `meta` with what you asked for, and the count with what you expect.

## From JSON to a table

You want one row per **laureate and physics prize**, with the few fields the question needs. The
JSON is nested (a list of laureates, each with a list of prizes), so walk through it with two
loops and keep what you need:

:::code-group
```python [Python]
import json
from pathlib import Path

import pandas as pd

rows = []
for path in sorted(Path("data/raw").glob("nobel-physics-laureates-*.json")):
    page = json.loads(path.read_text(encoding="utf-8"))
    for person in page["laureates"]:
        for prize in person["nobelPrizes"]:
            if prize["category"]["en"] != "Physics":
                continue          # Marie Curie's 1911 prize is in chemistry
            rows.append({
                "id": person["id"],
                "name": person["knownName"]["en"],
                "birth": person["birth"]["date"],
                "year": int(prize["awardYear"]),
            })
prizes = pd.DataFrame(rows)
prizes.shape               # (231, 4)
prizes["id"].nunique()     # 230
```
```r [R]
library(jsonlite)
library(dplyr)

rows <- list()
for (path in sort(Sys.glob("data/raw/nobel-physics-laureates-*.json"))) {
  page <- fromJSON(path, simplifyVector = FALSE)
  for (person in page$laureates) {
    for (prize in person$nobelPrizes) {
      if (prize$category$en != "Physics") next   # Marie Curie's 1911 prize is in chemistry
      rows[[length(rows) + 1]] <- tibble(
        id = person$id,
        name = person$knownName$en,
        birth = person$birth$date,
        year = as.integer(prize$awardYear)
      )
    }
  }
}
prizes <- bind_rows(rows)
dim(prizes)                # 231 4
n_distinct(prizes$id)      # 230
```
:::

This reads the pages from `data/raw/`, which the next sections fill. Two things the counts tell
you, and that you would have missed by counting people:

- **John Bardeen won the physics prize twice** (1956 and 1972), so 230 people give 231 rows.
  For the question “how old were they when they won”, one row per prize is right.
- **Marie Curie is in the physics list, but her record holds two prizes**, physics 1903 and
  chemistry 1911. Without the `if`, her chemistry prize would count as a physics prize.

For flat JSON, a list of records with no lists inside, `pd.json_normalize()` or
`fromJSON(simplifyVector = TRUE)` gives a table in one step. Nested JSON like this is clearer with
explicit loops: you see exactly what one row is.

## Paging

APIs rarely send everything at once. This one sends at most `limit` laureates per response,
starting at `offset`. The total is in `meta.count`, so you ask for page after page:

| Request | `offset` | `limit` | You get |
|---|---|---|---|
| 1 | 0 | 100 | laureates 1–100 |
| 2 | 100 | 100 | laureates 101–200 |
| 3 | 200 | 100 | laureates 201–230 |

Stop when `offset` reaches `count`. Other APIs page in other ways: a `page` number and a total
number of `pages` (the World Bank), or a `next` link to the next page (Kolada). The idea is the
same: **loop until the API says there is no more, and check that you got as many rows as it said
there are.**

::: warning Don't follow links you haven't tested
This API also gives a `links.next` address in every response. On 6 November 2026 it pointed to
`http://nobel-external-api-app.azurewebsites.net/…`, an internal address that answers 403
Forbidden. Building the next `offset` yourself works; following the link does not. Whatever you
get from an API, look at it before your code relies on it.

In R, `next` is a reserved word (it skips to the next loop round), so `page$links$next` is a
syntax error. Write `page$links[["next"]]`.
:::

## Be polite

An open API is a shared resource that someone pays to run. Use it like a guest:

- **Pause between requests.** One request a second is plenty for a homework. Never send requests
  in parallel.
- **Ask for what you need, once.** Bigger pages mean fewer requests; and a file you have already
  downloaded doesn't need downloading again (next section).
- **Say who you are.** A User-Agent header tells the server who is calling. Use something like
  `"MT4008 course example (Stockholm University)"`; don't put your personal e-mail address in code
  you share. Some servers refuse requests without one: Wikipedia answers `python-requests`'
  default User-Agent with 403 Forbidden.
- **Respect the limits.** SCB's API allows 30 requests per 10 seconds. If you get **429**, stop,
  wait (the `Retry-After` header, when there is one, says how many seconds), and slow down. In R,
  `req_throttle()` and `req_retry()` do this for you.
- **Read the terms of use.** The Nobel Prize API's terms say:
  *“Applications shall be constructed in a manner which minimizes the capacity burden of the API.
  Consider using a local cache instead of performing many API calls.”*

## Cache the raw responses

A report that calls an API every time it renders has four problems: it fails without internet; it
hammers the server; the answer can change under you (a new laureate in October, a corrected
number); and the reproducibility **check** on GitHub would call the API on every push. So split the
work in two:

1. **A fetch script** downloads every response once and saves it, **exactly as received**, in
   `data/raw/`. If a file is already there, it skips it.
2. **The report** reads only the files in `data/raw/`. It never touches the internet, so it
   renders anywhere, and the check never calls the API.

:::code-group
```python [Python: fetch.py]
# Download the physics laureates from the Nobel Prize API, once.
import json
import time
from pathlib import Path

import requests

URL = "https://api.nobelprize.org/2.1/laureates"
HEADERS = {"User-Agent": "MT4008 course example (Stockholm University)"}
RAW = Path("data/raw")
LIMIT = 100                      # laureates per page

RAW.mkdir(parents=True, exist_ok=True)
offset, count = 0, None
while count is None or offset < count:
    path = RAW / f"nobel-physics-laureates-{offset:03d}.json"
    if not path.exists():        # already downloaded: don't ask again
        params = {"nobelPrizeCategory": "phy", "limit": LIMIT, "offset": offset}
        r = requests.get(URL, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()     # stop with an error on 4xx and 5xx
        path.write_bytes(r.content)   # exactly as received
        print("saved", path, r.url)
        time.sleep(1)            # be polite: one request per second
    page = json.loads(path.read_text(encoding="utf-8"))
    count = page["meta"]["count"]     # how many laureates there are in total
    offset += LIMIT
```
```r [R: fetch.R]
# Download the physics laureates from the Nobel Prize API, once.
library(httr2)
library(jsonlite)

url <- "https://api.nobelprize.org/2.1/laureates"
limit <- 100                       # laureates per page

dir.create("data/raw", recursive = TRUE, showWarnings = FALSE)
offset <- 0
count <- Inf
while (offset < count) {
  path <- sprintf("data/raw/nobel-physics-laureates-%03d.json", offset)
  if (!file.exists(path)) {        # already downloaded: don't ask again
    resp <- request(url) |>
      req_url_query(nobelPrizeCategory = "phy", limit = limit, offset = offset) |>
      req_user_agent("MT4008 course example (Stockholm University)") |>
      req_perform()                # stops with an error on 4xx and 5xx
    writeBin(resp_body_raw(resp), path)   # exactly as received
    message("saved ", path)
    Sys.sleep(1)                   # be polite: one request per second
  }
  page <- fromJSON(path, simplifyVector = FALSE)
  count <- page$meta$count         # how many laureates there are in total
  offset <- offset + limit
}
```
:::

Run it once with `uv run python fetch.py` or `Rscript fetch.R`. It saves three files (395, 401 and
121 KB). Run it again and it does nothing, because the files exist. Both versions save
byte-for-byte the same files.

Why save the **raw** response, not a cleaned CSV? Because cleaning is a decision, and decisions
belong in code that a reviewer can read (week 1's first habit). The raw file is the evidence; the
cleaning in your report is the argument.

To refresh the data, delete the files and run the script again, all at once: pages fetched on
different days may not fit together, because the data can change in between.

You could instead put the download in a chunk of the report, guarded by “only if the file doesn't
exist”. It works, but a separate script is clearer: the report shows the analysis, and the
script shows exactly what was asked of the API.

## Write down where it came from

Six months from now, neither you nor a reader will remember which query made which file. Record it
next to the data, in `data/raw/README.md`:

| File | Source | Query | Licence | Retrieved |
|---|---|---|---|---|
| `nobel-physics-laureates-000.json`, `-100`, `-200` | Nobel Prize API 2.1, `https://api.nobelprize.org/2.1/laureates` | `nobelPrizeCategory=phy&limit=100&offset=0,100,200` | CC0 | 2026-11-06 |

This is the data's **provenance**: what was asked, of whom, and when. With it, anyone can repeat
the download, and see why their numbers differ if the source has changed since.

### Licences

Data on the web is not automatically free to use. Look for the licence, and write it down:

| Licence | You may | You must | Examples |
|---|---|---|---|
| **CC0** (public domain) | use it for anything | nothing (citing the source is still good practice) | Nobel Prize API, SCB |
| **CC BY 4.0** | use it for anything | credit the source | SMHI, the World Bank |
| **CC BY-SA 4.0** | use it for anything | credit the source, and share what you make from it under the same licence | Wikipedia |
| **Terms of use**, no standard licence | what the terms say | read them | many company APIs |
| **No licence stated** | look, but don't republish | ask the owner | most web pages |

## API keys

Some APIs want a **key**: a long string that identifies you, so that the provider can count your
requests. Trafiklab (Swedish public transport) is one; you get a free key by registering. A key is
like a password: **it never goes into Git.** A repository is easy to copy, and keys pushed to
GitHub are found by bots within minutes.

Put the key in a file called `.env` in the repository folder:

```text
TRAFIKLAB_KEY=paste-your-key-here
```

Add the line `.env` to the file `.gitignore`, so Git never sees it, and **commit `.gitignore`
before you create `.env`**. Then read the key from the environment:

:::code-group
```python [Python]
import os

key = os.environ["TRAFIKLAB_KEY"]      # from the environment, never typed in the code
r = requests.get(
    "https://api.resrobot.se/v2.1/location.name",
    params={"input": "Universitetet", "format": "json", "accessId": key},
    headers=HEADERS, timeout=30,
)
```
```r [R]
readRenviron(".env")                   # loads TRAFIKLAB_KEY=... into the environment
key <- Sys.getenv("TRAFIKLAB_KEY")
resp <- request("https://api.resrobot.se/v2.1/location.name") |>
  req_url_query(input = "Universitetet", format = "json", accessId = key) |>
  req_user_agent("MT4008 course example (Stockholm University)") |>
  req_perform()
```
:::

In Python, run the script with `uv run --env-file .env python fetch.py`, which puts the contents
of `.env` into the environment. Because only the fetch script needs the key and the report reads
the cached files, the check on GitHub never needs it.

If you do commit a key by mistake, **revoke it** on the provider's website and get a new one.
Deleting the file in a new commit is not enough: the old commit still holds it.

## Answering the question

Back to the laureates. With the table from [From JSON to a table](#from-json-to-a-table), the age
at the prize is the award year minus the birth year.

**Cleaning.** Why not use the full birth date? Because four laureates (Saul Perlmutter, and the
three 2025 laureates John Clarke, Michel H. Devoret and John M. Martinis) have birth dates like
`1942-00-00`: the API knows the year but not the day. `pd.to_datetime()` fails on them, and
`as.Date()` gives `NA`. Using years for everyone keeps all 231 prizes, and the age is off by at
most one year, which doesn't matter for this question. Write that decision down.

:::code-group
```python [Python]
import numpy as np

prizes["age"] = prizes["year"] - prizes["birth"].str[:4].astype(int)
prizes["period"] = pd.cut(prizes["year"], bins=[1900, 1950, 2000, 2026],
                          labels=["1901–1950", "1951–2000", "2001–2026"])
summary = (
    prizes.groupby("period", observed=True)["age"]
    .agg(n="size", mean="mean", median="median", sd="std")
)
summary["low"] = summary["mean"] - 1.96 * summary["sd"] / np.sqrt(summary["n"])
summary["high"] = summary["mean"] + 1.96 * summary["sd"] / np.sqrt(summary["n"])
```
```r [R]
prizes <- prizes |>
  mutate(age = year - as.integer(substr(birth, 1, 4)),
         period = cut(year, breaks = c(1900, 1950, 2000, 2026),
                      labels = c("1901–1950", "1951–2000", "2001–2026")))
summary <- prizes |>
  group_by(period) |>
  summarise(n = n(), mean = mean(age), median = median(age), sd = sd(age)) |>
  mutate(low = mean - 1.96 * sd / sqrt(n), high = mean + 1.96 * sd / sqrt(n))
```
:::

| Prizes awarded | n | Mean age | Median | sd | 95% interval for the mean |
|---|---|---|---|---|---|
| 1901–1950 | 54 | 46.8 | 45.5 | 10.2 | 44.1 to 49.5 |
| 1951–2000 | 108 | 55.5 | 54.0 | 12.1 | 53.2 to 57.8 |
| 2001–2026 | 69 | 70.1 | 72.0 | 13.9 | 66.8 to 73.4 |

![Age at the Nobel Prize in Physics against the year of the prize, one grey dot per laureate, with the mean of each period and its 95% interval in red: 47, 55 and 70 years](/img/week-5/nobel-age.svg)

The youngest was Lawrence Bragg, 25 in 1915; the oldest Arthur Ashkin, 96 in 2018. Since 2001,
more than half of the laureates (54%) were 70 or older; before 1951, one in 54 was.

**Are these a sample?** The table holds every physics laureate there has ever been, so in one
sense there is nothing to estimate. But the question is not about these 231 people; it is about
how the prize *works* in each period. As in [statistics section 2](/statistics#_2-data-are-observations-of-random-variables),
treat each age as an observation of a random variable whose mean is “the typical age at the prize
in that period”. A few different decisions by the committee would have given other laureates and
other ages; the interval says how much the mean could move because of that. The difference between
the last and the first period, with its interval as in
[comparing the two periods](/statistics#comparing-the-two-periods):
**23.3 years (95% interval 19.0 to 27.5)**.

### Who is in the data?

Before you write the conclusion, ask what process put each row into the data, and who it left
out. Data you collect from the web are almost never a random sample of anything.

- **Only winners.** The API holds laureates, not the physicists who were nominated and never won.
  Nominations are kept secret for 50 years, so there is no API for the recent ones.
- **Only the living.** Since 1974 the prize cannot be given to someone who has died. If the wait
  for the prize gets longer, more of the people who deserve it die first, and they are missing
  from the later periods. Those who remain are, by construction, the ones who lived long.
- **The prize is not the discovery.** The API gives the year of the prize, not the year of the
  work. Higher ages could mean that physicists make their discoveries later in life, or that they
  wait longer for the prize. These data can't tell the two apart.

### Writing it up

Statistics section 9's shape (the estimate, its uncertainty, what it can't tell you) fits
directly:

> Physics laureates of 2001–2026 were on average **70.1 years** old when they received the prize,
> **23.3 years older** than those of 1901–1950 (**95% interval 19.0 to 27.5 years**). Ages vary a
> lot within each period (standard deviation 10–14 years). The data hold only the prize year, not
> the year of the prize-winning work, so they cannot say whether physicists now make their
> discoveries later or wait longer to be recognised; and since only living people can receive the
> prize, those who waited longest and died are not in the data.

## Scraping a web page

When there is no API and no file to download, the data may still be on a web page.
**Scraping** means downloading the page's HTML and pulling the data out of it. Tables are the
easy case: HTML marks them with `<table>`, `<tr>` (row) and `<td>` (cell), and both pandas and
rvest turn them into data frames.

Our example: the table of Sweden's 290 municipalities and their populations on
[Wikipedia](https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden). Wikipedia's text is
licensed CC BY-SA 4.0, so you may use it if you credit it and share alike. Download the page once,
as with the API, then parse the saved file:

:::code-group
```python [Python]
import io
from pathlib import Path

import pandas as pd
import requests

URL = "https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden"
HEADERS = {"User-Agent": "MT4008 course example (Stockholm University)"}
path = Path("data/raw/wikipedia-municipalities-of-sweden.html")

if not path.exists():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    path.write_bytes(r.content)

html = path.read_text(encoding="utf-8")
tables = pd.read_html(io.StringIO(html), match="Seat", converters={"Code": str})
municipalities = tables[0]
municipalities.shape        # (290, 7)
```
```r [R]
library(httr2)
library(rvest)

url <- "https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden"
path <- "data/raw/wikipedia-municipalities-of-sweden.html"

if (!file.exists(path)) {
  request(url) |>
    req_user_agent("MT4008 course example (Stockholm University)") |>
    req_perform(path = path)        # save the body straight to the file
}

page <- read_html(path)
table <- html_element(page, "table.wikitable")      # the first table with class "wikitable"
municipalities <- html_table(table, convert = FALSE) # every column as text
municipalities$Population <- as.numeric(gsub(",", "", municipalities$Population))
dim(municipalities)         # 290 7
```
:::

`pd.read_html()` returns a *list* of every table on the page; `match="Seat"` keeps only the tables
that contain that word. Wrap the HTML text in `io.StringIO`: given a plain string, pandas 3 takes it
for a file name and fails with `File name too long`. In R, `html_element()` picks the table with a **CSS selector**:
`table.wikitable` means “a `<table>` with the class `wikitable`”. To find the selector for any
element, right-click it in your browser and choose **Inspect**.

Then check what you got, as in week 2. Three things went wrong here before the code above fixed
them:

- **Codes lost their leading zero.** Municipality codes are four digits: Alvesta is `0764`. Read
  as numbers, it becomes `764`, and 90 of the 290 codes no longer match the codes other sources
  use. Read identifiers as text: `converters={"Code": str}`, `convert = FALSE`.
- **Numbers with commas.** `32,620` is text until you remove the comma. pandas does that by
  default (`thousands=","`); in R we did it with `gsub()`.
- **Junk in the column names.** The last column's name contains a non-breaking space in Python
  (`'Land\xa0area (km2)'`), and in R a piece of the page's style sheet. Print the names, and
  rename the columns you keep.

The page you download today may differ from ours. Wikipedia keeps every version: ours is revision
[1362817780](https://en.wikipedia.org/w/index.php?title=List_of_municipalities_of_Sweden&oldid=1362817780)
(you find the number in the HTML as `"wgRevisionId":1362817780`). Record it in your README.

### Prefer the source

The page says its populations are from Statistics Sweden (SCB) for 2025. SCB has an open API (CC0)
with the same numbers, so let us compare. Its PxWebApi 2 takes the table's ID and one
`valueCodes[…]` parameter per variable:

:::code-group
```python [Python]
URL = "https://statistikdatabasen.scb.se/api/v2/tables/TAB628/data"
PARAMS = {
    "lang": "en",
    "valueCodes[Region]": "*",                # every region
    "valueCodes[Kon]": "1+2",                 # men and women together
    "valueCodes[ContentsCode]": "BE0101U2",   # population
    "valueCodes[Tid]": "2025",
    "outputFormat": "csv",
}
path = Path("data/raw/scb-population-2025.csv")
if not path.exists():
    r = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=30)
    r.raise_for_status()
    path.write_bytes(r.content)

scb = (
    pd.read_csv(path, dtype={"Region": str})
    .query("Region.str.len() == 4")           # municipalities have four-digit codes
    .rename(columns={"Region": "Code", "BE0101U2 2025": "scb"})
)
both = municipalities.merge(scb, on="Code", validate="one_to_one")
both.loc[both["Population"] != both["scb"], ["Municipality", "Population", "scb"]]
```
```r [R]
library(readr)

path <- "data/raw/scb-population-2025.csv"
if (!file.exists(path)) {
  request("https://statistikdatabasen.scb.se/api/v2/tables/TAB628/data") |>
    req_url_query(
      lang = "en",
      "valueCodes[Region]" = "*",               # every region
      "valueCodes[Kon]" = "1+2",                # men and women together
      "valueCodes[ContentsCode]" = "BE0101U2",  # population
      "valueCodes[Tid]" = "2025",
      outputFormat = "csv"
    ) |>
    req_user_agent("MT4008 course example (Stockholm University)") |>
    req_perform(path = path)
}
scb <- read_csv(path, col_types = cols(Region = col_character())) |>
  filter(nchar(Region) == 4) |>                 # municipalities have four-digit codes
  rename(Code = Region, scb = `BE0101U2 2025`)
both <- inner_join(municipalities, scb, by = "Code")
both |> filter(Population != scb) |> select(Municipality, Population, scb)
```
:::

All 290 codes match, and 288 populations agree. Two do not:

| Municipality | Wikipedia | SCB |
|---|---|---|
| Huddinge | 144 686 | 114 686 |
| Säter | 12 222 | 11 222 |

Two typos, one digit each, and Huddinge's is 30 000 people. Summed over Sweden, the scraped table
says 10 636 520; SCB says 10 605 520. Nothing on the page warns you. Copied data collects copying
errors, so **when the original source has an API or a download, use that, not a page that quotes
it.** (Joining tables on a key like `Code` is [week 4](/lectures/week-4).)

To find a table's ID in SCB's API, search at
`https://statistikdatabasen.scb.se/api/v2/tables?lang=en&query=population`, and see what a table
contains at `…/tables/TAB628/metadata?lang=en`.

### When not to scrape

Scraping is the last resort, not the first. Before you scrape, check, in this order:

1. **Is there an API or a file to download?** Look for “API”, “open data” or “download” on the
   site. Often the page you see is itself filled from an API (your browser's developer tools,
   under **Network**, show it).
2. **Do the terms of use allow it?** Many sites forbid automated downloading. If they do, don't.
3. **What does `robots.txt` say?** Every site can publish rules for automated visitors at
   `/robots.txt`, e.g. [en.wikipedia.org/robots.txt](https://en.wikipedia.org/robots.txt). Its
   `Disallow:` lines list the paths that programs should stay out of. Wikipedia's article pages
   (`/wiki/…`) are allowed; `/w/` is not, for general robots.
4. **Is it personal data?** Then see the next section; usually the answer is no.

And keep it small: a few pages, one at a time, with pauses. Scraping is also fragile. When the site
changes its layout, your code breaks, which is one more reason to keep the raw HTML you used.

## Personal data

The laureate records hold names, birth dates, birthplaces and gender. That is **personal data**:
anything about an identifiable person, even if it is public. In Sweden and the EU, the GDPR
governs how it may be collected and stored. You may use it for a purpose like ours, but the rules
come down to habits you should have anyway:

- **Don't collect what you don't need.** The question needs a birth year and a prize year; the
  analysis keeps those and nothing else.
- **Don't collect data about private people.** Public figures in an official register are one
  thing; scraping profiles, comments or reviews written by ordinary people is another, and not
  something to do for a homework.
- **Don't combine sources to identify people**, and don't publish personal data that you did not
  get from an open, licensed source.

For HW5, choose data about places, things, events or groups, not about private individuals.

## Common pitfalls

- **Calling the API from the report.** The check calls it on every push, and the report breaks the
  day the API changes. Fetch in a script, read the cache in the report.
- **Getting the first page only.** 100 rows when there are 230. Compare your row count with the
  total the API reports.
- **A misspelled parameter.** The API ignores it and returns something else, with status 200.
  Check `meta`, or whatever the API echoes back.
- **Numbers as text.** JSON values like `"1975"` and HTML cells like `"32,620"` are text until
  you convert them.
- **Codes read as numbers.** `0764` becomes `764`, and joins fail quietly.
- **A key in the code.** It is in Git's history for good. Use `.env`, and revoke a key you leaked.
- **No provenance.** A file in `data/raw/` with no URL, query, date or licence next to it.

## Check your understanding

1. In `https://api.worldbank.org/v2/country/SE/indicator/SP.POP.TOTL?format=json&per_page=50`,
   what are the base URL, the endpoint and the parameters?
2. An API answers your request with status 200 and 1 028 rows, though you expected 230. What do
   you check?
3. Why does the report read files from `data/raw/` rather than call the API? Give two reasons.
4. A classmate's fetch script contains `key = "a83f…"`. What do you write in your review, and
   what should they do now?
5. The physics laureates are all the laureates there are. Why does the page still give a
   confidence interval for the mean age?
6. Name one group of physicists the Nobel data leave out, and say how leaving them out could
   bias the answer.

## Your task

Do [HW5](/homework/5): ask your own question, collect the data from an open API, and go through
the whole cycle.

## Further reading

- [R for Data Science (2e)](https://r4ds.hadley.nz): chapter 23 (hierarchical data: JSON) and
  chapter 24 (web scraping), including its section on ethics and legalities.
- [httr2: Get started](https://httr2.r-lib.org/articles/httr2.html) ·
  [Requests: Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
  and [HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status).
- [Creative Commons: About the licences](https://creativecommons.org/licenses/).
- [IMY (the Swedish data protection authority): the GDPR](https://www.imy.se/en/organisations/data-protection/this-applies-accordning-to-gdpr/).
- Data: [Nobel Prize API](https://www.nobelprize.org/about/developer-zone-2/) and its
  [terms of use](https://www.nobelprize.org/about/terms-of-use-for-api-nobelprize-org-and-data-nobelprize-org/);
  [SCB's API](https://www.scb.se/en/services/open-data-api/).
