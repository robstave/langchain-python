"""
MCP runtime helpers for Fast.io-backed long-term memory.
"""
import ast
import os
import re
import base64
import json
from collections.abc import Mapping, Sequence
from typing import Any

from openai import BadRequestError
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from state import (
    FASTIO_MCP_TRANSPORT,
    FASTIO_MCP_URL,
    MEMORY_FILE_NAME,
    MEMORY_WORKSPACE_NAME,
    MODEL_NAME,
)

_client: MultiServerMCPClient | None = None
_agent = None
_dynamic_excluded_tools: set[str] = set()
_memory_file_id: str | None = None


def _excluded_tool_names() -> set[str]:
    raw = os.getenv("FASTIO_EXCLUDE_TOOLS", "org")
    return {name.strip() for name in raw.split(",") if name.strip()}


def _effective_excluded_tool_names() -> set[str]:
    return _excluded_tool_names() | _dynamic_excluded_tools


def _contains_unsupported_regex_pattern(schema: Any) -> bool:
    """
    Detect schema fragments likely rejected by OpenAI function schema validation.

    Current Fast.io MCP tool schemas may include patterns like:
      ^[^\\p{C}]*$
    which can trigger 400 invalid_function_parameters errors.
    """
    if isinstance(schema, Mapping):
        for key, value in schema.items():
            if key == "pattern" and isinstance(value, str) and "\\p{" in value:
                return True
            if _contains_unsupported_regex_pattern(value):
                return True
        return False

    if isinstance(schema, Sequence) and not isinstance(schema, (str, bytes)):
        return any(_contains_unsupported_regex_pattern(item) for item in schema)

    return False


def _tool_has_unsupported_schema(tool: Any) -> bool:
    schemas: list[Any] = []

    # Simple dict schema (works for tools that expose args directly)
    args_schema_dict = getattr(tool, "args", None)
    if isinstance(args_schema_dict, dict):
        schemas.append(args_schema_dict)

    # Try the modern tool_call_schema first.
    tool_call_schema = getattr(tool, "tool_call_schema", None)
    if tool_call_schema is not None and hasattr(tool_call_schema, "model_json_schema"):
        schemas.append(tool_call_schema.model_json_schema())

    args_schema = getattr(tool, "args_schema", None)
    if args_schema is not None and hasattr(args_schema, "model_json_schema"):
        schemas.append(args_schema.model_json_schema())

    if not schemas:
        return False
    return any(_contains_unsupported_regex_pattern(schema) for schema in schemas)


def _filter_tools_for_openai(tools: list[Any]) -> list[Any]:
    excluded_names = _effective_excluded_tool_names()
    kept = []
    skipped = []

    for tool in tools:
        name = getattr(tool, "name", "<unknown>")
        if name in excluded_names:
            skipped.append((name, "excluded via FASTIO_EXCLUDE_TOOLS"))
            continue
        if _tool_has_unsupported_schema(tool):
            skipped.append((name, "unsupported regex pattern in tool schema"))
            continue
        kept.append(tool)

    if skipped:
        print("\n[Memory] Skipping MCP tools not safe for OpenAI tool schemas:")
        for name, reason in skipped:
            print(f"  - {name}: {reason}")

    return kept


def _extract_invalid_tool_name_from_error(exc: BadRequestError) -> str | None:
    message = str(exc)
    match = re.search(r"Invalid schema for function '([^']+)'", message)
    if match:
        return match.group(1)
    return None


def _reset_agent() -> None:
    global _agent
    _agent = None


def _build_connection_config() -> dict[str, dict[str, Any]]:
    api_key = os.getenv("FASTIO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing FASTIO_API_KEY. Add it to your .env file.")

    return {
        "fastio": {
            "transport": FASTIO_MCP_TRANSPORT,
            "url": FASTIO_MCP_URL,
            "headers": {"Authorization": f"Bearer {api_key}"},
        }
    }


def _text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif hasattr(item, "text"):  # Pydantic TextContent from MCP
                parts.append(str(item.text))
            elif hasattr(item, "content"):
                parts.append(str(item.content))
        return "\n".join(p for p in parts if p).strip()
    if hasattr(content, "text"):
        return str(content.text)
    if hasattr(content, "content"):
        return str(content.content)
    return str(content)


