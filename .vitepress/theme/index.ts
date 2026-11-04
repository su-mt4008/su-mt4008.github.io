import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import AssignmentSchedule from './components/AssignmentSchedule.vue'
import HomePage from './components/HomePage.vue'
import LectureSchedule from './components/LectureSchedule.vue'
import LifeCycle from './components/LifeCycle.vue'
import { course } from './schedule/facts'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('HomePage', HomePage)
    app.component('LectureSchedule', LectureSchedule)
    app.component('AssignmentSchedule', AssignmentSchedule)
    app.component('LifeCycle', LifeCycle)
    // Markdown pages read course details as {{ $course.exam }}, :href="$course.links.moodle", etc.
    app.config.globalProperties.$course = course
  },
} satisfies Theme
