"""
Build the static site data from classified papers.
Generates both data.json (for GitHub Pages fetch) and embeds data into index.html
(for local file:// viewing).
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SITE_DIR = Path(__file__).parent.parent / "docs"
PAPERS_FILE = DATA_DIR / "papers.json"
SITE_DATA_FILE = SITE_DIR / "data.json"
HTML_FILE = SITE_DIR / "index.html"

from config import SUBTOPICS


def build():
    with open(PAPERS_FILE) as f:
        data = json.load(f)

    papers = data["papers"]

    filtered = []
    for p in papers:
        if p.get("relevant") is False:
            continue
        filtered.append({
            "id": p["id"],
            "doi": p.get("doi", ""),
            "title": p["title"],
            "authors": p.get("authors", [])[:5],
            "journal": p.get("journal", ""),
            "date": p.get("publication_date", ""),
            "cited": p.get("cited_by_count", 0),
            "oa": p.get("open_access", False),
            "topic": p.get("classified_topic") or (p.get("search_topics", [None])[0]),
            "topic2": p.get("secondary_topic"),
            "abstract": p.get("abstract", "")[:500],
        })

    filtered.sort(key=lambda x: x.get("date", ""), reverse=True)

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

    # Write standalone data.json (for GitHub Pages)
    with open(SITE_DATA_FILE, "w") as f:
        json.dump(output, f)

    # Embed data into HTML so it works with file:// protocol too
    html = HTML_FILE.read_text()
    data_json = json.dumps(output)
    embed_line = f"const EMBEDDED_DATA = {data_json};"

    # Match either the placeholder marker OR a previous embed
    marker = "/* __EMBEDDED_DATA__ */"
    if marker in html:
        html = html.replace(marker, embed_line)
    else:
        # Replace previous embedded data (starts with "const EMBEDDED_DATA = ")
        html = re.sub(
            r'const EMBEDDED_DATA = .+;',
            lambda m: embed_line,
            html,
            count=1,
        )

    HTML_FILE.write_text(html)
    print(f"Embedded data into index.html.")
    print(f"Built site data: {len(filtered)} papers across {len(topic_counts)} topics.")


if __name__ == "__main__":
    build()
