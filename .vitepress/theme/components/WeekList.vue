<script setup lang="ts">
import { computed } from 'vue'
import { formatEventWhen, formatWhen, type Phase, type Schedule } from '../schedule/logic'

const props = defineProps<{ schedule: Schedule; phase: Phase; currentWeek: number | null }>()

const setupLink = '/lectures/week-1#install-the-essentials'
const firstSession = computed(() => formatWhen(new Date(props.schedule.firstSession)))
const assignment = (id?: string) => props.schedule.assignments.find((a) => a.id === id)
const weekDate = (start: string) => formatWhen(new Date(`${start}T12:00:00+01:00`))
</script>

<template>
  <div class="weeks">
    <div class="wk zero" :class="{ open: phase === 'before', hi: phase === 'before' }">
      <div class="num">0</div>
      <div>
        <div class="date">
          Before {{ firstSession }}
          <b v-if="phase === 'before'">Start here</b>
        </div>
        <h3><a href="/about">Get set up</a></h3>
        <template v-if="phase === 'before'">
          <ol class="steps">
            <li><span class="n">1</span><a href="/about">Read how the course works</a><span class="t">5 min</span></li>
            <li><span class="n">2</span><a :href="setupLink">Install Git and Python or R</a><span class="t">30 min</span></li>
            <!-- TODO(owner): confirm how students join the GitHub organisation. -->
            <li><span class="n">3</span><a href="/lectures/week-1#quick-admin">Create a GitHub account and register it on Moodle</a><span class="t">10 min</span></li>
            <li><span class="n">4</span><a :href="schedule.links.moodle">Join the course on Moodle</a><span class="t">Hand-ins go here</span></li>
          </ol>
          <p class="next">Then go to <a href="/lectures/week-1">Week 1</a>, before the first session on {{ firstSession }}.</p>
        </template>
        <div v-else class="bits">
          <a href="/about">How the course works</a>
          <a :href="setupLink">Setup guide</a>
          <a :href="schedule.links.moodle">Moodle</a>
        </div>
      </div>
    </div>

    <div v-for="w in schedule.weeks" :key="w.n" class="wk" :class="{ hi: w.n === currentWeek }">
      <div class="num">{{ w.n }}</div>
      <div>
        <div class="date">
          {{ weekDate(w.start) }}<template v-if="w.note"> · {{ w.note }}</template>
          <b v-if="w.n === currentWeek">This week</b>
        </div>
        <h3><a :href="w.link">{{ w.title }}</a></h3>
        <div v-if="assignment(w.hw)" class="bits">
          <span>
            <a :href="assignment(w.hw)!.link">{{ w.hw }}</a>
            {{ assignment(w.hw)!.name }}, due {{ formatWhen(new Date(assignment(w.hw)!.due)) }}
          </span>
        </div>
      </div>
    </div>

    <div class="assess">
      <div v-for="e in schedule.events" :key="e.kind + e.at">
        <div class="date">{{ formatEventWhen(e) }}</div>
        <h3><a :href="e.link">{{ e.title }}</a></h3>
        <div class="bits">{{ e.blurb }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wk {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 20px;
  padding: 24px 0;
  border-top: 1px solid var(--c-line);
}
.wk.zero {
  border-top: 0;
  padding-top: 0;
}
.wk.zero.open {
  background: var(--c-tint);
  margin: 0 -24px 8px;
  padding: 24px;
  border-radius: 3px;
}
.num {
  font-family: var(--font-serif);
  font-size: 46px;
  line-height: 1;
  color: var(--c-faint);
}
.wk.hi .num,
.date b {
  color: var(--c-accent);
}
.date {
  font-size: 14px;
  color: var(--c-muted);
}
.date b {
  font-weight: 600;
  margin-left: 10px;
}
h3 {
  font-family: var(--font-serif);
  font-weight: 500;
  font-size: 21px;
  line-height: 1.3;
  margin: 2px 0 8px;
}
h3 a {
  text-decoration: none !important;
}
h3 a:hover {
  text-decoration: underline !important;
}
.bits {
  font-size: 14.5px;
  color: var(--c-muted);
  display: flex;
  flex-wrap: wrap;
  gap: 4px 22px;
}
.bits a {
  font-weight: 500;
}
.steps {
  list-style: none;
  margin: 6px 0 0;
  padding: 0;
  font-size: 15px;
}
.steps li {
  display: grid;
  grid-template-columns: 22px 1fr auto;
  gap: 10px;
  padding: 7px 0;
  border-top: 1px solid var(--c-line);
  align-items: baseline;
}
.steps li:first-child {
  border-top: 0;
}
.steps .n,
.steps .t {
  color: var(--c-muted);
}
.steps .t {
  font-size: 13.5px;
}
.next {
  margin: 12px 0 0;
  font-size: 15px;
  font-weight: 500;
}
.assess {
  margin-top: 20px;
  border-top: 2px solid var(--c-text);
  padding-top: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}
.assess h3 {
  margin-top: 0;
}

@media (max-width: 640px) {
  .wk {
    grid-template-columns: 40px minmax(0, 1fr);
    gap: 14px;
  }
  .num {
    font-size: 32px;
  }
  .wk.zero.open {
    margin: 0 -16px 8px;
    padding: 20px 16px;
  }
  .steps li {
    grid-template-columns: 18px 1fr;
  }
  .steps .t {
    grid-column: 2;
  }
  .assess {
    grid-template-columns: 1fr;
  }
}
</style>
