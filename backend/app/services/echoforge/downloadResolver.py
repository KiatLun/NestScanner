def resolveDownloader(
    modelName: str,
    sourceType: str,
    capabilities: list[dict],
) -> dict | None:

    normalizedModelName = modelName.lower()

    # 1. Prefer model-specific downloader
    for capability in capabilities:

        if capability.get("scope") != "model-specific":
            continue

        supportedModels = capability.get(
            "supportedModels",
            [],
        )

        for supportedModel in supportedModels:

            if supportedModel.lower() in normalizedModelName:
                return capability

    # 2. Fall back to generic downloader
    for capability in capabilities:

        if (
            capability.get("scope") == "generic"
            and capability.get("sourceType") == sourceType
        ):
            return capability

    # 3. Nothing currently supported
    return None
