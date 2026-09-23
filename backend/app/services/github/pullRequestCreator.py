import os
import re
from typing import Any

import requests

GITHUB_API_URL = "https://api.github.com"


def getGitHubToken() -> str:
    token = os.getenv(
        "GITHUB_TOKEN",
        "",
    ).strip()

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured.")

    return token


def getRepositoryOwner() -> str:
    owner = os.getenv(
        "ECHOFORGE_GITHUB_OWNER",
        "",
    ).strip()

    if not owner:
        raise RuntimeError("ECHOFORGE_GITHUB_OWNER " "is not configured.")

    return owner


def getRepositoryName() -> str:
    repo = os.getenv(
        "ECHOFORGE_GITHUB_REPO",
        "echoforge",
    ).strip()

    if not repo:
        raise RuntimeError("ECHOFORGE_GITHUB_REPO " "is not configured.")

    return repo


def buildHeaders() -> dict[str, str]:
    token = getGitHubToken()

    return {
        "Authorization": (f"Bearer {token}"),
        "Accept": ("application/vnd.github+json"),
        "X-GitHub-Api-Version": ("2022-11-28"),
    }


def githubRequest(
    method: str,
    endpoint: str,
    jsonBody: dict | None = None,
) -> Any:

    url = f"{GITHUB_API_URL}" f"{endpoint}"

    response = requests.request(
        method=method,
        url=url,
        headers=buildHeaders(),
        json=jsonBody,
        timeout=60,
    )

    if not response.ok:

        try:
            errorData = response.json()

        except Exception:
            errorData = response.text

        raise RuntimeError(
            "GitHub API request failed.\n"
            f"Method: {method}\n"
            f"URL: {url}\n"
            f"Status: {response.status_code}\n"
            f"Response: {errorData}"
        )

    if not response.content:
        return None

    return response.json()


def normalizeBranchName(
    value: str,
) -> str:

    normalized = (
        value.strip().lower().replace("_", "-").replace(" ", "-").replace("/", "-")
    )

    normalized = re.sub(
        r"[^a-z0-9-]",
        "-",
        normalized,
    )

    normalized = re.sub(
        r"-+",
        "-",
        normalized,
    )

    return normalized.strip("-")


def getBaseBranchRef(
    owner: str,
    repo: str,
    baseBranch: str,
) -> dict:

    return githubRequest(
        method="GET",
        endpoint=(f"/repos/{owner}/{repo}/" f"git/ref/heads/{baseBranch}"),
    )


def getCommit(
    owner: str,
    repo: str,
    commitSha: str,
) -> dict:

    return githubRequest(
        method="GET",
        endpoint=(f"/repos/{owner}/{repo}/" f"git/commits/{commitSha}"),
    )


def createBlob(
    owner: str,
    repo: str,
    content: str,
) -> str:

    result = githubRequest(
        method="POST",
        endpoint=(f"/repos/{owner}/{repo}/" "git/blobs"),
        jsonBody={
            "content": content,
            "encoding": "utf-8",
        },
    )

    blobSha = result.get("sha")

    if not blobSha:
        raise RuntimeError("GitHub did not return " "a blob SHA.")

    return blobSha


def createTree(
    owner: str,
    repo: str,
    baseTreeSha: str,
    files: dict[str, str],
) -> str:

    treeEntries = []

    for filePath, content in files.items():

        blobSha = createBlob(
            owner=owner,
            repo=repo,
            content=content,
        )

        treeEntries.append(
            {
                "path": filePath,
                "mode": "100644",
                "type": "blob",
                "sha": blobSha,
            }
        )

    result = githubRequest(
        method="POST",
        endpoint=(f"/repos/{owner}/{repo}/" "git/trees"),
        jsonBody={
            "base_tree": (baseTreeSha),
            "tree": treeEntries,
        },
    )

    treeSha = result.get("sha")

    if not treeSha:
        raise RuntimeError("GitHub did not return " "a tree SHA.")

    return treeSha


def createCommit(
    owner: str,
    repo: str,
    message: str,
    treeSha: str,
    parentCommitSha: str,
) -> str:

    result = githubRequest(
        method="POST",
        endpoint=(f"/repos/{owner}/{repo}/" "git/commits"),
        jsonBody={
            "message": message,
            "tree": treeSha,
            "parents": [parentCommitSha],
        },
    )

    commitSha = result.get("sha")

    if not commitSha:
        raise RuntimeError("GitHub did not return " "a commit SHA.")

    return commitSha


def createBranch(
    owner: str,
    repo: str,
    branchName: str,
    commitSha: str,
):

    githubRequest(
        method="POST",
        endpoint=(f"/repos/{owner}/{repo}/" "git/refs"),
        jsonBody={
            "ref": (f"refs/heads/" f"{branchName}"),
            "sha": commitSha,
        },
    )


