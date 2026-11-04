import { describe, expect, it } from 'vitest'
import { course, slideFacts } from './facts'

// Run in UTC so a formatter that falls back to the runtime zone fails.
process.env.TZ = 'UTC'

describe('course facts', () => {
  it('derives the session span from the TimeEdit sessions', () => {
    expect(course.firstSession).toBe('Thu 5 Nov')
    expect(course.lastSession).toBe('Mon 21 Dec')
  })
  it('gives session hours, room and teachers', () => {
    expect(course.hours).toBe('13:00–17:00')
    expect(course.room).toBe('Lecture room 19, Albano Hus 2, 2nd floor')
    expect(course.teachers).toBe('Per Alexandersson and Taariq Nazar')
  })
  it('formats the exam, project deadline and presentations', () => {
    expect(course.exam).toBe('Sat 9 Jan, 09:00–11:00')
    expect(course.project).toBe('Due Fri 8 Jan, 23:59')
    expect(course.proposal).toBe('Due Thu 19 Nov, 23:59')
    expect(course.presentation).toBe('Mon 11 Jan, 13:00–16:00')
    expect(course.presentationRoom).toBe('Lecture room 13, Albano Hus 2, 2nd floor')
  })
  it('gives the final deadline for all assignments', () => {
    expect(course.finalDeadline).toBe('Fri 15 Jan, 23:59')
  })
  it('exposes the links', () => {
    expect(course.links.moodle).toBe('https://kurser.math.su.se/course/view.php?id=1951')
    expect(Object.keys(course.links)).toEqual(['moodle', 'timeedit', 'github'])
  })
})

describe('slide facts (served as /course.json for the slides)', () => {
  const f = slideFacts()
  it('lists every assignment with its three deadlines', () => {
    expect(f.assignments).toHaveLength(5)
    expect(f.assignments[0]).toEqual({
      id: 'HW1', name: 'Your first reproducible report',
      due: 'Mon 9 Nov, 23:59', peerReview: 'Thu 12 Nov, 23:59', final: 'Fri 13 Nov, 23:59',
    })
  })
  it('carries the course facts as plain strings', () => {
    expect(f.exam).toBe('Sat 9 Jan, 09:00–11:00')
    expect(f.proposal).toBe('Due Thu 19 Nov, 23:59')
    expect(f.finalDeadline).toBe('Fri 15 Jan, 23:59')
    expect(f.room).toBe('Lecture room 19, Albano Hus 2, 2nd floor')
  })
  it('is plain JSON', () => {
    expect(JSON.parse(JSON.stringify(f))).toEqual(f)
  })
})

describe('lecture decks', () => {
  it('finds every deck in slides/ and links it from its week', async () => {
    const { decks, deckFor } = await import('./decks')
    const { schedule } = await import('./data')
    expect(decks).toEqual(expect.arrayContaining(['introduction', 'week-1']))
    expect(deckFor(schedule.weeks[0].link)).toBe('/slides/week-1/index.html')
    expect(deckFor(schedule.weeks[1].link)).toBeUndefined()
  })
  it('gives the deck for a lecture page, and none for other pages', async () => {
    const { deckFor } = await import('./decks')
    expect(deckFor('/lectures/introduction')).toBe('/slides/introduction/index.html')
    expect(deckFor('/lectures/week-1.html')).toBe('/slides/week-1/index.html')
    expect(deckFor('/lectures/week-2')).toBeUndefined()
    expect(deckFor('/homework/1')).toBeUndefined()
  })
})
