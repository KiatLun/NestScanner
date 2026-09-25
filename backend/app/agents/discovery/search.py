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
    discoverASRModels,
    deduplicateHFResults,
)

from app.tools.github import (
    searchGitHubRepositories,
)

from app.tools.arvixSearch import (
    searchArxivPapers,
)



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
    Discover ASR models from Hugging Face using
    multiple catalogue views:

    - newly created models
    - recently modified models
    - most downloaded models
    - trending models
    """

    results = []

    # =================================================
    # PRIMARY: DIRECT ASR CATEGORY SEARCH
    # =================================================

    if config.verbose:
        print(
            "\nSearching Hugging Face "
            "ASR discovery sources..."
        )

    try:
        categoryResults = discoverASRModels(
            limitPerSource=config.huggingFaceResultsPerDiscoverySource,
        )

        if config.verbose:
            print(
                f"Found {len(categoryResults)} "
                "ASR category models."
            )
            for model in categoryResults[:5]:
                print(
                    model["metadata"]["repositoryId"]
                )

        results.extend(categoryResults)

    except Exception as error:
        print(
            "Hugging Face ASR category search failed."
        )

        print(error)

    # =================================================
    # SECONDARY: KEYWORD SEARCH
    # =================================================

    for query in queries:

        if config.verbose:
            print(
                f"\nSearching Hugging Face: {query}"
            )

        try:
            queryResults = searchHuggingFaceModels(
                query,
                limit=config.huggingFaceResultsPerQuery,
            )

            if config.verbose:
                print(
                    f"Found {len(queryResults)} "
                    "Hugging Face results "
                    "before filtering."
                )

            queryResults = filterASRModels(
                queryResults
            )

            if config.verbose:
                print(
                    f"Found {len(queryResults)} "
                    "ASR models after filtering."
                )

            results.extend(queryResults)

        except Exception as error:
            print(
                f"Hugging Face search failed: {query}"
            )

            print(error)

    results = deduplicateHFResults(results)
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

    searchObjective = f"""
    {objective}

    Find identifiable automatic speech recognition models.

    Hugging Face should be treated as the primary discovery
    source.

    Only prioritize models with identifiable Hugging Face repository IDs.

    Hugging Face repository IDs should be treated as the unique identity of a model.

    Focus on specific published models or checkpoints.

    Different parameter-size variants must be treated as
    different models.

    For example:

    Qwen3-ASR-0.6B

    and:

    Qwen3-ASR-1.7B

    are separate models.

    Do not collapse distinct checkpoints into a model family.
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

    if config.enableHuggingFaceSearch:

        if config.verbose:
            print("\n=== HUGGING FACE SEARCH ===")

        allResults.extend(
            searchHuggingFace(
                searchPlan.huggingFaceQueries,
                config,
            )
        )
    if config.enableWebSearch:

        if config.verbose:
            print("\n=== WEB SEARCH ===")

        allResults.extend(
            searchWeb(
                searchPlan.webQueries,
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
