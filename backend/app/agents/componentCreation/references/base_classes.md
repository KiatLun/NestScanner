# Base Classes

The base classes in `components/base_classes/` are the foundation for building pipeline components. They handle all communication with MinIO and ClearML so that you can focus on your model logic.

> If you are new to echoforge, start with [tutorial.md](tutorial.md) first.

## Why base classes?

Every component needs to download data, run some logic, and upload results. Without base classes, each component would need to:

- Configure a boto3 client with MinIO credentials
- Know the bucket layout and naming conventions
- Handle content-addressed file deduplication
- Manage manifests (the JSON files that track what belongs to a dataset)
- Register datasets with ClearML
- Resolve datasets by ID or tag

The base classes do all of this for you. You inherit from them and implement only the logic specific to your component.

## Available base classes

```
components/base_classes/
├── base_inference.py          # BaseInferencePipeline  — for inference components
├── base_evaluation.py         # BaseEvaluationPipeline — for evaluation components
├── base_train_test_split.py   # BaseTrainTestSplit     — for data splitting components
├── base_training.py           # BaseTrainingPipeline   — for training components
├── base_segment_schema.py     # BaseSegmentSchema      — defines output segment format
├── data_schema/               # JSON schemas — single source of truth for output formats
│   ├── __init__.py            # Schema loader (get_model_prediction_template, etc.)
│   ├── dataset.json           # Dataset manifest schema
│   ├── model_prediction.json  # Inference output schema
│   ├── evaluation.json        # Evaluation output schema
│   ├── training_results.json  # Training output schema
│   └── model_tasks.json       # Registry of valid model task types
└── helper/
    ├── s3_config.py           # S3Config             — MinIO connection settings
    ├── data_handler.py        # BaseDatasetPipeline  — shared MinIO + ClearML plumbing
    ├── data_uploader.py       # DatasetUploader      — upload files and manifests
    └── data_downloader.py     # DatasetDownloader    — download files and manifests
```

## Data schemas

Output structures are defined in `data_schema/*.json`. The base classes load these templates at runtime via the schema loader (`data_schema/__init__.py`), so a schema change in one JSON file propagates to every component automatically.

All schemas share a common `dataset` block:

```json
{
    "dataset_id": "",
    "dataset_name": "",
    "dataset_description": "",
    "dataset_task": "",
    "dataset_tags": []
}
```

The `dataset_id` and `dataset_tags` fields are auto-populated from ClearML metadata — you never need to set them manually. The base classes fetch this information from the ClearML dataset registry when building output artifacts.

### Segment fields

Segment fields are **not** defined in the JSON files. `dataset.json` intentionally leaves the segment structure as an empty placeholder (`"segments": [{}]`). The actual field definitions and defaults live exclusively in `BaseSegmentSchema` (`base_segment_schema.py`).

The schema loader exposes them via `get_segment_defaults()`, which calls `BaseSegmentSchema().to_dict()` at runtime. This means:

- **To add or remove a segment field, update `BaseSegmentSchema` only.** The change propagates automatically to every component's output — you never touch a JSON file.
- Every base class that builds output containing segments calls `get_segment_defaults()` to seed the structure, so there is no risk of drift between the JSON and the Python class.

---
 
## Dataset resolution
 
Dataset resolution — finding which datasets to process — happens at the **pipeline level**, not inside each base class.
 
When you run a pipeline, `main.py` reads the top-level `datasets` block from your YAML config and resolves it to a list of dataset IDs before any stage runs. It then rewrites the pipeline stages using scatter/gather logic so that each component receives exactly **one** dataset ID via its `--dataset_id` argument. See [developer_guide.md](developer_guide.md) for the full YAML syntax.
 
Each base class accepts a `--dataset_id` argument (or equivalent) that takes either:
 
- **A plain ClearML dataset ID** — e.g. `"abc123def456"`
- **An artifact reference** — `"<task_id>:<artifact_name>"` — resolved at runtime by fetching the named artifact from the given task and reading its value. e.g. `"${train_test_split_file.id}:train_dataset_id"`
 
The artifact reference format is how pipeline stages chain together: a split stage exports `train_dataset_id` and `test_dataset_id` artifacts, and the downstream inference stage receives `"<split_task_id>:train_dataset_id"` as its `--dataset_id`.
 
