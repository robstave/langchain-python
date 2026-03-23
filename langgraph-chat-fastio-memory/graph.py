"""
Graph construction and routing logic.
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from nodes import (
    ask_agent,
    bootstrap_memory,
    choose_action,
    list_history,
    show_results,
    take_prompt,
)
from state import MemoryChatState


def action_router(state: MemoryChatState) -> str:
    action = state.get("action", "done")
    if action == "refine":
        return "refine"
    if action == "list":
        return "list"
    return "done"


def build_graph():
    graph = StateGraph(MemoryChatState)

    graph.add_node("bootstrap_memory", bootstrap_memory)
    graph.add_node("take_prompt", take_prompt)
    graph.add_node("ask_agent", ask_agent)
    graph.add_node("show_results", show_results)
    graph.add_node("choose_action", choose_action)
    graph.add_node("list_history", list_history)

    graph.set_entry_point("bootstrap_memory")
    graph.add_edge("bootstrap_memory", "take_prompt")
    graph.add_edge("take_prompt", "ask_agent")
    graph.add_edge("ask_agent", "show_results")
    graph.add_edge("show_results", "choose_action")

    graph.add_conditional_edges(
        "choose_action",
        action_router,
        {
            "done": END,
            "refine": "ask_agent",
            "list": "list_history",
        },
    )

    graph.add_edge("list_history", "choose_action")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
