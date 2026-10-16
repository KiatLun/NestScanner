# NestScanner --- Discovery & Research Pipeline Redesign

## 1. Objective

Redesign the NestScanner model-discovery workflow so that:

-   **Hugging Face is the primary and currently sole discovery source.**
-   The Discovery Agent identifies ASR models that are worth
    investigating.
-   Each Hugging Face repository ID represents the unique identity of a
    model.
-   Newly discovered models are sent to the Research Agent.
-   Models that have already been researched are skipped.
-   The system can later detect models whose Hugging Face metadata has
    changed and research them again.
-   Hugging Face metadata such as downloads, likes, creation date, and
    modification date can be used for ranking and frontend filtering.
-   The Research Agent performs deeper investigation of an individual
    model rather than discovering models itself.
-   The Evidence Matcher is removed from the critical Discovery path
    because Hugging Face repository IDs provide deterministic model
    identity.

------------------------------------------------------------------------

# 2. Target Architecture

``` text
                         HUGGING FACE
                              |
                              v
                    ASR model catalogue
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
        Created recent   Modified recent   Downloads high
             |                |                |
             +----------------+----------------+
                              |
                    Likes / other ranking
                              |
                              v
                       Candidate Pool
                              |
                              v
                    Python Deduplication
                              |
                              v
                     DISCOVERY AGENT
                              |
                    +---------+---------+
                    |                   |
             Already known          New / changed
                    |                   |
                   Skip                  v
                              RESEARCH AGENT
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
                    Hugging Face API          Model Card
                         |                         |
                         +------------+------------+
                                      |
                                      v
                              Technical Profile
                                      |
                                      v
                                 LLM Analysis
                                      |
                                      v
                            "Worth considering?"
                                      |
                                      v
                                  DATABASE
                                      |
                                      v
                                  DASHBOARD
```

------------------------------------------------------------------------

# 3. Current Problem

The original Discovery implementation was designed around multiple
evidence sources:

``` text
Hugging Face
Web Search
GitHub
arXiv
      |
      v
Evidence Matcher / LLM
      |
      v
Discovery Candidates
```

This created several problems:

1.  Hugging Face discovery was limited by keyword searches.
2.  A model could be missed if its name did not obviously contain `ASR`.
3.  The LLM Evidence Matcher was being asked to determine model identity
    even when a Hugging Face repository ID already uniquely identifies
    the repository.
4.  The workflow became unnecessarily dependent on web, GitHub, and
    arXiv search.
5.  Discovery and research responsibilities became blurred.
6.  A model that was already present in the database could be
    rediscovered repeatedly.

The new architecture separates these responsibilities.

------------------------------------------------------------------------

# 4. Hugging Face Discovery

## 4.1 ASR classification

The Hugging Face API should use:

``` python
pipeline_tag="automatic-speech-recognition"
```

as the primary ASR filter.

This is preferable to searching for strings such as:

``` text
ASR
speech recognition
speech-to-text
transcription
```

because a valid ASR model does not necessarily have `ASR` in its
repository name.

------------------------------------------------------------------------

## 4.2 Discovery views

The Hugging Face API should retrieve models through several catalogue
views:

### Recently created

Find newly published ASR models.

``` text
sort = created_at
```

### Recently modified

Find ASR models that have recently changed.

``` text
sort = last_modified
```

### Most downloaded

Find established/popular ASR models.

``` text
sort = downloads
```

### Most liked

Likes can be used as another popularity signal if supported by the
Hugging Face API version in use.

### Trending

Trending score can be collected when available, but should **not be
relied upon as the primary ranking signal** because it has not been
populating reliably.

------------------------------------------------------------------------

# 5. Hugging Face Result Structure

Each discovered model should be converted into a consistent result
structure.

Example:

``` json
{
  "source": "huggingface",
  "title": "Qwen/Qwen3-ASR-0.6B",
  "url": "https://huggingface.co/Qwen/Qwen3-ASR-0.6B",
  "description": null,
  "metadata": {
    "repositoryId": "Qwen/Qwen3-ASR-0.6B",
    "organisation": "Qwen",
    "pipelineTag": "automatic-speech-recognition",
    "downloads": 12345,
    "likes": 100,
    "createdAt": "...",
    "lastModified": "...",
    "tags": []
  }
}
```

The important field is:

``` text
repositoryId
```

This should be treated as the canonical identity of the model.

------------------------------------------------------------------------

# 6. Model Identity Rules

A Hugging Face repository ID identifies one discovery candidate.

For example:

``` text
Qwen/Qwen3-ASR-0.6B
Qwen/Qwen3-ASR-1.7B
```

must remain two separate candidates.

Do not collapse them into:

``` text
Qwen3-ASR
```

The same applies to:

