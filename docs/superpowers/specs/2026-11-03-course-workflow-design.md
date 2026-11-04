# MT4008 HT26: how students work and hand in

Status: agreed in conversation, pending final read (2026-11-03). Covers the course's working structure: sessions,
hand-in, reproducibility tooling and how students learn it. Lecture content, the assignment
texts and week 6 are separate pieces of work that build on this.

## Intent

MT4008 teaches **the science of data science** to students with no background: asking a
question the data can answer, choosing a method, checking the work, stating uncertainty and
limitations, and making everything reproducible. Code matters less than it used to (AI writes
it); the habits and the industry tools are the point.

The way students work and hand in should itself teach those habits. Every assignment is
practice in the workflow a professional data scientist uses: a Git repository, a branch, a pull
request, code review, a locked environment, a report that renders from raw data with one
command, and an automatic check that proves it runs on a clean machine.

## Goals

- Students hand in every assignment as a **pull request** on GitHub, and peer review and teacher
  feedback happen as **code review on that pull request**.
- Every hand-in is **checked automatically for reproducibility**: a fresh machine installs the
  locked environment and renders the report. Green means it runs from a fresh clone.
- Students use **VS Code** (or Positron for R) as their one tool: editor, Git, terminal, Quarto,
  pull-request review.
- Reports are **Quarto** documents (`.qmd`), so they work for Python and R, render to a page
  readable on GitHub, and diff cleanly in pull requests.
- Environments are **locked**: `uv` (pyproject.toml + uv.lock) for Python, `renv` (renv.lock) for R.
- **Students are never asked to do something the course has not shown them how to do.**

## Non-goals

- Automatic grading. The check proves reproducibility, nothing more. (Grading mechanics are
  removed from the site altogether.)
- Teaching Git from the command line in depth. VS Code's Source Control is the main interface;
  the guide shows the few equivalent commands.
- Rewriting weeks 2–6 here (separate work), apart from what this structure requires.

## Anti-goals (a failure even if it technically works)

- Students spending week 1 fighting installs instead of learning.
- A red check students cannot understand or fix on their own.
- Workflow steps described only in the teachers' heads or scattered across pages.
- Running out of GitHub Actions minutes mid-term without noticing.

## Decided

**Sessions.** No lectures and no live demos. Students work through the material on their own;
the two weekly sessions (Mon and Thu 13:00–17:00, Albano lecture room 19) are work time with the
teachers in the room. Mondays open with a 15–30 minute walkthrough of the week; Thu 5 Nov is the
course introduction instead. Coming to sessions is strongly encouraged. (Already on the site.)

**Hand-in flow, per assignment:**
1. The student has a private repo for the assignment in the `su-mt4008` organisation, created
   from a template (see Template).
2. They work on a branch (e.g. `hw1`), commit and push.
3. They open a pull request into `main` titled `HW<n>`. Opening it by the deadline (Monday 23:59)
   is the hand-in.
4. The automatic check runs on the pull request.
5. The assigned peer reviews the pull request by Thursday 23:59 (comments on lines, an overall
   review). Reviewers have access to the repo.
6. The teacher reviews the same pull request. The student pushes fixes as new commits; the
   pull request is merged when accepted.

Issues as the submission signal are retired; the existing `ready-for-grading` label goes with them.

**Template repository** (one per language: `hw-template-python`, `hw-template-r`; builder's
call on exact names):

```
report.qmd        sections: Question · Data · Cleaning · Exploration · Analysis ·
                  Conclusions & limitations · How to reproduce — each with a one-line prompt
data/raw/         raw data, never edited by hand (or a script that downloads it)
src/              functions the report uses
pyproject.toml + uv.lock   or   renv.lock (+ renv/ activation files)
.gitignore
README.md         what every file is for; the one command that renders the report
.github/workflows/check.yml
```

The same structure is the starting point for the group project.

**The automatic check** (GitHub Actions, `check.yml`): on pull requests only; installs Quarto and
the locked environment (cached); renders `report.qmd`; fails with a message that points to the
guide page. Cost controls: run on `pull_request` only, cache dependencies, `concurrency` with
cancel-in-progress, `timeout-minutes: 10`.

