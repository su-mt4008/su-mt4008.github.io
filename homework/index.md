# Assignments

The homework component has **5 assignments**, each paired with a **peer review** of a classmate’s work.
Each assignment is scored **0–100**, and you need **65** to pass it.

**Hand in on time.** Every on-time assignment gets a **peer review**, and reviewing a classmate’s
work is **required**. A late assignment misses the peer review and loses **30 points** instead. The **final deadline**
for all assignments, late or not, is **{{ $course.finalDeadline }}**. If you miss it,
you will have to redo **all** assignments in the next edition of the course.

Each homework aligns with the weekly material (e.g., **HW1 ↔ Week 1**, **HW2 ↔ Week 2**, …).

## At a Glance

* **Workload:** 5 assignments + 5 peer reviews
* **Deadlines per homework:** hand-in **Monday 23:59**, peer review **Thursday 23:59**, final version **Friday 23:59** (Europe/Stockholm)
* **Graded version:** your pull request as it stands on **Friday 23:59**, after you have had the chance to act on the review.
* **Scoring (per homework):** 0–100 points; **65** to pass.
* **Peer review:** required for every on-time assignment.
* **Late hand-in:** **−30 points**, and no peer review.
* **Final deadline for all assignments:** **{{ $course.finalDeadline }}**. Missing it means redoing all assignments in the next edition of the course.

## How Assignments Work

Each assignment contains a few tasks covering material from previous week(s).
**Write a short, blog-style report** in `report.qmd`, following the seven sections of the template (Question → Data → Cleaning → Exploration → Analysis → Conclusions & limitations → How to reproduce)—**not** a bullet-point list of answers.

### Hand-in

Every assignment is handed in as a **pull request** on GitHub. The full step-by-step is on
[How we work](/guide#hand-in-an-assignment); in short:

1. We create **one** private repository for you, **`<username>-assignments`**, from the course
   template. It is the same for Python and R, and has a folder per assignment: `hw1/` … `hw5/`.
   New here? Start with [Get started](/guide#get-started).
2. For each assignment, work on a branch `hw<n>` in the folder `hw<n>/`, render its
   `report.qmd`, commit and push.
3. Open a pull request **from `hw<n>` into `main`** titled **`HW<n>`** by the Monday deadline.
   *Opening the pull request is the hand-in.* Pushing straight to `main` is not.
4. The **check** renders your report on a clean computer. A red check still counts as handed in,
   but you must fix it ([how](/guide#when-the-check-is-red)).

### After Feedback

* Fix what the review points out by pushing new commits to the same branch **until Friday 23:59**;
  they appear in the same pull request. Reply to each comment saying what you changed.
* **We grade the version on Friday 23:59**: the latest state of your pull request at that time.
* Don’t merge the pull request yourself; we merge it when it is accepted.

## Peer Review

After the deadline you get access to a classmate’s repository, until Friday morning. Review their pull request: read the rendered report, then comment on specific lines of code ([how](/guide#review-a-pull-request)).

Address at least:

* **Coverage:** Has the student completed all required tasks?
* **Highlights:** What’s especially clear, effective, or well done?
* **Clarity issues:** What’s confusing or could be improved?

**Peer-review deadline:** **Thursdays 23:59 (Europe/Stockholm)** for the corresponding homework.

## Schedule

All times are **Europe/Stockholm**. Assignments are due **Monday 23:59**, peer reviews **Thursday 23:59**, and the final version, which is graded, **Friday 23:59**.

<AssignmentSchedule />

---

## Notes & Reminders

* **Format:** A short, readable report (`report.qmd`, rendered to `report.md`) with clear explanations and a few well-chosen figures.
* **Reproducibility:** Your repository must render from a fresh clone; the check on your pull request tests exactly that.
* **Peer-review tone:** Be kind, specific, and actionable—aim to help your classmate improve.
* **Late work:** A late assignment loses 30 points and is not peer reviewed. Nothing is accepted after **{{ $course.finalDeadline }}**.

## Academic Integrity & Tools

* You may use standard libraries and course-approved tools. If you consult external sources or AI assistants, **cite what you used and how**.
* All code and writing you submit must be **your own** and reflect your understanding.