---

## BaseInferencePipeline

The base class for all inference components. Subclass it and implement the `model_task` property plus four methods:

| Method | What you implement |
|---|---|
| `model_task` *(property)* | Return your task type string — **must** be one of the values in `model_tasks.json` (`"stt"`, `"vad"`, `"speaker_id"`, `"language_id"`). Validated at instantiation. |
| `load_model(model_path, **kwargs)` | Load your model from a local path |
| `preprocess(audio_path, item, **kwargs)` | Prepare inputs for inference |
| `infer(inputs, **kwargs)` | Run the model |
| `to_segments(inferred, **kwargs)` | Convert raw output to a list of segment dicts |

All abstract methods accept `**kwargs` so the base class can pass additional context in the future without breaking existing subclasses.

> **`model_task` is required.** Omitting it raises `ValueError` when the class is instantiated. If you need a new task type, add it to `data_schema/model_tasks.json` first.

Everything else is handled for you:

- **Argument parsing** — `--datasets`, `--model_id`, and `--add_tags` are built in. `--datasets` accepts a single ID, comma-separated IDs, a JSON list, or an artifact URL from a pipeline step.
- **ClearML task init** — the task is created and connected automatically; tags include `"inference"` and your `model_task`.
- **Model download** — given a `model_id`, the base class downloads the model via ClearML's `InputModel`.
- **Data download with prefetching** — a background thread pre-downloads the next file from MinIO while the GPU processes the current one. Files missing or empty due to stale cache are automatically re-downloaded.
- **ClearML metadata logging** — `dataset_id`, `dataset_name`, `dataset_tags` are automatically fetched from ClearML and included in the output.
- **Output upload** — predictions are saved as a JSON artifact (`model_predictions`) matching the `model_prediction.json` schema.

**Built-in helper methods:**

| Method | Purpose |
|---|---|
| `safe_load_audio(audio_path)` | Loads an audio file and safely collapses multi-channel (stereo) audio to a single mono 1D array. Use this in your `preprocess` method instead of native `soundfile.read` to prevent dimension-mismatch memory errors (OOM) in models. Returns `(waveform, sr)`. |

**Built-in CLI args:**
 
| Argument | Accepts |
|---|---|
| `--dataset_id` | A single ClearML dataset ID, or `<task_id>:<artifact_name>` |
| `--model_id` | A single ClearML model ID, or `<task_id>:<artifact_name>` |
| `--add_tags` | Comma-separated custom tags to attach to the output |
| `--model_type` | `"pretrained"` or `"finetuned"` — auto-detected from model tags if not set |
 
**Exported artifacts:**
 
| Artifact | Value |
|---|---|
| `dataset_id` | ClearML dataset ID of the uploaded predictions |
 
---

I'll look at the existing base classes and the training references in tutorial/developer guide to write something precise and consistent.Now I have the full picture. Here is the new section:

---

## BaseTrainPipeline

The base class for training components. Subclass it and implement the `model_task` property plus three methods:

| Method | What you implement |
|---|---|
| `model_task` *(property)* | Return your task type string — **must** be one of the values in `model_tasks.json` (`"stt"`, `"vad"`, `"speaker_id"`, `"language_id"`). Validated at instantiation. |
| `load_base_model(model_path, **kwargs)` | Load the pre-trained base model from a local path |
| `preprocess_dataset(manifests, **kwargs)` | Convert train and test manifests into a training-ready format |
| `train(data, config, model, **kwargs)` | Run the training loop and return `(saved_model_path, metrics)` |

All abstract methods accept `**kwargs` so extra CLI arguments added via `add_args()` are forwarded through the entire call chain without requiring changes to method signatures.

> **`model_task` is required.** Omitting it raises `ValueError` when the class is instantiated. If you need a new task type, add it to `data_schema/model_tasks.json` first.

**Call order inside `run()`:**

```
load_base_model()       ← called first, result available in self.model
preprocess_dataset()    ← called second, may use self.model / self.processor
preprocess_config()     ← called last, may inject dataset or model-dependent values
train()                 ← receives outputs of all three above
```

