from app.services.echoforge.onboardingDownloadResolver import (
    resolveOnboardingDownload,
)

from app.services.echoforge.modelDownloader import (
    downloadModel,
)


def executeOnboardingDownload(
    researchResult: dict,
) -> dict:

    downloadDecision = resolveOnboardingDownload(researchResult)

    if not downloadDecision["hasUsableDownloader"]:

        return {
            **downloadDecision,
            "status": "needs-downloader",
        }

    downloadResult = downloadModel(
        downloader={
            "downloader": downloadDecision["downloader"],
            "scope": downloadDecision["scope"],
            "sourceType": downloadDecision["sourceType"],
            "cacheName": downloadDecision["cacheName"],
        },
        modelName=downloadDecision["modelName"],
        sourceType=downloadDecision["sourceType"],
        source=downloadDecision["source"],
        cacheName=downloadDecision["cacheName"],
    )

    return {
        **downloadDecision,
        "status": "downloaded",
        "cacheName": downloadResult.get("cacheName"),
        "cachePath": downloadResult.get("cachePath"),
    }
