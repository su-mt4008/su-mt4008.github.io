# Your report title
Your name

<!--
This is your report. Keep the seven sections below, in this order.
The example (penguins) shows the idea; replace it with your own analysis.
Render it with:   uv run quarto render report.qmd
That writes report.md, which is what your reviewers read on GitHub. Commit both.
-->

## Question

*What do you want to find out, and why does it matter? Make it a
question the data can answer.*

Do the three penguin species at Palmer Station differ in body mass?

## Data

*Where does the data come from, how was it collected, and what can it
not tell you?*

``` python
# Relative path: works on any computer that has this repository.
penguins = pd.read_csv("data/raw/penguins.csv")
penguins.shape
```

    (344, 8)

Measurements of 344 adult penguins on three islands near Palmer Station,
Antarctica, 2007–2009. Only these islands and years are covered, so the
results say nothing about penguins elsewhere.

## Cleaning

*What did you change, and why? Every decision is in code, never by
hand.*

``` python
missing = penguins["body_mass_g"].isna().sum()
clean = penguins.dropna(subset=["body_mass_g"])
missing
```

    np.int64(2)

Two penguins have no body mass recorded; they are left out.

## Exploration

*Look at the data before drawing conclusions: distributions,
relationships, surprises.*

``` python
fig, ax = plt.subplots(figsize=(6, 3.5))
species = sorted(clean["species"].unique())
ax.boxplot([clean.loc[clean["species"] == s, "body_mass_g"] for s in species])
ax.set_xticks(range(1, len(species) + 1), species)
ax.set_ylabel("Body mass (g)")
plt.show()
```

![Body mass by
species.](report_files/figure-commonmark/cell-5-output-1.png)

## Analysis

*Answer the question with a method that fits it, and check that the
answer holds up.*

``` python
# Markdown(...) shows a table as a real table on GitHub.
Markdown(summarise_by(clean, "species", "body_mass_g").to_markdown(index=False))
```

| species   |   n |   mean |    sd |
|:----------|----:|-------:|------:|
| Adelie    | 151 | 3700.7 | 458.6 |
| Chinstrap |  68 | 3733.1 | 384.3 |
| Gentoo    | 123 |   5076 | 504.1 |

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
uv sync
uv run quarto render report.qmd
```
