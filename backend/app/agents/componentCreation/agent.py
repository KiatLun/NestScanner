from pathlib import Path
import re

from app.agents.componentCreation.schemas import (
    ComponentCreationInput,
    ComponentCreationOutput,
)

from app.llm.client import getLLM

# ============================================================
# Local Component Creation references
# ============================================================

REFERENCE_DIR = Path(__file__).resolve().parent / "references"

BASE_CLASSES_FILE = REFERENCE_DIR / "base_classes.md"

DEVELOPER_GUIDE_FILE = REFERENCE_DIR / "developer_guide.md"

STT_REFERENCE_DIR = REFERENCE_DIR / "stt_reference"

STT_REFERENCE_MAIN_FILE = STT_REFERENCE_DIR / "main.py"

STT_REFERENCE_REQUIREMENTS_FILE = STT_REFERENCE_DIR / "requirements.txt"

STT_REFERENCE_DOCKERFILE = STT_REFERENCE_DIR / "Dockerfile"


# ============================================================
# Reference loading
# ============================================================


def readReferenceFile(
    path: Path,
    required: bool = True,
) -> str:

    if not path.exists():

        if required:

            raise FileNotFoundError(
                "Required Component Creation " f"reference not found: {path}"
            )

        return ""

    return path.read_text(encoding="utf-8")


def loadComponentReferences() -> dict:

    return {
        "baseClasses": readReferenceFile(BASE_CLASSES_FILE),
        "developerGuide": readReferenceFile(DEVELOPER_GUIDE_FILE),
        "referenceMain": readReferenceFile(STT_REFERENCE_MAIN_FILE),
        "referenceRequirements": readReferenceFile(
            STT_REFERENCE_REQUIREMENTS_FILE,
            required=False,
        ),
        "referenceDockerfile": readReferenceFile(
            STT_REFERENCE_DOCKERFILE,
            required=False,
        ),
    }


# ============================================================
# Generated output parsing
# ============================================================


def extractSection(
    content: str,
    sectionName: str,
) -> str:

    pattern = rf"<{sectionName}>" rf"(.*?)" rf"</{sectionName}>"

    match = re.search(
        pattern,
        content,
        re.DOTALL,
    )

    if not match:

        raise ValueError(
            "Component Creation Agent response " "is missing section: " f"{sectionName}"
        )

    sectionContent = match.group(1).strip()

    if not sectionContent:

        raise ValueError(
            "Component Creation Agent returned " "an empty section: " f"{sectionName}"
        )

    return sectionContent


# ============================================================
# Deterministic component metadata
# ============================================================


def buildComponentName(
    modelFamily: str,
) -> str:

    normalizedFamily = (
        modelFamily.lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    )

    normalizedFamily = re.sub(
        r"[^a-z0-9_]",
        "",
        normalizedFamily,
    )

    return f"stt_inference_{normalizedFamily}"


def buildImageName(
    componentName: str,
) -> str:

    return f"{componentName}:latest"


def buildComponentRelativePath(
    componentName: str,
) -> str:

    return "inference_component/" "stt_inference/" f"{componentName}"


def buildEntryPoint(
    componentName: str,
) -> str:

    componentRelativePath = buildComponentRelativePath(componentName)

    return f"/app/{componentRelativePath}/main.py"


# ============================================================
# Reference convention helpers
# ============================================================


def extractBaseInferenceImport(
    referenceMain: str,
) -> str | None:

    lines = referenceMain.splitlines()

    for index, line in enumerate(lines):

        if "BaseInferencePipeline" not in line:

            continue

        strippedLine = line.strip()

        if not strippedLine.startswith("from "):

            continue

        # Single-line import
        if "import BaseInferencePipeline" in strippedLine:

            return strippedLine

        # Multi-line import
        importLines = [strippedLine]

        for nextLine in lines[index + 1 :]:

            importLines.append(nextLine.strip())

            if ")" in nextLine:

                break

        return "\n".join(importLines)

    return None


# ============================================================
# Generated component validation
# ============================================================


