import json

from app.llm.client import getLLM

llm = getLLM()


def getModelReleaseDate(
    evidenceGroup: dict,
) -> str | None:

    response = llm.invoke(f"""
You are extracting the actual release date of one ASR model
or model family.

Evidence:

{json.dumps(evidenceGroup, indent=2)}

Find the date when THIS model or model family was actually
released or introduced.

Rules:

1. Use only the supplied evidence.
2. Prefer explicit release statements.
3. Do not use:
   - repository update dates
   - model-card modification dates
   - article publication dates unless the text explicitly says
     the model was released on that date
4. Do not use dates referring to another model.
5. If the release date cannot be determined confidently,
   return null.

Return ONLY valid JSON:

{{
  "releaseDate": "YYYY-MM-DD"
}}

or:

{{
  "releaseDate": null
}}
""")

    try:
        data = json.loads(response.content)

        return data.get("releaseDate")

    except json.JSONDecodeError:
        return None
