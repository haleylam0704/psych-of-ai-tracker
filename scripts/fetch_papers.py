"""
Fetch papers from OpenAlex API.
No API key needed — just a polite email for faster rate limits.
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from config import OPENALEX_EMAIL, SUBTOPICS, MAX_RESULTS_PER_TOPIC

DATA_DIR = Path(__file__).parent.parent / "data"
PAPERS_FILE = DATA_DIR / "papers.json"

BASE_URL = "https://api.openalex.org/works"


def load_existing_papers() -> dict:
    """Load existing papers database. Keys are OpenAlex IDs for dedup."""
    if PAPERS_FILE.exists():
        with open(PAPERS_FILE) as f:
            data = json.load(f)
        return {p["id"]: p for p in data.get("papers", [])}
    return {}


def fetch_query(query: str, per_page: int = 50, max_pages: int = 4) -> list:
    """Fetch papers for a single search query from OpenAlex."""
    papers = []
    for page in range(1, max_pages + 1):
        params = urllib.parse.urlencode({
            "search": query,
            "filter": "type:article,language:en",
            "sort": "publication_date:desc",
            "per_page": per_page,
            "page": page,
            "mailto": OPENALEX_EMAIL,
        })
        url = f"{BASE_URL}?{params}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            results = data.get("results", [])
            if not results:
                break
            papers.extend(results)
            time.sleep(0.15)  # polite rate limiting
        except Exception as e:
            print(f"  Error fetching page {page}: {e}")
            break
    return papers


def parse_paper(raw: dict, search_topic: str):
    """Extract relevant fields from an OpenAlex work object."""
    openalex_id = raw.get("id", "")
    if not openalex_id:
        return None

    # Get abstract from inverted index
    abstract = ""
    inv_index = raw.get("abstract_inverted_index")
    if inv_index:
        # Reconstruct abstract from inverted index
        word_positions = []
        for word, positions in inv_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join(w for _, w in word_positions)

    title = raw.get("title", "")
    if not title:
        return None

    # Authors
    authors = []
    for authorship in raw.get("authorships", [])[:10]:
        author = authorship.get("author", {})
        name = author.get("display_name", "")
        if name:
            authors.append(name)

    # Journal
    source = raw.get("primary_location", {}) or {}
    source_obj = source.get("source", {}) or {}
    journal = source_obj.get("display_name", "")

    return {
        "id": openalex_id,
        "doi": raw.get("doi", ""),
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "journal": journal,
        "publication_date": raw.get("publication_date", ""),
        "cited_by_count": raw.get("cited_by_count", 0),
        "open_access": raw.get("open_access", {}).get("is_oa", False),
        "search_topics": [search_topic],
        "classified_topic": None,  # filled by classify step
        "secondary_topic": None,
        "relevant": None,  # filled by classify step
        "confidence": None,
    }


def fetch_all():
    """Fetch papers for all subtopics and merge with existing database."""
    existing = load_existing_papers()
    new_count = 0

    for topic_key, topic_info in SUBTOPICS.items():
        print(f"\nFetching: {topic_info['name']}")
        for query in topic_info["queries"]:
            print(f"  Query: {query}")
            raw_papers = fetch_query(query, per_page=50, max_pages=MAX_RESULTS_PER_TOPIC // 50)
            for raw in raw_papers:
                parsed = parse_paper(raw, topic_key)
                if not parsed:
                    continue
                pid = parsed["id"]
                if pid in existing:
                    # Dedup: just add the new search topic
                    if topic_key not in existing[pid]["search_topics"]:
                        existing[pid]["search_topics"].append(topic_key)
                    # Update citation count (may have changed)
                    existing[pid]["cited_by_count"] = parsed["cited_by_count"]
                else:
                    existing[pid] = parsed
                    new_count += 1

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_papers": len(existing),
        "papers": list(existing.values()),
    }
    with open(PAPERS_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. {new_count} new papers added. {len(existing)} total.")


if __name__ == "__main__":
    fetch_all()
