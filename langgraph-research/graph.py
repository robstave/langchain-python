"""
Graph construction and routing logic.
"""
from langgraph.graph import StateGraph, END

from state import ResearchState
from nodes import planner, search, evaluator, synthesizer


def router(state: ResearchState) -> str:
    """Conditional edge: loop back to planner or proceed to synthesis."""
    return "synthesize" if state["_enough"] else "planner"


def build_graph() -> StateGraph:
    """Constructs the research agent graph."""
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("planner",     planner)
    graph.add_node("search",      search)
    graph.add_node("evaluator",   evaluator)
    graph.add_node("synthesizer", synthesizer)

    # Entry point
    graph.set_entry_point("planner")

    # Edges
    graph.add_edge("planner",    "search")
    graph.add_edge("search",     "evaluator")

    # Conditional: evaluator → planner (loop) or synthesizer (done)
    graph.add_conditional_edges(
        "evaluator",
        router,
        {"planner": "planner", "synthesize": "synthesizer"},
    )

    graph.add_edge("synthesizer", END)

    return graph.compile()
