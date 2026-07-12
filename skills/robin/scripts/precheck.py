#!/usr/bin/env python3
"""Robin pre-check gate (Hermes / Telegram + Notion edition).

Deterministic, ZERO-LLM-TOKEN triage that runs at the start of every Robin tick
(cron every 30 min, or on-demand). It answers one question cheaply: *is there
anything for the model to do this tick?* — without ever reading a Notion page's
body or calling the LLM.

Two change sources:
  1. New feedback   -> unprocessed rows in the local feedback log.
  2. Notion answers -> a task's Notion page `last_edited_time` is newer than the
     value state.json recorded last tick (detected via a plain Notion REST call,
     which costs no model tokens).

Verdict:
  NOOP -> nothing changed, nothing in flight. The model must stop immediately.
  WORK -> payload says exactly what changed / what to advance.
  BUSY -> another tick already holds the single-tick lock; this run must stop
          immediately WITHOUT touching or releasing the lock (see tick lock).

Read-only w.r.t. Robin's data: never mutates the feedback log, state.json, or
Notion. The ONE thing it writes is the single-tick lock file (see below), which
is operational, not Robin state.

## Single-tick lock (only one tick at a time)

Robin does destructive work (git branches, merges, state.json writes), so two
ticks must never run concurrently. Hermes' scheduler already skips a *cron*
re-dispatch while the previous run is in flight, but that does NOT cover a manual
`/robin` / `robin tick` fired while a scheduled tick is working. This lock closes
that gap for ALL invocation paths.

- Acquiring: `precheck.py` (no args) atomically creates `~/.hermes/robin/tick.lock`
  (O_EXCL) recording pid + ISO acquire time. If a *fresh* lock already exists it
  returns `verdict=BUSY` and does NOT take the lock. A lock older than
  `LOCK_STALE_SECONDS` (a crashed/killed run) is stolen with a warning.
- On a `NOOP` verdict the gate releases the lock itself (no work follows), so an
  idle tick never leaves the lock held.
- On a `WORK` verdict the lock stays held; the tick MUST release it as its final
  action via `precheck.py release`, even on error.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROBIN_DIR = Path.home() / ".hermes/robin"
STATE_FILE = ROBIN_DIR / "state.json"
FEEDBACK_LOG = ROBIN_DIR / "feedback.jsonl"
ENV_FILE = Path.home() / ".hermes/.env"
LOCK_FILE = ROBIN_DIR / "tick.lock"
# A tick that has held the lock longer than this is presumed dead (crashed or
# killed) and its lock may be stolen. 60 min matches Hermes' 1h job ceiling, so
# a live run never trips it while a genuinely hung run cannot deadlock forever.
LOCK_STALE_SECONDS = 60 * 60

NOTION_VERSION = "2022-06-28"

# Stages where Robin is WAITING on Arjun. These only wake the tick when the
# task's Notion page changed (cheap REST poll), so idle waiting costs nothing.
WAITING_STAGES = {"grilling", "review", "blocked"}
# Stages where Robin has active work to push forward every tick regardless.
WORKING_STAGES = {"ingested", "planning", "implementing"}
ACTIVE_STAGES = WAITING_STAGES | WORKING_STAGES
TERMINAL_STAGES = {"done", "dropped"}


def load_env_key(name):
    """Fetch a key from the process env or ~/.hermes/.env (KEY=VALUE lines)."""
    if os.environ.get(name):
        return os.environ[name]
    if ENV_FILE.exists():
        try:
            for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() == name:
                    return v.strip().strip('"').strip("'")
        except OSError:
            pass
    return None


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            return {"_state_error": str(exc)}
    return {}


def load_feedback():
    """Return the list of feedback rows from the JSONL log (best-effort)."""
    rows = []
    if not FEEDBACK_LOG.exists():
        return rows
    try:
        for line in FEEDBACK_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                # A malformed line shouldn't sink the whole gate; flag upstream.
                rows.append({"_bad_line": line[:200]})
    except OSError as exc:
        rows.append({"_log_error": str(exc)})
    return rows


def _parse_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def notion_last_edited(page_id, token):
    """Return the page's last_edited_time (ISO str) via one plain REST GET.

    Zero model tokens. Raises urllib.error.HTTPError on auth failure (401) so the
    caller can refresh the OAuth token and retry; raises on other failures so the
    caller can fail *safe* (assume changed) rather than silently miss an answer.
    """
    pid = page_id.replace("-", "")
    url = f"https://api.notion.com/v1/pages/{pid}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("last_edited_time")


def _try_refresh_token(out):
    """Attempt an OAuth refresh via the sibling helper. Returns the new token or
    None, appending a warning on failure. Import is local so precheck stays
    importable even if the helper is absent."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import notion_token
        return notion_token.refresh()
    except Exception as exc:  # noqa: BLE001 — degrade safe on any refresh failure
        out["warnings"].append(f"Notion token refresh failed: {exc}")
        return None


