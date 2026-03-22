"""
Graph construction and routing logic for the chat agent.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import ChatState
from nodes import take_prompt, ask_llm, show_results, choose_action, summarize, list_history, compress


def action_router(state: ChatState) -> str:
    """Conditional edge: routes based on user's chosen action."""
    action = state.get("action", "done")
    if action == "refine":
        return "refine"
    elif action == "summarize":
        return "summarize"
    elif action == "list":
        return "list"
    elif action == "compress":
        return "compress"
    return "done"


def build_graph():
    """Constructs the chat agent graph with in-memory checkpointing."""
    graph = StateGraph(ChatState)

    # Add nodes
    graph.add_node("take_prompt",   take_prompt)
    graph.add_node("ask_llm",       ask_llm)
    graph.add_node("show_results",  show_results)
    graph.add_node("choose_action", choose_action)
    graph.add_node("summarize",     summarize)
    graph.add_node("list_history",  list_history)
    graph.add_node("compress",      compress)

    # Entry point
    graph.set_entry_point("take_prompt")

    # Linear edges: A → B → C → D
    graph.add_edge("take_prompt",   "ask_llm")
    graph.add_edge("ask_llm",       "show_results")
    graph.add_edge("show_results",  "choose_action")

    # Conditional edge from D (choose_action)
    graph.add_conditional_edges(
        "choose_action",
        action_router,
        {
            "done":      END,
            "refine":    "ask_llm",
            "summarize": "summarize",
            "list":      "list_history",
            "compress":  "compress",
        },
    )

    # Both list and summarize loop back to choose_action
    graph.add_edge("list_history", "choose_action")
    graph.add_edge("summarize", "choose_action")
    graph.add_edge("compress", "choose_action")

    # Compile with in-memory checkpointing
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
