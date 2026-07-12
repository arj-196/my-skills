#!/usr/bin/env python3
"""Notion OAuth token helper for Robin.

The Notion connection is an OAuth integration whose access token can expire.
This module owns the token lifecycle so the rest of Robin never thinks about it:

  get_token()  -> the current access token (from env / ~/.hermes/.env)
  refresh()    -> exchange the refresh_token for a fresh access+refresh pair,
                  persist BOTH back to ~/.hermes/.env, return the new access token

Notion rotates the refresh_token on every refresh, so both values MUST be
written back or the next refresh fails. Auth uses client_id:client_secret.

CLI:  python3 notion_token.py refresh    # force a refresh, print new token's tail
      python3 notion_token.py token      # print current access token
"""

import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".hermes/.env"
TOKEN_URL = "https://api.notion.com/v1/oauth/token"

ACCESS_KEY = "NOTION_API_KEY"
REFRESH_KEY = "NOTION_REFRESH_TOKEN"
CLIENT_ID_KEY = "NOTION_CLIENT_ID"
CLIENT_SECRET_KEY = "NOTION_CLIENT_SECRET"


def _read_env():
    vals = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def _write_env(updates):
    """Merge `updates` into ~/.hermes/.env, preserving all other lines."""
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    kept = [l for l in lines if l.strip() and l.split("=", 1)[0] not in updates]
    kept += [f"{k}={v}" for k, v in updates.items()]
    ENV_FILE.write_text("\n".join(kept) + "\n", encoding="utf-8")
    ENV_FILE.chmod(0o600)


def get_token():
    return _read_env().get(ACCESS_KEY)


def refresh():
    """Rotate the OAuth token. Returns the new access token.

    Raises RuntimeError with a clear message if credentials are missing or the
    endpoint rejects the refresh (so the caller can fail safe + warn).
    """
    env = _read_env()
    rt = env.get(REFRESH_KEY)
    cid = env.get(CLIENT_ID_KEY)
    secret = env.get(CLIENT_SECRET_KEY)
    if not (rt and cid and secret):
        missing = [k for k, v in {REFRESH_KEY: rt, CLIENT_ID_KEY: cid, CLIENT_SECRET_KEY: secret}.items() if not v]
        raise RuntimeError(f"cannot refresh Notion token; missing in .env: {', '.join(missing)}")

    body = json.dumps({"grant_type": "refresh_token", "refresh_token": rt}).encode()
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"Notion refresh HTTP {exc.code}: {detail}") from exc

    access = data.get("access_token")
    if not access:
        raise RuntimeError(f"Notion refresh returned no access_token: {data.get('error')}")

    updates = {ACCESS_KEY: access}
    if data.get("refresh_token"):            # Notion rotates it — persist the new one
        updates[REFRESH_KEY] = data["refresh_token"]
    _write_env(updates)
    return access


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "token"
    if cmd == "refresh":
        tok = refresh()
        print("refreshed; access token …" + tok[-6:])
    elif cmd == "token":
        print(get_token() or "")
    else:
        print("usage: notion_token.py [token|refresh]", file=sys.stderr)
        sys.exit(2)
