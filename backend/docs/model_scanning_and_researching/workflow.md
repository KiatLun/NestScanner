# NestScanner Backend

NestScanner is a backend system for continuously discovering, researching, and tracking machine-learning models.

The current backend focuses on three main responsibilities:

1. **Discover models** from Hugging Face.
2. **Build a structured technical profile** using reliable source evidence.
3. **Use an LLM to analyse the completed technical profile** and produce a useful final assessment.

The backend is implemented using **FastAPI**, Python, and an agent-based workflow.

The overall pipeline is:

```text
Scan Request
     ↓
Model Discovery
     ↓
Database / Freshness Check
     ↓
Candidate Selection
     ↓
Primary Model Research
     ↓
Targeted Missing-Field Research
     ↓
Build Technical Profile
     ↓
LLM Analysis
     ↓
Save Research Result
     ↓
Database
```

The key design principle is:

> **Use deterministic sources and structured extraction for facts; use the LLM for interpretation.**

---

# 1. Backend Overview

NestScanner should not treat the LLM as the primary source of model information.

Instead, the workflow separates:

```text
DISCOVERY
"What models should we investigate?"

RESEARCH
"What factual information can we verify about this model?"

TECHNICAL PROFILE
"What structured facts do we know about this model?"

LLM ANALYSIS
"What do these facts mean?"
```

This separation reduces hallucination and makes the final model analysis traceable to real evidence.

---

# 2. Backend Structure

The backend is located under:

```text
NestScanner/
└── backend/
    ├── app/
    │   ├── main.py
    │   │
    │   ├── graph/
    │   │   └── ...
    │   │
    │   ├── agents/
    │   │   ├── discovery/
    │   │   └── research/
    │   │       ├── buildTechnicalProfile.py
    │   │       └── ...
    │   │
    │   ├── tools/
    │   │   ├── arxivSearch.py
    │   │   ├── webSearch.py
    │   │   └── ...
    │   │
    │   ├── llm/
    │   │   └── ...
    │   │
    │   └── ...
    │
    ├── db.py
    ├── .env
    ├── sample.env
    └── ...
```

The exact internal files may continue to change as NestScanner is refactored, but the responsibility of each layer should remain separated.

---

# 3. Running the Backend

Run NestScanner from the `backend` directory.

```bash
cd NestScanner/backend
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start FastAPI:

```bash
python -m uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

---

# 4. Python Import Convention

Because Uvicorn is started from:

```text
NestScanner/backend/
```

using:

```bash
python -m uvicorn app.main:app --reload
```

the Python package root is:

```text
app
```

Therefore active backend imports should use:

```python
from app.agents.research import ...
from app.agents.discovery import ...
from app.tools.arxivSearch import ...
from app.llm.client import ...
```

and not:

```python
from backend.app.agents.research import ...
from backend.app.tools.arxivSearch import ...
```

Using `backend.app...` from this execution environment can cause:

```text
ModuleNotFoundError: No module named 'backend'
```

This is particularly important when copying implementations from older or deprecated agent folders.

---

# 5. Starting a Scan

A NestScanner workflow begins when a scan request is received by the backend.

Conceptually:

```text
POST /api/startScan
```

A scan represents one complete execution of the discovery and research workflow.

```text
Request
   ↓
Create scan record
   ↓
Run discovery
   ↓
Research selected candidates
   ↓
Store results
   ↓
Complete scan
```

The scan record allows NestScanner to preserve historical information instead of treating the database as only the latest state.

---

# 6. LangGraph Workflow

At a high level, the current application workflow is:

```text
START
  ↓
Discovery Agent
  ↓
Research Agent
  ↓
END
```

The simplicity of the graph does not mean that each node performs only one operation.

For example, the Research Agent internally performs:

```text
Research Agent
     │
     ├── Fetch Hugging Face information
     │
     ├── Parse model card
     │
     ├── Identify missing fields
     │
     ├── Perform targeted secondary research
     │
     ├── Build TechnicalProfile
     │
     ├── Perform LLM analysis
     │
     └── Save result
```

The LangGraph workflow therefore controls the major stages while each stage contains its own internal processing.