def acquire_lock(out):
    """Atomically take the single-tick lock. Return True if we hold it.

    Uses O_EXCL create so two processes racing at the same instant cannot both
    win. A fresh existing lock -> BUSY (return False, do NOT steal). A lock older
    than LOCK_STALE_SECONDS -> presumed dead, stolen with a warning.
    """
    now = datetime.now(timezone.utc)
    payload = json.dumps({"pid": os.getpid(), "acquired": now.isoformat()})
    try:
        fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.write(fd, payload.encode("utf-8"))
        finally:
            os.close(fd)
        out["lock"] = {"state": "acquired", "acquired": now.isoformat()}
        return True
    except FileExistsError:
        existing = None
        try:
            existing = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
        held = _parse_iso(existing.get("acquired")) if existing else None
        age = (now - held).total_seconds() if held else None
        if age is not None and age < LOCK_STALE_SECONDS:
            out["lock"] = {
                "state": "busy",
                "held_by_pid": (existing or {}).get("pid"),
                "acquired": (existing or {}).get("acquired"),
                "age_seconds": int(age),
            }
            return False
        # stale (or unparseable/very old) -> steal it
        out["warnings"].append(
            f"stole stale tick lock (age "
            f"{int(age) if age is not None else 'unknown'}s, "
            f"pid {(existing or {}).get('pid')})"
        )
        try:
            LOCK_FILE.write_text(payload, encoding="utf-8")
        except OSError as exc:
            out["warnings"].append(f"could not overwrite stale lock: {exc}")
        out["lock"] = {"state": "acquired-after-steal", "acquired": now.isoformat()}
        return True
    except OSError as exc:
        # Filesystem problem: degrade safe by proceeding without a held lock
        # rather than wedging Robin. Warn so it is visible.
        out["warnings"].append(f"tick lock unavailable ({exc}); proceeding unlocked")
        out["lock"] = {"state": "unlocked-degraded"}
        return True


def release_lock():
    try:
        LOCK_FILE.unlink()
        print(json.dumps({"lock": "released"}))
    except FileNotFoundError:
        print(json.dumps({"lock": "already-released"}))
    except OSError as exc:
        print(json.dumps({"lock": "release-failed", "error": str(exc)}))


