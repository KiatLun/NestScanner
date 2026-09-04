import json

from app.services.echoforge.downloadSourceResolver import (
    resolveDownloadSource,
)

EXPECTED_RESULTS = {
    "Qwen3-ASR-1.7B": {
        "modelName": "Qwen3-ASR-1.7B",
        "sourceType": "huggingface",
        "source": "Qwen/Qwen3-ASR-1.7B",
    },
    "Voxtral-Mini-3B-2507": {
        "modelName": "Voxtral-Mini-3B-2507",
        "sourceType": "huggingface",
        "source": "mistralai/Voxtral-Mini-3B-2507",
    },
    "Whisper Medium": {
        "modelName": "Whisper Medium",
        "sourceType": "huggingface",
        "source": "openai/whisper-medium",
    },
    "Silero VAD": {
        "modelName": "Silero VAD",
        "sourceType": "github",
        "source": "https://github.com/snakers4/silero-vad",
    },
    "Mega-ASR": {
        "modelName": "Mega-ASR",
        "sourceType": "huggingface",
        "source": "zhifeixie/Mega-ASR",
    },
    "Example Direct ASR": {
        "modelName": "Example Direct ASR",
        "sourceType": "directUrl",
        "source": ("https://example.org/models/" "example-asr/model.bin"),
    },
}


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
    print("=" * 70)
    print("DOWNLOAD SOURCE RESOLVER TEST")
    print("=" * 70)

    for researchResult in researchResults:

        modelName = researchResult["candidate"]["name"]

        expected = EXPECTED_RESULTS.get(modelName)

        if not expected:
            print()
            print(f"[SKIP] {modelName}")
            continue

        print()
        print("-" * 70)
        print(f"Testing: {modelName}")
        print("-" * 70)

        try:

            actual = resolveDownloadSource(researchResult)

        except Exception as error:

            failed += 1

            print(f"[FAIL] Resolver error: " f"{error}")

            continue

        fieldsToCompare = [
            "modelName",
            "sourceType",
            "source",
        ]

        testPassed = True

        for field in fieldsToCompare:

            expectedValue = expected.get(field)

            actualValue = actual.get(field)

            if actualValue == expectedValue:

                print(f"[PASS] {field}")

                print(f"       {actualValue}")

            else:

                testPassed = False

                print(f"[FAIL] {field}")

                print(f"       Expected: " f"{expectedValue}")

                print(f"       Actual:   " f"{actualValue}")

        if testPassed:

            passed += 1

            print()
            print(f"[RESULT] PASS - " f"{modelName}")

        else:

            failed += 1

            print()
            print(f"[RESULT] FAIL - " f"{modelName}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Passed: {passed}")

    print(f"Failed: {failed}")

    print(f"Total:  {passed + failed}")

    print("=" * 70)


if __name__ == "__main__":
    main()
