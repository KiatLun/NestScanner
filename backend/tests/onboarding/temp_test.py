from pprint import pprint

from app.graph.onboarding.workflow import (
    runOnboardingWorkflow,
)

"""
**Model-specific**

Expected behaviours:
1. Should create new modelList entry under whisper_download in echoforge
2. model_info.json in nestscanner should reflect the new whisper-small model entry under whisper_download
3. Model should be saved under deployment/.cache/whisper
"""
# researchResult = {
#     "candidate": {
#         "name": "Whisper Small",
#         "organisation": "OpenAI",
#         "sourceUrl": "https://github.com/openai/whisper",
#         "candidateType": "model",
#     },
#     "isLocallyDeployable": True,
#     "researchEvidence": {
#         "deployabilityEvidence": [
#             {
#                 "source": "huggingface",
#                 "title": "openai/whisper-small",
#                 "url": "https://huggingface.co/openai/whisper-small",
#                 "description": (
#                     "Official Whisper Small "
#                     "Hugging Face repository "
#                     "containing downloadable "
#                     "model weights and "
#                     "configuration files."
#                 ),
#             },
#             {
#                 "source": "github",
#                 "title": "OpenAI Whisper",
#                 "url": "https://github.com/openai/whisper",
#                 "description": (
#                     "Official source code " "repository for OpenAI Whisper."
#                 ),
#             },
#         ],
#         "technicalEvidence": [],
#     },
# }


"""
**Model-specific**

Expected behaviours:
1. Should create new modelList entry under voxtral_download in echoforge
2. model_info.json in nestscanner should reflect the new fun-asr model entry under voxtral_download
3. Model should be saved under deployment/.cache/voxtral
"""
researchResult = {
    "candidate": {
        "name": "Voxtral Mini 4B Realtime 2602",
        "organisation": "Mistral AI",
        "sourceUrl": (
            "https://huggingface.co/" "mistralai/Voxtral-Mini-4B-Realtime-2602"
        ),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": ("mistralai/" "Voxtral-Mini-4B-Realtime-2602"),
                "url": (
                    "https://huggingface.co/"
                    "mistralai/"
                    "Voxtral-Mini-4B-Realtime-2602"
                ),
                "description": (
                    "Official Mistral AI Hugging Face "
                    "repository containing downloadable "
                    "Voxtral Mini 4B Realtime model "
                    "weights and configuration files."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}


"""
**Generic Hugging Face**

Expected behaviours:
1. Should create new modelList entry under hugging_face_download in echoforge
2. model_info.json in nestscanner should reflect the new fun-asr model entry under hugging_face_download
3. Model should be saved under deployment/.cache/Fun-ASR-Nano-2512
"""
# researchResult = {
#     "candidate": {
#         "name": "Fun-ASR-Nano-2512",
#         "organisation": "FunAudioLLM",
#         "sourceUrl": ("https://huggingface.co/" "FunAudioLLM/Fun-ASR-Nano-2512"),
#         "candidateType": "model",
#     },
#     "isLocallyDeployable": True,
#     "researchEvidence": {
#         "deployabilityEvidence": [
#             {
#                 "source": "huggingface",
#                 "title": "FunAudioLLM/Fun-ASR-Nano-2512",
#                 "url": ("https://huggingface.co/" "FunAudioLLM/Fun-ASR-Nano-2512"),
#                 "description": (
#                     "Official Hugging Face repository "
#                     "for the Fun-ASR-Nano-2512 "
#                     "automatic speech recognition model."
#                 ),
#             },
#         ],
#         "technicalEvidence": [],
#     },
# }


"""
**Generic Hugging Face**

Expected behaviours:
1. Should create new modelList entry under hugging_face_download in echoforge
2. model_info.json in nestscanner should reflect the new SenseVoiceSmall model entry under hugging_face_download
3. Model should be saved under deployment/.cache/SenseVoiceSmall
"""
# researchResult = {
#     "candidate": {
#         "name": "SenseVoiceSmall",
#         "organisation": "FunAudioLLM",
#         "sourceUrl": ("https://huggingface.co/" "FunAudioLLM/SenseVoiceSmall"),
#         "candidateType": "model",
#     },
#     "isLocallyDeployable": True,
#     "researchEvidence": {
#         "deployabilityEvidence": [
#             {
#                 "source": "huggingface",
#                 "title": "FunAudioLLM/SenseVoiceSmall",
#                 "url": ("https://huggingface.co/" "FunAudioLLM/SenseVoiceSmall"),
#                 "description": (
#                     "Official Hugging Face repository "
#                     "for the SenseVoiceSmall speech "
#                     "recognition model."
#                 ),
#             },
#         ],
#         "technicalEvidence": [],
#     },
# }


"""
**Cant for both model-specific and generic HF**

Expected behaviours:
1. SHOULD NOT have a new modelList entry under any downloader folders in echoforge
2. SHOULD NOT be reflected in model_info.json
3. SHOULD NOT have any entry in deployment/.cache/
"""
# researchResult = {
#     "candidate": {
#         "name": "DeepSpeech 0.9.3",
#         "organisation": "Mozilla",
#         "sourceUrl": ("https://github.com/mozilla/DeepSpeech"),
#         "candidateType": "model",
#     },
#     "isLocallyDeployable": True,
#     "researchEvidence": {
#         "deployabilityEvidence": [
#             {
#                 "source": "github",
#                 "title": "Mozilla DeepSpeech 0.9.3",
#                 "url": ("https://github.com/" "mozilla/DeepSpeech/releases/tag/v0.9.3"),
#                 "description": (
#                     "Official Mozilla DeepSpeech release "
#                     "containing downloadable pretrained "
#                     "speech recognition model files."
#                 ),
#             },
#         ],
#         "technicalEvidence": [],
#     },
# }


def main():

    print()
    print("=" * 60)
    print("ONBOARDING WORKFLOW TEST")
    print("=" * 60)

    result = runOnboardingWorkflow(researchResult)

    print()
    print("=" * 60)
    print("ONBOARDING RESULT")
    print("=" * 60)

    pprint(
        result,
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()
