import type { Schedule } from './logic'

// The single source of truth for course dates and links.
// All times are Europe/Stockholm (CET, +01:00 for the whole course period).
//
// Sessions and the exam are from the HT26 TimeEdit schedule (links.timeedit).
// TODO(owner): hand-in and peer-review deadlines, the project deadline and any
// project presentations are still provisional. Confirm them, then set provisional: false.

const hw = (n: number, name: string, due: string, peerDue: string) => ({
  id: `HW${n}`,
  name,
  link: `/homework/${n}`,
  due: `${due}T23:59:00+01:00`,
  peerDue: `${peerDue}T23:59:00+01:00`,
})

// All sessions are 13:00–17:00 in the same room. Mondays are the live demo, Thursdays Q&A.
const place = 'in Albano, lecture room 19'
const session = (date: string) => {
  const monday = new Date(`${date}T12:00:00Z`).getUTCDay() === 1
  return {
    at: `${date}T13:00:00+01:00`,
    end: `${date}T17:00:00+01:00`,
    label: monday ? 'Live demo and help' : 'Q&A',
    place,
  }
}

export const schedule: Schedule = {
  provisional: true,
  firstSession: '2026-11-05T13:00:00+01:00',
  weeks: [
    { n: 1, start: '2026-11-02', title: 'Reproducible Analysis with GitHub, Jupyter, and Functional Programming', link: '/lectures/week-1', hw: 'HW1' },
    { n: 2, start: '2026-11-09', title: 'DataFrames & Visualising Data with Plots', link: '/lectures/week-2', hw: 'HW2' },
    { n: 3, start: '2026-11-16', title: 'Exploratory Data Analysis (EDA) & Processing Data', link: '/lectures/week-3', hw: 'HW3' },
    { n: 4, start: '2026-11-23', title: 'Joining Data, SQL, and an Introduction to RegEx', link: '/lectures/week-4', hw: 'HW4' },
    // TODO(owner): guest lecture in HT26? Add it as `note`.
    { n: 5, start: '2026-11-30', title: 'Retrieving Data from the Web (REST APIs & Web Scraping)', link: '/lectures/week-5', hw: 'HW5' },
    { n: 6, start: '2026-12-07', title: 'Extracting unstructured data with LLMs', link: '/lectures/week-6' },
  ],
  assignments: [
    hw(1, 'GitHub test-run', '2026-11-09', '2026-11-12'),
    hw(2, 'Tables and plots', '2026-11-16', '2026-11-19'),
    hw(3, 'Exploring and visualising data', '2026-11-23', '2026-11-26'),
    hw(4, 'SQL and regex', '2026-11-30', '2026-12-03'),
    hw(5, 'Data from the web', '2026-12-07', '2026-12-10'),
  ],
  // TODO(owner): TimeEdit books a room for Thursdays too, so Q&A is listed on campus, not on Zoom.
  sessions: [
    '2026-11-05',
    '2026-11-09', '2026-11-12',
    '2026-11-16', '2026-11-19',
    '2026-11-23', '2026-11-26',
    '2026-11-30', '2026-12-03',
    '2026-12-07', '2026-12-10',
    '2026-12-14', '2026-12-17',
    '2026-12-21',
  ].map(session),
  events: [
    { kind: 'project', at: '2027-01-08T23:59:00+01:00', title: 'Project', link: '/project', blurb: 'An individual, reproducible analysis of a dataset you choose.' },
    { kind: 'exam', at: '2027-01-09T09:00:00+01:00', end: '2027-01-09T11:00:00+01:00', title: 'Exam', link: '/exam/', blurb: 'Written, on campus. Register in Ladok first.' },
    // TODO(owner): project presentations in HT26? Add as kind: 'presentation'.
  ],
  links: {
    moodle: 'https://kurser.math.su.se/course/view.php?id=1951',
    zoom: 'https://stockholmuniversity.zoom.us/j/6254185246',
    timeedit: 'https://cloud.timeedit.net/su/web/stud1/s.html?sid=3&object=cevt_48074_HT2026&startDate=20261003&endDate=20270417&type=courseevent&h=t&l=en',
    github: 'https://github.com/su-mt4008',
  },
}
