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
    # "qwen3-asr-1.7b",
    # "mega-asr",
    # "fun-asr-nano-2512",
    "sensevoice-small",
    # "voxtral-mini-3b-2507",
    # "whisper-medium",
    # "whisper-small",
    # "voxtral-mini-4b-realtime-2602",
    # "silero-vad",
    # "deepspeech-0.9.3",
    # "example-direct-asr",
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


def printSection(
    title: str,
):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def validateGeneratedFiles(
    inferenceComponent: dict,
):

    componentDir = Path(
        inferenceComponent[
            "componentDir"
        ]
    )

    mainFile = Path(
        inferenceComponent[
            "mainFile"
        ]
    )

    requirementsFile = Path(
        inferenceComponent[
            "requirementsFile"
        ]
    )

    dockerfile = Path(
        inferenceComponent[
            "dockerfile"
        ]
    )

    expectedFiles = {
        "componentDir": componentDir,
        "main.py": mainFile,
        "requirements.txt": requirementsFile,
        "Dockerfile": dockerfile,
    }

    printSection(
        "GENERATED FILE CHECK"
    )

    for name, path in (
        expectedFiles.items()
    ):

        exists = path.exists()

        print(
            f"{name}: "
            f"{'PASS' if exists else 'FAIL'}"
        )

        print(
            f"  {path}"
        )

        if not exists:

            raise RuntimeError(
                "Generated artifact missing: "
                f"{path}"
            )

    return {
        "componentDir": componentDir,
        "mainFile": mainFile,
        "requirementsFile": (
            requirementsFile
        ),
        "dockerfile": dockerfile,
    }


def validateMainFile(
    mainFile: Path,
):

    mainContent = (
        mainFile.read_text(
            encoding="utf-8"
        )
    )

    printSection(
        "MAIN.PY VALIDATION"
    )

    # --------------------------------------------------------
    # Required Pattern A structure
    # --------------------------------------------------------

    requiredMainPatterns = [
        (
            "from stt_inference import "
            "SttInferencePipeline"
        ),
        "SttInferencePipeline",
        "def load_model",
        "def infer_segment",
        'if __name__ == "__main__":',
        ".run()",
    ]

    for pattern in (
        requiredMainPatterns
    ):

        found = (
            pattern
            in mainContent
        )

        print(
            f"{pattern}: "
            f"{'PASS' if found else 'FAIL'}"
        )

        if not found:

            raise RuntimeError(
                "Generated main.py is missing "
                "required Pattern A structure: "
                f"{pattern}"
            )

    # --------------------------------------------------------
    # Invalid imports
    # --------------------------------------------------------

    invalidImportPatterns = [
        "from components.",
        "import components.",
        "from inference_component.",
        "import inference_component.",
        (
            "from base_classes."
            "base_inference import "
            "BaseInferencePipeline"
        ),
    ]

    for pattern in (
        invalidImportPatterns
    ):

        found = (
            pattern
            in mainContent
        )

        print(
            f"Reject {pattern}: "
            f"{'FAIL' if found else 'PASS'}"
        )

        if found:

            raise RuntimeError(
                "Generated main.py contains "
                "invalid EchoForge import: "
                f"{pattern}"
            )

    # --------------------------------------------------------
    # Shared pipeline methods should not be reimplemented
    # --------------------------------------------------------

    disallowedMethods = [
        "def preprocess(",
        "def infer(",
        "def to_segments(",
        "def model_task(",
    ]

    for pattern in (
        disallowedMethods
    ):

        found = (
            pattern
            in mainContent
        )

        print(
            f"Reject {pattern}: "
            f"{'FAIL' if found else 'PASS'}"
        )

        if found:

            raise RuntimeError(
                "Generated Pattern A component "
                "reimplements shared "
                "SttInferencePipeline method: "
                f"{pattern}"
            )


def validateDockerfile(
    dockerfile: Path,
    inferenceComponent: dict,
):

    dockerContent = (
        dockerfile.read_text(
            encoding="utf-8"
        )
    )

    componentName = (
        inferenceComponent[
            "component"
        ]
    )

    componentRelativePath = (
        "inference_component/"
        "stt_inference/"
        f"{componentName}"
    )

    requirementsRelativePath = (
        f"{componentRelativePath}/"
        "requirements.txt"
    )

    printSection(
        "DOCKERFILE VALIDATION"
    )

    # --------------------------------------------------------
    # Required Pattern A Docker structure
    # --------------------------------------------------------

    requiredDockerPatterns = [
        "FROM",
        "WORKDIR /app",
        "COPY base_classes base_classes",
        (
            "COPY inference_component/"
            "stt_inference/"
            "stt_inference.py ."
        ),
        requirementsRelativePath,
        componentRelativePath,
        "LOCAL_PYTHON",
    ]

    for pattern in (
        requiredDockerPatterns
    ):

        found = (
            pattern
            in dockerContent
        )

        print(
            f"{pattern}: "
            f"{'PASS' if found else 'FAIL'}"
        )

        if not found:

            raise RuntimeError(
                "Generated Dockerfile is "
                "missing required Pattern A "
                f"structure: {pattern}"
            )

    # --------------------------------------------------------
    # Reject incorrect shortened component path
    # --------------------------------------------------------

    incorrectComponentPath = (
        "inference_component/"
        f"{componentName}"
    )

    found = (
        incorrectComponentPath
        in dockerContent
    )

    print(
        f"Reject {incorrectComponentPath}: "
        f"{'FAIL' if found else 'PASS'}"
    )

    if found:

        raise RuntimeError(
            "Generated Dockerfile uses "
            "incorrect component path: "
            f"{incorrectComponentPath}"
        )