---

# 7. Discovery Stage

The first major stage is model discovery.

The Discovery Agent is responsible for finding relevant models from Hugging Face.

Discovery may use strategies such as:

```text
Recently created models
Recently updated models
Popular models
Trending models
```

Relevant Hugging Face metadata is preserved during discovery.

Examples include:

```text
repositoryId
organisation
pipelineTag
downloads
likes
trendingScore
createdAt
lastModified
revision
tags
```

The most important external identifier is:

```text
repositoryId
```

For example:

```text
openai/whisper-medium
```

The Hugging Face repository ID should remain the canonical external identifier for the model.

NestScanner may additionally maintain an internal:

```text
modelId
```

for database relationships.

The distinction is:

```text
repositoryId
    ↓
external model identity

modelId
    ↓
internal NestScanner database identity
```

---

# 8. Discovery Deduplication

Multiple discovery strategies may return the same model.

For example:

```text
Trending search
    └── Model A

Popular search
    └── Model A

Recently updated
    └── Model A
```

Before continuing, models are deduplicated using their repository identity.

```text
Raw discovery results
        ↓
Deduplicate by repositoryId
        ↓
Unique models
```

This avoids researching the same model multiple times in one scan.

---

# 9. Database Freshness Check

Discovery does not automatically send every discovered model into research.

NestScanner first checks the existing database.

A discovered model may effectively be:

```text
NEW
UNRESEARCHED
STALE
CURRENT
```

---

## NEW

The repository does not currently exist in NestScanner.

```text
repositoryId
    ↓
No database record
    ↓
NEW
```

The model should be added and researched.

---

## UNRESEARCHED

The model exists, but no completed technical research is available.

```text
Model exists
     +
No completed research
     ↓
UNRESEARCHED
```

The model should enter research.

---

## STALE

The model has previously been researched, but Hugging Face reports that the repository has changed since the latest completed research.

The comparison is conceptually:

```text
Hugging Face lastModified
            >
Latest completed research time
```

If true:

```text
STALE
```

and the model should be researched again.

---

## CURRENT

The model already has completed research and Hugging Face does not indicate that the repository has changed afterwards.

```text
Latest research
      >=
HF lastModified
```

The model does not need to be unnecessarily researched again.

---

# 10. Candidate Selection

Candidates requiring research are normally models classified as:

```text
NEW
UNRESEARCHED
STALE
```

Discovery may also apply:

```text
maxCandidates
```

to limit how many models enter a single research run.

The important architectural decision is:

> **Discovery decides whether research is required.**

The Research Agent should not independently repeat the same freshness decision.

Therefore:

```text
Discovery Agent
     ↓
Determines WHAT needs research
     ↓
Research Agent
     ↓
Researches whatever it receives
```

This keeps responsibilities clear.

---

# 11. Research Philosophy

The current NestScanner research approach is deliberately different from simply asking an LLM:

```text
"Tell me everything about this model."
```

Instead, research follows a source-first approach.

```text
Hugging Face metadata
        +
Hugging Face model card
        ↓
Extract known information
        ↓
Determine what is missing
        ↓
Targeted additional research
        ↓
Complete structured profile
```

The goal is to avoid unnecessary web searches and avoid having the LLM invent factual details.

---

# 12. Primary Research Source: Hugging Face

For a Hugging Face model, the first research step should use the repository itself.

NestScanner should inspect information including:

```text
Hugging Face API metadata
Model card / README
Repository configuration
Repository tags
Linked datasets
Linked papers
Model relationships
```

The model card is particularly important because it commonly contains:

```text
architecture
model description
intended use
training information
datasets
evaluation results
license
fine-tuning information
hardware notes
usage examples
inference requirements
limitations
```

Information available directly from Hugging Face should not be searched for again elsewhere without a reason.

---

# 13. Targeted Secondary Research

After processing Hugging Face information, NestScanner determines which important technical fields remain missing or ambiguous.

Only those fields should trigger secondary research.

Possible secondary sources include:

```text
GitHub repositories
Research papers
arXiv
Official documentation
Project websites
Other authoritative technical sources
```

For example:

