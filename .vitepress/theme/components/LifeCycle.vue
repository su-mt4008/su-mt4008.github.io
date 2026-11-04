<script setup lang="ts">
// Inlines a life-cycle diagram from public/img/introduction/ (made by
// scripts/introduction_figures.py), so it takes the site's colours in light and dark mode.
const diagrams = import.meta.glob('../../../public/img/introduction/lifecycle-*.svg', {
  query: '?raw', import: 'default', eager: true,
}) as Record<string, string>

const props = defineProps<{ name: string }>()
const find = (file: string) => Object.entries(diagrams).find(([path]) => path.endsWith(file))?.[1] ?? ''
// The tall version of the diagram: it fits the text column and phones.
const tall = find(`lifecycle-${props.name}-tall.svg`)
</script>

<template>
  <figure class="lifecycle">
    <div class="tall" v-html="tall" />
  </figure>
</template>

<style scoped>
.lifecycle {
  margin: 24px 0;
  padding: 8px 0;
  border-top: 1px solid var(--c-line);
  border-bottom: 1px solid var(--c-line);
}
.lifecycle :deep(svg) {
  display: block;
  width: 100%;
  max-width: 640px;
  height: auto;
}
</style>
