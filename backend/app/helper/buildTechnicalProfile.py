import json

from app.llm.client import getLLM
from app.models.schemas import ModelProfile

llm = getLLM()


def buildTechnicalProfile(
    currentModel: dict,
    deeperEvidence: list[dict],
) -> dict:
    """
    Build the technical profile for one ASR model
    using the gathered research evidence.
    """

    response = llm.invoke(f"""
You are performing technical research on an ASR model.

Candidate:

{json.dumps(currentModel, indent=2)}

Research evidence:

{json.dumps(deeperEvidence, indent=2)}

Build a technical profile using ONLY information supported
by the supplied evidence.

Collect:

- name
- organisation
- releaseDate
- license
- architecture
- parameterCount
- languages
- reportedWer
- fineTuningSupport
- sourceUrls

Rules:

1. Do not guess.
2. Do not fabricate information.
3. Use null when a scalar field cannot be determined.
4. Use [] when a list field cannot be determined.
5. Keep benchmark context when reporting WER.
6. Do not treat CER as WER.
7. Prefer official/model-author sources when sources conflict.
8. sourceUrls should contain the most useful evidence URLs.

Return ONLY valid JSON.

Use exactly:

{{
  "name": "model name",
  "organisation": "organisation or null",
  "releaseDate": "release date or null",
  "license": "license or null",
  "architecture": "architecture or null",
  "parameterCount": "parameter count or null",
  "languages": [],
  "reportedWer": "reported WER with context or null",
  "fineTuningSupport": "fine-tuning information or null",
  "sourceUrls": []
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    rawContent = response.content

    print("\n=== RAW TECHNICAL PROFILE ===")
    print(rawContent)

    data = json.loads(rawContent)

    validated = ModelProfile.model_validate(data)

    return validated.model_dump()
