from app.services.echoforge.echoforgeConfig import MODEL_DOWNLOAD_DIR


def addModelToModelList(
    downloaderName: str,
    source: str,
    modelListName: str,
) -> dict:

    downloaderDir = MODEL_DOWNLOAD_DIR / downloaderName
    modelListPath = downloaderDir / "model_list"

    if not downloaderDir.exists():
        raise FileNotFoundError(
            f"Downloader directory does not exist: {downloaderDir}"
        )

    newEntry = f"{source.strip()} {modelListName.strip()}"

    # ----------------------------------------
    # Create model_list if it does not exist
    # ----------------------------------------

    if not modelListPath.exists():

        modelListPath.write_text(
            newEntry + "\n",
            encoding="utf-8",
        )

        return {
            "added": True,
            "created": True,
            "modelListPath": str(modelListPath),
            "entry": newEntry,
        }

    # ----------------------------------------
    # Check existing entries
    # ----------------------------------------

    existingLines = [
        line.strip()
        for line in modelListPath.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    for line in existingLines:

        parts = line.split()

        existingSource = parts[0]

        existingModelListName = (
            parts[1]
            if len(parts) >= 2
            else existingSource.replace("/", "-")
        )

        if (
            existingSource.lower() == source.strip().lower()
            or existingModelListName.lower()
            == modelListName.strip().lower()
        ):
            return {
                "added": False,
                "created": False,
                "modelListPath": str(modelListPath),
                "entry": line,
            }

    # ----------------------------------------
    # Append to existing model_list
    # ----------------------------------------

    with modelListPath.open("a", encoding="utf-8") as file:
        file.write(newEntry + "\n")

    return {
        "added": True,
        "created": False,
        "modelListPath": str(modelListPath),
        "entry": newEntry,
    }