
# Environment Setup

## 1. EchoForge Setup

### Step 1: Configure the environment

Set up your `.env` file using `sample.env` as a reference.

**Hugging Face access token**
- Create a Hugging Face access token with full access.
- Token setup: https://huggingface.co/settings/tokens

### Step 2: Ensure ClearML and MinIO are running

Ensure that both ClearML and MinIO are running.

For initial installation and configuration, refer to the [EchoForge Setup Guide](https://github.com/aceaigit/echoforge/blob/main/docs/setup.md).

### Step 3: Pull and use the latest EchoForge PR

Pull and use the changes from [EchoForge PR #217](https://github.com/aceaigit/echoforge/pull/217).

---

## 2. NestScanner Setup

### Step 1: Configure the environment

Set up your `.env` file using `sample.env` as a reference.

**GitHub personal access token**
- Create a GitHub personal access token. A fine-grained token can be used.
- Ensure the token has read-write access to the EchoForge repository for pull request creation.
- Token setup: https://github.com/settings/personal-access-tokens

**Hugging Face access token**
- Create a Hugging Face access token with full access.
- Token setup: https://huggingface.co/settings/tokens

---

# Combined Test Guide

## Summary

This test runs the above flow with the **speechbrain-crdnn-rnnlm-librispeech** model.

- The generic HF downloader is expected to be used since no specific downloaders for it
- Own inference component will be created since no existing one

## Steps

### 1. Ensure ClearML agents are running

```bash
cd services/clearml-agent
./stop_all_agents.sh
bash run_agent.sh
bash run_controller_agent.sh
```

### 2. Set your ClearML dataset ID

Open:

```text
NestScanner/backend/tests/graph/pipelineBuilding/test_combined_with_pr.py
```

Update:

```python
DATASET_ID = "YOUR_DATASET_ID"
```

### 3. Run the combined test

```bash
cd /path/to/NestScanner/backend
python3 -m tests.graph.pipelineBuilding.test_combined_with_pr
```

---

## Expected Outputs

A successful run should:

### 1. Update `model_info.json` in NestScanner to include

```json
{
    "source": "speechbrain/asr-crdnn-rnnlm-librispeech",
    "modelListName": "asr-crdnn-rnnlm-librispeech",
    "cacheName": "asr-crdnn-rnnlm-librispeech"
}
```

### 2. Create a model cache folder

```text
~/echoforge/deployment/.cache/asr-crdnn-rnnlm-librispeech
```

### 3. Update `model_list` in ~/echoforge/deployment/model_download/hugging_face_download to include

```text
speechbrain/asr-crdnn-rnnlm-librispeech asr-crdnn-rnnlm-librispeech
```

### 4. ClearML model registry

ClearML model-registry should show the upload.

### 5. Create a new pipeline YAML for asr-crdnn-rnnlm-librispeech at

```text
~/echoforge/pipeline/src/conf/nestscanner/speechbrain_crdnn_rnnlm_librispeech_evaluation.yaml
```

### 6. Create a new `stt_inference_speechbrain` folder

```text
~/echoforge/components/inference_component/stt_inference/stt_inference_speechbrain/
```

with the created:

```text
DockerFile
requirements.txt
main.py
```

### 6. ClearML pipeline execution

ClearML should show the pipeline running and completed (if no errors).

### 7. Pull Request

Under echoforge github, a draft pull request with the created files should appear.

---

## Note for Re-runs

### 1. Remove all created components / scripts

- The inference component folder (with the DockerFile, main.py, requirements.txt)
- The pipeline yaml
- The model folder in .cache

### 2. Remove the model entry in `model_list`

- Depending on which downloader you used, likely ~/echoforge/deployment/model_download/hugging_face_download/model_list