-   Base vs Large
-   Small vs Large
-   different parameter sizes
-   language-specific checkpoints
-   domain-specific checkpoints
-   fine-tuned checkpoints
-   distilled checkpoints
-   quantized checkpoints
-   separately published repositories

If they have different Hugging Face repository IDs, they should
initially be treated as separate models.

------------------------------------------------------------------------

# 7. Deduplication

Because one model may appear in multiple discovery views:

``` text
Recently created
Recently modified
Most downloaded
Most liked
```

the same repository can occur several times.

Deduplication should therefore be deterministic:

``` text
repositoryId -> unique candidate
```

Example:

``` text
Qwen/Qwen3-ASR-0.6B
Qwen/Qwen3-ASR-0.6B
Qwen/Qwen3-ASR-0.6B
```

becomes:

``` text
Qwen/Qwen3-ASR-0.6B
```

The existing `deduplicateHFResults()` function is intended for this
purpose.

------------------------------------------------------------------------

# 8. Discovery Agent Responsibility

The Discovery Agent should answer:

> **Which Hugging Face ASR models should we investigate?**

It should not perform deep technical research.

The intended flow is:

``` text
discoverASRModels()
        |
        v
deduplicateHFResults()
        |
        v
compare repository IDs with database
        |
        v
remove already-known/unchanged models
        |
        v
rank/select candidates
        |
        v
save candidates
        |
        v
Research Agent
```

The Discovery Agent does not need an LLM for basic candidate
identification.

------------------------------------------------------------------------

# 9. Existing vs New Models

Every candidate should be checked against the database using its:

``` text
repositoryId
```

The first version of the logic should be:

``` text
Repository ID exists?
       |
   +---+---+
   |       |
  YES      NO
   |       |
  SKIP     NEW
           |
           v
       RESEARCH
```

This prevents every scan from sending the same models to the Research
Agent.

------------------------------------------------------------------------

# 10. Future Changed-Model Detection

After the basic new-model workflow is working, add change detection.

The desired logic is:

``` text
Repository ID exists?
       |
   +---+---+
   |       |
  NO      YES
   |       |
  NEW    lastModified changed?
           |
        +--+--+
        |     |
       NO    YES
        |     |
       SKIP  RESEARCH AGAIN
```

This means:

-   New repository → research.
-   Existing repository with unchanged metadata → skip.
-   Existing repository whose Hugging Face `lastModified` has changed →
    research/update.

This is preferable to permanently skipping a model simply because it has
one historical research result.

------------------------------------------------------------------------

# 11. Candidate Ranking

The Discovery stage should support ranking before Research.

The candidate pool can contain hundreds of models, while only a smaller
number may be practical to research during one scan.

Potential ranking signals:

1.  Downloads
2.  Likes
3.  Recency of creation
4.  Recency of modification
5.  Trending score when available

However, ranking should not make new models impossible to discover.

A useful approach is to build a broad candidate pool from multiple
views:

``` text
Top recently created
+
Top recently modified
+
Top downloaded
+
Top liked
        |
        v
      UNION
        |
        v
   Deduplicate
        |
        v
 Database check
        |
        v
 Candidate selection
```

This allows a newly released model with few downloads to enter the
candidate pool through the "recently created" view.

------------------------------------------------------------------------

# 12. Avoid an Arbitrary Combined Score Initially

Do not immediately create something like:

``` text
score =
    0.4 * downloads
  + 0.3 * likes
  + 0.2 * recency
  + ...
```

Downloads, likes, and dates have different scales and meanings.

Initially, use the separate catalogue views and transparent ranking.

A combined scoring system can be introduced later if needed.

------------------------------------------------------------------------

# 13. Research Agent Responsibility

The Research Agent should answer:

> **What do we know about this specific Hugging Face ASR model?**

It receives a candidate from Discovery and performs deeper
investigation.

The Research flow should be:

``` text
Discovery Candidate
        |
        v
Hugging Face API metadata
        +
Hugging Face Model Card
        |
        v
Technical Profile
        |
        v
LLM Analysis
        |
        v
Worth considering?
```

Potential technical information includes:

-   architecture
-   parameter count
-   supported languages
-   reported WER
-   fine-tuning support
-   license
-   local deployability
-   release information
-   relevant technical evidence

------------------------------------------------------------------------

# 14. Evidence Matcher

The old Evidence Matcher was designed to combine evidence from:

``` text
Hugging Face
Web
GitHub
arXiv
```

and ask the LLM whether pieces of evidence referred to the same model.

That is no longer necessary for the core Discovery flow.

For Hugging Face discovery:

``` text
repositoryId
```

is already a deterministic identity.

Therefore:

``` text
HF API
   |
repositoryId
   |
Python deduplication
   |
Discovery Candidate
```

