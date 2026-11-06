# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas"]
# ///
"""The reviews for week 6 (/lectures/week-6 and slides/week-6).

Run from the repository root:  uv run scripts/week6_data.py
Downloads the UCI "Recipe Reviews and User Feedback" dataset (CC BY 4.0) into a new temporary
folder, keeps reviews with a star rating, and draws 50 reviews for each of 1-5 stars with a fixed
seed. Writes public/data/week-6/recipe-reviews.csv. User names and ids are left out: we don't
need them, so we don't keep them.

Source: Ali, A., Matuszewski, S., & Czupyt, J. (2023). Recipe Reviews and User Feedback [Dataset].
UCI Machine Learning Repository. https://doi.org/10.24432/C5FG95
"""

import html
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/911/recipe+reviews+and+user+feedback+dataset.zip"
OUT = Path("public/data/week-6")
OUT.mkdir(parents=True, exist_ok=True)
PER_STAR = 50
SEED = 4008

with tempfile.TemporaryDirectory() as tmp:
    zpath = Path(tmp) / "reviews.zip"
    req = urllib.request.Request(URL, headers={"User-Agent": "mt4008-course-materials"})
    with urllib.request.urlopen(req) as r:
        zpath.write_bytes(r.read())
    with zipfile.ZipFile(zpath) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(name) as f:
            raw = pd.read_csv(f)

print("downloaded:", raw.shape)
print(raw["stars"].value_counts().sort_index().to_dict())

reviews = (
    raw.rename(columns={"comment_id": "review_id", "recipe_name": "recipe"})
    .loc[lambda d: d["stars"].between(1, 5) & d["text"].notna()]
    .assign(text=lambda d: d["text"].map(html.unescape).str.strip())   # &#39; -> '
    .loc[lambda d: d["text"].str.len() >= 20]                            # drop "Yum!"-only reviews
    .drop_duplicates("text")
    [["review_id", "recipe", "stars", "text"]]
)
print("with stars, at least 20 characters, unique text:", len(reviews))
print("share of 5 stars among them:", round((reviews["stars"] == 5).mean(), 3))

sample = (
    reviews.groupby("stars", group_keys=False)
    .sample(n=PER_STAR, random_state=SEED)
    .sample(frac=1, random_state=SEED)          # shuffle, so the stars are not in order
    .reset_index(drop=True)
)
sample.to_csv(OUT / "recipe-reviews.csv", index=False)
print("sample:", sample.shape, sample["stars"].value_counts().sort_index().to_dict())
print("text length, median:", sample["text"].str.len().median())
