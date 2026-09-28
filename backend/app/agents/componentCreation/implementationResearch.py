import json
import os

from pathlib import Path
from urllib.parse import urlparse

import requests

from app.llm.client import getLLM

from app.tools.github import (
    getGitHubRepository,
    getGitHubRepositoryFiles,
    getGitHubFileContent,
)


# ============================================================
# Configuration
# ============================================================


MAX_FILE_CHARS = 12000

MAX_CONTEXT_CHARS = 50000

MAX_FILES = 8


CACHE_DIR = (
    Path(__file__).resolve().parent
    / ".cache"
)


# ============================================================
# Cache helpers
# ============================================================


def normalizeCacheName(
    modelFamily: str,
) -> str:

    normalizedName = (
        modelFamily
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )

    return normalizedName


def getImplementationCacheFile(
    modelFamily: str,
) -> Path:

    cacheName = (
        normalizeCacheName(
            modelFamily
        )
    )

    return (
        CACHE_DIR
        / f"{cacheName}.json"
    )


def loadImplementationCache(
    modelFamily: str,
) -> dict | None:

    cacheFile = (
        getImplementationCacheFile(
            modelFamily
        )
    )

    if not cacheFile.exists():

        return None

    try:

        with cacheFile.open(
            "r",
            encoding="utf-8",
        ) as file:

            cachedResult = (
                json.load(
                    file
                )
            )

    except Exception as error:

        print(
            "[Implementation Research] "
            "Unable to read implementation "
            f"cache: {error}"
        )

        return None

    return cachedResult


def saveImplementationCache(
    modelFamily: str,
    result: dict,
):

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cacheFile = (
        getImplementationCacheFile(
            modelFamily
        )
    )

    with cacheFile.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print(
        "[Implementation Research] "
        "Implementation research cached: "
        f"{cacheFile}"
    )


# ============================================================
# Source parsing
# ============================================================


def parseGithubSource(
    source: str,
) -> tuple[str, str] | None:

    if "github.com" not in source.lower():

        return None

    parsed = urlparse(
        source
    )

    pathParts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if len(pathParts) < 2:

        return None

    owner = pathParts[0]

    repository = (
        pathParts[1]
        .removesuffix(".git")
    )

    return (
        owner,
        repository,
    )


def parseHuggingFaceSource(
    source: str,
) -> str | None:

    source = source.strip()

    if (
        "huggingface.co"
        in source.lower()
    ):

        parsed = urlparse(
            source
        )

        pathParts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if len(pathParts) < 2:

            return None

        return (
            f"{pathParts[0]}/"
            f"{pathParts[1]}"
        )

    if (
        "/" in source
        and not source.startswith(
            "http"
        )
    ):

        parts = (
            source.split("/")
        )

        if len(parts) == 2:

            return source

    return None


# ============================================================
# Implementation file ranking
# ============================================================


def scoreImplementationFile(
    path: str,
) -> int:

    normalizedPath = (
        path.lower()
    )

    fileName = (
        normalizedPath
        .split("/")[-1]
    )

    score = 0

    exactNames = {
        "inference.py": 150,
        "infer.py": 150,
        "infer_vllm.py": 140,
        "infer_vllm_streaming.py": 140,
        "transcribe.py": 145,
        "predict.py": 130,
        "demo.py": 120,
        "example.py": 110,
        "readme.md": 120,
        "requirements.txt": 110,
        "pyproject.toml": 100,
        "setup.py": 95,
        "pipeline.py": 90,
        "model.py": 80,
    }

    score += exactNames.get(
        fileName,
        0,
    )

    keywordScores = {
        "inference": 70,
        "infer": 65,
        "transcribe": 70,
        "predict": 55,
        "recognize": 50,
        "decode": 40,
        "asr": 40,
        "speech": 30,
        "audio": 25,
        "processor": 35,
        "tokenizer": 30,
        "feature": 20,
        "model": 20,
        "demo": 40,
        "example": 35,
    }

    for (
        keyword,
        keywordScore,
    ) in keywordScores.items():

        if (
            keyword
            in normalizedPath
        ):

            score += (
                keywordScore
            )

    usefulExtensions = (
        ".py",
        ".md",
        ".txt",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
    )

    if not normalizedPath.endswith(
        usefulExtensions
    ):

        return 0

    unwantedPaths = (
        "/tests/",
        "/test/",
        "/docs/_build/",
        "/node_modules/",
        "/.github/",
        "/benchmark/",
        "/benchmarks/",
    )

    normalizedWithRoot = (
        f"/{normalizedPath}"
    )

    for unwantedPath in (
        unwantedPaths
    ):

        if (
            unwantedPath
            in normalizedWithRoot
        ):

            score -= 50

    return score


