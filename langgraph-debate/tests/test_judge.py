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


def install_langchain_openai_stub(monkeypatch):
    fake_openai = types.ModuleType("langchain_openai")

    class FakeChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, *_args, **_kwargs):
            return types.SimpleNamespace(content="")

    fake_openai.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_openai)


def test_parse_scores_with_structured_lines(monkeypatch):
    install_langchain_openai_stub(monkeypatch)
    judge_mod = load_module("debate_judge_parse", "nodes/judge.py")

    text = "PRO_SCORE: 8\nCON_SCORE: 6\nCOMMENTARY: Pro had stronger evidence."
    pro, con, commentary = judge_mod._parse_scores(text)

    assert pro == 8
    assert con == 6
    assert commentary == "Pro had stronger evidence."


def test_parse_scores_defaults_when_fields_missing(monkeypatch):
    install_langchain_openai_stub(monkeypatch)
    judge_mod = load_module("debate_judge_parse_default", "nodes/judge.py")

    text = "Judge remarks without explicit score lines."
    pro, con, commentary = judge_mod._parse_scores(text)

    assert pro == 5
    assert con == 5
    assert commentary == "Judge remarks without explicit score lines."


def test_judge_adds_round_and_generates_final_verdict(monkeypatch):
    install_langchain_openai_stub(monkeypatch)
    judge_mod = load_module("debate_judge_final", "nodes/judge.py")

    class FakeLLM:
        def __init__(self):
            self.calls = 0

        def invoke(self, _messages):
            self.calls += 1
            if self.calls == 1:
                return types.SimpleNamespace(
                    content="PRO_SCORE: 7\nCON_SCORE: 9\nCOMMENTARY: Con rebutted directly."
                )
            return types.SimpleNamespace(content="WINNER: Con\nREASON: Better rebuttals overall.")

    monkeypatch.setattr(judge_mod, "_get_llm", lambda: FakeLLM())

    state = {
        "topic": "Topic",
        "proposition": "The proposition",
        "rounds": [],
        "current_round": 1,
        "max_rounds": 1,
        "pro_argument": "Pro argument text",
        "con_argument": "Con argument text",
        "judgment": "",
        "final_verdict": "",
        "_done": False,
    }

    updated = judge_mod.judge(state)

    assert updated["_done"] is True
    assert updated["current_round"] == 2
    assert len(updated["rounds"]) == 1
    assert updated["rounds"][0]["score_pro"] == 7
    assert updated["rounds"][0]["score_con"] == 9
    assert "WINNER: Con" in updated["final_verdict"]
