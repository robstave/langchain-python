"""
Ask Agent node: calls LLM + Fast.io MCP tools with memory instructions.
"""
from agent_runtime import ask_with_memory
from state import MemoryChatState

COLOR_AGENT = "\033[93m"
COLOR_RESET = "\033[0m"


async def ask_agent(state: MemoryChatState) -> MemoryChatState:
    response = await ask_with_memory(state["query"], state["history"])

    new_history = state["history"] + [
        {"query": state["query"], "response": response},
    ]

    print(f"\n{COLOR_AGENT}[Agent]{COLOR_RESET} Response ready (turn {len(new_history)})")
    return {**state, "response": response, "history": new_history}
