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

            # --------------------------------
            # Exact source match
            # --------------------------------

            if normalizedSource == normalizedSupportedSource:

                return {
                    **entry,
                    "modelListName": (supportedModel.get("modelListName")),
                    "cacheName": (supportedModel.get("cacheName")),
                }

            # --------------------------------
            # Model-name/family match
            # --------------------------------

            modelPart = normalizedSupportedSource.split("/")[-1]

            if modelPart in normalizedModelName:

                return {
                    **entry,
                    "modelListName": (supportedModel.get("modelListName")),
                    "cacheName": (supportedModel.get("cacheName")),
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

            # If this exact model already exists
            # in the generic model_list, reuse
            # its metadata.
            for supportedModel in entry.get(
                "supportedModels",
                [],
            ):

                supportedSource = supportedModel.get("source")

                if not supportedSource:
                    continue

                if supportedSource.lower() == normalizedSource:

                    return {
                        **entry,
                        "modelListName": (supportedModel.get("modelListName")),
                        "cacheName": (supportedModel.get("cacheName")),
                    }

            # Unknown HF model can still try the
            # generic HF downloader.
            return {
                **entry,
                "modelListName": None,
                "cacheName": None,
            }

    return None
