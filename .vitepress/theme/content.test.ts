import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
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

describe('week 1', () => {
  const week1 = page('lectures/week-1.md')

  it('teaches the workflow: questions, reproducibility, project layout, environments, Quarto, Git, pull requests', () => {
    for (const heading of [/^## .*question/im, /^## .*reproducib/im, /^## .*project/im, /^## .*environment/im, /^## .*Quarto/m, /^## .*Git/m, /^##+ .*pull request/im]) {
      expect(week1).toMatch(heading)
    }
    for (const text of ['uv add', 'renv::snapshot()', '/guide', '/homework/1']) {
      expect(week1).toContain(text)
    }
  })

  it('drops the old tools', () => {
    for (const old of ['GitHub Desktop', 'Miniconda', 'conda create', 'Functional programming', 'Jupyter Lab']) {
      expect(week1).not.toContain(old)
    }
  })
})

describe('the whole site', () => {
  const skip = new Set(['node_modules', 'docs', 'mt4008', 'templates', '.vitepress', '.git', '.superpowers', 'public'])
  const pages = (dir: string): string[] =>
    readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
      e.isDirectory() ? (skip.has(e.name) ? [] : pages(join(dir, e.name))) : e.name.endsWith('.md') ? [join(dir, e.name)] : [],
    )

  it('has no instructions from the old issue-based hand-in', () => {
    const old = [/ready-for-grading/, /– Submission/, /open an issue/i, /GitHub Desktop/, /username-hw-/]
    const found = pages('.').flatMap((p) => old.filter((re) => re.test(page(p))).map((re) => `${p}: ${re}`))
    expect(found).toEqual([])
  })
})

describe('review fixes', () => {
  it('locks R packages to a dated Posit Package Manager snapshot, so Windows/Mac get binaries all term', () => {
    const lock = JSON.parse(page('templates/r/renv.lock'))
    expect(lock.R.Repositories[0].URL).toMatch(/^https:\/\/packagemanager\.posit\.co\/cran\/\d{4}-\d{2}-\d{2}$/)
  })

  it('tells students what to do after committing on main by mistake', () => {
    expect(page('guide.md')).toMatch(/^##+ .*on `main` by mistake/m)
    expect(page('homework/1.md')).toMatch(/push(ing)? (straight |directly )?to `main`[^.]*not a hand-in/i)
  })

  it('says exactly how to start R in the repository folder', () => {
    expect(page('guide.md')).toContain('R: Create R Terminal')
  })
})

describe('weekly rhythm', () => {
  it('explains that the version on Friday evening is the one graded', () => {
    for (const p of ['homework/index.md', 'guide.md', 'about.md']) {
      expect(page(p)).toMatch(/Friday/)
    }
    expect(page('homework/index.md')).toMatch(/graded/)
  })
})
