"""
Fetch papers from OpenAlex API using topic-based filtering.

Strategy: fetch papers at the intersection of relevant OpenAlex topics
and psychology concepts. This avoids keyword overfitting and catches
papers regardless of exact terminology.

No API key needed — just a polite email for faster rate limits.
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from config import (
    OPENALEX_EMAIL,
    OPENALEX_TOPIC_IDS,
    OPENALEX_PSYCH_CONCEPT_IDS,
    PUBLICATION_DATE_FROM,
    SAFETY_NET_QUERIES,
)

DATA_DIR = Path(__file__).parent.parent / "data"
PAPERS_FILE = DATA_DIR / "papers.json"

BASE_URL = "https://api.openalex.org/works"
PER_PAGE = 200  # OpenAlex max per page


def load_existing_papers():
    """Load existing papers database. Keys are OpenAlex IDs for dedup."""
    if PAPERS_FILE.exists():
        with open(PAPERS_FILE) as f:
            data = json.load(f)
        return {p["id"]: p for p in data.get("papers", [])}
    return {}


def fetch_page(url):
    """Fetch a single page with retry on rate limit."""
    req = urllib.request.Request(url)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = 2 ** (attempt + 1)
                print(f" [rate limited, waiting {wait}s]", end="", flush=True)
                time.sleep(wait)
            else:
                raise
    return None


def fetch_with_filter(filter_str, max_results=None, label=""):
    """Fetch all papers matching a filter string, using cursor pagination."""
    papers = []
    cursor = "*"
    page_num = 0

    while True:
        params = urllib.parse.urlencode({
            "filter": filter_str,
            "sort": "cited_by_count:desc",
            "per_page": PER_PAGE,
            "cursor": cursor,
            "mailto": OPENALEX_EMAIL,
        })
        url = f"{BASE_URL}?{params}"
        try:
            data = fetch_page(url)
            if not data:
                break
            results = data.get("results", [])
            if not results:
                break

            papers.extend(results)
            page_num += 1
            total = data.get("meta", {}).get("count", "?")

            if page_num % 10 == 0 or page_num == 1:
                print(f"  {label} page {page_num}: {len(papers)}/{total} fetched", flush=True)

            if max_results and len(papers) >= max_results:
                papers = papers[:max_results]
                break

            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error on page {page_num + 1}: {e}")
            break

    return papers


def parse_paper(raw):
    """Extract relevant fields from an OpenAlex work object."""
    openalex_id = raw.get("id", "")
    title = raw.get("title", "")
    if not openalex_id or not title:
        return None

    # Get abstract from inverted index
    abstract = ""
    inv_index = raw.get("abstract_inverted_index")
    if inv_index:
        word_positions = []
        for word, positions in inv_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join(w for _, w in word_positions)

    authors = []
    for authorship in raw.get("authorships", [])[:10]:
        author = authorship.get("author", {})
        name = author.get("display_name", "")
        if name:
            authors.append(name)

    source = raw.get("primary_location", {}) or {}
    source_obj = source.get("source", {}) or {}
    journal = source_obj.get("display_name", "")

    # Extract OpenAlex topic info for classification
    primary_topic = raw.get("primary_topic", {}) or {}
    topic_id = primary_topic.get("id", "")
    topic_name = primary_topic.get("display_name", "")

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
        "openalex_topic_id": topic_id,
        "openalex_topic_name": topic_name,
        "classified_topic": None,
        "secondary_topic": None,
        "relevant": None,
        "confidence": None,
    }


def fetch_all():
    """Fetch papers using topic+concept filtering, plus safety net queries."""
    existing = load_existing_papers()
    new_count = 0

    # --- Main fetch: topic IDs + psychology concept ---
    topic_filter = "|".join(OPENALEX_TOPIC_IDS)
    concept_filter = "|".join(OPENALEX_PSYCH_CONCEPT_IDS)
    main_filter = (
        f"primary_topic.id:{topic_filter},"
        f"concepts.id:{concept_filter},"
        f"from_publication_date:{PUBLICATION_DATE_FROM},"
        f"type:article,"
        f"language:en"
    )

    print("=== Fetching by topic + psychology concept ===")
    raw_papers = fetch_with_filter(main_filter, max_results=40000, label="topics+psych")
    print(f"  Total fetched: {len(raw_papers)}")

    for raw in raw_papers:
        parsed = parse_paper(raw)
        if not parsed:
            continue
        pid = parsed["id"]
        if pid not in existing:
            existing[pid] = parsed
            new_count += 1
        else:
            # Update citation count
            existing[pid]["cited_by_count"] = max(
                existing[pid]["cited_by_count"], parsed["cited_by_count"]
            )

    # --- Safety net: keyword queries for papers that fall through topic cracks ---
    print("\n=== Safety net keyword queries ===")
    for query in SAFETY_NET_QUERIES:
        print(f"  [{query}]", end="", flush=True)
        filter_str = (
            f"title_and_abstract.search:{query},"
            f"from_publication_date:{PUBLICATION_DATE_FROM},"
            f"type:article,"
            f"language:en"
        )
        raw_papers = fetch_with_filter(filter_str, max_results=500, label=query)
        added = 0
        for raw in raw_papers:
            parsed = parse_paper(raw)
            if not parsed:
                continue
            pid = parsed["id"]
            if pid not in existing:
                existing[pid] = parsed
                added += 1
                new_count += 1
        print(f" → {added} new")

    # Save (classification is handled separately by classify_papers.py)
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