This ordering is intentional: `preprocess_dataset` often needs the model's tokenizer or processor, and `preprocess_config` may need to know dataset statistics before training begins.

Everything else is handled for you:

- **Argument parsing** — `--train_dataset_id`, `--test_dataset_id`, `--base_model_id`, `--upload_uri`, and `--add_tags` are built in. All ID arguments accept a plain ClearML ID or an artifact reference (`<task_id>:<artifact_name>`).
- **ClearML task init** — the task is created and tagged with `["training", model_task]` automatically.
- **Base model download** — the pre-trained model is fetched from ClearML via `InputModel` and its local path is passed to `load_base_model()`.
- **Config management** — `load_default_config()` is called before training and connected to ClearML under the `"General"` configuration key, making hyperparameters visible and editable in the UI. Override `preprocess_config()` to inject runtime-derived values (e.g. vocabulary size from the dataset).
- **Trained model upload** — after `train()` returns, the saved weights are registered as a ClearML `OutputModel`, uploaded to MinIO at `--upload_uri`, and published. The framework tag defaults to `"pytorch"` — override `get_framework()` to change it.
- **Metrics logging** — scalar values in the `metrics` dict returned by `train()` are reported as ClearML single-value scalars. HuggingFace `Trainer` metrics are captured automatically by ClearML when `Task.init()` has been called.
- **Training results artifact** — a `training_results` artifact (matching `training_results.json` schema) is uploaded with base model info, trained model ID, dataset metadata, training args, and metrics.

**The `preprocess_dataset` manifests dict:**

```python
{
    "train": {"dataset": {...}, "items": [{"filename": ..., "remote_uri": ..., "segments": [...]}]},
    "test":  {"dataset": {...}, "items": [{"filename": ..., "remote_uri": ..., "segments": [...]}]},
}
```

**The `train` return value:**

```python
saved_model_path, metrics = self.train(data, config, model)
# saved_model_path: str — local directory containing the trained weights
# metrics: dict       — summary scalars, e.g. {"final_train_loss": 0.3, "epochs_completed": 3}
```

**Optional overrides:**

| Method | Purpose |
|---|---|
| `add_args(parser)` | Add subclass-specific CLI arguments, forwarded as kwargs to all three abstract methods |
| `load_default_config()` | Return a default hyperparameter dict connected to ClearML under `"General"` |
| `preprocess_config(config, **kwargs)` | Modify the resolved config before it is passed to `train()` — useful for injecting dataset-dependent values |
| `get_model_info()` | Return `{"task": "", "model_description": ""}` metadata |
| `get_framework()` | Return the ClearML model framework tag (default: `"pytorch"`) |

Example:

```python
from components.base_classes.base_train import BaseTrainPipeline

class MyWhisperTraining(BaseTrainPipeline):

    project_name = "my_project"
    task_name = "stt_training_whisper"

    @property
    def model_task(self) -> str:
        return "stt"

    def load_default_config(self) -> dict:
        return {"num_train_epochs": 3, "learning_rate": 1e-5, "per_device_train_batch_size": 8}

    def load_base_model(self, model_path, **kwargs):
        self.processor = WhisperProcessor.from_pretrained(model_path)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_path)

    def preprocess_dataset(self, manifests, **kwargs):
        # self.processor is already loaded
        train_items = manifests["train"]["items"]
        return build_hf_dataset(train_items, self.processor)

    def train(self, data, config, model, **kwargs) -> tuple[str, dict]:
        trainer = Seq2SeqTrainer(
            model=model,
            args=Seq2SeqTrainingArguments(output_dir="output", **config),
            train_dataset=data,
        )
        trainer.train()
        trainer.save_model("output/model")
        return "output/model", {"final_train_loss": trainer.state.log_history[-1].get("loss", 0)}

if __name__ == "__main__":
    MyWhisperTraining().run()
```

> **Working example:** See `components/training_component/tutorial_whisper_training.py`

**Built-in CLI args:**

