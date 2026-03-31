"""
Classify paper abstracts using Claude Haiku to determine relevance and subtopic.
Only classifies papers that haven't been classified yet (relevant == None).

Requires ANTHROPIC_API_KEY environment variable.
"""

import json
import os
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PAPERS_FILE = DATA_DIR / "papers.json"

# Import config for subtopics and prompt
from config import SUBTOPICS, CLASSIFICATION_PROMPT

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"
API_URL = "https://api.anthropic.com/v1/messages"

# Batch size for classification (process N papers per API call to save costs)
BATCH_SIZE = 20


def classify_single(title: str, abstract: str) -> dict:
    """Classify a single paper using Claude Haiku."""
    import urllib.request

    subtopic_list = "\n".join(
        f"- {k}: {v['name']} — {v['description']}" for k, v in SUBTOPICS.items()
    )
    prompt = CLASSIFICATION_PROMPT.format(
        subtopic_list=subtopic_list, title=title, abstract=abstract[:1500]
    )

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 150,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        text = result["content"][0]["text"]
        # Parse JSON from response
        # Handle case where model wraps in markdown code block
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except Exception as e:
        print(f"  Classification error: {e}")
        return {"relevant": None, "primary_topic": None, "secondary_topic": None, "confidence": 0.0}


def classify_batch(papers: list) -> list:
    """Classify a batch of papers using a single Haiku call."""
    import urllib.request

    subtopic_list = "\n".join(
        f"- {k}: {v['name']} — {v['description']}" for k, v in SUBTOPICS.items()
    )

    # Build batch prompt
    paper_entries = []
    for i, p in enumerate(papers):
        abstract = (p.get('abstract') or '')[:800]
        entry = f"[{i}] Title: {p['title']}"
        if abstract:
            entry += f"\nAbstract: {abstract}"
        paper_entries.append(entry)

    batch_prompt = f"""You are classifying psychology research papers about AI/LLMs.

For each paper, determine:
1. Is this paper actually about the PSYCHOLOGICAL aspects of AI (human reactions to, perceptions of, or behavioral effects of AI)? Not purely technical AI papers.
2. Which subtopic(s) does it best fit?

Subtopics:
{subtopic_list}

Respond as a JSON array with one object per paper, in order:
[{{"relevant": true/false, "primary_topic": "topic_key", "secondary_topic": "topic_key_or_null", "confidence": 0.0-1.0}}, ...]

Papers:

{chr(10).join(paper_entries)}"""

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 3000,
        "messages": [{"role": "user", "content": batch_prompt}],
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
        text = result["content"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except Exception as e:
        print(f"  Batch classification error: {e}")
        return [{"relevant": None, "primary_topic": None, "secondary_topic": None, "confidence": 0.0}] * len(papers)


def classify_all():
    """Classify all unclassified papers."""
    if not API_KEY:
        print("Error: ANTHROPIC_API_KEY not set. Skipping classification.")
        print("Papers will still appear on the site but without topic filtering.")
        return

    with open(PAPERS_FILE) as f:
        data = json.load(f)

    papers = data["papers"]
    unclassified = [p for p in papers if p.get("relevant") is None]
    print(f"Found {len(unclassified)} unclassified papers.")

    # Process in batches
    for i in range(0, len(unclassified), BATCH_SIZE):
        batch = unclassified[i : i + BATCH_SIZE]
        print(f"  Classifying batch {i // BATCH_SIZE + 1} ({len(batch)} papers)...")
        results = classify_batch(batch)

        for paper, classification in zip(batch, results):
            paper["relevant"] = classification.get("relevant")
            paper["classified_topic"] = classification.get("primary_topic")
            paper["secondary_topic"] = classification.get("secondary_topic")
            paper["confidence"] = classification.get("confidence")

        time.sleep(0.5)  # rate limit politeness

        # Save progress every 50 batches so we don't lose work on failure
        if (i // BATCH_SIZE + 1) % 50 == 0:
            with open(PAPERS_FILE, "w") as f:
                json.dump(data, f, indent=2)
            classified_so_far = sum(1 for p in papers if p.get("relevant") is not None)
            print(f"  [checkpoint: {classified_so_far}/{len(papers)} classified]")

    # Final save
    with open(PAPERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

    relevant_count = sum(1 for p in papers if p.get("relevant") is True)
    print(f"Done. {relevant_count} papers marked relevant out of {len(papers)} total.")


if __name__ == "__main__":
    classify_all()
