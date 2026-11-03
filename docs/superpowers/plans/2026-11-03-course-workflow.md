# Course Workflow (HW1-ready) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Everything HW1 needs for the pull-request workflow, live by Thu 5 Nov: Python and R
assignment templates with a reproducibility check, a "How we work" guide page, the new HW1 page,
a rewritten week 1, and the pull-request hand-in on every page.

**Architecture:** The two templates live in this repo under `templates/python/` and
`templates/r/` (excluded from the site build) as the source of truth, with a shell test that
does what the GitHub check does on a fresh copy. They are published to the org as template
repos only in the last, user-approved task. Site content stays in VitePress Markdown; a vitest
content test pins the switch from issues to pull requests.

**Tech Stack:** VitePress 1.6.4, vitest, Quarto 1.8.25, uv 0.10 (Python 3.12+), R 4.5 + renv,
GitHub Actions (`astral-sh/setup-uv`, `quarto-dev/quarto-actions/setup`, `r-lib/actions`),
actionlint via Docker.

**Spec:** `docs/superpowers/specs/2026-11-03-course-workflow-design.md`

## Global Constraints

- Repo names follow the org's existing pattern: `<username>-hw<n>` (e.g. `fumeng388-hw1`) and `<username>-project`.
- Hand-in = a pull request titled `HW<n>` from a branch into `main`, opened by Monday 23:59.
- Report = `report.qmd` with exactly these sections, in order: Question · Data · Cleaning · Exploration · Analysis · Conclusions & limitations · How to reproduce.
- `report.qmd` renders to GitHub-flavoured Markdown `report.md` + figures, and both are committed.
- Python env: `pyproject.toml` + `uv.lock`; R env: `renv.lock`. One command renders: `uv run quarto render report.qmd` / `quarto render report.qmd`.
- Check: runs on `pull_request` only; `concurrency` cancel-in-progress; `timeout-minutes: 10`; dependency caching; on failure prints a pointer to the guide page.
- Habits stated wherever the workflow is taught: raw data never edited by hand; relative paths only; set random seeds; restart and run everything before pushing; one command renders the report.
- Python and R both supported from HW1. Codespaces is a fallback only.
- Nothing is pushed to GitHub, no org repo is created, and nothing is merged to `main` without the user's explicit go-ahead (Task 7).

## Review Focus

1. A student's first push has no `report.md` yet or a stale one → the check must still pass if `report.qmd` renders; it must not compare committed output. (Task 1/2 test: render from a copy with `report.md` deleted.)
2. Windows students: paths, line endings, `uv`/`renv` commands → the guide gives Windows variants where they differ (Task 3 content test asserts a Windows note exists).
3. A student who pushes straight to `main` → no check runs and no hand-in exists; the guide and HW1 say so explicitly (Task 3/4 content test).
4. R check time and the Actions budget → R workflow caches the renv library; keep R package set minimal (Task 2 asserts the lockfile has < 40 packages).
5. Old instructions surviving on some page (issues, `ready-for-grading`, GitHub Desktop, conda, `username-hw-1`) → Task 6 content test bans them site-wide.

---

### Task 1: Python template + fresh-copy test

**Files:**
- Create: `templates/python/{report.qmd,pyproject.toml,uv.lock,.gitignore,README.md,data/raw/README.md,src/__init__.py,.github/workflows/check.yml,.devcontainer/devcontainer.json}`
- Create: `templates/test-template.sh`
- Modify: `.vitepress/config.mts` (add `'templates/**'` to `srcExclude`)

**Interfaces:**
- Produces: `templates/test-template.sh <python|r>` — copies the template to a temp dir, removes any `report.md`/`report_files`, runs the template's one render command, then asserts `report.md` exists and contains the seven section headings in order. Exit 0 = pass.
- Produces: guide anchor `/guide#when-the-check-is-red`, referenced by the check's failure message.

- [ ] **Step 1:** Write `templates/test-template.sh` and run it for `python` → FAIL (template missing).
- [ ] **Step 2:** Create the template: `report.qmd` (format `gfm`, `jupyter: python3`, the seven sections each with a one-line prompt in italics and a tiny working code cell that reads `data/raw/example.csv` with a relative path and sets a seed); `pyproject.toml` (python `>=3.12`, deps: pandas, matplotlib, jupyter); `uv lock`; `.gitignore` (`.venv/`, `.quarto/`, `__pycache__/`, `.ipynb_checkpoints/`, `.DS_Store`); README explaining every file and the one command; `data/raw/README.md` (raw data is never edited by hand; record source, licence, date); devcontainer with Python, uv and Quarto.
- [ ] **Step 3:** Write `check.yml` per Global Constraints; failure step prints `::error::` with the guide URL `https://su-mt4008.github.io/guide#when-the-check-is-red`.
- [ ] **Step 4:** Run `templates/test-template.sh python` → PASS; run actionlint (`docker run --rm -v "$PWD":/repo -w /repo rhysd/actionlint:latest templates/python/.github/workflows/check.yml`) → no errors.
- [ ] **Step 5:** `npm run docs:build` still builds; commit.

### Task 2: R template

