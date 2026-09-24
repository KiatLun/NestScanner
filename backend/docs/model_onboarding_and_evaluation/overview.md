# Overview of Model Onboarding and Evaluation Workflow

```text
                     [Research Agent]
                            │
                            │ 1. Pass a Researched Model
                            ▼
                   [Onboarding Workflow]
                            │
                            │ 1. Download Model
                            │ 2. Upload Model
                            ▼
               [Component Building Workflow]
                            │
                            │ 1. Build new components if needed
                            │ 2. Ensure all component images are available
                            ▼
                [Pipeline Building Workflow]
                            │
                            │ 1. Find all the component images
                            │ 2. Create pipeline yaml
                            ▼
                     [Pipeline Runner]
                            │
                            │ 1. Run pipeline in ClearML
                            ▼
                    [ClearML Execution]
                            │
                            ▼
                  Pipeline succeeds?
                     ┌──────┴──────┐
                    Yes            No
                     │              │
                     ▼              ▼
                [Completed]   [Capture Error]
                                    │
                                    ▼
                             Attempts remaining?
                               ┌────┴────┐
                              Yes        No
                               │          │
                               ▼          ▼
                    [Component Creation  [Failed]
                            Agent]
                               │
                               │ Repaired Component
                               └──────────────►
                            [Start from Pipeline Building Workflow again]
```
---
# Combined Test Guide

## Summary

This test runs the above flow with the **speechbrain-crdnn-rnnlm-librispeech** model.

- The generic HF downloader is expected to be used since no specific downloaders for it
- Own inference component will be created since no existing one

## Steps

### 0. Ensure ClearML and MinIO running

### 1. Ensure ClearML agents are running

```bash
cd services/clearml-agent
./stop_all_agents.sh
bash run_agent.sh
bash run_controller_agent.sh
```

### 2. Refresh EchoForge model info

```bash
cd /path/to/NestScanner/backend
python3 -m app.services.echoforge.model.modelInfoBuilder
```

### 3. Set your ClearML dataset ID

Open:

```text
NestScanner/backend/tests/graph/pipelineBuilding/test_combined.py
```

Update:

```python
DATASET_ID = "YOUR_DATASET_ID"
```

### 4. Run the combined test

```bash
cd /path/to/NestScanner/backend
python3 -m tests.graph.pipelineBuilding.test_combined
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

ClearML should show the pipeline running and completed



## Note for Re-runs
### 1. Remove all created components / scripts
- The inference component folder (with the DockerFile, main.py, requirements.txt)
- The pipeline yaml
- The model folder in .cache

### 2. Remove the model entry in `model_list`
- Depending on which downloader you used, likely ~/echoforge/deployment/model_download/hugging_face_download/model_list

### 3. Refresh EchoForge model info again

```bash
cd /path/to/NestScanner/backend
python3 -m app.services.echoforge.model.modelInfoBuilder
```