// Kept apart from data.ts: import.meta.glob only exists in Vite-built code (the theme),
// not in .vitepress/config.mts, which imports data.ts.
// Lecture decks: every slides/<name>/index.qmd is served at /slides/<name>/ and linked from
// the lecture page /lectures/<name> (see slides/_quarto.yml). Only the file names are read here.
export const decks = Object.keys(import.meta.glob('../../../slides/*/index.qmd', { query: '?raw' }))
  .map((path) => path.split('/').at(-2)!)
export const deckUrl = (name: string) => (decks.includes(name) ? `/slides/${name}/index.html` : undefined)
// The deck for a page path such as /lectures/week-1 or /lectures/week-1.html, if it has one.
export const deckFor = (path: string) => {
  const m = path.match(/^\/lectures\/([\w-]+?)(\.html)?$/)
  return m ? deckUrl(m[1]) : undefined
}

