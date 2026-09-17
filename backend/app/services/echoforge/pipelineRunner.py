import subprocess
from pathlib import Path

from app.services.echoforge.echoforgeConfig import (
    ECHOFORGE_ROOT,
    PIPELINE_SRC_DIR,
    CLEARML_ENV_FILE,
    CLEARML_CONFIG_FILE,
    NESTSCANNER_EVALUATION_IMAGE,
)

PIPELINE_CONTROLLER_IMAGE = NESTSCANNER_EVALUATION_IMAGE


def runPipeline(
    pipelinePath: str,
) -> dict:

    # ----------------------------------------
    # 1. Validate pipeline file
    # ----------------------------------------

    pipelinePathObject = Path(pipelinePath).resolve()

    if not pipelinePathObject.exists():
        raise RuntimeError(f"Pipeline file not found: " f"{pipelinePathObject}")

    if not pipelinePathObject.is_file():
        raise RuntimeError(f"Pipeline path is not a file: " f"{pipelinePathObject}")

    # ----------------------------------------
    # 2. Validate ClearML configuration
    # ----------------------------------------

    clearmlConfig = CLEARML_CONFIG_FILE

    if not clearmlConfig.exists():
        raise RuntimeError(f"ClearML config not found: " f"{clearmlConfig}")

    if not CLEARML_ENV_FILE.exists():
        raise RuntimeError(f"ClearML env file not found: " f"{CLEARML_ENV_FILE}")

    # ----------------------------------------
    # 3. Resolve pipeline config path
    # ----------------------------------------

    try:

        relativePipelinePath = pipelinePathObject.relative_to(
            PIPELINE_SRC_DIR.resolve()
        )

    except ValueError as error:

        raise RuntimeError(
            "Pipeline configuration must be "
            "inside the EchoForge pipeline/src "
            f"directory: {PIPELINE_SRC_DIR}"
        ) from error

    containerPipelinePath = Path("/app/pipeline_src") / relativePipelinePath

    # ----------------------------------------
    # 4. Build controller command
    # ----------------------------------------

    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "host",
        "-v",
        (f"{PIPELINE_SRC_DIR.resolve()}:" "/app/pipeline_src"),
        "-v",
        (f"{clearmlConfig.resolve()}:" "/root/clearml.conf:ro"),
        "--env-file",
        str(CLEARML_ENV_FILE.resolve()),
        PIPELINE_CONTROLLER_IMAGE,
        "python3",
        "/app/pipeline_src/main.py",
        "--conf",
        str(containerPipelinePath),
    ]

    # ----------------------------------------
    # 5. Run EchoForge controller
    # ----------------------------------------

    print()
    print("=" * 60)
    print("RUNNING ECHOFORGE PIPELINE")
    print("=" * 60)

    print("[Pipeline] Controller image: " f"{PIPELINE_CONTROLLER_IMAGE}")

    print("[Pipeline] Config: " f"{containerPipelinePath}")

    print("[Pipeline] Command: " + " ".join(command))

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

        raise RuntimeError("Failed to capture pipeline output.")

    for line in process.stdout:

        line = line.rstrip()

        outputLines.append(line)

        print(f"[EchoForge Pipeline] " f"{line}")

    returnCode = process.wait()

    # ----------------------------------------
    # 6. Handle controller failure
    # ----------------------------------------

    if returnCode != 0:

        raise RuntimeError("EchoForge pipeline failed.\n\n" + "\n".join(outputLines))

    # ----------------------------------------
    # 7. Submitted
    # ----------------------------------------

    print()
    print("[Pipeline] EchoForge pipeline " "submitted successfully.")

    return {
        "pipelinePath": str(pipelinePathObject),
        "pipelineConfig": str(containerPipelinePath),
        "controllerImage": (PIPELINE_CONTROLLER_IMAGE),
        "status": "submitted",
        "output": outputLines,
    }
