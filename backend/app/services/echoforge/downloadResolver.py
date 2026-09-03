def resolveDownloader(
    modelName: str,
    sourceType: str,
    source: str,
    modelInfo: list[dict],
) -> dict | None:

    normalizedModelName = modelName.lower()
    normalizedSourceType = sourceType.lower()
    normalizedSource = source.lower()

    # ----------------------------------------
    # 1. Prefer model-specific downloader
    # ----------------------------------------

    for entry in modelInfo:

        if entry.get("scope") != "model-specific":
            continue

        supportedModels = entry.get(
            "supportedModels",
            [],
        )

        for supportedModel in supportedModels:

            supportedSource = supportedModel.get("source")

            if not supportedSource:
                continue

            normalizedSupportedSource = supportedSource.lower()

            # Best match:
            # Research source matches supported source exactly
            if normalizedSource == normalizedSupportedSource:
                return {
                    **entry,
                    "cacheName": supportedModel.get("cacheName"),
                }

            # Secondary fallback:
            # model/family name appears in modelName
            modelPart = normalizedSupportedSource.split("/")[-1]

            if modelPart in normalizedModelName:
                return {
                    **entry,
                    "cacheName": supportedModel.get("cacheName"),
                }

    # ----------------------------------------
    # 2. Generic downloader fallback
    # ----------------------------------------

    for entry in modelInfo:

        if entry.get("scope") != "generic":
            continue

        entrySourceType = entry.get("sourceType")

        if not entrySourceType:
            continue

        if entrySourceType.lower() == normalizedSourceType:
            return {
                **entry,
                "cacheName": None,
            }

    return None
