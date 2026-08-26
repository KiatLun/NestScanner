import json

from llm.client import getLLM
from models.schemas import VerificationResult
from models.state import ScanState

llm = getLLM()


def verification_agent(state: ScanState) -> dict:
    """
    Verify the technical profile produced by the Research Agent.

    Baseline version:
    - no external tools
    - checks completeness and consistency
    - returns structured verification feedback
    """

    print("\n=== VERIFICATION AGENT ===")

    profile = state["profile"]

    response = llm.invoke(f"""
You are the Verification Agent for an ASR technology scanning system.

Your job is to inspect the Research Agent's technical profile.

Profile:

{json.dumps(profile, indent=2)}

Important fields:

- name
- organisation
- license
- architecture
- parameter_count
- sourceUrl

Check:

1. Whether important fields are missing.
2. Whether any claims contradict each other.
3. Whether any values look suspicious or unsupported.
4. Whether the model actually appears to be an ASR model.
5. Whether source URLs are provided for important claims.

You are NOT responsible for researching missing facts yourself.

Set verified=true only if the profile is sufficiently complete
and internally consistent.

If not verified, return the fields needing more research
and describe any issues.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "verified": true,
  "missingFields": [],
  "issues": []
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    raw_content = response.content

    print("\n=== RAW VERIFICATION RESPONSE ===")
    print(raw_content)

    data = json.loads(raw_content)

    validated = VerificationResult.model_validate(data)

    return {
        "verified": validated.verified,
        "missingFields": validated.missingFields,
        "issues": validated.issues,
        "retryCount": state.get("retryCount", 0) + 1,
    }
