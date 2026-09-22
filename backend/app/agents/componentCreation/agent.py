from pathlib import Path
import os
import platform
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

BASE_CLASSES_FILE = (
    REFERENCE_DIR
    / "base_classes.md"
)

DEVELOPER_GUIDE_FILE = (
    REFERENCE_DIR
    / "developer_guide.md"
)

STT_REFERENCE_DIR = (
    REFERENCE_DIR
    / "stt_reference"
)

STT_REFERENCE_MAIN_FILE = (
    STT_REFERENCE_DIR
    / "main.py"
)

STT_REFERENCE_REQUIREMENTS_FILE = (
    STT_REFERENCE_DIR
    / "requirements.txt"
)

STT_REFERENCE_DOCKERFILE = (
    STT_REFERENCE_DIR
    / "Dockerfile"
)


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
                "Required Component Creation "
                f"reference not found: {path}"
            )

        return ""

    return path.read_text(
        encoding="utf-8"
    )


def loadComponentReferences() -> dict:

    return {
        "baseClasses": readReferenceFile(
            BASE_CLASSES_FILE
        ),
        "developerGuide": readReferenceFile(
            DEVELOPER_GUIDE_FILE
        ),
        "referenceMain": readReferenceFile(
            STT_REFERENCE_MAIN_FILE
        ),
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

    pattern = (
        rf"<{sectionName}>"
        rf"(.*?)"
        rf"</{sectionName}>"
    )

    match = re.search(
        pattern,
        content,
        re.DOTALL,
    )

    if not match:

        raise ValueError(
            "Component Creation Agent response "
            "is missing section: "
            f"{sectionName}"
        )

    sectionContent = (
        match.group(1)
        .strip()
    )

    if not sectionContent:

        raise ValueError(
            "Component Creation Agent returned "
            "an empty section: "
            f"{sectionName}"
        )

    return sectionContent


# ============================================================
# Deterministic component metadata
# ============================================================


def buildComponentName(
    modelFamily: str,
) -> str:

    normalizedFamily = (
        modelFamily
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )

    normalizedFamily = re.sub(
        r"[^a-z0-9_]",
        "",
        normalizedFamily,
    )

    return (
        f"stt_inference_"
        f"{normalizedFamily}"
    )


def buildImageName(
    componentName: str,
) -> str:

    return (
        f"{componentName}:latest"
    )


def buildComponentRelativePath(
    componentName: str,
) -> str:

    return (
        "inference_component/"
        "stt_inference/"
        f"{componentName}"
    )


def buildEntryPoint(
    componentName: str,
) -> str:

    # EchoForge copies the contents of:
    #
    # inference_component/stt_inference/<component>
    #
    # directly into /app.
    #
    # Therefore:
    #
    # /app/main.py

    return "/app/main.py"


# ============================================================
# Deterministic Pattern A Docker generation
# ============================================================


def extractReferenceBaseImage(
    referenceDockerfile: str,
) -> str:

    for line in referenceDockerfile.splitlines():

        strippedLine = line.strip()

        if strippedLine.startswith("FROM "):

            return (
                strippedLine
                .removeprefix("FROM ")
                .strip()
            )

    raise ValueError(
        "Working EchoForge reference Dockerfile "
        "does not contain a FROM instruction."
    )


def extractReferenceLocalPython(
    referenceDockerfile: str,
) -> str:

    for line in referenceDockerfile.splitlines():

        strippedLine = line.strip()

        if strippedLine.startswith(
            "ENV LOCAL_PYTHON="
        ):

            return strippedLine

    return (
        "ENV LOCAL_PYTHON=/usr/bin/python3"
    )


def normalizeOptionalSection(
    content: str,
) -> str:

    normalized = (
        content.strip()
    )

    if normalized.upper() in {
        "",
        "NONE",
        "DEFAULT",
        "N/A",
    }:

        return ""

    return normalized


def parseSystemPackages(
    content: str,
) -> list[str]:

    normalized = (
        normalizeOptionalSection(
            content
        )
    )

    if not normalized:
        return []

    packages = []

    for rawLine in (
        normalized.splitlines()
    ):

        line = (
            rawLine
            .strip()
            .lstrip("-")
            .strip()
        )

        if not line:
            continue

        for package in line.split():

            if not re.fullmatch(
                r"[A-Za-z0-9_.+\-]+",
                package,
            ):

                raise ValueError(
                    "Invalid generated system "
                    "package name: "
                    f"{package}"
                )

            packages.append(
                package
            )

    return packages


def parseDockerCommands(
    content: str,
) -> list[str]:

    normalized = (
        normalizeOptionalSection(
            content
        )
    )

    if not normalized:
        return []

    commands = []

    for rawLine in (
        normalized.splitlines()
    ):

        command = (
            rawLine.strip()
        )

        if not command:
            continue

        if command.startswith("- "):
            command = (
                command[2:]
                .strip()
            )

        if not command:
            continue

        invalidTokens = [
            "COPY ",
            "ADD ",
            "FROM ",
            "WORKDIR ",
            "ENTRYPOINT ",
            "CMD ",
            "ENV LOCAL_PYTHON",
        ]

        for invalidToken in (
            invalidTokens
        ):

            if command.startswith(
                invalidToken
            ):

                raise ValueError(
                    "Model-specific Docker setup "
                    "must not override EchoForge "
                    "Docker structure: "
                    f"{command}"
                )

        if command.startswith("RUN "):

            command = (
                command
                .removeprefix("RUN ")
                .strip()
            )

        commands.append(
            command
        )

    return commands


def buildPatternADockerfile(
    componentName: str,
    references: dict,
    baseImageOverride: str = "",
    systemPackagesContent: str = "",
    preRequirementsCommandsContent: str = "",
) -> str:

    componentRelativePath = (
        buildComponentRelativePath(
            componentName
        )
    )

    requirementsRelativePath = (
        f"{componentRelativePath}/"
        "requirements.txt"
    )

    referenceDockerfile = (
        references[
            "referenceDockerfile"
        ]
    )

    referenceBaseImage = (
        extractReferenceBaseImage(
            referenceDockerfile
        )
    )

    localPythonLine = (
        extractReferenceLocalPython(
            referenceDockerfile
        )
    )

    baseImageOverride = (
        normalizeOptionalSection(
            baseImageOverride
        )
    )

    baseImage = (
        baseImageOverride
        or referenceBaseImage
    )

    systemPackages = (
        parseSystemPackages(
            systemPackagesContent
        )
    )

    preRequirementsCommands = (
        parseDockerCommands(
            preRequirementsCommandsContent
        )
    )

    aptPackages = [
        "libsndfile1",
        "python3-pip",
    ]

    for package in (
        systemPackages
    ):

        if package not in aptPackages:
            aptPackages.append(
                package
            )

    aptPackageText = (
        " \\\n        ".join(
            aptPackages
        )
    )

    dockerLines = [
        f"FROM {baseImage}",
        "",
        "RUN apt-get update \\",
        "    && apt-get install -y \\",
        f"        {aptPackageText} \\",
        "    && apt-get clean \\",
        "    && rm -rf /var/lib/apt/lists/*",
        "",
        "WORKDIR /app",
        "",
        "COPY base_classes/requirements.txt requirements_base.txt",
        "",
        (
            "RUN python3 -m pip install "
            "--no-cache-dir "
            "-r requirements_base.txt"
        ),
        "",
    ]

    for command in (
        preRequirementsCommands
    ):

        dockerLines.extend(
            [
                f"RUN {command}",
                "",
            ]
        )

    dockerLines.extend(
        [
            (
                "COPY "
                f"{requirementsRelativePath} "
                "requirements.txt"
            ),
            "",
            (
                "RUN python3 -m pip install "
                "--no-cache-dir "
                "-r requirements.txt"
            ),
            "",
            "COPY base_classes base_classes",
            (
                "COPY inference_component/"
                "stt_inference/stt_inference.py ."
            ),
            (
                f"COPY {componentRelativePath} ."
            ),
            "",
            localPythonLine,
            "",
        ]
    )

    return "\n".join(
        dockerLines
    )


# ============================================================
# Target runtime profile
# ============================================================


def buildRuntimeProfile() -> str:

    targetArchitecture = (
        os.getenv(
            "NESTSCANNER_TARGET_ARCHITECTURE",
            platform.machine(),
        )
        .strip()
        .lower()
    )

    targetPlatform = (
        os.getenv(
            "NESTSCANNER_TARGET_PLATFORM",
            "linux",
        )
        .strip()
        .lower()
    )

    gpuMode = (
        os.getenv(
            "NESTSCANNER_GPU_MODE",
            "unknown",
        )
        .strip()
        .lower()
    )

    if targetArchitecture in {
        "arm64",
        "aarch64",
    }:

        architectureGuidance = (
            "The target architecture is ARM64/aarch64. "
            "Do not assume x86_64-only wheels are available. "
            "Packages such as torch, torchaudio, torchvision, "
            "onnxruntime, flash-attn, and other compiled ML "
            "libraries must be checked for ARM64-compatible "
            "installation."
        )

    elif targetArchitecture in {
        "x86_64",
        "amd64",
    }:

        architectureGuidance = (
            "The target architecture is x86_64/amd64. "
            "Do not assume CUDA support merely because the "
            "architecture is x86_64."
        )

    else:

        architectureGuidance = (
            "The target architecture is not a common "
            "x86_64/ARM64 value. Treat compiled dependencies "
            "as platform-sensitive and avoid architecture "
            "assumptions."
        )

    gpuGuidance = (
        "NVIDIA GPU availability is not guaranteed. "
        "Prefer a CPU-compatible dependency installation "
        "when the model supports CPU inference, unless the "
        "runtime profile or implementation evidence clearly "
        "requires GPU execution."
    )

    if gpuMode in {
        "cuda",
        "nvidia",
        "gpu",
    }:

        gpuGuidance = (
            "The runtime is configured for NVIDIA CUDA. "
            "Use CUDA-compatible packages only when supported "
            "by the implementation evidence and target image."
        )

    elif gpuMode in {
        "cpu",
        "cpu-only",
        "none",
    }:

        gpuGuidance = (
            "The runtime is CPU-only. Do not install "
            "CUDA-only packages or assume NVIDIA GPU access."
        )

    return (
        f"Target container platform: {targetPlatform}\n"
        f"Target architecture: {targetArchitecture}\n"
        f"GPU mode: {gpuMode}\n\n"
        f"{architectureGuidance}\n\n"
        f"{gpuGuidance}\n\n"
        "The component runs inside Docker. Host-specific "
        "features such as Apple Metal/MPS are not automatically "
        "available inside a Linux container."
    )


# ============================================================
# Prompt
# ============================================================


def buildPrompt(
    componentInput: ComponentCreationInput,
    references: dict,
    componentName: str,
) -> str:

    runtimeProfile = (
        buildRuntimeProfile()
    )

    referenceDockerfile = (
        references[
            "referenceDockerfile"
        ]
    )

    return f"""
You are the EchoForge STT Component Creation Agent.

Generate the MODEL-SPECIFIC parts of a new Pattern A
EchoForge STT inference component.

EchoForge Docker structure is generated deterministically by
Python. Do NOT generate a complete Dockerfile.

============================================================
SOURCE PRIORITY
============================================================

1. EchoForge Pattern A rules below
2. official target-model implementation evidence
3. Research Agent technical profile
4. working EchoForge references

Do not invent target-model APIs.

============================================================
TARGET
============================================================

Model:
{componentInput.modelName}

Family:
{componentInput.modelFamily}

Source:
{componentInput.source}

Component:
{componentName}

============================================================
IMPLEMENTATION EVIDENCE
============================================================

{componentInput.implementationContext}

============================================================
TECHNICAL PROFILE
============================================================

{componentInput.technicalProfile}

============================================================
TARGET RUNTIME
============================================================

{runtimeProfile}

============================================================
PATTERN A MAIN.PY
============================================================

main.py MUST import:

from stt_inference import SttInferencePipeline

The generated class MUST subclass:

SttInferencePipeline

Normally implement only:

- __init__() when model-specific configuration is needed
- load_model(model_path, **kwargs)
- infer_segment(segment, sr=16000)

Do NOT implement:

- model_task
- preprocess()
- infer()
- to_segments()

load_model() MUST use the local model_path supplied by
EchoForge.

Do not redownload model weights or replace model_path with a
remote model identifier.

infer_segment() receives:

- segment: numpy waveform
- sr: sample rate

and MUST return transcription text.

main.py MUST end with:

if __name__ == "__main__":
    <GeneratedClassName>(
        "echoforge",
        "{componentName}",
    ).run()

Never import from:

components.*
inference_component.*

Do not import BaseInferencePipeline directly.

============================================================
DEPENDENCIES
============================================================

Generate requirements.txt containing ordinary target-model
runtime dependencies.

Do not include standard-library modules.

Do not invent package names for repository-local modules.

Platform-sensitive dependencies such as torch, torchaudio,
torchvision, CUDA packages, flash-attn, or special framework
wheels may require explicit installation before
requirements.txt.

If such packages need special installation, place the command
in PRE_REQUIREMENTS_COMMANDS and OMIT those packages from
requirements.txt to avoid duplicate installation.

Use official framework/vendor package indexes only when
supported by implementation evidence.

============================================================
DETERMINISTIC DOCKER CUSTOMIZATION
============================================================

Python will construct the final Dockerfile from the working
EchoForge Pattern A template.

The working reference Dockerfile is:

{referenceDockerfile}

You only specify deviations.

BASE_IMAGE:

Return DEFAULT unless the target model genuinely requires a
different base image supported by evidence.

If different, return only the image value, for example:

nvidia/cuda:12.8.0-devel-ubuntu22.04

SYSTEM_PACKAGES:

Return NONE when no additional apt packages are required.

Otherwise return only additional apt package names.
Do not include libsndfile1 or python3-pip because the
deterministic template already installs them.

PRE_REQUIREMENTS_COMMANDS:

Return NONE when no extra setup is needed.

Otherwise return one shell command per line that must run after
EchoForge base requirements are installed and before the
target requirements file is installed.

Examples of appropriate use:

python3 -m pip install torch==... torchaudio==... --index-url ...
python3 -m pip install packaging==24.2
git clone ...

Do NOT emit Docker structural instructions such as:

FROM
COPY
WORKDIR
ENV LOCAL_PYTHON
ENTRYPOINT
CMD

Python owns those instructions.

============================================================
WORKING MAIN.PY REFERENCE
============================================================

{references["referenceMain"]}

============================================================
OUTPUT
============================================================

Return EXACTLY these five sections:

<MAIN_PY>
complete main.py
</MAIN_PY>

<REQUIREMENTS>
complete requirements.txt
</REQUIREMENTS>

<BASE_IMAGE>
DEFAULT or exact base image
</BASE_IMAGE>

<SYSTEM_PACKAGES>
NONE or package names
</SYSTEM_PACKAGES>

<PRE_REQUIREMENTS_COMMANDS>
NONE or one command per line
</PRE_REQUIREMENTS_COMMANDS>

Do not return JSON.
Do not use Markdown code fences.
Do not add text outside these sections.
"""


# ============================================================
# Component Creation Agent
# ============================================================


def componentCreationAgent(
    componentInput: ComponentCreationInput,
) -> ComponentCreationOutput:

    print()
    print("=" * 60)

    print(
        "[Component Creation Agent] "
        "Starting component generation: "
        f"{componentInput.modelName}"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # 1. Load EchoForge references
    # --------------------------------------------------------

    print(
        "[Component Creation Agent] "
        "Loading local EchoForge references."
    )

    references = (
        loadComponentReferences()
    )

    print(
        "[Component Creation Agent] "
        "References loaded."
    )

    # --------------------------------------------------------
    # 2. Resolve deterministic metadata
    # --------------------------------------------------------

    componentName = (
        buildComponentName(
            componentInput.modelFamily
        )
    )

    componentRelativePath = (
        buildComponentRelativePath(
            componentName
        )
    )

    imageName = (
        buildImageName(
            componentName
        )
    )

    entryPoint = (
        buildEntryPoint(
            componentName
        )
    )

    print(
        "[Component Creation Agent] "
        f"Component name: {componentName}"
    )

    print(
        "[Component Creation Agent] "
        "Component path: "
        f"{componentRelativePath}"
    )

    print(
        "[Component Creation Agent] "
        f"Entry point: {entryPoint}"
    )

    print(
        "[Component Creation Agent] "
        "Implementation context size: "
        f"{len(componentInput.implementationContext)} "
        "characters"
    )

    runtimeProfile = (
        buildRuntimeProfile()
    )

    print(
        "[Component Creation Agent] "
        "Target runtime:"
    )

    print(
        runtimeProfile
    )

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

    print(
        "[Component Creation Agent] "
        "Calling LLM."
    )

    llm = getLLM()

    response = llm.invoke(
        prompt
    )

    if hasattr(
        response,
        "content",
    ):

        content = response.content

    else:

        content = str(
            response
        )

    if not isinstance(
        content,
        str,
    ):

        content = str(
            content
        )

    print(
        "[Component Creation Agent] "
        "LLM generation completed."
    )

    # --------------------------------------------------------
    # 5. Parse generated files
    # --------------------------------------------------------

    try:

        mainFileContent = (
            extractSection(
                content,
                "MAIN_PY",
            )
        )

        requirementsContent = (
            extractSection(
                content,
                "REQUIREMENTS",
            )
        )

        baseImageOverride = (
            extractSection(
                content,
                "BASE_IMAGE",
            )
        )

        systemPackagesContent = (
            extractSection(
                content,
                "SYSTEM_PACKAGES",
            )
        )

        preRequirementsCommandsContent = (
            extractSection(
                content,
                "PRE_REQUIREMENTS_COMMANDS",
            )
        )

    except Exception:

        print()
        print(
            "[Component Creation Agent] "
            "Unable to parse generated response."
        )

        print(
            "[Component Creation Agent] "
            "Raw response preview:"
        )

        print("-" * 70)

        print(
            content[:3000]
        )

        print("-" * 70)

        raise

    print(
        "[Component Creation Agent] "
        "Generated model-specific output "
        "parsed successfully."
    )

    # --------------------------------------------------------
    # 6. Build deterministic Pattern A Dockerfile
    # --------------------------------------------------------

    dockerfileContent = (
        buildPatternADockerfile(
            componentName=componentName,
            references=references,
            baseImageOverride=(
                baseImageOverride
            ),
            systemPackagesContent=(
                systemPackagesContent
            ),
            preRequirementsCommandsContent=(
                preRequirementsCommandsContent
            ),
        )
    )

    print(
        "[Component Creation Agent] "
        "Deterministic Pattern A "
        "Dockerfile created."
    )

    # --------------------------------------------------------
    # 7. Build structured result
    # --------------------------------------------------------

    result = (
        ComponentCreationOutput(
            componentName=componentName,
            mainFileContent=(
                mainFileContent
            ),
            requirementsContent=(
                requirementsContent
            ),
            dockerfileContent=(
                dockerfileContent
            ),
            imageName=imageName,
            entryPoint=entryPoint,
            reasoning=(
                "Generated Pattern A model-specific "
                "inference logic from official "
                "implementation evidence and built "
                "the EchoForge Dockerfile "
                "deterministically from the working "
                "runtime template."
            ),
        )
    )

    print(
        "[Component Creation Agent] "
        "Component generated: "
        f"{componentName}"
    )

    return result