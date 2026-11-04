---
outline: [2, 3]
---

# Statistics: the basics

Data science is about answering questions with data. But data are noisy: if you measured again,
you would get slightly different numbers. **Statistics** is how we tell a real pattern from that
noise, and say honestly how sure we are.

This page is the bare minimum you need for the course, explained from the ground up. It builds on
what you know from **Probability Theory I** (MT3001, Alm & Britton’s *Stokastik*): random
variables, expected value, variance, the law of large numbers and the central limit theorem. Each
section says **what** we do, **why**, then the maths, a figure, and a few lines of code.

**The running example:** *Has Lund got warmer?* SMHI has measured the temperature in Lund every
day since 1784. We compare the mean annual temperature in **1997–2010** with **2011–2025**.
(In [HW1](/homework/1) you ask the same question for Stockholm.) Download the data to follow
along: [smhi-lund-daily-temperature.csv](/data/statistics/smhi-lund-daily-temperature.csv)
(SMHI Open Data, station 53430, CC BY 4.0).

:::code-group
```python [Python]
import numpy as np
import pandas as pd

raw = pd.read_csv("smhi-lund-daily-temperature.csv", sep=";", skiprows=12, header=0,
                  usecols=[2, 3], names=["date", "temp"], parse_dates=["date"])
per_year = raw.groupby(raw["date"].dt.year)["temp"].mean()  # mean temperature per year
a = per_year.loc[1997:2010]   # 14 years
b = per_year.loc[2011:2025]   # 15 years
```
```r [R]
raw <- read.csv("smhi-lund-daily-temperature.csv", sep = ";", skip = 12)[, 3:4]
names(raw) <- c("date", "temp")
raw$year <- as.integer(substr(raw$date, 1, 4))
per_year <- aggregate(temp ~ year, data = raw, FUN = mean)  # mean temperature per year
a <- per_year$temp[per_year$year >= 1997 & per_year$year <= 2010]   # 14 years
b <- per_year$temp[per_year$year >= 2011 & per_year$year <= 2025]   # 15 years
```
:::

(All years from 1997 to 2025 are complete in this file. Always check that first: a year with
half its days missing has a misleading mean.)

![Mean annual temperature in Lund, 1997–2025, with the mean of each period](/img/statistics/data.svg)

The second period looks warmer: 9.71 °C against 8.89 °C, a difference of **0.82 °C**. The rest of
this page is about one question: *is that difference real, or could it be weather?*

## 1. From probability to statistics

In Probability Theory I the model was given, and you worked out what data it produces: *if a coin
is fair, how likely are 7 heads in 10 throws?* Statistics runs the other way: you have the data,
and you ask what model produced it: *I got 7 heads in 10 throws; is the coin fair?*

```
probability:   model  ──►  data      “if the climate is like this, what temperatures will we see?”
statistics:    data   ──►  model     “we saw these temperatures, what is the climate like?”
```

The tools are the ones you already have. A quick reminder of the ones we use:

| Concept | Notation | Svenska | What we use it for |
|---|---|---|---|
| Random variable | $X$ | stokastisk variabel | one measurement, before we see its value |
| Expected value | $E[X] = \mu$ | väntevärde | the “true” average we want to know |
| Variance, standard deviation | $\operatorname{Var}(X) = \sigma^2$, $\sigma$ | varians, standardavvikelse | how much single measurements scatter |
| Independence | | oberoende | lets us add up variances |
| Normal distribution | $N(\mu, \sigma^2)$ | normalfördelning | the shape averages end up with |
| Law of large numbers | $\bar X_n \to \mu$ | stora talens lag | averages of more data get closer to $\mu$ |
| Central limit theorem | $\bar X_n \approx N(\mu, \sigma^2/n)$ | centrala gränsvärdessatsen | tells us *how* close |

## 2. Data are observations of random variables

**What.** We treat the mean temperature of each year as a random variable $X_1, \dots, X_n$. Each
year is the same underlying climate, with expected value $\mu$, plus that year’s weather, which
scatters it by about $\sigma$. The 14 years 1997–2010 are our **sample**; the numbers we see are
**observations** $x_1, \dots, x_n$ of those random variables.

**Why.** It gives a precise meaning to “the climate” ($\mu$, which we never observe directly) as
opposed to “the weather we happened to get” (the $x_i$). Everything below is about learning
$\mu$ from the $x_i$, and saying how well we know it.

Two words to keep apart:

- a **parameter** is a property of the model, like $\mu$ or $\sigma$: fixed, but unknown;
- an **estimate** is a number we compute from the data to guess it, like the average $\bar x$.

