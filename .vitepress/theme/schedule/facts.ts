import config from '../../../course.config'
import { hours, people, schedule } from './data'
import { formatEventWhen, formatWhen, type CourseEvent } from './logic'

// Course details as display strings, for pages to read as `$course.<name>`.
// The values themselves live in data.ts.

const event = (kind: CourseEvent['kind']) => {
  const e = schedule.events.find((e) => e.kind === kind)
  return e ? formatEventWhen(e) : 'TBA'
}
const sessionDay = (i: number) => formatWhen(new Date(schedule.sessions.at(i)!.at))

export const course = {
  ...people,
  hours: `${hours.start}–${hours.end}`,
  firstSession: sessionDay(0),
  lastSession: sessionDay(-1),
  exam: event('exam'),
  proposal: event('proposal'),
  project: event('project'),
  presentation: event('presentation'),
  presentationRoom: config.presentations.room,
  finalDeadline: formatWhen(new Date(`${config.finalDeadline.date}T${config.finalDeadline.time}:00+01:00`), true),
  links: schedule.links,
}

// What the slides show, as plain strings. The site serves it as /course.json (see config.mts),
// and the deck fills it in when it opens, so the slides always match course.config.ts.
export const slideFacts = () => ({
  ...course,
  assignments: schedule.assignments.map((a) => ({
    id: a.id,
    name: a.name,
    due: formatWhen(new Date(a.due), true),
    peerReview: formatWhen(new Date(a.peerDue), true),
    final: formatWhen(new Date(a.finalDue), true),
  })),
})