**Files:** `templates/r/` mirroring Task 1 (`report.qmd` with `knitr` engine, `renv.lock`, `.Rprofile`, `renv/activate.R`, `renv/settings.json`, workflow with `r-lib/actions/setup-r@v2` + `setup-renv@v2`, devcontainer).

**Interfaces:** Consumes `templates/test-template.sh r`.

- [ ] **Step 1:** Run `templates/test-template.sh r` → FAIL.
- [ ] **Step 2:** Create the template; packages: readr, dplyr, ggplot2, knitr, rmarkdown (and their dependencies); `renv::snapshot()`.
- [ ] **Step 3:** Run the test → PASS; assert `renv.lock` lists fewer than 40 packages; actionlint clean.
- [ ] **Step 4:** Commit.

### Task 3: "How we work" guide page

**Files:** Create `guide.md`; modify `.vitepress/config.mts` (Course info sidebar entry "How we work" → `/guide`; nav `activeMatch` `^/(about|guide)`); create `.vitepress/theme/content.test.ts`.

**Interfaces:** Produces anchors `#set-up-your-computer`, `#hand-in-an-assignment`, `#when-the-check-is-red`, `#review-a-pull-request`, `#if-your-install-fails` (used by HW pages and the check).

- [ ] **Step 1:** Content test `guide covers the workflow`: `guide.md` contains each anchor heading above, the words `uv sync`, `renv::restore()`, `quarto render`, `Windows`, and a sentence that pushing to `main` is not a hand-in. Run → FAIL.
- [ ] **Step 2:** Write the guide: why the workflow (2–3 sentences); set up (VS Code + extensions: Python, Jupyter, Quarto, R, GitHub Pull Requests; Git; uv or R + renv; Quarto; Windows notes); hand in (clone `<username>-hw<n>`, branch `hw<n>`, work, render, commit, push, open PR titled `HW<n>`, Moodle not needed); the green/red check and the five most common red causes with fixes; reviewing a peer's PR (what to look for, line comments, suggestion blocks, tone); the habits; Codespaces as fallback. Menu paths written out exactly; screenshots marked `TODO(owner)` where they would help (cannot be captured here).
- [ ] **Step 3:** Test → PASS; build; commit.

### Task 4: HW1 page

**Files:** Rewrite `homework/1.md`; add the HW1 dataset under `public/data/hw1/` (small CSV of Swedish open data with a stated licence) — owner reviews the choice.

- [ ] **Step 1:** Content test `HW1 uses the pull-request flow`: `homework/1.md` links `/guide#hand-in-an-assignment`, names the branch `hw1`, the PR title `HW1`, the repo `<username>-hw1`, and the seven report sections. Run → FAIL.
- [ ] **Step 2:** Write HW1: goal = do the workflow once end to end; a given question and the dataset; tasks follow the seven sections at a minimal level (a count or an average, one figure, 2–3 sentences with one limitation); hand-in and peer review via the guide; scoring rules from the Assignments page.
- [ ] **Step 3:** Test → PASS; build; commit.

### Task 5: Week 1 rewrite

**Files:** Rewrite `lectures/week-1.md`.

- [ ] **Step 1:** Content test `week 1 teaches the workflow`: contains sections on reproducibility, project layout, environments (uv and renv), Quarto, Git in VS Code, pull requests; contains none of `GitHub Desktop`, `Miniconda`, `conda create`, `Functional programming`. Run → FAIL.
- [ ] **Step 2:** Rewrite: learning goals; why reproducibility (keep the good existing paragraph); turning a question into one data can answer; anatomy of a reproducible project (the template, file by file); environments with lockfiles; Quarto reports; Git and GitHub in VS Code (commit, branch, push, PR, review); the habits; common pitfalls; "your first task" → HW1. Python and R side by side where commands differ. Fix the fork/clone explanation.
- [ ] **Step 3:** Test → PASS; build; commit.

### Task 6: Pull-request hand-in everywhere

**Files:** `homework/index.md` (CRLF — keep), `homework/2.md`–`5.md` submission sections, `project.md` (submission + group repo PRs), `about.md` if needed.

- [ ] **Step 1:** Content test `no old hand-in instructions`: no page under the site contains `ready-for-grading`, `HW1 – Submission`-style issue titles, `open an issue`, `GitHub Desktop`, `username-hw-`. Run → FAIL.
- [ ] **Step 2:** Replace issue-based steps with the PR flow (linking the guide); peer review = review on the peer's PR; project: work through PRs within the group, hand-in = `main` at the deadline, same template and check.
- [ ] **Step 3:** Test → PASS; full `npm test`; build; commit.

### Task 7: Publish (each step needs the user's explicit go-ahead)

- [ ] Create `su-mt4008/hw-template-python` and `su-mt4008/hw-template-r` (private, marked as template), push the template contents.
- [ ] Verify the check on GitHub: a throwaway repo from each template, a PR, a green run; then a deliberately broken PR shows red with the guide pointer. Delete the throwaway repos.
- [ ] Hand the user the template names for their repo-creation scripts.
- [ ] Merge `redesign-ht26` to `main` (deploys the site) — only when the user says so.
