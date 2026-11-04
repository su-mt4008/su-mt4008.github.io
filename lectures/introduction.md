---
outline: 2
---

# Introduction: three questions, one cycle

The first session of the course, {{ $course.firstSession }}. This page tells the same story as
the slides, for reading afterwards or if you missed it.

The session has two halves. The first, these slides, shows what this course is about through
three real projects, then goes through how the course works. After the break comes
[week 1](/lectures/week-1), with its own slides, including the [statistics you need](/statistics).

## The data science cycle

Every analysis in this course, from the first assignment to your project, goes round the same
cycle: a **question**, the **data**, **cleaning** it, then **exploration** and **analysis**, round
and round, and finally **conclusions**. To answer more, you go back: fetch more data, or refine
the question, and round again. Being
**reproducible** is not a last step: it frames every step, from the first line of code.

<InlineSvg name="diagram-cycle" caption="Exploration and analysis go round and round; to answer more, go back to fetch more data or refine the question; being reproducible frames every step. After the cycle in Wickham, Çetinkaya-Rundel & Grolemund, R for Data Science (2e)." />

Your reports follow the cycle in seven sections: Question, Data, Cleaning, Exploration,
Analysis, Conclusions & limitations, and How to reproduce.

Below are three projects told along these steps, from small to ambitious. Each is a complete
report you can clone and render yourself:
[su-mt4008/lecture-demos/introduction](https://github.com/su-mt4008/lecture-demos/tree/main/introduction).
In each diagram, the red step is where the real work of that project was.

## 1. Are baby names a fashion? {#names}

*A small project: one source, a clear question, honest about its limits.*

People often say names skip three generations: the names of great-grandparents come back once
nobody's parents have them. Statistics Sweden (SCB) publishes how many people alive in 2021
have each of the 200 most common first names, by year of birth from 1922 to 2021. That is
enough to check.

![Share of births named Elsa, Alice and Astrid, 1922–2021: high in the 1920s, almost zero in 1960–80, high again after 2000](/img/introduction/names-comebacks.svg)

The pattern is easy to find. Elsa, Alice, Astrid, Ebba, Agnes and Axel were common in the 1920s,
nearly vanished around 1970 and are among the most common names again today.

The interesting part is the **limitation**. The table counts people *alive in 2021*: someone
born in 1925 who has died or emigrated is not in it. And it only lists names that are common
*today*, so a 1920s name that never came back is missing altogether. The data is tilted towards
finding comebacks. Saying that clearly is part of the result, not a footnote.

<LifeCycle name="names" />

**Why this is a good project:** the question is sharp, the data fits it, and the conclusion says
exactly how far the data reaches.

## 2. Why does electricity cost more in Malmö than in Luleå? {#electricity}

*A medium project: sources combined, an analysis beyond description, with its uncertainty.*

Sweden has four electricity price zones, from SE1 (Luleå) in the north to SE4 (Malmö) in the
south. Southern households often pay several times as much. How big is the gap, and does it go
with the weather? If wind power in the south pushes prices down, the gap should be smaller on
windy days in Malmö.

![Monthly mean spot price in SE4 Malmö and SE1 Luleå, 2023–2025](/img/introduction/electricity-zones.svg)

The project joins three files: three years of spot prices for the four zones from a free API,
and SMHI's wind and temperature in Malmö. Most of the work is in the **cleaning**, and none of
it shows in the final figure:

- the market went from hourly to 15-minute prices in October 2025, so a plain mean of the rows
  weighs a quarter-hour like an hour;
- the clocks change twice a year, so some days have 23 or 25 hours;
- the prices have UTC timestamps and the weather has Swedish dates, so the join has to use the
  right day;
- 22 of the 1,096 days have no weather data; they are dropped, and the report says so.

![Mean price gap between Malmö and Luleå, by wind quarter](/img/introduction/electricity-wind.svg)

On the calmest quarter of days, Malmö paid 0.55 kr/kWh more than Luleå; on the windiest, 0.15.
The difference, 0.40 kr/kWh, has a 95% bootstrap interval of 0.34 to 0.47, so it is not chance.
But wind and temperature explain only 18% of the day-to-day gap. The rest is what the data does
not contain: how much power the grid can carry south, nuclear plants in maintenance, prices on
the continent. And windy days differ from calm ones in other ways too: correlation, not cause.

<LifeCycle name="electricity" />

**Why this is a step up:** several sources combined, a comparison with its uncertainty, and a
discussion of what the analysis can't separate.

## 3. Is AI a bubble? {#ai-bubble}

*An ambitious project: a question that first has to be made measurable, checked from several
sides.*

Nobody can measure a bubble, and whether one bursts is a prediction, not a fact in any dataset.
So the first job, and the hardest, is turning the question into things data can answer. Bubbles
are usually described by three signs:

| A bubble means … | We measure | Source |
|:--|:--|:--|
| prices far above what companies earn | the cyclically adjusted price/earnings ratio (CAPE) of US stocks | Robert Shiller, since 1871 |
| prices that rose unusually fast | the NASDAQ index compared with five years earlier | FRED |
| everybody talking about it | the share of Hacker News story titles that mention AI | HN Search API |

The question becomes: how do today's values of these signs compare with 1929, the dot-com
bubble of 2000 and the crypto boom?

![CAPE of US stocks since 1881, with 1929, 2000 and today marked](/img/introduction/ai-cape.svg)

![The NASDAQ index divided by its value five years earlier](/img/introduction/ai-nasdaq.svg)

![Share of Hacker News story titles mentioning AI, crypto and bitcoin](/img/introduction/ai-attention.svg)

Two of the three signs are there. US stocks are priced higher relative to earnings than at any
time except the months around 2000, and higher than before the 1929 crash. AI is in about 14% of
Hacker News titles, close to its peak and about four times the highest share bitcoin ever had.
But the third sign is missing: the NASDAQ is 1.6 times its value five years ago, an ordinary
pace, far from the 5.9 times of 2000. A project that only showed the first two figures would
have told a more exciting story, and a less true one.

The honest conclusion: **two of the three signs that came before earlier crashes are there;
whether a crash follows is not in the data.** High valuations can last for years, and if AI raises earnings as
much as the market expects, today's prices may turn out reasonable. The three signs are a
choice, the data is about the US and an English-language forum, and history has only a handful
of bubbles to compare with.

There are cleaning traps here too: Shiller writes October as `2026.1`, which read as a number is
January.

<LifeCycle name="ai-bubble" />

**Why this is ambitious:** a vague question made measurable, several independent sources,
results checked against history, and conclusions that would convince a sceptical reader,
including about what they can't conclude.

## Same cycle, bigger question

The three reports are about the same length. What grows from one to the next is the question,
the number of sources and the care in the conclusions, not the number of pages. Keep that in
mind when you plan your [project](/project).

## How the course works

The second part of the session went through the practical side. Everything is on this site:

- **[About the course](/about):** what the course is, how a week works, the learning goals.
- **[Assignments](/homework/):** five assignments, the scoring rules and every deadline. The
  final deadline for all of them is {{ $course.finalDeadline }}.
- **[How we work](/guide):** setting up your computer, handing in with a pull request, the
  reproducibility check and peer review.
- **[Project](/project):** groups of 2–3, a proposal by {{ $course.proposal.replace('Due ', '') }}
  on Moodle, presentations {{ $course.presentation }}.
- **[Exam](/exam/):** written, {{ $course.exam }}.

## Week 1 and statistics

The second half of the session followed [week 1](/lectures/week-1) and its slides (reproducible
analysis, lockfiles, Quarto, Git and the check) and [Statistics: the basics](/statistics)
(standard errors, confidence intervals, the bootstrap, tests and their traps). Read both before starting
[HW1](/homework/1).

## Reproduce the three projects

```bash
git clone https://github.com/su-mt4008/lecture-demos
cd lecture-demos/introduction
uv sync
uv run quarto render
```

The data is saved in the repository, so this works without downloading anything. Each project
also has a `fetch` script that downloads its data again.

