researchAgentOutput = {}


"""
**Model-specific**

Expected behaviours:
1. Should create new modelList entry under whisper_download in echoforge
2. model_info.json in nestscanner should reflect the new whisper-small model entry under whisper_download
3. Model should be saved under deployment/.cache/whisper
"""
researchAgentOutput["whisper-small"] = {
    "candidate": {
        "name": "Whisper Small",
        "organisation": "OpenAI",
        "sourceUrl": "https://github.com/openai/whisper",
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": "openai/whisper-small",
                "url": "https://huggingface.co/openai/whisper-small",
                "description": (
                    "Official Whisper Small "
                    "Hugging Face repository "
                    "containing downloadable "
                    "model weights and "
                    "configuration files."
                ),
            },
            {
                "source": "github",
                "title": "OpenAI Whisper",
                "url": "https://github.com/openai/whisper",
                "description": (
                    "Official source code " "repository for OpenAI Whisper."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}

"""
**Model-specific**

Expected behaviours:
1. Should create a new modelList entry under the appropriate FunASR / Paraformer downloader in EchoForge
2. model_info.json in NestScanner should reflect the new paraformer-en model entry
3. Model should be saved under deployment/.cache/paraformer
4. Component Building should not find an existing Paraformer inference component
5. Component Creation Agent should generate stt_inference_paraformer
"""

researchAgentOutput["paraformer-en"] = {
    "candidate": {
        "name": "Paraformer EN",
        "organisation": "FunASR",
        "sourceUrl": "https://huggingface.co/funasr/paraformer-en",
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": "funasr/paraformer-en",
                "url": "https://huggingface.co/funasr/paraformer-en",
                "description": (
                    "Official FunASR Paraformer EN "
                    "Hugging Face repository "
                    "containing downloadable "
                    "model weights, configuration, "
                    "tokenizer files, and other "
                    "artifacts required for "
                    "local inference."
                ),
            },
            {
                "source": "github",
                "title": "FunASR",
                "url": "https://github.com/modelscope/FunASR",
                "description": (
                    "Official FunASR source code "
                    "repository containing the "
                    "inference framework and "
                    "Paraformer support."
                ),
            },
        ],
        "technicalEvidence": [
            {
                "source": "huggingface",
                "title": "Paraformer EN Model Card",
                "url": "https://huggingface.co/funasr/paraformer-en",
                "description": (
                    "Paraformer EN is an offline "
                    "English automatic speech "
                    "recognition model that can "
                    "be loaded through the FunASR "
                    "AutoModel interface and run "
                    "locally using model.generate()."
                ),
            },
        ],
    },
}

"""
**Model-specific**

Expected behaviours:
1. Should create a new modelList entry under the appropriate Hugging Face downloader in EchoForge
2. model_info.json in NestScanner should reflect the new wav2vec2-base-960h model entry
3. Model should be saved under the appropriate deployment/.cache model directory
4. Component Building should not find an existing Wav2Vec2 inference component
5. Component Creation Agent should generate stt_inference_wav2vec2
"""

researchAgentOutput["wav2vec2-base-960h"] = {
    "candidate": {
        "name": "Wav2Vec2 Base 960h",
        "organisation": "Meta",
        "sourceUrl": ("https://huggingface.co/" "facebook/wav2vec2-base-960h"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": ("facebook/" "wav2vec2-base-960h"),
                "url": ("https://huggingface.co/" "facebook/" "wav2vec2-base-960h"),
                "description": (
                    "Official Hugging Face "
                    "repository containing "
                    "downloadable Wav2Vec2 "
                    "model weights, processor "
                    "configuration, tokenizer "
                    "files, and local inference "
                    "support."
                ),
            },
        ],
        "technicalEvidence": [
            {
                "source": "huggingface",
                "title": ("Wav2Vec2 Base 960h " "Model Card"),
                "url": ("https://huggingface.co/" "facebook/" "wav2vec2-base-960h"),
                "description": (
                    "Wav2Vec2 Base 960h is an "
                    "English CTC speech "
                    "recognition model. "
                    "Inference uses a "
                    "Wav2Vec2 processor and "
                    "CTC model, followed by "
                    "argmax decoding of model "
                    "logits into text."
                ),
            },
        ],
    },
}

"""
**Model-specific**

Expected behaviours:
1. Should create a new modelList entry under the appropriate Hugging Face downloader in EchoForge
2. model_info.json in NestScanner should reflect the new speechbrain-crdnn-rnnlm-librispeech model entry
3. Model should be saved under the appropriate deployment/.cache model directory
4. Component Building should not find an existing SpeechBrain inference component
5. Component Creation Agent should generate stt_inference_speechbrain
"""