| Argument | Accepts |
|---|---|
| `--train_dataset_id` | A single ClearML dataset ID, or `<task_id>:<artifact_name>` |
| `--test_dataset_id` | A single ClearML dataset ID, or `<task_id>:<artifact_name>` |
| `--base_model_id` | A single ClearML model ID, or `<task_id>:<artifact_name>` |
| `--upload_uri` | S3/MinIO URI for model weights (defaults to `$UPLOAD_URI` env var or `s3://clearml/models`) |
| `--add_tags` | Custom tags to attach to the task and training results artifact |

**Exported artifacts:**

| Artifact | Value |
|---|---|
| `model_id` | ClearML model ID of the uploaded trained model |
| `training_results` | JSON artifact (matching `training_results.json` schema) with metrics, dataset info, and model references |

---

<GenerateWidget height="600px" component_placeholder_id="im_60529f7d925070ab">
```json
{
  "widgetSpec": {
    "height": "600px",
    "prompt": "Create an interactive visual architecture diagram for a system called EchoForge Data Pipeline. The objective is to illustrate how Base Classes connect ClearML, MinIO, and custom Subclasses. Data State: The architecture includes 'BaseDataPipeline' which handles standard processes, and 'Subclasses' like 'ConvertStereo' or 'StripSegments' that handle specific logic. Data flows from 'ClearML' (which stores metadata and Task execution state) to 'MinIO' (which stores physical audio files in a 'raw/' folder and JSON manifests in a 'manifests/' folder). Strategy: Diagram/Explorer layout. Behavior: Allow the user to click on different components ('ClearML', 'MinIO', 'BaseDataPipeline', 'Subclasses'). When clicked, highlight the selected node and display a detailed text explanation of its role in the pipeline (e.g., clicking 'MinIO' explains it holds raw files and manifests; clicking 'BaseDataPipeline' explains it handles downloading, resolving IDs, creating ClearML tasks, and uploading). Show directional flow arrows indicating the sequence: Download -> Process -> Upload."
  }
}
```
</GenerateWidget>

Here is the new section for `base_data.py`, following the established format of the README.

---

## BaseDataPipeline

The base class for data transformation and curation pipelines. It handles downloading a dataset, executing a custom data modification process, and uploading the modified result as a new ClearML dataset.

Subclass it and implement the `task` property plus one method:

| Method | What you implement |
|---|---|
| `task` *(property)* | Return your task name string (e.g., `"strip_segments"`, `"convert_stereo"`). This is used to prefix the output dataset name and is automatically added as a tag. |
| `process(manifest, **kwargs)` | Apply your data modification logic. You receive the downloaded dataset manifest. You must return the modified manifest. |
| `add_args(parser)` | (Optional) Add subclass-specific CLI arguments. |
| `add_tags()` | (Optional) Return a list of extra string tags to append to the output dataset. |

Any CLI arguments added via `add_args()` are automatically forwarded to `process()` as keyword arguments. 

### Processing Logic & Artifacts

Unlike inference or evaluation components that output JSON artifacts, data pipelines output **entirely new ClearML Datasets**. 

**Call order inside `run()`:**
1. **Resolution:** Translates the input `dataset_id` (which can be a direct ClearML ID or a `<task_id>:<artifact_name>` pipeline reference) into a valid dataset object.
2. **Download:** Fetches the `dataset.json` manifest for the target dataset.
3. **Process:** Your `process()` method is called to modify the manifest (and interact with physical files via `self.downloader` if needed).
4. **Naming & Tagging:** A new dataset name is generated using the pattern `{self.task}/{original_dataset_name}`. Tags are inherited from the parent dataset, with `self.task` and any tags from `add_tags()` appended.
5. **Upload:** The modified manifest is uploaded to MinIO, and a new child dataset is registered in ClearML linked to the original dataset parent.
6. **Artifact Export:** The ClearML Task uploads the new dataset's ID as an artifact named `id`, enabling downstream pipeline components to seamlessly consume the transformed data.

Example — simple manifest modification (e.g., stripping segments):

```python
from components.base_classes.base_data import BaseDataPipeline

class StripSegments(BaseDataPipeline):
    
    @property
    def task(self) -> str:
        return "strip_segments"

    def process(self, manifest: dict, **kwargs) -> dict:
        # Aggressively clear segment annotations
        for item in manifest.get("items", []):
            item["segments"] = []
        return manifest

if __name__ == "__main__":
    StripSegments().run()
```

