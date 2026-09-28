"""Create a draft EchoForge PR from explicitly reported NestScanner changes.

Generated files are copied from the local EchoForge checkout.

Shared model_list changes are applied as individual entries to the
target branch's remote content, so unrelated local edits to shared
files are never submitted.

Generated pipeline YAML files have their environment-specific dataset
and model IDs replaced with placeholders before being submitted.
The original local YAML files remain unchanged.
"""

from __future__ import annotations

import base64
import os
import re
import uuid

from pathlib import Path, PurePosixPath
from urllib.parse import quote

import requests
import yaml
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================

load_dotenv()

_GENERATED_PREFIXES = (
    "components/inference_component/",
    "pipeline/src/conf/nestscanner/",
)

_PIPELINE_PREFIX = "pipeline/src/conf/nestscanner/"


# ============================================================
# 1. Validate repository-relative paths
# ============================================================


def _safeRelativePath(
    path: str,
) -> str:

    posix = PurePosixPath(path)

    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or posix.as_posix() != path
        or any(part in (".", "..") for part in path.split("/"))
    ):
        raise ValueError(f"Invalid repository-relative path: {path!r}")

    return path


# ============================================================
# 2. Prepare pipeline YAML for GitHub PR
# ============================================================


def preparePipelineForPr(
    content: str,
) -> str:
    """
    Replace environment-specific IDs with reusable placeholders.

    This modifies only the in-memory copy submitted to GitHub.
    The original YAML in the local EchoForge checkout is unchanged.
    """

    pipeline = yaml.safe_load(content)

    if not isinstance(pipeline, dict):
        raise ValueError(
            "Generated pipeline YAML must contain " "a configuration dictionary."
        )

    # ----------------------------------------
    # Replace dataset IDs
    # ----------------------------------------

    datasets = pipeline.get("datasets")

    if not isinstance(datasets, dict):
        raise ValueError(
            "Generated pipeline YAML is missing " "its datasets configuration."
        )

    if "dataset_ids" not in datasets:
        raise ValueError("Generated pipeline YAML is missing " "datasets.dataset_ids.")

    datasets["dataset_ids"] = ["<your_dataset_id_here>"]

    # ----------------------------------------
    # Replace ClearML model ID
    # ----------------------------------------

    stages = pipeline.get("stages", {})

    inferenceStage = stages.get(
        "stt_inference",
    )

    if not isinstance(inferenceStage, dict):
        raise ValueError(
            "Generated pipeline YAML is missing " "the stt_inference stage."
        )

    parameters = inferenceStage.get(
        "parameter_override",
    )

    if not isinstance(parameters, dict):
        raise ValueError(
            "Generated pipeline YAML is missing " "the inference parameter overrides."
        )

    if "Args/model_id" not in parameters:
        raise ValueError("Generated pipeline YAML is missing " "Args/model_id.")

    parameters["Args/model_id"] = "<your_model_id_here>"

    # ----------------------------------------
    # Return reusable YAML
    # ----------------------------------------

    return yaml.safe_dump(
        pipeline,
        sort_keys=False,
        allow_unicode=True,
    )


# ============================================================
# 3. Build GitHub PR description
# ============================================================


def buildPullRequestBody(
    modelName: str,
    submittedFiles: dict[str, str],
) -> str:

    pipelineFiles = [
        path
        for path in submittedFiles
        if (path.startswith(_PIPELINE_PREFIX) and path.endswith((".yaml", ".yml")))
    ]

    # ----------------------------------------
    # Files included
    # ----------------------------------------

    fileList = "\n".join(f"- `{path}`" for path in submittedFiles)

    # ----------------------------------------
    # Configuration instructions
    # ----------------------------------------

    configurationSections = []

    for path in pipelineFiles:

        configurationSections.append(
            f"### `{path}`\n\n"
            "| Parameter | Required change |\n"
            "|---|---|\n"
            "| `datasets.dataset_ids` | "
            "Replace `<your_dataset_id_here>` with "
            "your ClearML dataset ID. |\n"
            "| `Args/model_id` | "
            "Replace `<your_model_id_here>` with "
            "your registered ClearML model ID. |"
        )

    if configurationSections:

        configurationInstructions = "\n\n".join(configurationSections)

    else:

        configurationInstructions = "No new pipeline YAML was generated."

    # ----------------------------------------
    # Full PR description
    # ----------------------------------------

    body = (
        "## Model Onboarding\n\n"
        f"Automated onboarding of `{modelName}` "
        "by NestScanner.\n\n"
        "## Files Included\n\n"
        f"{fileList}\n\n"
        "## Configuration Required\n\n"
        "Before running the generated pipeline, "
        "update the following values in your "
        "EchoForge environment.\n\n"
        f"{configurationInstructions}\n\n"
        "## Review Notes\n\n"
        "Review the generated component code, "
        "dependencies, Dockerfile and pipeline "
        "configuration before merging.\n\n"
        "The pipeline was submitted during "
        "NestScanner testing. Successful submission "
        "does not guarantee that inference and "
        "evaluation completed successfully."
    )

    return body


