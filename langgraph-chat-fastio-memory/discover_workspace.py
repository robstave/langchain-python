#!/usr/bin/env python3
"""
Helper script to discover Fast.io workspace IDs via MCP.
Run this to get the numeric ID for your workspace.
"""
import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def list_workspaces():
    """List all Fast.io workspaces and their numeric IDs."""

    mcp_config = {
        "fastio": {
            "url": os.getenv("FASTIO_MCP_URL", "https://mcp.fast.io/mcp"),
            "transport": os.getenv("FASTIO_MCP_TRANSPORT", "streamable_http"),
            "headers": {"Authorization": f"Bearer {os.getenv('FASTIO_API_KEY')}"},
        }
    }

    print("Connecting to Fast.io MCP...")
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()

    print(f"\nFound {len(tools)} MCP tools:")
    tool_map = {}
    for t in tools:
        print(f"  - {t.name}")
        tool_map[t.name] = t

    # Try workspace tool first (action=list)
    if "workspace" in tool_map:
        print("\nTrying workspace tool (action=list)...")
        try:
            result = await tool_map["workspace"].ainvoke({"action": "list"})
            _print_result("WORKSPACES", result)
            return
        except Exception as e:
            print(f"  workspace list failed: {e}")

    # Try storage tool (action=list with no workspace — lists workspaces)
    if "storage" in tool_map:
        print("\nTrying storage tool (action=list)...")
        try:
            result = await tool_map["storage"].ainvoke({"action": "list"})
            _print_result("STORAGE LIST", result)
            return
        except Exception as e:
            print(f"  storage list failed: {e}")

    # Fallback: print all tool schemas so user can inspect manually
    print("\n" + "=" * 70)
    print("Could not auto-list workspaces. Tool schemas for manual inspection:")
    print("=" * 70)
    for t in tools:
        schema = getattr(t, "args_schema", None)
        desc = getattr(t, "description", "")
        print(f"\n  Tool: {t.name}")
        if desc:
            print(f"  Desc: {desc[:120]}")
        if schema:
            try:
                print(f"  Args: {schema.schema()}")
            except Exception:
                pass
    print("=" * 70)


def _print_result(label: str, result) -> None:
    import ast
    import json
    import pprint

    print("\n" + "=" * 70)
    print(label + ":")
    print("=" * 70)
    _print_pretty(result)
    print("=" * 70)


def _print_pretty(value) -> None:
    # Unwrap lists (MCP returns a list of content items)
    if isinstance(value, list):
        for item in value:
            _print_pretty(item)
        return
    # Unwrap LangChain ToolMessage / objects with .content
    if hasattr(value, "content"):
        _print_pretty(value.content)
        return
    # Unwrap MCP TextContent {type: text, text: ...} or .text attr
    if isinstance(value, dict) and value.get("type") == "text":
        value = value["text"]
    elif hasattr(value, "text") and not isinstance(value, str):
        value = value.text

    import json, ast, pprint
    if isinstance(value, str):
        try:
            print(json.dumps(json.loads(value), indent=2))
            return
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            print(json.dumps(ast.literal_eval(value), indent=2, default=str))
            return
        except Exception:
            pass
        print(value)
    elif isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2, default=str))
    else:
        pprint.pprint(value)
    print("\nCopy the 19-digit numeric ID for your workspace into .env:")
    print("  FASTIO_MEMORY_WORKSPACE=<numeric-id>")


if __name__ == "__main__":
    try:
        asyncio.run(list_workspaces())
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nMake sure your .env has:")
        print("  FASTIO_API_KEY=...")

