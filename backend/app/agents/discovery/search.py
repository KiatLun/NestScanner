from app.agents.discovery.config import (
    DiscoveryConfig,
)

from app.tools.huggingFace import (
    discoverASRModels,
    deduplicateHFResults,
)


def searchHuggingFace(
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Discover ASR models directly from Hugging Face.

    Hugging Face is the sole discovery source.

    Models are collected from multiple catalogue views:

    - newly created models
    - recently modified models
    - most downloaded models
    - trending models

    Results are then deduplicated using the Hugging Face
    repository ID.
    """

    if config.verbose:
        print(
            "\n=== HUGGING FACE ASR DISCOVERY ==="
        )

    try:
        results = discoverASRModels(
            limitPerSource=(
                config.huggingFaceResultsPerDiscoverySource
            )
        )

        if config.verbose:
            print(
                f"Raw Hugging Face results: "
                f"{len(results)}"
            )

        results = deduplicateHFResults(
            results
        )

        if config.verbose:
            print(
                f"Unique Hugging Face models: "
                f"{len(results)}"
            )

            print(
                "\nSample discovered models:"
            )

            for model in results[:10]:

                metadata = model.get(
                    "metadata",
                    {},
                )

                print(
                    metadata.get(
                        "repositoryId"
                    ),
                    "| downloads:",
                    metadata.get(
                        "downloads"
                    ),
                    "| likes:",
                    metadata.get(
                        "likes"
                    ),
                    "| created:",
                    metadata.get(
                        "createdAt"
                    ),
                    "| modified:",
                    metadata.get(
                        "lastModified"
                    ),
                )

        return results

    except Exception as error:

        print(
            "Hugging Face discovery failed."
        )

        print(error)

        return []


def gatherDiscoveryEvidence(
    objective: str,
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Gather Discovery candidates from Hugging Face.

    The objective is retained for compatibility with
    the existing Discovery Agent interface.

    Model discovery itself does not use keyword queries.
    Hugging Face's automatic-speech-recognition pipeline
    tag is used as the primary ASR criterion.
    """

    return searchHuggingFace(
        config
    )