def validateGeneratedMain(
    mainFileContent: str,
    referenceMain: str,
):

    # --------------------------------------------------------
    # Required EchoForge interface
    # --------------------------------------------------------

    requiredPatterns = [
        "BaseInferencePipeline",
        "def load_model",
        "def preprocess",
        "def infer",
        "def to_segments",
        'return "stt"',
        ".run()",
    ]

    for pattern in requiredPatterns:

        if pattern not in mainFileContent:

            raise ValueError(
                "Generated main.py is missing "
                "required EchoForge pattern: "
                f"{pattern}"
            )

    # --------------------------------------------------------
    # Reference BaseInferencePipeline import
    # --------------------------------------------------------

    referenceBaseImport = extractBaseInferenceImport(referenceMain)

    if referenceBaseImport:

        referenceImportMatch = re.search(
            r"from\s+([A-Za-z0-9_\.]+)" r"\s+import",
            referenceBaseImport,
        )

        generatedImportMatch = re.search(
            r"from\s+([A-Za-z0-9_\.]+)"
            r"\s+import\s*\(?"
            r"[\s\S]*?"
            r"BaseInferencePipeline",
            mainFileContent,
        )

        if referenceImportMatch and generatedImportMatch:

            referenceModule = referenceImportMatch.group(1)

            generatedModule = generatedImportMatch.group(1)

            if generatedModule != referenceModule:

                raise ValueError(
                    "Generated main.py does not "
                    "follow the BaseInferencePipeline "
                    "import path used by the working "
                    "EchoForge reference component.\n"
                    f"Reference: {referenceModule}\n"
                    f"Generated: {generatedModule}"
                )

    # --------------------------------------------------------
    # Reject obvious placeholder code
    # --------------------------------------------------------

    invalidPatterns = [
        "TODO",
        "NotImplementedError",
    ]

    for pattern in invalidPatterns:

        if pattern in mainFileContent:

            raise ValueError(
                "Generated main.py contains "
                "placeholder implementation: "
                f"{pattern}"
            )


def validateGeneratedDockerfile(
    dockerfileContent: str,
    referenceDockerfile: str,
    componentName: str,
):

    # --------------------------------------------------------
    # Basic Dockerfile validity
    # --------------------------------------------------------

    if "FROM" not in dockerfileContent:

        raise ValueError("Generated Dockerfile is " "missing required pattern: FROM")

    # --------------------------------------------------------
    # Exact generated component path
    # --------------------------------------------------------

    componentRelativePath = buildComponentRelativePath(componentName)

    incorrectComponentPath = "inference_component/" f"{componentName}"

    if incorrectComponentPath in dockerfileContent:

        raise ValueError(
            "Generated Dockerfile uses an "
            "incorrect component path.\n"
            f"Generated: {incorrectComponentPath}\n"
            f"Expected: {componentRelativePath}"
        )

    # --------------------------------------------------------
    # Validate COPY paths when component path is used
    # --------------------------------------------------------

    generatedComponentReferences = [
        line.strip()
        for line in dockerfileContent.splitlines()
        if (line.strip().startswith("COPY ") and componentName in line)
    ]

    for line in generatedComponentReferences:

        if componentRelativePath not in line:

            raise ValueError(
                "Generated Dockerfile contains "
                "an invalid generated-component "
                "COPY path:\n"
                f"{line}\n"
                "Expected component location:\n"
                f"{componentRelativePath}"
            )

    # --------------------------------------------------------
    # Preserve important reference conventions
    # --------------------------------------------------------

    referencePatterns = [
        "WORKDIR",
        "LOCAL_PYTHON",
        "PYTHONPATH",
    ]

    for pattern in referencePatterns:

        if pattern in referenceDockerfile and pattern not in dockerfileContent:

            raise ValueError(
                "Generated Dockerfile does not "
                "follow the working EchoForge "
                "reference convention: "
                f"{pattern}"
            )


# ============================================================
# Prompt
# ============================================================


