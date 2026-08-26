from datetime import (
    date,
    datetime,
    timedelta,
)

from zoneinfo import ZoneInfo

from app.agents.discovery.searchPlanner import (
    buildDiscoveryQueries,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
    filterASRModels,
)

from app.tools.github import (
    searchGithubRepositories,
)

from app.tools.arvixSearch import (
    searchArxivPapers,
)


def getDiscoveryDateWindow() -> tuple[date, date]:
    """
    Return a recent-source search window.

    This is used only to guide Discovery searches.

    It is NOT treated as verified model release-date
    information.
    """

    currentDate = datetime.now(
        ZoneInfo("Asia/Singapore")
    ).date()

    cutoffDate = (
        currentDate
        - timedelta(days=30)
    )

    return cutoffDate, currentDate


def searchWeb(
    queries: list[str],
) -> list[dict]:
    """
    Search the general web.
    """

    results = []

    for query in queries:

        print(
            f"\nSearching web: {query}"
        )

        try:
            queryResults = webSearch(
                query,
                maxResults=5,
            )

            print(
                f"Found {len(queryResults)} "
                "web results."
            )

            results.extend(
                queryResults
            )

        except Exception as error:
            print(
                f"Web search failed: {query}"
            )

            print(error)

    return results


def searchHuggingFace(
    queries: list[str],
) -> list[dict]:
    """
    Search Hugging Face and retain ASR models.
    """

    results = []

    for query in queries:

        print(
            f"\nSearching Hugging Face: {query}"
        )

        try:
            queryResults = searchHuggingFaceModels(
                query,
                limit=20,
            )

            print(
                f"Found {len(queryResults)} "
                "Hugging Face results "
                "before filtering."
            )

            queryResults = filterASRModels(
                queryResults
            )

            print(
                f"Found {len(queryResults)} "
                "ASR models after filtering."
            )

            results.extend(
                queryResults
            )

        except Exception as error:
            print(
                f"Hugging Face search failed: {query}"
            )

            print(error)

    return results


def searchGithub(
    queries: list[str],
) -> list[dict]:
    """
    Search GitHub repositories.
    """

    results = []

    for query in queries:

        print(
            f"\nSearching GitHub: {query}"
        )

        try:
            queryResults = (
                searchGithubRepositories(
                    query,
                    limit=10,
                )
            )

            print(
                f"Found {len(queryResults)} "
                "GitHub repositories."
            )

            results.extend(
                queryResults
            )

        except Exception as error:
            print(
                f"GitHub search failed: {query}"
            )

            print(error)

    return results


def searchArxiv(
    queries: list[str],
) -> list[dict]:
    """
    Search arXiv papers.
    """

    results = []

    for query in queries:

        print(
            f"\nSearching arXiv: {query}"
        )

        try:
            queryResults = searchArxivPapers(
                query,
                limit=10,
            )

            print(
                f"Found {len(queryResults)} "
                "arXiv papers."
            )

            results.extend(
                queryResults
            )

        except Exception as error:
            print(
                f"arXiv search failed: {query}"
            )

            print(error)

    return results


def gatherDiscoveryEvidence(
    objective: str,
) -> list[dict]:
    """
    Build a search plan and gather evidence from
    web, Hugging Face, GitHub, and arXiv.
    """

    cutoffDate, currentDate = (
        getDiscoveryDateWindow()
    )

    searchObjective = f"""
{objective}

Current date: {currentDate}

Recent discovery window:

{cutoffDate} to {currentDate}

Find likely automatic speech recognition models or
model families appearing in recent sources.

This date range is a Discovery search heuristic only.

Do NOT attempt to prove that the model itself was
released during this period.

The Research Agent will later verify the true
release date and recency.
"""

    searchPlan = buildDiscoveryQueries(
        searchObjective
    )

    print(
        "\n=== SEARCH PLAN ==="
    )

    print(
        "\nWeb queries:"
    )

    for query in searchPlan.webQueries:
        print(f"- {query}")

    print(
        "\nHugging Face queries:"
    )

    for query in searchPlan.huggingFaceQueries:
        print(f"- {query}")

    print(
        "\nGitHub queries:"
    )

    for query in searchPlan.githubQueries:
        print(f"- {query}")

    print(
        "\narXiv queries:"
    )

    for query in searchPlan.arxivQueries:
        print(f"- {query}")

    allResults = []

    print(
        "\n=== WEB SEARCH ==="
    )

    allResults.extend(
        searchWeb(
            searchPlan.webQueries
        )
    )

    print(
        "\n=== HUGGING FACE SEARCH ==="
    )

    allResults.extend(
        searchHuggingFace(
            searchPlan.huggingFaceQueries
        )
    )

    print(
        "\n=== GITHUB SEARCH ==="
    )

    allResults.extend(
        searchGithub(
            searchPlan.githubQueries
        )
    )

    print(
        "\n=== ARXIV SEARCH ==="
    )

    allResults.extend(
        searchArxiv(
            searchPlan.arxivQueries
        )
    )

    rawResultCount = len(
        allResults
    )

    allResults = deduplicateResults(
        allResults
    )

    print(
        f"\nRaw discovery results: "
        f"{rawResultCount}"
    )

    print(
        f"Unique discovery results: "
        f"{len(allResults)}"
    )

    return allResults