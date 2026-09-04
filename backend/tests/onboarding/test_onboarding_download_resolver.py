import json

from app.services.echoforge.onboardingDownloadResolver import (
    resolveOnboardingDownload,
)

EXPECTED_RESULTS = {
    "Qwen3-ASR-1.7B": {
        "sourceType": "huggingface",
        "source": "Qwen/Qwen3-ASR-1.7B",
        "hasUsableDownloader": True,
        "downloader": "hugging_face_download",
        "scope": "generic",
    },
    "Voxtral-Mini-3B-2507": {
        "sourceType": "huggingface",
        "source": "mistralai/Voxtral-Mini-3B-2507",
        "hasUsableDownloader": True,
        "downloader": "voxtral_download",
        "scope": "model-specific",
    },
    "Whisper Medium": {
        "sourceType": "huggingface",
        "source": "openai/whisper-medium",
        "hasUsableDownloader": True,
        "downloader": "whisper_download",
        "scope": "model-specific",
    },
    "Silero VAD": {
        "sourceType": "github",
        "source": "https://github.com/snakers4/silero-vad",
        "hasUsableDownloader": True,
        "downloader": "silero_download",
        "scope": "model-specific",
    },
    "Mega-ASR": {
        "sourceType": "huggingface",
        "source": "zhifeixie/Mega-ASR",
        "hasUsableDownloader": True,
        "downloader": "hugging_face_download",
        "scope": "generic",
    },
    "Example Direct ASR": {
        "sourceType": "directUrl",
        "source": ("https://example.org/models/" "example-asr/model.bin"),
        "hasUsableDownloader": False,
        "downloader": None,
        "scope": None,
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
    print("=" * 80)
    print("ONBOARDING DOWNLOAD RESOLVER TEST")
    print("=" * 80)

    for researchResult in researchResults:

        modelName = researchResult["candidate"]["name"]

        expected = EXPECTED_RESULTS.get(modelName)

        if not expected:
            continue

        print()
        print("-" * 80)
        print(f"Testing: {modelName}")
        print("-" * 80)

        try:
            actual = resolveOnboardingDownload(researchResult)

        except Exception as error:
            failed += 1

            print(f"[FAIL] {error}")

            continue

        fieldsToCompare = [
            "sourceType",
            "source",
            "hasUsableDownloader",
            "downloader",
            "scope",
        ]

        testPassed = True

        for field in fieldsToCompare:

            expectedValue = expected.get(field)

            actualValue = actual.get(field)

            if expectedValue == actualValue:

                print(f"[PASS] {field}: " f"{actualValue}")

            else:

                testPassed = False

                print(f"[FAIL] {field}")

                print(f"       Expected: " f"{expectedValue}")

                print(f"       Actual:   " f"{actualValue}")

        if testPassed:
            passed += 1
            print(f"[RESULT] PASS - {modelName}")

        else:
            failed += 1
            print(f"[RESULT] FAIL - {modelName}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")


if __name__ == "__main__":
    main()
