# Example: penguin body mass
MT4008

<!--
A worked example of a report: what each of the seven sections is for.
Your assignments go in hw1/ ... hw5/; leave this folder as it is.
The same example in Python is in example/python/.
-->

## Question

*What do you want to find out, and why does it matter? Make it a
question the data can answer.*

Do the three penguin species at Palmer Station differ in body mass?

## Data

*Where does the data come from, how was it collected, and what can it
not tell you?*

``` r
# Relative path: works on any computer that has this repository.
penguins <- read_csv("data/raw/penguins.csv", show_col_types = FALSE)
dim(penguins)
```

    [1] 344   8

Measurements of 344 adult penguins on three islands near Palmer Station,
Antarctica, 2007–2009. Only these islands and years are covered, so the
results say nothing about penguins elsewhere.

## Cleaning

*What did you change, and why? Every decision is in code, never by
hand.*

``` r
sum(is.na(penguins$body_mass_g))
```

    [1] 2

``` r
clean <- penguins |> filter(!is.na(body_mass_g))
```

Two penguins have no body mass recorded; they are left out.

## Exploration

*Look at the data before drawing conclusions: distributions,
relationships, surprises.*

``` r
ggplot(clean, aes(species, body_mass_g)) +
  geom_boxplot() +
  labs(x = NULL, y = "Body mass (g)")
```

![Body mass by
species.](report_files/figure-commonmark/unnamed-chunk-4-1.png)

## Analysis

*Answer the question with a method that fits it, and check that the
answer holds up.*

``` r
clean |>
  group_by(species) |>
  summarise(n = n(), mean = round(mean(body_mass_g), 1), sd = round(sd(body_mass_g), 1)) |>
  knitr::kable()
```

| species   |   n |   mean |    sd |
|:----------|----:|-------:|------:|
| Adelie    | 151 | 3700.7 | 458.6 |
| Chinstrap |  68 | 3733.1 | 384.3 |
| Gentoo    | 123 | 5076.0 | 504.1 |

## Conclusions & limitations

*What does the evidence support, how sure are you, and what could
explain it otherwise?*

Gentoo penguins are on average about 1.35 kg heavier than the other two
species, which are similar to each other. These are averages from three
islands and three years; we have not tested whether the difference
between Adelie and Chinstrap is larger than chance.

## How to reproduce

*Exactly what someone needs to do to get the same result.*

``` bash
Rscript -e 'renv::restore()'
quarto render example/r/report.qmd
```