def createPullRequest(
    owner: str,
    repo: str,
    branchName: str,
    baseBranch: str,
    title: str,
    body: str,
) -> dict:

    return githubRequest(
        method="POST",
        endpoint=(f"/repos/{owner}/{repo}/" "pulls"),
        jsonBody={
            "title": title,
            "head": branchName,
            "base": baseBranch,
            "body": body,
        },
    )


def buildComponentFiles(
    componentName: str,
    mainFileContent: str,
    requirementsContent: str,
    dockerfileContent: str,
) -> dict[str, str]:

    componentBasePath = (
        "components/" "inference_component/" "stt_inference/" f"{componentName}"
    )

    return {
        (f"{componentBasePath}/" "main.py"): mainFileContent,
        (f"{componentBasePath}/" "requirements.txt"): requirementsContent,
        (f"{componentBasePath}/" "Dockerfile"): dockerfileContent,
    }


def createComponentPullRequest(
    modelName: str,
    componentName: str,
    mainFileContent: str,
    requirementsContent: str,
    dockerfileContent: str,
    baseBranch: str = "main",
) -> dict:

    print()
    print("=" * 70)
    print("[Pull Request Creator] " f"Creating PR for " f"{componentName}")
    print("=" * 70)

    owner = getRepositoryOwner()

    repo = getRepositoryName()

    files = buildComponentFiles(
        componentName=(componentName),
        mainFileContent=(mainFileContent),
        requirementsContent=(requirementsContent),
        dockerfileContent=(dockerfileContent),
    )

    branchName = "nestscanner/" "add-" f"{normalizeBranchName(componentName)}"

    commitMessage = "feat: add " f"{modelName} " "inference component"

    prTitle = "Add " f"{modelName} " "inference component"

    prBody = (
        f"Adds EchoForge inference "
        f"support for {modelName}.\n\n"
        "Changes:\n"
        f"- adds `{componentName}`\n"
        "- adds model-specific "
        "inference logic\n"
        "- adds required Python "
        "dependencies\n"
        "- adds Docker configuration\n"
        "- integrates with the shared "
        "EchoForge STT inference "
        "pipeline\n\n"
        "Generated through NestScanner "
        "Component Creation."
    )

    print("[Pull Request Creator] " f"Repository: " f"{owner}/{repo}")

    print("[Pull Request Creator] " f"Base branch: {baseBranch}")

    print("[Pull Request Creator] " f"New branch: {branchName}")

    # --------------------------------------------------------
    # 1. Resolve base branch
    # --------------------------------------------------------

    baseRef = getBaseBranchRef(
        owner=owner,
        repo=repo,
        baseBranch=(baseBranch),
    )

    baseCommitSha = baseRef["object"]["sha"]

    print("[Pull Request Creator] " "Base commit: " f"{baseCommitSha}")

    # --------------------------------------------------------
    # 2. Resolve base tree
    # --------------------------------------------------------

    baseCommit = getCommit(
        owner=owner,
        repo=repo,
        commitSha=(baseCommitSha),
    )

    baseTreeSha = baseCommit["tree"]["sha"]

    print("[Pull Request Creator] " "Base tree: " f"{baseTreeSha}")

    # --------------------------------------------------------
    # 3. Create blobs + tree
    # --------------------------------------------------------

    print("[Pull Request Creator] " f"Uploading {len(files)} " "generated file(s).")

    treeSha = createTree(
        owner=owner,
        repo=repo,
        baseTreeSha=(baseTreeSha),
        files=files,
    )

    print("[Pull Request Creator] " f"Created tree: {treeSha}")

    # --------------------------------------------------------
    # 4. Create commit
    # --------------------------------------------------------

    commitSha = createCommit(
        owner=owner,
        repo=repo,
        message=(commitMessage),
        treeSha=(treeSha),
        parentCommitSha=(baseCommitSha),
    )

    print("[Pull Request Creator] " f"Created commit: " f"{commitSha}")

    # --------------------------------------------------------
    # 5. Create branch
    # --------------------------------------------------------

    createBranch(
        owner=owner,
        repo=repo,
        branchName=(branchName),
        commitSha=(commitSha),
    )

    print("[Pull Request Creator] " "Branch created.")

    # --------------------------------------------------------
    # 6. Create PR
    # --------------------------------------------------------

    pullRequest = createPullRequest(
        owner=owner,
        repo=repo,
        branchName=(branchName),
        baseBranch=(baseBranch),
        title=(prTitle),
        body=(prBody),
    )

    prNumber = pullRequest.get("number")

    prUrl = pullRequest.get("html_url")

    if not prUrl:
        raise RuntimeError(
            "GitHub created the pull " "request but did not return " "html_url."
        )

    result = {
        "status": "created",
        "repository": (f"{owner}/{repo}"),
        "modelName": modelName,
        "component": (componentName),
        "branch": branchName,
        "baseBranch": baseBranch,
        "commitSha": (commitSha),
        "prNumber": (prNumber),
        "prUrl": prUrl,
    }

    print()
    print("[Pull Request Creator] " "Pull request created.")

    print("[Pull Request Creator] " f"PR: {prUrl}")

    return result
