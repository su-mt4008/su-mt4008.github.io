# /// script
# requires-python = ">=3.12"
# dependencies = ["ollama", "pandas"]
# ///
"""Run a local language model over the week-6 reviews, once, and save what it said.

Needs Ollama running on this computer (https://ollama.com) and the model pulled:
    ollama pull llama3.2:3b

Run from the repository root:
    uv run scripts/week6_extract.py                       # the labels the page uses
    uv run scripts/week6_extract.py --out public/data/week-6/variants/rerun.csv
    uv run scripts/week6_extract.py --temperature 1 --out public/data/week-6/variants/temperature-1.csv
    uv run scripts/week6_extract.py --model llama3.2:1b --out public/data/week-6/variants/llama3.2-1b.csv
    uv run scripts/week6_extract.py --prompt b --out public/data/week-6/variants/prompt-b.csv

Each run writes a CSV with one row per review, and a .json file next to it that records the
model, its digest, the Ollama version, the options, the prompt and the schema: everything
someone needs to rerun it. The page and its figures only read these saved files.
"""

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import ollama
import pandas as pd

DATA = Path("public/data/week-6/recipe-reviews.csv")
HOST = "http://localhost:11434"

# The table we want: three fields, each with a fixed set of allowed values.
SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "mixed", "negative"]},
        "made_it": {"type": "boolean"},
        "changed_recipe": {"type": "boolean"},
    },
    "required": ["sentiment", "made_it", "changed_recipe"],
}

PROMPTS = {
    # The prompt the page uses.
    "a": """You read reviews of recipes and fill in a form. Answer only from the review.

sentiment: what the reviewer thinks of the recipe.
  "positive" if they mainly like it, "negative" if they mainly dislike it,
  "mixed" if they like some things and dislike others, or are lukewarm.
made_it: true if the reviewer says or clearly implies that they cooked the recipe, false otherwise.
changed_recipe: true if the reviewer says they changed ingredients, amounts or steps, false otherwise.

Reply with JSON only: {"sentiment": ..., "made_it": ..., "changed_recipe": ...}""",
    # The same task, worded differently: is the result sensitive to the wording?
    "b": """Classify this recipe review.

- sentiment: positive, mixed or negative
- made_it: did the reviewer cook it? (true/false)
- changed_recipe: did the reviewer change the recipe? (true/false)

Return JSON.""",
}


def get_json(path):
    with urllib.request.urlopen(HOST + path) as r:
        return json.load(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="llama3.2:3b")
    p.add_argument("--temperature", type=float, default=0)
    p.add_argument("--seed", type=int, default=4008)
    p.add_argument("--prompt", default="a", choices=PROMPTS)
    p.add_argument("--out", default="public/data/week-6/llm-labels.csv")
    args = p.parse_args()

    reviews = pd.read_csv(DATA)
    options = {"temperature": args.temperature, "seed": args.seed}
    rows, start = [], time.time()
    for i, r in reviews.iterrows():
        response = ollama.chat(
            model=args.model,
            messages=[
                {"role": "system", "content": PROMPTS[args.prompt]},
                {"role": "user", "content": r["text"]},
            ],
            format=SCHEMA,
            options=options,
        )
        answer = json.loads(response.message.content)
        rows.append({"review_id": r["review_id"], **answer})
        if i % 50 == 0:
            print(i, answer)
    seconds = time.time() - start

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)

    tags = {m["name"]: m for m in get_json("/api/tags")["models"]}
    meta = {
        "model": args.model,
        "model_digest": tags[args.model]["digest"],
        "ollama_version": get_json("/api/version")["version"],
        "options": options,
        "prompt_name": args.prompt,
        "prompt": PROMPTS[args.prompt],
        "schema": SCHEMA,
        "input": str(DATA),
        "n": len(rows),
        "seconds": round(seconds),
        "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"wrote {out}: {len(rows)} rows in {seconds:.0f} s")


if __name__ == "__main__":
    main()
