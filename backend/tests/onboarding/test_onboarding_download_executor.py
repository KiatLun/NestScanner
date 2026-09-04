import json

from app.services.echoforge.onboardingDownloadExecutor import (
    executeOnboardingDownload,
)


def main():

    with open(
        "tests/onboarding/sampleOutput.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    researchResults = data["research"]["results"]

    targetModel = None

    for researchResult in researchResults:

        candidate = researchResult.get(
            "candidate",
            {},
        )

        if candidate.get("name") == "Qwen3-ASR-1.7B":

            targetModel = researchResult
            break

    if not targetModel:

        raise RuntimeError("Qwen3-ASR-1.7B not found " "in sampleOutput.json")

    print()
    print("=" * 70)
    print("ONBOARDING DOWNLOAD EXECUTOR TEST")
    print("=" * 70)

    result = executeOnboardingDownload(targetModel)

    print()
    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    print()
    print("=" * 70)

    if result.get("status") != "downloaded":

        raise RuntimeError("Model download did not complete.")

    if not result.get("cachePath"):

        raise RuntimeError("Download completed but " "cachePath was not returned.")

    print("[PASS] Model downloaded")
    print(f"[PASS] Cache path: " f"{result['cachePath']}")


if __name__ == "__main__":
    main()
