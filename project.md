# Project

- **Deadline:** **{{ $course.project }} (Stockholm time)**
- **Presentations:** **{{ $course.presentation }}**, {{ $course.presentationRoom }}

## Overview

Your individual project is a **blog-style data story** based on a **unique dataset you collect yourself**. Use the course tools to obtain, transform, explore, visualize, and explain your data.

**Submission**: push your work to your course GitHub `project` repository and
**open an issue**. You may push early and often; **we will look at the version
that exists at the deadline**.

**Presentation**: a **max 5-minute** talk in front of the class. **Attendance is
compulsory** for the full session in which you present.

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

We **strongly recommend** using data you personally collected and genuinely care about. **Do not use sensitive data.** Your raw data must be legally shareable on GitHub (no licensing or privacy violations).

## What to do

1. **Find data “in the wild.”** This could be an open SQL database, an API, web-scraped data, personal logs (running watch, app exports), or hobby data.
2. **Decide on a story.** Examples: test a simple hypothesis, create a compelling visualization, write an educational explainer, or do a small piece of data journalism. Define your **audience** up front (general public, BSc students, *ornithologists*, …).
3. **Analyze.** Read → wrangle → visualize → summarize. Keep the story from step 2 in focus and interpret results accordingly.
4. **Write the post.** Swedish or English. Target **~1000–1500 words**, **≤ 7 figures** (tables count as figures), and **≤ 7 visible code chunks** (it’s fine to hide non-essential code). The post must be **reproducible**.
5. **Present.** Prepare a **5-minute** talk whose goal is to convince your classmates to read your post.

> **Pro tip:** Be realistic. Whatever you think you can do—plan for **half** of that and you’ll still be busy. Get a minimal, working version early and iterate.

## Submission & Reproducibility

* Push to your `project` course repo and **open an issue** to signal submission.
* Include:

  * A **clear notebook** (Jupyter/R Markdown) that reproduces your analysis end-to-end.
  * The **data** you used (or a script that downloads it), and brief notes on source/licensing.
  * A short **README** with: title, audience, how to run, and any package requirements.

    > If you used extra packages, list them at the top of the notebook or in a simple `requirements.txt`/`install` note.
* We will clone your repo and **run the notebook**. Make sure it runs cleanly from a fresh checkout.