researchAgentOutput["speechbrain-crdnn-rnnlm-librispeech"] = {
    "candidate": {
        "name": "SpeechBrain CRDNN RNNLM LibriSpeech",
        "organisation": "SpeechBrain",
        "sourceUrl": (
            "https://huggingface.co/" "speechbrain/asr-crdnn-rnnlm-librispeech"
        ),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": ("speechbrain/" "asr-crdnn-rnnlm-librispeech"),
                "url": (
                    "https://huggingface.co/"
                    "speechbrain/"
                    "asr-crdnn-rnnlm-librispeech"
                ),
                "description": (
                    "Official SpeechBrain ASR "
                    "repository containing "
                    "downloadable acoustic model, "
                    "language model, tokenizer, "
                    "normalizer, and hyperparameter "
                    "files required for local "
                    "speech recognition."
                ),
            },
            {
                "source": "github",
                "title": "SpeechBrain",
                "url": ("https://github.com/" "speechbrain/speechbrain"),
                "description": (
                    "Official SpeechBrain toolkit "
                    "providing pretrained ASR "
                    "interfaces and local inference "
                    "support."
                ),
            },
        ],
        "technicalEvidence": [
            {
                "source": "huggingface",
                "title": ("SpeechBrain CRDNN RNNLM " "LibriSpeech Model Card"),
                "url": (
                    "https://huggingface.co/"
                    "speechbrain/"
                    "asr-crdnn-rnnlm-librispeech"
                ),
                "description": (
                    "English automatic speech "
                    "recognition model using a "
                    "CRDNN acoustic model with "
                    "CTC/attention decoding and "
                    "an RNN language model. "
                    "Local inference is provided "
                    "through SpeechBrain's "
                    "EncoderDecoderASR interface."
                ),
            },
        ],
    },
}

"""
**Model-specific**

Expected behaviours:
1. Should create a new modelList entry under the appropriate Hugging Face downloader in EchoForge
2. model_info.json in NestScanner should reflect the new hubert-large-ls960-ft model entry
3. Model should be saved under the appropriate deployment/.cache model directory
4. Component Building should not find an existing HuBERT inference component
5. Component Creation Agent should generate stt_inference_hubert
"""

researchAgentOutput["hubert-large-ls960-ft"] = {
    "candidate": {
        "name": "HuBERT Large LS960 FT",
        "organisation": "Meta",
        "sourceUrl": ("https://huggingface.co/" "facebook/hubert-large-ls960-ft"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": ("facebook/" "hubert-large-ls960-ft"),
                "url": ("https://huggingface.co/" "facebook/" "hubert-large-ls960-ft"),
                "description": (
                    "Official HuBERT ASR model "
                    "repository containing "
                    "downloadable model weights, "
                    "processor configuration, "
                    "tokenizer files, and other "
                    "artifacts required for "
                    "local inference."
                ),
            },
            {
                "source": "github",
                "title": "Hugging Face Transformers",
                "url": ("https://github.com/" "huggingface/transformers"),
                "description": (
                    "Transformers provides "
                    "HuBERT and CTC model support "
                    "for loading and running "
                    "speech recognition models "
                    "locally."
                ),
            },
        ],
        "technicalEvidence": [
            {
                "source": "huggingface",
                "title": ("HuBERT Large LS960 FT " "Model Card"),
                "url": ("https://huggingface.co/" "facebook/" "hubert-large-ls960-ft"),
                "description": (
                    "HuBERT Large LS960 FT is "
                    "an English automatic speech "
                    "recognition model fine-tuned "
                    "with a CTC objective. "
                    "It can be loaded locally "
                    "using AutoProcessor and "
                    "AutoModelForCTC, with "
                    "predictions decoded from "
                    "the model logits."
                ),
            },
        ],
    },
}

"""
**Model-specific**

Expected behaviours:
1. Should create a new modelList entry under the appropriate downloader in EchoForge
2. model_info.json in NestScanner should reflect the new SpeechBrain CommonVoice EN model entry
3. Model should be saved under the appropriate deployment/.cache model directory
4. Component Building should not find an existing SpeechBrain inference component
5. Component Creation Agent should generate stt_inference_speechbrain
"""

