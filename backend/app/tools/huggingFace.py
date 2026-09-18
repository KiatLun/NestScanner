from huggingface_hub import HfApi

api = HfApi()


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
                "url": (f"https://huggingface.co/" f"{modelId}"),
                "description": None,
                "metadata": {
                    "organisation": (modelId.split("/")[0] if "/" in modelId else None),
                    "pipelineTag": (model.pipeline_tag),
                    "downloads": (model.downloads),
                    "likes": model.likes,
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
                        model.last_modified.isoformat() if model.last_modified else None
                    ),
                    "tags": (model.tags or []),
                },
            }
        )

    return results

def getASRModels(
    limit: int = 50,
) -> list[dict]:
    """
    Retrieve models directly from Hugging Face's
    automatic-speech-recognition pipeline category.

    This does not rely on ASR keywords appearing in the
    model name or description.
    """

    models = api.list_models(
        pipeline_tag="automatic-speech-recognition",
        limit=limit,
        full=True,
        sort="last_modified",
    )

    results = []

    for model in models:
        modelId = model.id

        results.append(
            {
                "source": "huggingface",
                "title": modelId,
                "url": (
                    f"https://huggingface.co/{modelId}"
                ),
                "description": None,
                "metadata": {
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
