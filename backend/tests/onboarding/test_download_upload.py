import json

from app.graph.onboarding.workflow import (
    runOnboardingWorkflow,
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
    skipped = 0

    print()
    print("=" * 80)
    print("ONBOARDING WORKFLOW TEST")
    print("=" * 80)

    for researchResult in researchResults:

        modelName = researchResult.get("candidate", {}).get("name", "Unknown Model")

        print()
        print("-" * 80)
        print(f"Testing: {modelName}")
        print("-" * 80)

        try:

            result = runOnboardingWorkflow(researchResult)

        except Exception as error:

            failed += 1

            print()
            print(f"[FAIL] {modelName}")
            print(f"       Exception: {error}")

            continue

        print()
        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        status = result.get("status")

        # ----------------------------------------
        # Completed
        # ----------------------------------------

        if status == "completed":

            passed += 1

            print()
            print(f"[PASS] {modelName}")

            print(f"       ClearML Model ID: " f"{result.get('clearmlModelId')}")

            print(f"       Cache: " f"{result.get('cachePath')}")

        # ----------------------------------------
        # Downloader required
        # ----------------------------------------

        elif status == "downloader-required":

            skipped += 1

            print()
            print(f"[SKIP] {modelName}")
            print("       No usable existing " "downloader.")

        # ----------------------------------------
        # Failed
        # ----------------------------------------

        else:

            failed += 1

            print()
            print(f"[FAIL] {modelName}")
            print(f"       Status: {status}")

            error = result.get("error")

            if error:

                print(f"       Error: {error}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"Completed: {passed}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {failed}")
    print(f"Total:     {len(researchResults)}")


if __name__ == "__main__":
    main()