# ============================================================
# 4. Create GitHub PR
# ============================================================


def createPullRequest(
    *,
    modelName: str,
    echoforgeRoot: str | Path,
    generatedFiles: list[str],
    sharedEntries: dict[str, list[str]],
    dryRun: bool = True,
) -> dict:
    """
    Create one draft PR after the NestScanner workflow succeeds.

    Args:
        modelName:
            Used for commit and PR naming.

        echoforgeRoot:
            Root directory of the local EchoForge checkout.

        generatedFiles:
            Repository-relative paths of complete generated files.

        sharedEntries:
            Map of repository-relative model_list paths to exact
            lines added by NestScanner during this run.

            The full local model_list is never uploaded.

        dryRun:
            Preview locally selected inputs without making
            GitHub API calls.
    """

    # ----------------------------------------
    # 1. Resolve local EchoForge directory
    # ----------------------------------------

    root = Path(echoforgeRoot).expanduser().resolve(strict=True)

    # ----------------------------------------
    # 2. Normalize reported changes
    # ----------------------------------------

    normalizedFiles = list(
        dict.fromkeys(
            map(
                _safeRelativePath,
                generatedFiles,
            )
        )
    )

    normalizedShared = {
        _safeRelativePath(path): list(dict.fromkeys(lines))
        for path, lines in sharedEntries.items()
    }

    # ----------------------------------------
    # 3. Validate generated file paths
    # ----------------------------------------

    for path in normalizedFiles:

        if not path.startswith(_GENERATED_PREFIXES):
            raise ValueError("Unexpected generated-file path: " f"{path}")

        if path in normalizedShared:
            raise ValueError("Path cannot be both generated " f"and shared: {path}")

    # ----------------------------------------
    # 4. Validate shared file entries
    # ----------------------------------------

    for path, lines in normalizedShared.items():

        if not re.fullmatch(
            r"deployment/model_download/[^/]+/model_list",
            path,
        ):
            raise ValueError(f"Unexpected shared-file path: {path}")

        if not lines or any(
            not line.strip() or "\n" in line or "\r" in line for line in lines
        ):
            raise ValueError("Invalid model_list entries for: " f"{path}")

    # ----------------------------------------
    # 5. Read generated files
    # ----------------------------------------

    localFiles = {}

    for path in normalizedFiles:

        filePath = (root / path).resolve(strict=True)

        if not filePath.is_relative_to(root) or not filePath.is_file():
            raise ValueError(f"Invalid generated file: {path}")

        content = filePath.read_text(encoding="utf-8")

        # ------------------------------------
        # Sanitize pipeline YAML for GitHub
        # ------------------------------------

        if path.startswith(_PIPELINE_PREFIX) and path.endswith((".yaml", ".yml")):

            content = preparePipelineForPr(content)

            print(
                "[GitHub PR] Replaced dataset "
                "and model IDs with placeholders: "
                f"{path}"
            )

        localFiles[path] = content

    # ----------------------------------------
    # 6. Dry-run preview
    # ----------------------------------------

    if dryRun:

        print()
        print("[GitHub PR] Dry run: " "no GitHub API calls will be made.")

        print(
            "[GitHub PR] Generated files:",
            len(localFiles),
        )

        print(
            "[GitHub PR] Shared files:",
            len(normalizedShared),
        )

        # Preview sanitized pipeline YAML.
        pipelinePreviews = {
            path: content
            for path, content in localFiles.items()
            if (path.startswith(_PIPELINE_PREFIX) and path.endswith((".yaml", ".yml")))
        }

        # Preview PR body with the reported files.
        # Shared entries may still be filtered later
        # against the remote version.
        previewFiles = dict(localFiles)

        for path in normalizedShared:
            previewFiles.setdefault(path, "")

        prBody = buildPullRequestBody(
            modelName=modelName,
            submittedFiles=previewFiles,
        )

        return {
            "status": "dry-run",
            "modelName": modelName,
            "generatedFiles": list(localFiles),
            "sharedEntries": normalizedShared,
            "pipelinePreviews": pipelinePreviews,
            "pullRequestBody": prBody,
        }

    # ----------------------------------------
    # 7. Check for changes
    # ----------------------------------------

    if not localFiles and not normalizedShared:

        return {
            "status": "no-changes",
            "modelName": modelName,
        }

    # ----------------------------------------
    # 8. Configure GitHub API
    # ----------------------------------------

    token = os.environ["GITHUB_TOKEN"]

    owner = os.environ["ECHOFORGE_GITHUB_OWNER"]

    repo = os.environ.get(
        "ECHOFORGE_GITHUB_REPO",
        "EchoForge",
    )

    apiUrl = f"https://api.github.com/repos/" f"{owner}/{repo}"

    session = requests.Session()

    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": ("application/vnd.github+json"),
            "X-GitHub-Api-Version": "2026-03-10",
        }
    )

    def request(
        method: str,
        endpoint: str,
        *,
        allowMissing: bool = False,
        **kwargs,
    ):

        response = session.request(
            method,
            apiUrl + endpoint,
            timeout=30,
            **kwargs,
        )

        if allowMissing and response.status_code == 404:
            return None

        if not response.ok:
            raise RuntimeError(
                f"GitHub {method} {endpoint} failed: "
                f"HTTP {response.status_code}; "
                f"{response.text[:600]}"
            )

        return response.json()

    # ----------------------------------------
    # 9. Resolve default branch
    # ----------------------------------------

    repository = request(
        "GET",
        "",
    )

    baseBranch = repository["default_branch"]

    baseReference = request(
        "GET",
        f"/git/ref/heads/{baseBranch}",
    )

    baseSha = baseReference["object"]["sha"]

    baseCommit = request(
        "GET",
        f"/git/commits/{baseSha}",
    )

    baseTree = baseCommit["tree"]["sha"]

    # ----------------------------------------
    # 10. Apply shared model_list changes
    # ----------------------------------------

    for path, linesToAdd in normalizedShared.items():

        remote = request(
            "GET",
            f"/contents/{quote(path, safe='/')}",
            params={
                "ref": baseBranch,
            },
            allowMissing=True,
        )

        if remote is None:

            original = ""

        else:

            if remote.get("type") != "file" or remote.get("encoding") != "base64":
                raise ValueError(
                    "GitHub did not provide " "text file contents: " f"{path}"
                )

            original = base64.b64decode(remote["content"]).decode("utf-8")

        # Compare exact lines to avoid adding
        # the same model_list entry twice.
        existing = set(original.splitlines())

        addedLines = [line for line in linesToAdd if line not in existing]

        if not addedLines:
            continue

        separator = "" if (not original or original.endswith("\n")) else "\n"

        # Use GitHub's version of model_list,
        # not the local version.
        localFiles[path] = original + separator + "\n".join(addedLines) + "\n"

    # ----------------------------------------
    # 11. Check for remaining changes
    # ----------------------------------------

    if not localFiles:

        return {
            "status": "no-changes",
            "modelName": modelName,
        }

    # ----------------------------------------
    # 12. Create Git tree
    # ----------------------------------------

    tree = request(
        "POST",
        "/git/trees",
        json={
            "base_tree": baseTree,
            "tree": [
                {
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "content": content,
                }
                for path, content in localFiles.items()
            ],
        },
    )

    if tree["sha"] == baseTree:

        return {
            "status": "no-changes",
            "modelName": modelName,
        }

    # ----------------------------------------
    # 13. Create Git commit
    # ----------------------------------------

    commit = request(
        "POST",
        "/git/commits",
        json={
            "message": (f"feat: onboard {modelName}"),
            "tree": tree["sha"],
            "parents": [
                baseSha,
            ],
        },
    )

    # ----------------------------------------
    # 14. Create Git branch
    # ----------------------------------------

    slug = (
        re.sub(
            r"[^a-z0-9]+",
            "-",
            modelName.lower(),
        ).strip("-")
        or "asr-model"
    )

    branch = f"nestscanner/{slug}-" f"{uuid.uuid4().hex[:8]}"

    request(
        "POST",
        "/git/refs",
        json={
            "ref": (f"refs/heads/{branch}"),
            "sha": commit["sha"],
        },
    )

    # ----------------------------------------
    # 15. Build PR description
    # ----------------------------------------

    body = buildPullRequestBody(
        modelName=modelName,
        submittedFiles=localFiles,
    )

    # ----------------------------------------
    # 16. Create draft PR
    # ----------------------------------------

    pull = request(
        "POST",
        "/pulls",
        json={
            "title": (f"feat: onboard {modelName}"),
            "head": branch,
            "base": baseBranch,
            "body": body,
            "draft": True,
        },
    )

    print()
    print(
        "[GitHub PR] Created:",
        pull["html_url"],
    )

    # ----------------------------------------
    # 17. Return PR information
    # ----------------------------------------

    return {
        "status": "created",
        "modelName": modelName,
        "branch": branch,
        "pullRequestUrl": pull["html_url"],
        "pullRequestNumber": pull["number"],
        "submittedFiles": list(localFiles),
    }
