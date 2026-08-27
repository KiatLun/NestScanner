from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.models.state import ScanState

from app.agents.discovery import discoveryAgent
from app.agents.research import researchAgent


def build_graph():

    workflow = StateGraph(ScanState)

    workflow.add_node(
        "discovery",
        discoveryAgent,
    )

    workflow.add_node(
        "research",
        researchAgent,
    )

    workflow.add_edge(
        START,
        "discovery",
    )

    workflow.add_edge(
        "discovery",
        "research",
    )

    workflow.add_edge(
        "research",
        END,
    )

    return workflow.compile()
