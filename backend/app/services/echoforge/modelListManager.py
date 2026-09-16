from pathlib import Path

from app.services.echoforge.echoforgeConfig import (
    MODEL_DOWNLOAD_DIR,
)


def getModelListPath(
    downloaderName: str,
) -> Path:

    downloaderDir = MODEL_DOWNLOAD_DIR / downloaderName

    if not downloaderDir.exists():
        raise FileNotFoundError(f"Downloader directory not found: " f"{downloaderDir}")

    return downloaderDir / "model_list"


def getModelListName(
    source: str,
) -> str:

    return source.strip().split("/")[-1]


def getModelListEntries(
    downloaderName: str,
) -> list[dict]:

    modelListPath = getModelListPath(downloaderName)

    if not modelListPath.exists():
        return []

    entries = []

    for rawLine in modelListPath.read_text(encoding="utf-8").splitlines():

        line = rawLine.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        parts = line.split()

        source = parts[0]

        modelListName = parts[1] if len(parts) >= 2 else getModelListName(source)

        entries.append(
            {
                "source": source,
                "modelListName": (modelListName),
            }
        )

    return entries


def findModelListEntry(
    downloaderName: str,
    source: str,
) -> dict | None:

    normalizedSource = source.strip().lower()

    entries = getModelListEntries(downloaderName)

    for entry in entries:

        entrySource = entry["source"].strip().lower()

        if entrySource == normalizedSource:
            return entry

    return None


def hasModelListEntry(
    downloaderName: str,
    source: str,
) -> bool:

    return (
        findModelListEntry(
            downloaderName=downloaderName,
            source=source,
        )
        is not None
    )


def addModelListEntry(
    downloaderName: str,
    source: str,
    modelListName: str | None = None,
) -> dict:

    modelListPath = getModelListPath(downloaderName)

    source = source.strip()

    if not modelListName:
        modelListName = getModelListName(source)

    existingEntry = findModelListEntry(
        downloaderName=downloaderName,
        source=source,
    )

    if existingEntry:

        return {
            **existingEntry,
            "added": False,
            "createdModelList": False,
            "modelListPath": (str(modelListPath)),
        }

    createdModelList = not modelListPath.exists()

    modelListPath.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    newLine = f"{source} " f"{modelListName}"

    if modelListPath.exists():

        existingText = modelListPath.read_text(encoding="utf-8")

        if existingText and not existingText.endswith("\n"):
            existingText += "\n"

        modelListPath.write_text(
            existingText + newLine + "\n",
            encoding="utf-8",
        )

    else:

        modelListPath.write_text(
            newLine + "\n",
            encoding="utf-8",
        )

    return {
        "source": source,
        "modelListName": modelListName,
        "added": True,
        "createdModelList": (createdModelList),
        "modelListPath": (str(modelListPath)),
    }


def removeModelListEntry(
    downloaderName: str,
    source: str,
) -> bool:

    modelListPath = getModelListPath(downloaderName)

    if not modelListPath.exists():
        return False

    normalizedSource = source.strip().lower()

    originalLines = modelListPath.read_text(encoding="utf-8").splitlines()

    updatedLines = []

    removed = False

    for rawLine in originalLines:

        line = rawLine.strip()

        if not line or line.startswith("#"):
            updatedLines.append(rawLine)
            continue

        parts = line.split()

        entrySource = parts[0].strip().lower()

        if entrySource == normalizedSource:
            removed = True
            continue

        updatedLines.append(rawLine)

    if not removed:
        return False

    remainingContent = "\n".join(updatedLines)

    if remainingContent:
        remainingContent += "\n"

    modelListPath.write_text(
        remainingContent,
        encoding="utf-8",
    )

    return True
