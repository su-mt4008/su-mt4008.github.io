# MT4008 Course Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the VitePress course site (IBM Plex, black & white + red accent, light/dark), add a date-aware custom home page driven by one schedule file, and rename MT4007 → MT4008.

**Architecture:** A custom theme extends VitePress’s default theme (CSS variables + fonts). The schedule lives in one typed data file; pure, unit-tested functions derive “current week”, “phase” and “next up” from it. Vue components (`HomePage`, `NextUp`, `WeekList`, `LectureSchedule`, `AssignmentSchedule`) render it; the home page computes dates in the browser after mount.

**Tech Stack:** VitePress 1.6.4, Vue 3 (bundled), TypeScript, Vitest, IBM Plex via Google Fonts.

**Spec:** `docs/superpowers/specs/2026-10-21-course-page-redesign-design.md` · visual reference `docs/superpowers/specs/2026-10-21-home-mockup.html`

All paths are relative to the repo root `/Users/taariqnazar/Documents/SU/teaching/mt4008/course-page`. Work on branch `redesign-ht26`. Never push to `main`.

## Global Constraints

- VitePress **1.6.4** exactly (no 2.0 alpha).
- `srcExclude: ['docs/**', 'mt4008/**']` in the VitePress config.
- Keep `markdown.math: true`, local search, and the `final-grade.md` calculator working.
- URLs do not change: `/homework/*`, `/about`, `/final-grade`, `/lectures/*`, `/project`, `/exam/`.
- Course code is **MT4008** everywhere; GitHub org is `su-mt4008` (https://github.com/su-mt4008).
- Navbar labels, in order: Course info · Lectures · Assignments · Project · Exam (+ search, appearance toggle). “Homework” is relabelled “Assignments” in nav/sidebar/headings; paths stay.
- Theme colours (OKLCH), light → dark: bg `98.5% 0 0`→`17% 0 0`; text `20% 0 0`→`94% 0 0`; muted `48% 0 0`→`70% 0 0`; line `90% 0 0`→`29% 0 0`; faint `85% 0 0`→`36% 0 0`; tint `96% 0 0`→`21% 0 0`; accent `58% .2 27`→`70% .17 28`.
- Links: text-coloured, underlined with `--faint` underline, `--text` on hover. Red accent only for the highlighted week numeral and its label.
- Fonts: IBM Plex Serif (headings, week numerals, site title), IBM Plex Sans (body), IBM Plex Mono (code blocks only). `font-variant-numeric: tabular-nums` on dates.
- No card grids, side-stripe borders, uppercase eyebrow labels, gradients, glows.
- Every unconfirmed value in source is marked `// TODO(owner): …` (see spec “Missing information”).
- All schedule times are Europe/Stockholm; stored as ISO strings with explicit `+01:00` offset (whole course runs in CET).

## Review Focus

1. **Deadline at exactly 23:59 / just after** — a hand-in due `…T23:59:00+01:00` is still “next up” at 23:58 and gone at 00:00. Test in Task 2.
2. **Gap between last teaching week and project/exam (Christmas)** — no “This week” highlight; next up shows project then exam. Test in Task 2.
3. **After the last event** — next up is empty (block hidden), no highlight, week 0 collapsed. Test in Task 2; visual check in Task 4.
4. **Viewer in another timezone** — results depend only on the absolute instant, not the browser’s zone; date labels always render in Europe/Stockholm. Test in Task 2 (`formatWhen` with `TZ` unset).
5. **Phone width (375 px)** — no horizontal scroll, left column stacks above the week list, sticky disabled. Visual check in Task 4.

---

## File Structure

- `package.json` — modify: vitepress 1.6.4, add vitest, `test` script.
- `.vitepress/config.mts` — modify: title/description, nav, sidebar labels, editLink, socialLinks, srcExclude, head fonts.
- `.vitepress/theme/index.ts` — create: extend default theme, register global components.
- `.vitepress/theme/style.css` — create: fonts, colour tokens mapped onto VitePress `--vp-*` vars, link and heading styles.
- `.vitepress/theme/schedule/data.ts` — create: the single schedule file (HT26 provisional).
- `.vitepress/theme/schedule/logic.ts` — create: pure date logic.
- `.vitepress/theme/schedule/logic.test.ts` — create: Vitest tests.
- `.vitepress/theme/components/HomePage.vue`, `NextUp.vue`, `WeekList.vue`, `LectureSchedule.vue`, `AssignmentSchedule.vue` — create.
- `index.md` — replace content with home page.
- `about.md` — add “How a week works” section.
- `lectures/index.md`, `homework/index.md` — replace hard-coded schedule tables with components; MT4008 links; relabel.
- `homework/2.md`, `homework/3.md`, `homework/4.md`, `lectures/week-2.md` — su-mt4007 → su-mt4008.

---

### Task 1: Upgrade, config, rename

**Files:** Modify `package.json`, `.vitepress/config.mts`, `index.md` (hero name only, replaced fully in Task 4), `homework/2.md`, `homework/3.md`, `homework/4.md`, `lectures/index.md`, `lectures/week-2.md`

**Interfaces:** Produces `npm test` (vitest run) and a building site.

- [ ] **Step 1:** `npm install -D vitepress@1.6.4 vitest` (keep `markdown-it-mathjax3`). Add script `"test": "vitest run"`.
- [ ] **Step 2:** In `config.mts`: `title: "MT4008"`, `description: "Course page for MT4008 Statistical Data Processing at Stockholm University"`, `srcExclude: ['docs/**', 'mt4008/**']`, editLink pattern `https://github.com/su-mt4008/su-mt4008.github.io/issues/new?title=:path` with text `Spotted a mistake? Suggest a change`, `socialLinks: [{ icon: 'github', link: 'https://github.com/su-mt4008' }]`.
- [ ] **Step 3:** Nav: `Course info → /about` (activeMatch `^/(about|final-grade)`), `Lectures → /lectures/`, `Assignments → /homework/` (activeMatch `^/homework/`), `Project → /project`, `Exam → /exam/`. Drop the `Home` item (site title links home).
- [ ] **Step 4:** Sidebars: `/lectures/` keeps Week 1–6; `/homework/` group text `Assignments`, items `Overview → /homework/`, `HW1`…`HW5` (remove nothing; there is no HW6); add `/about` and `/final-grade` sidebar group `Course info`: `About the course → /about`, `How a week works → /about#how-a-week-works`, `Grading → /final-grade`.
- [ ] **Step 5:** Replace `su-mt4007` → `su-mt4008` and `MT4007` → `MT4008` in all listed files. Verify:
  Run: `grep -rn "4007" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=cache --exclude-dir=docs --exclude=package-lock.json .`
  Expected: no output.
- [ ] **Step 6:** Run `npm run docs:build`. Expected: build completes with no dead-link errors, and no `docs/` pages in `.vitepress/dist`.
- [ ] **Step 7:** Commit `chore: upgrade VitePress 1.6.4, rename to MT4008, relabel nav`.

### Task 2: Schedule data + date logic (TDD)

**Files:** Create `.vitepress/theme/schedule/data.ts`, `logic.ts`, `logic.test.ts`

**Interfaces — Produces** (exported from `logic.ts`, types also exported):

```ts
export interface Week { n: number; start: string; title: string; link: string; note?: string; hw?: string }
export interface Assignment { id: string; name: string; link: string; due: string; peerDue: string }
export interface Session { weekday: 1 | 4; start: string; end: string; label: string; place: string; link?: string } // start/end "13:00"
export interface CourseEvent { kind: 'project' | 'exam' | 'presentation'; at: string; end?: string; title: string; link: string; blurb: string }
export interface Schedule {
  provisional: boolean
  firstSession: string                 // ISO datetime
  weeks: Week[]                        // start = Monday, "YYYY-MM-DD"
  assignments: Assignment[]
  sessions: Session[]                  // recur weekly during teaching weeks only
  events: CourseEvent[]
  links: { moodle: string; zoom: string; timeedit: string; github: string }
}
export type Phase = 'before' | 'teaching' | 'after-teaching' | 'over'
export interface NextItem { at: Date; kind: 'session' | 'handin' | 'peer' | CourseEvent['kind']; label: string; link?: string }

export function getPhase(now: Date, s: Schedule): Phase
export function getCurrentWeek(now: Date, s: Schedule): number | null
export function getNextUp(now: Date, s: Schedule, count?: number): NextItem[]   // default 2, sorted ascending
export function formatWhen(d: Date, withTime?: boolean): string                // "Mon 2 Nov" / "Mon 2 Nov, 13:00", Europe/Stockholm
```

Rules: week n spans `[start 00:00, start+7d 00:00)` Stockholm. `before` = now < `firstSession`; `teaching` = from first week start until end of last week; `after-teaching` = after that until the end of the last event (`end ?? at`); `over` after. Next-up candidates: each session occurrence in teaching weeks (label e.g. `Q&A on Zoom`), each hand-in (`HW3 hand-in`), each peer review (`HW3 peer review`), each event; include an item while `now < at` (for sessions, while `now < end`).

- [ ] **Step 1: Write `data.ts`** exporting `schedule: Schedule` with `provisional: true`, `// TODO(owner): HT26 dates` and these provisional values: weeks start `2026-11-02`, `-09`, `-16`, `-23`, `-30`, `2026-12-07`; titles/links from the current `lectures/week-1..6.md` H1s and paths (`/lectures/week-n`); week n (1–5) has `hw: 'HWn'`, week 6 none. Assignments HW1–HW5 with names `GitHub test-run`, `Tables and plots`, `Exploring and visualising data`, `SQL and regex`, `Data from the web`, links `/homework/n`, `due` = Monday after the week at `23:59:00+01:00`, `peerDue` = Thursday after at `23:59:00+01:00`. `firstSession: '2026-11-02T13:00:00+01:00'`. Sessions: Mon `13:00–16:00` `Live demo and help` `on campus`; Thu `13:00–16:00` `Q&A` `on Zoom` with Zoom link. Events: project `2027-01-08T23:59:00+01:00` (link `/project`, blurb `An individual, reproducible analysis of a dataset you choose.`), exam `2027-01-11T08:00:00+01:00` end `11:00` (link `/exam/`, blurb `Written, on campus. What it covers and how to prepare.`). Links: moodle `https://kurser.math.su.se/course/view.php?id=1631` (TODO), zoom = current Zoom link from `lectures/index.md`, timeedit = current link (TODO HT26), github `https://github.com/su-mt4008`.
- [ ] **Step 2: Write failing tests** in `logic.test.ts` against `schedule` (dates as `new Date('…+01:00')`):
  - `getPhase` → `'before'` at `2026-10-21T12:00`, `'teaching'` at `2026-11-18T10:00`, `'after-teaching'` at `2026-12-24T12:00`, `'over'` at `2027-01-12T09:00`.
  - `getCurrentWeek` → `1` at `2026-11-02T00:00`, `3` at `2026-11-22T23:59`, `4` at `2026-11-23T00:00`, `null` at `2026-12-24T12:00`, `null` at `2026-10-21T12:00`.
  - `getNextUp` at `2026-11-18T10:00` → labels `['Q&A on Zoom', 'HW2 peer review']` with dates `2026-11-19T13:00` and `2026-11-19T23:59`, in that order (session first since it starts earlier).
  - Review focus 1: HW1 hand-in (`2026-11-09T23:59`) is in `getNextUp(…, 10)` at `2026-11-09T23:58` and absent at `2026-11-10T00:00`.
  - Review focus 2: at `2026-12-24T12:00` → kinds `['project', 'exam']`.
  - Review focus 3: at `2027-01-12T09:00` → `[]`.
  - Before phase: at `2026-10-21T12:00` first item is the Mon 2 Nov 13:00 session.
  - Review focus 4: `formatWhen(new Date('2026-11-19T23:59:00+01:00'), true)` === `'Thu 19 Nov, 23:59'` and `formatWhen(new Date('2026-11-02T00:30:00+01:00'))` === `'Mon 2 Nov'` (fails if browser/UTC zone is used).
- [ ] **Step 3:** Run `npm test`. Expected: FAIL (functions not defined).
- [ ] **Step 4:** Implement the four functions in `logic.ts`. `formatWhen` uses `Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Stockholm', weekday: 'short', day: 'numeric', month: 'short', hour/minute when withTime, hourCycle: 'h23' })` and assembles parts so the output is exactly `Thu 19 Nov, 23:59`.
- [ ] **Step 5:** Run `npm test`. Expected: all pass.
- [ ] **Step 6:** Commit `feat: schedule data and date logic`.

### Task 3: Theme (fonts, colours, light/dark)

**Files:** Create `.vitepress/theme/index.ts`, `.vitepress/theme/style.css`; modify `.vitepress/config.mts` (head)

**Interfaces — Produces:** CSS custom properties `--c-bg`, `--c-text`, `--c-muted`, `--c-line`, `--c-faint`, `--c-tint`, `--c-accent` on `:root` and `.dark`; `--font-serif`, `--font-sans`, `--font-mono`. Theme default export `{ extends: DefaultTheme, enhanceApp }` registering components globally (components added in Task 4/5; register them there).

- [ ] **Step 1:** Add Google Fonts `<link>` (preconnect + `IBM Plex Sans 400;500;600`, `IBM Plex Serif 400;500;600`, `IBM Plex Mono 400;500`, `display=swap`) via `head` in config.
- [ ] **Step 2:** In `style.css` define tokens from Global Constraints and map them: `--vp-c-bg`, `--vp-c-bg-alt` (tint), `--vp-c-bg-soft` (tint), `--vp-c-text-1` (text), `--vp-c-text-2` (muted), `--vp-c-divider` / `--vp-c-border` (line), `--vp-c-brand-1/2/3` (text, so active nav/sidebar items are black/white, not coloured), `--vp-font-family-base` (sans), `--vp-font-family-mono` (mono). Headings `h1–h3` in `.vp-doc` and `.VPNavBarTitle` use serif. `.vp-doc a`: colour text, `text-decoration: underline`, underline colour faint, hover text.
- [ ] **Step 3:** Run `npm run docs:dev` and check: `/lectures/week-1` (math, code blocks), `/final-grade` (calculator works), `/homework/` in both appearances via the toggle; no blue left anywhere; code blocks readable in dark.
- [ ] **Step 4:** `npm run docs:build` passes. Commit `feat: IBM Plex black-and-white theme`.

### Task 4: Home page

**Files:** Create `.vitepress/theme/components/HomePage.vue`, `NextUp.vue`, `WeekList.vue`; modify `.vitepress/theme/index.ts`, `index.md`

**Interfaces:** Consumes `schedule`, `getPhase`, `getCurrentWeek`, `getNextUp`, `formatWhen` (Task 2) and theme tokens (Task 3). Produces global component `<HomePage />`.

- [ ] **Step 1:** `index.md` becomes frontmatter `layout: page`, `sidebar: false`, `aside: false`, `editLink: false`, body `<HomePage />`.
- [ ] **Step 2:** `HomePage.vue`: holds `now = ref<Date | null>(null)`, sets `now.value = new Date()` in `onMounted` (and every 60 s). Until mounted, use the build-time phase from `getPhase(new Date(), schedule)` so SSR output is sensible. Two-column grid (`330px` / `1fr`, gap `72px`, left sticky `top: calc(var(--vp-nav-height) + 24px)`), single column below `960px` with sticky off. Left: `<h1>` “Statistical Data Processing”, sentence “Getting, cleaning, exploring and explaining data, in a way someone else can rerun. Python or R, your choice.”, `<NextUp>`, link row Moodle · Zoom · TimeEdit · GitHub from `schedule.links`. If `schedule.provisional`, a muted line “Dates are provisional.” under the links.
- [ ] **Step 3:** `NextUp.vue` (props `items: NextItem[]`, `phase: Phase`): heading “Next up”; each item as bold `formatWhen(at, true)` then label (linked when `link`). In `before` phase add muted “Set up before then — see week 0.”. Renders nothing when `items` is empty.
- [ ] **Step 4:** `WeekList.vue` (props `schedule`, `phase`, `currentWeek`): week 0 entry “Get set up”, date line `Before ${formatWhen(firstSession)}`. Expanded when `phase === 'before'` with red “Start here” and four steps: `Read how the course works` → `/about` (5 min); `Install Git and Python or R` → `/lectures/week-1#install-the-essentials` (30 min); `Create a GitHub account and register it on Moodle` → `/lectures/week-1#quick-admin` (10 min) `<!-- TODO(owner): org-join process -->`; `Join the course on Moodle` → moodle link (“Hand-ins go here”); then “Then go to Week 1, before the first session on {date}.” Otherwise one line: How the course works · Setup guide (`/lectures/week-1#install-the-essentials`) · Moodle. Weeks 1–6 then Project/Exam exactly as in the mockup (numeral, date + note, serif title link, line with `HWn` link + name + `due {formatWhen(due)}`; no Quiz link yet). Highlight (`--c-accent` numeral + “This week”) on `currentWeek`; week 0 highlighted in `before`.
- [ ] **Step 5:** Register `HomePage` in `index.ts`. Run `npm run docs:dev`; compare `/` with the mockup in light and dark. To check states, temporarily pass a fixed date (e.g. `?now=2026-11-18T10:00` read in `onMounted`, dev-only via `import.meta.env.DEV`) and check: before (`2026-10-21`), teaching (`2026-11-18`), Christmas (`2026-12-24`), over (`2027-01-12`) — Review focus 2 and 3.
- [ ] **Step 6:** Resize to 375 px: no horizontal scroll, left column first, not sticky (Review focus 5).
- [ ] **Step 7:** `npm test && npm run docs:build` pass. Commit `feat: date-aware home page`.

### Task 5: Course info + generated schedule tables

**Files:** Create `.vitepress/theme/components/LectureSchedule.vue`, `AssignmentSchedule.vue`; modify `.vitepress/theme/index.ts`, `about.md`, `lectures/index.md`, `homework/index.md`

**Interfaces:** Consumes `schedule`, `formatWhen`. Produces global `<LectureSchedule />`, `<AssignmentSchedule />`.

- [ ] **Step 1:** `LectureSchedule.vue`: table Week · Monday · Topic (link); `AssignmentSchedule.vue`: table Assignment (link + name) · Hand-in · Peer review, dates via `formatWhen(…, true)`. Register both.
- [ ] **Step 2:** In `lectures/index.md` replace the `## Schedule` table with `<LectureSchedule />`; in `homework/index.md` retitle `# Assignments`, `## Schedule (2025)` → `## Schedule`, replace its table with `<AssignmentSchedule />`. Leave other prose as is.
- [ ] **Step 3:** Add `## How a week works` to `about.md` after “How the course runs”: an ordered list — any time: work through the week’s material (and quiz, when available); Monday 13–16 on campus: live demo of last week’s material, then help; Thursday 13–16 on Zoom: open Q&A; next Monday 23:59: hand in the assignment on Moodle; next Thursday 23:59: peer review a classmate. Times Stockholm. Mark `<!-- TODO(owner): review -->`.
- [ ] **Step 4:** `npm run docs:build` passes (no dead links, anchor `/about#how-a-week-works` resolves). Commit `feat: course info section and generated schedules`.

---

## Self-review notes

- Spec coverage: look/theme (T3), navigation & rename (T1), home left/right column + date awareness (T4), single schedule source (T2, T5), course info (T1, T5), inner pages keep doc layout with prev/next (default theme, T3). Quizzes: out of scope; Quiz links omitted until they exist. Lecture-page reordering is content work and is not done now (spec non-goal on rewriting content).
- Missing owner info is all behind `TODO(owner)` in `data.ts`, `about.md` and `WeekList.vue`.