def runModelTest(
    modelKey: str,
):

    print()
    print("-" * 70)
    print(
        f"Testing: {modelKey}"
    )
    print("-" * 70)

    if (
        modelKey
        not in researchAgentOutput
    ):

        raise RuntimeError(
            "Research fixture not found: "
            f"{modelKey}"
        )

    if (
        modelKey
        not in modelTestConfig
    ):

        raise RuntimeError(
            "Model test config not found: "
            f"{modelKey}"
        )

    researchResult = (
        researchAgentOutput[
            modelKey
        ]
    )

    testConfig = (
        modelTestConfig[
            modelKey
        ]
    )

    candidate = (
        researchResult[
            "candidate"
        ]
    )

    modelName = (
        candidate[
            "name"
        ]
    )

    source = (
        candidate[
            "sourceUrl"
        ]
    )

    modelFamily = (
        testConfig[
            "modelFamily"
        ]
    )

    expectGenerated = (
        testConfig[
            "expectGenerated"
        ]
    )

    technicalProfile = {
        "candidate": candidate,
        "isLocallyDeployable": (
            researchResult[
                "isLocallyDeployable"
            ]
        ),
        "researchEvidence": (
            researchResult[
                "researchEvidence"
            ]
        ),
    }

    print(
        f"Model: {modelName}"
    )

    print(
        f"Family: {modelFamily}"
    )

    print(
        f"Source: {source}"
    )

    print(
        "Expected component: "
        f"{'generated' if expectGenerated else 'existing'}"
    )

    # --------------------------------------------------------
    # Run Component Building
    # --------------------------------------------------------

    result = (
        runComponentBuildingWorkflow(
            modelName=modelName,
            source=source,
            modelFamily=modelFamily,
            technicalProfile=(
                technicalProfile
            ),
            forceBuild=True,
        )
    )

    printSection(
        "COMPONENT BUILDING RESULT"
    )

    pprint(
        result,
        sort_dicts=False,
    )

    # --------------------------------------------------------
    # Workflow status
    # --------------------------------------------------------

    if (
        result.get("status")
        != "completed"
    ):

        raise RuntimeError(
            "Component Building failed.\n"
            f"Status: "
            f"{result.get('status')}\n"
            f"Error: "
            f"{result.get('error')}"
        )

    # --------------------------------------------------------
    # Inference component
    # --------------------------------------------------------

    inferenceComponent = (
        result.get(
            "inferenceComponent"
        )
    )

    if not inferenceComponent:

        raise RuntimeError(
            "No inference component "
            "returned."
        )

    printSection(
        "INFERENCE COMPONENT"
    )

    pprint(
        inferenceComponent,
        sort_dicts=False,
    )

    matchedBy = (
        inferenceComponent.get(
            "matchedBy"
        )
    )

    # --------------------------------------------------------
    # Check expected component route
    # --------------------------------------------------------

    if expectGenerated:

        if (
            matchedBy
            != "generated"
        ):

            raise RuntimeError(
                "Expected generated component, "
                f"but matchedBy={matchedBy}"
            )

        generatedFiles = (
            validateGeneratedFiles(
                inferenceComponent
            )
        )

        validateMainFile(
            generatedFiles[
                "mainFile"
            ]
        )

        validateDockerfile(
            generatedFiles[
                "dockerfile"
            ],
            inferenceComponent=(
                inferenceComponent
            ),
        )

    else:

        if matchedBy == "generated":

            raise RuntimeError(
                "Expected existing component, "
                "but Component Creation Agent "
                "generated a new one."
            )

        print()
        print(
            "Existing inference component: "
            "PASS"
        )

    # --------------------------------------------------------
    # Docker image
    # --------------------------------------------------------

    inferenceImageResult = (
        result.get(
            "inferenceImageResult"
        )
    )

    if not inferenceImageResult:

        raise RuntimeError(
            "No inference image result "
            "returned."
        )

    printSection(
        "INFERENCE IMAGE RESULT"
    )

    pprint(
        inferenceImageResult,
        sort_dicts=False,
    )

    printSection(
        f"TEST PASSED: {modelKey}"
    )


def main():

    printSection(
        "COMPONENT CREATION TEST"
    )

    passedModels = []
    failedModels = []

    for modelKey in (
        modelsToTest
    ):

        try:

            runModelTest(
                modelKey
            )

            passedModels.append(
                modelKey
            )

        except Exception as error:

            failedModels.append(
                {
                    "model": modelKey,
                    "error": str(error),
                }
            )

            printSection(
                f"TEST FAILED: "
                f"{modelKey}"
            )

            print(
                str(error)
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    printSection(
        "TEST SUMMARY"
    )

    print(
        f"Passed: "
        f"{len(passedModels)}"
    )

    for modelKey in (
        passedModels
    ):

        print(
            f"  PASS  {modelKey}"
        )

    print()

    print(
        f"Failed: "
        f"{len(failedModels)}"
    )

    for failure in (
        failedModels
    ):

        print(
            f"  FAIL  "
            f"{failure['model']}"
        )

        print(
            f"        "
            f"{failure['error']}"
        )

    if failedModels:

        raise RuntimeError(
            f"{len(failedModels)} "
            "component test(s) failed."
        )


if __name__ == "__main__":

    main()