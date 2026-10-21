import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import AssignmentSchedule from './components/AssignmentSchedule.vue'
import EventDate from './components/EventDate.vue'
import HomePage from './components/HomePage.vue'
import LectureSchedule from './components/LectureSchedule.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('HomePage', HomePage)
    app.component('LectureSchedule', LectureSchedule)
    app.component('AssignmentSchedule', AssignmentSchedule)
    app.component('EventDate', EventDate)
  },
} satisfies Theme
