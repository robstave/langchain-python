"""
Bootstrap node: verifies Fast.io memory on session start.
"""
from agent_runtime import bootstrap_memory_session
from state import MemoryChatState

COLOR_BOOTSTRAP = "\033[96m"
COLOR_RESET = "\033[0m"


async def bootstrap_memory(state: MemoryChatState) -> MemoryChatState:
    summary = await bootstrap_memory_session()
    print(f"\n{COLOR_BOOTSTRAP}{'═' * 60}")
    print("[Memory] Session memory bootstrap complete")
    print(f"{'═' * 60}")
    print(summary)
    print(f"{'═' * 60}{COLOR_RESET}")
    return {**state, "memory_status": summary}
