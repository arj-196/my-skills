#!/usr/bin/env python3
"""Append one feedback to Robin's log (capture path).

Called when Arjun sends a Telegram message beginning with "Feedback". Keeps id
allocation, timestamp, and JSONL formatting deterministic so the capture step
never has to hand-format the log. Read the text from argv or stdin.

  python3 scripts/add_feedback.py "Feedback the login page is slow"
  echo "Feedback ..." | python3 scripts/add_feedback.py

Prints the allocated feedback id (e.g. F-4). Idempotent-ish: it does NOT dedup;
capture should only call it once per inbound Telegram message.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROBIN_DIR = Path.home() / ".hermes/robin"
FEEDBACK_LOG = ROBIN_DIR / "feedback.jsonl"


def next_id():
    n = 0
    if FEEDBACK_LOG.exists():
        for line in FEEDBACK_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                fid = json.loads(line).get("id", "")
            except json.JSONDecodeError:
                continue
            if isinstance(fid, str) and fid.startswith("F-"):
                try:
                    n = max(n, int(fid[2:]))
                except ValueError:
                    pass
    return f"F-{n + 1}"


def main():
    text = " ".join(sys.argv[1:]).strip() or sys.stdin.read().strip()
    if not text:
        print("ERROR: empty feedback text", file=sys.stderr)
        return 1

    # Strip a leading "Feedback" trigger word (and any following separator) so
    # the stored text is the substance, not the trigger.
    lowered = text.lower()
    if lowered.startswith("feedback"):
        text = text[len("feedback"):].lstrip(" :,-–—\t").strip() or text

    ROBIN_DIR.mkdir(parents=True, exist_ok=True)
    fid = next_id()
    row = {
        "id": fid,
        "ts": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "status": "unprocessed",   # -> "grouped" once a task absorbs it
        "task_id": None,           # set to R-n when grouped
    }
    with FEEDBACK_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(fid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
