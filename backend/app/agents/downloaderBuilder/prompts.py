import json


def buildDownloaderGenerationPrompt(
    researchResult: dict,
    downloadDecision: dict,
) -> str:

    return f"""
You are building a new model downloader for echoforge.

Your task is to generate ONLY the files required for one new
echoforge model downloader.

The downloader must download the model into:

    /cache/<cacheName>

You may generate ONLY:

- download.py
- dockerfile
- model_list

Do not modify any existing echoforge files.

The downloader must follow echoforge's existing downloader conventions.

Important concepts:

- downloaderName:
  echoforge downloader directory name.
  Must end in "_download".

- modelListName:
  model identifier used by models_download.py when selecting:
      --name downloaderName:modelListName

- cacheName:
  actual directory created under /cache.

modelListName and cacheName are NOT necessarily the same.

Research result:
{json.dumps(researchResult, indent=2)}

Resolved download decision:
{json.dumps(downloadDecision, indent=2)}

Return ONLY valid JSON with this structure:

{{
    "downloaderName": "example_download",
    "modelListName": "example-model",
    "cacheName": "example",
    "reason": "short explanation",
    "files": {{
        "download.py": "complete file contents",
        "dockerfile": "complete file contents",
        "model_list": "complete file contents"
    }}
}}

Do not return markdown.
Do not return explanations outside the JSON.
""".strip()


def buildDownloaderRepairPrompt(
    researchResult: dict,
    downloadDecision: dict,
    downloaderPlan: dict,
    attemptResult: dict,
) -> str:

    return f"""
You previously generated an echoforge downloader, but execution failed.

Repair ONLY the generated downloader files.

You may modify ONLY:

- download.py
- dockerfile
- model_list

Do not modify:

- models_download.py
- base_downloader.py
- existing downloader directories
- ClearML configuration
- MinIO configuration
- NestScanner source code

Keep these identifiers unchanged:

downloaderName:
{downloaderPlan["downloaderName"]}

modelListName:
{downloaderPlan["modelListName"]}

cacheName:
{downloaderPlan["cacheName"]}

The successful downloader must create:

    /cache/{downloaderPlan["cacheName"]}

Research result:
{json.dumps(researchResult, indent=2)}

Download decision:
{json.dumps(downloadDecision, indent=2)}

Current generated files:
{json.dumps(downloaderPlan["files"], indent=2)}

Execution result:
{json.dumps(attemptResult, indent=2)}

Determine the likely cause of failure and repair the downloader.

Return ONLY valid JSON:

{{
    "reason": "what failed and what was changed",
    "files": {{
        "download.py": "complete repaired contents",
        "dockerfile": "complete repaired contents",
        "model_list": "complete repaired contents"
    }}
}}

Do not return markdown.
""".strip()
