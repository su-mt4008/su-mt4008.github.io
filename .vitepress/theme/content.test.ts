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