should replace:

``` text
HF + Web + GitHub + arXiv
   |
LLM Evidence Matcher
   |
Discovery Candidate
```

The Evidence Matcher can remain in the codebase temporarily, but it
should not be required for the new Discovery path.

------------------------------------------------------------------------

# 15. LangGraph Workflow

The existing LangGraph structure is already appropriate:

``` text
START
  |
  v
discoveryAgent
  |
  v
research_agent
  |
  v
END
```

No fundamental change to the graph is required.

The important change is what the individual agents do.

------------------------------------------------------------------------

# 16. ScanState

The existing state structure is sufficient:

``` python
class ScanState(TypedDict, total=False):
    query: str
    scanId: int

    discoveryConfig: dict
    researchConfig: dict

    candidates: list[dict]
    researchResults: list[dict]
```

The main handoff is:

``` text
Discovery Agent
      |
      | state["candidates"]
      v
Research Agent
```

No separate `newCandidates` state field is required.

------------------------------------------------------------------------

# 17. Database Design

The existing database already contains the main concepts needed.

## Models

The `models` table stores unique models and uses:

``` text
repository_id
```

as a unique field.

This aligns with the new architecture.

## Scan Models

`scan_models` links models to a scan and stores:

``` text
discovery_evidence
```

## Research Results

`research_results` stores the research output for a model during a scan.

The existing schema therefore provides the basic persistence layer for:

``` text
Scan
  |
  +-- Model
  |
  +-- Research Result
```

------------------------------------------------------------------------

# 18. Important Database Observation

`saveDiscoveryCandidate()` already checks `repository_id` when saving a
candidate and reuses an existing model ID if the repository already
exists.

Therefore, database identity is already aligned with the new Hugging
Face-based design.

However, **saving and discovery filtering are different
responsibilities**.

The Discovery Agent should filter out models that should not be
researched before sending them downstream.

The save function then persists the selected candidates.

------------------------------------------------------------------------

# 19. Planned File Changes

## `app/tools/huggingFace.py`

Keep this as the Hugging Face integration layer.

Target responsibilities:

``` text
modelToResult()
getNewASRModels()
getRecentlyModifiedASRModels()
getPopularASRModels()
getLikedASRModels()
getTrendingASRModels()   # optional
discoverASRModels()
deduplicateHFResults()
```

The existing keyword search functions should no longer be the primary
discovery mechanism.

------------------------------------------------------------------------

## `app/agents/discovery/search.py`

Simplify this file so that Discovery primarily calls the Hugging Face
discovery functions.

The old:

``` text
Web
GitHub
arXiv
```

search path can be removed from the active Discovery workflow if Hugging
Face remains the sole discovery source.

------------------------------------------------------------------------

## `app/agents/discovery/evidenceMatcher.py`

Remove from the critical Discovery path.

It is not needed to establish identity when the repository ID is
available.

------------------------------------------------------------------------

## `app/agents/discovery/agent.py`

This becomes the main candidate-selection layer.

Target flow:

``` text
discoverASRModels()
        |
deduplicateHFResults()
        |
database comparison
        |
new/changed candidates
        |
maxCandidates
        |
saveDiscoveryCandidate()
```

------------------------------------------------------------------------

## `app/agents/research/__init__.py`

Keep the Research Agent in the LangGraph workflow.

It should receive only the candidates selected by Discovery.

It should skip candidates that do not have a valid internal model ID.

------------------------------------------------------------------------

## `app/agents/research/agent.py`

Use this for the actual deep research process.

It should focus on a specific model rather than discovering models.

------------------------------------------------------------------------

## `app/models/state.py`

No major change is expected.

The existing `candidates` and `researchResults` fields are sufficient.

------------------------------------------------------------------------

## LangGraph workflow file

No major change is expected.

The desired graph is already:

``` text
START
  ↓
Discovery
  ↓
Research
  ↓
END
```

------------------------------------------------------------------------

# 20. Frontend Requirements

The frontend should be able to use the Hugging Face metadata stored for
each model.

Useful fields include:

``` text
repositoryId
downloads
likes
createdAt
lastModified
pipelineTag
tags
trendingScore
```

The frontend should support:

### Filtering

Examples:

``` text
Organisation
Pipeline
Tags
Minimum downloads
Minimum likes
Created date
Last modified date
```

### Ranking / sorting

Examples:

``` text
Most downloaded
Most liked
Newest
Recently modified
Trending
```

Trending should remain optional because its value may be missing or
unreliable.

------------------------------------------------------------------------

# 21. Why This Architecture Is Better

The redesigned pipeline gives each component a clear responsibility.

### Hugging Face integration

> Find ASR repositories.

### Discovery Agent

> Decide which repositories are new/relevant enough to research.

### Database

