from pathlib import Path
from pprint import pprint

from app.graph.componentBuilding.workflow import (
    runComponentBuildingWorkflow,
)

from tests.fixtures.researchAgentOutput import (
    researchAgentOutput,
)

# ============================================================
# Models to test
# ============================================================

modelsToTest = [
    # "qwen3-asr-1.7b",  # Existing inference component
    "mega-asr",  # No existing inference component
    # "fun-asr-nano-2512",  # No existing inference component
    # "sensevoice-small",  # No existing inference component
    # "voxtral-mini-3b-2507",  # Existing inference component
    # "whisper-medium",  # Existing inference component
    # "whisper-small",  # Existing inference component
    # "voxtral-mini-4b-realtime-2602",  # Existing inference component
    # "silero-vad",  # Existing inference component
    # "deepspeech-0.9.3",  # No existing inference component
    # "example-direct-asr",  # No existing inference component
]

# ============================================================
# Model test configuration
# ============================================================

modelTestConfig = {
    "qwen3-asr-1.7b": {
        "modelFamily": "qwen",
        "expectGenerated": False,
    },
    "mega-asr": {
        "modelFamily": "mega-asr",
        "expectGenerated": True,
    },
    "fun-asr-nano-2512": {
        "modelFamily": "fun-asr",
        "expectGenerated": True,
    },
    "sensevoice-small": {
        "modelFamily": "sensevoice",
        "expectGenerated": True,
    },
    "voxtral-mini-3b-2507": {
        "modelFamily": "voxtral",
        "expectGenerated": False,
    },
    "whisper-medium": {
        "modelFamily": "whisper",
        "expectGenerated": False,
    },
    "whisper-small": {
        "modelFamily": "whisper",
        "expectGenerated": False,
    },
    "voxtral-mini-4b-realtime-2602": {
        "modelFamily": "voxtral",
        "expectGenerated": False,
    },
    "silero-vad": {
        "modelFamily": "silero",
        "expectGenerated": False,
    },
    "deepspeech-0.9.3": {
        "modelFamily": "deepspeech",
        "expectGenerated": True,
    },
    "example-direct-asr": {
        "modelFamily": "example-direct-asr",
        "expectGenerated": True,
    },
}


def printSection(title: str):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def validateGeneratedFiles(
    inferenceComponent: dict,
):

    componentDir = Path(inferenceComponent["componentDir"])

    mainFile = Path(inferenceComponent["mainFile"])

    requirementsFile = Path(inferenceComponent["requirementsFile"])

    dockerfile = Path(inferenceComponent["dockerfile"])

    expectedFiles = {
        "componentDir": componentDir,
        "main.py": mainFile,
        "requirements.txt": requirementsFile,
        "Dockerfile": dockerfile,
    }

    printSection("GENERATED FILE CHECK")

    for name, path in expectedFiles.items():

        exists = path.exists()

        print(f"{name}: " f"{'PASS' if exists else 'FAIL'}")

        print(f"  {path}")

        if not exists:

            raise RuntimeError("Generated artifact missing: " f"{path}")

    return {
        "componentDir": componentDir,
        "mainFile": mainFile,
        "requirementsFile": requirementsFile,
        "dockerfile": dockerfile,
    }


def validateMainFile(
    mainFile: Path,
):

    mainContent = mainFile.read_text(encoding="utf-8")

    requiredMainPatterns = [
        "BaseInferencePipeline",
        "def load_model",
        "def preprocess",
        "def infer",
        "def to_segments",
        'return "stt"',
        ".run()",
    ]

    printSection("MAIN.PY VALIDATION")

    for pattern in requiredMainPatterns:

        found = pattern in mainContent

        print(f"{pattern}: " f"{'PASS' if found else 'FAIL'}")

        if not found:

            raise RuntimeError(
                "Generated main.py is missing " f"required pattern: {pattern}"
            )


def validateDockerfile(
    dockerfile: Path,
):

    dockerContent = dockerfile.read_text(encoding="utf-8")

    requiredDockerPatterns = [
        "FROM",
        "LOCAL_PYTHON",
        "COPY",
        "WORKDIR",
    ]

    printSection("DOCKERFILE VALIDATION")

    for pattern in requiredDockerPatterns:

        found = pattern in dockerContent

        print(f"{pattern}: " f"{'PASS' if found else 'FAIL'}")

        if not found:

            raise RuntimeError(
                "Generated Dockerfile is " "missing required pattern: " f"{pattern}"
            )