We will also assume the years are **independent** and have **the same** $\mu$ and $\sigma$ within
a period. That is a simplification (weather in one year barely affects the next, but the climate
might drift *within* a period), and [section 6](#_6-relationships-correlation-and-trend) shows
how to look at the drift directly. Every analysis rests on assumptions like these; good ones say
so.

## 3. Describe before you test

**What.** Summarise each period with a centre and a spread:

$$
\bar x = \frac{1}{n}\sum_{i=1}^{n} x_i \qquad
s = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n} (x_i - \bar x)^2}
$$

$\bar x$ (the **mean**) estimates $\mu$, and $s$ (the **standard deviation**) estimates $\sigma$.
(We divide by $n-1$ rather than $n$ because the $x_i$ are, on average, a bit closer to their own
mean $\bar x$ than to the true $\mu$; $n-1$ corrects for that.) The **median**, the middle value,
is a second measure of centre that a single extreme year can’t drag around.

**Why.** Before asking whether 0.82 °C is “a lot”, you need something to compare it with. The
spread of single years is that yardstick.

| Period | $n$ | mean | median | standard deviation |
|---|---|---|---|---|
| 1997–2010 | 14 | 8.89 °C | 8.84 °C | 0.62 °C |
| 2011–2025 | 15 | 9.71 °C | 9.88 °C | 0.62 °C |

![Each dot is one year; red shows the mean plus and minus one standard deviation](/img/statistics/spread.svg)

Single years vary by about ±0.6 °C, nearly as much as the difference between the periods. So one
warm year proves nothing: plenty of years in the first period are warmer than some in the second.
Whether the *means* differ needs the next step.

:::code-group
```python [Python]
a.mean(), a.median(), a.std()   # pandas' std divides by n - 1
```
```r [R]
c(mean(a), median(a), sd(a))   # sd divides by n - 1
```
:::

**Always plot first.** A summary can hide a lot: an outlier, two groups mixed together, a trend.
The figure takes one line and often answers half the question.

## 4. How sure are you? Standard errors and confidence intervals

**What.** The mean $\bar x = 8.89$ °C is itself an observation of a random variable, $\bar X$.
With a different 14 years of weather, we would have got a different mean. The question is how
different. That is the **uncertainty** of our estimate.

**Why.** An estimate without its uncertainty can’t be interpreted. “8.89 °C, give or take 0.01”
and “8.89 °C, give or take 2” mean completely different things.

### The standard error

You know from Probability Theory I how the mean of independent variables behaves:

$$
E[\bar X] = \mu, \qquad
\operatorname{Var}(\bar X) = \operatorname{Var}\Big(\frac{1}{n}\sum_{i=1}^n X_i\Big) = \frac{1}{n^2}\cdot n\sigma^2 = \frac{\sigma^2}{n}.
$$

So the mean is centred on the truth, and its standard deviation, called the **standard error**,
shrinks with the square root of the sample size:

$$
\operatorname{SE} = \frac{\sigma}{\sqrt n} \approx \frac{s}{\sqrt n} = \frac{0.62}{\sqrt{14}} = 0.17 \text{ °C}.
$$

![Simulated: the temperature of one year (grey) scatters much more than the mean of 14 years (red)](/img/statistics/sampling.svg)

That is the law of large numbers made precise: one year scatters by 0.62 °C, but the mean of
14 years by only 0.17 °C. To halve the uncertainty, you need four times the data.

### The confidence interval

The central limit theorem says $\bar X$ is approximately normal, $\bar X \approx N(\mu, \operatorname{SE}^2)$.
A normal variable lands within 1.96 standard deviations of its mean 95% of the time, so

$$
P\big(\mu - 1.96\,\operatorname{SE} \le \bar X \le \mu + 1.96\,\operatorname{SE}\big) \approx 0.95 .
$$

Turn the inequality around and you get the **95% confidence interval** for $\mu$:

$$
\bar x \pm 1.96\,\frac{s}{\sqrt n} = 8.89 \pm 1.96 \cdot 0.17 = [8.57,\ 9.22] \text{ °C}.
$$

**What “95%” means.** It is a property of the *method*, not of this one interval: if we could
repeat the whole thing with new data many times, 95% of the intervals we built would contain the
true $\mu$. In the simulation below, one of the 20 intervals misses, which is what we expect.

![Simulated: 20 samples of 14 years, each with its 95% interval; the red one misses the true mean (dashed)](/img/statistics/intervals.svg)