If your pipeline needs to modify the actual audio files (not just the manifest), you can use `self.downloader.batch_download_file(manifest, cache_dir)` within `process()` to fetch the raw files locally, modify them, and use `self.downloader._upload_file(new_file_path)` to get a new remote URI for the manifest.

**Built-in CLI args:**

| Argument | Accepts |
|---|---|
| `--dataset_id` | A single ClearML dataset ID, or `<task_id>:<artifact_name>`. |

**Exported artifacts:**

| Artifact | Value |
|---|---|
| `id` | ClearML dataset ID of the newly generated dataset. |

---

## BaseTrainTestSplit

The base class for data splitting components. Implement one method and optionally add CLI arguments:

| Method | What you implement |
|---|---|
| `split(manifest, **kwargs)` | Return a dict of split manifests (e.g. `{"train": {...}, "test": {...}}`) |
| `add_args(parser)` | (Optional) Add subclass-specific CLI arguments |

Any CLI arguments added via `add_args()` are automatically forwarded to `split()` as keyword arguments. This keeps the base class generic — it handles dataset resolution, ClearML registration, and upload, while each subclass defines its own splitting parameters.

Example — duration-based split:

```python
class DurationTrainTestSplit(BaseTrainTestSplit):

    def add_args(self, parser):
        parser.add_argument("--test_duration", type=float, default=3600)

    def split(self, manifest, **kwargs):
        test_duration = kwargs["test_duration"]
        # ... splitting logic
```

The base class handles:

- **Dataset resolution** — finds datasets by tag or ID, with optional exclusion of already-split datasets.
- **Empty split protection** — if your `split()` returns an empty `items` list for any split, that split is **skipped** (no ClearML dataset is created, no ID appears in the output artifacts) and a warning is printed. Downstream stages (inference, training, evaluation) never receive an empty dataset ID.
- **Upload of split datasets** — each non-empty split is uploaded as a new ClearML dataset with appropriate tags and parent linkage.
- **Metadata propagation** — `dataset_id`, `dataset_name`, and `dataset_tags` from the source dataset are carried into each split.

**Built-in CLI args:**
 
| Argument | Accepts |
|---|---|
| `--dataset_id` | A single ClearML dataset ID, or `<task_id>:<artifact_name>` |

**Exported artifacts:**
 
One artifact per split name, using the pattern `<split_name>_dataset_id`. For a standard train/test split:
 
| Artifact | Value |
|---|---|
| `train_dataset_id` | ClearML dataset ID of the uploaded train split |
| `test_dataset_id` | ClearML dataset ID of the uploaded test split |
 
---

## BaseEvaluationPipeline

The base class for evaluation components. It consumes the output of an inference task and compares predictions against ground truth.

| Method | What you implement |
|---|---|
| `evaluate(paired_data, **kwargs)` | Compute metrics from paired prediction/reference data, return a results dict |
| `add_args(parser)` | (Optional) Add subclass-specific CLI arguments |





The base class handles:

- **Artifact retrieval** — downloads the `model_predictions` artifact from the inference task.
- **Ground-truth lookup** — uses the dataset name in the inference output to find and fetch the original manifest from MinIO.
- **File pairing** — matches predicted files to ground-truth files by filename.
- **Result upload** — uploads the evaluation results as an `evaluation_results` artifact matching the `evaluation.json` schema, with `model` and `dataset` blocks carried from the inference output.

`paired_data` is a list passed to `evaluate()` with one dict per audio file:
- `filename`: str
- `reference_segments`: list[dict]
- `prediction_segments`: list[dict]

```python
{
    "filename": "audio_001.wav",
    "prediction_segments": [...],             # raw predicted segments
    "reference_segments": [...],              # raw ground-truth segments
}
```

Your `evaluate()` must return a dict matching the evaluation schema:

```python
{
    "dataset_eval": {"wer": 0.15, "cer": 0.08},          # aggregate metrics
    "filebased_eval": [                                    # per-file metrics
        {
            "filename": "audio_001.wav",
            "wer": 0.12,
            "segmentbased_eval": [...]                     # optional per-segment metrics
        }
    ]
}
```

Example:

