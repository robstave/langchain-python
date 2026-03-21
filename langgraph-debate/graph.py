"""Graph construction for the multi-agent debate."""

from langgraph.graph import StateGraph, END
from state import DebateState
from nodes import moderator, pro, con, judge


def judge_router(state: dict) -> str:
    """Route after the judge: continue debating or finish."""
    if state.get("_done"):
        return "done"
    return "next_round"


def build_graph() -> StateGraph:
    """Build and compile the debate graph."""
    g = StateGraph(DebateState)

    g.add_node("moderator", moderator)
    g.add_node("pro", pro)
    g.add_node("con", con)
    g.add_node("judge", judge)

    g.set_entry_point("moderator")
    g.add_edge("moderator", "pro")
    g.add_edge("pro", "con")
    g.add_edge("con", "judge")

    g.add_conditional_edges("judge", judge_router, {
        "next_round": "pro",
        "done": END,
    })

    return g.compile()