def buildPrompt(
    componentInput: ComponentCreationInput,
    references: dict,
    componentName: str,
) -> str:

    componentRelativePath = buildComponentRelativePath(componentName)

    mainRelativePath = f"{componentRelativePath}/main.py"

    requirementsRelativePath = f"{componentRelativePath}/requirements.txt"

    return f"""
You are the Component Creation Agent for EchoForge.

Your task is to adapt a known working EchoForge STT inference
component so that it supports a new ASR model.

============================================================
SOURCE OF TRUTH
============================================================

Use all supplied sources together.

PRIORITY 1 - ECHOFORGE DOCUMENTATION

The supplied base classes documentation and developer guide
define the authoritative EchoForge interface and behavioural
contract.

The generated component MUST comply with these documents.

If the working reference component conflicts with the
documentation, follow the documentation.

PRIORITY 2 - WORKING STT REFERENCE COMPONENT

The supplied STT reference component is known to work inside
EchoForge.

Use it as the concrete implementation template for:

- import paths
- package structure
- BaseInferencePipeline usage
- class structure
- method signatures
- ClearML integration
- runtime behaviour
- .run() pattern
- Docker structure
- Docker working-directory assumptions
- Python path conventions
- environment configuration
- dependency installation conventions

Preserve these conventions unless:

1. the EchoForge documentation requires something different, or
2. the target model genuinely requires a model-specific change.

PRIORITY 3 - RESEARCH AGENT OUTPUT

The Research Agent information describes the target model.

Use it for model-specific decisions such as:

- model framework
- model loading
- processor
- tokenizer
- feature extractor
- audio preparation
- inference API
- decoding
- target-model dependencies

============================================================
TARGET MODEL
============================================================

Model name:
{componentInput.modelName}

Model family:
{componentInput.modelFamily}

Model source:
{componentInput.source}

Generated component name:
{componentName}

Research Agent technical profile:

{componentInput.technicalProfile}

============================================================
GENERATED COMPONENT LOCATION
============================================================

The EchoForge Docker build context is the components directory.

The generated component WILL be written at this exact path,
relative to that build context:

{componentRelativePath}

Therefore:

main.py is located at:

{mainRelativePath}

requirements.txt is located at:

{requirementsRelativePath}

These paths are deterministic.

Do NOT guess or shorten them.

In particular, do NOT use:

inference_component/{componentName}

because that path is WRONG.

The stt_inference directory MUST remain present.

When adapting Docker COPY statements from the reference,
replace the reference component path with this exact path:

{componentRelativePath}

============================================================
ECHOFORGE BASE CLASSES DOCUMENTATION
============================================================

{references["baseClasses"]}

============================================================
ECHOFORGE DEVELOPER GUIDE
============================================================

{references["developerGuide"]}

============================================================
WORKING STT REFERENCE - main.py
============================================================

{references["referenceMain"]}

============================================================
WORKING STT REFERENCE - requirements.txt
============================================================

{references["referenceRequirements"]}

============================================================
WORKING STT REFERENCE - Dockerfile
============================================================

{references["referenceDockerfile"]}

============================================================
ADAPTATION STRATEGY
============================================================

Start from the working STT reference component.

Do NOT create a completely new EchoForge integration from
scratch.

First determine which parts of the reference are:

1. EchoForge infrastructure
2. reference-model-specific code

Preserve EchoForge infrastructure whenever it remains
compatible with the supplied documentation.

Preserve the same general approach to:

- imports
- BaseInferencePipeline import path
- class inheritance
- model_task
- method signatures
- ClearML behaviour
- runtime environment
- pipeline execution
- Docker structure
- working directory
- Python path behaviour
- .run() behaviour

Only modify parts required for the TARGET MODEL.

Typical model-specific parts include:

- model-library imports
- processor/tokenizer imports
- load_model()
- preprocess()
- infer()
- decoding
- to_segments() where required
- target-model requirements
- target-model system dependencies

Do not change EchoForge infrastructure merely because another
implementation is possible.

============================================================
MAIN.PY REQUIREMENTS
============================================================

The generated main.py must:

- comply with the supplied EchoForge documentation

- preserve the working STT reference component's EchoForge
  structure as closely as possible

- subclass BaseInferencePipeline

- use the same BaseInferencePipeline import path as the working
  reference unless the documentation explicitly requires
  otherwise

- implement the model_task property

- return "stt" from model_task

- implement:

  load_model(model_path, **kwargs)

- load model weights from the local model_path supplied by
  EchoForge

- NOT download model weights again during inference

- implement:

  preprocess(audio_path, item, **kwargs)

- use EchoForge audio-loading utilities according to the
  documentation and working reference

- implement:

  infer(inputs, **kwargs)

- implement:

  to_segments(inferred, **kwargs)

- produce the STT output structure required by EchoForge

- use the correct target-model inference API

- use Research Agent information for target-model-specific
  implementation decisions

- preserve the reference component startup pattern

- contain working implementation code

- not contain TODO blocks

- not contain NotImplementedError

- not invent unsupported target-model APIs

============================================================
REQUIREMENTS.TXT REQUIREMENTS
============================================================

Use the reference requirements as an implementation guide.

Retain dependencies required by EchoForge or by the working
runtime environment.

Remove packages only required by the reference model.

Add dependencies required by the target model.

The generated requirements.txt must:

- match imports used by main.py
- use valid pip-installable package names
- avoid standard-library modules
- avoid unnecessary dependencies

============================================================
DOCKERFILE REQUIREMENTS
============================================================

Use the working reference Dockerfile as the primary template.

Preserve its EchoForge-specific runtime conventions as closely
as possible.

This includes, where present in the reference:

- base-image approach
- environment variables
- LOCAL_PYTHON
- PYTHONPATH
- WORKDIR
- COPY layout
- package-installation approach
- operating-system dependency setup

When adapting a COPY command that points to the inference
component, use this exact component path:

{componentRelativePath}

For example, if the reference Dockerfile copies the component
requirements separately, the adapted path must be:

COPY {requirementsRelativePath} requirements.txt

If the reference Dockerfile copies the component directory,
the adapted path must be:

COPY {componentRelativePath} .

Do NOT use:

COPY inference_component/{componentName}/requirements.txt requirements.txt

Do NOT use:

COPY inference_component/{componentName} .

Those paths are incorrect because they omit:

stt_inference/

Only change Dockerfile content when required by:

- target-model system dependencies
- target-model Python dependencies
- EchoForge documentation

Do NOT redesign:

- Docker COPY strategy
- Python path strategy
- working directory
- container source layout
- ClearML runtime integration

unless the EchoForge documentation requires it.

============================================================
IMPORTANT REASONING RULE
============================================================

Before generating the files, reason internally about:

1. Which parts of the working reference are EchoForge
   infrastructure?
2. Which parts are reference-model-specific?
3. Which parts are explicitly required by EchoForge
   documentation?
4. Which parts must change for the target model?
5. What is the exact generated component path?

Then:

Preserve infrastructure.

Respect documentation.

Use the deterministic component path supplied above.

Replace only model-specific logic.

============================================================
OUTPUT FORMAT
============================================================

Return EXACTLY these three sections:

<MAIN_PY>
complete contents of main.py
</MAIN_PY>

<REQUIREMENTS>
complete contents of requirements.txt
</REQUIREMENTS>

<DOCKERFILE>
complete contents of Dockerfile
</DOCKERFILE>

============================================================
STRICT OUTPUT RULES
============================================================

- Do not return JSON.
- Do not use Markdown code fences.
- Do not add explanations before <MAIN_PY>.
- Do not add explanations after </DOCKERFILE>.
- Do not write filenames outside the section markers.
- Do not omit any section.
"""


