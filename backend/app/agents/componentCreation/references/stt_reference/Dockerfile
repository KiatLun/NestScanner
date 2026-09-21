FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

RUN apt-get update \
    && apt-get install -y libsndfile1 python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY base_classes/requirements.txt requirements_base.txt
RUN pip install --no-cache-dir -r requirements_base.txt

COPY inference_component/stt_inference/stt_inference_whisper/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY base_classes base_classes
COPY inference_component/stt_inference/stt_inference_whisper .

ENV LOCAL_PYTHON=/usr/bin/python3