"""
Build the static site data from classified papers.
Generates docs/data.json for GitHub Pages.
For local development, run: python3 -m http.server 8000 --directory docs
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SITE_DIR = Path(__file__).parent.parent / "docs"
PAPERS_FILE = DATA_DIR / "papers.json"
SITE_DATA_FILE = SITE_DIR / "data.json"

from config import SUBTOPICS


def build():
    with open(PAPERS_FILE) as f:
        data = json.load(f)

    papers = data["papers"]

    filtered = []
    for p in papers:
        if p.get("relevant") is False:
            continue
        topic = p.get("classified_topic")
        if not topic:
            continue
        filtered.append({
            "id": p["id"],
            "doi": p.get("doi", ""),
            "title": p["title"],
            "authors": p.get("authors", [])[:3],
            "journal": p.get("journal", ""),
            "date": p.get("publication_date", ""),
            "cited": p.get("cited_by_count", 0),
            "oa": p.get("open_access", False),
            "topic": topic,
            "topic2": p.get("secondary_topic"),
            "abstract": (p.get("abstract") or "")[:250],
        })

    filtered.sort(key=lambda x: x.get("date") or "", reverse=True)

    topic_counts = {}
    for p in filtered:
        t = p.get("topic")
        if t:
            topic_counts[t] = topic_counts.get(t, 0) + 1

    output = {
        "last_updated": data.get("last_updated", ""),
        "total": len(filtered),
        "topic_counts": topic_counts,
        "topics": {k: {"name": v["name"], "description": v["description"]} for k, v in SUBTOPICS.items()},
        "papers": filtered,
    }

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SITE_DATA_FILE, "w") as f:
        json.dump(output, f)

    size_mb = SITE_DATA_FILE.stat().st_size / 1024 / 1024
    print(f"Built site data: {len(filtered)} papers across {len(topic_counts)} topics ({size_mb:.1f} MB)")


if __name__ == "__main__":
    build()
