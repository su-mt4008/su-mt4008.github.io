#!/usr/bin/env bash
# Usage: templates/test-template.sh python|r|project-python|project-r
# Does what the GitHub check does, on a fresh copy of a template: install the
# locked environment, render with one command, and check that each report.md
# has the seven report sections in order.
# python, r: assignments templates (example/ and hw1/ ... hw5/).
# project-python, project-r: one report.qmd at the top.
set -euo pipefail

name=${1:?usage: test-template.sh python|r|project-python|project-r}
lang=${name#project-}
here=$(cd "$(dirname "$0")" && pwd)
src="$here/$name"
[ -d "$src" ] || { echo "FAIL: no template at $src"; exit 1; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -R "$src/." "$work/"
# A fresh clone has no local environment, and the check must not rely on committed renders.
rm -rf "$work/.venv" "$work/renv/library" "$work/.quarto"
find "$work" -name report.md -delete
find "$work" -type d -name report_files -prune -exec rm -rf {} +
cd "$work"

if [ -f _quarto.yml ]; then dirs=(example hw1 hw2 hw3 hw4 hw5); target=""; else dirs=(.); target=report.qmd; fi

case $lang in
  python) uv sync --locked && uv run quarto render $target ;;
  r) Rscript -e 'renv::restore(prompt = FALSE)' && quarto render $target ;;
  *) echo "FAIL: unknown language $lang"; exit 1 ;;
esac

sections=("Question" "Data" "Cleaning" "Exploration" "Analysis" "Conclusions & limitations" "How to reproduce")
for dir in "${dirs[@]}"; do
  report="$dir/report.md"
  [ -f "$report" ] || { echo "FAIL: $report was not rendered"; exit 1; }
  prev=0
  for s in "${sections[@]}"; do
    line=$(grep -n -m1 -x -F "## $s" "$report" | cut -d: -f1 || true)
    if [ -z "$line" ] || [ "$line" -le "$prev" ]; then
      echo "FAIL: section '## $s' missing or out of order in $report"
      exit 1
    fi
    prev=$line
  done
done

echo "PASS: $name template renders every report from a fresh copy"
