from langgraph.graph import StateGraph, START, END

from app.models.state import ScanState

from app.agents.discovery import discoveryAgent
from app.agents.research import research_agent
from app.agents.verification import verification_agent

from app.graph.routing import verification_router


def build_graph():
    workflow = StateGraph(ScanState)

    workflow.add_node(
        "discovery",
        discoveryAgent,
    )

    workflow.add_node(
        "research",
        research_agent,
    )

    workflow.add_node(
        "verification",
        verification_agent,
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
        "verification",
    )

    workflow.add_conditional_edges(
        "verification",
        verification_router,
        {
            "research_again": "research",
            "done": END,
        },
    )

    return workflow.compile()
