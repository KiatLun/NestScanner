from pprint import pprint

from app.graph.componentBuilding.inferenceComponentResolver import (
    resolveInferenceComponent,
)

component = resolveInferenceComponent(
    modelName="Whisper Small",
    source="openai/whisper-small",
)

pprint(
    component,
    sort_dicts=False,
)
