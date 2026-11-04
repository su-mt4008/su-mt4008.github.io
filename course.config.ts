// MT4008 course settings: everything that changes from term to term.
// Edit the values here; every page reads them from this file.
// Dates are 'YYYY-MM-DD' and times 'HH:MM', all in Stockholm time.

export default {
  // Shows "Dates are provisional." on the home page. Set to false once the dates below are final.
  provisional: false,

  links: {
    moodle: 'https://kurser.math.su.se/course/view.php?id=1951',
    timeedit: 'https://cloud.timeedit.net/su/web/stud1/s.html?sid=3&object=cevt_48074_HT2026&startDate=20261003&endDate=20270417&type=courseevent&h=t&l=en',
    github: 'https://github.com/su-mt4008',
  },

  teachers: 'Per Alexandersson and Taariq Nazar',
  room: 'Lecture room 19, Albano Hus 2, 2nd floor',
  roomShort: 'Albano, lecture room 19', // used in "Next up" on the home page

  // Sessions, copied from TimeEdit. The first is the course introduction; Mondays open with a walkthrough.
  sessionStart: '13:00',
  sessionEnd: '17:00',
  sessionDates: [
    '2026-11-05',
    '2026-11-09', '2026-11-12',
    '2026-11-16', '2026-11-19',
    '2026-11-23', '2026-11-26',
    '2026-11-30', '2026-12-03',
    '2026-12-07', '2026-12-10',
    '2026-12-14', '2026-12-17',
    '2026-12-21',
  ],

  // The Monday each lecture week starts, week 1 first.
  weekStarts: ['2026-11-02', '2026-11-09', '2026-11-16', '2026-11-23', '2026-11-30', '2026-12-07'],

  // Last chance for any assignment, late or not. Missing it means redoing all assignments next year.
  finalDeadline: { date: '2027-01-15', time: '23:59' },

  // HW1 first. `ready: false` shows the assignment (name and dates) without a link, and leaves
  // its page out of the published site; set it to true when the assignment text is final.
  // All three deadlines are at 23:59: hand in (Monday), peer review (Thursday),
  // and the final version after the review (Friday), which is the version graded.
  assignments: [
    { ready: true, due: '2026-11-09', peerReview: '2026-11-12', final: '2026-11-13' },
    { ready: false, due: '2026-11-16', peerReview: '2026-11-19', final: '2026-11-20' },
    { ready: false, due: '2026-11-23', peerReview: '2026-11-26', final: '2026-11-27' },
    { ready: false, due: '2026-11-30', peerReview: '2026-12-03', final: '2026-12-04' },
    { ready: false, due: '2026-12-07', peerReview: '2026-12-10', final: '2026-12-11' },
  ],

  // Groups hand in their project proposal on Moodle.
  proposal: { due: '2026-11-19', time: '23:59' },
  project: { due: '2027-01-08', time: '23:59' },
  exam: { date: '2027-01-09', start: '09:00', end: '11:00' }, // from TimeEdit
  // From TimeEdit. Leave date empty if unknown; the pages then show the note.
  presentations: { date: '2027-01-11', start: '13:00', end: '16:00', room: 'Lecture room 13, Albano Hus 2, 2nd floor', note: 'TBD' },
}
