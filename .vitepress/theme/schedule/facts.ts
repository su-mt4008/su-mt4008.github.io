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
  links: schedule.links,
}
