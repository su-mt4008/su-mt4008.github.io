import config from '../../../course.config'
import type { Schedule } from './logic'

// Builds the schedule from course.config.ts, the one file to edit each term.
// This file holds what stays the same between terms: week topics and assignment names.
// All times are Europe/Stockholm (CET, +01:00 for the whole course period).

const at = (date: string, time: string) => `${date}T${time}:00+01:00`

export const people = { teachers: config.teachers, room: config.room }
export const hours = { start: config.sessionStart, end: config.sessionEnd }

const topics = [
  { title: 'Reproducible Analysis: Questions, Git and Quarto', hw: 'HW1' },
  { title: 'DataFrames & Visualising Data with Plots', hw: 'HW2' },
  { title: 'Exploratory Data Analysis (EDA) & Processing Data', hw: 'HW3' },
  { title: 'Joining Data, SQL, and an Introduction to RegEx', hw: 'HW4' },
  // TODO(owner): guest lecture in HT26? Add it as `note`.
  { title: 'Retrieving Data from the Web (REST APIs & Web Scraping)', hw: 'HW5' },
  { title: 'Extracting unstructured data with LLMs' },
]

const assignmentNames = ['GitHub test-run', 'Tables and plots', 'Exploring and visualising data', 'SQL and regex', 'Data from the web']

// The first session introduces the course. After that every session is work time, and Mondays start with a walkthrough.
const sessionLabel = (date: string, i: number) => {
  if (i === 0) return 'Course introduction'
  return new Date(`${date}T12:00:00Z`).getUTCDay() === 1 ? 'Walkthrough and work session' : 'Work session'
}
const session = (date: string, i: number) => ({
  at: at(date, config.sessionStart),
  end: at(date, config.sessionEnd),
  label: sessionLabel(date, i),
  place: `in ${config.roomShort}`,
})

const presentationsWhen = () => {
  const p = config.presentations
  return p.date ? { at: at(p.date, p.start), end: at(p.date, p.end) } : { tbd: p.note }
}

export const schedule: Schedule = {
  provisional: config.provisional,
  weeks: topics.map((t, i) => ({ n: i + 1, start: config.weekStarts[i], link: `/lectures/week-${i + 1}`, ...t })),
  assignments: config.assignments.map((a, i) => ({
    id: `HW${i + 1}`,
    name: assignmentNames[i],
    link: `/homework/${i + 1}`,
    due: at(a.due, '23:59'),
    peerDue: at(a.peerReview, '23:59'),
    finalDue: at(a.final, '23:59'),
  })),
  sessions: config.sessionDates.map(session),
  events: [
    { kind: 'proposal', at: at(config.proposal.due, config.proposal.time), title: 'Project proposal', link: '/project#proposal', blurb: 'Your group, scope and target grade, handed in on Moodle.' },
    { kind: 'project', at: at(config.project.due, config.project.time), title: 'Project', link: '/project', blurb: 'A group data science project, reproducible from start to finish.' },
    { kind: 'exam', at: at(config.exam.date, config.exam.start), end: at(config.exam.date, config.exam.end), title: 'Exam', link: '/exam/', blurb: 'Written, on campus. Register in Ladok first.' },
    { kind: 'presentation', ...presentationsWhen(), title: 'Presentations', link: '/project', blurb: 'A 15–20 minute talk per group. Attendance is compulsory.' },
  ],
  links: config.links,
}