# ============================================================
# Component Creation Agent
# ============================================================


def componentCreationAgent(
    componentInput: ComponentCreationInput,
) -> ComponentCreationOutput:

    print(
        "[Component Creation Agent] "
        "Starting component generation: "
        f"{componentInput.modelName}"
    )

    # --------------------------------------------------------
    # 1. Load EchoForge references
    # --------------------------------------------------------

    print("[Component Creation Agent] " "Loading local EchoForge references.")

    references = loadComponentReferences()

    print("[Component Creation Agent] " "References loaded.")

    # --------------------------------------------------------
    # 2. Resolve deterministic metadata
    # --------------------------------------------------------

    componentName = buildComponentName(componentInput.modelFamily)

    componentRelativePath = buildComponentRelativePath(componentName)

    imageName = buildImageName(componentName)

    entryPoint = buildEntryPoint(componentName)

    print("[Component Creation Agent] " "Component name: " f"{componentName}")

    print("[Component Creation Agent] " "Component path: " f"{componentRelativePath}")

    # --------------------------------------------------------
    # 3. Build adaptation prompt
    # --------------------------------------------------------

    prompt = buildPrompt(
        componentInput=componentInput,
        references=references,
        componentName=componentName,
    )

    # --------------------------------------------------------
    # 4. Call LLM
    # --------------------------------------------------------

    print("[Component Creation Agent] " "Calling LLM.")

    llm = getLLM()

    response = llm.invoke(prompt)

    if hasattr(
        response,
        "content",
    ):

        content = response.content

    else:

        content = str(response)

    if not isinstance(
        content,
        str,
    ):

        content = str(content)

    print("[Component Creation Agent] " "LLM generation completed.")

    # --------------------------------------------------------
    # 5. Parse generated files
    # --------------------------------------------------------

    try:

        mainFileContent = extractSection(
            content,
            "MAIN_PY",
        )

        requirementsContent = extractSection(
            content,
            "REQUIREMENTS",
        )

        dockerfileContent = extractSection(
            content,
            "DOCKERFILE",
        )

    except Exception:

        print()
        print("[Component Creation Agent] " "Unable to parse generated response.")

        print("[Component Creation Agent] " "Raw response preview:")

        print("-" * 70)

        print(content[:3000])

        print("-" * 70)

        raise

    print("[Component Creation Agent] " "Generated files parsed successfully.")

    # --------------------------------------------------------
    # 6. Validate EchoForge conventions
    # --------------------------------------------------------

    validateGeneratedMain(
        mainFileContent=mainFileContent,
        referenceMain=references["referenceMain"],
    )

    validateGeneratedDockerfile(
        dockerfileContent=dockerfileContent,
        referenceDockerfile=references["referenceDockerfile"],
        componentName=componentName,
    )

    print("[Component Creation Agent] " "Generated component validation passed.")

    # --------------------------------------------------------
    # 7. Build structured result
    # --------------------------------------------------------

    result = ComponentCreationOutput(
        componentName=componentName,
        mainFileContent=mainFileContent,
        requirementsContent=requirementsContent,
        dockerfileContent=dockerfileContent,
        imageName=imageName,
        entryPoint=entryPoint,
        reasoning=(
            "Adapted from a working EchoForge "
            "STT inference component while "
            "respecting EchoForge documentation, "
            "the deterministic component path, "
            "and Research Agent technical "
            "information."
        ),
    )

    print("[Component Creation Agent] " "Component generated: " f"{componentName}")

    return result


from pathlib import Path
import re

from app.agents.componentCreation.schemas import (
    ComponentCreationInput,
    ComponentCreationOutput,
)

from app.llm.client import getLLM

# ============================================================
# Local Component Creation references
# ============================================================

REFERENCE_DIR = Path(__file__).resolve().parent / "references"

BASE_CLASSES_FILE = REFERENCE_DIR / "base_classes.md"

