"""
Graph construction and routing logic.
"""
from langgraph.graph import StateGraph, END

from state import ResearchState
from nodes import planner, search, evaluator, synthesizer, feedback, export_markdown


def evaluator_router(state: ResearchState) -> str:
    """Conditional edge: loop back to planner or proceed to synthesis."""
    return "synthesize" if state["_enough"] else "planner"


def feedback_router(state: ResearchState) -> str:
    """
    After feedback, decide where to go:
    - If user is satisfied (_enough=True): export the answer
    - If user added refinement queries: go straight to search
    - Otherwise: go back to planner for automatic re-planning
    """
    if state["_enough"]:
        return "export"
    # If the user provided specific queries (option 3), skip the planner
    if state["search_queries"]:
        return "search"
    return "planner"


def build_graph() -> StateGraph:
    """Constructs the research agent graph."""
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("planner",     planner)
    graph.add_node("search",      search)
    graph.add_node("evaluator",   evaluator)
    graph.add_node("synthesizer", synthesizer)
    graph.add_node("feedback",    feedback)
    graph.add_node("export",      export_markdown)

    # Entry point
    graph.set_entry_point("planner")

    # Edges
    graph.add_edge("planner",    "search")
    graph.add_edge("search",     "evaluator")

    # Conditional: evaluator → planner (loop) or synthesizer (done)
    graph.add_conditional_edges(
        "evaluator",
        evaluator_router,
        {"planner": "planner", "synthesize": "synthesizer"},
    )

    # Synthesizer → Feedback
    graph.add_edge("synthesizer", "feedback")

    # Conditional: feedback → export (done) or planner/search (continue)
    graph.add_conditional_edges(
        "feedback",
        feedback_router,
        {"export": "export", "planner": "planner", "search": "search"},
    )

    graph.add_edge("export", END)

    return graph.compile()
