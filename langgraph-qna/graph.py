"""
Graph construction for the document Q&A pipeline.
"""
from langgraph.graph import StateGraph, END

from state import QnAState
from nodes import loader, chunker, retriever, answerer


def build_graph() -> StateGraph:
    """Constructs the Q&A pipeline graph."""
    graph = StateGraph(QnAState)

    # Add nodes
    graph.add_node("loader",    loader)
    graph.add_node("chunker",   chunker)
    graph.add_node("retriever", retriever)
    graph.add_node("answerer",  answerer)

    # Entry point
    graph.set_entry_point("loader")

    # Linear flow
    graph.add_edge("loader",    "chunker")
    graph.add_edge("chunker",   "retriever")
    graph.add_edge("retriever", "answerer")
    graph.add_edge("answerer",  END)

    return graph.compile()


def build_question_graph() -> StateGraph:
    """
    Builds a graph for follow-up questions (skips loader/chunker).
    Reuses existing chunks from state.
    """
    graph = StateGraph(QnAState)

    graph.add_node("retriever", retriever)
    graph.add_node("answerer",  answerer)

    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "answerer")
    graph.add_edge("answerer",  END)

    return graph.compile()
