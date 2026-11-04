<script setup lang="ts">
import { schedule } from '../schedule/data'
import { formatWhen } from '../schedule/logic'
</script>

<template>
  <table>
    <thead>
      <tr><th>Assignment</th><th>Hand-in</th><th>Peer review</th><th>Final version</th></tr>
    </thead>
    <tbody>
      <tr v-for="a in schedule.assignments" :key="a.id">
        <td>
          <a v-if="a.link" :href="a.link">{{ a.id }}</a><template v-else>{{ a.id }}</template>
          {{ a.name }}<span v-if="!a.link" class="soon"> (coming soon)</span>
        </td>
        <td>{{ formatWhen(new Date(a.due), true) }}</td>
        <td>{{ formatWhen(new Date(a.peerDue), true) }}</td>
        <td>{{ formatWhen(new Date(a.finalDue), true) }}</td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.soon {
  color: var(--c-muted);
}
</style>
