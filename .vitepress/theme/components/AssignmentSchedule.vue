<script setup lang="ts">
import { schedule } from '../schedule/data'
import { formatWhen } from '../schedule/logic'
</script>

<template>
  <table>
    <thead>
      <tr><th>Assignment</th><th>Hand-in</th><th>Peer review</th></tr>
    </thead>
    <tbody>
      <tr v-for="a in schedule.assignments" :key="a.id">
        <td><a :href="a.link">{{ a.id }}</a> {{ a.name }}</td>
        <td>{{ formatWhen(new Date(a.due), true) }}</td>
        <td>{{ formatWhen(new Date(a.peerDue), true) }}</td>
      </tr>
    </tbody>
  </table>
</template>
