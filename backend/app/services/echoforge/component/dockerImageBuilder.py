import subprocess
from pathlib import Path


def dockerImageExists(
    imageName: str,
) -> bool:

    process = subprocess.run(
        [
            "docker",
            "image",
            "inspect",
            imageName,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    return process.returncode == 0


def buildDockerImage(
    imageName: str,
    dockerfile: str | Path,
    buildContext: str | Path,
) -> dict:

    dockerfilePath = Path(dockerfile).resolve()

    buildContextPath = Path(buildContext).resolve()

    if not dockerfilePath.exists():
        raise RuntimeError(f"Dockerfile not found: " f"{dockerfilePath}")

    if not buildContextPath.exists():
        raise RuntimeError(f"Docker build context not found: " f"{buildContextPath}")

    command = [
        "docker",
        "build",
        "-t",
        imageName,
        "-f",
        str(dockerfilePath),
        str(buildContextPath),
    ]

    print()
    print("=" * 60)
    print("BUILDING DOCKER IMAGE")
    print("=" * 60)

    print(f"[Docker] Image: " f"{imageName}")

    print(f"[Docker] Dockerfile: " f"{dockerfilePath}")

    print(f"[Docker] Build context: " f"{buildContextPath}")

    print("[Docker] Command: " + " ".join(command))

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    outputLines = []

    if process.stdout is None:

        process.kill()

        raise RuntimeError("Failed to capture Docker build output.")

    for line in process.stdout:

        line = line.rstrip()

        outputLines.append(line)

        print(f"[Docker] {line}")

    returnCode = process.wait()

    if returnCode != 0:

        raise RuntimeError(
            f"Docker image build failed: " f"{imageName}\n\n" + "\n".join(outputLines)
        )

    return {
        "imageName": imageName,
        "dockerfile": str(dockerfilePath),
        "buildContext": str(buildContextPath),
        "status": "built",
    }


def ensureDockerImage(
    imageName: str,
    dockerfile: str | Path,
    buildContext: str | Path,
    forceBuild: bool = False,
) -> dict:

    if not forceBuild and dockerImageExists(imageName):

        print(f"[Docker] Image already exists: " f"{imageName}")

        return {
            "imageName": imageName,
            "dockerfile": str(Path(dockerfile).resolve()),
            "buildContext": str(Path(buildContext).resolve()),
            "status": "existing",
        }

    return buildDockerImage(
        imageName=imageName,
        dockerfile=dockerfile,
        buildContext=buildContext,
    )
