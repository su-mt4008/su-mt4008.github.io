---
outline: 2
---

# Text as Data: Extracting Structure with LLMs

**This week** you learn to turn free text, such as reviews, job ads or open survey answers,
into a table with fixed columns, using a language model (an LLM) that runs on your own laptop.
The model is a measuring instrument, and like any instrument it can be wrong. So most of this
page is about checking it: comparing its answers with answers you trust, putting an interval
on how often it agrees, and setting it up so that someone else can rerun what you did.

**By the end of the week you can**

- describe the table you want from a text as a schema: fields with fixed allowed values;
- run a local model over a few hundred texts with Ollama, from Python or R;
- explain why the extraction runs once, in its own script, and the report reads a saved file;
- check the model against a hand-coded random sample, and report its agreement with a 95%
  confidence interval;
- name what changes a model's answers (the model, its version, the prompt, the temperature),
  and pin each one;
- decide when text must not be sent to a hosted service.

**How to use this page.** Read it from top to bottom with VS Code open, and run the code as you
go: download [recipe-reviews.csv](/data/week-6/recipe-reviews.csv) into `data/raw/` in a scratch
folder first, so the paths below work. Running a model needs Ollama (below) and about 2 GB of
disk. If you can't install it, download the model's saved answers,
[llm-labels.csv](/data/week-6/llm-labels.csv), into `data/`: everything from
[Is the model right?](#is-the-model-right) on works with that file alone.

There is **no homework this week**: it is project time. Use what you learn here if your group's
data include text.

**Also read this week:** [Statistics: the basics](/statistics), section
[4](/statistics#_4-how-sure-are-you-standard-errors-and-confidence-intervals) again. An agreement
rate is a mean, and it gets an interval like any other mean.

## The example: what do reviewers think of a recipe?

The whole page uses one dataset: reviews of recipes on the cooking site Taste of Home, collected
by Ali, Matuszewski and Czupyt and published in the
[UCI Machine Learning Repository](https://doi.org/10.24432/C5FG95) under the CC BY 4.0 licence.
Each review is a short text and a rating from 1 to 5 stars.

> **Can a small language model on a laptop tell from the text alone what the reviewer thought of
> the recipe, and whether they changed it?**

The stars make this a good example to learn on: they let us check the model's answers about
the reviewer's opinion against what the reviewer said with the rating. In your own project there is usually
no such column, and you make the check yourself, by hand (see [below](#no-answer-key-code-a-sample-by-hand)).

The full dataset has 15 670 reviews with stars and at least 20 characters of text, and 84% of
them give 5 stars. A random sample would be almost all 5-star reviews, and would say little
about how the model handles unhappy ones. So the file for this week has **50 reviews for each
of 1 to 5 stars**, 250 in all, drawn at random with a fixed seed. We left out the user names
and ids: we don't need them, so we don't keep them. The script that made the file is
`scripts/week6_data.py` in the course repository.

## From text to a table

A language model reads text and writes text. Asked "what did this reviewer think?", it might
answer "They liked it overall, though the frosting was a problem", which is a fine sentence
and useless for counting. For analysis you want the same few columns for every text, each with
values you decide in advance:

| Field | Allowed values | Meaning |
|---|---|---|
| `sentiment` | `positive`, `mixed`, `negative` | what the reviewer thinks of the recipe |
| `made_it` | `true`, `false` | the reviewer says they cooked it |
| `changed_recipe` | `true`, `false` | the reviewer says they changed ingredients, amounts or steps |

This description of a table is called a **schema**. Ollama accepts it as a JSON schema and only
lets the model produce answers that fit it: no other fields, no other values, no chatty
sentence around them. This is **structured output**. For the review

> I also added a few dashes of "Old Bay". This was very good. I will be making it again.

the model returns `{"sentiment": "positive", "made_it": true, "changed_recipe": true}`: one row
of the table.

Choose the fields before you start, from your question, as you would design a questionnaire.
Prefer **fixed categories** over free text: you can count `positive`, `mixed` and `negative`,
but you can't count 250 different sentences. And write down what each value means: the
definitions go into the prompt, and into your report.

## Running a model on your laptop

We use [**Ollama**](https://ollama.com), a free program that downloads open models and runs
them on your own computer. Nothing you send it leaves your laptop, it costs nothing, and it
works offline.

1. **Install it.** On macOS or Windows, download the installer from
   [ollama.com/download](https://ollama.com/download); on Linux, follow the command on the same
   page. Ollama then runs in the background and listens on `http://localhost:11434`.
2. **Download a model**, in a terminal:

   ```bash
   ollama pull llama3.2:3b
   ```

   This is Meta's Llama 3.2 with 3 billion parameters: a 2.0 GB download that runs on an
   ordinary laptop without a graphics card. On a laptop with little memory, use `llama3.2:1b`
   (1.3 GB) instead; it is faster, and less accurate (see [below](#what-changes-the-answers)).
3. **Check that it works:**

   ```bash
   ollama run llama3.2:3b "Say hello in Swedish."
   ollama list        # the models you have, with their ID
   ```

There are newer and larger models in the [Ollama library](https://ollama.com/library). Any of
them will do, as long as you write down exactly which one you used. Avoid models whose name ends
in `:cloud`: those run on Ollama's servers, not on your laptop.

## The extraction script

The script reads the texts, sends them to the model one at a time with the prompt and the schema,
and saves the answers. Put the prompt in its own file, `prompts/reviews.txt`, so it is committed
and reviewed like code:

```text
You read reviews of recipes and fill in a form. Answer only from the review.

sentiment: what the reviewer thinks of the recipe.
  "positive" if they mainly like it, "negative" if they mainly dislike it,
  "mixed" if they like some things and dislike others, or are lukewarm.
made_it: true if the reviewer says or clearly implies that they cooked the recipe, false otherwise.
changed_recipe: true if the reviewer says they changed ingredients, amounts or steps, false otherwise.

Reply with JSON only: {"sentiment": ..., "made_it": ..., "changed_recipe": ...}
```

In Python, add the `ollama` package to your project first (`uv add ollama`); in R, install
`httr2` (`renv::install("httr2")`, then `renv::snapshot()`). Then, as `scripts/extract.py` or
`scripts/extract.R`:

:::code-group
```python [Python]
import json
from pathlib import Path

import ollama
import pandas as pd

MODEL = "llama3.2:3b"                       # the exact tag, never just "llama3.2"
OPTIONS = {"temperature": 0, "seed": 4008}  # the same answers every run
SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "mixed", "negative"]},
        "made_it": {"type": "boolean"},
        "changed_recipe": {"type": "boolean"},
    },
    "required": ["sentiment", "made_it", "changed_recipe"],
}
PROMPT = Path("prompts/reviews.txt").read_text()

reviews = pd.read_csv("data/raw/recipe-reviews.csv")
rows = []
for _, review in reviews.iterrows():
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},          # the instructions
            {"role": "user", "content": review["text"]},    # one review
        ],
        format=SCHEMA,
        options=OPTIONS,
    )
    answer = json.loads(response.message.content)  # {"sentiment": "positive", ...}
    rows.append({"review_id": review["review_id"], **answer})

pd.DataFrame(rows).to_csv("data/llm-labels.csv", index=False)
```
```r [R]
library(httr2)
library(readr)
library(dplyr)

model <- "llama3.2:3b"                         # the exact tag, never just "llama3.2"
options <- list(temperature = 0, seed = 4008)  # the same answers every run
schema <- list(
  type = "object",
  properties = list(
    sentiment = list(type = "string", enum = c("positive", "mixed", "negative")),
    made_it = list(type = "boolean"),
    changed_recipe = list(type = "boolean")
  ),
  required = c("sentiment", "made_it", "changed_recipe")
)
prompt <- read_file("prompts/reviews.txt")

ask <- function(text) {
  resp <- request("http://localhost:11434/api/chat") |>
    req_body_json(list(
      model = model, stream = FALSE, format = schema, options = options,
      messages = list(
        list(role = "system", content = prompt),   # the instructions
        list(role = "user", content = text)        # one review
      )
    )) |>
    req_perform() |>
    resp_body_json()
  as_tibble(jsonlite::fromJSON(resp$message$content))
}

reviews <- read_csv("data/raw/recipe-reviews.csv")
labels <- bind_rows(lapply(reviews$text, ask)) |>
  mutate(review_id = reviews$review_id, .before = 1)
write_csv(labels, "data/llm-labels.csv")
```
:::

What each piece is for:

- **The system message** holds the instructions, the same for every text; the user message
  holds one review. Each review is sent on its own, so the answer for one can't depend on
  the others.
- **`format`** is the schema. The R version sends the same request to Ollama's HTTP API that
  the Python package sends for you.
- **`temperature` 0** makes the model pick its most likely answer every time, instead of
  drawing at random; the **seed** fixes whatever randomness is left. Both are explained
  [below](#what-changes-the-answers).
- **`review_id`** goes into the output, so you can join the answers back to the texts.

On the laptop we used (a Mac with 24 GB memory), the 250 reviews took 77 seconds. Try it on
a handful first: `reviews.head(10)` or `head(reviews, 10)`.

**Try it.** Run the script on the first ten reviews and read the texts next to the answers.
Would you have answered the same?

## Run once, save, and let the report read the file

The GitHub check that renders your report can't run a language model: it has no Ollama, and a
model of 2 GB per run would make every check slow. And even if it could, you would not want the
numbers in your report to change each time it renders. So the extraction is a separate step:

```text
prompts/reviews.txt        the prompt, committed
scripts/extract.py         runs the model once (or extract.R); not run by the check
data/llm-labels.csv        the model's answers, committed
data/llm-labels.md         a note: model, ID, Ollama version, options, date
report.qmd                 reads data/llm-labels.csv; never calls the model
```

It is the same idea as saving the responses from an API to a file (week 5): the slow, outside
step runs once, its result is committed, and the report only reads files. Anyone with Ollama
can rerun `scripts/extract.py` and compare their file with yours; the README says how.

For the record next to the output, take the ID from `ollama list` and the version from
`ollama --version`. For this page: `llama3.2:3b`, ID `a80c4f17acd5`, Ollama 0.40.15,
temperature 0, seed 4008, run on 6 November 2026.

## Is the model right?

Treat the model's answers like readings from a new thermometer: before you use them, compare
them with readings you trust. Here we trust the stars, roughly: 1 or 2 stars should be a
`negative` review, 4 or 5 a `positive` one, and 3 stars could be anything.

Read the saved answers, join them to the reviews, and cross-tabulate:

:::code-group
```python [Python]
import numpy as np
import pandas as pd

reviews = pd.read_csv("data/raw/recipe-reviews.csv")
labels = pd.read_csv("data/llm-labels.csv")        # saved by scripts/extract.py
d = reviews.merge(labels, on="review_id")

pd.crosstab(d["stars"], d["sentiment"])
```
```r [R]
library(readr)
library(dplyr)

reviews <- read_csv("data/raw/recipe-reviews.csv")
labels <- read_csv("data/llm-labels.csv")          # saved by scripts/extract.R
d <- inner_join(reviews, labels, by = "review_id")

table(stars = d$stars, model = d$sentiment)
```
:::

| Stars | negative | mixed | positive |
|---|---|---|---|
| 1 | **46** | 0 | 4 |
| 2 | **40** | 7 | 3 |
| 3 | 24 | 15 | 11 |
| 4 | 4 | 5 | **41** |
| 5 | 2 | 0 | **48** |

![For each star rating, how many of the 50 reviews the model called negative, mixed or positive](/img/week-6/sentiment-by-stars.svg)

A table like this is called a **confusion table**: the counts on the diagonal (in bold) are
where the two agree, everything else is where they don't. Read off it:

- For 1, 2, 4 and 5 stars, the model mostly agrees with the stars.
- The model rarely says `mixed`: 27 times in 250. Even the 3-star reviews, which are lukewarm
  by definition, are mostly `negative` (24 of 50).

### The agreement rate, with an interval

Count agreement on the clear cases, the 200 reviews with 1–2 or 4–5 stars. The model agrees
on 175, so $\hat p = 175/200 = 0.875$.

That 87.5% comes from one sample of 200 reviews; another sample would have given a different
rate. How different? Write $X_i = 1$ if the model agrees on review $i$ and $0$ if not. Then
$\hat p$ is the mean of the $X_i$, and section 4 of the statistics page applies as it is. Each
$X_i$ is a Bernoulli variable with variance $p(1-p)$ (Probability Theory I), so

$$
\operatorname{SE} = \sqrt{\frac{\hat p(1-\hat p)}{n}} = \sqrt{\frac{0.875 \cdot 0.125}{200}} = 0.023,
\qquad
0.875 \pm 1.96 \cdot 0.023 = [0.829,\ 0.921].
$$

So on reviews like these, the model agrees with the stars on between 83% and 92% of them.

:::code-group
```python [Python]
clear = d[d["stars"] != 3].assign(
    expected=lambda x: np.where(x["stars"] >= 4, "positive", "negative")
)
agree = clear["sentiment"] == clear["expected"]
n, p = len(agree), agree.mean()
se = np.sqrt(p * (1 - p) / n)
print(f"{p:.3f} [{p - 1.96 * se:.3f}, {p + 1.96 * se:.3f}], n = {n}")
```
```r [R]
clear <- d |>
  filter(stars != 3) |>
  mutate(expected = if_else(stars >= 4, "positive", "negative"),
         agree = sentiment == expected)
clear |>
  summarise(n = n(), p = mean(agree)) |>
  mutate(se = sqrt(p * (1 - p) / n), low = p - 1.96 * se, high = p + 1.96 * se)
```
:::

**Say what it was measured on.** The rate depends on the mix of texts. Per star rating, the
model agrees on 46, 40, 41 and 48 of the 50 reviews with 1, 2, 4 and 5 stars. In the full data,
84% of the reviews give 5 stars, the easiest case, so the agreement there would come out higher than in
our balanced sample. Neither number is wrong; they answer different questions. In a report, say
what the sample was.

### Read the disagreements

A rate doesn't tell you *how* the model goes wrong. Print the 25 disagreements and read them
all; it takes ten minutes.

:::code-group
```python [Python]
clear.loc[~agree, ["stars", "sentiment", "text"]]
```
```r [R]
clear |> filter(!agree) |> select(stars, sentiment, text)
```
:::

Here they are of three kinds.

- **The model said `mixed` where the stars are 2 or 4**, 12 of the 25: "Everyone enjoyed it but
  mine was very dense" (4 stars). Often a fair reading: the "answer key" has no `mixed` for 2
  or 4 stars.
- **The star is the problem.** "This is fantastic, everyone loved it and yes I will definitely
  make this again." has 1 star. The model said `positive`, and it is right. The stars are a
  reasonable check, not the truth.
- **The text isn't a review.** Some are replies to other users ("@ buzzbombz, why would you give
  it 4 stars and then post a different recipe?", 5 stars, `negative`) or questions ("If I am
  allergic to soy, is there something I could substitute for it?", 1 star, `positive`). The
  schema has no answer for these, so the model picks one.

And some are plain mistakes: "This cake was delicious. Had a lot of trouble with the frosting
[…] will certainly change the frosting recipe." (2 stars) is `mixed` rather than `positive`.

Reading them tells you what to fix. Here, a field `is_review` (true/false) would let you drop
replies and questions before counting. But if you change the prompt or the schema, run the
model on **all** the texts again, and check it on **new** texts: a prompt you tuned until it
agreed with these 200 will look better on these 200 than it is. That is the trap of choosing
after looking ([statistics section 8](/statistics#_8-traps)).

### No answer key: code a sample by hand

For `changed_recipe` there are no stars to compare with. The model says that 123 of the 250
reviewers (49%) changed the recipe. Is that right? The only way to find out is to read
texts yourself and compare:

1. **Draw a random sample with a seed**, so that the sample is fair and others can draw the
   same one.
2. **Write your coding rules first.** Does doubling the recipe count as a change? Leaving
   something out? Decide, and write it down.
3. **Code without looking at the model's answers**, so they can't sway you. Ideally two people
   code the same texts and compare; where you disagree with each other, the question is
   ambiguous, and the model will struggle too.
4. **Compare**, with a confusion table and an agreement rate with its interval, as above.

:::code-group
```python [Python]
to_code = reviews.sample(n=40, random_state=2026)[["review_id", "text"]]
to_code["my_changed_recipe"] = ""            # fill in TRUE or FALSE
to_code.to_csv("data/hand-coding.csv", index=False)

# after coding:
coded = pd.read_csv("data/hand-coding.csv").merge(labels, on="review_id")
pd.crosstab(coded["my_changed_recipe"], coded["changed_recipe"])
```
```r [R]
set.seed(2026)
to_code <- reviews |>
  slice_sample(n = 40) |>
  select(review_id, text) |>
  mutate(my_changed_recipe = NA)             # fill in TRUE or FALSE
write_csv(to_code, "data/hand-coding.csv", na = "")

# after coding:
coded <- read_csv("data/hand-coding.csv") |> inner_join(labels, by = "review_id")
table(me = coded$my_changed_recipe, model = coded$changed_recipe)
```
:::

Open `data/hand-coding.csv` in VS Code, not Excel (week 2), and type `TRUE` or `FALSE` after the
last comma of each row.

**How many to code?** The half-width of the interval, $1.96\sqrt{\hat p(1-\hat p)/n}$, is
largest when $\hat p = 0.5$. In that worst case:

| Texts coded, $n$ | 20 | 40 | 100 | 200 |
|---|---|---|---|---|
| Interval at most ± | 22 points | 15.5 points | 9.8 points | 6.9 points |

Forty texts take less than an hour and give a rough check; for a number you build conclusions
on, code about 100.

**Try it.** Code the 40 reviews yourself, following steps 1–4. How often do you agree with the
model on `changed_recipe`? Put an interval on it. Then read the reviews where you disagree:
who is right?

## What changes the answers?

A thermometer gives the same reading for the same temperature. A language model's answers
depend on several things you choose, and each one must be written down for anyone to rerun
your work. We ran the same 250 reviews several times, changing one thing at a time:

![Labels that changed between two runs, out of 250, for each field: none when run again with the same settings; 35 to 43 at temperature 1 with another seed; 35 to 65 with a reworded prompt; 28 to 100 with the smaller model](/img/week-6/what-changes.svg)

- **Run again, same settings:** not one of the 750 answers changed.
- **Temperature.** The model writes its answer one piece (token) at a time, each drawn from a
  probability distribution over what could come next. At temperature 0 it always takes the
  most likely piece; at higher temperatures it draws at random, more and more evenly. At
  temperature 1, two runs with different seeds disagreed on 37 sentiments, 43 `made_it` and
  35 `changed_recipe` answers out of 250. For measuring, use temperature 0, and fix the seed.
- **The prompt.** A shorter prompt that only names the fields, without saying what each value
  means ("prompt B"), changed 65 of the 250 sentiments, and agreement with the stars fell from
  87.5% to 70.5%: it called many negative reviews `mixed`. The wording is part of the method.
- **The model.** `llama3.2:1b` agreed with the bigger model on most sentiments (28 changed), but
  on `made_it` and `changed_recipe` it disagreed with it on 91 and 100 of the 250 reviews.

![Agreement with the stars on the 200 clear reviews, with 95% intervals: 87.5% for the main run, 70.5% with prompt B, 84.0% with the smaller model](/img/week-6/agreement-intervals.svg)

The intervals of the two models overlap: on sentiment, these 200 reviews can't tell the 1b
model from the 3b. The reworded prompt is clearly worse.

**Versions change, too.** A name such as `llama3.2` (without the `:3b`) or `latest` can point to a
different file next month: some tags in the Ollama library were re-published only weeks ago.
The ID that `ollama list` shows identifies the exact file you used. And a different Ollama
version or computer may round differently and change a few answers, even at temperature 0. That
is one more reason to commit the output, not just the script.

**So, pin everything:** the exact model tag and its ID, the Ollama version, temperature 0, the
seed, and the prompt and the schema, committed in the repository.

## Privacy: where does the text go?

When you use a chatbot or an API from a company, your text is sent to their servers. That is
fine for public product reviews. It is **not** fine for interview transcripts, open answers from
a survey you ran, messages, medical notes or anything else with names or other personal data:
under GDPR, sending personal data to a third party needs a legal basis and usually the people's
consent, and the company's terms decide what happens to the text afterwards.

A local model keeps the text on your laptop, which is the main reason this course uses one.
Two things still apply:

- **Ollama can also run models in the cloud**: models whose name ends in `:cloud` send your
  text to Ollama's servers. Use local models.
- **The repository is public to your reviewers.** Data with personal information must not be
  committed, whatever model you use; see the [project rules](/project#data). Our reviews are
  public, and we left out the user names.

## Using this in your project

If your project has text, such as job ads, news, reviews, parliamentary speeches or answers to
open questions, an extraction like this can turn it into variables you can count, compare and
plot. It is also a good example of a C or A level method: a step that goes **beyond
description**, whose **limitations** you discuss, and whose results you **check**, with the
uncertainty quantified (see [what an A project looks like](/project#what-an-e-c-and-a-project-looks-like)).

In the report, write:

- **what was extracted, and how:** the fields and their allowed values; the model, its tag and ID,
  the Ollama version, temperature and seed; where the prompt and the schema are in the repository;
- **how you checked it:** how many texts you coded by hand, how they were drawn, your coding rules,
  and the agreement rate with its 95% interval;
- **what the disagreements look like**, and what that means for your conclusions;
- **how to rerun it**: the README names the script, and says that the report uses the saved output.

For this page, that would read:

> We classified the sentiment of 250 recipe reviews (50 per star rating) with `llama3.2:3b`
> (Ollama 0.40.15, temperature 0, seed 4008; prompt and schema in `prompts/`). On the 200
> reviews with 1–2 or 4–5 stars, the model agreed with the rating for 87.5% (95% CI 83–92%).
> Most disagreements were reviews it called mixed, ratings that contradict the text, and
> replies to other users that are not reviews.

## Common pitfalls

- **No check at all.** "The model classified the texts" is not a method until you say how often
  it is right. Hand-code a sample.
- **Checking on the texts you tuned the prompt on.** The agreement will look better than it is.
  Keep fresh texts for the final check.
- **Calling the model from the report.** The check fails, rendering takes minutes, and the numbers
  can change between renders. Run once, save, commit.
- **`llama3.2` or `latest` instead of an exact tag**, no temperature, no seed: nobody, including
  you next month, can get the same answers.
- **Free-text fields.** "Describe the main complaint" gives 250 different sentences. Use fixed
  categories, and add `other` if you need it.
- **Personal data in a hosted service**, or in the repository.

## Check your understanding

1. Why does the schema use `positive`, `mixed`, `negative` rather than asking the model to
   describe the reviewer's opinion?
2. The model agrees with the stars on 175 of 200 reviews. Show that the 95% interval is about
   83–92%. How many reviews would you need for an interval of about ±2 points?
3. A classmate's report renders the model's answers inside `report.qmd`. What goes wrong, and what do
   you suggest in your review?
4. A review with 1 star says "Delicious, my family loved it!" and the model says `positive`.
   Is the model wrong?
5. Your group wants to classify answers from a survey you ran among students, using a hosted
   chatbot. What do you need to think about first?

## This week: the project

There is no new homework. Finish the HW5 peer review by Thursday and your final HW5 version by
Friday ([Homework](/homework/)). Then work on the [project](/project): the deadline is
{{ $course.project.replace('Due ', '') }}, the presentations are {{ $course.presentation }}, and
the [exam](/exam/) is {{ $course.exam }}.

## Further reading

- Ollama: [download](https://ollama.com/download),
  [structured outputs](https://docs.ollama.com/capabilities/structured-outputs),
  [the chat API](https://docs.ollama.com/api/chat) (the `format` and `options` fields),
  [the model library](https://ollama.com/library) and the tags of
  [llama3.2](https://ollama.com/library/llama3.2/tags).
- The Python package [ollama](https://pypi.org/project/ollama/) and the R package
  [httr2](https://httr2.r-lib.org/).
- In R, [ellmer](https://ellmer.tidyverse.org/) is a higher-level alternative: `chat_ollama()`
  and `parallel_chat_structured()` return a data frame directly. See its
  [structured data](https://ellmer.tidyverse.org/articles/structured-data.html) article.
- Data: Ali, Matuszewski and Czupyt (2023), [Recipe Reviews and User Feedback](https://doi.org/10.24432/C5FG95),
  UCI Machine Learning Repository, CC BY 4.0.
- [Statistics: the basics](/statistics), sections 4 (intervals) and 8 (traps), on this site.