DEVELOPER_GUIDE_FILE = REFERENCE_DIR / "developer_guide.md"

STT_REFERENCE_DIR = REFERENCE_DIR / "stt_reference"

STT_REFERENCE_MAIN_FILE = STT_REFERENCE_DIR / "main.py"

STT_REFERENCE_REQUIREMENTS_FILE = STT_REFERENCE_DIR / "requirements.txt"

STT_REFERENCE_DOCKERFILE = STT_REFERENCE_DIR / "Dockerfile"


# ============================================================
# Reference loading
# ============================================================


def readReferenceFile(
    path: Path,
    required: bool = True,
) -> str:

    if not path.exists():

        if required:

            raise FileNotFoundError(
                "Required Component Creation " f"reference not found: {path}"
            )

        return ""

    return path.read_text(encoding="utf-8")


def loadComponentReferences() -> dict:

    return {
        "baseClasses": readReferenceFile(BASE_CLASSES_FILE),
        "developerGuide": readReferenceFile(DEVELOPER_GUIDE_FILE),
        "referenceMain": readReferenceFile(STT_REFERENCE_MAIN_FILE),
        "referenceRequirements": readReferenceFile(
            STT_REFERENCE_REQUIREMENTS_FILE,
            required=False,
        ),
        "referenceDockerfile": readReferenceFile(
            STT_REFERENCE_DOCKERFILE,
            required=False,
        ),
    }


# ============================================================
# Generated output parsing
# ============================================================


def extractSection(
    content: str,
    sectionName: str,
) -> str:

    pattern = rf"<{sectionName}>" rf"(.*?)" rf"</{sectionName}>"

    match = re.search(
        pattern,
        content,
        re.DOTALL,
    )

    if not match:

        raise ValueError(
            "Component Creation Agent response " "is missing section: " f"{sectionName}"
        )

    sectionContent = match.group(1).strip()

    if not sectionContent:

        raise ValueError(
            "Component Creation Agent returned " "an empty section: " f"{sectionName}"
        )

    return sectionContent


# ============================================================
# Deterministic component metadata
# ============================================================


def buildComponentName(
    modelFamily: str,
) -> str:

    normalizedFamily = (
        modelFamily.lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    )

    normalizedFamily = re.sub(
        r"[^a-z0-9_]",
        "",
        normalizedFamily,
    )

    return f"stt_inference_{normalizedFamily}"


def buildImageName(
    componentName: str,
) -> str:

    return f"{componentName}:latest"


def buildComponentRelativePath(
    componentName: str,
) -> str:

    return "inference_component/" "stt_inference/" f"{componentName}"


def buildEntryPoint(
    componentName: str,
) -> str:

    # The working EchoForge Docker pattern copies the
    # inference component contents directly into /app.
    #
    # Example:
    #
    # COPY inference_component/stt_inference/<component> .
    #
    # Therefore main.py exists at:
    #
    # /app/main.py

    return "/app/main.py"


# ============================================================
# Reference convention helpers
# ============================================================


def extractBaseInferenceImport(
    referenceMain: str,
) -> str | None:

    lines = referenceMain.splitlines()

    for index, line in enumerate(lines):

        if "BaseInferencePipeline" not in line:

            continue

        strippedLine = line.strip()

        if not strippedLine.startswith("from "):

            continue

        # Single-line import
        if "import BaseInferencePipeline" in strippedLine:

            return strippedLine

        # Multi-line import
        importLines = [strippedLine]

        for nextLine in lines[index + 1 :]:

            importLines.append(nextLine.strip())

            if ")" in nextLine:

                break

        return "\n".join(importLines)

    return None


# ============================================================
# Generated component validation
# ============================================================


def validateGeneratedMain(
    mainFileContent: str,
    referenceMain: str,
):

    # --------------------------------------------------------
    # Required EchoForge interface
    # --------------------------------------------------------

    requiredPatterns = [
        "BaseInferencePipeline",
        "def load_model",
        "def preprocess",
        "def infer",
        "def to_segments",
        'return "stt"',
        ".run()",
    ]

    for pattern in requiredPatterns:

        if pattern not in mainFileContent:

            raise ValueError(
                "Generated main.py is missing "
                "required EchoForge pattern: "
                f"{pattern}"
            )

    # --------------------------------------------------------
    # Reference BaseInferencePipeline import
    # --------------------------------------------------------

    referenceBaseImport = extractBaseInferenceImport(referenceMain)

    if referenceBaseImport:

        referenceImportMatch = re.search(
            r"from\s+([A-Za-z0-9_\.]+)" r"\s+import",
            referenceBaseImport,
        )

        generatedImportMatch = re.search(
            r"from\s+([A-Za-z0-9_\.]+)"
            r"\s+import\s*\(?"
            r"[\s\S]*?"
            r"BaseInferencePipeline",
            mainFileContent,
        )

        if referenceImportMatch and generatedImportMatch:

            referenceModule = referenceImportMatch.group(1)

            generatedModule = generatedImportMatch.group(1)

            if generatedModule != referenceModule:

                raise ValueError(
                    "Generated main.py does not "
                    "follow the BaseInferencePipeline "
                    "import path used by the working "
                    "EchoForge reference component.\n"
                    f"Reference: {referenceModule}\n"
                    f"Generated: {generatedModule}"
                )

    # --------------------------------------------------------
    # Reject obvious placeholder code
    # --------------------------------------------------------

    invalidPatterns = [
        "TODO",
        "NotImplementedError",
    ]

    for pattern in invalidPatterns:

        if pattern in mainFileContent:

            raise ValueError(
                "Generated main.py contains "
                "placeholder implementation: "
                f"{pattern}"
            )