```python
class SttEvaluation(BaseEvaluationPipeline):

    def add_args(self, parser):
        parser.add_argument("--metrics", type=str, default="wer,cer")

    def evaluate(self, paired_data, **kwargs):
        # compute WER/CER per file and aggregate
        ...
```

**Built-in CLI args:**
 
| Argument | Accepts |
|---|---|
| `--hyp_dataset_id` | Dataset ID of the inference predictions. Accepts a plain ID or `<task_id>:<artifact_name>`. |
| `--ref_dataset_id` | Dataset ID of the ground-truth source. Accepts a plain ID or `<task_id>:<artifact_name>`. |
| `--add_tags` | Custom tags (auto-inherited from upstream inference artifact if not set) |


**Exported artifacts:**
 
One JSON file containing evaluation results, `evaluation_results`.

| Artifact | Value |
|---|---|
| `evaluation_results` | JSON evaluation result |

---

## BaseSegmentSchema

The single source of truth for segment field definitions. It is a Python dataclass with these default fields:

| Field | Type | Default |
|---|---|---|
| `start` | `float` | `0.0` |
| `end` | `float` | `0.0` |
| `speaker` | `str` | `""` |
| `raw_text` | `str` | `""` |
| `processed_transcript` | `str` | `""` |
| `language` | `str` | `""` |
| `keyword` | `list` | `[]` |
| `estimated_snr` | `float` | `0.0` |
| `audio_characteristics` | `list` | `[]` |

To add a field to every component's output: add it here. The schema loader's `get_segment_defaults()` calls `BaseSegmentSchema().to_dict()` and returns the result — no JSON file needs updating.

---

## How MinIO is handled for you

### Connection

`S3Config` reads MinIO credentials from environment variables injected by the ClearML agent:

| Env var | Purpose |
|---|---|
| `AWS_ENDPOINT_URL` | MinIO endpoint (e.g. `http://localhost:9000`) |
| `AWS_ACCESS_KEY_ID` | MinIO access key |
| `AWS_SECRET_ACCESS_KEY` | MinIO secret key |
| `MINIO_BUCKET` | Bucket name (default: `clearml`) |

You never need to set these manually — they are configured in the ClearML agent's docker environment block.

### How data is stored in MinIO

Files are stored **content-addressed**:

```
clearml/                                  ← bucket
├── raw/<md5-prefix>/<md5-hash>           ← audio files (deduplicated)
└── manifests/<dataset-id>/dataset.json   ← manifest per dataset
```

- **Audio files** are stored by their MD5 hash. The first two characters of the hash form a directory prefix (e.g. `raw/a3/a3f1b2c4...`). Uploading the same file twice is a no-op — the second upload is skipped.
- **Manifests** are JSON files that list every file in a dataset along with its `remote_uri` pointing to the content-addressed location.

### How data flows between ClearML and MinIO

ClearML holds **metadata** (dataset name, project, tags, version). MinIO holds **the actual files**. They are linked through the manifest.

```
                     ┌──────────────────┐
  "find datasets     │   ClearML        │  metadata only:
   tagged 'atco2'" → │   (dataset       │  name, project,
                     │    registry)     │  tags, version
                     └────────┬─────────┘
                              │ dataset record points to
                              │ manifests/<id>/dataset.json
                              ▼
                     ┌──────────────────┐
                     │   MinIO          │
                     │                  │  manifests + audio files
                     │  manifests/      │
                     │  raw/            │
                     └──────────────────┘
```

When a component needs data:

1. Query ClearML for a dataset by ID or tag (via `DatasetDownloader`).
2. ClearML returns the dataset record, which points to `manifests/<dataset-id>/dataset.json` in MinIO.
3. The manifest is fetched from MinIO.
4. The manifest lists every audio file's `remote_uri` (e.g. `s3://clearml/raw/a3/a3f1b2c4...`).
5. Files are downloaded from MinIO using those URIs.

This keeps ClearML lightweight (no binary blobs) and MinIO stores everything deduplicated.

---

## Data flow — end to end

This section traces the full lifecycle of data through echoforge: upload → split → inference → evaluation.

### 1. Upload: local files → MinIO + ClearML