::: tip Small samples
With few observations, using $s$ instead of $\sigma$ adds extra uncertainty, and the exact
interval uses the $t$-distribution: 2.16 instead of 1.96 for $n = 14$. The idea is the same;
software does this for you.
:::

### Comparing the two periods

What we really want is the **difference** $\mu_b - \mu_a$. The estimate is
$\bar x_b - \bar x_a = 0.82$ °C. The two periods are independent, so their variances add:

$$
\operatorname{SE}_{\text{diff}} = \sqrt{\frac{s_a^2}{n_a} + \frac{s_b^2}{n_b}} = 0.23 \text{ °C},
\qquad 0.82 \pm 1.96 \cdot 0.23 = [0.37,\ 1.27] \text{ °C}.
$$

The whole interval is above zero: the data are consistent with warming of anywhere between about
0.4 and 1.3 °C, but not with no warming at all.

:::code-group
```python [Python]
diff = b.mean() - a.mean()
se_diff = np.sqrt(a.var() / len(a) + b.var() / len(b))
diff - 1.96 * se_diff, diff + 1.96 * se_diff
```
```r [R]
diff <- mean(b) - mean(a)
se_diff <- sqrt(var(a) / length(a) + var(b) / length(b))
c(diff - 1.96 * se_diff, diff + 1.96 * se_diff)
```
:::

### The same idea by computer: the bootstrap

The formula needed the CLT and a formula for the standard error. For many quantities (a median,
a ratio, a correlation) there is no simple formula. The **bootstrap** gets the uncertainty by
simulation instead: pretend the sample *is* the population, draw new samples from it **with
replacement**, recompute the difference each time, and look at how much it varies.

![The difference in 10,000 resampled datasets; the middle 95% (red) is the bootstrap interval](/img/statistics/bootstrap.svg)

The middle 95% of the resampled differences gives roughly [0.40, 1.26] °C, almost the same as
the formula. (Simulations give slightly different numbers each run; that is expected.)

:::code-group
```python [Python]
rng = np.random.default_rng(1)   # a seed makes the simulation reproducible
boot = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(10_000)]
np.percentile(boot, [2.5, 97.5])
```
```r [R]
set.seed(1)   # a seed makes the simulation reproducible
boot <- replicate(10000, mean(sample(b, replace = TRUE)) - mean(sample(a, replace = TRUE)))
quantile(boot, c(0.025, 0.975))
```
:::

## 5. Could it be chance? Hypothesis tests and p-values

**What.** A **test** asks one specific question: *if there were no real difference, how surprising
would our data be?* We write the “no difference” model as the **null hypothesis**
$H_0: \mu_a = \mu_b$, and measure how far our result is from it.

**Why.** Weather alone produces differences between periods. A test tells you whether the
difference you found is larger than weather alone would plausibly produce.

If $H_0$ is true, the CLT says the difference is approximately $N(0, \operatorname{SE}_{\text{diff}}^2)$.
Our difference is

$$
z = \frac{\bar x_b - \bar x_a}{\operatorname{SE}_{\text{diff}}} = \frac{0.82}{0.23} = 3.6
$$

standard errors away from zero. The **p-value** is the probability, if $H_0$ were true, of a
difference at least that far from zero in either direction:
$p = P(|Z| \ge 3.6) \approx 0.0003$.

### The same idea by computer: the permutation test

If the period made no difference, the labels “1997–2010” and “2011–2025” would be arbitrary. So
**shuffle** the years between the two periods at random, recompute the difference, and repeat
many times. That shows what differences pure chance produces. The p-value is the share of
shuffles that give a difference at least as large as the real one.

![Differences when the years are shuffled at random; the observed 0.82 °C (red line) is far out in the tail](/img/statistics/permutation.svg)

Only about 1 in 1,000 shuffles gives a difference as large as 0.82 °C, so $p \approx 0.001$.
Weather alone is a very unlikely explanation.

:::code-group
```python [Python]
pooled = np.concatenate([a, b])
perm = []
for _ in range(10_000):
    rng.shuffle(pooled)
    perm.append(pooled[len(a):].mean() - pooled[:len(a)].mean())
np.mean(np.abs(perm) >= abs(diff))   # the p-value
```
```r [R]
pooled <- c(a, b)
perm <- replicate(10000, { s <- sample(pooled); mean(s[-(1:length(a))]) - mean(s[1:length(a)]) })
mean(abs(perm) >= abs(diff))   # the p-value
```
:::

### What a p-value is not

- It is **not** the probability that $H_0$ is true. It is the probability of data like ours *if*
  $H_0$ were true.