def validateGeneratedDockerfile(
    dockerfileContent: str,
    referenceDockerfile: str,
    componentName: str,
):

    # --------------------------------------------------------
    # Basic Dockerfile validity
    # --------------------------------------------------------

    if "FROM" not in dockerfileContent:

        raise ValueError("Generated Dockerfile is " "missing required pattern: FROM")

    # --------------------------------------------------------
    # Exact generated component path
    # --------------------------------------------------------

    componentRelativePath = buildComponentRelativePath(componentName)

    incorrectComponentPath = "inference_component/" f"{componentName}"

    if incorrectComponentPath in dockerfileContent:

        raise ValueError(
            "Generated Dockerfile uses an "
            "incorrect component path.\n"
            f"Generated: {incorrectComponentPath}\n"
            f"Expected: {componentRelativePath}"
        )

    # --------------------------------------------------------
    # Validate component COPY paths
    # --------------------------------------------------------

    componentCopyLines = [
        line.strip()
        for line in dockerfileContent.splitlines()
        if (line.strip().startswith("COPY ") and componentName in line)
    ]

    for line in componentCopyLines:

        if componentRelativePath not in line:

            raise ValueError(
                "Generated Dockerfile contains "
                "an invalid component COPY path:\n"
                f"{line}\n"
                "Expected component path:\n"
                f"{componentRelativePath}"
            )

    # --------------------------------------------------------
    # Preserve important reference conventions
    # --------------------------------------------------------

    referencePatterns = [
        "WORKDIR",
        "LOCAL_PYTHON",
        "PYTHONPATH",
    ]

    for pattern in referencePatterns:

        if pattern in referenceDockerfile and pattern not in dockerfileContent:

            raise ValueError(
                "Generated Dockerfile does not "
                "follow the working EchoForge "
                "reference convention: "
                f"{pattern}"
            )


# ============================================================
# Prompt
# ============================================================