researchAgentOutput["speechbrain-commonvoice-en"] = {
    "candidate": {
        "name": "SpeechBrain Wav2Vec2 CommonVoice EN",
        "organisation": "SpeechBrain",
        "sourceUrl": (
            "https://huggingface.co/" "speechbrain/asr-wav2vec2-commonvoice-en"
        ),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": ("speechbrain/" "asr-wav2vec2-commonvoice-en"),
                "url": (
                    "https://huggingface.co/"
                    "speechbrain/"
                    "asr-wav2vec2-commonvoice-en"
                ),
                "description": (
                    "Official SpeechBrain ASR "
                    "repository containing model "
                    "checkpoints, tokenizer, "
                    "hyperparameter configuration, "
                    "and other files needed for "
                    "local speech recognition."
                ),
            },
            {
                "source": "github",
                "title": "SpeechBrain",
                "url": ("https://github.com/" "speechbrain/speechbrain"),
                "description": (
                    "Official SpeechBrain toolkit "
                    "providing pretrained ASR "
                    "interfaces and local inference "
                    "support."
                ),
            },
        ],
        "technicalEvidence": [
            {
                "source": "huggingface",
                "title": ("SpeechBrain Wav2Vec2 " "CommonVoice EN Model Card"),
                "url": (
                    "https://huggingface.co/"
                    "speechbrain/"
                    "asr-wav2vec2-commonvoice-en"
                ),
                "description": (
                    "The model is an English "
                    "automatic speech recognition "
                    "system using Wav2Vec2 with "
                    "CTC. The documented local "
                    "inference path loads the "
                    "pretrained SpeechBrain ASR "
                    "interface and transcribes "
                    "audio locally."
                ),
            },
        ],
    },
}

