import json

from app.services.echoforge.modelOnboarding import (
    executeOnboardingDownloadAndUpload,
)


def main():

    with open(
        "tests/onboarding/sampleOutput.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    researchResults = data["research"]["results"]

    passed = 0
    failed = 0

    print()
    print("=" * 80)
    print("DOWNLOAD + UPLOAD TEST")
    print("=" * 80)

    for researchResult in researchResults:

        modelName = researchResult["candidate"]["name"]

        print()
        print("-" * 80)
        print(f"Testing: {modelName}")
        print("-" * 80)

        try:
            result = executeOnboardingDownloadAndUpload(researchResult)

        except Exception as error:
            failed += 1

            print(f"[FAIL] {modelName}")
            print(f"       {error}")

            continue

        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        status = result.get("status")

        if status == "completed":
            passed += 1

            print()
            print(f"[PASS] {modelName}")

            print(f"       ClearML Model ID: " f"{result.get('clearmlModelId')}")

        elif status == "needs-downloader":
            print()
            print(f"[SKIP] {modelName}")
            print("       No usable existing downloader.")

        else:
            failed += 1

            print()
            print(f"[FAIL] {modelName}")
            print(f"       Status: {status}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Completed: {passed}")
    print(f"Failed:    {failed}")
    print(f"Total:     {len(researchResults)}")


if __name__ == "__main__":
    main()
