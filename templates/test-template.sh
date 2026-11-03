#!/usr/bin/env bash
# Usage: templates/test-template.sh python|r
# Does what the GitHub check does, on a fresh copy of a template:
# install the locked environment, render report.qmd, and check that
# report.md has the seven report sections in order.
set -euo pipefail

lang=${1:?usage: test-template.sh python|r}
here=$(cd "$(dirname "$0")" && pwd)
src="$here/$lang"
[ -d "$src" ] || { echo "FAIL: no template at $src"; exit 1; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -R "$src/." "$work/"
# A fresh clone has no local environment, and the check must not rely on a committed render.
rm -rf "$work/report.md" "$work/report_files" "$work/.venv" "$work/renv/library" "$work/.quarto"
cd "$work"

case $lang in
  python) uv sync --locked && uv run quarto render report.qmd ;;
  r) Rscript -e 'renv::restore(prompt = FALSE)' && quarto render report.qmd ;;
  *) echo "FAIL: unknown language $lang"; exit 1 ;;
esac

[ -f report.md ] || { echo "FAIL: report.md was not rendered"; exit 1; }

sections=("Question" "Data" "Cleaning" "Exploration" "Analysis" "Conclusions & limitations" "How to reproduce")
prev=0
for s in "${sections[@]}"; do
  line=$(grep -n -m1 -x -F "## $s" report.md | cut -d: -f1 || true)
  if [ -z "$line" ] || [ "$line" -le "$prev" ]; then
    echo "FAIL: section '## $s' missing or out of order in report.md"
    exit 1
  fi
  prev=$line
done

echo "PASS: $lang template renders from a fresh copy"
