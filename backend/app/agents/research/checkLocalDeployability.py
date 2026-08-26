import json

from app.llm.client import getLLM

llm = getLLM()


def checkLocalDeployability(
    currentModel: dict,
    deeperEvidence: list[dict],
) -> bool:
    """
    Check whether the model appears locally deployable.

    Requirements:

    1. Public/downloadable model weights exist.
    2. The model can run using local code/frameworks.
    """

    if not deeperEvidence:
        return False

    response = llm.invoke(f"""
You are checking whether an ASR model can be deployed locally.

Candidate:

{json.dumps(currentModel, indent=2)}

Research evidence:

{json.dumps(deeperEvidence, indent=2)}

Return true ONLY if BOTH conditions are supported by
the supplied evidence:

1. Public model weights are available or downloadable.

2. The model can be run locally using publicly available
   code or a local inference framework.

Evidence of local inference may include:

- from_pretrained
- Transformers
- PyTorch
- ONNX
- vLLM
- local inference scripts
- inference.py
- model loading examples
- downloadable checkpoints
- local installation/inference instructions

Important:

- A GitHub repository alone is NOT enough.
- A paper alone is NOT enough.
- A model being available through an API does NOT prove
  local deployability.
- Do not assume missing information.
- Do not perform new research.
- Judge only from the supplied evidence.

Return ONLY:

true

or

false
""")

    result = response.content.strip().lower()

    return result == "true"
