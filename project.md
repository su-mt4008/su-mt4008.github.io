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

## Inspiration

A few examples of scope and style:

* [The Olympic Medal Table Visualized Gapminder Style](https://staff.math.su.se/hoehle/blog/2016/08/21/gapMedal.html)
* [On a First Name Basis with Statistics Sweden](https://staff.math.su.se/hoehle/blog/2017/03/25/scbnames.html)
* [Baby Weight Shiny app](https://shirinsplayground.netlify.app/2020/09/baby_weight_app/)
* [Are #python users more likely to get into Slytherin?](https://masalmon.eu/2018/01/01/sortinghat/)

## Data

During the course you’ve seen many ways to source data. Additional public, web-based sources include:

* [Stockholm Open Data Portal](https://dataportalen.stockholm.se/dataportalen/)
* APIs listed on [Sweden’s national data portal](https://www.dataportal.se/en/datasets?p=1&q=&s=2&t=20&f=&rt=esterms_IndependentDataService%24esterms_ServedByDataService&c=false)
* [COVID-19 data (Folkhälsomyndigheten)](https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/statistik-och-analyser/bekraftade-fall-i-sverige/)

We **strongly recommend** using data you collected yourselves and genuinely care about. **Do not use sensitive data.** Your raw data must be legally shareable on GitHub (no licensing or privacy violations).

## What you hand in

1. **The repository:** the full analysis, from raw data (or the script that fetches it) to the final report.
2. **The report:** a blog-style write-up, in Swedish or English, aimed at your audience.
   <!-- TODO(owner): report length and figure limits for the larger group projects? -->
3. **The presentation:** a **5-minute** talk whose goal is to convince the class to read your report. **Attendance is compulsory** for the full session in which you present.
   <!-- TODO(owner): presentation length for groups? -->

> **Pro tip:** Be realistic. Whatever you think you can do—plan for **half** of that and you’ll still be busy. Get a minimal, working version early and iterate.

## Submission & Reproducibility

* Push to your group’s `project` course repo and **open an issue** to signal submission. You may push early and often; **we will look at the version that exists at the deadline**.
* Include:

  * A **clear notebook** (Jupyter/R Markdown) that reproduces your analysis end-to-end.
  * The **data** you used (or a script that downloads it), and brief notes on source/licensing.
  * A short **README** with: title, audience, how to run, and any package requirements.

    > If you used extra packages, list them at the top of the notebook or in a simple `requirements.txt`/`install` note.
* We will clone your repo and **run the notebook**. Make sure it runs cleanly from a fresh checkout.