def runModelTest(
    modelKey: str,
):

    print()
    print("-" * 70)
    print(f"Testing: {modelKey}")
    print("-" * 70)

    if modelKey not in researchAgentOutput:

        raise RuntimeError("Research fixture not found: " f"{modelKey}")

    if modelKey not in modelTestConfig:

        raise RuntimeError("Model test config not found: " f"{modelKey}")

    researchResult = researchAgentOutput[modelKey]

    testConfig = modelTestConfig[modelKey]

    candidate = researchResult["candidate"]

    modelName = candidate["name"]

    source = candidate["sourceUrl"]

    modelFamily = testConfig["modelFamily"]

    expectGenerated = testConfig["expectGenerated"]

    technicalProfile = {
        "candidate": candidate,
        "isLocallyDeployable": (researchResult["isLocallyDeployable"]),
        "researchEvidence": (researchResult["researchEvidence"]),
    }

    print(f"Model: {modelName}")

    print(f"Family: {modelFamily}")

    print(f"Source: {source}")

    print("Expected component: " f"{'generated' if expectGenerated else 'existing'}")

    # --------------------------------------------------------
    # Run Component Building
    # --------------------------------------------------------

    result = runComponentBuildingWorkflow(
        modelName=modelName,
        source=source,
        modelFamily=modelFamily,
        technicalProfile=technicalProfile,
        forceBuild=True,
    )

    printSection("COMPONENT BUILDING RESULT")

    pprint(
        result,
        sort_dicts=False,
    )

    # --------------------------------------------------------
    # Workflow status
    # --------------------------------------------------------

    if result.get("status") != "completed":

        raise RuntimeError(
            "Component Building failed.\n"
            f"Status: {result.get('status')}\n"
            f"Error: {result.get('error')}"
        )

    # --------------------------------------------------------
    # Inference component
    # --------------------------------------------------------

    inferenceComponent = result.get("inferenceComponent")

    if not inferenceComponent:

        raise RuntimeError("No inference component returned.")

    printSection("INFERENCE COMPONENT")

    pprint(
        inferenceComponent,
        sort_dicts=False,
    )

    matchedBy = inferenceComponent.get("matchedBy")

    # --------------------------------------------------------
    # Check expected component route
    # --------------------------------------------------------

    if expectGenerated:

        if matchedBy != "generated":

            raise RuntimeError(
                "Expected generated component, " f"but matchedBy={matchedBy}"
            )

        generatedFiles = validateGeneratedFiles(inferenceComponent)

        validateMainFile(generatedFiles["mainFile"])

        validateDockerfile(generatedFiles["dockerfile"])

    else:

        if matchedBy == "generated":

            raise RuntimeError(
                "Expected existing component, "
                "but Component Creation Agent "
                "generated a new one."
            )

        print()
        print("Existing inference component: PASS")

    # --------------------------------------------------------
    # Docker image
    # --------------------------------------------------------

    inferenceImageResult = result.get("inferenceImageResult")

    if not inferenceImageResult:

        raise RuntimeError("No inference image result returned.")

    printSection("INFERENCE IMAGE RESULT")

    pprint(
        inferenceImageResult,
        sort_dicts=False,
    )

    printSection(f"TEST PASSED: {modelKey}")


def main():

    printSection("COMPONENT CREATION TEST")

    passedModels = []
    failedModels = []

    for modelKey in modelsToTest:

        try:

            runModelTest(modelKey)

            passedModels.append(modelKey)

        except Exception as error:

            failedModels.append(
                {
                    "model": modelKey,
                    "error": str(error),
                }
            )

            printSection(f"TEST FAILED: {modelKey}")

            print(str(error))

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    printSection("TEST SUMMARY")

    print(f"Passed: {len(passedModels)}")

    for modelKey in passedModels:

        print(f"  PASS  {modelKey}")

    print()

    print(f"Failed: {len(failedModels)}")

    for failure in failedModels:

        print(f"  FAIL  {failure['model']}")

        print(f"        {failure['error']}")

    if failedModels:

        raise RuntimeError(f"{len(failedModels)} " "component test(s) failed.")


if __name__ == "__main__":

    main()
