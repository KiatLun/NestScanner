import json

from pathlib import Path

from clearml import Dataset, Task


def getInferenceDatasetId(
    taskId: str,
) -> str:
    """
    Get the output dataset ID stored as a ClearML artifact
    on the inference task.
    """

    print(
        "[Inference Result Reader] "
        f"Reading inference task: {taskId}"
    )

    task = Task.get_task(
        task_id=taskId
    )

    if not task.artifacts:
        raise RuntimeError(
            "Inference task contains no artifacts: "
            f"{taskId}"
        )

    print(
        "[Inference Result Reader] "
        f"Found {len(task.artifacts)} artifact(s)."
    )

    for artifactName, artifact in task.artifacts.items():

        print(
            "[Inference Result Reader] "
            f"Checking artifact: {artifactName}"
        )

        try:
            artifactData = artifact.get()

        except Exception as error:
            print(
                "[Inference Result Reader] "
                f"Could not read artifact "
                f"'{artifactName}': {error}"
            )

            continue

        # ----------------------------------------------------
        # Case 1:
        # Artifact directly contains the dataset ID as string
        # ----------------------------------------------------

        if isinstance(
            artifactData,
            str,
        ):
            datasetId = artifactData.strip()

            if datasetId:
                print(
                    "[Inference Result Reader] "
                    "Dataset ID found: "
                    f"{datasetId}"
                )

                return datasetId

        # ----------------------------------------------------
        # Case 2:
        # Artifact contains a dictionary
        # ----------------------------------------------------

        if isinstance(
            artifactData,
            dict,
        ):
            datasetId = (
                artifactData.get(
                    "dataset_id"
                )
                or artifactData.get(
                    "datasetId"
                )
            )

            if datasetId:
                print(
                    "[Inference Result Reader] "
                    "Dataset ID found: "
                    f"{datasetId}"
                )

                return str(
                    datasetId
                ).strip()

    raise RuntimeError(
        "Could not find an output dataset ID "
        f"in inference task artifacts: {taskId}"
    )


def getInferenceDatasetPath(
    datasetId: str,
) -> Path:
    """
    Download the ClearML output dataset locally.
    ClearML handles the backing MinIO/S3 storage.
    """

    print(
        "[Inference Result Reader] "
        "Retrieving inference dataset: "
        f"{datasetId}"
    )

    dataset = Dataset.get(
        dataset_id=datasetId
    )

    localPath = (
        dataset.get_local_copy()
    )

    if not localPath:
        raise RuntimeError(
            "ClearML did not return a local path "
            "for inference dataset: "
            f"{datasetId}"
        )

    datasetPath = Path(
        localPath
    )

    if not datasetPath.exists():
        raise RuntimeError(
            "Inference dataset path does not exist: "
            f"{datasetPath}"
        )

    print(
        "[Inference Result Reader] "
        "Dataset available locally at: "
        f"{datasetPath}"
    )

    return datasetPath


