# MT4008 assignment (Python)

Work on a branch, render the report, and open a pull request. Step-by-step instructions:
<https://su-mt4008.github.io/guide>

## Render the report

```bash
uv sync                          # install exactly the packages in uv.lock
uv run quarto render report.qmd  # run the analysis and write report.md
```

## What each file is for

| File | What it is |
|---|---|
| `report.qmd` | Your report: text and code, in seven sections. **Edit this.** |
| `report.md`, `report_files/` | The rendered report and its figures. Made by `quarto render`; commit them, never edit them by hand. |
| `data/raw/` | The data exactly as you got it. Never edit by hand; note source and licence in `data/raw/README.md`. |
| `src/` | Functions the report uses, to keep the report readable. |
| `pyproject.toml` | The packages you use. Add one with `uv add <name>`. |
| `uv.lock` | The exact versions of every package. Made by uv; commit it, never edit it. |
| `.python-version` | The Python version uv uses. |
| `.github/workflows/check.yml` | The check that runs on your pull request. Leave it as it is. |
| `.devcontainer/` | Lets you open this repository in GitHub Codespaces if your own installation fails. |
| `.gitignore` | Files Git should never commit, such as your local `.venv/`. |

## Habits

- Never edit raw data by hand.
- Use relative paths only (`data/raw/file.csv`, not `C:\Users\...`).
- Set a random seed when anything is random.
- Render from scratch before every push.
