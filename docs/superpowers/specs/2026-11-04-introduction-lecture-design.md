# Introduction lecture: slides + companion post (design)

Date: 2026-11-04. Branch: `redesign-ht26`. Needed for Thu 5 Nov 2026, 13:00 (first session).

## Intent

The first session of MT4008 opens with a motivating story, then the practicalities, then the
first week's content. One theme runs through it all: **the data science life cycle**
(question → data → cleaning → exploration → analysis → conclusions & limitations → reproduce —
the same seven sections every student report has). Students should leave knowing what a good
project looks like at three ambition levels, how the course runs, and enough of week 1 and the
statistics basics to start HW1.

The slides are part of the site: a link on the site, with a companion blog-style post that tells
the same story in prose.

## Structure (90 minutes)

**Part 1 — 45 min**

1. Motivation, ~25 min: three real, reproducible projects, increasing ambition (~5, ~10, ~10 min).
   Each project: the question, what was done at each life-cycle step (one diagram), 2–3 result
   figures, the honest limitations, and the grade level it roughly corresponds to.
   - **Small (≈E): "Are baby names a fashion?"** One source: SCB's 100 most common first names
     by year of birth 1922–2021 (table `BE0001T100` / `BE0001F100`, old PxWeb API). Rise and fall,
     and comebacks after ~100 years. Limitation slide: the counts are people alive in 2021, so
     older cohorts are thinned by deaths and emigration (survivorship bias).
   - **Medium (≈C): "Why does electricity cost more in Malmö than in Luleå?"** Two or three
     sources joined: hourly spot prices per zone SE1–SE4 (elprisetjustnu.se API, from Nov 2022)
     and SMHI wind/temperature. Joins, time zones/DST, correlation vs cause.
   - **Ambitious (≈A): "Is AI a bubble?"** Several sources: Shiller CAPE (1871–), FRED NASDAQCOM,
     and a text source (Hacker News Algolia API: share of stories mentioning AI vs earlier hype
     terms). The lesson: "bubble" cannot be measured directly; the work is operationalising the
     question and being careful about what the evidence supports. No predictions.
   - Closing slide: the three diagrams side by side — same cycle, bigger question, more sources.
     The report is not longer; the thinking is.
2. Course structure, ~20 min: what the course is, how a week works (self-study, Monday
   walkthrough, sessions as work time), homework (0–100, 65 to pass, −30 late with no peer
   review, peer review Thu 23:59, final version Fri 23:59, final deadline 15 Jan), project
   (groups of 2–3, proposal 19 Nov on Moodle, A/C/E criteria, 15–20 min presentations), exam.
   Every slide ends with a pointer to the page on the site.

**Part 2 — 45 min**

3. Week 1: reproducible analysis — questions, the seven-section report, the
   `<username>-assignments` repo, lockfiles, Quarto, Git and the PR flow (condensed from
   `lectures/week-1.md`).
4. Statistics basics: from Probability I to statistics — data as random variables, standard
   error and confidence intervals, bootstrap, tests and permutation, correlation vs causation,
   the many-tests trap (condensed from `statistics.md`, reusing its figures).
5. Close: HW1 is out, due Mon 9 Nov; what to do before Monday.

## Decisions

- **Slides:** Quarto reveal.js deck, source in `slides/introduction/` of this repo, rendered into
  `public/slides/introduction/` (committed) so VitePress serves it at `/slides/introduction/`.
  Styled to match the site: IBM Plex, site palette, light and dark.
- **Companion post:** `lectures/introduction.md`, linked as "Introduction" above Week 1 in the
  Lectures sidebar, from the lectures index, and from week 1. Post and deck link to each other.
- **Dates and numbers come from `course.config.ts`.** The deck gets them through a generated
  Quarto variables file, so the slides cannot drift from the site.
- **The projects are real and reproducible.** Each is a full seven-section Quarto report with a
  fetch step that saves raw data to `data/`, in `su-mt4008/lecture-demos` under `introduction/`
  (uv + Quarto, same shape as the student template). Students can clone and render them.
- **Figures** are computed from the projects' saved data by a script (like
  `scripts/statistics_figures.py`), as SVGs with transparent background, grey ink and one red
  accent, so they read in both themes. The deck and the post use the same files.
- **Life-cycle diagrams:** one per project, the same seven-step strip, each step annotated with
  what that project did; data sources visibly branch and merge as ambition grows. Clean SVG in
  the site's style — not generic flowchart boxes.

## Non-goals

- No live coding or demos in the session.
- No grading mechanics beyond what the site states.
- No financial prediction in the AI project.

## Left to the builder

Exact slide count and wording, figure choices within each project, the precise operationalisation
of the AI-bubble indicators, and the reveal.js theme details, within the constraints above.

## Update: one deck per lecture (2026-11-04)

Every week gets a deck, so the setup is shared: `slides/_quarto.yml` renders every
`slides/<name>/index.qmd` to `public/slides/<name>/` (one shared copy of reveal.js in
`site_libs/`), with the theme and the dates script in `slides/_shared/`. A lecture page
`/lectures/<name>` gets a Slides link automatically when `slides/<name>/` exists, and the
Lectures schedule has a Slides column. The first session uses two decks: `introduction`
(projects and course structure) and `week-1` (week 1 and statistics).
