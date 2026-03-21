# Document Q&A Pipeline — Implementation Plan

## Overview

A LangGraph-based pipeline that loads local Markdown/text files, chunks them, and answers
user questions with citations back to the source file and line number. No external APIs
beyond OpenAI — your own files are the knowledge base.

This is designed as a **stepping stone to vector DB retrieval**: the naive version stuffs
all relevant chunks into the LLM prompt. Later, swapping in a vector store for similarity
search is a minimal code change with a big conceptual payoff.

## Why This Project

- Teaches: text splitting, document loading, chain composition, retrieval basics
- Reuses patterns from `langgraph-research`: state management, node functions, conditional routing, structured logging, colorful output
- Natural "before/after" for adding a vector DB later
- Zero external APIs besides OpenAI

## Architecture

```
User question
     │
     ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Loader  │────▶│ Chunker  │────▶│ Retriever│────▶│ Answerer │
│          │     │          │     │ (naive)  │     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                        │
                                                        ▼
                                                     Answer
                                                   + citations
```

## Project Structure

```
langgraph-qna/
├── qna.py                # Main entry point
├── state.py              # State definition and configuration
├── graph.py              # Graph construction
├── nodes/
│   ├── __init__.py
│   ├── loader.py         # Loads files from docs/
│   ├── chunker.py        # Splits documents into chunks
│   ├── retriever.py      # Finds relevant chunks (stuff or keyword mode)
│   └── answerer.py       # LLM generates answer with citations
├── docs/                 # Sample documents to query against
│   ├── python_data_structures.md
│   ├── http_status_codes.md
│   └── git_commands.md
├── requirements.txt
├── run.sh
├── .env                  # API keys (not committed)
└── README.md
```

## State Definition

```python
class QnAState(TypedDict):
    question: str                # user's question
    doc_dir: str                 # path to documents directory
    documents: list[dict]        # loaded docs: {path, filename, content, line_count}
    chunks: list[dict]           # chunked docs: {source, filename, chunk_id, text, start_line, end_line}
    relevant_chunks: list[dict]  # chunks selected by retriever
    answer: str                  # final answer with citations
```

## Configuration (`state.py`)

```python
MODEL_NAME = "gpt-5.4-mini"
DOC_DIR = "docs"               # default directory to load
CHUNK_SIZE = 500               # characters per chunk
CHUNK_OVERLAP = 50             # overlap between chunks
RETRIEVAL_MODE = "keyword"     # "stuff" or "keyword"
TOP_K = 5                      # chunks to retrieve in keyword mode
```

## Node Details

### 1. Loader (`nodes/loader.py`)

Recursively loads `.md` and `.txt` files from a directory.

- Walk `state["doc_dir"]` for `.md`, `.txt` files
- For each file, read content and store: `{path, filename, content, line_count}`
- Skip hidden files, `venv/`, `__pycache__/`
- Print: `[Loader] Loaded 5 files (12,340 chars total)`

### 2. Chunker (`nodes/chunker.py`)

Splits documents into overlapping chunks with line tracking.

- Split each document by paragraphs (double newline) or fixed size (~500 chars)
- Track `start_line` and `end_line` for each chunk (for citations)
- Add overlap: last portion of previous chunk prepended (configurable)
- Store: `{source, filename, chunk_id, text, start_line, end_line}`
- Print: `[Chunker] Created 24 chunks from 3 files`

### 3. Retriever (`nodes/retriever.py`)

Selects relevant chunks for the question. Two modes:

- **Stuff mode** (`RETRIEVAL_MODE = "stuff"`): Pass ALL chunks to the answerer. Works for small corpus.
- **Keyword mode** (`RETRIEVAL_MODE = "keyword"`): Extract keywords, score chunks by overlap, return top-K.
- Print: `[Retriever] Selected 5/24 chunks (keyword mode)`

This is exactly where a vector DB slots in later — same interface, smarter scoring.

### 4. Answerer (`nodes/answerer.py`)

LLM generates an answer using the selected chunks.

- System prompt: "Answer using ONLY provided context. Cite as [filename:line-line]."
- If no relevant chunks: "I couldn't find information about that in the loaded documents."
- Print: `[Answerer] Answer written.`

## Graph Flow

```
Loader → Chunker → Retriever → Answerer → END
```

Interactive question loop in `qna.py`: load docs once, ask multiple questions.

## Implementation Order

1. `state.py` — state + config
2. `docs/` — sample markdown files
3. `requirements.txt`, `run.sh`
4. `nodes/loader.py`
5. `nodes/chunker.py`
6. `nodes/retriever.py`
7. `nodes/answerer.py`
8. `nodes/__init__.py`, `graph.py`, `qna.py`
9. `README.md`

## Future: Vector DB Upgrade Path

1. Add embedder node after chunker
2. Replace retriever keyword scoring with vector similarity
3. State gets a `vector_store` field
4. Everything else stays identical
