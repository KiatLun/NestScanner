from dataclasses import dataclass


@dataclass
class ResearchConfig:

    # =================================================
    # DEPLOYABILITY
    # =================================================

    # Maximum number of additional searches that can be
    # performed when determining local deployability.

    maxDeployabilitySearches: int = 1

    # Maximum number of results returned for each
    # deployability search.

    deployabilityResultsPerSearch: int = 3


    # =================================================
    # TECHNICAL PROFILE
    # =================================================

    # Maximum number of general web results returned
    # for each targeted technical search.

    technicalResultsPerSearch: int = 3

    # Maximum number of GitHub results returned for
    # each targeted technical search.

    technicalGithubResults: int = 2

    # Maximum number of arXiv results returned for
    # each targeted technical search.

    technicalArxivResults: int = 2


    # =================================================
    # LOGGING
    # =================================================

    verbose: bool = True


defaultResearchConfig = ResearchConfig()