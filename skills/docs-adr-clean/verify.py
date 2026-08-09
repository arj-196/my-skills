#!/usr/bin/env python3
"""Verify an ADR corpus after a clean/merge/renumber pass.

    python3 verify.py [repo_root] [--adr-dir docs/adr]

Checks, all of which must pass:
  1. every Python source file still parses (reflowing comments can break code)
  2. the set of ADR numbers referenced anywhere == the set of ADR files present
     (including citations wrapped across a line break: "ADR\n0004")
  3. every "ADR NNNN § anchor" resolves to a real `##` heading in that ADR
  4. every markdown link into the ADR directory resolves to a file
  5. numbering is contiguous 0001..N with no gaps

Exit 0 if clean, 1 otherwise. Prints a word-count summary either way.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

# A citation: number, plus an optional "§ anchor" terminated by punctuation.
# \s+ not a literal space: the number may arrive via a joined continuation
# line (see the wrap handling below) with its original indent collapsed.
CITE = re.compile(r"ADR\s+(\d{4})(?:\s*§\s*([^.,;:)\]\n]+))?")
LINK = re.compile(r"\]\(([^)]*adr/[^)]+\.md)\)")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
             "build", ".mypy_cache", ".pytest_cache", ".ruff_cache"}


# Generic scaffolding headings are not citable anchors; only decision-named
# sections are. An ADR whose sections are all scaffolding needs no anchor.
SCAFFOLD = {"context", "decision", "consequences", "status", "alternatives",
            "alternatives considered", "considered options",
            "considered alternatives", "tried and retracted"}


def anchorable(headings: list[str]) -> list[str]:
    return [h for h in headings if h.strip().lower() not in SCAFFOLD]


def walk(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not any(d in SKIP_DIRS for d in p.parts):
            yield p


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    adr_dir = root / "docs" / "adr"
    if "--adr-dir" in sys.argv:
        adr_dir = root / sys.argv[sys.argv.index("--adr-dir") + 1]
    if not adr_dir.is_dir():
        print(f"no ADR directory at {adr_dir}")
        return 1

    adrs = sorted(p for p in adr_dir.glob("[0-9]*.md"))
    heads = {p.name[:4]: [h.strip() for h in
                          re.findall(r"^##\s+(.+)$", p.read_text(), re.M)]
             for p in adrs}
    present = set(heads)
    fails: list[str] = []

    # 1 — sources parse
    for p in walk(root):
        if p.suffix == ".py":
            try:
                ast.parse(p.read_text())
            except SyntaxError as e:
                fails.append(f"{p.relative_to(root)}:{e.lineno} does not parse: {e.msg}")

    # 2–3 — citations and anchors
    referenced: set[str] = set()
    n_cites = n_anchored = 0
    for p in walk(root):
        if p.suffix not in {".py", ".md", ".txt", ".rst", ".toml", ".ts", ".tsx",
                            ".js", ".go", ".rs", ".java", ".rb", ".sh"}:
            continue
        if adr_dir in p.parents and p.name != "README.md":
            continue                      # an ADR citing its own siblings is fine
        lines = p.read_text().split("\n")
        for i, ln in enumerate(lines):
            nxt = re.sub(r"^\s*#?\s*", "", lines[i + 1]) if i + 1 < len(lines) else ""
            # the citation itself may wrap between "ADR" and its number
            # ("ADR\n0004", the continuation possibly behind a comment
            # prefix). A line-anchored scan is blind to exactly the stale
            # citations a renumbering pass leaves behind — join for matching,
            # but skip matches starting in the tail: line i+1 scans those.
            scan = ln + " " + nxt if re.search(r"ADR\s*$", ln) else ln
            for m in CITE.finditer(scan):
                if m.start() > len(ln):
                    continue
                n_cites += 1
                num, sec = m.group(1), m.group(2)
                referenced.add(num)
                where = f"{p.relative_to(root)}:{i + 1}"
                if num not in present:
                    fails.append(f"{where} cites ADR {num} — no such file")
                    continue
                # an anchor may wrap onto the next line, with the break either
                # before or after the "§"
                if sec is None and re.fullmatch(r"\s*§?\s*", scan[m.end():]):
                    tail = scan[m.start():] + (" " + nxt if scan is ln else "")
                    m2 = CITE.search(tail)
                    sec = m2.group(2) if m2 else None
                if sec is None:
                    n_real = len(anchorable(heads[num]))
                    if n_real > 2:
                        print(f"  · {where} cites ADR {num} with no § anchor "
                              f"({n_real} anchorable sections)")
                    continue
                n_anchored += 1
                s = " ".join(sec.split()).lower()
                if not any(h.lower().startswith(s[:len(h)]) or s.startswith(h.lower())
                           for h in heads[num]):
                    fails.append(f"{where} ADR {num} § {sec.strip()} — no such section")

    missing = present - referenced
    if missing:
        print(f"  · ADRs never cited from code or docs: {sorted(missing)}")

    # 4 — markdown links
    for p in walk(root):
        if p.suffix != ".md":
            continue
        for m in LINK.finditer(p.read_text()):
            target = (p.parent / m.group(1)).resolve()
            if not target.exists():
                fails.append(f"{p.relative_to(root)} broken link -> {m.group(1)}")

    # 5 — contiguous numbering
    nums = sorted(int(n) for n in present)
    if nums and nums != list(range(1, len(nums) + 1)):
        gaps = sorted(set(range(1, max(nums) + 1)) - set(nums))
        fails.append(f"numbering not contiguous; gaps at {gaps}")

    words = sum(len(p.read_text().split()) for p in adrs)
    print(f"\n{len(adrs)} ADRs, {words:,} words, "
          f"{n_cites} citations ({n_anchored} anchored)")
    for p in adrs:
        print(f"  {p.name:<55} {len(p.read_text().split()):>6,} words")

    if fails:
        print(f"\n{len(fails)} FAILURE(S):")
        for f in fails:
            print(f"  ✗ {f}")
        return 1
    print("\n✓ all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
