# MT4008 course page redesign (HT26)

Date: 2026-10-21 · Repo: `su-mt4008/su-mt4008.github.io` (this repo) · Branch: `redesign-ht26`
Visual reference: [`2026-10-21-home-mockup.html`](./2026-10-21-home-mockup.html) (open in a browser; the brainstorm frame CSS is missing, but the page itself renders; use the “Before / During week 3” buttons and the “Dark / light” link).

## Intent

The course page is the single place where students find everything about the course: lectures, assignments, project, exam, grading. Today it is hard to navigate. The redesign makes the structure obvious, gives new students a clear starting path, and gives the site a calm, deliberate look that does not read as templated or AI-generated.

Last year’s site is preserved under the existing git tag `2025`.

## Goals

- A student can reach any lecture, assignment, the project or the exam in one click from the home page.
- A new student knows exactly what to do first (week 0) and what comes next.
- A returning student sees what is next (session or deadline) without hunting.
- Light and dark mode, both first-class.
- Course is **MT4008** everywhere (was MT4007).

## Non-goals (now)

- Quizzes. They come later (see “Planned: quizzes”), but lecture pages must leave room for them.
- Rewriting the course content itself (lecture text, assignment text). Only structure, navigation, naming and styling change, plus the new home page and week 0.
- Moving away from VitePress.

## Anti-goals

- Anything that looks like a generic template or AI output: card grids, coloured side-stripes on boxes, uppercase “eyebrow” labels, gradients, glows, icon-per-heading, monospace used as decoration, marketing-style hero.
- Duplicated navigation (the same link in three places) or content repeated on several pages.

## Constraints

- VitePress, upgraded from 1.4.x to **1.6.4** (latest stable; do not use the 2.0 alpha).
- Deployed by `.github/workflows/deploy.yml` on push to `main`. Do not push to `main` as part of this work; the user reviews locally (`npm run docs:dev`) first.
- `docs/` must be excluded from the VitePress build (`srcExclude: ['docs/**', 'mt4008/**']`); `mt4008/` is an unrelated empty folder in the working tree.
- Math (`markdown.math: true`) and local search must keep working.
- `final-grade.md` contains an interactive Vue grade calculator; it must keep working.

## Decided

### Look

- **Fonts:** IBM Plex Serif (headings, week numerals, site name) + IBM Plex Sans (everything else), via Google Fonts or self-hosted. Tabular figures for dates. No monospace except real code blocks (IBM Plex Mono is fine there).
- **Theme: black & white with a single red accent** (“6a” in the brainstorm). Values (OKLCH):
  - Light: bg `oklch(98.5% 0 0)`, text `oklch(20% 0 0)`, muted `oklch(48% 0 0)`, line `oklch(90% 0 0)`, faint (inactive numerals) `oklch(85% 0 0)`, tint (week-0 panel) `oklch(96% 0 0)`, accent `oklch(58% .2 27)`.
  - Dark: bg `oklch(17% 0 0)`, text `oklch(94% 0 0)`, muted `oklch(70% 0 0)`, line `oklch(29% 0 0)`, faint `oklch(36% 0 0)`, tint `oklch(21% 0 0)`, accent `oklch(70% .17 28)`.
  - Links are text-coloured and **underlined** (faint underline, darker on hover), not coloured. Red is used only to mark the highlighted week (its numeral and its “Start here” / “This week” label).
- Light/dark uses VitePress’s built-in appearance toggle, restyled.

### Navigation

- Top navbar on every page: site name **MT4008** (links home) · Course info · Lectures · Assignments · Project · Exam · Search · light/dark.
- “Homework” is renamed **Assignments** in all labels.
- **Course info** groups: how the course works (current `about.md`), how a week works, grading (current grading text + `final-grade.md` calculator).

### Home page (custom layout, see mockup)

Two columns on desktop; stacks to one column on mobile (left column first, but compact).

