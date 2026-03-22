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


def test_loader_reads_only_supported_files_and_skips_hidden_dirs(tmp_path):
    loader_mod = load_module("qna_loader", "nodes/loader.py")

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("hello\nworld\n", encoding="utf-8")
    (docs / "notes.txt").write_text("plain text", encoding="utf-8")
    (docs / "image.png").write_text("not used", encoding="utf-8")

    hidden = docs / ".hidden"
    hidden.mkdir()
    (hidden / "secret.md").write_text("ignore me", encoding="utf-8")

    venv_dir = docs / "venv"
    venv_dir.mkdir()
    (venv_dir / "also_skip.md").write_text("ignore me too", encoding="utf-8")

    state = {
        "question": "q",
        "doc_dir": str(docs),
        "documents": [],
        "chunks": [],
        "relevant_chunks": [],
        "answer": "",
    }
    updated = loader_mod.loader(state)

    filenames = sorted(doc["filename"] for doc in updated["documents"])
    assert filenames == ["guide.md", "notes.txt"]
    assert updated["documents"][0]["line_count"] >= 1


def test_chunk_lines_uses_overlap_between_chunks():
    chunker_mod = load_module("qna_chunker", "nodes/chunker.py")
    chunker_mod.CHUNK_SIZE = 12
    chunker_mod.CHUNK_OVERLAP = 6

    lines = ["line1\n", "line2\n", "line3\n", "line4\n"]
    chunks = chunker_mod._chunk_lines(lines, "file.md", "/tmp/file.md")

    assert len(chunks) == 3
    assert [c["start_line"] for c in chunks] == [1, 2, 3]
    assert [c["end_line"] for c in chunks] == [2, 3, 4]
    assert "line2" in chunks[1]["text"]


def test_keyword_retrieve_prefers_more_overlap_and_respects_top_k():
    retriever_mod = load_module("qna_retriever", "nodes/retriever.py")
    retriever_mod.TOP_K = 2

    chunks = [
        {"text": "python list tuple dict", "chunk_id": 1},
        {"text": "python dict set", "chunk_id": 2},
        {"text": "gardening tomatoes soil", "chunk_id": 3},
    ]
    selected = retriever_mod._keyword_retrieve("python dict", chunks)

    assert len(selected) == 2
    assert selected[0]["chunk_id"] == 1
    assert selected[1]["chunk_id"] == 2


def test_extract_keywords_filters_common_stop_words():
    retriever_mod = load_module("qna_retriever_keywords", "nodes/retriever.py")

    keywords = retriever_mod._extract_keywords("What is the best way to use a deque in Python?")

    assert "what" not in keywords
    assert "is" not in keywords
    assert "python" in keywords
    assert "deque" in keywords
