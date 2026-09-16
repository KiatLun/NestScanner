def getDownloaderFamily(
    downloaderName: str,
) -> str:

    return downloaderName.removesuffix("_download").replace("_", "-").lower()


def normalizeName(
    value: str,
) -> str:

    return value.strip().lower().replace("-", "").replace("_", "").replace(" ", "")


def resolveDownloader(
    modelName: str,
    sourceType: str,
    source: str,
    modelInfo: list[dict],
) -> dict | None:

    normalizedModelName = normalizeName(modelName)

    normalizedSourceType = sourceType.strip().lower()

    normalizedSource = source.strip().lower()

    normalizedSourceName = normalizeName(normalizedSource.split("/")[-1])

    # ----------------------------------------
    # 1. Prefer model-specific downloader
    # ----------------------------------------

    for entry in modelInfo:

        if entry.get("scope") != "model-specific":
            continue

        entrySourceType = entry.get("sourceType")

        if not entrySourceType:
            continue

        if entrySourceType.strip().lower() != normalizedSourceType:
            continue

        downloaderName = entry.get("downloader")

        if not downloaderName:
            continue

        supportedModels = entry.get(
            "supportedModels",
            [],
        )

        # ------------------------------------
        # 1A. Exact source already known
        # ------------------------------------

        for supportedModel in supportedModels:

            supportedSource = supportedModel.get("source")

            if not supportedSource:
                continue

            normalizedSupportedSource = supportedSource.strip().lower()

            if normalizedSupportedSource == normalizedSource:

                return {
                    **entry,
                    "modelListName": (supportedModel.get("modelListName")),
                    "cacheName": (supportedModel.get("cacheName")),
                    "existingModelListEntryBeforeDownload": True,
                }

        # ------------------------------------
        # 1B. Model-family match
        # ------------------------------------

        familyName = getDownloaderFamily(downloaderName)

        normalizedFamilyName = normalizeName(familyName)

        familyMatches = (
            normalizedFamilyName in normalizedModelName
            or normalizedFamilyName in normalizedSourceName
        )

        if not familyMatches:
            continue

        # ------------------------------------
        # Recover model-specific cache name
        # ------------------------------------

        cacheName = None

        for supportedModel in supportedModels:

            supportedCacheName = supportedModel.get("cacheName")

            if supportedCacheName:

                cacheName = supportedCacheName

                break

        if not cacheName:
            cacheName = familyName

        return {
            **entry,
            "modelListName": None,
            "cacheName": cacheName,
            "existingModelListEntryBeforeDownload": False,
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

        if entrySourceType.strip().lower() != normalizedSourceType:
            continue

        supportedModels = entry.get(
            "supportedModels",
            [],
        )

        # ------------------------------------
        # 2A. Exact model already known
        # ------------------------------------

        for supportedModel in supportedModels:

            supportedSource = supportedModel.get("source")

            if not supportedSource:
                continue

            normalizedSupportedSource = supportedSource.strip().lower()

            if normalizedSupportedSource == normalizedSource:

                return {
                    **entry,
                    "modelListName": (supportedModel.get("modelListName")),
                    "cacheName": (supportedModel.get("cacheName")),
                    "existingModelListEntryBeforeDownload": True,
                }

        # ------------------------------------
        # 2B. New model for generic downloader
        # ------------------------------------

        return {
            **entry,
            "modelListName": None,
            "cacheName": None,
            "existingModelListEntryBeforeDownload": False,
        }

    # ----------------------------------------
    # 3. No compatible downloader
    # ----------------------------------------

    return None
