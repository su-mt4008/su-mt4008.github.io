import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

// Content checks: the pages students rely on must teach the pull-request workflow.
const page = (path: string) => readFileSync(path, 'utf8')

describe('guide', () => {
  const guide = page('guide.md')

  it('has the sections other pages and the check link to', () => {
    for (const anchor of [
      'set-up-your-computer',
      'hand-in-an-assignment',
      'when-the-check-is-red',
      'review-a-pull-request',
      'if-your-install-fails',
    ]) {
      expect(guide).toMatch(new RegExp(`^##+ .*\\{#${anchor}\\}`, 'm'))
    }
  })

  it('gives the commands for both languages and for Windows', () => {
    for (const text of ['uv sync', 'renv::restore()', 'quarto render', 'Windows']) {
      expect(guide).toContain(text)
    }
  })

  it('says that pushing to main is not a hand-in', () => {
    expect(guide).toMatch(/push(ing)? (straight |directly )?to `main`[^.]*not a hand-in/i)
  })
})

describe('HW1', () => {
  const hw1 = page('homework/1.md')

  it('uses the pull-request flow from the guide', () => {
    for (const text of ['/guide#hand-in-an-assignment', '`hw1`', '`HW1`', '<username>-hw1']) {
      expect(hw1).toContain(text)
    }
  })

  it('walks through the seven report sections', () => {
    for (const section of ['Question', 'Data', 'Cleaning', 'Exploration', 'Analysis', 'Conclusions & limitations', 'How to reproduce']) {
      expect(hw1).toContain(`**${section}**`)
    }
  })
})
