<script setup lang="ts">
// Inlines a diagram from public/img/introduction/ (made by scripts/introduction_figures.py),
// so it takes the site's colours in light and dark mode.
const files = import.meta.glob('../../../public/img/introduction/diagram-*.svg', {
  query: '?raw', import: 'default', eager: true,
}) as Record<string, string>

const props = defineProps<{ name: string; caption?: string }>()
const svg = Object.entries(files).find(([path]) => path.endsWith(`/${props.name}.svg`))?.[1] ?? ''
</script>

<template>
  <figure class="inline-svg">
    <div v-html="svg" />
    <figcaption v-if="caption">{{ caption }}</figcaption>
  </figure>
</template>

<style scoped>
.inline-svg {
  margin: 24px 0;
}
.inline-svg :deep(svg) {
  display: block;
  width: 100%;
  height: auto;
}
figcaption {
  margin-top: 8px;
  font-size: 14px;
  color: var(--c-muted);
}
</style>
