"""
Graph construction and routing logic.
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from nodes import (
    ask_agent,
    bootstrap_memory,
    list_history,
    show_results,
    take_prompt,
)
from state import MemoryChatState


def prompt_router(state: MemoryChatState) -> str:
    action = state.get("action", "ask")
    if action == "list":
        return "list"
    if action == "done":
        return "done"
    return "ask"


def build_graph():
    graph = StateGraph(MemoryChatState)

    graph.add_node("bootstrap_memory", bootstrap_memory)
    graph.add_node("take_prompt", take_prompt)
    graph.add_node("ask_agent", ask_agent)
    graph.add_node("show_results", show_results)
    graph.add_node("list_history", list_history)

    graph.set_entry_point("bootstrap_memory")
    graph.add_edge("bootstrap_memory", "take_prompt")

    graph.add_conditional_edges(
        "take_prompt",
        prompt_router,
        {
            "ask": "ask_agent",
            "list": "list_history",
            "done": END,
        },
    )

    graph.add_edge("ask_agent", "show_results")
    graph.add_edge("show_results", "take_prompt")
    graph.add_edge("list_history", "take_prompt")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