- It does **not** say how big the effect is. A tiny, unimportant difference can have a very small
  p-value if you have enough data. Report the **difference and its interval**; the p-value only
  adds “unlikely to be chance”.
- **0.05 is a convention, not a law of nature.** $p = 0.049$ and $p = 0.051$ are the same
  evidence.

## 6. Relationships: correlation and trend

**What.** Instead of cutting the years into two periods, look at temperature against year
directly. Two numbers describe how they move together:

- the **correlation** $r$, between $-1$ and $1$: how closely the points follow a straight line
  ($r = 0.62$ here);
- the **slope** $\beta$ of the best straight line $y = \alpha + \beta\,x$, found by **least
  squares** (the line that minimises $\sum_i (y_i - \alpha - \beta x_i)^2$): how much $y$ changes
  per unit of $x$.

**Why.** Splitting into periods throws information away and depends on where you split. The slope
uses every year and answers the question in a natural unit.

![Mean annual temperature in Lund with the least-squares line](/img/statistics/trend.svg)

The slope is **0.54 °C per decade**, with a 95% interval of about [0.27, 0.80]. Like the mean,
the slope is an estimate with a standard error, and software gives you both.

:::code-group
```python [Python]
years = per_year.loc[1997:2025]
slope, intercept = np.polyfit(years.index, years.values, 1)
r = np.corrcoef(years.index, years.values)[0, 1]
```
```r [R]
years <- subset(per_year, year >= 1997 & year <= 2025)
fit <- lm(temp ~ year, data = years)
coef(fit)       # intercept and slope
confint(fit)    # 95% intervals
cor(years$year, years$temp)
```
:::

## 7. Correlation is not causation

**What.** A relationship in data does not tell you what causes what. Ice-cream sales and drownings
rise and fall together, but ice cream doesn’t cause drowning: both are caused by a third thing,
**summer**. A third variable like this is called a **confounder**.

**Why.** Most data in data science are **observational**: we watch what happens, we don’t control
it. Only an experiment, where you change one thing on purpose and keep everything else the same,
can show cause directly. With observational data you have to think through the alternative
explanations yourself.

For Lund, our data show *that* the temperature measured there rose. They don’t show *why* on their
own. Before concluding “the climate warmed”, ask what else could explain it. For example:

- **The station changed.** The top of the data file lists the station’s positions and heights:
  they changed in 1974, 1992 and 1997. A move to a warmer or cooler spot shifts every later
  measurement.
- **The city grew around it.** Buildings and asphalt hold heat, so a city station can warm faster
  than the countryside (the *urban heat island*).

In this case the warming matches what stations all over the world show, so the climate explanation
is strong. But the habit matters more than the case: **for every conclusion, list what else could
explain it.**

## 8. Traps

- **Testing many things.** With $p < 0.05$ as the bar, about 1 in 20 tests on pure noise comes out
  “significant”. Test 20 things and report the one that worked, and you have reported noise.

  ![20 comparisons of random noise: one comes out below 0.05](/img/statistics/many-tests.svg)

- **Choosing after looking.** Picking the split year, the subgroup or the outliers to remove
  *after* seeing which choice gives the nicest result is the same trap in disguise. Decide before
  you look, or show that the result holds for other reasonable choices.
- **Small samples.** With few observations, intervals are wide and a single unusual value moves
  everything. Say how many observations a number rests on.
- **Outliers.** One extreme value can move a mean a lot. Plot the data, check whether an outlier
  is an error or real, and compare with the median.
- **Huge samples.** With millions of rows, almost every difference is “significant”. Then the
  question is only whether it is big enough to matter.

## 9. Writing it up

A good statistical sentence has three parts: **the estimate**, **its uncertainty**, and **what it
can’t tell you**. For example:

> The mean annual temperature in Lund was **0.82 °C higher** in 2011–2025 than in 1997–2010
> (**95% confidence interval 0.37 to 1.27 °C**; a difference this large would be very unlikely
> if both periods had the same climate, $p \approx 0.001$). Single years vary by about ±0.6 °C,
> so individual warm or cold years say little. The data come from one station that moved in
> 1997, so part of the change may reflect the station rather than the climate.

Use this shape in the **Analysis** and **Conclusions & limitations** sections of your reports.

## Further reading

- The **statistics part of Alm & Britton, *Stokastik***, which you already have from Probability
  Theory I: estimation, confidence intervals and hypothesis tests in full.
- [OpenIntro Statistics](https://www.openintro.org/book/os/) (free): chapters on inference for
  means, and on linear regression.
- [Seeing Theory](https://seeing-theory.brown.edu): interactive visualisations of these ideas.
