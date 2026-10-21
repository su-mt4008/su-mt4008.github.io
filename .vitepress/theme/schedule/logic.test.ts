import { describe, expect, it } from 'vitest'
import { schedule } from './data'
import { formatEventWhen, formatWhen, getCurrentWeek, getNextUp, getPhase } from './logic'

// Run in UTC so a formatter that falls back to the runtime zone fails.
process.env.TZ = 'UTC'

const at = (s: string) => new Date(`${s}:00+01:00`)

describe('getPhase', () => {
  it('is before ahead of the first session', () => {
    expect(getPhase(at('2026-10-21T12:00'), schedule)).toBe('before')
  })
  it('is teaching during the weeks', () => {
    expect(getPhase(at('2026-11-18T10:00'), schedule)).toBe('teaching')
  })
  it('is teaching from Monday midnight of week 1, agreeing with getCurrentWeek', () => {
    expect(getPhase(at('2026-11-02T09:00'), schedule)).toBe('teaching')
    expect(getCurrentWeek(at('2026-11-02T09:00'), schedule)).toBe(1)
  })
  it('is after-teaching over Christmas', () => {
    expect(getPhase(at('2026-12-24T12:00'), schedule)).toBe('after-teaching')
  })
  it('is over after the exam ends', () => {
    expect(getPhase(at('2027-01-12T09:00'), schedule)).toBe('over')
  })
})

describe('getCurrentWeek', () => {
  it('starts week 1 at Monday midnight', () => {
    expect(getCurrentWeek(at('2026-11-02T00:00'), schedule)).toBe(1)
  })
  it('keeps week 3 until Sunday 23:59', () => {
    expect(getCurrentWeek(at('2026-11-22T23:59'), schedule)).toBe(3)
  })
  it('moves to week 4 at Monday midnight', () => {
    expect(getCurrentWeek(at('2026-11-23T00:00'), schedule)).toBe(4)
  })
  it('is null over Christmas', () => {
    expect(getCurrentWeek(at('2026-12-24T12:00'), schedule)).toBeNull()
  })
  it('is null before the course', () => {
    expect(getCurrentWeek(at('2026-10-21T12:00'), schedule)).toBeNull()
  })
})

describe('getNextUp', () => {
  it('lists the next two items in date order during teaching', () => {
    const items = getNextUp(at('2026-11-18T10:00'), schedule)
    expect(items.map((i) => i.label)).toEqual(['Q&A in Albano, lecture room 19', 'HW2 peer review'])
    expect(items.map((i) => i.at.getTime())).toEqual([
      at('2026-11-19T13:00').getTime(),
      at('2026-11-19T23:59').getTime(),
    ])
  })
  it('keeps a hand-in until 23:59 and drops it at midnight', () => {
    const labels = (s: string) => getNextUp(at(s), schedule, 10).map((i) => i.label)
    expect(labels('2026-11-09T23:58')).toContain('HW1 hand-in')
    expect(labels('2026-11-10T00:00')).not.toContain('HW1 hand-in')
  })
  it('shows project then exam over Christmas', () => {
    expect(getNextUp(at('2026-12-24T12:00'), schedule).map((i) => i.kind)).toEqual(['project', 'exam'])
  })
  it('is empty after the exam', () => {
    expect(getNextUp(at('2027-01-12T09:00'), schedule)).toEqual([])
  })
  it('starts with the first session before the course', () => {
    const [first] = getNextUp(at('2026-10-21T12:00'), schedule)
    expect(first.kind).toBe('session')
    expect(first.at.getTime()).toBe(at('2026-11-05T13:00').getTime())
  })
  it('has no session on Monday of week 1, matching TimeEdit', () => {
    const [first] = getNextUp(at('2026-11-02T09:00'), schedule)
    expect(first.at.getTime()).toBe(at('2026-11-05T13:00').getTime())
  })
  it('keeps the sessions booked after the last lecture week', () => {
    const [first] = getNextUp(at('2026-12-15T10:00'), schedule)
    expect(first.kind).toBe('session')
    expect(first.at.getTime()).toBe(at('2026-12-17T13:00').getTime())
  })
  it('ends a session at 17:00', () => {
    const labels = (s: string) => getNextUp(at(s), schedule).map((i) => i.at.getTime())
    expect(labels('2026-11-19T16:59')).toContain(at('2026-11-19T13:00').getTime())
    expect(labels('2026-11-19T17:00')).not.toContain(at('2026-11-19T13:00').getTime())
  })
})

describe('formatEventWhen', () => {
  it('shows a deadline as due date and time', () => {
    const project = schedule.events.find((e) => e.kind === 'project')!
    expect(formatEventWhen(project)).toBe('Due Fri 8 Jan, 23:59')
  })
  it('shows an event with an end as a time range', () => {
    const exam = schedule.events.find((e) => e.kind === 'exam')!
    expect(formatEventWhen(exam)).toBe('Sat 9 Jan, 09:00–11:00')
  })
})

describe('formatWhen', () => {
  it('formats date and time in Stockholm time', () => {
    expect(formatWhen(new Date('2026-11-19T23:59:00+01:00'), true)).toBe('Thu 19 Nov, 23:59')
  })
  it('uses the Stockholm date, not the runtime zone', () => {
    expect(formatWhen(new Date('2026-11-02T00:30:00+01:00'))).toBe('Mon 2 Nov')
  })
})
