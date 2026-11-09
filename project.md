# Project

- **Proposal:** **{{ $course.proposal }} (Stockholm time)**, on Moodle
- **Deadline:** **{{ $course.project }} (Stockholm time)**
- **Presentations:** **{{ $course.presentation }}**, {{ $course.presentationRoom }}

## Overview

In **groups of 2–3**, you carry out a full data science project: a question you care about, data you collect yourselves, an analysis that would convince a sceptical reader, and a write-up that anyone can reproduce from your repository.

The scope this year is **much larger** than in previous years. **Think big.** Use the first two weeks to form a group and find a question worth answering, then tell us your plan in a proposal.

## Timeline

1. **Weeks 1–2:** form a group of 2–3 and choose your question. Use the work sessions to find partners and to test ideas with us.
2. **Proposal** ({{ $course.proposal }}): hand it in on Moodle (see below).
3. **After the proposal:** we review it and either accept it or tell you what to change.
   <!-- TODO(owner): if a proposal is not accepted, how and by when do groups revise it? -->
4. **Project deadline** ({{ $course.project }}).
5. **Presentations** ({{ $course.presentation }}).

## Proposal {#proposal}

One proposal per group, handed in on **Moodle** by **{{ $course.proposal }}**. Keep it short (about one page) and include:

* **Group members:** the names of all 2–3 members.
* **Aim:** the question you want to answer, and who would care about the answer.
* **Scope:** which data you will use and how you will get it, what analysis you plan, and what the final result will be.
* **Target grade:** **A**, **C** or **E**, and how your plan meets the criteria for that grade (see below).

We accept a proposal when its scope fits the target grade. Aiming for an A means planning for one from the start.

## What an E, C and A project looks like

<!-- TODO(owner): draft criteria; edit freely. -->

Each level includes everything in the levels below it.

### E

* A **clear question** the data can answer, and a stated audience.
* Data you obtained yourselves, with its **source, licence and how it was collected** documented.
* Cleaning steps that are **documented and justified**.
* An exploration with **appropriate, labelled** figures.
* Conclusions that **follow from the analysis**, and no claims beyond it.
* A repository that **runs from a fresh clone** by following the README.
* Every member has contributed, visibly, in the repository history.

### C

* A question that is **motivated**: why it matters, and what is already known.
* **Non-trivial data collection**: an API, web scraping, a database, or several sources combined.
* An analysis that goes **beyond description**: a comparison, a model or a test, with the choice of method **justified**.
* A discussion of **limitations and possible biases** in the data and the method.
* A **reproducible environment** (pinned dependencies) and code split into clear, reusable parts.
* Teamwork through **branches, pull requests and code review**.

### A

* An **ambitious scope**: a question and data that take real effort, at a realistic scale.
* Results that are **checked**: uncertainty quantified, robustness or sensitivity tested, and alternative explanations considered.
* Conclusions that would **convince a sceptical reader**.
* Industry practice throughout: **one command** takes raw data to the final report, with **automated checks** on the data or code.
* A polished, well-argued write-up for its audience.

## Examples

These are blog posts written the way your report should be: a question, the code that answers it and its output, in one rendered notebook. None was written to our criteria, so each note says roughly where it falls on the scale above and what a group of 2–3 would add to reach the next level. Most are longer than your report should be.

* **[Public pinball machines per capita](https://www.sumsar.net/blog/pinball-machines-per-capita/)** (Rasmus Bååth, 2024, R). Which countries have the most public pinball machines per person, and does that track wealth? Data pulled from the Pinball Map API and joined with World Bank figures, code inline throughout. *Between E and C:* real data collection from two sources, but the correlations come without uncertainty, the limitations are one line and there is no repository. A group would freeze a data snapshot, put a confidence interval on the correlation, test the choices it made (the population cut-off, the log scale) and ship it as a repository.
* **[A Bayesian model of a pinball championship](https://www.sumsar.net/blog/bayesian-plackett-luce-model-pinball-competition/)** (Rasmus Bååth, 2024, R and Stan). Who is the most skilled player, and how sure can we be? Messy competition spreadsheets tidied in the post, then a ranking model with posterior intervals. *Between E and C:* a strong, justified model, but a single downloaded file, convergence checks the author admits are skimped, and printed output that doesn't match the code (spot it). Re-running from a clean environment is exactly what would have caught that.
* **[Do people get more conservative with age?](https://www.allendowney.com/blog/2026/11/06/do-people-get-more-conservative-with-age/)** (Allen Downey, 2026, Python). Separates age, generation and survey year in 50 years of the US General Social Survey. The post is prose and figures; the full analysis is a [companion notebook](https://allendowney.github.io/OvertonParadox/appendix/) that reruns it, with alternative item sets and a check that it reproduces the published results. *A-level checking, C-level packaging:* the robustness work is what we mean by an A, but there is no pinned environment (the notebook even warns that an unpinned install breaks it) and no single command from raw data to post. Far too big for a group as it stands; a version with ten survey questions is not.
* **[Age-structure adjusted all-cause mortality](https://staff.math.su.se/hoehle/blog/2021/03/01/mortadj.html)** (Michael Höhle, 2021, R; from our own department). How much of Germany's 2020 excess mortality is left once you account for an ageing population? Several official sources combined, and the answer flips sign after adjustment. *Between E and C:* the limitations section is a model for yours, but the code lives in a linked R Markdown file rather than in the post, and there is no uncertainty on the excess. The same question with SCB data is a realistic C or A project.

## Data

During the course you’ve seen many ways to source data. Additional public, web-based sources include:

* [Stockholm Open Data Portal](https://dataportalen.stockholm.se/dataportalen/)
* APIs listed on [Sweden’s national data portal](https://www.dataportal.se/en/datasets?p=1&q=&s=2&t=20&f=&rt=esterms_IndependentDataService%24esterms_ServedByDataService&c=false)
* [COVID-19 data (Folkhälsomyndigheten)](https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/statistik-och-analyser/bekraftade-fall-i-sverige/)

We **strongly recommend** using data you collected yourselves and genuinely care about. **Do not use sensitive data.** Your raw data must be legally shareable on GitHub (no licensing or privacy violations).

## What you hand in

1. **The repository:** the full analysis, from raw data (or the script that fetches it) to the final report.
2. **The report:** a blog-style write-up, in Swedish or English, aimed at your audience. Target **~1000–1500 words**, **≤ 7 figures** (tables count as figures) and **≤ 7 visible code chunks** (it’s fine to hide non-essential code). A bigger project does not mean a longer report: say more with less.
3. **The presentation:** a **15–20 minute** talk per group, presenting your question, how you answered it and what you found. **Attendance is compulsory** for the full session in which you present.

> **Pro tip:** Be realistic. Whatever you think you can do—plan for **half** of that and you’ll still be busy. Get a minimal, working version early and iterate.

## Repository, pull requests and hand-in

* Each group gets one **project repository** from the course template: the same `report.qmd`,
  locked environment and check as the assignments.
* **All work goes through pull requests.** Each change is a branch and a pull request, reviewed
  by another group member before it is merged into `main`. This is how teams work in industry,
  and it is part of the C criteria.
* **The hand-in is `main` at the deadline.** You may push and merge early and often; **we look
  at `main` as it is at the deadline**.
* `main` must render from a fresh clone (green check): the report, the data (or the script that
  downloads it, with notes on source and licence), the lockfile, and a README with the title,
  the audience and the one command that renders everything.

See [How we work](/guide) for the workflow.