```text
Hugging Face profile
        ↓
Architecture       ✓
Parameters         ✓
License            ✓
Languages          ✓
Training datasets  ?
Hardware           ?
Benchmark details  ?
        ↓
Search ONLY for:
    training datasets
    hardware
    benchmark details
```

This is preferable to performing broad web searches for every model.

The intended behaviour is:

> **Search to fill gaps, not to recreate information already available.**

---

# 14. Building the Technical Profile

The main output of the research stage is a structured:

```text
TechnicalProfile
```

The TechnicalProfile represents the factual technical understanding NestScanner has built for a model.

A profile may include fields such as:

```text
Identity
├── repositoryId
├── modelName
├── organisation
└── source

Model lineage
├── baseModel
└── baseModelRelation

Architecture
├── architecture
├── parameterCount
└── modelType

Capabilities
├── task
├── languages
├── multilingual
└── streaming / realtime support

Training
├── trainingDatasets
└── fineTuningInformation

Evaluation
├── benchmarks
├── datasets
├── metrics
├── WER
└── CER

Deployment
├── inferenceFramework
├── softwareRequirements
├── hardwareRequirements
├── quantization
└── deploymentInformation

Licensing
└── license

Research
├── paper
├── publicationInformation
└── evidence / sources
```

Not every model will contain every field.

Missing information should remain unknown rather than being invented.

---

# 15. Model Lineage

One of the newer additions to the TechnicalProfile is explicit model lineage.

NestScanner should identify:

```text
baseModel
```

where possible.

For example:

```text
Base model:
facebook/wav2vec2-base
```

NestScanner should also describe the relationship between the current model and its base model.

For example:

```text
baseModelRelation:
finetune
```

Possible relationships may include:

```text
finetune
adapter
quantized
merge
```

This is useful because two repositories may share an architecture but represent very different types of modifications.

For example:

```text
Base model
   ↓
Fine-tuned model
   ↓
Domain-specific ASR model
```

is different from:

```text
Base model
   ↓
Quantized model
```

The model lineage should therefore be represented explicitly instead of relying only on the model name.

---

# 16. Training Dataset Information

The TechnicalProfile should also attempt to identify what data was used to train or fine-tune the model.

For example:

```text
trainingDatasets:
[
    Common Voice,
    LibriSpeech,
    proprietary dataset
]
```

Where possible, NestScanner should distinguish between:

```text
pretraining data
fine-tuning data
evaluation data
```

These should not automatically be treated as equivalent.

If the training dataset cannot be reliably determined, it should remain unknown.

---

# 17. Benchmark Information

Benchmarks should contain enough context to interpret the value.

For example, storing only:

```text
WER = 7.3
```

is insufficient.

A useful benchmark should preserve information such as:

```text
metric: WER
value: 7.3
dataset: LibriSpeech
subset: test-clean
language: English
source: ...
```

Conceptually:

```text
Benchmark
├── metric
├── value
├── dataset
├── subset
├── language
└── source
```

This is important because benchmark values cannot be meaningfully compared without understanding the conditions under which they were measured.

---

# 18. Inference and Runtime Requirements

The TechnicalProfile should capture information relevant to actually running the model.

This may include:

```text
inferenceFramework
softwareRequirements
runtimeRequirements
hardwareRequirements
quantizationSupport
```

Examples of frameworks may include:

```text
Transformers
PyTorch
faster-whisper
ONNX Runtime
CTranslate2
```

Hardware information may include evidence about:

```text
CPU support
GPU requirements
VRAM requirements
CUDA requirements
memory requirements
```

NestScanner should only populate specific requirements when supported by evidence.

---

# 19. Local Deployability

Local deployability should not be guessed purely from model popularity, size, or model type.

Instead, it should be evidence-based.

Relevant evidence may include:

```text
Are downloadable model weights available?

Is inference code available?

Is there a supported runtime?

Are required dependencies available?

Are the hardware requirements practical?

Does the license permit the intended deployment?

Does the model depend on a remote proprietary API?
```

A result should therefore not automatically become:

```text
isLocallyDeployable = true
```

simply because the model exists on Hugging Face.

