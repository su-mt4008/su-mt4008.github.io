# Assignments

The homework component has **5 assignments**, each paired with a **peer review** of a classmate’s work.
Each assignment is scored **0–100**, and you need **65** to pass it.

**Hand in on time.** A late assignment loses **15 points**. The **final deadline**
for all assignments, late or not, is **{{ $course.finalDeadline }}**. If you miss it,
you will have to redo **all** assignments in the next edition of the course.

Each homework aligns with the weekly material (e.g., **HW1 ↔ Week 1**, **HW2 ↔ Week 2**, …).

## At a Glance

* **Workload:** 5 assignments + 5 peer reviews
* **Deadlines per homework:** Assignment **Monday 23:59**, Peer Review **Thursday 23:59** (Europe/Stockholm)
* **Scoring (per homework):** 0–100 points; **65** to pass.
* **Late hand-in:** **−15 points**.
* **Final deadline for all assignments:** **{{ $course.finalDeadline }}**. Missing it means redoing all assignments in the next edition of the course.

## How Assignments Work

Each assignment contains a few tasks covering material from previous week(s).
**Submit a short, blog-style report** with explanations and a clear workflow—**not** a bullet-point list of answers.

### Submission Flow

1. Push your work to **your homework GitHub repository** (e.g., `homework-1`). Include a short, readable **report** (notebook or markdown) in the repo.
2. **Open an issue** in that repo titled **`HW# – Submission`** (e.g., `HW1 – Submission`).
   *We only look at assignments with this issue.*
   *(If you use labels, add `ready-for-grading`.)*

### After Feedback

* You may **fix mistakes** pointed out in the feedback. Commit your changes.
* Add a **comment under the closed submission issue** describing what you changed.
* We’ll take another look.

## Peer Review

You’ll be assigned a partner (announced in class or on Moodle). Read their report and code, then leave constructive feedback under **their submission issue**.

Address at least:

* **Coverage:** Has the student completed all required tasks?
* **Highlights:** What’s especially clear, effective, or well done?
* **Clarity issues:** What’s confusing or could be improved?

**Peer-review deadline:** **Thursdays 23:59 (Europe/Stockholm)** for the corresponding homework.

## Schedule

All times are **Europe/Stockholm**. Assignments are due **Monday 23:59**; peer reviews are due **Thursdays 23:59**.

<AssignmentSchedule />

---

## Notes & Reminders

* **Format:** A short, readable report (notebook or markdown) with clear explanations and a few well-chosen figures.
* **Reproducibility:** Your repo should run from a fresh clone (data access notes, environment instructions if needed).
* **Peer-review tone:** Be kind, specific, and actionable—aim to help your classmate improve.
* **Late work:** A late assignment loses 15 points. Nothing is accepted after **{{ $course.finalDeadline }}**.

## Academic Integrity & Tools

* You may use standard libraries and course-approved tools. If you consult external sources or AI assistants, **cite what you used and how**.
* All code and writing you submit must be **your own** and reflect your understanding.