def selectImplementationFiles(
    paths: list[str],
) -> list[str]:

    scoredPaths = []

    for path in paths:

        score = (
            scoreImplementationFile(
                path
            )
        )

        if score <= 0:

            continue

        scoredPaths.append(
            (
                score,
                path,
            )
        )

    scoredPaths.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    selectedPaths = []

    for _, path in scoredPaths:

        if path in selectedPaths:

            continue

        selectedPaths.append(
            path
        )

        if (
            len(selectedPaths)
            >= MAX_FILES
        ):

            break

    return selectedPaths


# ============================================================
# GitHub implementation evidence
# ============================================================


def collectGithubEvidence(
    source: str,
) -> list[dict]:

    parsedSource = (
        parseGithubSource(
            source
        )
    )

    if parsedSource is None:

        return []

    (
        owner,
        repository,
    ) = parsedSource

    print(
        "[Implementation Research] "
        "Inspecting GitHub repository: "
        f"{owner}/{repository}"
    )

    repositoryInfo = (
        getGitHubRepository(
            owner=owner,
            repository=repository,
        )
    )

    branch = (
        repositoryInfo.get(
            "default_branch",
            "main",
        )
    )

    print(
        "[Implementation Research] "
        f"Default branch: {branch}"
    )

    paths = (
        getGitHubRepositoryFiles(
            owner=owner,
            repository=repository,
            branch=branch,
        )
    )

    print(
        "[Implementation Research] "
        f"Repository files found: "
        f"{len(paths)}"
    )

    selectedPaths = (
        selectImplementationFiles(
            paths
        )
    )

    print(
        "[Implementation Research] "
        f"Selected implementation files: "
        f"{len(selectedPaths)}"
    )

    for path in selectedPaths:

        print(
            "[Implementation Research] "
            f"Selected: {path}"
        )

    evidence = []

    for path in selectedPaths:

        try:

            content = (
                getGitHubFileContent(
                    owner=owner,
                    repository=repository,
                    path=path,
                    branch=branch,
                )
            )

        except Exception as error:

            print(
                "[Implementation Research] "
                f"Unable to retrieve "
                f"{path}: {error}"
            )

            continue

        if not content.strip():

            continue

        evidence.append(
            {
                "sourceType": (
                    "github"
                ),
                "repository": (
                    f"{owner}/"
                    f"{repository}"
                ),
                "path": path,
                "url": (
                    "https://github.com/"
                    f"{owner}/"
                    f"{repository}/"
                    f"blob/"
                    f"{branch}/"
                    f"{path}"
                ),
                "content": (
                    content[
                        :MAX_FILE_CHARS
                    ]
                ),
            }
        )

    return evidence


# ============================================================
# Hugging Face helpers
# ============================================================


def getHuggingFaceHeaders() -> dict:

    headers = {
        "User-Agent": "NestScanner",
    }

    token = (
        os.getenv(
            "HF_TOKEN"
        )
        or os.getenv(
            "HUGGINGFACE_TOKEN"
        )
    )

    if token:

        headers[
            "Authorization"
        ] = (
            f"Bearer {token}"
        )

    return headers