The technical profile can still be generated even when local deployability is:

```text
false
```

or:

```text
unknown
```

Model research and deployment suitability are separate questions.

---

# 20. Research Evidence

Technical fields should be associated with the evidence used to derive them.

Potential evidence sources include:

```text
Hugging Face metadata
Model card
GitHub
Research paper
Official documentation
Web source
```

The resulting relationship should conceptually be:

```text
Technical claim
      ↓
Supporting evidence
      ↓
Original source
```

This makes the final profile easier to inspect and allows the later LLM analysis to operate from grounded information.

---

# 21. Role of `buildTechnicalProfile.py`

The research implementation includes:

```text
app/agents/research/buildTechnicalProfile.py
```

Its purpose is to construct the structured technical representation of the model from the research evidence.

Conceptually:

```text
HF metadata
       +
Model card
       +
Targeted secondary evidence
       ↓
buildTechnicalProfile
       ↓
TechnicalProfile
```

The builder should focus on factual extraction and normalisation.

It should not become responsible for broad subjective conclusions about whether the model is "good" or "bad".

Those conclusions belong to the later analysis stage.

---

# 22. Final LLM Analysis

Once the TechnicalProfile has been assembled, the structured evidence can be passed to an LLM for final interpretation.

This stage answers a different type of question.

Research asks:

```text
"What do we know?"
```

The LLM analysis asks:

```text
"What does it mean?"
```

The LLM may analyse areas such as:

```text
Strengths

Weaknesses

Important limitations

Likely use cases

Deployment trade-offs

Hardware practicality

Model maturity

Potential operational concerns

Comparison considerations

Suitability for the intended NestScanner / EchoForge environment
```

For example:

```text
Technical Profile
├── 769M parameters
├── multilingual
├── WER benchmark results
├── CUDA support
├── downloadable weights
├── MIT license
└── hardware requirements
        ↓
LLM Analysis
        ↓
"Strong multilingual ASR capability, but the model is
significantly heavier than smaller Whisper variants and
may be unsuitable for resource-constrained deployment..."
```

The important point is that the LLM receives the evidence that NestScanner has already collected.

It should not be expected to recall factual details from its own training data.

---

# 23. Why LLM Analysis Happens Last

Running the LLM after research gives the system a cleaner reasoning architecture.

Bad approach:

```text
Model name
    ↓
LLM
    ↓
"Research result"
```

In this design, factual information may depend heavily on what the LLM happens to remember.

NestScanner instead uses:

```text
Model
  ↓
Source retrieval
  ↓
Evidence
  ↓
Structured extraction
  ↓
TechnicalProfile
  ↓
LLM
  ↓
Analysis
```

The final LLM analysis is therefore grounded in the model's current technical evidence.

---

# 24. Research Output

The final research result can conceptually contain two major components:

```text
ResearchResult
│
├── technicalProfile
│      └── structured factual information
│
└── analysis
       └── LLM interpretation of that information
```

This separation is useful because downstream systems can decide whether they need:

```text
raw structured facts
```

or:

```text
human-readable analysis
```

without mixing the two.

---

# 25. Recency Is a Discovery Concern

The Research Agent should not be responsible for deciding whether a model is recent enough to research.

Recency and freshness belong primarily to the Discovery stage.

For example:

```text
HF lastModified
       ↓
Discovery freshness check
       ↓
Should this model be researched?
```

Once the model enters Research:

```text
Research Agent
      ↓
Build the best available technical profile
```

This keeps research independent of why the model was selected.

---

# 26. Database Layer

Database interaction should remain centralised rather than being distributed randomly across agents.

Conceptually:

```text
Discovery Agent ─┐
Research Agent  ─┼──→ db.py ───→ Database
API             ─┘
```

The database stores persistent concepts such as:

```text
Models
Scans
Scan-model relationships
Research results
Technical profiles
Research timestamps
```

---

# 27. Model Identity and Research History

NestScanner separates the permanent identity of a model from individual research executions.

Conceptually:

```text
Model
│
├── Research Result — Scan 1
├── Research Result — Scan 4
└── Research Result — Scan 8
```

