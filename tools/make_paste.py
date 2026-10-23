#!/usr/bin/env python3
"""Build a ready-to-paste install prompt with the variables filled in.

Reads prompt.md, fills in the persona id and the repo's absolute path,
and writes paste-ready.md (agent-facing part only, inputs line included)
so installing is: run this, copy the file, paste it. No manual editing.

Usage:
    python3 tools/make_paste.py <persona-id> [repo-path]

repo-path defaults to this repo's root. Output: <repo>/paste-ready.md
"""
import re
import sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    persona = sys.argv[1]
    script_repo = Path(__file__).resolve().parent.parent
    repo = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else script_repo

    src = repo / "prompt.md"
    if not src.is_file():
        print(f"FAIL: {src} not found")
        return 1
    text = src.read_text(encoding="utf-8")

    # Agent-facing part = everything after the first standalone --- line.
    parts = re.split(r"^---\s*$", text, maxsplit=1, flags=re.M)
    body = parts[1] if len(parts) == 2 else text

    body = body.replace("<PERSONA>", persona).replace("<REPO>", str(repo))
    leftover = sorted(set(re.findall(r"<[A-Z][A-Z0-9_]+>", body)))
    out = f"Inputs: PERSONA={persona}, REPO={repo}\n" + body.lstrip("\n")

    dest = repo / "paste-ready.md"
    dest.write_text(out, encoding="utf-8")
    print(f"wrote {dest} ({len(out)} chars) — copy the whole file and paste it")
    if leftover:
        print(f"note: unfilled placeholders remain: {', '.join(leftover)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
