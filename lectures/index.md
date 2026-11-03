# Lectures

There are no lectures: the material is designed for self-study, one week at a time. Instead, we meet twice a week for **work sessions**, from {{ $course.firstSession }} to {{ $course.lastSession }}:

* **Mondays, {{ $course.hours }}:** a **15–30 minute walkthrough** of this week’s material, then work time.
* **Thursdays, {{ $course.hours }}:** work time.

The first session, on {{ $course.firstSession }}, is an **introduction to the course**.

All sessions are in **{{ $course.room }}**, with {{ $course.teachers }}.

**Bring your laptop and come to work.** Work on the material and the assignments in the room, and ask us whenever you get stuck or something is unclear. The sessions are optional, but they are the best way through the course: it is much faster to sort out a problem together than alone.

Any changes to times or rooms show up first in TimeEdit:
<a :href="$course.links.timeedit">View the schedule</a>

Example code from the material is here:
[GitHub: su-mt4008/lecture-demos](https://github.com/su-mt4008/lecture-demos)

## Schedule

<LectureSchedule />