Uploading is done **outside the pipeline** using `DatasetUploader.upload()`.

```python
uploader = DatasetUploader()
uploader.upload(
    dataset_name="my_dataset",
    project="my_project",
    manifest=manifest,
    tags=["atco2"],
)
```

What happens under the hood:

```
DatasetUploader.upload()
         │
┌────────┼────────────────┐
▼        ▼                ▼
1. Hash each    2. Store the       3. Register in
   audio file      manifest           ClearML
         │              │                  │
         ▼              ▼                  ▼
   MinIO: raw/    MinIO: manifests/   ClearML: dataset
   a3/a3f1b2c4…  <id>/dataset.json   record with name,
   (content-     (JSON with          project, tags,
    addressed,    remote_uri per      version
    deduplicated) file)
```

- Each audio file is MD5-hashed. If the hash already exists in MinIO, the upload is skipped.
- Every manifest entry's `remote_uri` is updated to the content-addressed location.
- A ClearML `Dataset` record is created — ClearML holds no binary data, only references.

### 2. Split: one dataset → train + test datasets

`BaseTrainTestSplit` fetches the manifest, calls your `split()` method, then uploads each split as a new dataset. Audio files are **not re-uploaded** — only new manifests are written.

```
ClearML: dataset "my_dataset"
         │
         ▼
DatasetDownloader.get_manifest()        ← fetches manifests/<id>/dataset.json from MinIO
         │
         ▼
your split() method                     ← returns {"train": {...}, "test": {...}}
         │
         ├──▶ DatasetUploader.upload("my_dataset_train", parent=original_id)
         └──▶ DatasetUploader.upload("my_dataset_test",  parent=original_id)
```

### 3. Inference: dataset + model → predictions

`BaseInferencePipeline` downloads the dataset manifest and model, runs inference per file with background prefetching, and uploads results as a ClearML task artifact.

```
ClearML: dataset_id ──▶ DatasetDownloader.get_manifest()
ClearML: model_id   ──▶ InputModel.get_local_copy()
         │
         ▼
For each file in manifest["items"]:
    download_item_audio()               ← background thread downloads next file
         │
         ▼
    your preprocess() → infer() → to_segments()
         │
         ▼
Task.upload_artifact("model_predictions")
```

### 4. Evaluation: predictions + ground truth → metrics

`BaseEvaluationPipeline` pulls the inference artifact, fetches ground truth, pairs by filename, and calls your `evaluate()`.

```
ClearML: inference task_id
         │
         ▼
Task.get_task().artifacts["model_predictions"]  ← download inference output
         │
         ├──▶ find original dataset via DatasetDownloader
         │         └──▶ fetch ground truth manifest from MinIO
         │
         ▼
Pair by filename: prediction segments ↔ ground-truth segments
         │
         ▼
your evaluate(paired_data)
         │
         ▼
Task.upload_artifact("evaluation_results")
```

### Summary: what lives where

| What | Where | Example |
|---|---|---|
| Audio files | MinIO `raw/` | `s3://clearml/raw/a3/a3f1b2c4...` |
| Manifests | MinIO `manifests/` | `s3://clearml/manifests/<id>/dataset.json` |
| Dataset metadata | ClearML dataset registry | id, name, project, tags, version, parent |
| Models | ClearML model registry | downloaded via `InputModel` |
| Inference output | ClearML task artifact | `model_predictions` JSON |
| Evaluation output | ClearML task artifact | `evaluation_results` JSON |

ClearML never stores binary data. MinIO stores all files, deduplicated by content hash. They are linked through manifests.

---

## Why this matters for you

Because all components share the same base classes:

- **Features propagate automatically.** If we add tag-based dataset filtering to `BaseInferencePipeline`, every inference component gets it without code changes.
- **Storage is consistent.** Every component reads and writes data the same way. No one-off scripts that put files in unexpected locations.
- **Schemas are centralised.** Output formats are defined in `data_schema/*.json`. Change the schema once and every base class picks it up.
- **ClearML metadata is logged automatically.** `dataset_id`, `dataset_tags`, and `dataset_name` flow through inference → evaluation without manual effort.
- **Onboarding is faster.** You learn the pattern once — subclass, implement your methods, done.
