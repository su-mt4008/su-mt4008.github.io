---
outline: 2
---

# Reproducible Analysis: Questions, Git and Quarto

**This week** you learn what a data analysis consists of, how to turn a question into one data
can answer, and how to set up your work so that anyone can rerun it and get the same result.
You also learn the tools you will use every week: VS Code, Git and GitHub, Quarto, and `uv` or
`renv`.

**By the end of the week you can**

- name the seven steps of a data analysis, and say what each is for;
- turn a vague question into one that data can answer;
- explain why an analysis that only runs on your computer can’t be trusted;
- set up a project with a locked environment and a Quarto report;
- use Git and GitHub from VS Code: commit, branch, push, open and review a pull request.

**How to use this page.** Read it once from top to bottom (about two hours), with VS Code open,
and do the small exercises as you go. Then do [HW1](/homework/1). Setup instructions are on
[How we work](/guide#set-up-your-computer); this page explains the *why*.

## What a data analysis consists of

Every data analysis, from a homework to a published study, goes through the same steps:

| Step | What you do | The question to ask yourself |
|---|---|---|
| **Question** | Decide what you want to find out. | Can data answer this? Who cares about the answer? |
| **Data** | Find or collect data, and learn how it was made. | What does it measure? Who or what is missing? |
| **Cleaning** | Fix types, missing values, duplicates, odd entries. | Did I write down every decision? |
| **Exploration** | Look at distributions, relationships, surprises. | What do I see before I start concluding? |
| **Analysis** | Use a method that fits the question. | Does the answer hold up if I check it? |
| **Conclusions & limitations** | Say what the evidence supports, and how sure you are. | What else could explain this? |
| **How to reproduce** | Make it possible for anyone to rerun it all. | Would it run on someone else’s computer? |

The tools change from week to week; these steps don’t. Every assignment and the project use them,
and so does the template your repositories start from. Code is how you carry out the steps, but
the science is in the questions in the right-hand column.

## Asking a question data can answer

Most analyses go wrong at the first step: the question is too vague to answer. Compare:

- *“Is the climate changing?”* — too big, and no dataset answers it on its own.
- *“Has Stockholm got warmer?”* — better, but warmer than when, and measured how?
- *“Was the mean annual temperature at Stockholm-Observatoriekullen higher in 2011–2025 than in
  1997–2010?”* — this one a dataset can answer.

A good question says **what** is measured, **where or for whom**, and **compared with what**.
Then ask what the answer would *not* tell you: one weather station in a city is not “Sweden”,
and 30 years is a short period for climate. Stating that is not a weakness of your analysis; it
is part of doing it honestly.

**Try it.** Sharpen one of these into a question a dataset could answer: *“Are trains late?”*,
*“Do students study more before exams?”*

## Why reproducibility matters

Reproducibility means someone else (or future-you) can run your analysis and get the same
numbers. It builds trust, makes mistakes findable, and lets others build on your work. A result
that nobody can reproduce is, scientifically, just a claim.

Analyses usually fail to reproduce for boring reasons:

| What goes wrong | Example | The habit that prevents it |
|---|---|---|
| Different package versions | Your code uses a function that changed in pandas 3. | A **locked environment**. |
| Hidden state | A variable you created by hand an hour ago, then deleted the code. | **Render from scratch** before every push. |
| Hand-edited data | You fixed a typo in the CSV in Excel; nobody knows. | **Never edit raw data by hand**; change it in code. |
| Paths that only exist on your computer | `C:\Users\anna\Downloads\data.csv` | **Relative paths only**: `data/raw/data.csv`. |
| Randomness | A random sample differs every run. | **Set a seed**. |
| Missing files | The data was never committed. | Commit data (or a download script); let the **check** catch it. |

In this course, an **automatic check** runs your report on a clean computer every time you open
or update a pull request. If it is green, your analysis is reproducible.

## Anatomy of a reproducible project

Every assignment repository starts from the same template. Each part has one job:

```
<username>-hw1/
├─ report.qmd        ← your report: text and code, seven sections
├─ report.md         ← the rendered report (made by Quarto; commit it)
├─ report_files/     ← its figures (made by Quarto; commit them)
├─ data/raw/         ← data exactly as you got it, plus a README with source and licence
├─ src/  or  R/      ← functions the report uses
├─ pyproject.toml + uv.lock   or   renv.lock   ← the locked environment
├─ .github/workflows/check.yml                ← the reproducibility check
└─ README.md         ← what everything is, and the one command that renders it
```

The structure is the same every time, so a reader (or a reviewer) knows where to look. Raw data
is separate from code, and everything generated (`report.md`, figures) can be recreated from
the rest with one command.

## Environments and lockfiles

Your code depends on packages (pandas, ggplot2, …), and packages change between versions. An
**environment** is a set of packages installed *for one project*, separate from everything else
on your computer. A **lockfile** records the exact version of every package, so that anyone can
install the very same set.

:::code-group
```bash [Python (uv)]
uv sync                 # install exactly what uv.lock lists into .venv/
uv add seaborn          # add a package: updates pyproject.toml and uv.lock
uv run python script.py # run something inside the environment
```
```r [R (renv)]
renv::restore()             # install exactly what renv.lock lists into this project
install.packages("janitor") # add a package to this project's library...
renv::snapshot()            # ...and record it in renv.lock
```
:::

Commit the lockfile (`uv.lock` or `renv.lock`) every time it changes. The local environment
itself (`.venv/`, `renv/library/`) is never committed: anyone can rebuild it from the lockfile.

**Try it.** In your HW1 repository, run `uv sync` or `renv::restore()`. Then look at the
lockfile: find the exact version of pandas or dplyr you are using.

## Reports with Quarto

A **Quarto** document (`.qmd`) mixes text and code. When you **render** it, Quarto runs the code
from top to bottom and writes a report with the results and figures in place. This is
*literate programming*: the explanation sits next to the code that does the work, so a reader
can follow both.

A `.qmd` file has three kinds of content:

````markdown
---
title: "Has Stockholm got warmer?"
format: gfm
---

## Question

Was the mean annual temperature …

```{python}
#| fig-cap: "Mean temperature per year."
plt.plot(years, temps)
```
````

1. **A header** between the `---` lines, with settings. `format: gfm` makes a Markdown report
   that GitHub can show.
2. **Text** in Markdown: headings with `##`, **bold** with `**…**`, lists with `-`.
3. **Code chunks** in ```` ```{python} ```` (or ```` ```{r} ````). Quarto runs them and puts
   the output right below.

