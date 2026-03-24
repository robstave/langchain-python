import importlib.util
import sys
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


def base_state():
    return {
        "query": "original",
        "response": "answer",
        "history": [],
        "action": "",
        "memory_status": "ready",
    }


def test_take_prompt_routes_normal_message(monkeypatch):
    take_prompt_mod = load_module("fastio_take_prompt_normal", "nodes/take_prompt.py")
    monkeypatch.setattr("builtins.input", lambda _: "Tell me more about memory")

    updated = take_prompt_mod.take_prompt(base_state())

    assert updated["action"] == "ask"
    assert updated["query"] == "Tell me more about memory"


def test_take_prompt_routes_list_command(monkeypatch):
    take_prompt_mod = load_module("fastio_take_prompt_list", "nodes/take_prompt.py")
    monkeypatch.setattr("builtins.input", lambda _: " /LiSt ")

    updated = take_prompt_mod.take_prompt(base_state())

    assert updated["action"] == "list"
    assert updated["query"] == "/LiSt"


def test_take_prompt_routes_quit_command(monkeypatch):
    take_prompt_mod = load_module("fastio_take_prompt_quit", "nodes/take_prompt.py")
    monkeypatch.setattr("builtins.input", lambda _: "quit")

    updated = take_prompt_mod.take_prompt(base_state())

    assert updated["action"] == "done"
    assert updated["query"] == "quit"


def test_take_prompt_uses_default_for_empty_input(monkeypatch):
    take_prompt_mod = load_module("fastio_take_prompt_default", "nodes/take_prompt.py")
    monkeypatch.setattr("builtins.input", lambda _: "")

    updated = take_prompt_mod.take_prompt(base_state())

    assert updated["action"] == "ask"
    assert updated["query"] == take_prompt_mod.DEFAULT_QUESTION
