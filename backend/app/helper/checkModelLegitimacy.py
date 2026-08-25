import json

from app.llm.client import getLLM

llm = getLLM()


def checkModelLegitimacy(
    currentModel: dict,
    deeperEvidence: list[dict],
) -> bool:
    """
    Check whether the discovered model appears to be
    a legitimate released model backed by credible
    public artifacts.
    """

    if not deeperEvidence:
        return False

    response = llm.invoke(f"""
You are checking whether an ASR model is a legitimate,
identifiable model release.

Candidate:

{json.dumps(currentModel, indent=2)}

Research evidence:

{json.dumps(deeperEvidence, indent=2)}

Return true only when the evidence supports that this is
a real ASR model or model family with credible public
artifacts.

Strong evidence includes:

- an official Hugging Face model repository
- an official GitHub repository
- an official project/model page
- an official research paper
- an official model card

Important:

- A generic article is not sufficient.
- A tutorial is not sufficient.
- A leaderboard entry alone is not sufficient.
- A random third-party repository is not sufficient.
- Do not assume that similarly named results are official.
- Prefer evidence tied to the model organisation or authors.
- Do not perform new research.
- Judge only from the supplied evidence.

Return ONLY:

true

or

false
""")

    result = response.content.strip().lower()

    return result == "true"