def getHuggingFaceModelInfo(
    repoId: str,
) -> dict:

    url = (
        "https://huggingface.co/"
        "api/models/"
        f"{repoId}"
    )

    response = requests.get(
        url,
        headers=(
            getHuggingFaceHeaders()
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def getHuggingFaceFileContent(
    repoId: str,
    path: str,
) -> str:

    url = (
        "https://huggingface.co/"
        f"{repoId}/resolve/main/"
        f"{path}"
    )

    response = requests.get(
        url,
        headers=(
            getHuggingFaceHeaders()
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.text


# ============================================================
# Hugging Face implementation evidence
# ============================================================


def collectHuggingFaceEvidence(
    source: str,
) -> list[dict]:

    repoId = (
        parseHuggingFaceSource(
            source
        )
    )

    if not repoId:

        return []

    print(
        "[Implementation Research] "
        "Inspecting Hugging Face repository: "
        f"{repoId}"
    )

    try:

        modelInfo = (
            getHuggingFaceModelInfo(
                repoId
            )
        )

    except Exception as error:

        print(
            "[Implementation Research] "
            "Unable to retrieve Hugging Face "
            f"model information: {error}"
        )

        return []

    siblings = modelInfo.get(
        "siblings",
        [],
    )

    paths = []

    for sibling in siblings:

        path = sibling.get(
            "rfilename"
        )

        if path:

            paths.append(
                path
            )

    print(
        "[Implementation Research] "
        f"Hugging Face files found: "
        f"{len(paths)}"
    )

    selectedPaths = (
        selectImplementationFiles(
            paths
        )
    )

    print(
        "[Implementation Research] "
        f"Selected implementation files: "
        f"{len(selectedPaths)}"
    )

    evidence = []

    for path in selectedPaths:

        print(
            "[Implementation Research] "
            f"Selected: {path}"
        )

        try:

            content = (
                getHuggingFaceFileContent(
                    repoId=repoId,
                    path=path,
                )
            )

        except Exception as error:

            print(
                "[Implementation Research] "
                f"Unable to retrieve "
                f"{path}: {error}"
            )

            continue

        if not content.strip():

            continue

        evidence.append(
            {
                "sourceType": (
                    "huggingface"
                ),
                "repository": (
                    repoId
                ),
                "path": path,
                "url": (
                    "https://huggingface.co/"
                    f"{repoId}/blob/main/"
                    f"{path}"
                ),
                "content": (
                    content[
                        :MAX_FILE_CHARS
                    ]
                ),
            }
        )

    return evidence


# ============================================================
# Evidence collection
# ============================================================


def collectImplementationEvidence(
    source: str,
) -> list[dict]:

    if parseGithubSource(
        source
    ):

        try:

            return (
                collectGithubEvidence(
                    source
                )
            )

        except Exception as error:

            print(
                "[Implementation Research] "
                "GitHub evidence collection "
                f"failed: {error}"
            )

            return []

    if parseHuggingFaceSource(
        source
    ):

        try:

            return (
                collectHuggingFaceEvidence(
                    source
                )
            )

        except Exception as error:

            print(
                "[Implementation Research] "
                "Hugging Face evidence "
                f"collection failed: {error}"
            )

            return []

    print(
        "[Implementation Research] "
        "Unsupported implementation "
        f"source: {source}"
    )

    return []


# ============================================================
# Evidence context
# ============================================================


def buildEvidenceContext(
    evidence: list[dict],
) -> str:

    sections = []

    totalCharacters = 0

    for item in evidence:

        header = (
            "\n"
            "============================================================\n"
            f"SOURCE FILE: {item['path']}\n"
            f"SOURCE TYPE: {item['sourceType']}\n"
            f"REPOSITORY: {item['repository']}\n"
            f"URL: {item['url']}\n"
            "============================================================\n"
        )

        content = (
            item["content"]
        )

        section = (
            header
            + content
        )

        remainingCharacters = (
            MAX_CONTEXT_CHARS
            - totalCharacters
        )

        if remainingCharacters <= 0:

            break

        section = (
            section[
                :remainingCharacters
            ]
        )

        sections.append(
            section
        )

        totalCharacters += (
            len(section)
        )

    return "\n".join(
        sections
    )


# ============================================================
# Implementation extraction prompt
# ============================================================


def buildImplementationPrompt(
    modelName: str,
    modelFamily: str,
    source: str,
    technicalProfile: str,
    evidenceContext: str,
) -> str:

    return f"""
You are analysing official implementation evidence for an
automatic speech recognition model.

Your job is NOT to generate EchoForge code.

Your task is to determine how the target model is actually
loaded and used for inference.

============================================================
TARGET MODEL
============================================================

Model name:

{modelName}

Model family:

{modelFamily}

Model source:

{source}

============================================================
EXISTING TECHNICAL PROFILE
============================================================

{technicalProfile}

============================================================
OFFICIAL IMPLEMENTATION EVIDENCE
============================================================

{evidenceContext}

============================================================
TASK
============================================================

Extract concrete information required to implement inference.

Determine, only when supported by the supplied evidence:

1. MODEL LOADING

Identify:

- exact Python classes
- exact functions
- exact import paths
- checkpoint loading
- configuration loading
- processor creation
- tokenizer creation
- feature extractor creation
- local-directory expectations
- repository-local modules
- trust_remote_code requirements where relevant

2. AUDIO PREPROCESSING

Identify:

- required sample rate
- waveform representation
- mono/stereo expectations
- feature extraction
- processor calls
- tensor shapes where documented
- batching behaviour where documented

3. INFERENCE

Identify:

- exact method used for inference
- generate()
- transcribe()
- forward()
- custom inference functions
- required arguments
- generation parameters
- device behaviour
- dtype behaviour where documented

4. DECODING

Identify:

- how raw output becomes text
- tokenizer decoding
- processor decoding
- CTC decoding
- timestamp handling
- segment handling

5. DEPENDENCIES

Identify:

- pip-installable Python packages
- repository-local Python modules
- custom/native dependencies
- system packages where documented

Clearly distinguish:

PIP DEPENDENCIES

from:

REPOSITORY-LOCAL CODE

6. LOCAL MODEL CONSIDERATIONS

EchoForge already downloads model artifacts before inference.

Determine:

- whether the official code normally downloads weights
- whether its loading API supports a local path
- whether model_path can directly replace a remote identifier
- whether additional repository code/configuration is required
- whether model_path is expected to contain a file or directory
- whether the repository itself must be available at runtime

============================================================
EVIDENCE PRIORITY
============================================================

Prefer evidence in this order:

1. executable official inference code
2. official model-loading source code
3. official example/demo code
4. official README/model card
5. dependency/configuration files

If README text conflicts with executable code, prefer the
executable code.

============================================================
STRICT RULES
============================================================

- Do NOT invent APIs.
- Do NOT assume Hugging Face Transformers unless supported.
- Do NOT assume AutoModel.
- Do NOT assume AutoProcessor.
- Do NOT assume from_pretrained().
- Do NOT assume generate().
- Do NOT assume transcribe().
- Preserve exact class names.
- Preserve exact function names.
- Preserve repository-local import paths.
- Clearly identify repository-local modules.
- Do NOT invent pip package names.
- State UNKNOWN when evidence is insufficient.
- Do NOT generate main.py.
- Do NOT generate requirements.txt.
- Do NOT generate Dockerfile.

============================================================
OUTPUT FORMAT
============================================================

Return exactly:

<MODEL_LOADING>
...
</MODEL_LOADING>

<PREPROCESSING>
...
</PREPROCESSING>

<INFERENCE>
...
</INFERENCE>

<DECODING>
...
</DECODING>

<DEPENDENCIES>
...
</DEPENDENCIES>

<LOCAL_MODEL_CONSIDERATIONS>
...
</LOCAL_MODEL_CONSIDERATIONS>
"""


# ============================================================
# Implementation research
# ============================================================


def researchModelImplementation(
    modelName: str,
    modelFamily: str,
    source: str,
    technicalProfile: dict | str,
    forceResearch: bool = False,
) -> dict:

    print()
    print("=" * 60)

    print(
        "[Implementation Research] "
        f"Starting: {modelName}"
    )

    print("=" * 60)

    # ----------------------------------------
    # 1. Check cache
    # ----------------------------------------

    if not forceResearch:

        cachedResult = (
            loadImplementationCache(
                modelFamily
            )
        )

        if cachedResult:

            print(
                "[Implementation Research] "
                "Using cached implementation "
                f"research for {modelFamily}."
            )

            return cachedResult

    elif forceResearch:

        print(
            "[Implementation Research] "
            "forceResearch=True. "
            "Ignoring existing cache."
        )

    # ----------------------------------------
    # 2. Normalize technical profile
    # ----------------------------------------

    if isinstance(
        technicalProfile,
        str,
    ):

        technicalProfileText = (
            technicalProfile
        )

    else:

        technicalProfileText = (
            json.dumps(
                technicalProfile,
                indent=2,
                default=str,
            )
        )

    # ----------------------------------------
    # 3. Collect implementation evidence
    # ----------------------------------------

    evidence = (
        collectImplementationEvidence(
            source
        )
    )

    print(
        "[Implementation Research] "
        f"Usable implementation files: "
        f"{len(evidence)}"
    )

    # ----------------------------------------
    # 4. Stop if no evidence
    # ----------------------------------------

    if not evidence:

        print(
            "[Implementation Research] "
            "No usable official implementation "
            "evidence found."
        )

        return {
            "modelName": modelName,
            "modelFamily": modelFamily,
            "source": source,
            "status": (
                "implementation-evidence-missing"
            ),
            "evidence": [],
            "implementationContext": "",
        }

    # ----------------------------------------
    # 5. Build evidence context
    # ----------------------------------------

    evidenceContext = (
        buildEvidenceContext(
            evidence
        )
    )

    print(
        "[Implementation Research] "
        "Evidence context size: "
        f"{len(evidenceContext)} characters"
    )

    # ----------------------------------------
    # 6. Extract implementation behaviour
    # ----------------------------------------

    prompt = (
        buildImplementationPrompt(
            modelName=modelName,
            modelFamily=modelFamily,
            source=source,
            technicalProfile=(
                technicalProfileText
            ),
            evidenceContext=(
                evidenceContext
            ),
        )
    )

    print(
        "[Implementation Research] "
        "Calling LLM to extract "
        "implementation behaviour."
    )

    llm = (
        getLLM()
    )

    response = (
        llm.invoke(
            prompt
        )
    )

    if hasattr(
        response,
        "content",
    ):

        implementationContext = (
            response.content
        )

    else:

        implementationContext = (
            str(
                response
            )
        )

    if not isinstance(
        implementationContext,
        str,
    ):

        implementationContext = (
            str(
                implementationContext
            )
        )

    implementationContext = (
        implementationContext.strip()
    )

    # ----------------------------------------
    # 7. Extraction failure
    # ----------------------------------------

    if not implementationContext:

        return {
            "modelName": modelName,
            "modelFamily": modelFamily,
            "source": source,
            "status": (
                "implementation-extraction-failed"
            ),
            "evidence": [
                {
                    "sourceType": (
                        item[
                            "sourceType"
                        ]
                    ),
                    "repository": (
                        item[
                            "repository"
                        ]
                    ),
                    "path": (
                        item[
                            "path"
                        ]
                    ),
                    "url": (
                        item[
                            "url"
                        ]
                    ),
                }
                for item in evidence
            ],
            "implementationContext": "",
        }

    # ----------------------------------------
    # 8. Build successful result
    # ----------------------------------------

    result = {
        "modelName": modelName,
        "modelFamily": modelFamily,
        "source": source,
        "status": "completed",
        "evidence": [
            {
                "sourceType": (
                    item[
                        "sourceType"
                    ]
                ),
                "repository": (
                    item[
                        "repository"
                    ]
                ),
                "path": (
                    item[
                        "path"
                    ]
                ),
                "url": (
                    item[
                        "url"
                    ]
                ),
            }
            for item in evidence
        ],
        "implementationContext": (
            implementationContext
        ),
    }

    # ----------------------------------------
    # 9. Save successful research to cache
    # ----------------------------------------

    saveImplementationCache(
        modelFamily=modelFamily,
        result=result,
    )

    print(
        "[Implementation Research] "
        f"Completed: {modelName}"
    )

    return result