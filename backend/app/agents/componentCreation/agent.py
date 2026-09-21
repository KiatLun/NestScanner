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


def buildEntryPoint(
    componentName: str,
) -> str:

    return "/app/inference_component/" "stt_inference/" f"{componentName}/main.py"


# ============================================================
# Prompt
# ============================================================


def buildPrompt(
    componentInput: ComponentCreationInput,
    references: dict,
    componentName: str,
) -> str:

    requirementsPath = (
        "/app/inference_component/" "stt_inference/" f"{componentName}/requirements.txt"
    )

    mainPath = "/app/inference_component/" "stt_inference/" f"{componentName}/main.py"

    dockerfileRelativePath = (
        "inference_component/" "stt_inference/" f"{componentName}/Dockerfile"
    )

    return f"""
You are the Component Creation Agent for EchoForge.

Your task is to create a complete automatic speech recognition
inference component for the target model.

============================================================
SOURCE OF TRUTH PRIORITY
============================================================

Use the following priority when making implementation decisions:

1. EchoForge base classes documentation
2. EchoForge developer guide
3. Research Agent technical profile
4. Existing STT reference component

The base classes documentation and developer guide describe
the EchoForge contract and must be treated as authoritative.

The reference STT component is only an implementation example.

Do not copy model-specific logic from the reference component
unless it is appropriate for the target model.

============================================================
TARGET MODEL
============================================================

Model name:
{componentInput.modelName}

Model family:
{componentInput.modelFamily}

Model source:
{componentInput.source}

Research Agent technical profile:
{componentInput.technicalProfile}

============================================================
GENERATED COMPONENT
============================================================

Component name:
{componentName}

Generated main.py location inside the container:
{mainPath}

Generated requirements.txt location inside the container:
{requirementsPath}

Generated Dockerfile location relative to the EchoForge
components directory:
{dockerfileRelativePath}

============================================================
ECHOFORGE BASE CLASSES DOCUMENTATION
============================================================

{references["baseClasses"]}

============================================================
ECHOFORGE DEVELOPER GUIDE
============================================================

{references["developerGuide"]}

============================================================
REFERENCE STT COMPONENT - main.py
============================================================

{references["referenceMain"]}

============================================================
REFERENCE STT COMPONENT - requirements.txt
============================================================

{references["referenceRequirements"]}

============================================================
REFERENCE STT COMPONENT - Dockerfile
============================================================

{references["referenceDockerfile"]}

============================================================
TASK
============================================================

Generate a new EchoForge STT inference component for the
TARGET MODEL.

The generated implementation must follow the interfaces,
methods, behaviour, and conventions described by the supplied
EchoForge documentation.

============================================================
MAIN.PY REQUIREMENTS
============================================================

main.py must:

- use the EchoForge inference base class described in the
  supplied base classes documentation

- implement the required STT inference interface

- implement the model_task property

- return "stt" from model_task

- implement:

  load_model(model_path, **kwargs)

- load the model from the local model_path supplied by
  EchoForge

- NOT download model weights again during inference

- implement:

  preprocess(audio_path, item, **kwargs)

- use the EchoForge safe audio loading method where required
  by the supplied base class documentation

- implement:

  infer(inputs, **kwargs)

- implement:

  to_segments(inferred, **kwargs)

- return results in the STT output format expected by
  EchoForge

- use the correct inference framework and model API based on
  the Research Agent technical profile

- call .run() when the script is executed directly

- contain working implementation code

- not contain placeholder logic

- not contain TODO blocks

- not invent unsupported APIs

============================================================
REQUIREMENTS.TXT REQUIREMENTS
============================================================

requirements.txt must:

- include all model-specific packages required by main.py

- include the correct inference framework

- contain valid pip-installable package names

- avoid Python standard-library modules

- avoid unnecessary dependencies

============================================================
DOCKER BUILD CONTEXT
============================================================

IMPORTANT:

The Docker build context is the EchoForge:

components/

directory.

The generated Dockerfile itself will be located at:

components/{dockerfileRelativePath}

Therefore ALL Docker COPY source paths are relative to the
components directory, NOT relative to the generated component
folder.

Do NOT use:

COPY requirements.txt requirements.txt

because requirements.txt is not at the Docker build-context
root.

The preferred pattern is:

COPY . /app

This copies the EchoForge components directory into /app.

After that, the generated component will exist at:

{mainPath}

and its requirements file will exist at:

{requirementsPath}

============================================================
DOCKERFILE REQUIREMENTS
============================================================

Dockerfile must:

- use an appropriate Python base image

- install required operating-system dependencies if necessary

- set:

  ENV DEBIAN_FRONTEND=noninteractive
  ENV PYTHONUNBUFFERED=1
  ENV PIP_NO_CACHE_DIR=1
  ENV LOCAL_PYTHON=python3

- use:

  WORKDIR /app

- copy the entire EchoForge components build context using:

  COPY . /app

- install clearml

- install clearml-agent

- install the generated component requirements using exactly
  this path:

  {requirementsPath}

- NOT use:

  COPY requirements.txt requirements.txt

- NOT assume the Docker build context is the generated
  component directory

- preserve the EchoForge directory structure inside /app

A valid pattern is:

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV LOCAL_PYTHON=python3

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \\
    pip install clearml clearml-agent && \\
    pip install -r {requirementsPath}

Add operating-system dependencies before the Python package
installation if the model requires them.

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
- Do not use ```python.
- Do not use ```dockerfile.
- Do not add explanations before <MAIN_PY>.
- Do not add explanations after </DOCKERFILE>.
- Do not write filenames outside the section tags.
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
    # 1. Load local EchoForge references
    # --------------------------------------------------------

    print("[Component Creation Agent] " "Loading local EchoForge references.")

    references = loadComponentReferences()

    print("[Component Creation Agent] " "References loaded.")

    # --------------------------------------------------------
    # 2. Resolve deterministic metadata
    # --------------------------------------------------------

    componentName = buildComponentName(componentInput.modelFamily)

    imageName = buildImageName(componentName)

    entryPoint = buildEntryPoint(componentName)

    print("[Component Creation Agent] " "Component name: " f"{componentName}")

    # --------------------------------------------------------
    # 3. Build prompt
    # --------------------------------------------------------

    prompt = buildPrompt(
        componentInput=componentInput,
        references=references,
        componentName=componentName,
    )

    # --------------------------------------------------------
    # 4. Generate component
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
    # 6. Basic generated-content validation
    # --------------------------------------------------------

    if "COPY requirements.txt" in dockerfileContent:

        raise ValueError(
            "Generated Dockerfile uses "
            "'COPY requirements.txt', "
            "which is invalid for the "
            "EchoForge components build context."
        )

    if "COPY . /app" not in dockerfileContent:

        raise ValueError(
            "Generated Dockerfile must copy "
            "the EchoForge components context "
            "using 'COPY . /app'."
        )

    expectedRequirementsPath = (
        "/app/inference_component/" "stt_inference/" f"{componentName}/requirements.txt"
    )

    if expectedRequirementsPath not in dockerfileContent:

        raise ValueError(
            "Generated Dockerfile does not "
            "install the component requirements "
            "from the expected EchoForge path: "
            f"{expectedRequirementsPath}"
        )

    print("[Component Creation Agent] " "Generated Dockerfile validation passed.")

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
            "Generated using local EchoForge "
            "base classes documentation, "
            "developer guide, Research Agent "
            "technical profile, and STT "
            "reference component."
        ),
    )

    print("[Component Creation Agent] " "Component generated: " f"{componentName}")

    return result