Render it from the terminal with `uv run quarto render report.qmd` (Python) or
`quarto render report.qmd` (R). The Quarto extension in VS Code also has a **Preview** button.

Useful chunk options, written as `#|` lines at the top of a chunk:

| Option | Effect |
|---|---|
| `#\| fig-cap: "…"` | a caption under the figure |
| `#\| echo: false` | show the result but not the code |
| `#\| include: false` | run the code but show nothing (setup chunks) |

Why Quarto rather than Jupyter notebooks? A `.qmd` file is plain text, so Git can show exactly
what changed, line by line, and a reviewer can comment on it. A notebook is stored as JSON with
its outputs inside, so its changes are almost unreadable in a pull request. Quarto also works
the same way for Python and R.

## Git and GitHub

**Git** records versions of your files. **GitHub** keeps a copy of your repository online, where
others can see it, review it and run checks on it. The words you need:

| Word | Meaning |
|---|---|
| **repository** (repo) | a project folder whose history Git tracks |
| **commit** | a saved version, with a message saying what changed |
| **branch** | a separate line of work; `main` is the accepted version |
| **clone** | download a repository from GitHub to your computer |
| **push** / **pull** | send your commits to GitHub / fetch others’ commits |
| **pull request** | a proposal to merge a branch into `main`, where it is reviewed |
| **merge** | bring a branch’s commits into `main` |
| **fork** | your own copy of someone else’s repository on GitHub, still linked to the original (used to contribute to projects you can’t write to) |

The workflow you use every week:

```
main     ●──────────────────────────────●  (merged when accepted)
          \                            /
hw1        ●──●──●──●  ──► pull request "HW1"  ◄── check, review, fixes
          commit commit…
```

1. **Clone** your repository and make a **branch** (`hw1`).
2. Work and **commit** small steps with clear messages: “Clean the date column” beats “update”.
3. **Push** the branch and open a **pull request** into `main`. That is your hand-in.
4. The **check** runs; a classmate and the teachers **review**; you push fixes to the same branch.
5. When it is accepted, it is **merged** into `main`.

The exact clicks in VS Code are on [How we work](/guide#hand-in-an-assignment).

### Reviewing a pull request

Code review is the everyday version of scientific peer review: someone else checks your work
before it is accepted. You do it every week. A good review reads the report first, as a reader
would, then the code, and asks: Is the question clear? Do the conclusions follow? Would this run
anywhere? It points to specific lines, suggests concrete changes, and is kind. See
[Review a pull request](/guide#review-a-pull-request).

**Try it.** Make a small change on your `hw1` branch, commit it, push, and look at your
repository on GitHub: find the branch, the commit and its message.

## Habits

These five habits make an analysis reproducible. They apply to every assignment and the project:

1. **Never edit raw data by hand.** Every change happens in code.
2. **Relative paths only.**
3. **Set a random seed** whenever anything is random.
4. **Render from scratch before every push.**
5. **One command renders everything.**

## Common pitfalls

- **“It works on my computer but the check is red.”** Almost always a package missing from the
  lockfile, a file that isn’t committed, or an absolute path. See
  [When the check is red](/guide#when-the-check-is-red).
- **“I committed to `main` by mistake.”** Ask in a session; it’s easy to fix, and it’s why we
  always work on a branch.
- **“My report shows different numbers each time.”** Something random without a seed, or code
  that depends on what you ran earlier. Render from scratch.
- **“Huge files in Git.”** Keep raw data small (under ~50 MB per file); for bigger data, commit
  a script that downloads it.

## Check your understanding

1. Which of the seven steps does each of these belong to: removing duplicate rows; a boxplot;
   “the station is in a city, so it may be warmer than the countryside”; `uv sync`?
2. Why is the lockfile committed, but not `.venv/` or `renv/library/`?
3. Your classmate’s check is red with `No such file or directory: 'C:\Users\…\data.csv'`.
   What do you write in your review?
4. Why does this course use `.qmd` files rather than notebooks?

## Your first task

Do [HW1](/homework/1): the whole workflow once, on Stockholm temperatures.

## Further reading

- [The Turing Way: Guide for reproducible research](https://book.the-turing-way.org/reproducible-research/reproducible-research)
- [Pro Git](https://git-scm.com/book/en/v2), chapters 1–3
- [Happy Git and GitHub for the useR](https://happygitwithr.com) (R users)
- [Quarto: Get started](https://quarto.org/docs/get-started/)
- [uv documentation](https://docs.astral.sh/uv/) · [renv: Introduction](https://rstudio.github.io/renv/articles/renv.html)
- [Markdown basics](https://www.markdownguide.org/basic-syntax/)
