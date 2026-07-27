#!/usr/bin/env python3
"""Direct Notion REST client for Robin — replaces the old `claude -p` bridge.

Robin used to reach Notion by driving the Claude Code CLI's Notion connector
(`claude -p --allowedTools mcp__claude_ai_Notion__notion-*`). That coupled Robin
to an interactive OAuth login that kept expiring. This module talks to the
Notion REST API directly using the workspace-integration token that already
lives in ~/.hermes/.env (NOTION_API_KEY), with automatic OAuth refresh via the
sibling notion_token.py on 401/403. No Claude CLI, no MCP, no login prompts.

Auth & refresh
--------------
Every request sends `Authorization: Bearer <NOTION_API_KEY>`. On a 401/403 the
client calls notion_token.refresh() ONCE per process, rewrites the rotated
token pair into ~/.hermes/.env, and retries. If refresh fails it raises so the
caller can fail safe + warn (same contract precheck.py already relies on).

Python API (import these from the skill's tick handler)
-------------------------------------------------------
  fetch_blocks(page_id)          -> list[block dict]   (all children, 1 level)
  fetch_blocks_deep(page_id)     -> list[block dict]   (recursive, nested)
  render_text(page_id)           -> str  (flattened, human/LLM-readable, with
                                          block ids + to_do checkbox states)
  append_blocks(page_id, blocks) -> list[created block dict]
  update_block(block_id, body)   -> updated block dict
  delete_block(block_id)         -> deleted block dict
  create_page(parent, props, children=None) -> created page dict
  create_database(parent_page_id, title, properties) -> created db dict
  query_data_source(data_source_id, body=None) -> query result dict
  retrieve_page(page_id)         -> page dict (properties, last_edited_time…)
  request(method, path, body=None) -> parsed JSON (generic escape hatch)

CLI (so the skill can also drive it via the terminal tool)
----------------------------------------------------------
  notion_api.py render <page_id>
        Print a flattened, readable rendering of the page's blocks: each line is
        `<block_id>  <type>  [x]/[ ] (for to_do)  <text>`. This is what the tick
        handler reads to get the "Robin needs input" Q&A verbatim + the Done
        checkbox state — the exact job the old bridge did.
  notion_api.py fetch <page_id>            # raw block children JSON (1 level)
  notion_api.py fetch-deep <page_id>       # raw block children JSON (recursive)
  notion_api.py page <page_id>             # page object JSON (props + edit time)
  notion_api.py append <page_id>           # blocks JSON array read from stdin
  notion_api.py update-block <block_id>    # block body JSON read from stdin
  notion_api.py delete-block <block_id>
  notion_api.py create-page                # {parent, properties, children?} on stdin
  notion_api.py create-database            # {parent_page_id, title, properties} on stdin
  notion_api.py query-ds <data_source_id>  # optional query body JSON on stdin
  notion_api.py call <METHOD> <PATH>       # generic; JSON body on stdin if any

All CLI subcommands print JSON to stdout (or plain text for `render`) and exit
non-zero with an {"error": …} JSON on failure.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notion_token  # sibling helper: get_token() / refresh()

API_ROOT = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionError(RuntimeError):
    pass


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def request(method, path, body=None, _refreshed=[False]):
    """Authenticated Notion REST call with one-shot auto-refresh on 401/403.

    `path` is relative to the API root (e.g. "/pages/<id>") or an absolute URL.
    Returns parsed JSON. Raises NotionError on failure.
    """
    token = notion_token.get_token()
    if not token:
        raise NotionError("NOTION_API_KEY missing from env / ~/.hermes/.env")

    url = path if path.startswith("http") else f"{API_ROOT}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None

    def _do(tok):
        req = urllib.request.Request(url, data=data, headers=_headers(tok), method=method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    try:
        return _do(token)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403) and not _refreshed[0]:
            _refreshed[0] = True
            try:
                token = notion_token.refresh()
            except Exception as rexc:  # noqa: BLE001
                raise NotionError(f"auth {exc.code} and token refresh failed: {rexc}") from exc
            try:
                return _do(token)
            except urllib.error.HTTPError as exc2:
                detail = exc2.read().decode("utf-8", "replace")[:400]
                raise NotionError(f"Notion {method} {path} HTTP {exc2.code}: {detail}") from exc2
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise NotionError(f"Notion {method} {path} HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise NotionError(f"Notion {method} {path} network error: {exc}") from exc


# ── Reads ────────────────────────────────────────────────────────────────────

def retrieve_page(page_id):
    return request("GET", f"/pages/{page_id.replace('-', '')}")


def fetch_blocks(page_id):
    """All direct child blocks of a page/block (handles pagination)."""
    blocks, cursor = [], None
    while True:
        q = f"?start_cursor={cursor}&page_size=100" if cursor else "?page_size=100"
        res = request("GET", f"/blocks/{page_id.replace('-', '')}/children{q}")
        blocks.extend(res.get("results", []))
        if res.get("has_more"):
            cursor = res.get("next_cursor")
        else:
            break
    return blocks


def fetch_blocks_deep(page_id, _depth=0):
    """Recursively fetch child blocks, attaching children under `_children`."""
    if _depth > 6:  # guard against pathological nesting
        return []
    out = []
    for b in fetch_blocks(page_id):
        if b.get("has_children"):
            b["_children"] = fetch_blocks_deep(b["id"], _depth + 1)
        out.append(b)
    return out


def _rich_text(block):
    """Extract plain text from a block's rich_text payload, whatever its type."""
    btype = block.get("type")
    payload = block.get(btype, {}) if btype else {}
    rt = payload.get("rich_text") or payload.get("caption") or []
    return "".join(seg.get("plain_text", "") for seg in rt)


