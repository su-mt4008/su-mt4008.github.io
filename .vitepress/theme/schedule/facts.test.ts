import { describe, expect, it } from 'vitest'
import { course } from './facts'

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
    expect(course.presentation).toBe('Mon 11 Jan, 13:00–16:00')
    expect(course.presentationRoom).toBe('Lecture room 13, Albano Hus 2, 2nd floor')
  })
  it('exposes the links', () => {
    expect(course.links.moodle).toBe('https://kurser.math.su.se/course/view.php?id=1951')
    expect(Object.keys(course.links)).toEqual(['moodle', 'timeedit', 'github'])
  })
})
