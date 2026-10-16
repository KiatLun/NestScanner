import json

from huggingface_hub import (
    HfApi,
    hf_hub_download,
)

from app.llm.client import getLLM

from app.models.schemas import (
    TechnicalProfile,
)

from app.agents.research.config import (
    ResearchConfig,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.github import (
    getGitHubTechnicalEvidence,
)

from app.tools.arxivSearch import (
    searchArxivPapers,
)


api = HfApi()
llm = getLLM()


# =========================================================
# HUGGING FACE EVIDENCE
# =========================================================

def getHuggingFaceTechnicalEvidence(
    candidate: dict,
) -> list[dict]:

    repositoryId = candidate.get(
        "repositoryId"
    )

    if not repositoryId:
        return []

    evidence = []

    modelUrl = (
        f"https://huggingface.co/{repositoryId}"
    )

    # =================================================
    # MODEL METADATA
    # =================================================

    try:

        modelInfo = api.model_info(
            repo_id=repositoryId,
            files_metadata=True,
        )

        cardData = getattr(
            modelInfo,
            "cardData",
            None,
        )

        cardDataDict = {}

        if cardData is not None:

            try:

                if hasattr(
                    cardData,
                    "to_dict",
                ):

                    cardDataDict = (
                        cardData.to_dict()
                    )

                elif isinstance(
                    cardData,
                    dict,
                ):

                    cardDataDict = cardData

            except Exception:

                cardDataDict = {}

        files = []

        for sibling in getattr(
            modelInfo,
            "siblings",
            [],
        ):

            filename = getattr(
                sibling,
                "rfilename",
                None,
            )

            if filename:
                files.append(filename)

        evidence.append(
            {
                "source": "huggingface",

                "title": repositoryId,

                "url": modelUrl,

                "description": (
                    "Exact Hugging Face repository "
                    "metadata and model card metadata."
                ),

                "metadata": {

                    "repositoryId": repositoryId,

                    "pipelineTag": getattr(
                        modelInfo,
                        "pipeline_tag",
                        None,
                    ),

                    "downloads": getattr(
                        modelInfo,
                        "downloads",
                        None,
                    ),

                    "likes": getattr(
                        modelInfo,
                        "likes",
                        None,
                    ),

                    "tags": getattr(
                        modelInfo,
                        "tags",
                        [],
                    ),

                    "libraryName": getattr(
                        modelInfo,
                        "library_name",
                        None,
                    ),

                    "license": cardDataDict.get(
                        "license"
                    ),

                    "baseModel": cardDataDict.get(
                        "base_model"
                    ),

                    "baseModelRelation": (
                        cardDataDict.get(
                            "base_model_relation"
                        )
                    ),

                    "datasets": cardDataDict.get(
                        "datasets"
                    ),

                    "languages": (
                        cardDataDict.get(
                            "language"
                        )
                    ),

                    "pipelineTagFromCard": (
                        cardDataDict.get(
                            "pipeline_tag"
                        )
                    ),

                    "files": files,
                },
            }
        )

    except Exception as error:

        print(
            "Failed to retrieve Hugging Face "
            f"metadata for {repositoryId}:"
        )

        print(error)

    # =================================================
    # MODEL CARD
    # =================================================

    try:

        readmePath = hf_hub_download(
            repo_id=repositoryId,
            filename="README.md",
            repo_type="model",
        )

        with open(
            readmePath,
            "r",
            encoding="utf-8",
        ) as file:

            readme = file.read()

        evidence.append(
            {
                "source": "huggingface",

                "title": (
                    f"{repositoryId} Model Card"
                ),

                "url": modelUrl,

                "description": (
                    "Exact Hugging Face model card."
                ),

                "metadata": {
                    "repositoryId": repositoryId,
                    "content": readme[:40000],
                },
            }
        )

    except Exception as error:

        print(
            "Failed to retrieve Hugging Face "
            f"model card for {repositoryId}:"
        )

        print(error)

    return evidence


# =========================================================
# IDENTIFY MISSING INFORMATION
# =========================================================

def identifyMissingTechnicalInformation(
    candidate: dict,
    evidence: list[dict],
) -> dict:
    """
    Determine which technical fields are still missing.

    For every missing field, generate:
    - one targeted search query
    - the most appropriate external sources

    Hugging Face has already been searched directly,
    so external searches should focus on sources that
    can provide additional information.
    """

    response = llm.invoke(
        f"""
You are planning technical research for ONE exact
automatic speech recognition model.

==================================================
EXACT MODEL
==================================================

{json.dumps(
    candidate,
    indent=2,
    ensure_ascii=False,
)}

==================================================
CURRENT EVIDENCE
==================================================

{json.dumps(
    evidence,
    indent=2,
    ensure_ascii=False,
)}

==================================================
FIELDS TO CHECK
==================================================

Determine whether the supplied evidence is sufficient
to establish each of these fields:

- architecture
- parameterCount
- languages
- license
- baseModel
- baseModelRelation
- reportedWer
- benchmarkDetails
- fineTuningSupport
- trainingDatasets
- inferenceFramework
- inferenceRequirements
- hardwareRequirements

==================================================
IMPORTANT
==================================================

The candidate repositoryId is the exact identity
of the model.

Do NOT mix information from another model.

Different parameter-size variants are different models.

Do NOT infer information merely from the model name.

If the evidence already establishes a field reliably,
do NOT search for that field again.

If the field cannot be established from the current
evidence, mark it as missing.

==================================================
SOURCE STRATEGY
==================================================

For each missing field, choose appropriate sources.

Architecture:
- web
- github
- arxiv

Parameter count:
- web
- arxiv

Languages:
- web

License:
- web

Base model:
- web
- arxiv

Base model relationship:
- web
- arxiv

WER:
- web
- arxiv

Benchmark details:
- web
- arxiv

Fine-tuning:
- web
- github

Training datasets:
- web
- github
- arxiv

Inference framework:
- web
- github

Inference requirements:
- web
- github

Hardware requirements:
- web
- github

Do not automatically use every source for every field.

==================================================
SEARCH QUERY RULES
==================================================

Queries must identify the exact model.

Prefer:

"exact-model-name" architecture

"exact-model-name" parameter count

"exact-model-name" fine tuning

"exact-model-name" WER benchmark

Do NOT generate queries such as:

site:huggingface.co exact-model-name architecture

Do NOT restrict general web searches to Hugging Face.

The purpose of external research is to find
information outside the directly retrieved HF evidence.

==================================================
GITHUB SEARCH RULES
==================================================

GitHub repositories may use a project name rather than
the exact Hugging Face repository ID.

Therefore, queries should be suitable for finding the
underlying project.

For example:

"ELARSpeech" fine tuning

rather than only:

"Sanghyang00/ELARSpeech-Whisper-Large-v3-auk"

==================================================
ARXIV SEARCH RULES
==================================================

Academic papers may use the project/model name rather
than the Hugging Face repository ID.

Prefer project names and model names.

For example:

"ELARSpeech" speech recognition

rather than requiring the exact Hugging Face repository ID.

==================================================
FALLBACK SEARCH INFORMATION
==================================================

For every missing field, provide a primary query and
up to two fallback queries.

The fallback queries should become progressively broader
while still preserving model identity.

Example:

Primary:
"ELARSpeech-Whisper-Large-v3-auk" architecture

Fallback 1:
"ELARSpeech" Whisper architecture

Fallback 2:
"ELARSpeech" architecture

Do NOT make the final fallback completely generic.

Bad:

Whisper architecture

==================================================
RETURN FORMAT
==================================================

Return ONLY valid JSON.

Example:

{{
    "missingFields": [
        "architecture",
        "reportedWer",
        "fineTuningSupport"
    ],

    "searches": [
        {{
            "field": "architecture",
            "query": "\"ELARSpeech-Whisper-Large-v3-auk\" architecture",
            "fallbackQueries": [
                "\"ELARSpeech\" Whisper architecture",
                "\"ELARSpeech\" architecture"
            ],
            "sources": [
                "web",
                "github",
                "arxiv"
            ]
        }},

        {{
            "field": "reportedWer",
            "query": "\"ELARSpeech-Whisper-Large-v3-auk\" WER benchmark",
            "fallbackQueries": [
                "\"ELARSpeech\" WER",
                "\"ELARSpeech\" benchmark"
            ],
            "sources": [
                "web",
                "arxiv"
            ]
        }},

        {{
            "field": "fineTuningSupport",
            "query": "\"ELARSpeech-Whisper-Large-v3-auk\" fine tuning",
            "fallbackQueries": [
                "\"ELARSpeech\" fine tuning",
                "\"ELARSpeech\" training"
            ],
            "sources": [
                "web",
                "github"
            ]
        }}
    ]
}}

If no fields are missing:

{{
    "missingFields": [],
    "searches": []
}}

Every missing field must have a corresponding
search object.

Do not include markdown.
Do not include explanations outside the JSON.
"""
    )

    try:

        return json.loads(
            response.content
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ):

        return {
            "missingFields": [],
            "searches": [],
        }


# =========================================================
# TARGETED EXTERNAL RESEARCH
# =========================================================

def gatherTargetedTechnicalEvidence(
    candidate: dict,
    searches: list[dict],
    config: ResearchConfig,
) -> list[dict]:
    """
    Perform targeted research for every missing
    technical field.

    Each search specifies:
    - field
    - primary query
    - fallback queries
    - appropriate sources

    A fallback query is only used when the previous
    query returns no results.
    """

    evidence = []

    # =================================================
    # SEARCH EACH MISSING FIELD
    # =================================================

    for search in searches:

        field = search.get(
            "field"
        )

        primaryQuery = search.get(
            "query"
        )

        fallbackQueries = search.get(
            "fallbackQueries",
            [],
        )

        sources = search.get(
            "sources",
            [],
        )

        if not primaryQuery:
            continue

        if config.verbose:

            print(
                "\n=== TARGETED TECHNICAL RESEARCH ==="
            )

            print(
                "Field:",
                field,
            )

            print(
                "Sources:",
                ", ".join(sources),
            )

        # =================================================
        # BUILD QUERY LIST
        # =================================================

        queries = [
            primaryQuery
        ]

        queries.extend(
            fallbackQueries[:2]
        )

        fieldEvidence = []

        # =================================================
        # TRY QUERIES IN ORDER
        # =================================================

        for queryIndex, query in enumerate(
            queries
        ):

            if config.verbose:

                print(
                    "Search:",
                    queryIndex + 1,
                    "/",
                    len(queries),
                )

                print(
                    "Query:",
                    query,
                )

            # =================================================
            # WEB
            # =================================================

            if "web" in sources:

                try:

                    webResults = webSearch(
                        query,
                        maxResults=(
                            config.technicalResultsPerSearch
                        ),
                    )

                    if webResults:

                        fieldEvidence.extend(
                            webResults
                        )

                        if config.verbose:

                            print(
                                f"Web results: "
                                f"{len(webResults)}"
                            )

                    else:

                        if config.verbose:

                            print(
                                "Web search returned "
                                "no results."
                            )

                except Exception as error:

                    if config.verbose:

                        print(
                            "Technical web search failed:"
                        )

                        print(error)

            # =================================================
            # GITHUB
            # =================================================

            if "github" in sources:

                try:

                    githubResults = (
                        getGitHubTechnicalEvidence(
                            query=query,
                            limit=(
                                config.technicalGithubResults
                            ),
                            maxRepositories=3,
                            maxFilesPerRepository=8,
                            maxCharactersPerFile=15000,
                        )
                    )

                    if githubResults:

                        fieldEvidence.extend(
                            githubResults
                        )

                        if config.verbose:

                            print(
                                f"GitHub technical evidence: "
                                f"{len(githubResults)}"
                            )

                    else:

                        if config.verbose:

                            print(
                                "GitHub search returned "
                                "no technical evidence."
                            )

                except Exception as error:

                    if config.verbose:

                        print(
                            "GitHub technical search failed:"
                        )

                        print(error)

            # =================================================
            # ARXIV
            # =================================================

            if "arxiv" in sources:

                try:

                    arxivResults = (
                        searchArxivPapers(
                            query,
                            limit=(
                                config.technicalArxivResults
                            ),
                        )
                    )

                    if arxivResults:

                        fieldEvidence.extend(
                            arxivResults
                        )

                        if config.verbose:

                            print(
                                f"arXiv results: "
                                f"{len(arxivResults)}"
                            )

                    else:

                        if config.verbose:

                            print(
                                "arXiv search returned "
                                "no results."
                            )

                except Exception as error:

                    if config.verbose:

                        print(
                            "arXiv technical search failed:"
                        )

                        print(error)

            # =================================================
            # STOP FALLBACKS IF WE FOUND EVIDENCE
            # =================================================

            if fieldEvidence:
                break

        evidence.extend(
            fieldEvidence
        )

    return deduplicateResults(
        evidence
    )


# =========================================================
# BUILD TECHNICAL PROFILE
# =========================================================

def buildTechnicalProfile(
    candidate: dict,
    discoveryEvidence: list[dict],
    deployabilityEvidence: list[dict],
    releaseDate: str | None,
    config: ResearchConfig,
) -> dict:
    """
    Build a technical profile for ONE exact model.

    Research flow:

    1. Discovery evidence
    2. Exact Hugging Face repository
    3. Hugging Face model card
    4. Identify ALL missing information
    5. Research EVERY missing field
    6. Final LLM extraction
    7. Pydantic validation
    """

    repositoryId = candidate.get(
        "repositoryId"
    )

    if not repositoryId:

        raise ValueError(
            "Candidate is missing repositoryId."
        )

    # =================================================
    # 1. INITIAL EVIDENCE
    # =================================================

    evidence = []

    evidence.extend(
        discoveryEvidence
    )

    evidence.extend(
        deployabilityEvidence
    )

    # =================================================
    # 2. HUGGING FACE
    # =================================================

    if config.verbose:

        print(
            "\n=== HUGGING FACE TECHNICAL RESEARCH ==="
        )

    huggingFaceEvidence = (
        getHuggingFaceTechnicalEvidence(
            candidate
        )
    )

    evidence.extend(
        huggingFaceEvidence
    )

    evidence = deduplicateResults(
        evidence
    )

    # =================================================
    # 3. IDENTIFY ALL INFORMATION GAPS
    # =================================================

    researchPlan = (
        identifyMissingTechnicalInformation(
            candidate,
            evidence,
        )
    )

    missingFields = researchPlan.get(
        "missingFields",
        [],
    )

    searches = researchPlan.get(
        "searches",
        [],
    )

    # =================================================
    # VALIDATE SEARCH PLAN
    # =================================================

    searchFields = {
        search.get("field")
        for search in searches
        if search.get("field")
    }

    missingSearchFields = [
        field
        for field in missingFields
        if field not in searchFields
    ]

    if config.verbose and missingSearchFields:

        print(
            "\nWARNING: Missing technical fields "
            "without searches:"
        )

        for field in missingSearchFields:

            print(
                f"- {field}"
            )

    # =================================================
    # LOG INFORMATION GAPS
    # =================================================

    if config.verbose:

        print(
            "\n=== TECHNICAL INFORMATION GAPS ==="
        )

        if missingFields:

            for field in missingFields:

                print(
                    f"- {field}"
                )

        else:

            print(
                "No major information gaps."
            )

        print(
            "\nTechnical searches to perform:",
            len(searches),
        )

    # =================================================
    # 4. RESEARCH EVERY GAP
    # =================================================

    if searches:

        externalEvidence = (
            gatherTargetedTechnicalEvidence(
                candidate,
                searches,
                config,
            )
        )

        evidence.extend(
            externalEvidence
        )

        evidence = deduplicateResults(
            evidence
        )

    # =================================================
    # 5. FINAL LLM EXTRACTION
    # =================================================

    response = llm.invoke(
        f"""
You are building a technical profile for ONE exact
automatic speech recognition model.

The model identity has already been established.

==================================================
EXACT MODEL
==================================================

{json.dumps(
    candidate,
    indent=2,
    ensure_ascii=False,
)}

Exact Hugging Face repository:

{repositoryId}


==================================================
RELEASE DATE
==================================================

{releaseDate}


==================================================
EVIDENCE
==================================================

{json.dumps(
    evidence,
    indent=2,
    ensure_ascii=False,
)}


==================================================
TASK
==================================================

Extract ONLY information supported by the evidence.

Fields:

- architecture
- parameterCount
- languages
- license
- baseModel
- baseModelRelation
- reportedWer
- benchmarkDetails
- fineTuningSupport
- trainingDatasets
- inferenceFramework
- inferenceRequirements
- hardwareRequirements


==================================================
GENERAL RULES
==================================================

1. Use ONLY the supplied evidence.

2. Do NOT fabricate information.

3. Do NOT guess.

4. Do NOT use information from another model.

5. Different parameter-size variants are different models.

6. The exact Hugging Face repository is the model identity.

7. Prefer evidence from the exact Hugging Face repository.

8. External evidence must refer to the exact model.

9. If evidence conflicts, prefer the more authoritative source.

10. If a field cannot be established reliably, return null.

11. For list fields, return [] when no reliable information exists.


==================================================
BASE MODEL
==================================================

Determine whether this model is derived from another model.

Examples:

baseModel:
"openai/whisper-large-v3"

baseModelRelation:
"finetune"


Allowed baseModelRelation values:

- finetune
- adapter
- quantized
- merge
- unknown
- null


Do NOT infer a base model merely because another
model name appears in the model name.

Prefer explicit Hugging Face model-card metadata,
official documentation, or strong technical evidence.

If no base model is established:

baseModel = null
baseModelRelation = null


==================================================
ARCHITECTURE
==================================================

Describe the actual architecture only when supported.


==================================================
PARAMETER COUNT
==================================================

Use the parameter count for the exact model.

Do not use another checkpoint's parameter count.


==================================================
LANGUAGES
==================================================

Return only explicitly supported languages.


==================================================
LICENSE
==================================================

Use the license associated with the exact model
repository or weights.


==================================================
WER
==================================================

Return reported WER only when explicitly supported.

Include benchmark context when possible.

Do NOT:

- convert CER to WER
- treat CER as WER
- invent WER
- combine unrelated benchmarks
- combine different model variants

If only CER is available:

null


==================================================
BENCHMARK DETAILS
==================================================

Provide useful context such as:

- dataset
- language
- benchmark split
- evaluation setup
- model variant

Return null when reliable context is unavailable.


==================================================
FINE-TUNING
==================================================

Determine whether fine-tuning is explicitly supported.

Useful evidence:

- fine-tuning instructions
- training scripts
- LoRA / PEFT
- training examples
- official training documentation

Do not assume fine-tuning is supported merely because
the underlying framework supports training.


==================================================
TRAINING DATASETS
==================================================

Return dataset names only when explicitly identified
as training datasets.

Do not confuse evaluation datasets with training datasets.


==================================================
INFERENCE FRAMEWORK
==================================================

Identify frameworks explicitly supported for running
the model.

Examples:

- Transformers
- PyTorch
- ONNX Runtime
- CTranslate2


==================================================
INFERENCE REQUIREMENTS
==================================================

Include explicitly documented dependencies or runtime
requirements.


==================================================
HARDWARE REQUIREMENTS
==================================================

Include explicitly documented hardware requirements.

Do not invent numerical hardware requirements.


==================================================
RETURN FORMAT
==================================================

Return ONLY valid JSON:

{{
    "architecture": null,
    "parameterCount": null,
    "languages": [],
    "license": null,
    "baseModel": null,
    "baseModelRelation": null,
    "reportedWer": null,
    "benchmarkDetails": null,
    "fineTuningSupport": null,
    "trainingDatasets": [],
    "inferenceFramework": null,
    "inferenceRequirements": null,
    "hardwareRequirements": null
}}

Do not include:

- name
- organisation
- repositoryId
- sourceUrl
- downloads
- likes
- trendingScore
- createdAt
- lastModified
- releaseDate
- sourceUrls

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
"""
    )

    # =================================================
    # 6. PARSE RESPONSE
    # =================================================

    try:

        data = json.loads(
            response.content
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ) as error:

        raise ValueError(
            "LLM returned invalid JSON while "
            "building technical profile."
        ) from error

    # =================================================
    # 7. VALIDATE
    # =================================================

    validated = TechnicalProfile.model_validate(
        data
    )

    # =================================================
    # 8. RETURN
    # =================================================

    return {
        "technicalProfile": (
            validated.model_dump()
        ),

        "evidence": evidence,

        "releaseDate": releaseDate,
    }