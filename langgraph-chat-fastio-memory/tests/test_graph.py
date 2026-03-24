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


def test_prompt_router_supports_prompt_commands():
    graph_mod = load_module("fastio_graph_router", "graph.py")

    assert graph_mod.prompt_router({"action": "ask"}) == "ask"
    assert graph_mod.prompt_router({"action": "list"}) == "list"
    assert graph_mod.prompt_router({"action": "done"}) == "done"
    assert graph_mod.prompt_router({"action": "anything-else"}) == "ask"