def findInferenceManifest(
    datasetPath: Path,
) -> Path:
    """
    Find the inference manifest JSON inside the
    downloaded ClearML dataset.
    """

    print(
        "[Inference Result Reader] "
        "Searching for inference manifest."
    )

    jsonFiles = list(
        datasetPath.rglob(
            "*.json"
        )
    )

    if not jsonFiles:
        raise RuntimeError(
            "No JSON files found inside "
            "inference dataset: "
            f"{datasetPath}"
        )

    # --------------------------------------------------------
    # Prefer likely manifest filenames first
    # --------------------------------------------------------

    preferredNames = [
        "manifest.json",
        "dataset.json",
        "metadata.json",
    ]

    for preferredName in preferredNames:

        for jsonFile in jsonFiles:

            if (
                jsonFile.name.lower()
                == preferredName.lower()
            ):
                print(
                    "[Inference Result Reader] "
                    "Manifest found: "
                    f"{jsonFile}"
                )

                return jsonFile

    # --------------------------------------------------------
    # Otherwise inspect JSON files and find one containing
    # the expected EchoForge dataset structure.
    # --------------------------------------------------------

    for jsonFile in jsonFiles:

        try:
            content = json.loads(
                jsonFile.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            continue

        if (
            isinstance(
                content,
                dict,
            )
            and "items" in content
        ):
            print(
                "[Inference Result Reader] "
                "Manifest found: "
                f"{jsonFile}"
            )

            return jsonFile

    raise RuntimeError(
        "JSON files were found, but none "
        "look like an EchoForge inference manifest."
    )


def loadInferenceManifest(
    manifestPath: Path,
) -> dict:
    """
    Load the inference manifest JSON.
    """

    try:
        manifest = json.loads(
            manifestPath.read_text(
                encoding="utf-8"
            )
        )

    except Exception as error:
        raise RuntimeError(
            "Failed to read inference manifest: "
            f"{manifestPath}. "
            f"Error: {error}"
        ) from error

    if not isinstance(
        manifest,
        dict,
    ):
        raise RuntimeError(
            "Inference manifest is not "
            "a JSON object: "
            f"{manifestPath}"
        )

    return manifest


def extractInferenceErrors(
    manifest: dict,
) -> list[dict]:
    """
    Extract all segment-level inference failures.
    """

    errors = []

    items = manifest.get(
        "items",
        [],
    )

    for itemIndex, item in enumerate(
        items
    ):
        filename = item.get(
            "filename",
            "",
        )

        segments = item.get(
            "segments",
            [],
        )

        for segmentIndex, segment in enumerate(
            segments
        ):
            if not segment.get(
                "error",
                False,
            ):
                continue

            errorMessage = segment.get(
                "metadata",
                ""
            )

            errors.append(
                {
                    "itemIndex": itemIndex,
                    "segmentIndex": segmentIndex,
                    "filename": filename,
                    "start": segment.get(
                        "start"
                    ),
                    "end": segment.get(
                        "end"
                    ),
                    "errorMessage": (
                        errorMessage
                    ),
                }
            )

    return errors


def getUniqueErrorMessages(
    errors: list[dict],
) -> list[str]:
    """
    Deduplicate error messages while preserving order.
    """

    errorMessages = []

    for error in errors:

        errorMessage = error.get(
            "errorMessage",
            ""
        )

        if (
            errorMessage
            and errorMessage
            not in errorMessages
        ):
            errorMessages.append(
                errorMessage
            )

    return errorMessages


def getInferenceResult(
    taskId: str,
) -> dict:
    """
    Main public function.

    Given a ClearML inference task ID:

    1. Read the task artifact.
    2. Extract the output dataset ID.
    3. Download the dataset through ClearML.
    4. Locate the inference manifest.
    5. Extract segment-level inference errors.
    6. Return a structured result.
    """

    print()
    print(
        "=" * 60
    )
    print(
        "[Inference Result Reader] "
        "Reading inference result"
    )
    print(
        "=" * 60
    )

    datasetId = (
        getInferenceDatasetId(
            taskId
        )
    )

    datasetPath = (
        getInferenceDatasetPath(
            datasetId
        )
    )

    manifestPath = (
        findInferenceManifest(
            datasetPath
        )
    )

    manifest = (
        loadInferenceManifest(
            manifestPath
        )
    )

    errors = (
        extractInferenceErrors(
            manifest
        )
    )

    errorMessages = (
        getUniqueErrorMessages(
            errors
        )
    )

    status = (
        "failed"
        if errors
        else "completed"
    )

    result = {
        "taskId": taskId,
        "datasetId": datasetId,
        "datasetPath": str(
            datasetPath
        ),
        "manifestPath": str(
            manifestPath
        ),
        "status": status,
        "errorCount": len(
            errors
        ),
        "errorMessages": (
            errorMessages
        ),
        "errors": errors,
    }

    print()
    print(
        "[Inference Result Reader] "
        f"Status: {status}"
    )

    print(
        "[Inference Result Reader] "
        "Dataset ID: "
        f"{datasetId}"
    )

    print(
        "[Inference Result Reader] "
        "Errors found: "
        f"{len(errors)}"
    )

    if errorMessages:

        print(
            "[Inference Result Reader] "
            "Unique error messages:"
        )

        for errorMessage in errorMessages:
            print(
                f"  - {errorMessage}"
            )

    print(
        "=" * 60
    )

    return result