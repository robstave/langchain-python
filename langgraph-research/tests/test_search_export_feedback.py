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
        "query": "Where are good wildflower trails?",
        "search_queries": ["wildflowers california"],
        "results": [],
        "seen_urls": set(),
        "iteration": 0,
        "final_answer": "Sample answer",
        "_enough": False,
        "feedback_hint": "",
    }


def test_search_deduplicates_and_increments_iteration(monkeypatch):
    search_mod = load_module("research_search", "nodes/search.py")

    raw_results = [
        {"title": "A", "url": "https://a.test", "content": "x"},
        {"title": "B", "url": "https://b.test", "content": "y"},
        {"title": "A dup", "url": "https://a.test", "content": "z"},
    ]
    monkeypatch.setattr(search_mod, "search_web", lambda _queries: raw_results)

    state = base_state()
    updated = search_mod.search(state)

    assert updated["iteration"] == 1
    assert len(updated["results"]) == 2
    assert updated["seen_urls"] == {"https://a.test", "https://b.test"}


def test_export_markdown_writes_file_and_dedups_sources(tmp_path, monkeypatch):
    export_mod = load_module("research_export", "nodes/export.py")
    export_mod.ANSWERS_DIR = str(tmp_path / "answers")

    state = base_state()
    state["results"] = [
        {"title": "Doc A", "url": "https://a.test", "content": "x"},
        {"title": "Doc B", "url": "https://b.test", "content": "y"},
        {"title": "Doc A duplicate", "url": "https://a.test", "content": "z"},
    ]
    state["iteration"] = 2

    export_mod.export_markdown(state)

    files = list((tmp_path / "answers").glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "# Where are good wildflower trails?" in content
    assert content.count("https://a.test") == 1
    assert content.count("https://b.test") == 1


def test_feedback_done_sets_enough_true(monkeypatch):
    feedback_mod = load_module("research_feedback_done", "nodes/feedback.py")
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")

    updated = feedback_mod.feedback(base_state())
    assert updated["_enough"] is True


def test_feedback_keep_going_adds_hint(monkeypatch):
    feedback_mod = load_module("research_feedback_hint", "nodes/feedback.py")
    inputs = iter(["2", "Focus on peak bloom dates"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    updated = feedback_mod.feedback(base_state())
    assert updated["_enough"] is False
    assert updated["feedback_hint"] == "Focus on peak bloom dates"


def test_feedback_refine_adds_query(monkeypatch):
    feedback_mod = load_module("research_feedback_refine", "nodes/feedback.py")
    inputs = iter(["3", "wildflower bloom by month california"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    updated = feedback_mod.feedback(base_state())
    assert updated["_enough"] is False
    assert updated["search_queries"][-1] == "wildflower bloom by month california"
