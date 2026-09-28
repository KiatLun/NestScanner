"""Create a draft EchoForge PR from explicitly reported NestScanner changes.

Generated files are copied from the local EchoForge checkout. Shared model_list
changes are applied as individual entries to the target branch's remote content,
so unrelated local edits to those shared files are never submitted.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path, PurePosixPath
import re
import uuid

import requests

_GENERATED_PREFIXES = (
    "components/inference_component/",
    "pipeline/src/conf/nestscanner/",
)


def _safeRelativePath(path: str) -> str:
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


def createPullRequest(
    *,
    modelName: str,
    echoforgeRoot: str | Path,
    generatedFiles: list[str],
    sharedEntries: dict[str, list[str]],
    dryRun: bool = True,
) -> dict:
    """Create one draft PR after the NestScanner workflow reports success.

    Args:
        modelName: Used for commit and PR naming.
        echoforgeRoot: Root directory of the local EchoForge checkout.
        generatedFiles: Repository-relative paths of complete, generated files.
        sharedEntries: Map of repo-relative model_list paths to *exact new lines*
            that NestScanner successfully added during this run. The full local
            model_list is intentionally never uploaded.
        dryRun: Show locally selected inputs without making GitHub API calls.
    """
    root = Path(echoforgeRoot).expanduser().resolve(strict=True)
    normalizedFiles = list(dict.fromkeys(map(_safeRelativePath, generatedFiles)))
    normalizedShared = {
        _safeRelativePath(path): list(dict.fromkeys(lines))
        for path, lines in sharedEntries.items()
    }

    for path in normalizedFiles:
        if not path.startswith(_GENERATED_PREFIXES):
            raise ValueError(f"Unexpected generated-file path: {path}")
        if path in normalizedShared:
            raise ValueError(f"Path cannot be both generated and shared: {path}")

    for path, lines in normalizedShared.items():
        if not re.fullmatch(r"deployment/model_download/[^/]+/model_list", path):
            raise ValueError(f"Unexpected shared-file path: {path}")
        if not lines or any(
            not line.strip() or "\n" in line or "\r" in line for line in lines
        ):
            raise ValueError(f"Invalid model_list entries for: {path}")

    localFiles = {}
    for path in normalizedFiles:
        filePath = (root / path).resolve(strict=True)
        if not filePath.is_relative_to(root) or not filePath.is_file():
            raise ValueError(f"Invalid generated file: {path}")
        localFiles[path] = filePath.read_text(encoding="utf-8")

    if dryRun:
        return {
            "status": "dry-run",
            "modelName": modelName,
            "generatedFiles": list(localFiles),
            "sharedEntries": normalizedShared,
        }

    if not localFiles and not normalizedShared:
        return {"status": "no-changes", "modelName": modelName}

    token = os.environ["GITHUB_TOKEN"]
    owner = os.environ["ECHOFORGE_GITHUB_OWNER"]
    repo = os.environ.get("ECHOFORGE_GITHUB_REPO", "EchoForge")
    apiUrl = f"https://api.github.com/repos/{owner}/{repo}"

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }
    )

    def request(method: str, endpoint: str, *, allowMissing: bool = False, **kwargs):
        response = session.request(method, apiUrl + endpoint, timeout=30, **kwargs)
        if allowMissing and response.status_code == 404:
            return None
        if not response.ok:
            raise RuntimeError(
                f"GitHub {method} {endpoint} failed: "
                f"HTTP {response.status_code}; {response.text[:600]}"
            )
        return response.json()

    repository = request("GET", "")
    baseBranch = repository["default_branch"]
    baseReference = request("GET", f"/git/ref/heads/{baseBranch}")
    baseSha = baseReference["object"]["sha"]
    baseCommit = request("GET", f"/git/commits/{baseSha}")
    baseTree = baseCommit["tree"]["sha"]

    # Apply only NestScanner's specific new entries to the remote model_list.
    for path, linesToAdd in normalizedShared.items():
        from urllib.parse import quote

        remote = request(
            "GET",
            f"/contents/{quote(path, safe='/')}",
            params={"ref": baseBranch},
            allowMissing=True,
        )
        if remote is None:
            original = ""
        else:
            if remote.get("type") != "file" or remote.get("encoding") != "base64":
                raise ValueError(f"GitHub did not provide text file contents: {path}")
            original = base64.b64decode(remote["content"]).decode("utf-8")

        existing = set(original.splitlines())
        addedLines = [line for line in linesToAdd if line not in existing]
        if not addedLines:
            continue
        separator = "" if not original or original.endswith("\n") else "\n"
        localFiles[path] = original + separator + "\n".join(addedLines) + "\n"

    if not localFiles:
        return {"status": "no-changes", "modelName": modelName}

    tree = request(
        "POST",
        "/git/trees",
        json={
            "base_tree": baseTree,
            "tree": [
                {"path": path, "mode": "100644", "type": "blob", "content": content}
                for path, content in localFiles.items()
            ],
        },
    )
    if tree["sha"] == baseTree:
        return {"status": "no-changes", "modelName": modelName}

    commit = request(
        "POST",
        "/git/commits",
        json={
            "message": f"feat: onboard {modelName}",
            "tree": tree["sha"],
            "parents": [baseSha],
        },
    )
    slug = re.sub(r"[^a-z0-9]+", "-", modelName.lower()).strip("-") or "asr-model"
    branch = f"nestscanner/{slug}-{uuid.uuid4().hex[:8]}"
    request(
        "POST",
        "/git/refs",
        json={
            "ref": f"refs/heads/{branch}",
            "sha": commit["sha"],
        },
    )

    body = (
        f"Automated NestScanner onboarding of `{modelName}`.\n\n"
        "Files included:\n"
        + "\n".join(f"- `{path}`" for path in localFiles)
        + "\n\nGenerated code should be reviewed before merging."
    )
    pull = request(
        "POST",
        "/pulls",
        json={
            "title": f"feat: onboard {modelName}",
            "head": branch,
            "base": baseBranch,
            "body": body,
            "draft": True,
        },
    )
    return {
        "status": "created",
        "modelName": modelName,
        "branch": branch,
        "pullRequestUrl": pull["html_url"],
        "pullRequestNumber": pull["number"],
        "submittedFiles": list(localFiles),
    }
