# MT4008 assignments (Python)

All five assignments live in this one repository, each in its own folder. For each assignment:
make a branch `hwN` from `main`, work in `hwN/`, render, and open a pull request titled `HWN`.
Step-by-step instructions: <https://su-mt4008.github.io/guide>

## Render

```bash
uv sync              # install exactly the packages in uv.lock
uv run quarto render # render every report (example/ and hw1/ ... hw5/)
```

To render just one report while you work: `uv run quarto render hw1/report.qmd`.

## What each file is for

| File | What it is |
|---|---|
| `hw1/` … `hw5/` | One folder per assignment. **Edit `hwN/report.qmd`**; put that assignment's data in `hwN/data/raw/`. |
| `hwN/report.md`, `hwN/report_files/` | The rendered report and its figures. Made by Quarto; commit them, never edit them by hand. |
| `example/` | A worked example of a report. Read it; leave it as it is. |
| `_quarto.yml` | Tells Quarto which reports to render and how. |
| `pyproject.toml` | The packages you use. Add one with `uv add <name>`. |
| `uv.lock` | The exact versions of every package. Made by uv; commit it, never edit it. |
| `.python-version` | The Python version uv uses. |
| `.github/workflows/check.yml` | The check that runs on your pull requests. Leave it as it is. |
| `.devcontainer/` | Lets you open this repository in GitHub Codespaces if your own installation fails. |
| `.gitignore` | Files Git should never commit, such as your local `.venv/`. |

## Habits

- Never edit raw data by hand.
- Use relative paths only (`data/raw/file.csv`, not `C:\Users\...`).
- Set a random seed when anything is random.
- Render from scratch before every push.