Budget: a free organisation has 2,000 Actions minutes/month for private repos (3,000 on Team).
Estimate ~2 min per run; 40 students × 5 assignments × ~5 runs ≈ 2,000 min, spread over Nov–Dec.
Without a payment method, running out stops checks rather than billing. Apply for the GitHub
Education teacher upgrade of the organisation.

**Habits taught from week 1:** raw data is never edited by hand; relative paths only; set random
seeds; restart and run everything before pushing; one command renders the report.

**How students learn it** — three places:
1. **A "How we work" guide page** on the site, linked from every assignment and from the check's
   failure message. Step by step with screenshots: install VS Code (+ Python/Jupyter/Quarto/R
   extensions, GitHub Pull Requests extension), sign in to GitHub, clone, branch, commit, push,
   open a pull request, read a red/green check and fix a red one, review a peer's pull request,
   the `uv`/`renv` and `quarto render` commands and what they do.
2. **Week 1 material rewritten** around this workflow: why reproducibility, project layout, a
   locked environment, Quarto, Git in VS Code, the first pull request. Replaces GitHub Desktop,
   conda/Miniconda and the functional-programming section.
3. **HW1 = the workflow once, end to end**, on a tiny provided dataset, so students learn the
   hand-in before any real analysis.

## Changed 2026-11-03: one repository per student

Decided by the teachers after the first build: **one repository per student for all five
assignments**, `<username>-assignments`, from an assignments template with `example/` and
`hw1/` … `hw5/` folders, one shared lockfile and a `_quarto.yml` so `quarto render` renders every
report. Each assignment is a branch `hwN` and a pull request `HWN` that only changes `hwN/`.
Reviewers are added after the Monday deadline and removed on Friday morning (GitHub read access
is repository-wide; branches cannot be hidden). Group projects use the single-report project
templates. This supersedes "one private repo per student per assignment" below.

## Calls made by Claude (check these)

- **Rendered output is committed.** `report.qmd` renders to `report.md` (GitHub-flavoured
  Markdown) plus its figures, and both are committed, so peers and teachers see results directly
  in the pull request on GitHub. The check renders from scratch and must succeed; it does not
  compare its output byte-for-byte with the committed render (too brittle for beginners).
- **Codespaces is a fallback for students whose install fails, not the default.**

## Answered by the teachers (2026-11-03)

1. **HW1 uses the new pull-request flow** this term (due Mon 9 Nov). Everything HW1 needs must be
   live by the course introduction on Thu 5 Nov: the templates with their check, the guide page,
   the rewritten week 1 and the new HW1 page.
2. **Repositories and peer access are the teachers' job**, with their own existing scripts. The
   template and guide must match: one private repo per student per assignment, created from the
   template; the peer reviewer is given access after the Monday deadline.
3. **Organisation plan:** the teachers apply for the GitHub Education upgrade (GitHub Team). Until
   it lands, `main` cannot be protected on private repos, so working through pull requests is an
   instruction (taught in the guide and HW1), not an enforced rule. Once on Team, add a ruleset
   requiring a pull request into `main`.
4. **Python and R are both available from HW1** (interpretation of the teachers' answer, to be
   confirmed): two templates, and the guide covers both. Students pick one language for the course.
5. **The project uses pull requests too**: the same template and check. Within a group, all work
   goes through pull requests with review by a group member; the hand-in is `main` at the deadline.
6. **After the deadline:** the pull request must be open by Monday 23:59; a red check still counts
   as handed in but must be fixed; the teachers' script tags the state at the deadline.

## Left to the builder

- Exact workflow YAML, caching keys, Quarto version pinning, R/Python package lists for the template.
- Exact layout and screenshots of the guide page; where it sits in the navigation (Course info
  or Assignments).
- Wording of the check's failure message.
- Updating the Assignments overview, HW pages and Project page to the pull-request flow
  (replacing the issue-based instructions).
