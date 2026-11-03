export interface Week { n: number; start: string; title: string; link: string; note?: string; hw?: string }
export interface Assignment { id: string; name: string; link: string; due: string; peerDue: string }
export interface Session { at: string; end: string; label: string; place: string; link?: string }
// An event without `at` has no date yet; it shows `tbd` instead and stays out of Next up.
export interface CourseEvent { kind: 'proposal' | 'project' | 'exam' | 'presentation'; at?: string; end?: string; tbd?: string; title: string; link: string; blurb: string }
export interface Schedule {
  provisional: boolean
  weeks: Week[]
  assignments: Assignment[]
  sessions: Session[]
  events: CourseEvent[]
  links: { moodle: string; timeedit: string; github: string }
}
export type Phase = 'before' | 'teaching' | 'after-teaching' | 'over'
export interface NextItem { at: Date; kind: 'session' | 'handin' | 'peer' | CourseEvent['kind']; label: string; link?: string }

const DAY = 24 * 60 * 60 * 1000
const TZ = 'Europe/Stockholm'

// The course runs entirely in CET (+01:00), so a fixed offset is exact.
const local = (date: string, time = '00:00') => new Date(`${date}T${time}:00+01:00`)
const weekStart = (w: Week) => local(w.start)
const weekEnd = (w: Week) => new Date(weekStart(w).getTime() + 7 * DAY)

function lastEventEnd(s: Schedule): Date {
  const dated = s.events.filter((e) => e.at)
  return new Date(Math.max(...dated.map((e) => new Date(e.end ?? e.at!).getTime())))
}

export function getPhase(now: Date, s: Schedule): Phase {
  if (now < weekStart(s.weeks[0])) return 'before'
  if (now < weekEnd(s.weeks[s.weeks.length - 1])) return 'teaching'
  if (now < lastEventEnd(s)) return 'after-teaching'
  return 'over'
}

export function getCurrentWeek(now: Date, s: Schedule): number | null {
  const week = s.weeks.find((w) => weekStart(w) <= now && now < weekEnd(w))
  return week ? week.n : null
}

export function getNextUp(now: Date, s: Schedule, count = 2): NextItem[] {
  const items: (NextItem & { until: Date })[] = []
  for (const ses of s.sessions) {
    items.push({ at: new Date(ses.at), until: new Date(ses.end), kind: 'session', label: `${ses.label} ${ses.place}`, link: ses.link })
  }
  for (const a of s.assignments) {
    items.push({ at: new Date(a.due), until: new Date(a.due), kind: 'handin', label: `${a.id} hand-in`, link: a.link })
    items.push({ at: new Date(a.peerDue), until: new Date(a.peerDue), kind: 'peer', label: `${a.id} peer review`, link: a.link })
  }
  for (const e of s.events) {
    if (!e.at) continue
    items.push({ at: new Date(e.at), until: new Date(e.end ?? e.at), kind: e.kind, label: e.title, link: e.link })
  }
  return items
    .filter((i) => now < i.until)
    .sort((a, b) => a.at.getTime() - b.at.getTime())
    .slice(0, count)
    .map(({ until, ...item }) => item)
}

export function formatWhen(d: Date, withTime = false): string {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: TZ,
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    ...(withTime ? { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' } : {}),
  }).formatToParts(d)
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? ''
  const date = `${get('weekday')} ${get('day')} ${get('month')}`
  return withTime ? `${date}, ${get('hour')}:${get('minute')}` : date
}

export function formatEventWhen(e: CourseEvent): string {
  if (!e.at) return e.tbd ?? 'TBA'
  const start = formatWhen(new Date(e.at), true)
  return e.end ? `${start}–${formatWhen(new Date(e.end), true).slice(-5)}` : `Due ${start}`
}
