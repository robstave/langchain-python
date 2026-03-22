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
        "summary": "",
    }


def test_choose_action_refine_with_user_text(monkeypatch):
    choose_action_mod = load_module("chat_choose_action_refine", "nodes/choose_action.py")
    inputs = iter(["2", "Tell me more about checkpoints"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    updated = choose_action_mod.choose_action(base_state())

    assert updated["action"] == "refine"
    assert updated["query"] == "Tell me more about checkpoints"


def test_choose_action_refine_with_empty_text_uses_default(monkeypatch):
    choose_action_mod = load_module("chat_choose_action_default", "nodes/choose_action.py")
    inputs = iter(["2", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    updated = choose_action_mod.choose_action(base_state())

    assert updated["action"] == "refine"
    assert updated["query"] == "Can you elaborate on that?"


def test_choose_action_compress(monkeypatch):
    choose_action_mod = load_module("chat_choose_action_compress", "nodes/choose_action.py")
    monkeypatch.setattr("builtins.input", lambda _: "5")

    updated = choose_action_mod.choose_action(base_state())

    assert updated["action"] == "compress"
    assert updated["query"] == "original"


def test_choose_action_falls_back_to_done(monkeypatch):
    choose_action_mod = load_module("chat_choose_action_done", "nodes/choose_action.py")
    monkeypatch.setattr("builtins.input", lambda _: "9")

    updated = choose_action_mod.choose_action(base_state())

    assert updated["action"] == "done"
