import json

from app.llm.client import getLLM


def resolveDownloadSource(
    researchResult: dict,
) -> dict:

    candidate = researchResult.get(
        "candidate",
        {},
    )

    modelName = candidate.get("name")

    candidateSourceUrl = candidate.get("sourceUrl")

    researchEvidence = researchResult.get(
        "researchEvidence",
        {},
    )

    deployabilityEvidence = researchEvidence.get(
        "deployabilityEvidence",
        [],
    )

    technicalEvidence = researchEvidence.get(
        "technicalEvidence",
        [],
    )

    evidenceForLLM = []

    # Primary evidence:
    # deployability evidence is most relevant
    # for deciding how the model can be obtained.
    for evidence in deployabilityEvidence[:12]:

        evidenceForLLM.append(
            {
                "evidenceType": "deployability",
                "source": evidence.get("source"),
                "title": evidence.get("title"),
                "url": evidence.get("url"),
                "description": evidence.get("description"),
            }
        )

    # Technical evidence can sometimes contain the
    # actual model repository even when deployability
    # evidence only points to GitHub/documentation.
    for evidence in technicalEvidence[:8]:

        evidenceForLLM.append(
            {
                "evidenceType": "technical",
                "source": evidence.get("source"),
                "title": evidence.get("title"),
                "url": evidence.get("url"),
                "description": evidence.get("description"),
            }
        )

    prompt = f"""
You are determining how an open-source ASR model
should actually be downloaded for local deployment.

Model:
{modelName}

Candidate source URL:
{candidateSourceUrl}

Research evidence:
{json.dumps(evidenceForLLM, indent=2)}

Your task is to identify the actual source from which
the model weights should be obtained.

The candidate source URL is NOT necessarily the
download location.

For example:

- A candidate may point to a GitHub repository,
  while the actual model weights are hosted on
  Hugging Face.

- A candidate may point to a blog or documentation
  page, while the weights are hosted elsewhere.

Possible source types:

1. huggingface

Use this when the actual model weights are hosted
in a Hugging Face model repository and can be
downloaded normally from that repository.

For Hugging Face:

source MUST contain only the repository ID.

Correct:
zhifeixie/Mega-ASR

Incorrect:
https://huggingface.co/zhifeixie/Mega-ASR


2. github

Use this when the official GitHub repository itself
is the main source required to obtain the model.

For GitHub:

source MUST be the full GitHub URL.


3. directUrl

Use this when the actual model files are downloaded
directly from an HTTP or HTTPS URL outside normal
Hugging Face or GitHub repository downloading.

For directUrl:

source MUST be the full URL.


4. mixed

Use this when obtaining the complete model requires
multiple different sources or mechanisms.

Example:

GitHub repository
+
weights from another host.


5. custom

Use this when the model has a specialised or
model-specific download procedure that does not
fit the other source types cleanly.


Rules:

1. Prefer the official model weights.

2. Prefer the original model over:
   - quantized variants
   - ONNX conversions
   - MLX conversions
   - GGUF conversions
   - fine-tuned variants
   - mirrors
   - community reuploads

3. Do NOT choose:
   - documentation pages
   - papers
   - blog posts
   - news articles
   - demos
   - unrelated repositories
   - API-only endpoints

4. If an official GitHub repository says that its
   model weights are hosted on Hugging Face, choose
   Hugging Face.

5. If both GitHub and Hugging Face exist:
   - choose Hugging Face if GitHub contains code
     but Hugging Face contains the actual weights.
   - choose GitHub only if GitHub itself is required
     to obtain the model.

6. Do not assume that candidateSourceUrl is the
   correct download source.

7. The returned source should identify the source
   needed for downloading the actual model weights,
   not merely documentation or inference code.

8. If there is insufficient evidence to determine
   the source confidently, use custom rather than
   inventing a source.

Return ONLY valid JSON.

Required format:

{{
    "sourceType": "huggingface | github | directUrl | mixed | custom",
    "source": "...",
    "reason": "..."
}}
"""

    llm = getLLM()

    response = llm.invoke(prompt)

    content = response.content.strip()

    # Remove markdown code fences if the LLM
    # returns ```json ... ```.
    if content.startswith("```"):

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

        if content.lower().startswith("json"):
            content = content[4:].strip()

    try:

        result = json.loads(content)

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Invalid download-source response "
            f"from LLM: {error}\n"
            f"Response: {content}"
        )

    sourceType = result.get("sourceType")

    source = result.get("source")

    reason = result.get("reason")

    validSourceTypes = {
        "huggingface",
        "github",
        "directUrl",
        "mixed",
        "custom",
    }

    if sourceType not in validSourceTypes:

        raise RuntimeError("Invalid sourceType returned " f"by LLM: {sourceType}")

    if not source:

        raise RuntimeError("LLM did not identify a " "download source.")

    # Normalise Hugging Face URLs in case
    # the LLM ignores the requested format.
    if sourceType == "huggingface":

        huggingFacePrefix = "https://huggingface.co/"

        if source.startswith(huggingFacePrefix):
            source = source[len(huggingFacePrefix) :]

        source = source.strip("/")

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "reason": reason,
    }
