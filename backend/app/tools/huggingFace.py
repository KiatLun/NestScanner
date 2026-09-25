from huggingface_hub import HfApi

api = HfApi()


def modelToResult(model) -> dict:
    modelId = model.id

    return {
        "source": "huggingface",
        "title": modelId,
        "url": f"https://huggingface.co/{modelId}",
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
                if getattr(model, "created_at", None)
                else None
            ),
            "lastModified": (
                model.last_modified.isoformat()
                if getattr(model, "last_modified", None)
                else None
            ),
            "tags": model.tags or [],
        },
    }


# =================================================
# Get new ASR models from Hugging Face
# =================================================
def getNewASRModels(limit: int = 100) -> list[dict]:

    models = api.list_models(
        pipeline_tag="automatic-speech-recognition",
        limit=limit,
        sort="created_at",
        full=True,
    )

    return [modelToResult(model) for model in models]

# ===================================================
# Get recently modified ASR models from Hugging Face
# ===================================================

def getRecentlyModifiedASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag="automatic-speech-recognition",
        limit=limit,
        sort="last_modified",
        full=True,
    )

    return [modelToResult(model) for model in models]

# =================================================
# Get most downloaded ASR models from Hugging Face
# =================================================

def getPopularASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag="automatic-speech-recognition",
        limit=limit,
        sort="downloads",
        full=True,
    )

    return [modelToResult(model) for model in models]


# =================================================
# Get trending ASR models from Hugging Face
# =================================================

def getTrendingASRModels(
    limit: int = 100,
) -> list[dict]:

    models = api.list_models(
        pipeline_tag="automatic-speech-recognition",
        limit=limit,
        sort="trending_score",
        full=True,
    )

    return [modelToResult(model) for model in models]


def discoverASRModels(
    limitPerSource: int = 100,
) -> list[dict]:

    candidates = []

    candidates.extend(
        getNewASRModels(limitPerSource)
    )

    candidates.extend(
        getRecentlyModifiedASRModels(limitPerSource)
    )

    candidates.extend(
        getPopularASRModels(limitPerSource)
    )

    candidates.extend(
        getTrendingASRModels(limitPerSource)
    )

    return candidates

def deduplicateHFResults(
    results: list[dict],
) -> list[dict]:

    seen = set()
    unique = []

    for result in results:

        repositoryId = result.get(
            "metadata",
            {},
        ).get("repositoryId")

        if not repositoryId:
            continue

        if repositoryId in seen:
            continue

        seen.add(repositoryId)
        unique.append(result)

    return unique



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
                "title": modelId,
                "url": f"https://huggingface.co/{modelId}",
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
                    "createdAt": (
                        model.created_at.isoformat()
                        if getattr(model, "created_at", None)
                        else None
                    ),
                    "lastModified": (
                        model.last_modified.isoformat()
                        if model.last_modified
                        else None
                    ),
                    "tags": model.tags or [],
                },
            }
        )

    return results


def filterASRModels(
    models: list[dict],
) -> list[dict]:
    """
    Keep Hugging Face models explicitly tagged for ASR.
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