**Left column** (sticky on desktop), only:
1. Title “Statistical Data Processing” + one sentence: what the course is, “Python or R, your choice.”
2. **Next up:** the next two calendar items (a session or a deadline), each as date/time + what it is + link where relevant. Before the course starts: the first session and “Set up before then — see week 0.” After the exam: hide the block.
3. One row of links: **Moodle · Zoom · TimeEdit · GitHub** (GitHub = https://github.com/su-mt4008).

**Right column**, a single list read top to bottom:
- **Week 0 — “Get set up”.** Four steps, each a link with a time hint: read how the course works; install Git and Python or R; create a GitHub account and join the course organisation; join the course on Moodle. Ends with “Then go to Week 1, before the first session on <date>.” Before the course starts, week 0 is expanded and highlighted with a red “Start here”. Once the course has started it collapses to one line of links (How the course works · Setup guide · Moodle).
- **Weeks 1–N**, one entry each: large serif numeral, Monday date (plus any note, e.g. guest lecture), lecture title (links to the lecture page), then a line with the assignment (`HWn` link + short name + due date) and a Quiz link (hidden until quizzes exist). The current week’s numeral is red with a “This week” label; other numerals are faint.
- **Project** and **Exam** side by side below a heavy rule, each with date, title link, one-line description.
- Footer: “Spotted a mistake? Suggest a change on GitHub.” (edit link → `su-mt4008` repo).

**Date awareness:** “this week”, week 0 expanded/collapsed, and “Next up” are computed in the browser from the current date (not at build time, so the deployed static site never goes stale). Render a sensible default on the server and update on mount, without layout jump.

### Single source of truth for the schedule

All dates, titles and links shown on the home page (and ideally the lectures and assignments index tables) come from one data file (e.g. `.vitepress/schedule.ts` or a YAML/JSON file): weeks (number, Monday date, title, lecture link, notes), assignments (id, short name, hand-in deadline, peer-review deadline, link), sessions (recurring Mon on campus 13–16, Thu Zoom 13–16, plus one-offs), project deadline, exam date/time, first-session date. Updating the term means editing that one file.

### Rename MT4007 → MT4008

Replace every occurrence, including `github.com/su-mt4007/...` links (the GitHub org was renamed to `su-mt4008`; old URLs redirect, new ones are canonical). Currently in: `.vitepress/config.mts` (description, editLink, commented socialLinks), `index.md`, `homework/2.md`, `homework/3.md`, `homework/4.md`, `lectures/index.md`, `lectures/week-2.md`. Also fix the editLink to point at `su-mt4008/su-mt4008.github.io`.

### Inner pages

Lecture, assignment, project, exam and course-info pages keep VitePress’s doc layout (sidebar + outline) but use the new fonts and theme. Each lecture page follows the same order: goals, material (reading/videos/demo code), linked assignment with deadlines, and a reserved spot at the end for the quiz; plus previous/next links.

## Planned: quizzes (not in this build)

Each lecture will end with a short self-check quiz: multiple choice, instant feedback on each wrong answer explaining why, all in the browser, nothing stored, not graded. Design the lecture page so a `<Quiz>` component can be dropped in at the end later; questions will live next to the lecture (e.g. in frontmatter or a sibling file).

## Left to the builder

- How to implement the custom home layout (Vue component via `layout: home` override, a custom `Layout` slot, or a page-level component), and how to extend the default theme.
- Font loading strategy (Google Fonts vs self-hosted) and exact type scale/spacing, matching the mockup.
- Data file format and shape.
- Mobile layout details, as long as nothing is hidden on mobile.
- Whether the lectures/assignments index pages are generated from the data file or kept as Markdown (preferred: generated, so dates live in one place).

## Decisions after review

Marked *(Claude’s call)* where the course owner has not confirmed; they can override.

- **Weeks and assignments:** 6 lecture weeks, 5 assignments (HW1–5), matching the repo and the “3 of 5” grading rule. Week 6 (LLMs) has no assignment; its lecture page stays as is. No week 7 entry. *(Claude’s call, from repo)*
- **URLs unchanged:** labels change (“Homework” → “Assignments”), paths stay: `/homework/*`, `/about`, `/final-grade`. “Course info” is a navbar group/sidebar covering `/about`, a new `/how-a-week-works` section (or anchor in `/about`), and `/final-grade`. *(Claude’s call)*
- **Next up:** the next two upcoming items among sessions, hand-in deadlines and peer-review deadlines. Recurring sessions (Mon on campus, Thu Zoom) only during teaching weeks. After the last teaching week: project, exam, presentations. Hidden after the last item. No “This week” highlight outside teaching weeks. *(Claude’s call)*
- **Week 0 links:** point into the existing setup sections of `lectures/week-1.md`; no lecture content is rewritten now. *(Claude’s call)*
- **“How a week works”:** written by Claude from existing text in `about.md`, `lectures/index.md` and `homework/index.md`, for the owner to review.
- **Dates for local review:** provisional HT26 dates in the schedule file, flagged `provisional: true`; the site shows a small “Dates are provisional” note while that flag is set. *(Claude’s call)*

## Missing information (placeholders in use)

Each placeholder is marked `TODO(owner)` in the source.

1. HT26 dates: first session, each Monday, assignment and peer-review deadlines, project deadline, exam date/time, project presentations. Provisional: weeks start Mon 2 Nov 2026, one week per week, project due Fri 8 Jan 2027, exam Mon 11 Jan 2027 08:00–11:00.
2. HT26 TimeEdit link (current one is HT25).
3. Correct Moodle course link (`id=1631` in `index.md` vs `id=1333` in `lectures/week-1.md`). Using `id=1631`.
4. How students join the GitHub organisation (placeholder: “Post your GitHub username on Moodle; you’ll get an invite”, as in HT25).
5. Zoom link for HT26 (using the current one).
6. Guest lecture for HT26, if any (HT25 note removed).