> Remember which repositories have already been seen/researched.

### Research Agent

> Investigate a specific model.

### LLM

> Interpret technical information and produce higher-level analysis.

### Frontend

> Let users filter, sort, and inspect the resulting model intelligence.

This avoids using an LLM for deterministic tasks that can be handled
directly by the Hugging Face API and database.

------------------------------------------------------------------------

# 22. Implementation Order

Implement the redesign incrementally.

## Step 1 --- Hugging Face discovery

Ensure the API can reliably retrieve:

``` text
recently created
recently modified
most downloaded
most liked
```

ASR models.

Verify that repository IDs are present.

------------------------------------------------------------------------

## Step 2 --- Deduplication

Combine the discovery views and deduplicate using:

``` text
repositoryId
```

Verify that one repository appears only once.

------------------------------------------------------------------------

## Step 3 --- Discovery Agent

Replace the old:

``` text
gatherDiscoveryEvidence()
→ groupModelEvidence()
```

flow with:

``` text
discoverASRModels()
→ deduplicate
→ database filtering
→ candidate selection
```

------------------------------------------------------------------------

## Step 4 --- Database comparison

Implement deterministic repository lookup.

Initially:

``` text
existing repository → skip
new repository → research
```

------------------------------------------------------------------------

## Step 5 --- Research integration

Pass only new candidates to the existing Research Agent.

Verify:

``` text
Discovery
  ↓
Research
```

works through the existing LangGraph state.

------------------------------------------------------------------------

## Step 6 --- Model-card research

Make Research gather:

``` text
HF API
+
HF model card
```

and construct the technical profile.

------------------------------------------------------------------------

## Step 7 --- LLM analysis

Use the LLM after the technical profile has been collected.

The LLM should answer higher-level questions such as:

``` text
Is this model worth considering?
```

rather than determining basic repository identity.

------------------------------------------------------------------------

## Step 8 --- Changed-model detection

Add:

``` text
lastModified
```

comparison so changed models can be researched again.

------------------------------------------------------------------------

## Step 9 --- Frontend filtering and ranking

Expose the stored Hugging Face metadata to the dashboard and add:

``` text
filter
sort
rank
```

controls.

------------------------------------------------------------------------

# 23. Validation Checklist

A successful implementation should satisfy all of the following.

### Discovery

-   [ ] Only Hugging Face is used as the model discovery source.
-   [ ] Models are filtered using the ASR pipeline category.
-   [ ] Newly created models are discovered.
-   [ ] Recently modified models are discovered.
-   [ ] Popular/downloaded models are discovered.
-   [ ] Likes can be used for discovery/ranking.
-   [ ] Trending is optional.
-   [ ] Repository IDs are preserved exactly.
-   [ ] Different checkpoints remain separate.

### Deduplication

-   [ ] Duplicate repository IDs are removed.
-   [ ] A model appearing in multiple catalogue views becomes one
    candidate.

### Database

-   [ ] Existing repository IDs are detected.
-   [ ] Existing unchanged models are skipped.
-   [ ] New models are saved.
-   [ ] Later, changed models can be re-researched.

### Research

-   [ ] Only selected Discovery candidates enter Research.
-   [ ] Research uses Hugging Face metadata/model cards.
-   [ ] Technical profiles are generated.
-   [ ] LLM analysis is performed after technical information is
    collected.

### Frontend

-   [ ] Downloads are visible.
-   [ ] Likes are visible.
-   [ ] Created date is visible.
-   [ ] Last modified date is visible.
-   [ ] Users can filter models.
-   [ ] Users can sort/rank models.
-   [ ] Trending does not block the feature when missing.

------------------------------------------------------------------------

# 24. Final Target

The final NestScanner workflow should behave like this:

``` text
                         NEW SCAN
                            |
                            v
                    Hugging Face API
                            |
             +--------------+--------------+
             |              |              |
          Created        Modified       Popular
          recent          recent        /liked
             |              |              |
             +--------------+--------------+
                            |
                            v
                     Candidate Pool
                            |
                            v
                       Deduplicate
                            |
                            v
                  Compare with Database
                            |
              +-------------+-------------+
              |                           |
         Already known               New / changed
              |                           |
             SKIP                         v
                                  Research Agent
                                        |
                              +---------+---------+
                              |                   |
                           HF API             Model Card
                              |                   |
                              +---------+---------+
                                        |
                                        v
                                Technical Profile
                                        |
                                        v
                                   LLM Analysis
                                        |
                                        v
                              Worth considering?
                                        |
                                        v
                                    Database
                                        |
                                        v
                                    Dashboard
```

The central design principle is:

> **Use deterministic systems for discovery, identity, deduplication,
> and database comparison; use the Research Agent and LLM for deeper
> interpretation and analysis.**
