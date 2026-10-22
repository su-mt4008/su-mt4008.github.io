---
outline: 2
---

# Reproducible Analysis with GitHub, Jupyter, and Functional Programming

**Who this is for.** Anyone doing data analysis in Python or R who wants results to be easy to rerun, check, and share.

**You will learn to**
- set up an isolated environment for a project,
- write runnable notebooks with clear narrative,
- version your work with Git/GitHub,
- apply functional programming (FP) ideas for predictability.

**Resources (Markdown, Git, setup)**
- [Basics of Markdown](https://www.markdownguide.org/basic-syntax/)
- [Extended Markdown](https://www.markdownguide.org/extended-syntax/)
- [Git & GitHub basics (W3Schools)](https://www.w3schools.com/git/git_intro.asp?remote=github)
- [Git & GitHub basics (video, ~1h)](https://www.youtube.com/watch?v=RGOj5yH7evk)

**Resources (functional programming)**
- [R4DS, Ch. 26: Functional programming](https://r4ds.hadley.nz/)
- [purrr (R)](https://purrr.tidyverse.org/)
- [Functional programming in Python](https://realpython.com/python-functional-programming/)

> This post is hands-on: follow along once, then use it as a reference.

## Why reproducibility?

Reproducibility means someone else (or future-you) can run your analysis and get the same numbers. It builds trust, makes debugging easier, and lets others build on your work.

We’ll combine:
- **Python or R** for the analysis,
- **Jupyter Lab** for literate, executable documents,
- **Git** (local) + **GitHub** (remote) for versioning and collaboration.

Functional programming (FP) ties it together by encouraging **pure, modular code** with fewer surprises.


## Quick admin

Please register your GitHub username on the <a :href="$course.links.moodle">Moodle course page</a>.  
No GitHub yet? Create an account → then register it on Moodle. We’ll review homework via GitHub.


## Install the essentials

### Git & GitHub Desktop

**What & why**
- **Git** tracks versions of your code and notebooks.
- **GitHub** hosts your repository online for backup, sharing, and feedback.
- **GitHub Desktop** is a simple GUI that bundles Git.

**Install**
- Download **GitHub Desktop**: https://desktop.github.com/  
- Sign in with your GitHub account.

> Tip: Learn by doing. We’ll create a repo and push within minutes.


## Miniconda & Jupyter Lab

**What & why**
- **(Mini)Conda** manages packages **and** isolated environments (one clean setup per project).
- **Jupyter Lab** runs notebooks that mix code, text, and plots.

### Install Miniconda
1. Go to https://docs.conda.io/projects/miniconda/en/latest/
2. Download for your OS and run the installer.

### Create a course environment

Pick **Python** or **R** and run in your terminal:

:::code-group
```[Python]
conda config --add channels conda-forge && conda create --name py_env pandas numpy matplotlib jupyterlab -y
```
```[R]
conda config --add channels conda-forge && conda create --name renv r-essentials r-base=4.1.3 -y
```
:::

> Conda environments keep dependencies from clashing across projects.

### Launch Jupyter Lab

Activate your environment and start Jupyter:

```
conda activate ENV_NAME
jupyter lab
```

Use `py_env` for Python or `renv` for R.

### Markdown in notebooks

Use **Markdown** for narrative: explain goals, assumptions, and decisions near the code that implements them. Start with the “Basics” link above.


## Git basics you’ll actually use

**Docs & guides**
- [Branching & merging (GitHub Flow)](https://docs.github.com/en/get-started/quickstart/github-flow)
- [.gitignore](https://git-scm.com/docs/gitignore)
- [Fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)

### Ignore noisy files

Create a `.gitignore` in the repo root (or via GitHub Desktop → *Repository Settings → Ignored Files*). At minimum:

```
.ipynb_checkpoints
```

### Fork vs clone (which do I pick?)

- **Fork**: your own copy, detached from the original (great for starting from a template or contributing to open source).
- **Clone**: a local copy of a repo you already collaborate on (keeps the link to the original).

### Branches (safe experiments)

A branch lets you try ideas without risking `main`.

In **GitHub Desktop**:
- **New branch**: *Current Branch → New Branch…*
- **Publish** to send it to GitHub.
- **Merge**: *Current Branch → Choose a branch to merge into… → Create merge commit*
- **Delete**: right-click the branch → **Delete**


## Functional programming (FP) for predictable analyses

FP treats programs as **pure functions** over **immutable data**. The payoffs:

- **Same input → same output** (fewer “works on my machine” bugs)  
- Easier **testing** and **parallelization**  
- Clear, composable pipelines (`map` / `filter` / `reduce`)

### Core ideas at a glance

- **Immutability**: don’t change values in place; return new ones.
- **Pure functions**: output depends only on inputs; avoid side effects.
- **Higher-order functions**: functions that take/return functions.
- **Composition**: build bigger behavior by chaining small functions.

### Examples (Python & R)

**Pure vs. impure**

:::code-group
```Python
# Impure: mutates external state
total = 0
def add_to_total(value):
    global total
    total += value

# Pure: depends only on inputs
def add(a, b):
    return a + b
```
```R
# Impure: mutates external state
total <- 0
add_to_total <- function(value) {
  total <<- total + value
}

# Pure: depends only on inputs
add <- function(a, b) {
  a + b
}
```
:::

**Higher-order functions**

:::code-group
```Python
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x * x, numbers))         # map
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))  # filter
```
```R
library(purrr)
numbers <- c(1, 2, 3, 4, 5)
squared <- map(numbers, ~ .x * .x)
even_numbers <- keep(numbers, ~ .x %% 2 == 0)
```
:::

**Immutability**

:::code-group
```Python
immutable_list = [1, 2, 3]
new_list = [*immutable_list, 4]  # original unchanged
```
```R
immutable_vector <- c(1, 2, 3)
new_vector <- c(immutable_vector, 4)  # original unchanged
```
:::

**Composition**

:::code-group
```Python
def add_one(x): return x + 1
def square(x):  return x * x
square_and_add_one = lambda x: add_one(square(x))
square_and_add_one(3)  # 10
```
```R
add_one <- function(x) x + 1
square  <- function(x) x * x
square_and_add_one <- purrr::compose(add_one, square)
square_and_add_one(3)  # 10
```
:::

**Map + reduce**

:::code-group
```Python
numbers = [1, 2, 3, 4, 5]
squared_and_sum = sum(map(lambda x: x * x, numbers))  # 55
```
```R
library(purrr)
numbers <- c(1, 2, 3, 4, 5)
squared_and_sum <- numbers %>% map_dbl(~ .x * .x) %>% reduce(`+`)  # 55
```
:::


## Quick win: first repo + first notebook (5 steps)

1. **Create environment**: `py_env` or `renv`.  
2. **Start Jupyter**: `jupyter lab`, make `week1.ipynb`.  
3. **Write**: one Markdown cell (“Goal”), one code cell that prints `2 + 2`.  
4. **Init repo** (GitHub Desktop → *File → New repository…*).  
5. **Commit & publish**: write a clear message (“Add week1 notebook”), then **Publish repository**.

> From now on: small, frequent commits with clear messages beat giant, infrequent ones.


## Common pitfalls (and fixes)

- **“My notebook runs differently each time.”**  
  Use pure functions and fix random seeds; restart kernel and *Run All* before committing.

- **“Conflicting packages.”**  
  Use a fresh Conda environment per project; avoid installing globally.

- **“Gigantic notebooks in Git.”**  
  Keep outputs lightweight; avoid committing large data files—store data in `/data/` and add it to `.gitignore` (or use Git LFS if needed).


## Mini-exercises

1. **Markdown warm-up**: write a short intro cell with a heading, a list, and a link.  
2. **Environment check**: import `pandas`/`numpy` (Python) or `tidyverse` (R) and print their versions.  
3. **Pure function**: write a function that standardizes a numeric vector/array and returns the standardized copy (don’t mutate inputs).  
4. **Git practice**: make a branch `feat/add-standardize`, add your function, commit twice (once for function, once for tests/usage), merge into `main`, delete the branch.


## Putting it all together (your workflow)

1. **Create** a clean environment and launch **Jupyter Lab**.  
2. **Start** a GitHub repo (use GitHub Desktop).  
3. **Write** notebooks with clear Markdown and pure, testable functions.  
4. **Commit** often; use branches to experiment; maintain a `.gitignore`.  
5. **Push** to GitHub so your work is transparent and reproducible.


## Your first task

Create your first notebook and push it to GitHub. See **[homework 1](/homework/1)** for specifics.
