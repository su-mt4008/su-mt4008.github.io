<script setup lang="ts">
import { computed } from 'vue'
import { schedule } from '../schedule/data'
import { formatEventWhen, type CourseEvent } from '../schedule/logic'

const props = defineProps<{ kind: CourseEvent['kind'] }>()
const event = computed(() => schedule.events.find((e) => e.kind === props.kind))
</script>

<template>
  <strong v-if="event">{{ formatEventWhen(event) }} (Stockholm time)</strong>
</template>