def main():
    out = {
        "verdict": "NOOP",
        "reasons": [],
        "new_feedbacks": [],
        "waiting_tasks": [],          # awaiting Arjun; wake only on Notion change
        "changed_tasks": [],          # waiting tasks whose Notion page changed
        "working_tasks": [],          # Robin has active work to push this tick
        "lock": {},
        "warnings": [],
    }

    ROBIN_DIR.mkdir(parents=True, exist_ok=True)

    # Single-tick lock FIRST — before any triage. If another tick holds it,
    # stop immediately with BUSY and do NOT release (we never took it).
    if not acquire_lock(out):
        out["verdict"] = "BUSY"
        out["reasons"].append("another tick holds the single-tick lock")
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    state = load_state()
    if "_state_error" in state:
        out["warnings"].append(f"state.json unreadable: {state['_state_error']}")
        state = {}

    tasks = state.get("tasks", {})
    token = load_env_key("NOTION_API_KEY")
    if not token:
        out["warnings"].append(
            "NOTION_API_KEY not set in env or ~/.hermes/.env — cannot cheaply "
            "poll Notion; waiting tasks will be woken every tick (token waste). "
            "Create a Notion internal integration, share the Robin home page with "
            "it, and store the secret as NOTION_API_KEY."
        )

    # --- 1. New feedback (local, deterministic) ---
    for row in load_feedback():
        if "_bad_line" in row:
            out["warnings"].append(f"malformed feedback line: {row['_bad_line']}")
            continue
        if "_log_error" in row:
            out["warnings"].append(f"feedback log error: {row['_log_error']}")
            continue
        if row.get("status", "unprocessed") == "unprocessed":
            out["new_feedbacks"].append(
                {"id": row.get("id"), "ts": row.get("ts"), "text": row.get("text")}
            )

    # --- 2. Task state (Notion change poll for waiting tasks) ---
    refreshed_this_run = [False]  # one-element list so the loop can rebind it
    for task_id, task in tasks.items():
        stage = task.get("stage")
        if stage not in ACTIVE_STAGES:
            continue

        info = {
            "id": task_id,
            "stage": stage,
            "title": task.get("title"),
            "app": task.get("app"),
            "notion_page_id": task.get("notion_page_id"),
        }

        awaiting = task.get("awaiting_answer", False)
        if stage in WAITING_STAGES and awaiting:
            page_id = task.get("notion_page_id")
            seen = task.get("notion_last_edit")
            changed = None
            if not page_id:
                # No page yet but marked awaiting — inconsistent; wake to fix.
                changed = True
                out["warnings"].append(f"{task_id} awaiting_answer but has no notion_page_id")
            elif not token:
                # Can't poll cheaply -> fail safe, assume it changed.
                changed = True
            else:
                try:
                    try:
                        latest = notion_last_edited(page_id, token)
                    except urllib.error.HTTPError as exc:
                        if exc.code in (401, 403) and not refreshed_this_run[0]:
                            # Token likely expired -> refresh once, retry, reuse
                            # the new token for the remaining tasks this run.
                            refreshed_this_run[0] = True
                            new = _try_refresh_token(out)
                            if new:
                                token = new
                                latest = notion_last_edited(page_id, token)
                            else:
                                raise
                        else:
                            raise
                    info["notion_last_edit_seen"] = seen
                    info["notion_last_edit_latest"] = latest
                    lt, st = _parse_iso(latest), _parse_iso(seen)
                    if lt is None:
                        changed = True  # couldn't parse -> be safe
                    elif st is None:
                        changed = True  # never recorded -> first look
                    else:
                        changed = lt > st
                except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError) as exc:
                    out["warnings"].append(f"{task_id} Notion poll failed ({exc}); waking to be safe")
                    changed = True

            info["notion_changed"] = bool(changed)
            out["waiting_tasks"].append(info)
            if changed:
                out["changed_tasks"].append(task_id)
        else:
            # WORKING_STAGES, or a waiting stage not yet awaiting an answer
            # (Robin still owes the questions/plan) -> active work this tick.
            out["working_tasks"].append(info)

    # --- Verdict ---
    if out["new_feedbacks"]:
        out["reasons"].append(f"{len(out['new_feedbacks'])} new feedback(s) to group")
    if out["changed_tasks"]:
        out["reasons"].append("Notion answers changed: " + ", ".join(out["changed_tasks"]))
    if out["working_tasks"]:
        stages = ", ".join(f"{t['id']}:{t['stage']}" for t in out["working_tasks"])
        out["reasons"].append(f"work in progress: {stages}")
    if any(w for w in out["warnings"] if "malformed" in w or "unreadable" in w or "inconsistent" in w):
        out["reasons"].append("warnings need review")

    if out["reasons"]:
        out["verdict"] = "WORK"

    # NOOP means no work follows this call, so the gate releases its own lock
    # here — otherwise an idle tick would leave the lock held until the next
    # run stole it as stale. On WORK we keep the lock; the tick releases it as
    # its final step via `precheck.py release`.
    if out["verdict"] == "NOOP" and out.get("lock", {}).get("state", "").startswith("acquired"):
        try:
            LOCK_FILE.unlink()
            out["lock"]["state"] = "released-noop"
        except OSError:
            pass

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "release":
        release_lock()
    else:
        sys.exit(main())