def buildPrompt(
    componentInput: ComponentCreationInput,
    references: dict,
    componentName: str,
) -> str:

    componentRelativePath = buildComponentRelativePath(componentName)

    requirementsRelativePath = f"{componentRelativePath}/" "requirements.txt"

    return f"""
You are the Component Creation Agent for EchoForge.

Your task is to adapt a known working EchoForge STT inference
component so that it supports a new ASR model.

============================================================
SOURCE OF TRUTH
============================================================

Use all supplied sources together.

PRIORITY 1 - ECHOFORGE DOCUMENTATION

The supplied base classes documentation and developer guide
define the authoritative EchoForge interface and behavioural
contract.

The generated component MUST comply with these documents.

If the working reference component conflicts with the
documentation, follow the documentation.

PRIORITY 2 - WORKING STT REFERENCE COMPONENT

The supplied STT reference component is known to work inside
EchoForge.

Use it as the concrete implementation template for:

- import paths
- package structure
- BaseInferencePipeline usage
- class structure
- method signatures
- ClearML integration
- runtime behaviour
- .run() pattern
- Docker structure
- Docker working-directory assumptions
- Python path conventions
- environment configuration
- dependency installation conventions
- component COPY behaviour
- runtime entry-point layout

Preserve these conventions unless:

1. the EchoForge documentation requires something different, or
2. the target model genuinely requires a model-specific change.

PRIORITY 3 - RESEARCH AGENT OUTPUT

The Research Agent information describes the target model.

Use it for model-specific decisions such as:

- model framework
- model loading
- processor
- tokenizer
- feature extractor
- audio preparation
- inference API
- decoding
- target-model dependencies

============================================================
TARGET MODEL
============================================================

Model name:
{componentInput.modelName}

Model family:
{componentInput.modelFamily}

Model source:
{componentInput.source}

Generated component name:
{componentName}

Research Agent technical profile:

{componentInput.technicalProfile}

============================================================
GENERATED COMPONENT LOCATION
============================================================

The EchoForge Docker build context is:

components/

The generated component WILL exist at this exact location
relative to the Docker build context:

{componentRelativePath}

Its requirements file is:

{requirementsRelativePath}

Do NOT guess or shorten this path.

In particular, do NOT use:

inference_component/{componentName}

because that incorrectly omits:

stt_inference/

============================================================
CONTAINER RUNTIME LAYOUT
============================================================

Follow the working STT reference Docker layout.

The working EchoForge inference-component pattern copies the
contents of the model-specific component directly into /app.

For the generated component, this means a Docker COPY pattern
such as:

COPY {componentRelativePath} .

results in:

/app/main.py
/app/requirements.txt

The ClearML task therefore executes:

/app/main.py

The runtime entry point for this generated component is:

/app/main.py

Do NOT assume that main.py remains at:

/app/{componentRelativePath}/main.py

unless the working reference Dockerfile explicitly preserves
that directory structure.

For this component, follow the reference behaviour and place
the component contents directly under /app.

============================================================
ECHOFORGE BASE CLASSES DOCUMENTATION
============================================================

{references["baseClasses"]}

============================================================
ECHOFORGE DEVELOPER GUIDE
============================================================

{references["developerGuide"]}

============================================================
WORKING STT REFERENCE - main.py
============================================================

{references["referenceMain"]}

============================================================
WORKING STT REFERENCE - requirements.txt
============================================================

{references["referenceRequirements"]}

============================================================
WORKING STT REFERENCE - Dockerfile
============================================================

{references["referenceDockerfile"]}

============================================================
ADAPTATION STRATEGY
============================================================

Start from the working STT reference component.

Do NOT create a completely new EchoForge integration from
scratch.

First determine which parts of the reference are:

1. EchoForge infrastructure
2. reference-model-specific code

Preserve EchoForge infrastructure whenever it remains
compatible with the supplied documentation.

Preserve the same general approach to:

- imports
- BaseInferencePipeline import path
- class inheritance
- model_task
- method signatures
- ClearML behaviour
- runtime environment
- pipeline execution
- Docker structure
- working directory
- Python path behaviour
- component COPY behaviour
- runtime file layout
- .run() behaviour

Only modify parts required for the TARGET MODEL.

Typical model-specific parts include:

- model-library imports
- processor/tokenizer imports
- load_model()
- preprocess()
- infer()
- decoding
- to_segments() where required
- target-model requirements
- target-model system dependencies

Do not change EchoForge infrastructure merely because another
implementation is possible.

============================================================
MAIN.PY REQUIREMENTS
============================================================

The generated main.py must:

- comply with the supplied EchoForge documentation

- preserve the working STT reference component's EchoForge
  structure as closely as possible

- subclass BaseInferencePipeline

- use the same BaseInferencePipeline import path as the working
  reference unless the documentation explicitly requires
  otherwise

- implement the model_task property

- return "stt" from model_task

- implement:

  load_model(model_path, **kwargs)

- load model weights from the local model_path supplied by
  EchoForge

- NOT download model weights again during inference

- implement:

  preprocess(audio_path, item, **kwargs)

- use EchoForge audio-loading utilities according to the
  documentation and working reference

- implement:

  infer(inputs, **kwargs)

- implement:

  to_segments(inferred, **kwargs)

- produce the STT output structure required by EchoForge

- use the correct target-model inference API

- use Research Agent information for target-model-specific
  implementation decisions

- preserve the reference component startup pattern

- contain working implementation code

- not contain TODO blocks

- not contain NotImplementedError

- not invent unsupported target-model APIs

============================================================
REQUIREMENTS.TXT REQUIREMENTS
============================================================

Use the reference requirements as an implementation guide.

Retain dependencies required by EchoForge or by the working
runtime environment.

Remove dependencies that are specific only to the reference
model.

Add dependencies required by the target model.

The generated requirements.txt must:

- match imports used by main.py
- use valid pip-installable package names
- avoid standard-library modules
- avoid unnecessary dependencies

============================================================
DOCKERFILE REQUIREMENTS
============================================================

Use the working reference Dockerfile as the primary template.

Preserve its EchoForge-specific runtime conventions as closely
as possible.

This includes, where present in the reference:

- base-image approach
- environment variables
- LOCAL_PYTHON
- PYTHONPATH
- WORKDIR
- COPY layout
- base_classes COPY
- package-installation approach
- operating-system dependency setup
- runtime file layout

When adapting COPY statements that refer to the model-specific
component, use the exact path:

{componentRelativePath}

For example, if the reference separately copies the component
requirements:

COPY {requirementsRelativePath} requirements.txt

If the reference then copies the component contents into the
working directory:

COPY {componentRelativePath} .

Preserve that behaviour.

Do NOT use:

COPY inference_component/{componentName}/requirements.txt requirements.txt

Do NOT use:

COPY inference_component/{componentName} .

because those paths omit:

stt_inference/

Do NOT unnecessarily redesign:

- Docker COPY strategy
- Python path strategy
- working directory
- runtime source layout
- ClearML integration

Only modify Docker behaviour when required by:

- target-model system dependencies
- target-model Python dependencies
- EchoForge documentation

============================================================
IMPORTANT REASONING RULE
============================================================

Before generating the files, reason internally about:

1. Which parts of the working reference are EchoForge
   infrastructure?
2. Which parts are reference-model-specific?
3. Which parts are explicitly required by EchoForge
   documentation?
4. Which parts must change for the target model?
5. What is the exact generated component path?
6. Where does the Dockerfile place main.py inside the
   container?

Then:

Preserve infrastructure.

Respect documentation.

Use the deterministic component path supplied above.

Preserve the working runtime layout.

Replace only model-specific logic.

============================================================
OUTPUT FORMAT
============================================================

Return EXACTLY these three sections:

<MAIN_PY>
complete contents of main.py
</MAIN_PY>

<REQUIREMENTS>
complete contents of requirements.txt
</REQUIREMENTS>

<DOCKERFILE>
complete contents of Dockerfile
</DOCKERFILE>

============================================================
STRICT OUTPUT RULES
============================================================

- Do not return JSON.
- Do not use Markdown code fences.
- Do not add explanations before <MAIN_PY>.
- Do not add explanations after </DOCKERFILE>.
- Do not write filenames outside the section markers.
- Do not omit any section.
"""


