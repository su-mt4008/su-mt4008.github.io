<script setup lang="ts">
import { schedule } from '../schedule/data'
import { formatWhen } from '../schedule/logic'
import { deckFor } from '../schedule/decks'
</script>

<template>
  <table>
    <thead>
      <tr><th>Week</th><th>Monday</th><th>Topic</th><th>Slides</th></tr>
    </thead>
    <tbody>
      <tr v-for="w in schedule.weeks" :key="w.n">
        <td>{{ w.n }}</td>
        <td>{{ formatWhen(new Date(`${w.start}T12:00:00+01:00`)) }}</td>
        <td><a :href="w.link">{{ w.title }}</a><template v-if="w.note"> · {{ w.note }}</template></td>
        <td><a v-if="deckFor(w.link)" :href="deckFor(w.link)" target="_blank" rel="noopener">Slides</a></td>
      </tr>
    </tbody>
  </table>
</template>