The model itself remains the same model:

```text
openai/whisper-medium
```

while its research information may change over time as:

```text
the repository changes
new benchmarks appear
documentation improves
deployment information changes
```

This allows NestScanner to maintain historical research rather than overwriting all previous results.

---

# 28. Scan History

Each scan represents a historical discovery event.

For example:

```text
Scan A
│
├── Model X
├── Model Y
└── Model Z

Scan B
│
├── Model X
└── Model Q
```

This allows NestScanner to answer questions such as:

```text
When was this model discovered?

Which scan selected it?

When was it last researched?

Why was it researched again?

What information changed?
```

---

# 29. Example End-to-End Flow

Suppose discovery finds:

```text
organisation/example-asr-large
```

Hugging Face reports:

```text
lastModified = 2026-10-10
```

NestScanner checks the database.

The most recent completed research occurred on:

```text
2026-09-20
```

Since:

```text
2026-10-10 > 2026-09-20
```

the model is:

```text
STALE
```

and enters Research.

Research retrieves:

```text
HF API metadata
HF model card
repository metadata
```

From those sources NestScanner finds:

```text
architecture        ✓
parameters          ✓
languages           ✓
license             ✓
base model          ✓
benchmark           ✓
training dataset    ?
hardware            ?
```

Rather than performing a generic web search, Research searches specifically for:

```text
training dataset
hardware requirements
```

using authoritative sources.

The gathered information becomes:

```text
TechnicalProfile
```

The profile is then provided to the LLM.

The LLM produces the final interpretation:

```text
strengths
limitations
deployment trade-offs
suitability
important observations
```

Finally:

```text
TechnicalProfile
        +
LLM Analysis
        ↓
ResearchResult
        ↓
Database
```

---

# 30. Complete Backend Workflow

The resulting NestScanner backend architecture is:

```text
                       API Client
                           │
                           ▼
                    POST /api/startScan
                           │
                           ▼
                      Create Scan
                           │
                           ▼
                   DISCOVERY AGENT
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         Hugging Face API          Database
                │                     │
                └──────────┬──────────┘
                           ▼
                     Deduplicate
                           │
                           ▼
                  Freshness Checking
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
         NEW          UNRESEARCHED         STALE
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                   Candidate Selection
                           │
                      maxCandidates
                           │
                           ▼
                    RESEARCH AGENT
                           │
                           ▼
                 Hugging Face Metadata
                           +
                      Model Card
                           │
                           ▼
                 Extract Known Fields
                           │
                           ▼
                 Identify Missing Fields
                           │
                           ▼
              Targeted Secondary Research
                 ┌─────────┼─────────┐
                 ▼         ▼         ▼
              GitHub     Papers     Docs
                 └─────────┼─────────┘
                           ▼
                  Research Evidence
                           │
                           ▼
               buildTechnicalProfile
                           │
                           ▼
                   TechnicalProfile
                           │
                           ▼
                     LLM ANALYSIS
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Strengths    Limitations   Suitability
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ResearchResult
                           │
                           ▼
                 saveResearchResult()
                           │
                           ▼
                        Database
```

---

# 31. Separation of Responsibilities

The backend should maintain the following responsibility boundaries.

### API Layer

Responsible for:

```text
receiving requests
starting scans
returning backend responses
```

### Graph / Workflow Layer

Responsible for:

```text
execution order
passing workflow state
moving between Discovery and Research
```

### Discovery

Responsible for:

```text
finding models
preserving HF metadata
deduplicating models
checking existing database state
checking repository freshness
selecting candidates
```

### Research

Responsible for:

```text
retrieving model information
reading model cards
collecting evidence
identifying missing fields
performing targeted searches
building the TechnicalProfile
```

### LLM Analysis

Responsible for:

```text
interpreting the completed TechnicalProfile
identifying strengths and limitations
explaining trade-offs
providing higher-level assessment
```

### Tools

Responsible for:

```text
Hugging Face access
web search
paper search
GitHub / documentation retrieval
other external information retrieval
```

### Database

Responsible for:

```text
persistent model identity
scan history
research history
technical profiles
analysis results
timestamps
```

---

