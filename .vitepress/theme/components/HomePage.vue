<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { schedule } from '../schedule/data'
import { getCurrentWeek, getNextUp, getPhase } from '../schedule/logic'
import NextUp from './NextUp.vue'
import WeekList from './WeekList.vue'

declare const __BUILD_TIME__: number

// Server render and hydration use the build time; the real date takes over on mount,
// so the deployed static page never goes stale.
const now = ref(new Date(__BUILD_TIME__))

function readNow(): Date {
  if (import.meta.env.DEV) {
    // Dev only: preview another moment with ?now=2026-11-18T10:00
    const q = new URLSearchParams(location.search).get('now')
    if (q) return new Date(`${q}:00+01:00`)
  }
  return new Date()
}

let timer: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  now.value = readNow()
  timer = setInterval(() => (now.value = readNow()), 60_000)
})
onUnmounted(() => clearInterval(timer))

const phase = computed(() => getPhase(now.value, schedule))
const currentWeek = computed(() => getCurrentWeek(now.value, schedule))
const nextUp = computed(() => getNextUp(now.value, schedule))
const links = [
  { text: 'Moodle', href: schedule.links.moodle },
  { text: 'TimeEdit', href: schedule.links.timeedit },
  { text: 'GitHub', href: schedule.links.github },
]
</script>

<template>
  <div class="mt-home">
    <div class="wrap">
      <div class="lead">
        <h1>Statistical Data Processing</h1>
        <p class="intro">
          Getting, cleaning, exploring and explaining data, in a way someone else can rerun. Python or R, your choice.
        </p>
        <NextUp :items="nextUp" :phase="phase" />
        <p class="quick">
          <a v-for="l in links" :key="l.text" :href="l.href">{{ l.text }}</a>
        </p>
        <p v-if="schedule.provisional" class="provisional">Dates are provisional.</p>
      </div>
      <WeekList :schedule="schedule" :phase="phase" :current-week="currentWeek" />
    </div>
    <footer>
      Spotted a mistake?
      <a href="https://github.com/su-mt4008/su-mt4008.github.io/issues/new?title=index">Suggest a change on GitHub</a>.
    </footer>
  </div>
</template>

<style scoped>
.mt-home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 48px 0;
  font-size: 16px;
  line-height: 1.6;
  color: var(--c-text);
}
.wrap {
  display: grid;
  grid-template-columns: 330px minmax(0, 1fr);
  gap: 72px;
  padding-bottom: 64px;
}
.lead {
  position: sticky;
  top: calc(var(--vp-nav-height) + 24px);
  align-self: start;
}
h1 {
  font-family: var(--font-serif);
  font-weight: 500;
  font-size: 44px;
  line-height: 1.08;
  letter-spacing: -0.015em;
  margin: 0 0 18px;
}
.intro {
  margin: 0 0 26px;
  color: var(--c-muted);
}
.quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
  font-size: 14.5px;
  margin: 0;
  border-top: 1px solid var(--c-line);
  padding-top: 14px;
}
.provisional {
  margin: 14px 0 0;
  font-size: 13.5px;
  color: var(--c-muted);
}
footer {
  padding: 18px 0 32px;
  border-top: 1px solid var(--c-line);
  font-size: 14px;
  color: var(--c-muted);
}

@media (max-width: 960px) {
  .mt-home {
    padding: 32px 24px 0;
  }
  .wrap {
    grid-template-columns: minmax(0, 1fr);
    gap: 40px;
  }
  .lead {
    position: static;
  }
  h1 {
    font-size: 36px;
  }
}
@media (max-width: 640px) {
  .mt-home {
    padding: 24px 16px 0;
  }
  h1 {
    font-size: 32px;
  }
}
</style>
