from dataclasses import dataclass


@dataclass
class DiscoveryConfig:

    # Planner
    useLlmPlanner: bool = False

    # Enable / disable sources
    enableWebSearch: bool = True
    enableHuggingFaceSearch: bool = True
    enableGithubSearch: bool = True
    enableArxivSearch: bool = True

    # Results per query
    webResultsPerQuery: int = 2
    huggingFaceResultsPerQuery: int = 10
    huggingFaceCategoryResults: int = 100
    githubResultsPerQuery: int = 6
    arxivResultsPerQuery: int = 2


    # Candidate generation
    maxCandidates: int = 10

    # Logging
    verbose: bool = True


defaultDiscoveryConfig = DiscoveryConfig()
