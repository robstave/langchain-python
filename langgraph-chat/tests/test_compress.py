import importlib.util
import sys
import types
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_module(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, PROJECT_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def install_langchain_stubs(monkeypatch):
    fake_openai = types.ModuleType("langchain_openai")

    class FakeChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, *_args, **_kwargs):
            return types.SimpleNamespace(content="stub")

    fake_openai.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_openai)

    messages_mod = types.ModuleType("langchain_core.messages")

    class _Message:
        def __init__(self, content):
            self.content = content

    class HumanMessage(_Message):
        pass

    class SystemMessage(_Message):
        pass

    messages_mod.HumanMessage = HumanMessage
    messages_mod.SystemMessage = SystemMessage

    core_mod = types.ModuleType("langchain_core")
    core_mod.messages = messages_mod

    monkeypatch.setitem(sys.modules, "langchain_core", core_mod)
    monkeypatch.setitem(sys.modules, "langchain_core.messages", messages_mod)


def build_state(history):
    return {
        "query": "latest question",
        "response": "latest response",
        "history": history,
        "action": "",
        "summary": "",
    }


def test_compress_reduces_old_turns_and_preserves_recent(monkeypatch):
    install_langchain_stubs(monkeypatch)
    compress_mod = load_module("chat_compress_main", "nodes/compress.py")

    class FakeLLM:
        def invoke(self, _messages):
            return types.SimpleNamespace(content="compressed summary")

    monkeypatch.setattr(compress_mod, "_get_llm", lambda: FakeLLM())

    history = [
        {"query": "q1", "response": "a1"},
        {"query": "q2", "response": "a2"},
        {"query": "q3", "response": "a3"},
        {"query": "q4", "response": "a4"},
        {"query": "q5", "response": "a5"},
    ]
    updated = compress_mod.compress(build_state(history))

    assert len(updated["history"]) == 3
    compressed, recent_1, recent_2 = updated["history"]
    assert compressed["compressed"] is True
    assert compressed["compressed_count"] == 3
    assert compressed["query"] == "q1"
    assert compressed["response"] == "compressed summary"
    assert recent_1["query"] == "q4"
    assert recent_2["query"] == "q5"


def test_compress_returns_original_state_when_not_enough_history(monkeypatch):
    install_langchain_stubs(monkeypatch)
    compress_mod = load_module("chat_compress_short", "nodes/compress.py")

    class FakeLLM:
        def invoke(self, _messages):
            raise AssertionError("LLM should not be called for short history")

    monkeypatch.setattr(compress_mod, "_get_llm", lambda: FakeLLM())

    history = [
        {"query": "q1", "response": "a1"},
        {"query": "q2", "response": "a2"},
        {"query": "q3", "response": "a3"},
        {"query": "q4", "response": "a4"},
    ]
    state = build_state(history)
    updated = compress_mod.compress(state)

    assert updated is state
