from ddgs import DDGS


def webSearch(
    query: str,
    maxResults: int = 10,
) -> list[dict]:

    results = DDGS().text(
        query,
        max_results=maxResults,
    )

    normalized = []

    for result in results:
        normalized.append(
            {
                "source": "web",
                "title": (result.get("title") or "Untitled result"),
                "url": result.get("href"),
                "description": result.get("body"),
                "metadata": {
                    "s": query,
                },
            }
        )

    return normalized


def deduplicateResults(
    results: list[dict],
) -> list[dict]:

    seen_urls = set()
    unique = []

    for result in results:
        url = result.get("url")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique.append(result)

    return unique