# 32. Deprecated Implementations

Older implementations may remain in deprecated directories for reference.

They should not participate in the active workflow.

For example:

```text
app/
├── agents/
│   ├── discovery/
│   └── research/
│
└── agents_deprecated/
```

Only:

```text
app/agents/
```

should be used by the active application.

Deprecated files do not execute simply because they exist.

If an error points to an active file such as:

```text
app/agents/research/buildTechnicalProfile.py
```

then the problem is in the active implementation.

However, when code is copied from deprecated implementations, old imports may still remain.

For example:

```python
from backend.app.tools.arxivSearch import ...
```

should be changed to the current convention:

```python
from app.tools.arxivSearch import ...
```

---

# 33. Environment Configuration

Machine-specific settings and credentials should be stored in:

```text
backend/.env
```

with example configuration documented in:

```text
sample.env
```

Where NestScanner interacts with EchoForge, configuration such as:

```text
ECHOFORGE_ROOT
```

should be loaded from environment configuration instead of being hardcoded.

Secrets, local paths, tokens, and machine-specific configuration should not be committed directly into the source code.

---

# 34. Current Design Principles

The current backend follows several important principles.

### 1. Discovery and research are separate

```text
Discovery:
Should we research this model?

Research:
What do we know about this model?
```

---

### 2. Hugging Face is the primary model source

Use repository metadata and the model card before searching elsewhere.

---

### 3. Secondary research is targeted

Do not repeatedly search for facts already available from the model repository.

Search only for important missing or ambiguous information.

---

### 4. Facts and analysis are separate

```text
TechnicalProfile
      =
structured facts

LLM Analysis
      =
interpretation of those facts
```

---

### 5. Missing information stays missing

NestScanner should prefer:

```text
unknown
```

over an unsupported guess.

---

### 6. Model lineage matters

Fine-tuned, adapter, merged, and quantized models should not be treated as unrelated standalone architectures.

---

### 7. Benchmarks need context

A metric without its dataset, subset, language, and source is not sufficient for meaningful comparison.

---

### 8. Deployability must be evidence-based

Do not infer that a model is locally deployable solely because it appears on Hugging Face.

---

### 9. Research is historical

A model may have several research results over time.

Do not overwrite the concept of historical research with only the latest scan.

---

# 35. Current Backend Scope

The backend currently centres around:

```text
✓ FastAPI backend

✓ LangGraph workflow

✓ Hugging Face model discovery

✓ Multiple discovery strategies

✓ Model deduplication

✓ Persistent model identity

✓ repositoryId / modelId separation

✓ Database freshness checking

✓ NEW / UNRESEARCHED / STALE / CURRENT handling

✓ Candidate limiting

✓ Agent-based research

✓ Hugging Face metadata extraction

✓ Model-card research

✓ Targeted secondary research

✓ TechnicalProfile construction

✓ Model lineage extraction

✓ Base-model relationships

✓ Training-dataset research

✓ Benchmark extraction

✓ Inference/runtime information

✓ Hardware requirement research

✓ Evidence-based local-deployment assessment

✓ Research evidence collection

✓ Final LLM analysis

✓ Persistent research history
```

---

# 36. Summary

NestScanner should be understood as a persistent model intelligence pipeline rather than simply a model search application.

The backend follows:

```text
DISCOVER
   ↓
CHECK EXISTING KNOWLEDGE
   ↓
SELECT MODELS REQUIRING WORK
   ↓
RESEARCH PRIMARY SOURCES
   ↓
IDENTIFY INFORMATION GAPS
   ↓
PERFORM TARGETED RESEARCH
   ↓
BUILD STRUCTURED TECHNICAL PROFILE
   ↓
LET THE LLM INTERPRET THE EVIDENCE
   ↓
SAVE THE RESULT
   ↓
USE IT DURING FUTURE SCANS
```

In its simplest form:

```text
Sources
   ↓
Facts
   ↓
TechnicalProfile
   ↓
LLM Analysis
   ↓
Persistent Model Intelligence
```

That separation between **source retrieval**, **structured factual research**, and **LLM interpretation** is the core of the current NestScanner backend design.