"""
**Model-specific**

Expected behaviours:
1. Should create new modelList entry under voxtral_download in echoforge
2. model_info.json in nestscanner should reflect the new voxtral model entry under voxtral_download
3. Model should be saved under deployment/.cache/voxtral
"""
researchAgentOutput["voxtral-mini-4b-realtime-2602"] = {
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
researchAgentOutput["fun-asr-nano-2512"] = {
    "candidate": {
        "name": "Fun-ASR-Nano-2512",
        "organisation": "FunAudioLLM",
        "sourceUrl": ("https://huggingface.co/" "FunAudioLLM/Fun-ASR-Nano-2512"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": "FunAudioLLM/Fun-ASR-Nano-2512",
                "url": ("https://huggingface.co/" "FunAudioLLM/Fun-ASR-Nano-2512"),
                "description": (
                    "Official Hugging Face repository "
                    "for the Fun-ASR-Nano-2512 "
                    "automatic speech recognition model."
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
2. model_info.json in nestscanner should reflect the new SenseVoiceSmall model entry under hugging_face_download
3. Model should be saved under deployment/.cache/SenseVoiceSmall
"""
researchAgentOutput["sensevoice-small"] = {
    "candidate": {
        "name": "SenseVoiceSmall",
        "organisation": "FunAudioLLM",
        "sourceUrl": ("https://huggingface.co/" "FunAudioLLM/SenseVoiceSmall"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": "FunAudioLLM/SenseVoiceSmall",
                "url": ("https://huggingface.co/" "FunAudioLLM/SenseVoiceSmall"),
                "description": (
                    "Official Hugging Face repository "
                    "for the SenseVoiceSmall speech "
                    "recognition model."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}


"""
**Cant for both model-specific and generic HF**

Expected behaviours:
1. SHOULD NOT have a new modelList entry under any downloader folders in echoforge
2. SHOULD NOT be reflected in model_info.json
3. SHOULD NOT have any entry in deployment/.cache/
"""
researchAgentOutput["deepspeech-0.9.3"] = {
    "candidate": {
        "name": "DeepSpeech 0.9.3",
        "organisation": "Mozilla",
        "sourceUrl": ("https://github.com/mozilla/DeepSpeech"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "github",
                "title": "Mozilla DeepSpeech 0.9.3",
                "url": ("https://github.com/" "mozilla/DeepSpeech/releases/tag/v0.9.3"),
                "description": (
                    "Official Mozilla DeepSpeech release "
                    "containing downloadable pretrained "
                    "speech recognition model files."
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
2. model_info.json in nestscanner should reflect the new qwen3-asr-1.7b model entry under hugging_face_download
3. Model should be saved under deployment/.cache/qwen3-asr-1.7b
"""
researchAgentOutput["qwen3-asr-1.7b"] = {
    "candidate": {
        "name": "Qwen3-ASR-1.7B",
        "organisation": "Qwen",
        "sourceUrl": ("https://github.com/QwenLM/Qwen3-ASR"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": "Qwen/Qwen3-ASR-1.7B",
                "url": ("https://huggingface.co/" "Qwen/Qwen3-ASR-1.7B"),
                "description": (
                    "Official Qwen3-ASR 1.7B model "
                    "repository containing downloadable "
                    "model weights."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}


"""
**Model-specific**

Expected behaviours:
1. Should create new modelList entry under voxtral_download in echoforge
2. model_info.json in nestscanner should reflect the new voxtral-mini-3b-2507 model entry under voxtral_download
3. Model should be saved under deployment/.cache/voxtral
"""
researchAgentOutput["voxtral-mini-3b-2507"] = {
    "candidate": {
        "name": "Voxtral-Mini-3B-2507",
        "organisation": "Mistral AI",
        "sourceUrl": ("https://huggingface.co/" "mistralai/Voxtral-Mini-3B-2507"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": ("mistralai/Voxtral-Mini-3B-2507"),
                "url": ("https://huggingface.co/" "mistralai/Voxtral-Mini-3B-2507"),
                "description": (
                    "Official Mistral AI Hugging Face "
                    "repository containing the model "
                    "weights."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}


"""
**Model-specific**

Expected behaviours:
1. Should create new modelList entry under whisper_download in echoforge
2. model_info.json in nestscanner should reflect the new whisper-medium model entry under whisper_download
3. Model should be saved under deployment/.cache/whisper
"""
researchAgentOutput["whisper-medium"] = {
    "candidate": {
        "name": "Whisper Medium",
        "organisation": "OpenAI",
        "sourceUrl": "https://github.com/openai/whisper",
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": "openai/whisper-medium",
                "url": ("https://huggingface.co/" "openai/whisper-medium"),
                "description": (
                    "Official Whisper Medium model "
                    "repository containing model weights."
                ),
            },
            {
                "source": "github",
                "title": "OpenAI Whisper",
                "url": "https://github.com/openai/whisper",
                "description": ("Official source code repository " "for Whisper."),
            },
        ],
        "technicalEvidence": [],
    },
}


"""
**Repository-based model**

Expected behaviours:
1. Should identify that the model is not provided through the generic Hugging Face downloader
2. Onboarding should resolve whether an existing model-specific downloader can handle Silero VAD
3. If no compatible downloader exists, status should be downloader-required
"""
researchAgentOutput["silero-vad"] = {
    "candidate": {
        "name": "Silero VAD",
        "organisation": "Silero",
        "sourceUrl": ("https://github.com/snakers4/silero-vad"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "github",
                "title": "Silero VAD",
                "url": ("https://github.com/" "snakers4/silero-vad"),
                "description": (
                    "Official Silero VAD repository. "
                    "The model is obtained through the "
                    "project repository and its model "
                    "loading procedure."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}


"""
**Generic Hugging Face**

Expected behaviours:
1. Should determine that the GitHub repository contains the code while the model weights are hosted on Hugging Face
2. Should create new modelList entry under hugging_face_download in echoforge
3. model_info.json in nestscanner should reflect the new mega-asr model entry under hugging_face_download
4. Model should be saved under deployment/.cache/mega-asr
"""
researchAgentOutput["mega-asr"] = {
    "candidate": {
        "name": "Mega-ASR",
        "organisation": None,
        "sourceUrl": ("https://github.com/xzf-thu/Mega-ASR"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "github",
                "title": "xzf-thu/Mega-ASR",
                "url": ("https://github.com/" "xzf-thu/Mega-ASR"),
                "description": (
                    "Official Mega-ASR code repository. "
                    "Model weights are available separately "
                    "on Hugging Face."
                ),
            },
        ],
        "technicalEvidence": [
            {
                "source": "huggingface",
                "title": "zhifeixie/Mega-ASR",
                "url": ("https://huggingface.co/" "zhifeixie/Mega-ASR"),
                "description": ("Official Mega-ASR model weights."),
            },
        ],
    },
}


"""
**Cant for both model-specific and generic HF**

Expected behaviours:
1. SHOULD NOT create a new modelList entry under the generic Hugging Face downloader
2. SHOULD NOT attempt to treat the direct model.bin URL as a Hugging Face repository
3. Should return downloader-required if no existing model-specific downloader can handle the model
"""
researchAgentOutput["example-direct-asr"] = {
    "candidate": {
        "name": "Example Direct ASR",
        "organisation": "Example Research",
        "sourceUrl": ("https://example.org/example-asr"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "web",
                "title": "Example Direct ASR Download",
                "url": ("https://example.org/models/" "example-asr/model.bin"),
                "description": (
                    "The official model weights are "
                    "provided directly as a downloadable "
                    "model.bin file."
                ),
            },
        ],
        "technicalEvidence": [],
    },
}
