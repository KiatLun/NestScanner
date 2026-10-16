from huggingface_hub import HfApi


api = HfApi()


# =================================================
# Convert Hugging Face model to result
# =================================================

def modelToResult(
    model,
    discoverySource: str,
) -> dict:

    modelId = model.id

    return {
        "source": "huggingface",

        "title": modelId,

        "url": (
            f"https://huggingface.co/{modelId}"
        ),

        "description": None,

        "metadata": {

            "repositoryId": modelId,

            "organisation": (
                modelId.split("/")[0]
                if "/" in modelId
                else None
            ),

            "pipelineTag": model.pipeline_tag,

            "downloads": model.downloads,

            "likes": model.likes,

            "trendingScore": getattr(
                model,
                "trending_score",
                None,
            ),

            "createdAt": (
                model.created_at.isoformat()
                if getattr(
                    model,
                    "created_at",
                    None,
                )
                else None
            ),

            "lastModified": (
                model.last_modified.isoformat()
                if getattr(
                    model,
                    "last_modified",
                    None,
                )
                else None
            ),

            "tags": model.tags or [],

            # Keep track of which HF catalogue
            # source discovered this model.
            "discoverySources": [
                discoverySource
            ],
        },
    }


# =================================================
# Get new ASR models from Hugging Face
# =================================================

def getNewASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag=(
            "automatic-speech-recognition"
        ),
        limit=limit,
        sort="created_at",
        full=True,
    )

    return [
        modelToResult(
            model,
            "new",
        )
        for model in models
    ]


# =================================================
# Get recently modified ASR models
# =================================================

def getRecentlyModifiedASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag=(
            "automatic-speech-recognition"
        ),
        limit=limit,
        sort="last_modified",
        full=True,
    )

    return [
        modelToResult(
            model,
            "recently_modified",
        )
        for model in models
    ]


# =================================================
# Get most downloaded ASR models
# =================================================

def getPopularASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag=(
            "automatic-speech-recognition"
        ),
        limit=limit,
        sort="downloads",
        full=True,
    )

    return [
        modelToResult(
            model,
            "popular",
        )
        for model in models
    ]


# =================================================
# Get most liked ASR models
# =================================================

def getLikedASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag=(
            "automatic-speech-recognition"
        ),
        limit=limit,
        sort="likes",
        full=True,
    )

    return [
        modelToResult(
            model,
            "liked",
        )
        for model in models
    ]

# =================================================
# Get trending ASR models from Hugging Face
# =================================================

def getTrendingASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag=(
            "automatic-speech-recognition"
        ),
        limit=limit,
        sort="trending_score",
        full=True,
    )

    return [
        modelToResult(
            model,
            "trending",
        )
        for model in models
    ]


# =================================================
# Discover ASR models
# =================================================

def discoverASRModels(
    limitPerSource: int = 100,
) -> list[dict]:
    """
    Discover ASR models from multiple Hugging Face
    catalogue views.

    Sources:

    1. Newest
    2. Recently modified
    3. Most downloaded
    4. Most liked
    5. Trending
    """

    candidates = []

    # =================================================
    # NEWEST
    # =================================================

    candidates.extend(
        getNewASRModels(
            limitPerSource
        )
    )

    # =================================================
    # RECENTLY MODIFIED
    # =================================================

    candidates.extend(
        getRecentlyModifiedASRModels(
            limitPerSource
        )
    )

    # =================================================
    # MOST DOWNLOADED
    # =================================================

    candidates.extend(
        getPopularASRModels(
            limitPerSource
        )
    )

    # =================================================
    # MOST LIKED
    # =================================================

    candidates.extend(
        getLikedASRModels(
            limitPerSource
        )
    )

    # =================================================
    # TRENDING
    # =================================================

    candidates.extend(
        getTrendingASRModels(
            limitPerSource
        )
    )

    return candidates


# =================================================
# Deduplicate Hugging Face results
# =================================================

def deduplicateHFResults(
    results: list[dict],
) -> list[dict]:
    """
    Deduplicate models by repository ID.

    If a model appears in multiple catalogue views,
    preserve all discovery sources.
    """

    seen = {}

    unique = []

    for result in results:

        repositoryId = (
            result.get(
                "metadata",
                {},
            ).get(
                "repositoryId"
            )
        )

        if not repositoryId:
            continue

        # =================================================
        # FIRST OCCURRENCE
        # =================================================

        if repositoryId not in seen:

            metadata = result.setdefault(
                "metadata",
                {},
            )

            discoverySources = metadata.get(
                "discoverySources",
                [],
            )

            metadata[
                "discoverySources"
            ] = list(
                dict.fromkeys(
                    discoverySources
                )
            )

            seen[
                repositoryId
            ] = result

            unique.append(
                result
            )

            continue

        # =================================================
        # DUPLICATE
        # =================================================

        existing = seen[
            repositoryId
        ]

        existingMetadata = (
            existing.setdefault(
                "metadata",
                {},
            )
        )

        newMetadata = result.get(
            "metadata",
            {},
        )

        existingSources = (
            existingMetadata.get(
                "discoverySources",
                [],
            )
        )

        newSources = (
            newMetadata.get(
                "discoverySources",
                [],
            )
        )

        existingMetadata[
            "discoverySources"
        ] = list(
            dict.fromkeys(
                existingSources
                + newSources
            )
        )

    return unique


# =================================================
# Search Hugging Face by keyword
# =================================================

def searchHuggingFaceModels(
    query: str,
    limit: int = 20,
) -> list[dict]:

    models = api.list_models(
        search=query,
        limit=limit,
        full=True,
    )

    results = []

    for model in models:

        modelId = model.id

        results.append(
            {
                "source": "huggingface",

                "title": modelId,

                "url": (
                    f"https://huggingface.co/"
                    f"{modelId}"
                ),

                "description": None,

                "metadata": {

                    "repositoryId": modelId,

                    "organisation": (
                        modelId.split("/")[0]
                        if "/" in modelId
                        else None
                    ),

                    "pipelineTag": (
                        model.pipeline_tag
                    ),

                    "downloads": (
                        model.downloads
                    ),

                    "likes": (
                        model.likes
                    ),

                    "createdAt": (
                        model.created_at.isoformat()
                        if getattr(
                            model,
                            "created_at",
                            None,
                        )
                        else None
                    ),

                    "lastModified": (
                        model.last_modified.isoformat()
                        if model.last_modified
                        else None
                    ),

                    "tags": (
                        model.tags or []
                    ),
                },
            }
        )

    return results


# =================================================
# Filter ASR models
# =================================================

def filterASRModels(
    models: list[dict],
) -> list[dict]:
    """
    Keep Hugging Face models explicitly tagged
    for automatic speech recognition.
    """

    return [
        model
        for model in models
        if model.get(
            "metadata",
            {},
        ).get(
            "pipelineTag"
        )
        == "automatic-speech-recognition"
    ]