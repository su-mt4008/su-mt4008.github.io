import type { Schedule } from './logic'

// The single source of truth for course dates and links.
// All times are Europe/Stockholm (CET, +01:00 for the whole course period).
//
// TODO(owner): HT26 dates are provisional. Confirm weeks, deadlines, project
// deadline, exam time and any project presentations, then set provisional: false.

const hw = (n: number, name: string, due: string, peerDue: string) => ({
  id: `HW${n}`,
  name,
  link: `/homework/${n}`,
  due: `${due}T23:59:00+01:00`,
  peerDue: `${peerDue}T23:59:00+01:00`,
})

export const schedule: Schedule = {
  provisional: true,
  firstSession: '2026-11-02T13:00:00+01:00',
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
  sessions: [
    { weekday: 1, start: '13:00', end: '16:00', label: 'Live demo and help', place: 'on campus' },
    // TODO(owner): HT26 Zoom link.
    { weekday: 4, start: '13:00', end: '16:00', label: 'Q&A', place: 'on Zoom', link: 'https://stockholmuniversity.zoom.us/j/6254185246' },
  ],
  events: [
    { kind: 'project', at: '2027-01-08T23:59:00+01:00', title: 'Project', link: '/project', blurb: 'An individual, reproducible analysis of a dataset you choose.' },
    { kind: 'exam', at: '2027-01-11T08:00:00+01:00', end: '2027-01-11T11:00:00+01:00', title: 'Exam', link: '/exam/', blurb: 'Written, on campus. What it covers and how to prepare.' },
    // TODO(owner): project presentations in HT26? Add as kind: 'presentation'.
  ],
  links: {
    // TODO(owner): confirm Moodle course id (1631 vs 1333).
    moodle: 'https://kurser.math.su.se/course/view.php?id=1631',
    zoom: 'https://stockholmuniversity.zoom.us/j/6254185246',
    // TODO(owner): HT26 TimeEdit link (this one is HT25).
    timeedit: 'https://cloud.timeedit.net/su/web/stud1/s.html?tab=3&object=cevt_48076_HT2025&startDate=20251004&endDate=20260418&type=courseevent&h=t',
    github: 'https://github.com/su-mt4008',
  },
}
