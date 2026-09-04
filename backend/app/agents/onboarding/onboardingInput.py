from urllib.parse import urlparse


def inferSourceType(
    sourceUrl: str,
) -> str | None:

    if not sourceUrl:
        return None

    normalizedUrl = sourceUrl.lower()

    if "huggingface.co" in normalizedUrl:
        return "huggingface"

    if "github.com" in normalizedUrl:
        return "github"

    if normalizedUrl.startswith(("http://", "https://")):
        return "directUrl"

    return None


def normalizeSource(
    sourceUrl: str,
    sourceType: str | None,
) -> str:

    if not sourceUrl:
        return ""

    # Hugging Face:
    # https://huggingface.co/Qwen/Qwen3-ASR-1.7B
    # ->
    # Qwen/Qwen3-ASR-1.7B

    if sourceType == "huggingface":

        parsed = urlparse(sourceUrl)

        return parsed.path.strip("/")

    # For GitHub/direct URL,
    # preserve the actual URL for now.

    return sourceUrl


def prepareOnboardingInput(
    researchResult: dict,
) -> dict:

    candidate = researchResult.get(
        "candidate",
        {},
    )

    modelName = candidate.get("name")

    sourceUrl = candidate.get(
        "sourceUrl",
        "",
    )

    sourceType = inferSourceType(sourceUrl)

    source = normalizeSource(
        sourceUrl,
        sourceType,
    )

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "technicalProfile": researchResult.get(
            "technicalProfile",
            {},
        ),
        "researchEvidence": researchResult.get(
            "researchEvidence",
            {},
        ),
    }
