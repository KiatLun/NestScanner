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
    webResultsPerQuery: int = 5
    huggingFaceResultsPerQuery: int = 20
    githubResultsPerQuery: int = 10
    arxivResultsPerQuery: int = 5


    # Candidate generation
    maxCandidates: int = 10

    # Logging
    verbose: bool = True


defaultDiscoveryConfig = DiscoveryConfig()