def _extract_last_assistant_text(result: Any) -> str:
    if isinstance(result, dict) and isinstance(result.get("messages"), list):
        for message in reversed(result["messages"]):
            role = None
            content = None

            if isinstance(message, dict):
                role = message.get("role") or message.get("type")
                content = message.get("content")
            else:
                role = getattr(message, "type", None) or getattr(message, "role", None)
                content = getattr(message, "content", None)

            if role in {"assistant", "ai", "AIMessage"}:
                return _text_from_content(content)

        if result["messages"]:
            last = result["messages"][-1]
            if isinstance(last, dict):
                return _text_from_content(last.get("content", ""))
            return _text_from_content(getattr(last, "content", ""))

    return _text_from_content(result)


def _parse_structured_text(text: str) -> Any | None:
    """Parse JSON-like payloads returned by MCP tools."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError, TypeError):
        return None


def _extract_storage_items(list_payload: Any) -> list[dict[str, Any]]:
    """Extract node items from the storage list response across known shapes."""
    if isinstance(list_payload, dict):
        nodes = list_payload.get("nodes")
        if isinstance(nodes, dict) and isinstance(nodes.get("items"), list):
            return [item for item in nodes["items"] if isinstance(item, dict)]

        items = list_payload.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]

        if isinstance(nodes, list):
            extracted: list[dict[str, Any]] = []
            for node in nodes:
                if isinstance(node, dict):
                    node_items = node.get("items")
                    if isinstance(node_items, list):
                        extracted.extend(item for item in node_items if isinstance(item, dict))
            if extracted:
                return extracted

    if isinstance(list_payload, list):
        return [item for item in list_payload if isinstance(item, dict)]

    return []


def _canonical_node_id(node_id: str | None) -> str:
    """Normalize ID formats so dashed and non-dashed forms compare equal."""
    if not node_id:
        return ""
    return re.sub(r"[^a-z0-9]", "", node_id.lower())


def _memory_system_prompt() -> str:
    file_hint = (
        f"  Memory file node_id (EXACT value for read-content/delete): '{_memory_file_id}'\n"
        if _memory_file_id
        else f"  Memory file name: '{MEMORY_FILE_NAME}' (list root first to find its node_id)\n"
    )
    return (
        "You are a helpful assistant with Fast.io MCP tools.\n\n"
        "Storage tool parameters (ALWAYS use these exact values):\n"
        f"  context_type: 'workspace'\n"
        f"  context_id: '{MEMORY_WORKSPACE_NAME}'\n"
        f"  node_id: 'root' to list workspace root\n"
        + file_hint +
        "\nValid storage actions: list, details, read-content, add-file, delete, rename, copy, move, search, create-folder\n"
        "NOTE: There is NO write-content or update-content action.\n"
        "To UPDATE the memory file content, you MUST:\n"
        "  1. read-content with the memory file node_id to get current content\n"
        "  2. delete with node_id=<memory file node_id> to remove the old file\n"
        f"  3. add-file with parent_node_id='root', name='{MEMORY_FILE_NAME}', text_content=<full updated text>\n"
        "\nRules:\n"
        "1) Always pass context_type='workspace' "
        f"and context_id='{MEMORY_WORKSPACE_NAME}' on every storage call.\n"
        "2) Always read long-term memory before answering preference/personal-context questions.\n"
        "3) When saving a fact, read first, then delete the old file, then add-file with all content.\n"
        "4) Never claim memory was saved unless the add-file call succeeded.\n"
        "5) Keep normal answers concise and practical."
    )


async def _get_agent():
    global _client, _agent
    if _agent is not None:
        return _agent

    raw_tools = await _get_raw_tools()
    tools = _filter_tools_for_openai(raw_tools)
    if not tools:
        raise RuntimeError(
            "No compatible Fast.io MCP tools available after filtering. "
            "Try adjusting FASTIO_EXCLUDE_TOOLS."
        )

    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    _agent = create_react_agent(model, tools)
    return _agent


async def _ainvoke_with_schema_fallback(messages: list[dict[str, str]]) -> Any:
    """
    Invoke the agent and automatically recover from tool-schema incompatibilities.

    If OpenAI rejects one tool's schema (e.g. unsupported regex syntax), we parse the
    offending tool name from the error, exclude it, rebuild the agent, and retry.
    """
    for _ in range(6):
        agent = await _get_agent()
        try:
            return await agent.ainvoke({"messages": messages})
        except BadRequestError as exc:
            tool_name = _extract_invalid_tool_name_from_error(exc)
            if not tool_name:
                raise
            if tool_name in _dynamic_excluded_tools:
                raise

            _dynamic_excluded_tools.add(tool_name)
            print(
                f"\n[Memory] Excluding MCP tool '{tool_name}' due to invalid OpenAI schema; retrying..."
            )
            _reset_agent()

    raise RuntimeError("Unable to invoke agent after excluding incompatible MCP tools.")


def _prepare_user_prompt(user_query: str) -> str:
    text = user_query.strip()
    lower = text.lower()

    if lower.startswith("/remember "):
        payload = text[len("/remember ") :].strip()
        return (
            "Store this in long-term memory as a durable user fact or preference, then confirm:\n"
            f"{payload}"
        )
    if lower in {"/recall", "/memory"}:
        return "Read the long-term memory file and summarize what you currently remember."
    if lower.startswith("/forget "):
        payload = text[len("/forget ") :].strip()
        return (
            "Remove or mark this item as forgotten in long-term memory, then confirm what changed:\n"
            f"{payload}"
        )
    return text


async def _get_raw_tools() -> list[Any]:
    """Return raw MCP tools (unfiltered), initializing the client if needed."""
    global _client
    if _client is None:
        _client = MultiServerMCPClient(_build_connection_config())
    return await _client.get_tools()


async def bootstrap_memory_session() -> str:
    """
    Bootstrap long-term memory by calling the storage tool directly.
    This avoids relying on the LLM to construct correct tool parameters.
    """
    global _memory_file_id
    try:
        raw_tools = await _get_raw_tools()
    except Exception as e:
        return f"Memory bootstrap failed (MCP connect): {e}"

    storage = next((t for t in raw_tools if t.name == "storage"), None)
    if storage is None:
        return "No storage tool available — memory disabled."

    ws_id = MEMORY_WORKSPACE_NAME
    base_params = {"context_type": "workspace", "context_id": ws_id}

    # 1. List workspace root to check if memory file exists
    try:
        result = await storage.ainvoke({**base_params, "action": "list", "node_id": "root"})
        result_text = _text_from_content(result)
    except Exception as e:
        return f"Memory bootstrap failed (list): {e}"

    # 2. Check if the memory file already exists
    print(f"[Debug] list result_text (first 500): {result_text[:500]!r}")
    file_id = None
    data = _parse_structured_text(result_text)
    if data is not None:
        items = _extract_storage_items(data)
        print(f"[Debug] nodes.items count: {len(items)}")
        for item in items:
            print(f"[Debug]   item name={item.get('name')!r}  id={item.get('id')!r}")
            if item.get("name") == MEMORY_FILE_NAME:
                file_id = item.get("id")
                print(f"[Debug] Found memory file '{MEMORY_FILE_NAME}' -> id={file_id!r}")
                break
        if file_id is None:
            print(f"[Debug] Memory file '{MEMORY_FILE_NAME}' NOT found in listing")
    else:
        print("[Debug] Failed to parse list result")

    if file_id:
        _memory_file_id = file_id

    # 3. If file doesn't exist, create it via the upload MCP tool
    if file_id is None:
        upload = next((t for t in raw_tools if t.name == "upload"), None)
        if upload is None:
            return "Memory bootstrap failed: no upload tool."
        initial_content = "# Long-term Memory\n\n- (no items yet)\n"
        try:
            create_result = await upload.ainvoke({
                "action": "text-file",
                "profile_type": "workspace",
                "profile_id": ws_id,
                "filename": MEMORY_FILE_NAME,
                "content": initial_content,
                "parent_node_id": "root",
            })
            create_text = _text_from_content(create_result)
            created = _parse_structured_text(create_text)
            if isinstance(created, Mapping):
                file_id = created.get("new_file_id") or created.get("id")
                if file_id:
                    _memory_file_id = file_id
            return f"Created new memory file '{MEMORY_FILE_NAME}'."
        except Exception as e:
            return f"Memory bootstrap failed (create): {e}"

    # 4. Read the existing file content
    try:
        read_result = await storage.ainvoke({
            **base_params,
            "action": "read-content",
            "node_id": file_id,
        })
        content = _text_from_content(read_result)
        print(f"[Debug] read-content raw (first 500): {content[:500]!r}")
        # read-content may return JSON metadata with base64 content
        try:
            meta = json.loads(content)
            print(f"[Debug] read-content meta keys: {list(meta.keys()) if isinstance(meta, dict) else type(meta)}")
            if isinstance(meta, dict):
                size = meta.get("size", -1)
                content_type = meta.get("content_type", "<missing>")
                raw = meta.get("content", "")
                print(f"[Debug] size={size!r}  content_type={content_type!r}  raw[:100]={raw[:100]!r}")
                if size == 0 and not raw:
                    return "Memory file exists but is empty."
                # Decode base64 content if present
                if raw and content_type == "base64":
                    content = base64.b64decode(raw).decode("utf-8", errors="replace")
                elif raw:
                    content = raw
                # (else: size>0 but no raw — fall through with whatever content is)
        except (json.JSONDecodeError, TypeError):
            pass  # content is plain text already
        print(f"[Debug] final content (first 300): {content[:300]!r}")
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        if lines:
            return f"Memory loaded ({len(lines)} items): " + "; ".join(lines[:5])
        return "Memory file exists but is empty."
    except Exception as e:
        return f"Memory file exists (id={file_id}) but read failed: {e}"


async def _direct_read_memory() -> str:
    """Read memory file content directly via MCP (no LLM)."""
    import json
    if not _memory_file_id:
        return ""
    try:
        raw_tools = await _get_raw_tools()
    except Exception:
        return ""
    storage = next((t for t in raw_tools if t.name == "storage"), None)
    if storage is None:
        return ""
    base_params = {"context_type": "workspace", "context_id": MEMORY_WORKSPACE_NAME}
    try:
        read_result = await storage.ainvoke({**base_params, "action": "read-content", "node_id": _memory_file_id})
        content = _text_from_content(read_result)
        try:
            meta = json.loads(content)
            if isinstance(meta, dict):
                raw = meta.get("content", "")
                if raw and meta.get("content_type") == "base64":
                    content = base64.b64decode(raw).decode("utf-8", errors="replace")
                elif raw:
                    content = raw
        except (json.JSONDecodeError, TypeError):
            pass
        return content
    except Exception as e:
        return f"(read failed: {e})"


async def _direct_write_memory(new_content: str) -> str:
    """
    Upload new memory file content via the MCP upload tool (text-file action),
    then delete the old file only after the upload succeeds.
    """
    global _memory_file_id
    old_file_id = _memory_file_id
    ws_id = MEMORY_WORKSPACE_NAME

    try:
        raw_tools = await _get_raw_tools()
    except Exception as e:
        return f"Memory write failed (MCP connect): {e}"

    upload = next((t for t in raw_tools if t.name == "upload"), None)
    if upload is None:
        return "Memory write failed: no upload tool."

    new_id: str | None = None
    try:
        result = await upload.ainvoke({
            "action": "text-file",
            "profile_type": "workspace",
            "profile_id": ws_id,
            "filename": MEMORY_FILE_NAME,
            "content": new_content,
            "parent_node_id": "root",
        })
        result_text = _text_from_content(result)
        data = _parse_structured_text(result_text)
        if isinstance(data, Mapping):
            new_id = data.get("new_file_id") or data.get("id")
    except Exception as e:
        return f"Memory write failed (upload): {e}"

    if not new_id:
        return f"Memory write failed: upload returned no file ID"

    print(f"[write_memory] upload OK  old_id={old_file_id!r}  new_id={new_id!r}")
    _memory_file_id = new_id

    old_norm = _canonical_node_id(old_file_id)
    new_norm = _canonical_node_id(new_id)

    # Verify new file appears in workspace listing before deleting old file
    new_file_confirmed = False
    storage = next((t for t in raw_tools if t.name == "storage"), None)
    if storage:
        try:
            list_result = await storage.ainvoke({
                "context_type": "workspace",
                "context_id": ws_id,
                "action": "list",
                "node_id": "root",
            })
            list_text = _text_from_content(list_result)
            list_data = _parse_structured_text(list_text)
            if list_data is not None:
                items = _extract_storage_items(list_data)
                ids = {item.get("id") for item in items if isinstance(item, dict)}
                canonical_ids = {_canonical_node_id(str(file_id)) for file_id in ids if file_id}
                new_file_confirmed = bool(new_id in ids or (new_norm and new_norm in canonical_ids))
                print(
                    "[write_memory] listing ids="
                    f"{ids}  canonical_ids={canonical_ids}  new_confirmed={new_file_confirmed}"
                )
        except Exception as le:
            print(f"[write_memory] listing failed: {le}")

    # Fallback: listing shape/consistency can lag; confirm by directly querying new file id.
    if storage and not new_file_confirmed:
        try:
            await storage.ainvoke({
                "context_type": "workspace",
                "context_id": ws_id,
                "action": "details",
                "node_id": new_id,
            })
            new_file_confirmed = True
            print("[write_memory] details lookup confirmed new file")
        except Exception as ce:
            print(f"[write_memory] details lookup failed: {ce}")

    ids_are_distinct = bool(old_norm and new_norm and old_norm != new_norm)

    # Only delete old file when new one is confirmed present and it's different
    if new_file_confirmed and old_file_id and ids_are_distinct:
        try:
            await storage.ainvoke({
                "context_type": "workspace",
                "context_id": ws_id,
                "action": "delete",
                "node_id": old_file_id,
            })
            print(f"[write_memory] deleted old file {old_file_id!r}")
        except Exception as de:
            print(f"[write_memory] delete failed (non-fatal): {de}")
    elif new_file_confirmed and old_file_id and not ids_are_distinct:
        print("[write_memory] old/new ids refer to same file; skipping delete")
    elif not new_file_confirmed:
        print(f"[write_memory] WARNING: new file {new_id!r} not found in listing — skipping delete of old file")

    return "Memory saved."


async def _direct_remember(fact: str) -> str:
    """Append a fact to memory and save."""
    current = await _direct_read_memory()
    if not current.strip():
        current = "# Long-term Memory\n\n"
    # Append new fact as a bullet under a Notes section
    if "## Notes" not in current:
        current = current.rstrip() + "\n\n## Notes\n"
    current = current.rstrip() + f"\n- {fact}\n"
    result = await _direct_write_memory(current)
    if result == "Memory saved.":
        return f"Remembered: {fact}"
    return result


async def _direct_forget(item: str) -> str:
    """Remove lines matching item from memory and save."""
    current = await _direct_read_memory()
    if not current.strip():
        return "Memory is already empty."
    lines = current.splitlines(keepends=True)
    filtered = [l for l in lines if item.lower() not in l.lower()]
    if len(filtered) == len(lines):
        return f"No memory item matching '{item}' found."
    result = await _direct_write_memory("".join(filtered))
    if result == "Memory saved.":
        return f"Forgot: {item}"
    return result


async def ask_with_memory(user_query: str, history: list[dict]) -> str:
    text = user_query.strip()
    lower = text.lower()

    # Handle memory-write commands directly in Python to avoid MCP upload_id issues
    if lower.startswith("/remember "):
        payload = text[len("/remember "):].strip()
        return await _direct_remember(payload)
    if lower.startswith("/forget "):
        payload = text[len("/forget "):].strip()
        return await _direct_forget(payload)
    if lower in {"/recall", "/memory"}:
        content = await _direct_read_memory()
        return f"Current memory:\n\n{content}" if content else "Memory is empty."

    messages = [{"role": "system", "content": _memory_system_prompt()}]
    for turn in history:
        # Skip memory-command turns — they're handled outside the LLM and
        # confuse the agent into trying storage writes it can't do correctly.
        q = turn.get("query", "").strip().lower()
        if q.startswith("/remember ") or q.startswith("/forget ") or q in {"/recall", "/memory"}:
            continue
        messages.append({"role": "user", "content": turn["query"]})
        messages.append({"role": "assistant", "content": turn["response"]})
    messages.append({"role": "user", "content": text})

    result = await _ainvoke_with_schema_fallback(messages)
    return _extract_last_assistant_text(result)
