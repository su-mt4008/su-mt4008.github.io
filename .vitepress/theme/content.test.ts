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
    for (const text of ['/guide#hand-in-an-assignment', '`hw1`', '`HW1`', '<username>-assignments', '`hw1/report.qmd`']) {
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
    const old = [/ready-for-grading/, /– Submission/, /open an issue/i, /GitHub Desktop/, /username-hw-/, /<username>-hw/, /hw<n>`\*\*/]
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

describe('one repository per student', () => {
  it('the guide says reviewer access ends Friday morning', () => {
    expect(page('guide.md')).toMatch(/Friday morning/)
  })
})

describe('statistics page', () => {
  it('exists, builds on Probability Theory I, and covers the basics', () => {
    const stats = page('statistics.md')
    for (const text of ['Probability Theory I', 'centrala gränsvärdessatsen', 'standard error', 'confidence interval', 'p-value', 'bootstrap', 'permutation', 'confounder']) {
      expect(stats.toLowerCase()).toContain(text.toLowerCase())
    }
  })
  it('is linked from HW1 and week 1', () => {
    expect(page('homework/1.md')).toContain('/statistics')
    expect(page('lectures/week-1.md')).toContain('/statistics')
  })
})

describe('introduction lecture', () => {
  const post = page('lectures/introduction.md')
  const deck = page('slides/introduction/index.qmd') + page('slides/week-1/index.qmd')
  const exists = (path: string) => { try { readFileSync(path); return true } catch { return false } }

  it('the slides link back to the post (the post gets its Slides link automatically)', () => {
    expect(deck).toContain('/lectures/introduction')
  })
  it('the post shows a diagram for each project, and each diagram exists in both shapes', () => {
    for (const name of ['names', 'electricity', 'ai-bubble']) {
      expect(post).toContain(`<LifeCycle name="${name}" />`)
      expect(exists(`public/img/introduction/lifecycle-${name}.svg`)).toBe(true)
      expect(exists(`public/img/introduction/lifecycle-${name}-tall.svg`)).toBe(true)
    }
  })
  it('every image the post and the slides use exists', () => {
    const images = [...post.matchAll(/\]\((\/img\/[^)]+)\)/g), ...deck.matchAll(/src="\.\.\/\.\.(\/img\/[^"]+)"/g)].map((m) => m[1])
    expect(images.length).toBeGreaterThan(15)
    for (const img of images) expect(exists(`public${img}`), img).toBe(true)
  })
  it('dates on the slides are filled in from /course.json, not typed in', () => {
    for (const key of ['finalDeadline', 'proposal', 'presentation', 'project', 'exam', 'assignments.0.due']) {
      expect(deck).toContain(`data-course="${key}"`)
    }
    expect(deck).toContain('data-course-assignments')
  })
  it('is in the Lectures sidebar and linked from week 1 and the lectures page', () => {
    expect(page('.vitepress/config.mts')).toContain("link: '/lectures/introduction'")
    expect(page('lectures/week-1.md')).toContain('/lectures/introduction')
    expect(page('lectures/index.md')).toContain('/lectures/introduction')
  })
})

describe('lecture decks', () => {
  const config = page('slides/_quarto.yml')
  const decks = [...config.matchAll(/^\s+- (\S+)\/index\.qmd$/gm)].map((m) => m[1])
  it('every deck in slides/_quarto.yml exists, has a lecture page, and links back to it', () => {
    expect(decks).toEqual(expect.arrayContaining(['introduction', 'week-1']))
    for (const name of decks) {
      expect(page(`lectures/${name}.md`).length).toBeGreaterThan(0)
      expect(page(`slides/${name}/index.qmd`)).toContain(`/lectures/${name}`)
    }
  })
  it('every deck folder is listed in slides/_quarto.yml, so `quarto render` builds it', () => {
    const folders = readdirSync('slides', { withFileTypes: true })
      .filter((d) => d.isDirectory() && !d.name.startsWith('_') && !d.name.startsWith('.')).map((d) => d.name)
    expect(folders.sort()).toEqual([...decks].sort())
  })
})

describe('deck links', () => {
  // Quarto rewrites root paths like /img/x.svg relative to slides/, which breaks them, so decks
  // use paths relative to their own folder: ../../img/x.svg, ../../about.
  for (const name of ['introduction', 'week-1']) {
    it(`${name} uses no root-relative links or images`, () => {
      expect(page(`slides/${name}/index.qmd`)).not.toMatch(/(href|src)="\/(?!\/)/)
    })
    it(`${name} rendered: every image and site link points two levels up`, () => {
      const html = page(`public/slides/${name}/index.html`)
      const refs = [...html.matchAll(/(?:href|src)="(\.\.\/[^"#]*)/g)].map((m) => m[1])
        .filter((r) => !r.includes('site_libs'))
      expect(refs.length).toBeGreaterThan(5)
      for (const r of refs) expect(r, r).toMatch(/^\.\.\/\.\.\//)
    })
  }
})