def render_text(page_id):
    """Flatten a page into readable lines the tick handler can parse.

    Each line: `<block_id>\t<type>\t<checkbox>\t<text>` where <checkbox> is
    `[x]`/`[ ]` for to_do blocks (Robin's Done signal) or `-` otherwise.
    Nested blocks are indented with two spaces per level. This is the direct-API
    equivalent of the old bridge instruction "return the block text verbatim
    plus the state of the Done checkbox".
    """
    lines = []

    def walk(blocks, depth):
        for b in blocks:
            btype = b.get("type", "?")
            indent = "  " * depth
            if btype == "to_do":
                checked = b.get("to_do", {}).get("checked")
                box = "[x]" if checked else "[ ]"
            else:
                box = "-"
            text = _rich_text(b)
            lines.append(f"{b.get('id','')}\t{btype}\t{box}\t{indent}{text}")
            if b.get("_children"):
                walk(b["_children"], depth + 1)

    walk(fetch_blocks_deep(page_id), 0)
    return "\n".join(lines)


# ── Writes ───────────────────────────────────────────────────────────────────

def append_blocks(page_id, blocks):
    res = request("PATCH", f"/blocks/{page_id.replace('-', '')}/children",
                  {"children": blocks})
    return res.get("results", [])


def update_block(block_id, body):
    return request("PATCH", f"/blocks/{block_id.replace('-', '')}", body)


def delete_block(block_id):
    return request("DELETE", f"/blocks/{block_id.replace('-', '')}")


def create_page(parent, properties, children=None):
    """parent: {"page_id": …} | {"database_id": …} | {"data_source_id": …}."""
    body = {"parent": parent, "properties": properties}
    if children:
        body["children"] = children
    return request("POST", "/pages", body)


def create_database(parent_page_id, title, properties):
    body = {
        "parent": {"type": "page_id", "page_id": parent_page_id.replace("-", "")},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties,
    }
    return request("POST", "/databases", body)


def query_data_source(data_source_id, body=None):
    return request("POST", f"/databases/{data_source_id.replace('-', '')}/query",
                   body or {})


# ── CLI ────────────────────────────────────────────────────────────────────

def _stdin_json():
    raw = sys.stdin.read().strip()
    return json.loads(raw) if raw else None


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "render":
            print(render_text(rest[0]))
        elif cmd == "fetch":
            print(json.dumps(fetch_blocks(rest[0]), indent=2, ensure_ascii=False))
        elif cmd == "fetch-deep":
            print(json.dumps(fetch_blocks_deep(rest[0]), indent=2, ensure_ascii=False))
        elif cmd == "page":
            print(json.dumps(retrieve_page(rest[0]), indent=2, ensure_ascii=False))
        elif cmd == "append":
            blocks = _stdin_json()
            if not isinstance(blocks, list):
                raise NotionError("append expects a JSON array of blocks on stdin")
            print(json.dumps(append_blocks(rest[0], blocks), indent=2, ensure_ascii=False))
        elif cmd == "update-block":
            print(json.dumps(update_block(rest[0], _stdin_json()), indent=2, ensure_ascii=False))
        elif cmd == "delete-block":
            print(json.dumps(delete_block(rest[0]), indent=2, ensure_ascii=False))
        elif cmd == "create-page":
            p = _stdin_json() or {}
            print(json.dumps(create_page(p["parent"], p["properties"], p.get("children")),
                             indent=2, ensure_ascii=False))
        elif cmd == "create-database":
            p = _stdin_json() or {}
            print(json.dumps(create_database(p["parent_page_id"], p["title"], p["properties"]),
                             indent=2, ensure_ascii=False))
        elif cmd == "query-ds":
            print(json.dumps(query_data_source(rest[0], _stdin_json()), indent=2, ensure_ascii=False))
        elif cmd == "call":
            method, path = rest[0], rest[1]
            print(json.dumps(request(method.upper(), path, _stdin_json()),
                             indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"error": f"unknown command: {cmd}"}))
            return 2
    except (NotionError, KeyError, IndexError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
