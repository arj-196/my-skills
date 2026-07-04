#!/usr/bin/env python3
"""Robin pre-check gate.

Deterministic, zero-token triage that runs at the start of every scheduled
Robin tick. Parses the Obsidian inbox file and Robin's local state cache,
then prints a JSON verdict:

  NOOP  -> nothing new, no task awaiting action. The model must stop immediately.
  WORK  -> there is something to do; payload describes exactly what.

Read-only: never mutates the vault or the state file.
"""

import json
import re
import sys
from pathlib import Path

VAULT_FILE = (
    Path.home()
    / "Library/Mobile Documents/iCloud~md~obsidian/Documents/ArjVaultICloud"
    / "A2 - TODO Apps.md"
)
STATE_FILE = Path("/Users/arjun/Mendo/playground/Robin/state.json")

# Stages that require model attention on a tick.
# - grilling / review: must check the Slack thread for replies
# - planning / implementing: work in progress to advance
# - blocked: must check the Slack thread for the user's instruction
ACTIVE_STAGES = {"ingested", "grilling", "planning", "review", "implementing", "blocked"}
TERMINAL_STAGES = {"done", "dropped"}

MARKER_RE = re.compile(r"\U0001F916\s*(R-\d+)(?:\s+([\w-]+))?")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
BULLET_RE = re.compile(r"^[-*]\s+(?:\[[ xX]\]\s+)?(\S.*)$")
PATH_ROW_RE = re.compile(r"^\|\s*path\s*\|\s*(.+?)\s*\|\s*$", re.IGNORECASE)
IDEAS_RE = re.compile(r"^(\*\*ideas\*\*|#{1,6}\s+ideas)\s*:?\s*$", re.IGNORECASE)
HR_RE = re.compile(r"^\s*(---+|\*\*\*+|___+)\s*$")


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            return {"_state_error": str(exc)}
    return {}


def parse_vault(text):
    """Return list of sections, each with path, new (unmarked) bullets, marked bullets."""
    sections = []
    current = None
    in_ideas = False
    open_task = None  # the last top-level bullet dict, for attaching detail lines

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\n")
        heading = HEADING_RE.match(line)

        if heading and len(heading.group(1)) == 2:  # new ## section
            current = {
                "section": heading.group(2).strip(),
                "path": None,
                "new_bullets": [],
                "marked_bullets": [],
            }
            sections.append(current)
            in_ideas = False
            open_task = None
            continue

        if current is None:
            continue

        if IDEAS_RE.match(line.strip()):
            in_ideas = True  # Ideas block runs to the end of the section
            open_task = None
            continue
        if in_ideas:
            continue

        path_row = PATH_ROW_RE.match(line.strip())
        if path_row:
            value = path_row.group(1).strip()
            current["path"] = value
            open_task = None
            continue

        if heading or HR_RE.match(line) or line.strip().startswith("|"):
            open_task = None
            continue

        bullet = BULLET_RE.match(line)  # top-level: no leading whitespace
        if bullet:
            body = bullet.group(1).strip()
            marker = MARKER_RE.search(body)
            entry = {
                "line": lineno,
                "text": body,
                "detail": [],
            }
            if marker:
                entry["id"] = marker.group(1)
                entry["stage"] = marker.group(2) or "ingested"
                current["marked_bullets"].append(entry)
            else:
                current["new_bullets"].append(entry)
            open_task = entry
            continue

        # Continuation: indented bullets or plain lines attach to the open task.
        stripped = line.strip()
        if stripped and stripped not in {"-", "*", "- [ ]"}:
            if open_task is not None:
                open_task["detail"].append(stripped)
        # blank lines: keep the task open (phone typing is messy)

    return sections


def main():
    out = {
        "verdict": "NOOP",
        "reasons": [],
        "new_bullets": [],
        "marked_bullets": [],
        "sections_missing_path": [],
        "active_tasks": [],
        "warnings": [],
    }

    if not VAULT_FILE.exists():
        out["verdict"] = "WORK"
        out["reasons"].append(f"vault file missing: {VAULT_FILE}")
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    state = load_state()
    if "_state_error" in state:
        out["warnings"].append(f"state.json unreadable: {state['_state_error']}")
        state = {}

    ignored = set(state.get("ignored_sections", []))
    app_paths = state.get("app_paths", {})
    tasks = state.get("tasks", {})

    sections = parse_vault(VAULT_FILE.read_text(encoding="utf-8"))

    for sec in sections:
        name = sec["section"]
        if name in ignored:
            continue
        effective_path = sec["path"] or app_paths.get(name)
        for b in sec["new_bullets"]:
            out["new_bullets"].append({**b, "section": name, "path": effective_path})
        for b in sec["marked_bullets"]:
            out["marked_bullets"].append({**b, "section": name})
            state_task = tasks.get(b.get("id"))
            if state_task is None and b.get("stage") not in TERMINAL_STAGES:
                out["warnings"].append(
                    f"{b['id']} has a vault marker but no state entry (state lost?)"
                )
        if sec["new_bullets"] and not effective_path:
            out["sections_missing_path"].append(name)

    for task_id, task in tasks.items():
        if task.get("stage") in ACTIVE_STAGES:
            out["active_tasks"].append(
                {
                    "id": task_id,
                    "stage": task.get("stage"),
                    "title": task.get("title"),
                    "section": task.get("section"),
                    "slack_thread_ts": task.get("slack_thread_ts"),
                }
            )

    if out["new_bullets"]:
        out["reasons"].append(f"{len(out['new_bullets'])} new bullet(s) in inbox")
    if out["active_tasks"]:
        stages = ", ".join(f"{t['id']}:{t['stage']}" for t in out["active_tasks"])
        out["reasons"].append(f"active tasks: {stages}")
    if out["warnings"]:
        out["reasons"].append("warnings need review")

    if out["reasons"]:
        out["verdict"] = "WORK"

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
