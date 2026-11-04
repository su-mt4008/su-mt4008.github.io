#!/usr/bin/env bash
# Usage: templates/test-template.sh assignments|project-python|project-r
# Does what the GitHub check does, on a fresh copy of a template: install the
# locked environment, render with one command, and check that each report.md
# has the seven report sections in order.
# assignments: the one assignments template, for Python and R students alike. It is
#   tested twice, once as each: hw1 gets a code chunk in that language, then every
#   report is rendered with that language's command, and so is its example.
# project-python, project-r: one report.qmd at the top.
set -euo pipefail

name=${1:?usage: test-template.sh assignments|project-python|project-r}
here=$(cd "$(dirname "$0")" && pwd)
src="$here/$name"
[ -d "$src" ] || { echo "FAIL: no template at $src"; exit 1; }

sections=("Question" "Data" "Cleaning" "Exploration" "Analysis" "Conclusions & limitations" "How to reproduce")
check_sections() {
  for dir in "$@"; do
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
}

# A fresh clone has no local environment, and the check must not rely on committed renders.
fresh_copy() {
  local dir
  dir=$(mktemp -d)
  cp -R "$src/." "$dir/"
  rm -rf "$dir/.venv" "$dir/renv/library" "$dir/.quarto"
  find "$dir" -name report.md -delete
  find "$dir" -type d -name report_files -prune -exec rm -rf {} +
  echo "$dir"
}

# What a student's report has: a code chunk in their language, under "## Data".
add_chunk() {
  local lang=$1 file=$2 code
  case $lang in
    python) code='print(1 + 1 == 2)' ;;
    r) code='print(1 + 1 == 2)' ;;
  esac
  awk -v lang="$lang" -v code="$code" '{ print } /^## Data$/ { print ""; print "```{" lang "}"; print code; print "```" }' "$file" > "$file.new"
  mv "$file.new" "$file"
}

work=""
trap 'if [ -n "$work" ]; then rm -rf "$work"; fi' EXIT

case $name in
  assignments)
    for lang in python r; do
      work=$(fresh_copy)
      cd "$work"
      add_chunk "$lang" hw1/report.qmd
      case $lang in
        python) uv sync --locked && uv run quarto render && uv run quarto render example/python/report.qmd ;;
        r) Rscript -e 'renv::restore(prompt = FALSE)' && quarto render && quarto render example/r/report.qmd ;;
      esac
      check_sections hw1 hw2 hw3 hw4 hw5 "example/$lang"
      grep -qE 'TRUE|True' hw1/report.md || { echo "FAIL: the $lang chunk in hw1 did not run"; exit 1; }
      cd "$here"; rm -rf "$work"; work=""
      echo "ok: a $lang student renders every report, and example/$lang"
    done
    ;;
  project-python|project-r)
    work=$(fresh_copy)
    cd "$work"
    case ${name#project-} in
      python) uv sync --locked && uv run quarto render report.qmd ;;
      r) Rscript -e 'renv::restore(prompt = FALSE)' && quarto render report.qmd ;;
    esac
    check_sections .
    ;;
  *) echo "FAIL: unknown template $name"; exit 1 ;;
esac

echo "PASS: $name template renders every report from a fresh copy"