# ============================================================
# Component Creation Agent
# ============================================================


def componentCreationAgent(
    componentInput: ComponentCreationInput,
) -> ComponentCreationOutput:

    print(
        "[Component Creation Agent] "
        "Starting component generation: "
        f"{componentInput.modelName}"
    )

    # --------------------------------------------------------
    # 1. Load EchoForge references
    # --------------------------------------------------------

    print("[Component Creation Agent] " "Loading local EchoForge references.")

    references = loadComponentReferences()

    print("[Component Creation Agent] " "References loaded.")

    # --------------------------------------------------------
    # 2. Resolve deterministic metadata
    # --------------------------------------------------------

    componentName = buildComponentName(componentInput.modelFamily)

    componentRelativePath = buildComponentRelativePath(componentName)

    imageName = buildImageName(componentName)

    entryPoint = buildEntryPoint(componentName)

    print("[Component Creation Agent] " "Component name: " f"{componentName}")

    print("[Component Creation Agent] " "Component path: " f"{componentRelativePath}")

    print("[Component Creation Agent] " "Entry point: " f"{entryPoint}")

    # --------------------------------------------------------
    # 3. Build adaptation prompt
    # --------------------------------------------------------

    prompt = buildPrompt(
        componentInput=componentInput,
        references=references,
        componentName=componentName,
    )

    # --------------------------------------------------------
    # 4. Call LLM
    # --------------------------------------------------------

    print("[Component Creation Agent] " "Calling LLM.")

    llm = getLLM()

    response = llm.invoke(prompt)

    if hasattr(
        response,
        "content",
    ):

        content = response.content

    else:

        content = str(response)

    if not isinstance(
        content,
        str,
    ):

        content = str(content)

    print("[Component Creation Agent] " "LLM generation completed.")

    # --------------------------------------------------------
    # 5. Parse generated files
    # --------------------------------------------------------

    try:

        mainFileContent = extractSection(
            content,
            "MAIN_PY",
        )

        requirementsContent = extractSection(
            content,
            "REQUIREMENTS",
        )

        dockerfileContent = extractSection(
            content,
            "DOCKERFILE",
        )

    except Exception:

        print()
        print("[Component Creation Agent] " "Unable to parse generated response.")

        print("[Component Creation Agent] " "Raw response preview:")

        print("-" * 70)

        print(content[:3000])

        print("-" * 70)

        raise

    print("[Component Creation Agent] " "Generated files parsed successfully.")

    # --------------------------------------------------------
    # 6. Validate EchoForge conventions
    # --------------------------------------------------------

    validateGeneratedMain(
        mainFileContent=mainFileContent,
        referenceMain=references["referenceMain"],
    )

    validateGeneratedDockerfile(
        dockerfileContent=dockerfileContent,
        referenceDockerfile=references["referenceDockerfile"],
        componentName=componentName,
    )

    print("[Component Creation Agent] " "Generated component validation passed.")

    # --------------------------------------------------------
    # 7. Build structured result
    # --------------------------------------------------------

    result = ComponentCreationOutput(
        componentName=componentName,
        mainFileContent=mainFileContent,
        requirementsContent=requirementsContent,
        dockerfileContent=dockerfileContent,
        imageName=imageName,
        # Component contents are copied directly
        # into /app by the EchoForge Dockerfile.
        entryPoint=entryPoint,
        reasoning=(
            "Adapted from a working EchoForge "
            "STT inference component while "
            "respecting EchoForge documentation, "
            "the deterministic component path, "
            "the working Docker/runtime layout, "
            "and Research Agent technical "
            "information."
        ),
    )

    print("[Component Creation Agent] " "Component generated: " f"{componentName}")

    return result
