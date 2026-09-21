# Component Guide

> **New to echoforge?** Do the [tutorial](tutorial.md) first. This guide assumes you have the system running and understand the basic data flow.

---

## The mental model

This repo is production. Only code that lives here runs in the production environment. That means:

- **Your experiment repo is your sandbox.** Run notebooks, ad-hoc scripts, one-off experiments — all fine there.
- **Echoforge is where experiments become components.** Once something works, you package it here, test it in the pipeline, and it becomes available for MLOps to deploy.

The flow from experiment to production:

```
Your repo (experiments)
    │
    │  experiment works?
    ▼
Package as a component in echoforge
    │
    │  upload data    → done via deployment/ folder (Step 1)
    │  upload model   → done via deployment/ folder (Step 2)
    │
    ▼
Write component scripts using base classes (Step 3)
    │
    ▼
Wire components into a pipeline YAML (Step 4)
    │
    ▼
Run tests (Step 5)
    │
    ▼
MLOps brings components offline (biweekly cadence)
```

---

## Table of contents

1. [Upload your dataset](#step-1-upload-your-dataset)
2. [Upload your model](#step-2-upload-your-model)
3. [Write your component scripts](#step-3-write-your-component-scripts)
4. [Wire components into a pipeline YAML](#step-4-wire-components-into-a-pipeline-yaml)
5. [Testing](#step-5-testing)
6. [Push images to GoHarbor](#step-6-push-images-to-goharbor-optional)
7. [Visualize data lineage with Marquez (optional)](#step-7-visualize-data-lineage-with-marquez-optional)
8. [Reference: directory structure](#reference-directory-structure)
9. [Reference: pipeline variable syntax](#reference-pipeline-variable-syntax)
10. [Reference: YAML stage fields](#reference-yaml-stage-fields)

---

## Step 1: Upload your dataset

Pipeline components consume datasets that already exist in ClearML — they don't read local files. Before running any pipeline you must upload your data. Dataset uploads live in the `deployment/` folder alongside model uploads, so that both data and models follow the same two-phase workflow and can be transferred together to air-gapped environments.

### 1.1 Prepare your manifest

Echoforge datasets follow a standard manifest format (`dataset.json`):

```json
{
  "dataset": {
    "dataset_name": "my_dataset",
    "dataset_description": "Description of the dataset",
    "dataset_task": "Automatic Speech Recognition",
    "last_updated": "YYYY-MM-DD"
  },
  "items": [
    {
      "filename": "audio/file_001.wav",
      "file_metadata": {
        "original_name": "file_001.wav",
        "file_size": 16000,
        "file_length": 5.2
      },
      "segments": [
        {
          "start": 0.0,
          "end": 5.2,
          "speaker": "speaker_1",
          "raw_text": "hello world",
          "processed_transcript": "hello world",
          "language": "en",
          "keyword": [],
          "estimated_snr": 0.0,
          "audio_characteristics": []
        }
      ]
    }
  ]
}
```

**Segment fields** are defined centrally in `BaseSegmentSchema` (`components/base_classes/base_segment_schema.py`). See [base-classes.md](base-classes.md) for the full field reference.

### 1.2 Write an upload script

**Where to put it:** `deployment/simulated_data/<data_name>` — alongside model uploads, so that datasets and models follow the same two-phase workflow and can be transferred together to airgap environments.

For reference, the existing upload scripts are:
- `deployment/simulate_data/upload_atco2_to_clearml.py` — tutorial dataset upload

Use `DatasetUploader` from `components/base_classes/helper/data_uploader.py`:

```python
import argparse
import json
from datetime import datetime
from clearml import Task
from base_classes.helper.data_uploader import DatasetUploader

def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date '{s}' — expected YYYY-MM-DD (e.g. 2026-01-01)")

def main():
    task = Task.init(
        project_name="my_project",
        task_name="upload_my_dataset",
        task_type="data_processing",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, type=valid_date, help="Date to set as last_updated in dataset.json (YYYY-MM-DD)")
    args = parser.parse_args()

    with open("dataset.json") as f:
        manifest = json.load(f)

    manifest["dataset"]["last_updated"] = args.date

    uploader = DatasetUploader()
    dataset_id = uploader.upload(
        dataset_name="my_dataset",
        project="my_project",
        manifest=manifest,
        tags=["my_tag"],
    )
    print(f"Dataset uploaded: {dataset_id}")

if __name__ == "__main__":
    main()
```

What `DatasetUploader.upload()` does under the hood:

1. **Hashes each audio file** (MD5) and uploads to MinIO at `raw/<prefix>/<hash>` — deduplicated and content-addressed. If the hash already exists, the upload is skipped.
2. **Updates each manifest entry** with a `remote_uri` pointing to the content-addressed location.
3. **Stores the manifest** in MinIO at `manifests/<dataset-id>/dataset.json`.
4. **Registers a ClearML Dataset** with name, project, tags, and version.

### 1.3 Run the upload

Build the tutorial Docker image (or your own) and run the upload script:

```bash
# Build (if not already built)
docker build -t echoforge_tutorial -f pipeline/tutorial/Dockerfile .

# Copy ClearML credentials
cp ./services/clearml-agent/clearml.env ./pipeline/tutorial/clearml.env

# Run your upload script (from deployment/simulate_data/ where your script and data live)
docker run --rm \
  -v ./deployment/simulate_data:/app/simulate_data \
  -w /app/simulate_data \
  --env-file ./pipeline/tutorial/clearml.env \
  echoforge_tutorial python3 upload_my_dataset.py --date 2026-01-01
```

### 1.4 Verify in ClearML

Go to http://localhost:8080/datasets and confirm your dataset appears with the correct name, project, and tags.

> **Tip:** For a working example, see `deployment/simulate_data/upload_atco2_to_clearml.py` and `deployment/simulate_data/generate_atco2_dataset.py`.

---

## Step 2: Upload your model

Models are uploaded to the ClearML model registry via the `deployment/` workflow.

### Why models are handled this way

Echoforge is designed to run in **air-gapped (offline) environments** where the production machines have no internet access. The model workflow is built around this constraint:

1. **Two-phase process** — downloading (internet-required) and uploading (ClearML-required) are separate steps. An online machine downloads models, then the entire `deployment/` folder is transferred to the air-gapped machine where models are uploaded to the local ClearML registry.
2. **Content hash tracking** — `models_download.py` hashes the content of each model's `dockerfile` + `download.py`. If neither file has changed, the model is already cached correctly and the download is skipped. This prevents redundant multi-gigabyte downloads when nothing has changed.
3. **Upload state tracking** — `models_upload/model_state.json` records the content hash uploaded per model. Re-running is safe: unchanged models are skipped automatically.
4. **Two roles** — `--deployment` flag distinguishes deployers (state is written) from developers (state is never written, so developer runs don't affect the airgap build record).

### 2.1 Use the deployment model workflow

**To add a new model:**

1. **Create a download folder** in `deployment/model_download/<your_model>/`:

   ```
   deployment/model_download/
   └── my_model_download/
       ├── dockerfile          (or dockerfile.ref — see below)
       └── download.py
   ```

   `download.py` must subclass `BaseModelDownloader` from `base_downloader.py`. The `model_name` property sets the subdirectory under `.cache/` where files are stored:

   ```python
   from pathlib import Path
   from base_downloader import BaseModelDownloader

   class MyModelDownloader(BaseModelDownloader):

       @property
       def model_name(self) -> str:
           return "my_model_download"   # → deployment/.cache/my_model_download/

       def download(self, cache_dir: Path) -> None:
           from huggingface_hub import snapshot_download
           snapshot_download(repo_id="my-org/my-model", local_dir=str(cache_dir))

   if __name__ == "__main__":
       MyModelDownloader().run()
   ```

   `dockerfile` — build context is always `model_download/` so `base_downloader.py` is accessible:

   ```dockerfile
   FROM python:3.12-slim
   RUN pip install huggingface_hub
   WORKDIR /app
   COPY base_downloader.py .
   COPY my_model_download/download.py .
   CMD ["python", "download.py"]
   ```

   **Reusing a Dockerfile:** if your model can share an existing Dockerfile, create a `dockerfile.ref` file instead containing a repo-relative path to the shared Dockerfile:

   ```
   deployment/model_download/shared/python-hf-downloader.dockerfile
   ```

   `models_download.py` resolves the reference automatically for both building and hash tracking.

Both scripts use only the Python standard library — all heavy dependencies run inside Docker. No pip installs needed on the host.

2. **Download and upload (developer mode):**

   ```bash
   # Download your model only (cache stored, state NOT recorded)
   cd deployment/model_download
   python models_download.py --name my_model_download

   # Upload to ClearML (state NOT recorded)
   cd deployment/models_upload
   python models_upload.py --name my_model_download \
     --project my-model-registry \
     --env-file ../../pipeline/tutorial/clearml.env
   ```

3. **Download and upload (deployer mode — records state for airgap build):**

   ```bash
   # Download (writes model_download/model_state.json)
   cd deployment/model_download
   python models_download.py --name my_model_download --deployment

   # Upload (writes models_upload/model_state.json)
   cd deployment/models_upload
   python models_upload.py --deployment --env-file ../../pipeline/tutorial/clearml.env
   ```

   Flags for `models_download.py`:

   | Flag                          | Effect                                                |
   | ----------------------------- | ----------------------------------------------------- |
   | `--name my_model_download`    | Process a single model only                           |
   | `--deployment`                | Write state to `model_state.json` after download      |
   | `--force`                     | Re-download even if cache already exists              |
   | `--dry-run`                   | Preview without building images or running containers |

   Flags for `models_upload.py`:

   | Flag                          | Effect                                                |
   | ----------------------------- | ----------------------------------------------------- |
   | `--name my_model_download`    | Upload a specific model only (developer mode)         |
   | `--model-name "my-model"`     | Override the ClearML model name (default: folder name)|
   | `--project my-model-registry` | ClearML project name (default: `model-registry`)      |
   | `--upload-uri s3://...`       | Upload URI (default: `$CLEARML_UPLOAD_URI`)           |
   | `--env-file clearml.env`      | .env file with ClearML credentials for the container  |
   | `--image models-upload`       | Docker image to run the worker in (default: `models-upload`) |
   | `--deployment`                | Upload all `.cache/` subdirs, write state             |
   | `--force`                     | Re-upload even if content hash matches                |
   | `--dry-run`                   | Preview without uploading                             |

4. **Get the model ID:** Go to http://localhost:8080/projects → your model registry project → Models tab → copy the model ID. You will need this for your pipeline YAML.

---

## Step 3: Write your component scripts

### Component naming convention

```
<model_task>_<component_task>_<model>
```

Where:

- `model_task` = `vad`, `stt`, etc.
- `component_task` = `inference`, `evaluation`, `train`, `train_test_split`
- `model` = `whisper`, `wav2vec`, etc.

Examples: `stt_inference_whisper`, `stt_evaluation`, `stt_training_whisper`

### Choose the right base class

**Always prefer using a base class.** Base classes handle all ClearML/MinIO boilerplate, enforce consistent output schemas, and propagate metadata automatically. If no base class fits your use case, use the helper classes (`DatasetUploader`, `DatasetDownloader`) directly. If your component represents a genuinely new pattern (e.g. training), consider whether it warrants a new base class before writing a one-off script.

| Base class               | Use for                   | You implement                                                          |
| ------------------------ | ------------------------- | ---------------------------------------------------------------------- |
| `BaseInferencePipeline`  | Inference components      | `model_task`, `load_model`, `preprocess`, `infer`, `to_segments`       |
| `BaseTrainTestSplit`     | Data splitting components | `split` (and optionally `add_args`)                                    |
| `BaseEvaluationPipeline` | Evaluation components     | `model_task`, `evaluate` (and optionally `add_args`)                   |

If none of the above fit, use the helper classes directly:

| Helper class        | Use for                               |
| ------------------- | ------------------------------------- |
| `DatasetUploader`   | Uploading datasets to ClearML + MinIO |
| `DatasetDownloader` | Downloading datasets, resolving IDs   |
| `S3Config`          | MinIO connection settings             |

See [base-classes.md](base-classes.md) for the full reference.

> **Training components:** There is no training base class. For a working reference, see `components/training_component/tutorial_whisper_training.py`. Use `DatasetDownloader` and `DatasetUploader` directly and follow the patterns in that file.

### 3.1 Writing an inference component

**Where to put it:** Create a new directory under `components/inference_component/`.

For reference, see the existing implementation: `components/inference_component/tutorial_whisper_inference.py`

```
components/inference_component/
└── stt_inference_my_model/
    ├── dockerfile                       # Optional — use echoforge_tutorial image during dev
    └── stt_inference_my_model.py
```

Subclass `BaseInferencePipeline` and implement the `model_task` property plus four methods:

```python
from components.base_classes.base_inference import BaseInferencePipeline

class MyModelInference(BaseInferencePipeline):

    project_name = "my_project"
    task_name = "stt_my_model"

    @property
    def model_task(self) -> str:
        """Must be one of: "stt", "vad", "fa", "speaker_id", "language_id"."""
        return "stt"

    def load_model(self, model_path, **kwargs):
        """Load your model from a local directory path."""
        self.model = MyModel.from_pretrained(model_path)

    def preprocess(self, audio_path, item, **kwargs):
        """Read audio and prepare model inputs.

        Args:
            audio_path: local path to the downloaded audio file
            item: item component in the dataset manifest
        Returns:
            whatever your infer() method expects as input
        """
        # Always use safe_load_audio to prevent stereo-audio memory crashes
        audio, sr = self.safe_load_audio(audio_path)
        return self.processor(audio, sampling_rate=sr, return_tensors="pt")

    def infer(self, inputs, **kwargs):
        """Run inference on preprocessed inputs.

        Returns:
            raw model output (passed to to_segments)
        """
        with torch.no_grad():
            output = self.model.generate(**inputs)
        return self.processor.batch_decode(output)

    def to_segments(self, inferred, **kwargs):
        """Convert model output to a list of segment dicts.

        Each dict should contain fields from BaseSegmentSchema:
        start, end, raw_text, processed_transcript, speaker, language, etc.
        """
        return [
            {
                "start": 0.0,
                "end": 0.0,
                "raw_text": text,
                "processed_transcript": text,
            }
            for text in inferred
        ]

if __name__ == "__main__":
    pipeline = MyModelInference()
    pipeline.run()
```

**What the base class handles for you:**

- **Safe audio loading** — `self.safe_load_audio(audio_path)` is available to automatically read and collapse multi-channel audio to mono, protecting models from interpreting extra audio channels as massive batch dimensions.
- `--dataset_id` and `--model_id` CLI arguments — each accepts a plain ClearML ID or an artifact reference (`<task_id>:<artifact_name>`)
- `--add_tags` and `--model_type` CLI arguments
- ClearML task initialization and connection
- Model download via `InputModel` (falls back to model name lookup if not a valid ID)
- Background audio file prefetching (3-file buffer via threading) with automatic re-download on stale cache
- ClearML metadata logging (`dataset_id`, `dataset_name`, `dataset_tags`)
- Output upload as a new ClearML dataset and export of the resulting `dataset_id` artifact for downstream stages

**Optional overrides:**

| Method                  | Purpose                                                 |
| ----------------------- | ------------------------------------------------------- |
| `add_args(parser)`      | Add custom CLI arguments                                |
| `get_schema()`          | Return a custom `BaseSegmentSchema` subclass            |
| `postprocess(inferred)` | Post-process after `infer()`, before `to_segments()`    |
| `get_model_info()`      | Return `{"task": "", "model_description": ""}` metadata |

> **Working example:** See `components/inference_component/tutorial_whisper_inference.py`

### 3.2 Writing a data split component

**Where to put it:** Create a new script under `components/data_component/`.

For reference, see the existing implementation: `components/data_component/stt_train_test_split_minio.py`

```
components/data_component/
└── stt_train_test_split_my_strategy.py
```

Subclass `BaseTrainTestSplit` and implement the `split` method:

```python
from components.base_classes.base_train_test_split import BaseTrainTestSplit

class MyTrainTestSplit(BaseTrainTestSplit):

    project_name = "my_project"
    task_name = "my_split_strategy"

    def add_args(self, parser):
        """Add custom CLI arguments. These are forwarded to split() as kwargs."""
        parser.add_argument("--test_ratio", type=float, default=0.2)

    def split(self, manifest, **kwargs):
        """Split manifest items into named subsets.

        Args:
            manifest: the dataset manifest dict with "dataset" and "items" keys
            **kwargs: all custom args from add_args()
        Returns:
            dict of {split_name: manifest_dict} — each with "dataset" and "items"
        """
        test_ratio = kwargs["test_ratio"]
        items = manifest["items"]
        random.shuffle(items)

        split_idx = int(len(items) * (1 - test_ratio))
        train_items = items[:split_idx]
        test_items = items[split_idx:]

        return {
            "train": {"dataset": manifest["dataset"], "items": train_items},
            "test": {"dataset": manifest["dataset"], "items": test_items},
        }

if __name__ == "__main__":
    splitter = MyTrainTestSplit()
    splitter.run()
```

**What the base class handles:**

- `--dataset_id` CLI argument — accepts a plain ClearML ID or an artifact reference (`<task_id>:<artifact_name>`)
- Dataset download via `DatasetDownloader`
- Upload of each split as a new ClearML dataset with tags (source tags + split name) and parent linkage
- **Empty split protection** — if your `split()` returns zero items for a split, that split is skipped (no ClearML dataset created, no ID in output artifacts). A warning is printed. Downstream stages never receive an empty dataset ID.
- Exports one artifact per split: `train_dataset_id`, `test_dataset_id` (etc.) for downstream stages

> **Working examples:** `components/data_component/train_test_split_segment.py` (segment-level split), `components/data_component/stt_train_test_split_minio.py` (duration-based split)

### 3.3 Writing an evaluation component

**Where to put it:** Create a new directory under `components/evaluation_component/`.

For reference, see the existing implementation: `components/evaluation_component/stt_evaluation/stt_evaluation.py`

```
components/evaluation_component/
└── stt_evaluation_my_metric/
    ├── Dockerfile                       # Optional — use echoforge_tutorial image during dev
    └── stt_evaluation_my_metric.py
```

Subclass `BaseEvaluationPipeline` and implement `model_task` plus `evaluate`:

```python
import jiwer
from components.base_classes.base_evaluation import BaseEvaluationPipeline

class MyEvaluation(BaseEvaluationPipeline):

    project_name = "my_project"
    task_name = "my_evaluation"

    @property
    def model_task(self) -> str:
        """Must be one of: "stt", "vad", "speaker_id", "language_id"."""
        return "stt"

    def evaluate(self, paired_data, **kwargs):
        """Compute metrics from paired prediction/reference data.

        Args:
            paired_data: list of dicts, each with:
                - filename: str
                - prediction_text: str (concatenated from segments)
                - reference_text: str (concatenated from segments)
                - prediction_segments: list[dict]
                - reference_segments: list[dict]
        Returns:
            dict matching the evaluation schema
        """
        file_results = []
        all_preds, all_refs = [], []

        for pair in paired_data:
            wer = jiwer.wer(pair["reference_text"], pair["prediction_text"])
            file_results.append({
                "filename": pair["filename"],
                "wer": wer,
                "segmentbased_eval": [],
            })
            all_preds.append(pair["prediction_text"])
            all_refs.append(pair["reference_text"])

        return {
            "dataset_eval": {"wer": jiwer.wer(all_refs, all_preds)},
            "filebased_eval": file_results,
        }

if __name__ == "__main__":
    evaluator = MyEvaluation()
    evaluator.run()
```

**What the base class handles:**

- `--hyp_dataset_id` and `--ref_dataset_id` CLI arguments — the hypothesis (inference output) and reference (ground truth) datasets. Each accepts a plain ClearML dataset ID or an artifact reference (`<task_id>:<artifact_name>`).
- `--add_tags` CLI argument (auto-inherited from upstream inference artifact if not set)
- Downloads both manifests via `DatasetDownloader`
- Pairs predictions with ground truth by filename
- Text extraction from segments (override `extract_prediction_text` / `extract_reference_text` to customize)
- Uploads `evaluation_results` artifact with model and dataset metadata propagated from inference
- **Empty dataset guard** — skips evaluation (with a warning) if the inference artifact has no items or if no filenames match the ground-truth manifest. The pipeline continues; only the affected dataset is skipped.

> **Working example:** See `components/evaluation_component/stt_evaluation/stt_evaluation.py`

### 3.4 Dockerfile requirements

Every component Docker image must install ClearML and set `LOCAL_PYTHON`:

```dockerfile
FROM python:3.12-slim

# Install your dependencies
RUN pip install clearml clearml-agent torch soundfile jiwer
# ... add your model-specific dependencies

# Required: ClearML agent needs to know the Python path
ENV LOCAL_PYTHON=python3

COPY . /app
WORKDIR /app
```

> **Tip:** If your component runs inside the `echoforge_tutorial` image during development, you can skip creating a separate Dockerfile until you're ready to deploy.

---

## Step 4: Wire components into a pipeline YAML

Once your component scripts exist, connect them via a YAML config file.

**Where to put it:** `pipeline/src/conf/<your_pipeline_name>.yaml`

For reference, see the existing configs:

- `pipeline/src/conf/tutorial_full_chain.yaml` — split → inference → evaluation
- `pipeline/src/conf/tutorial_data_pipeline.yaml` — data split only
- `pipeline/src/conf/tutorial_model_inference.yaml` — inference only
- `pipeline/src/conf/example_pipeline.yaml` — 5-stage train + evaluate example

### 4.1 YAML structure

```yaml
project_name: my_project

# Optional: env file injected into every container (needed for MinIO credentials)
environment: /path/to/echoforge/services/clearml-agent/clearml.env

# Optional: mount local cache directories into agent containers
mounts:
  - /home/user/.cache/huggingface:/root/.cache/huggingface

# Datasets to process — resolved once at pipeline start by main.py
datasets:
  dataset_ids:        # explicit IDs (can also use <task_id>:<artifact_name> references)
    - abc123def456
  tags:               # find all datasets tagged with these values
    - my_tag
  exclude_tags:       # exclude any datasets that also carry these tags
    - train
    - test

stages:
  stage_name:
    image_name: my_image:latest  # Docker image containing your script
    task_type: inference          # training / inference / data_processing / testing
    entry_point: /app/my_script.py
    working_dir: /app
    parents:                      # stages that must complete before this one starts
      - some_other_stage
    parameter_override:
      Args/my_arg: some_value     # overrides argparse args (prefix: Args/)
      General/my_config_key: val  # overrides config values (prefix: General/)
```

> **Important:** Always use the `environment` key when running pipelines locally. MinIO credentials are not forwarded automatically.

### 4.2 Scatter and gather: running one stage per dataset

The `datasets` block in the YAML is resolved before any stage runs. `main.py` calls `resolve_stages()` which rewrites stages based on two special placeholder syntaxes.

**Scatter (`${datasets}`)** — creates one copy of the stage per dataset, renaming each to `<stage_name>/<dataset_name>`:

```yaml
datasets:
  tags:
    - atco2

stages:
  my_split:
    image_name: my_image:latest
    task_type: data_processing
    entry_point: /app/data_component/my_split.py
    parameter_override:
      Args/dataset_id: "${datasets}"    # replaced with one dataset ID per resolved dataset
```

**Downstream scatter** — any stage that lists a scattered stage as a parent, or references it in `parameter_override`, is automatically scattered too:

```yaml
  my_inference:
    image_name: my_image:latest
    task_type: inference
    entry_point: /app/inference_component/my_inference.py
    parents:
      - my_split                         # my_split is scattered → my_inference is too
    parameter_override:
      Args/dataset_id: "${my_split.id}:test_dataset_id"   # resolved per dataset
      Args/model_id: <your-model-id>
```

**Gather (`${datasets[*]}` or `${parent[*]}`)** — aggregates all scattered iterations into a single JSON list. Use this for stages that need to process all datasets together (e.g. reporting):

```yaml
  my_report:
    image_name: my_image:latest
    task_type: testing
    entry_point: /app/evaluation_component/my_report.py
    parents:
      - my_inference                     # waits for ALL scattered inference stages
    parameter_override:
      Args/dataset_ids: "${my_inference[*].id}:dataset_id"   # JSON list of all dataset IDs
```

### 4.3 Example: full component chain (split → inference → evaluation)

This is the standard three-stage chain. Copy and adapt for your use case:

```yaml
project_name: my_project
environment: /path/to/echoforge/services/clearml-agent/clearml.env

datasets:
  tags:
    - my_tag
  exclude_tags:
    - train
    - test

stages:
  # Stage 1: Split each dataset into train/test
  my_train_test_split:
    image_name: my_image:latest
    task_type: data_processing
    entry_point: /app/data_component/stt_train_test_split_minio.py
    parameter_override:
      Args/dataset_id: "${datasets}"     # one split task per resolved dataset

  # Stage 2: Run inference on each test split
  my_inference:
    image_name: my_image:latest
    task_type: inference
    entry_point: /app/inference_component/stt_inference_my_model/stt_inference_my_model.py
    parents:
      - my_train_test_split
    parameter_override:
      # Resolve test dataset ID from the split stage's exported artifact
      Args/dataset_id: "${my_train_test_split.id}:test_dataset_id"
      Args/model_id: <your-model-id-from-clearml>

  # Stage 3: Evaluate predictions against ground truth
  my_evaluation:
    image_name: my_image:latest
    task_type: testing
    entry_point: /app/evaluation_component/stt_evaluation_my_metric/stt_evaluation_my_metric.py
    parents:
      - my_inference
    parameter_override:
      # Hypothesis: inference output dataset
      Args/hyp_dataset_id: "${my_inference.id}:dataset_id"
      # Reference: original test split dataset (ground truth)
      Args/ref_dataset_id: "${my_train_test_split.id}:test_dataset_id"
```

### 4.4 Passing values between stages

When a stage needs the output of a parent stage, use the `${}` syntax. The parent must be listed under `parents`.

```yaml
# Access a task ID combined with an artifact name (resolved at runtime by DatasetDownloader)
Args/dataset_id: "${split_stage.id}:test_dataset_id"

# Access a string artifact value directly via ClearML's .preview
Args/dataset_id: "${split_stage.artifacts.test_dataset_id.preview}"

# Access a parameter value from another stage
Args/model_name: "${train_stage.parameters.Args/model_name}"
```

**How artifact chaining works:**

| Source stage             | Exports artifact(s)                          | Consumed by   | Via argument                                                    |
| ------------------------ | -------------------------------------------- | ------------- | --------------------------------------------------------------- |
| `BaseTrainTestSplit`     | `train_dataset_id`, `test_dataset_id`        | Inference     | `Args/dataset_id: "${split.id}:test_dataset_id"`               |
| `BaseInferencePipeline`  | `dataset_id`                                 | Evaluation    | `Args/hyp_dataset_id: "${inference.id}:dataset_id"`            |
| `BaseEvaluationPipeline` | `evaluation_results` (JSON artifact)         | Downstream    | access via `${eval.artifacts.evaluation_results.preview}`       |

Each base class accepts both a plain ClearML dataset ID and an artifact reference (`<task_id>:<artifact_name>`) for any `--dataset_id`, `--hyp_dataset_id`, or `--ref_dataset_id` argument. Resolution happens inside `DatasetDownloader` at runtime.

### 4.5 Run the pipeline

```bash
docker run --rm --network host \
  -v ./pipeline/src:/app \
  --env-file ./pipeline/tutorial/clearml.env \
  echoforge_tutorial python3 /app/main.py --conf /app/conf/my_pipeline.yaml
```

Monitor at http://localhost:8080/pipelines. Each stage creates child tasks visible in the ClearML UI:

- **Split:** one task per resolved dataset (e.g. `my_train_test_split/dataset_name`), exports `train_dataset_id` and `test_dataset_id`
- **Inference:** one task per dataset (e.g. `my_inference/dataset_name`), exports `dataset_id`
- **Evaluation:** one task per dataset (e.g. `my_evaluation/dataset_name`), uploads `evaluation_results` artifact

---

## Step 5: Testing

### 5.1 Run the existing integration tests

The test suite in `tests/test_tutorial_pipeline.py` runs the full tutorial workflow end-to-end. This is the canonical way to confirm the system is working correctly after modifying base code.

**Prerequisites:**

- All services running (ClearML server, agents, MinIO)
- `services/clearml-agent/clearml.env` exists (the test suite reads credentials from this path)
- ClearML SDK configured on the host
- Model uploaded (the tests handle this via `TestModelUpload`)

```bash
# Install test dependencies
pip install pytest clearml

# Run all tests in order
pytest tests/test_tutorial_pipeline.py -v --tb=short

# Run a specific test class (e.g. if setup is already done)
pytest tests/test_tutorial_pipeline.py::TestFullChain -v
```

The tests run in this order:

| Test class          | What it does                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| `TestTutorialSetup` | Builds Docker image, generates ATCO2 data, uploads to ClearML, splits to circuits              |
| `TestDataPipeline`  | Runs `tutorial_data_pipeline.yaml`, polls ClearML until complete                               |
| `TestModelUpload`   | Builds download/upload images, uploads whisper-tiny to model registry                          |
| `TestFullChain`     | Runs `tutorial_full_chain.yaml` (split → inference → evaluation), verifies all stages complete |

Each test checks that the ClearML task status reaches `"completed"`. If a stage fails, the test reports which stage failed and its status.

### 5.2 Write unit tests for your component

When you add a new component, add a matching test file.

**Where to put it:** `tests/test_<component_name>.py`

For reference, see the existing test: `tests/test_tutorial_pipeline.py`

The test should verify your component logic independently of the full pipeline.

**Example: unit test for an inference component:**

```python
"""
Unit tests for stt_inference_my_model.

Tests the component logic (preprocess, infer, to_segments) in isolation,
without requiring ClearML services or Docker.
"""

import os
import json
import pytest
import numpy as np

from components.inference_component.stt_inference_my_model.stt_inference_my_model import (
    MyModelInference,
)


class TestMyModelInference:
    """Test inference component methods in isolation."""

    @pytest.fixture
    def pipeline(self, mocker):
        """Create an instance without calling run().

        ClearML is not initialised here — unit tests only exercise
        component logic (preprocess, infer, to_segments).
        """
        mocker.patch("clearml.Task.init")
        return MyModelInference()

    def test_to_segments_returns_valid_schema(self, pipeline):
        """Verify to_segments returns dicts with required segment fields."""
        mock_output = ["hello world", "testing one two three"]
        segments = pipeline.to_segments(mock_output)

        assert isinstance(segments, list)
        assert len(segments) == len(mock_output)

        for seg in segments:
            assert "raw_text" in seg
            assert "start" in seg
            assert "end" in seg
            assert isinstance(seg["raw_text"], str)
            assert isinstance(seg["start"], (int, float))

    def test_to_segments_empty_input(self, pipeline):
        """Verify to_segments handles empty input gracefully."""
        segments = pipeline.to_segments([])
        assert segments == []

    def test_preprocess_reads_audio(self, pipeline, tmp_path):
        """Verify preprocess reads an audio file without error."""
        import soundfile as sf

        audio_data = np.zeros(16000, dtype=np.float32)
        audio_path = tmp_path / "test.wav"
        sf.write(str(audio_path), audio_data, 16000)

        manifest = {"dataset": {}, "items": []}
        result = pipeline.preprocess(str(audio_path), manifest)
        assert result is not None
```

**Example: unit test for an evaluation component:**

```python
"""
Unit tests for stt_evaluation_my_metric.
"""

import pytest
from components.evaluation_component.stt_evaluation_my_metric.stt_evaluation_my_metric import (
    MyEvaluation,
)


class TestMyEvaluation:
    """Test evaluation logic in isolation."""

    @pytest.fixture
    def evaluator(self):
        return MyEvaluation()

    def test_evaluate_perfect_match(self, evaluator):
        """Perfect transcription should yield WER of 0."""
        paired_data = [
            {
                "filename": "test.wav",
                "prediction_text": "hello world",
                "reference_text": "hello world",
                "prediction_segments": [],
                "reference_segments": [],
            }
        ]
        result = evaluator.evaluate(paired_data)

        assert "dataset_eval" in result
        assert "filebased_eval" in result
        assert result["dataset_eval"]["wer"] == 0.0

    def test_evaluate_complete_mismatch(self, evaluator):
        """Completely wrong transcription should yield high WER."""
        paired_data = [
            {
                "filename": "test.wav",
                "prediction_text": "foo bar baz",
                "reference_text": "hello world test",
                "prediction_segments": [],
                "reference_segments": [],
            }
        ]
        result = evaluator.evaluate(paired_data)
        assert result["dataset_eval"]["wer"] > 0.0

    def test_evaluate_empty_input(self, evaluator):
        """Empty paired_data should not crash."""
        result = evaluator.evaluate([])
        assert "dataset_eval" in result
```

**Example: unit test for a data split component:**

```python
"""
Unit tests for my_train_test_split.
"""

import pytest
from components.data_component.stt_train_test_split_my_strategy import MyTrainTestSplit


class TestMyTrainTestSplit:
    """Test split logic in isolation."""

    @pytest.fixture
    def splitter(self):
        return MyTrainTestSplit()

    def test_split_produces_train_and_test(self, splitter):
        """Split should return both train and test keys."""
        manifest = {
            "dataset": {"dataset_name": "test"},
            "items": [{"filename": f"file_{i}.wav"} for i in range(100)],
        }
        result = splitter.split(manifest, test_ratio=0.2)

        assert "train" in result
        assert "test" in result
        assert len(result["train"]["items"]) + len(result["test"]["items"]) == 100

    def test_split_respects_ratio(self, splitter):
        """Test set size should approximately match the requested ratio."""
        manifest = {
            "dataset": {"dataset_name": "test"},
            "items": [{"filename": f"file_{i}.wav"} for i in range(1000)],
        }
        result = splitter.split(manifest, test_ratio=0.2)
        test_ratio = len(result["test"]["items"]) / 1000
        assert 0.15 <= test_ratio <= 0.25

    def test_split_single_item(self, splitter):
        """Single item should go to either train or test, not be lost."""
        manifest = {
            "dataset": {"dataset_name": "test"},
            "items": [{"filename": "only_file.wav"}],
        }
        result = splitter.split(manifest, test_ratio=0.2)
        total = len(result["train"]["items"]) + len(result["test"]["items"])
        assert total == 1
```

### 5.3 Running your tests

```bash
# Run just your component tests
pytest tests/test_my_component.py -v --tb=short

# Run all tests
pytest tests/ -v --tb=short
```

Test logs (stdout/stderr from each pipeline stage) are written to `tests/logs/<YYYYMMDD_HHMMSS>/` and are never overwritten between runs. Check the timestamped subfolder for logs from the most recent run.

### 5.4 When to run which tests

| Scenario                   | What to run                                                    |
| -------------------------- | -------------------------------------------------------------- |
| Modified base class code   | `pytest tests/test_tutorial_pipeline.py -v` (full integration) |
| Added a new component      | Your unit tests + the full integration suite                   |
| Changed pipeline YAML only | `pytest tests/test_tutorial_pipeline.py::TestFullChain -v`     |
| Quick sanity check         | Your component unit tests only                                 |

---

## Step 6: Push images to GoHarbor (optional)

GoHarbor centralises container storage so agents pull from your local registry instead of rebuilding images.

1. Create a new **public** project in GoHarbor at http://localhost/harbor/projects
2. Tag and push:

```bash
docker login http://localhost:80
# user: admin / password: Harbor12345

docker tag my_image:latest localhost/speech/my_image
docker push localhost/speech/my_image
```

3. Update your pipeline YAML:

```yaml
image_name: localhost/speech/my_image
```

---

## Step 7: Visualize data lineage with Marquez (optional)

**What it is:** Marquez is an open-source metadata service used for data lineage that tracks how datasets in ClearML are related. It consumes OpenLineage events to visualize the connection between "Parent" datasets and "Child" versions in a unified graph. The system includes a sync daemon that automatically maps all ClearML projects into a single Marquez namespace called `datasets` and polls ClearML every 60 seconds to detect new or deleted datasets.

```bash
# Start the Marquez stack and the Sync Daemon
docker compose -f ./services/clearml_to_marquez/docker-compose.yml up -d
```

---

## Reference: directory structure

```
echoforge/
├── components/
│ ├── base_classes/                    # Shared base classes — read before modifying
│ │ ├── __init__.py
│ │ ├── base_inference.py              # BaseInferencePipeline
│ │ ├── base_evaluation.py             # BaseEvaluationPipeline
│ │ ├── base_train_test_split.py       # BaseTrainTestSplit
│ │ ├── base_segment_schema.py         # BaseSegmentSchema (segment field definitions)
│ │ ├── data_schema/                   # JSON schemas for output formats
│ │ │ ├── __init__.py                  # Schema loader
│ │ │ ├── dataset.json                 # Dataset manifest schema
│ │ │ ├── model_prediction.json        # Inference output schema
│ │ │ ├── evaluation.json              # Evaluation output schema
│ │ │ ├── training_results.json        # Training output schema
│ │ │ └── model_tasks.json             # Registry of valid model task types
│ │ └── helper/
│ │ ├── __init__.py
│ │ ├── s3_config.py                   # S3Config (MinIO connection)
│ │ ├── data_handler.py                # BaseDatasetPipeline (shared MinIO plumbing)
│ │ ├── data_uploader.py               # DatasetUploader
│ │ └── data_downloader.py             # DatasetDownloader
│ ├── data_component/                  # ← place new data split scripts here
│ │ ├── Dockerfile
│ │ ├── train_test_split_segment.py    # Segment-level split (reference implementation)
│ │ ├── stt_train_test_split_minio.py  # Duration-based split (reference implementation)
│ │ ├── upload_dataset.py              # Dataset upload script
│ │ └── upload_model.py               # Direct model upload script
│ ├── inference_component/            # ← place new inference scripts here
│ │ └── tutorial_whisper_inference.py  # Whisper inference (reference implementation)
│ ├── training_component/             # ← place new training scripts here
│ │ └── tutorial_whisper_training.py   # Whisper fine-tuning (reference implementation)
│ └── evaluation_component/           # ← place new evaluation scripts here
│ └── stt_evaluation/
│ ├── Dockerfile
│ └── stt_evaluation.py               # WER evaluation (reference implementation)
│
├── pipeline/
│   ├── src/
│   │   ├── Dockerfile
│   │   ├── main.py                            # Pipeline controller entrypoint
│   │   ├── conf/                              # ← place new pipeline YAML configs here
│   │   │   ├── tutorial_full_chain.yaml       # Split → inference → evaluation
│   │   │   ├── tutorial_data_pipeline.yaml    # Data split only
│   │   │   ├── tutorial_model_inference.yaml  # Inference only
│   │   │   ├── tutorial_chaining.yaml         # Chaining example
│   │   │   ├── example_pipeline.yaml          # 5-stage train + evaluate example
│   │   │   ├── example_inference.yaml         # Inference example
│   │   │   └── train_vad.yaml                 # VAD training example
│   │   └── task_conf/
│   │       └── train_whisper.yaml             # Whisper training hyperparameters
│   └── tutorial/                              # Tutorial Docker image and credentials
│       ├── dockerfile
│       └── upload_whisper_to_clearml.py        # Uploads whisper model to ClearML
│
├── deployment/
│   ├── download.sh                            # Phase 1: download apt/pip/docker on online machine
│   ├── install.sh                             # Phase 2: install on air-gapped machine
│   ├── readme.md
│   ├── simulate_data/                         # ← dataset simulation and upload scripts go here
│   │   ├── atco2/                             # ATCO2 sample data (reference)
│   │   ├── generate_atco2_dataset.py          # Generates sample ATCO2 data
│   │   ├── upload_atco2_to_clearml.py         # Uploads sample dataset to ClearML
│   │   └── atco2_to_circuits.py               # Splits dataset into circuits
│   ├── model_download/                        # ← place new model download containers here
│   │   └── whisper_download/                  # Whisper download (reference implementation)
│   │       ├── dockerfile
│   │       └── download.py
│   ├── models_upload/                         # Model upload orchestration
│   │   ├── Dockerfile
│   │   ├── models.yaml                        # ← add new model entries here
│   │   ├── manage.py                          # Download + upload orchestrator
│   │   ├── model_state.json                   # Tracks uploaded model revisions
│   │   └── run_models_upload.sh               # Shell wrapper
│   └── docker/
│       ├── build.py                           # Docker image build orchestrator
│       ├── images.yaml                        # Image registry definitions
│       └── build_state.json                   # Tracks built image hashes
│
├── tests/                                     # ← place new test files here
│ └── test_tutorial_pipeline.py                # Integration test suite
│
├── docs/
│ ├── developer_guide.md                       # This file — building new components
│ ├── tutorial.md                              # End-to-end walkthrough
│ ├── base-classes.md                          # Base class reference and data flow
│ └── setup.md                                # Infrastructure setup
│
├── services/                                  # Infrastructure (docker-compose configs)
│ ├── clearml/                                 # ClearML server
│ ├── clearml-agent/                           # ClearML agent
│ ├── goharbor/                                # GoHarbor container registry
│ ├── minio/                                   # MinIO S3-compatible object storage
│ └── clearml_to_marquez/                      # ClearML to Marquez Data Lineage Visualisation
│
├── README.md
└── CONTRIBUTING.md
```

---

## Reference: pipeline variable syntax

| Syntax                                        | Resolves to                                                                 |
| --------------------------------------------- | --------------------------------------------------------------------------- |
| `${datasets}`                                 | Scatter: replaced with one dataset ID per resolved dataset                  |
| `${datasets[*]}`                              | Gather: replaced with a JSON list of all resolved dataset IDs               |
| `${stage.id}:artifact_name`                   | Artifact reference — resolved at runtime by `DatasetDownloader`             |
| `${stage[*].id}:artifact_name`                | Gather: JSON list of artifact references across all scattered iterations     |
| `${stage.artifacts.name.preview}`             | String preview of a task artifact (ClearML native syntax)                   |
| `${stage.parameters.Args/arg_name}`           | Parameter value from another stage (ClearML native syntax)                  |

---

## Reference: YAML stage fields

| Field                 | Required | Description                                                              |
| --------------------- | -------- | ------------------------------------------------------------------------ |
| `image_name`          | Yes      | Docker image containing the script                                       |
| `task_type`           | Yes      | ClearML task type: `training`, `inference`, `data_processing`, `testing` |
| `entry_point`         | Yes      | Absolute path to the Python script inside the container                  |
| `working_dir`         | No       | Working directory inside the container (default: `/app`)                 |
| `parents`             | No       | Stages that must complete before this stage starts                       |
| `parameter_override`  | No       | Overrides for argparse arguments (`Args/`) or config values (`General/`) |
| `config`              | No       | Path to a config file to override via `configuration_overrides`          |
| `cache_executed_step` | No       | Cache completed steps to skip re-execution (default: `true`)             |