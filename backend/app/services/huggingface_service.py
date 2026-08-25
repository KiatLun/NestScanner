from huggingface_hub import HfApi

api = HfApi()

def get_asr_models(limit: int = 10):
    models = api.list_models(
        pipeline_tag="automatic-speech-recognition",
        sort="lastModified", # get the most recently updated models
        limit=limit
    )

    results = []

    for model in models:
        results.append(
            {
                "id": model.id,
                "author": model.author,
                "downloads": model.downloads,
                "likes": model.likes,
                "pipeline_tag": model.pipeline_tag,
                "last_modified": (
                    model.last_modified.isoformat()
                    if model.last_modified
                    else None
                ),
            }
        )

    return results
        