# MT4008 assignments

All five assignments live in this one repository, each in its own folder. It works for
**Python and R**: use the language you chose for the course, and ignore the other language's files.
For each assignment: make a branch `hwN` from `main`, work in `hwN/`, render, and open a pull
request titled `HWN`. Step-by-step instructions: <https://su-mt4008.github.io/guide>

## Render

Python:

```bash
uv sync              # install exactly the packages in uv.lock
uv run quarto render # render every report (hw1/ ... hw5/)
```

R:

```bash
Rscript -e 'renv::restore()'  # install exactly the packages in renv.lock
quarto render                 # render every report (hw1/ ... hw5/)
```

To render just one report while you work: `uv run quarto render hw1/report.qmd` (Python) or
`quarto render hw1/report.qmd` (R).

## What each file is for

| File | What it is |
|---|---|
| `hw1/` … `hw5/` | One folder per assignment. **Edit `hwN/report.qmd`**; put that assignment's data in `hwN/data/raw/`. Start code chunks with `{python}` or `{r}`. |
| `hwN/report.md`, `hwN/report_files/` | The rendered report and its figures. Made by Quarto; commit them, never edit them by hand. |
| `example/python/`, `example/r/` | The same worked example of a report, in each language. Read yours; leave them as they are. |
| `_quarto.yml` | Tells Quarto which reports to render and how. |
| `.github/workflows/check.yml` | The check that runs on your pull requests. Leave it as it is. |
| `.devcontainer/` | Lets you open this repository in GitHub Codespaces if your own installation fails. |
| `.gitignore` | Files Git should never commit, such as your local `.venv/` or `renv/library/`. |

**Python only** (R users: leave these alone)

| File | What it is |
|---|---|
| `pyproject.toml` | The packages you use. Add one with `uv add <name>`. |
| `uv.lock` | The exact versions of every package. Made by uv; commit it, never edit it. |
| `.python-version` | The Python version uv uses. |

**R only** (Python users: leave these alone)

| File | What it is |
|---|---|
| `.Rprofile`, `renv/` | Switch on this project's own package library when R starts here. Leave them as they are. |
| `renv.lock` | The exact versions of every package. After installing a new package, run `renv::snapshot()` and commit it. |

## Habits

- Never edit raw data by hand.
- Use relative paths only (`data/raw/file.csv`, not `C:\Users\...`).
- Set a random seed when anything is random.
- Render from scratch before every push.
