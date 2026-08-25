import json

from app.services.huggingface_service import get_asr_models
from app.services.llm_service import ask_llm


def discover_asr_models(limit: int = 20) -> str:
    models = get_asr_models(limit=limit)

    models_json = json.dumps(
        models,
        indent=2,
    )

    prompt = f"""
You are an AI research assistant focused on speech recognition models.

Below is a list of recently updated automatic speech recognition models
from Hugging Face.

Your task is to identify models that appear worth further investigation.

Look for:
- newly released or recently updated models
- models with meaningful download activity
- models with strong community interest
- models that appear to introduce new architectures or capabilities
- multilingual models
- potentially important ASR models

Do not assume that a recently modified model is necessarily newly released.

For each interesting model, provide:
1. model ID
2. reason it looks interesting
3. whether it should be investigated further

Models:

{models_json}
"""

    return ask_llm(prompt)