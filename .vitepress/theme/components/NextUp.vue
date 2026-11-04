<script setup lang="ts">
import { formatWhen, type NextItem, type Phase } from '../schedule/logic'

defineProps<{ items: NextItem[]; phase: Phase }>()
</script>

<template>
  <section v-if="items.length" class="next-up">
    <h2>Next up</h2>
    <p v-for="item in items" :key="item.at.getTime() + item.label">
      <b>{{ formatWhen(item.at, true) }}</b><br />
      <a v-if="item.link" :href="item.link">{{ item.label }}</a>
      <template v-else>{{ item.label }}</template>
    </p>
    <p v-if="phase === 'before'" class="muted">Set up before then — see week 0.</p>
  </section>
</template>

<style scoped>
.next-up {
  border-top: 1px solid var(--c-line);
  padding-top: 18px;
  margin-bottom: 24px;
}
h2 {
  font-family: var(--font-sans);
  font-size: 14.5px;
  font-weight: 600;
  margin: 0 0 10px;
  border: 0;
  padding: 0;
}
p {
  margin: 0 0 12px;
  font-size: 15px;
  line-height: 1.5;
}
b {
  font-weight: 500;
}
.muted {
  color: var(--c-muted);
}
</style>
