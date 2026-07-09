#!/usr/bin/env python3
"""
arj-focus Linear helper — all ARJ workspace access goes through here.

Claude Code's Linear MCP is scoped to the Mendo org and CANNOT reach Arjun's
personal ARJ workspace, so ARJ read/write uses the personal API key via GraphQL.
The key is read from the LINEAR_ARJ_API_KEY env var (stored in ~/.hermes/.env,
chmod 600, never committed). See docs/adr/0002.

Usage:
  linear_arj.py list                 # all ARJ issues, any state, with description (for anchor dedup)
  linear_arj.py create <json>        # create issue; json: {title, description, priority}
  linear_arj.py comment <id> <text>  # add a comment to an issue
  linear_arj.py set_priority <id> <0-4>

Priority: 0 none, 1 urgent, 2 high, 3 medium, 4 low.
Exit non-zero on any API error so the caller can avoid advancing last_run.txt.
"""
import json
import os
import sys
import urllib.request
import urllib.error

TEAM_ID = "9cfe0eac-3600-4f74-a20a-8dcc2415ee2c"
API = "https://api.linear.app/graphql"


def _key():
    k = os.environ.get("LINEAR_ARJ_API_KEY")
    if not k:
        # last-ditch: source ~/.hermes/.env ourselves
        env = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env):
            for line in open(env):
                if line.startswith("LINEAR_ARJ_API_KEY="):
                    k = line.split("=", 1)[1].strip()
                    break
    if not k:
        sys.exit("ERROR: LINEAR_ARJ_API_KEY not set (expected in ~/.hermes/.env)")
    return k


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Authorization": _key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Linear HTTP {e.code}: {e.read().decode()[:500]}")
    if "errors" in out:
        sys.exit("Linear API error: " + json.dumps(out["errors"]))
    return out["data"]


def cmd_list():
    q = """
    query($t:String!){ team(id:$t){ issues(first:250){ nodes {
      id identifier title priority
      state { name type }
      description
    } } } }"""
    nodes = gql(q, {"t": TEAM_ID})["team"]["issues"]["nodes"]
    print(json.dumps(nodes, ensure_ascii=False, indent=2))


def cmd_create(payload_json):
    p = json.loads(payload_json)
    q = """
    mutation($i:IssueCreateInput!){ issueCreate(input:$i){
      success issue { identifier url } } }"""
    inp = {
        "teamId": TEAM_ID,
        "title": p["title"],
        "description": p.get("description", ""),
        "priority": int(p.get("priority", 0)),
        # default new Tickets to Todo (active), not Backlog
        "stateId": p.get("stateId", "fad22da0-cfe6-4310-8384-7f6d97f5a13d"),
    }
    d = gql(q, {"i": inp})["issueCreate"]
    print(json.dumps(d, ensure_ascii=False))


def cmd_comment(issue_id, text):
    q = """
    mutation($i:CommentCreateInput!){ commentCreate(input:$i){ success } }"""
    print(json.dumps(gql(q, {"i": {"issueId": issue_id, "body": text}})))


def cmd_set_priority(issue_id, pri):
    q = """
    mutation($id:String!,$i:IssueUpdateInput!){ issueUpdate(id:$id,input:$i){ success } }"""
    print(json.dumps(gql(q, {"id": issue_id, "i": {"priority": int(pri)}})))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
    elif cmd == "create":
        cmd_create(sys.argv[2])
    elif cmd == "comment":
        cmd_comment(sys.argv[2], sys.argv[3])
    elif cmd == "set_priority":
        cmd_set_priority(sys.argv[2], sys.argv[3])
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
