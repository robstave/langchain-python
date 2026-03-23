#!/usr/bin/env python3
"""Debug: inspect the storage tool schema and test calling it."""
import asyncio
import json
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

WORKSPACE_ID = os.getenv("FASTIO_MEMORY_WORKSPACE", "")


async def debug():
    mcp_config = {
        "fastio": {
            "url": os.getenv("FASTIO_MCP_URL", "https://mcp.fast.io/mcp"),
            "transport": os.getenv("FASTIO_MCP_TRANSPORT", "streamable_http"),
            "headers": {"Authorization": f"Bearer {os.getenv('FASTIO_API_KEY')}"},
        }
    }

    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()

    tool_map = {t.name: t for t in tools}

    # 1. Dump storage tool schema
    if "storage" in tool_map:
        st = tool_map["storage"]
        print("=" * 70)
        print("STORAGE TOOL")
        print("=" * 70)
        print(f"Name: {st.name}")
        print(f"Description: {getattr(st, 'description', 'N/A')[:300]}")
        args_schema = getattr(st, "args_schema", None)
        if args_schema:
            try:
                schema_dict = args_schema.model_json_schema()
                print(f"Schema:\n{json.dumps(schema_dict, indent=2)}")
            except Exception:
                try:
                    print(f"Schema:\n{json.dumps(args_schema.schema(), indent=2)}")
                except Exception as e2:
                    print(f"Schema extraction failed: {e2}")
        print()

        # 2. Try calling storage list with workspace_id
        print(f"Workspace ID from .env: {WORKSPACE_ID}")
        print()

        print("Trying storage list (root)...")
        try:
            result = await st.ainvoke({"action": "list", "context_type": "workspace", "context_id": WORKSPACE_ID, "node_id": "root"})
            print("  SUCCESS:")
            _pretty_print(result)
        except Exception as e:
            print(f"  FAILED: {e}")
        print()

    # 3. Probe the upload tool
    if "upload" in tool_map:
        ut = tool_map["upload"]
        print("=" * 70)
        print("UPLOAD TOOL")
        print("=" * 70)
        print(f"Description: {getattr(ut, 'description', 'N/A')[:400]}")
        args_schema = getattr(ut, "args_schema", None)
        if args_schema:
            try:
                print(f"Schema:\n{json.dumps(args_schema.model_json_schema(), indent=2)}")
            except Exception as e:
                print(f"Schema extraction failed: {e}")
        print()

        sample_content = "# test\n- hello from debug\n"
        sample_name = "__debug_test__.md"

        attempts = [
            {"action": "text-file", "profile_type": "workspace", "profile_id": WORKSPACE_ID,
             "filename": sample_name, "content": sample_content, "parent_node_id": "root"},
            {"action": "text-file", "profile_type": "workspace", "profile_id": WORKSPACE_ID,
             "filename": sample_name, "text_content": sample_content, "parent_node_id": "root"},
            {"action": "text-file", "profile_type": "workspace", "profile_id": WORKSPACE_ID,
             "filename": sample_name, "content": sample_content, "parent_node_id": "root",
             "context_type": "workspace", "context_id": WORKSPACE_ID},
        ]

        for params in attempts:
            print(f"Trying upload: {params}")
            try:
                result = await ut.ainvoke(params)
                print("  SUCCESS:")
                _pretty_print(result)
                break
            except Exception as e:
                print(f"  FAILED: {e}")
            print()
    else:
        print("No 'upload' tool found!")
        print("Available tools:", [t.name for t in tools])



def _pretty_print(value, _depth=0) -> None:
    """Print a value as formatted JSON if possible, else pprint it."""
    import ast
    import pprint

    # Unwrap lists (MCP returns a list of content items)
    if isinstance(value, list):
        for item in value:
            _pretty_print(item, _depth + 1)
        return

    # Unwrap LangChain ToolMessage / objects with .content
    if hasattr(value, "content"):
        _pretty_print(value.content, _depth + 1)
        return

    # Unwrap MCP TextContent objects ({type: text, text: ...} or .text attr)
    if isinstance(value, dict) and value.get("type") == "text":
        value = value["text"]
    elif hasattr(value, "text") and not isinstance(value, str):
        value = value.text

    if isinstance(value, str):
        # Try JSON first
        try:
            parsed = json.loads(value)
            print(json.dumps(parsed, indent=2))
            return
        except (json.JSONDecodeError, ValueError):
            pass
        # Try Python repr (e.g. {'key': 'val'})
        try:
            parsed = ast.literal_eval(value)
            print(json.dumps(parsed, indent=2, default=str))
            return
        except Exception:
            pass
        print(value)
    elif isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2, default=str))
    else:
        pprint.pprint(value)


if __name__ == "__main__":
    asyncio.run(debug())
