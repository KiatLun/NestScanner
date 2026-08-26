from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
)

from app.tools.github import (
    searchGithubRepositories,
)

from app.tools.arvixSearch import (
    searchArxivPapers,
)


def gatherDeeperEvidence(
    currentModel: dict,
) -> list[dict]:
    """
    Gather model-specific evidence for deeper research.

    Discovery finds the candidate.
    Research now searches specifically around that model.
    """

    modelName = currentModel.get(
        "name",
        "",
    )

    organisation = currentModel.get(
        "organisation",
        "",
    )

    sourceUrl = currentModel.get("sourceUrl") or currentModel.get("sourceUrl")

    evidence = []

    # =================================================
    # 1. KEEP DISCOVERY SOURCE
    # =================================================

    if sourceUrl:
        evidence.append(
            {
                "source": "discovery",
                "title": modelName,
                "url": sourceUrl,
                "description": ("Source passed from Discovery."),
                "metadata": {},
            }
        )

    # =================================================
    # 2. HUGGING FACE
    # =================================================

    huggingFaceQueries = [
        modelName,
    ]

    if organisation:
        huggingFaceQueries.append(f"{organisation} {modelName}")

    for query in huggingFaceQueries:

        try:
            results = searchHuggingFaceModels(
                query,
                limit=10,
            )

            evidence.extend(results)

        except Exception as error:

            print(f"Hugging Face deeper search " f"failed for: {query}")

            print(error)

    # =================================================
    # 3. GITHUB
    # =================================================

    githubQueries = [
        modelName,
        f"{modelName} inference",
        f"{modelName} implementation",
    ]

    if organisation:
        githubQueries.append(f"{organisation} {modelName}")

    for query in githubQueries:

        try:
            results = searchGithubRepositories(
                query,
                limit=10,
            )

            evidence.extend(results)

        except Exception as error:

            print(f"GitHub deeper search " f"failed for: {query}")

            print(error)

    # =================================================
    # 4. ARXIV
    # =================================================

    try:
        arxivResults = searchArxivPapers(
            modelName,
            limit=5,
        )

        evidence.extend(arxivResults)

    except Exception as error:

        print(f"arXiv deeper search " f"failed for: {modelName}")

        print(error)

    # =================================================
    # 5. GENERAL WEB
    # =================================================

    webQueries = [
        f"{modelName} official",
        f"{modelName} Hugging Face",
        f"{modelName} GitHub",
        f"{modelName} paper",
        f"{modelName} inference",
        f"{modelName} local inference",
        f"{modelName} model weights",
        f"{modelName} benchmark WER",
        f"{modelName} fine tuning",
    ]

    if organisation:
        webQueries.append(f"{organisation} {modelName}")

    for query in webQueries:

        try:
            results = webSearch(
                query,
                maxResults=5,
            )

            evidence.extend(results)

        except Exception as error:

            print(f"Web deeper search " f"failed for: {query}")

            print(error)

    # =================================================
    # 6. DEDUPLICATE
    # =================================================

    return deduplicateResults(evidence)
