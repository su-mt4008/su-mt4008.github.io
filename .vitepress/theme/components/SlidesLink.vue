<script setup lang="ts">
// Shown at the top of a lecture page that has a deck in slides/ (see slides/_quarto.yml).
import { computed } from 'vue'
import { useRoute } from 'vitepress'
import { deckFor } from '../schedule/decks'

const route = useRoute()
const deck = computed(() => deckFor(route.path))
</script>

<template>
  <p v-if="deck" class="slides-link">
    <a :href="deck" target="_blank" rel="noopener">Slides</a>
    <span>Press <kbd>F</kbd> for full screen, <kbd>S</kbd> for speaker notes</span>
  </p>
</template>

<style scoped>
.slides-link {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px 16px;
  margin: 0 0 24px;
  font-size: 14px;
  color: var(--c-muted);
}
.slides-link a {
  font-weight: 600;
  color: var(--c-text);
  text-decoration: underline;
  text-decoration-color: var(--c-accent);
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;
}
.slides-link a::after {
  content: ' ↗';
  font-weight: 400;
}
kbd {
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 0 5px;
  border: 1px solid var(--c-line);
  border-radius: 3px;
}
</style>
