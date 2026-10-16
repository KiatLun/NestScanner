from dataclasses import dataclass


@dataclass
class DiscoveryConfig:

    # Planner
    useLlmPlanner: bool = False

    # Enable / disable sources
    enableWebSearch: bool = False
    enableHuggingFaceSearch: bool = True
    enableGithubSearch: bool = False
    enableArxivSearch: bool = False

    # Results per query
    webResultsPerQuery: int = 0
    huggingFaceResultsPerQuery: int = 5
    huggingFaceResultsPerDiscoverySource: int = 10
    githubResultsPerQuery: int = 0
    arxivResultsPerQuery: int = 0


    # Candidate generation
    maxCandidates: int = 5

    # Logging
    verbose: bool = True


defaultDiscoveryConfig = DiscoveryConfig()
