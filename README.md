# Chain Exercises

A collection of Python projects for learning LangChain, LangGraph, and related frameworks.

This repository contains hands-on exercises and examples to understand how these tools work in practice.

## Projects

| Project | Description | Requirements |
|---------|-------------|-------------|
| [langgraph-research](langgraph-research/) | Iterative web research agent — plans queries, searches with Tavily, evaluates results, synthesizes an answer. Includes search dedup, markdown export, and user feedback loop. | OpenAI API key, Tavily API key |
| [langgraph-qna](langgraph-qna/) | Document Q&A pipeline — loads local markdown/text files, chunks them, retrieves relevant passages by keyword, and answers questions with cited sources. | OpenAI API key |
| [langgraph-debate](langgraph-debate/) | Multi-agent debate — Pro and Con LLM agents argue a proposition across multiple rounds while a Judge scores and declares a winner. | OpenAI API key |
