# HW4
Your name

<!--
Your report for HW4. The assignment is on the course site: https://su-mt4008.github.io/homework/4
Keep the seven sections below, in this order; replace each prompt with your own text and code.
Your data goes in hw4/data/raw/; read it with a relative path such as "data/raw/file.csv".
Render everything with the command under "How to reproduce", and commit report.md too.
Write your code in the language you chose for the course: start code chunks
with {python} or {r}. See example/python/ or example/r/ for a worked example in your language.
-->

## Question

*What do you want to find out, and why does it matter? Make it a
question the data can answer.*

## Data

*Where does the data come from, how was it collected, and what can it
not tell you?*

## Cleaning

*What did you change, and why? Every decision is in code, never by
hand.*

## Exploration

*Look at the data before drawing conclusions: distributions,
relationships, surprises.*

## Analysis

*Answer the question with a method that fits it, and check that the
answer holds up.*

## Conclusions & limitations

*What does the evidence support, how sure are you, and what could
explain it otherwise?*

## How to reproduce

*Exactly what someone needs to do to get the same result. Keep the
commands for your language.*

Python:

``` bash
uv sync
uv run quarto render
```

R:

``` bash
Rscript -e 'renv::restore()'
quarto render
```
