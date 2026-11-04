import course from '../course.config'
import { defineConfig, type Plugin } from 'vitepress'
import { slideFacts } from './theme/schedule/facts'

// https://vitepress.dev/reference/site-config
// Assignments marked `ready: false` in course.config.ts are listed without a link, and their
// pages are left out of the published site (they still show when previewing locally).
const building = process.argv.includes('build')
const homeworkItems = course.assignments.map((a, i) =>
  a.ready ? { text: `HW${i + 1}`, link: `/homework/${i + 1}` } : { text: `HW${i + 1} (coming soon)` },
)
const unpublished = building
  ? course.assignments.flatMap((a, i) => (a.ready ? [] : [`homework/${i + 1}.md`]))
  : []

// The slides (public/slides/) read dates and rules from /course.json, so they never drift
// from course.config.ts. Served by the dev server and written into the built site.
const courseJson = (): Plugin => ({
  name: 'mt4008-course-json',
  configureServer(server) {
    server.middlewares.use('/course.json', (_req, res) => {
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify(slideFacts()))
    })
  },
  generateBundle() {
    this.emitFile({ type: 'asset', fileName: 'course.json', source: JSON.stringify(slideFacts()) })
  },
})

const lecturesSidebar = [
  {
    text: 'Lectures',
    items: [
      { text: 'Introduction', link: '/lectures/introduction' },
      { text: 'Week 1', link: '/lectures/week-1' },
      { text: 'Week 2', link: '/lectures/week-2' },
      { text: 'Week 3', link: '/lectures/week-3' },
      { text: 'Week 4', link: '/lectures/week-4' },
      { text: 'Week 5', link: '/lectures/week-5' },
      { text: 'Week 6', link: '/lectures/week-6' },
    ]
  },
  {
    text: 'Reference',
    items: [{ text: 'Statistics: the basics', link: '/statistics' }]
  }
]

const courseInfoSidebar = [
  {
    text: 'Course info',
    items: [
      { text: 'About the course', link: '/about' },
      { text: 'How a week works', link: '/about#how-a-week-works' },
      { text: 'Get started', link: '/guide#get-started' },
      { text: 'How we work', link: '/guide' },
    ]
  }
]

export default defineConfig({
  title: "MT4008",
  description: "Course page for MT4008 Statistical Data Processing at Stockholm University",
  srcExclude: ['docs/**', 'mt4008/**', 'templates/**', ...unpublished],
  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@400;500;600&display=swap' }],
  ],
  markdown: {
    math: true,
  },
  vite: {
    // Same value in the server and client bundles, so hydration matches.
    define: { __BUILD_TIME__: JSON.stringify(Date.now()) },
    plugins: [courseJson()],
  },
  themeConfig: {
    editLink: {
      pattern: "https://github.com/su-mt4008/su-mt4008.github.io/issues/new?title=:path",
      text: "Spotted a mistake? Suggest a change"
    },
    search: {
      provider: 'local'
    },
    nav: [
      { text: 'Course info', link: '/about', activeMatch: '^/(about|guide)' },
      { text: 'Lectures', link: '/lectures/', activeMatch: '^/(lectures|statistics)' },
      { text: 'Assignments', link: '/homework/', activeMatch: '^/homework/' },
      { text: 'Project', link: '/project' },
      { text: 'Exam', link: '/exam/' },
    ],
    sidebar: {
      '/lectures/': lecturesSidebar,
      '/statistics': lecturesSidebar,
      '/homework/': [
        {
          text: "Assignments",
          items: [
            { text: 'Overview', link: '/homework/' },
            { text: 'Get started', link: '/guide#get-started' },
            { text: 'How to hand in', link: '/guide#hand-in-an-assignment' },
            ...homeworkItems,
          ]
        }
      ],
      '/about': courseInfoSidebar,
      '/guide': courseInfoSidebar,
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/su-mt4008' }
    ]
  }
})
