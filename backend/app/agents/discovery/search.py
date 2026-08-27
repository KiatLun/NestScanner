from datetime import (
    date,
    datetime,
    timedelta,
)

from zoneinfo import ZoneInfo

from app.agents.discovery.config import (
    DiscoveryConfig,
)

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
    searchGitHubRepositories,
)

from app.tools.arvixSearch import (
    searchArxivPapers,
)


def getDiscoveryDateWindow(
    config: DiscoveryConfig,
) -> tuple[date, date]:
    """
    Return a recent-source search window.

    This is used only to guide Discovery searches.

    It is NOT treated as verified model release-date
    information.
    """

    currentDate = datetime.now(ZoneInfo("Asia/Singapore")).date()

    cutoffDate = currentDate - timedelta(days=config.discoveryWindowDays)

    return cutoffDate, currentDate


def searchWeb(
    queries: list[str],
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Search the general web.
    """
    results = []

    for query in queries:

        if config.verbose:
            print(f"\nSearching web: {query}")

        try:
            queryResults = webSearch(
                query,
                maxResults=config.webResultsPerQuery,
            )

            if config.verbose:
                print(f"Found {len(queryResults)} " "web results.")

            results.extend(queryResults)

        except Exception as error:
            print(f"Web search failed: {query}")

            print(error)

    return results


def searchHuggingFace(
    queries: list[str],
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Search Hugging Face and retain ASR models.
    """

    results = []

    for query in queries:

        if config.verbose:
            print(f"\nSearching Hugging Face: " f"{query}")

        try:
            queryResults = searchHuggingFaceModels(
                query,
                limit=(config.huggingFaceResultsPerQuery),
            )

            if config.verbose:
                print(
                    f"Found {len(queryResults)} "
                    "Hugging Face results "
                    "before filtering."
                )

            queryResults = filterASRModels(queryResults)

            if config.verbose:
                print(f"Found {len(queryResults)} " "ASR models after filtering.")

            results.extend(queryResults)

        except Exception as error:
            print(f"Hugging Face search failed: " f"{query}")

            print(error)

    return results


def searchGithub(
    queries: list[str],
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Search GitHub repositories.
    """

    results = []

    for query in queries:

        if config.verbose:
            print(f"\nSearching GitHub: {query}")

        try:
            queryResults = searchGitHubRepositories(
                query,
                limit=config.githubResultsPerQuery,
            )

            if config.verbose:
                print(f"Found {len(queryResults)} " "GitHub repositories.")

            results.extend(queryResults)

        except Exception as error:
            print(f"GitHub search failed: {query}")

            print(error)

    return results


def searchArxiv(
    queries: list[str],
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Search arXiv papers.
    """

    results = []

    for query in queries:

        if config.verbose:
            print(f"\nSearching arXiv: {query}")

        try:
            queryResults = searchArxivPapers(
                query,
                limit=config.arxivResultsPerQuery,
            )

            if config.verbose:
                print(f"Found {len(queryResults)} " "arXiv papers.")

            results.extend(queryResults)

        except Exception as error:
            print(f"arXiv search failed: {query}")

            print(error)

    return results


def gatherDiscoveryEvidence(
    objective: str,
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Build a search plan and gather evidence from
    web, Hugging Face, GitHub, and arXiv.
    """

    cutoffDate, currentDate = getDiscoveryDateWindow(config)

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
        searchObjective,
        config,
    )
    if config.verbose:

        print("\n=== SEARCH PLAN ===")

        print("\nWeb queries:")

        for query in searchPlan.webQueries:
            print(f"- {query}")

        print("\nHugging Face queries:")

        for query in searchPlan.huggingFaceQueries:
            print(f"- {query}")

        print("\nGitHub queries:")

        for query in searchPlan.githubQueries:
            print(f"- {query}")

        print("\narXiv queries:")

        for query in searchPlan.arxivQueries:
            print(f"- {query}")

    allResults = []

    if config.enableWebSearch:

        if config.verbose:
            print("\n=== WEB SEARCH ===")

        allResults.extend(
            searchWeb(
                searchPlan.webQueries,
                config,
            )
        )

    if config.enableHuggingFaceSearch:

        if config.verbose:
            print("\n=== HUGGING FACE SEARCH ===")

        allResults.extend(
            searchHuggingFace(
                searchPlan.huggingFaceQueries,
                config,
            )
        )

    if config.enableGithubSearch:

        if config.verbose:
            print("\n=== GITHUB SEARCH ===")

        allResults.extend(
            searchGithub(
                searchPlan.githubQueries,
                config,
            )
        )

    if config.enableArxivSearch:

        if config.verbose:
            print("\n=== ARXIV SEARCH ===")

        allResults.extend(
            searchArxiv(
                searchPlan.arxivQueries,
                config,
            )
        )

    rawResultCount = len(allResults)

    allResults = deduplicateResults(allResults)

    if config.verbose:
        print(f"\nRaw discovery results: " f"{rawResultCount}")

        print(f"Unique discovery results: " f"{len(allResults)}")

    return allResults
