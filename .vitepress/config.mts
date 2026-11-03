import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "MT4008",
  description: "Course page for MT4008 Statistical Data Processing at Stockholm University",
  srcExclude: ['docs/**', 'mt4008/**'],
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
      { text: 'Course info', link: '/about', activeMatch: '^/about' },
      { text: 'Lectures', link: '/lectures/' },
      { text: 'Assignments', link: '/homework/', activeMatch: '^/homework/' },
      { text: 'Project', link: '/project' },
      { text: 'Exam', link: '/exam/' },
    ],
    sidebar: {
      '/lectures/': [
        {
          text: "Lectures",
          items: [
            { text: 'Week 1', link: '/lectures/week-1' },
            { text: 'Week 2', link: '/lectures/week-2' },
            { text: 'Week 3', link: '/lectures/week-3' },
            { text: 'Week 4', link: '/lectures/week-4' },
            { text: 'Week 5', link: '/lectures/week-5' },
            { text: 'Week 6', link: '/lectures/week-6' },
          ]
        }
      ],
      '/homework/': [
        {
          text: "Assignments",
          items: [
            { text: 'Overview', link: '/homework/' },
            { text: 'HW1', link: '/homework/1' },
            { text: 'HW2', link: '/homework/2' },
            { text: 'HW3', link: '/homework/3' },
            { text: 'HW4', link: '/homework/4' },
            { text: 'HW5', link: '/homework/5' },
          ]
        }
      ],
      '/about': [
        {
          text: "Course info",
          items: [
            { text: 'About the course', link: '/about' },
            { text: 'How a week works', link: '/about#how-a-week-works' },
          ]
        }
      ],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/su-mt4008' }
    ]
  }
})
