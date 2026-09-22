FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

RUN apt-get update \
    && apt-get install -y \
        libsndfile1 \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade Python packaging tools before installing dependencies
RUN python3 -m pip install --upgrade \
    pip \
    setuptools \
    wheel

# Install EchoForge base dependencies
COPY base_classes/requirements.txt requirements_base.txt

RUN python3 -m pip install \
    --no-cache-dir \
    -r requirements_base.txt

# Install model-specific dependencies
COPY inference_component/stt_inference/stt_inference_whisper/requirements.txt requirements.txt

RUN python3 -m pip install \
    --no-cache-dir \
    -r requirements.txt

# Copy EchoForge base classes
COPY base_classes base_classes

# Copy inference component contents directly into /app
COPY inference_component/stt_inference/stt_inference_whisper .

ENV LOCAL_PYTHON=/usr/bin/python3
ENV PYTHONPATH=/app