from dataclasses import dataclass


@dataclass
class ResearchConfig:

    # =================================================
    # RECENCY
    # =================================================

    recencyWindowDays: int = 180
    maxRecencySearches: int = 3
    recencyResultsPerSearch: int = 5

    # =================================================
    # DEPLOYABILITY
    # =================================================

    maxDeployabilitySearches: int = 3
    deployabilityResultsPerSearch: int = 5

    # =================================================
    # TECHNICAL PROFILE
    # =================================================

    technicalResultsPerSearch: int = 5
    technicalHuggingFaceResults: int = 10
    technicalGithubResults: int = 5
    technicalArxivResults: int = 5

    # =================================================
    # LOGGING
    # =================================================

    verbose: bool = True


defaultResearchConfig = ResearchConfig()
