# Onboarding Agent

Before onboarding begins, Research Agent results are compared against models already known by `echoforge`. Existing models are skipped, and only new models proceed to onboarding.

## Onboarding Flow

### 1. Check for a known model family — `modelInfoReader.py` + `downloaderResolver.py`

Compare the new model against `model_info.json` and existing `supportedModels`.

```text
New model
→ strong/exact match to known model family?
   ├─ Yes → use the corresponding model-specific downloader
   └─ No  → continue to resolve the download source (step 2)
```

### 2. Determine how the model should be downloaded — `downloadSourceResolver.py`

If the model does not belong to a known family, use the Research Agent evidence and LLM reasoning to determine:

- where the actual model weights are hosted
- the source type
- the likely download mechanism

Possible source types:

- Hugging Face
- GitHub
- direct URL
- mixed/custom

This step distinguishes between:

```text
where the model is documented
vs
where the actual weights are downloaded from
```

### 3. Match against existing downloaders — `downloaderResolver.py`

Use the resolved download information to check whether any existing `echoforge` downloader can already handle the model.

```text
Resolved download mechanism
→ compatible existing downloader?
   ├─ Yes → use that downloader
   └─ No  → check generic fallback downloader
```

### 4. Use generic fallback downloader where possible — `downloaderResolver.py`

If no existing model-specific downloader is suitable:

```text
Source is Hugging Face?
   ├─ Yes → use generic hugging_face_download
   └─ No  → mark as needs-downloader
```

### 5. Attempt the download — `onboardingDownloadExecutor.py` + `modelDownloader.py`

If a usable downloader is found:

```text
Selected downloader
→ run echoforge download
→ verify expected cache is created
→ download complete
```

If no usable downloader exists:

```text
status = needs-downloader
```

## Overall Flow

```text
New Research Agent model
        ↓
Known model family?
   ┌────┴────┐
  Yes        No
   ↓          ↓
Use model-   Research evidence
specific     + LLM reasoning
downloader        ↓
             Determine actual
             download source
                  ↓
             Existing downloader
             can handle it?
             ┌────┴────┐
            Yes        No
             ↓          ↓
           Use it    Hugging Face?
                      ┌───┴───┐
                     Yes      No
                      ↓        ↓
                  Generic    needs-
                  HF         downloader
                  downloader
                      ↓
                 Attempt download
                      ↓
                 Verify cache
```
