#!/usr/bin/env python3
"""Operator-side verification of a persona install.

An installing agent's report is a claim, not a result. This script is the
result: run it yourself, from any terminal that can read the profile's
files, and it checks the install against the repo — no trust involved.

Usage:
    python3 tools/verify_profile.py <profile-home> <persona-id> [--repo PATH]

    <profile-home>  the installed profile's home directory
                    (a named Hermes profile: /opt/data/profiles/<name>;
                    the default profile: /opt/data itself)
    <persona-id>    a folder name under personas/
    --repo PATH     repo root (default: this script's repo)

Checks:
    1. memories/MEMORY.md exists in the profile; size in characters
       (Hermes seed-memory limit ~2,200).
    2. Every skill declared in personas/<id>/persona.yaml exists under
       the profile's skills/ tree (searched recursively — platforms may
       nest skills under category folders) with a SKILL.md inside.
    3. A persona file exists in the profile home (persona.md or SOUL.md).

Exit code 0 = every check passed, 1 = at least one failed.
"""
import re
import sys
from pathlib import Path

def parse_skills(yaml_text):
    """Skills list from persona.yaml — flow style [a, b] or block style."""
    m = re.search(r"^skills\s*:\s*\[(.*?)\]\s*$", yaml_text, flags=re.M)
    if m:
        return [s.strip().strip("'\"") for s in m.group(1).split(",") if s.strip()]
    skills, in_list = [], False
    for line in yaml_text.splitlines():
        if re.match(r"^skills\s*:", line):
            in_list = True
            continue
        if in_list:
            item = re.match(r"^\s*-\s*([A-Za-z0-9._-]+)\s*$", line)
            if item:
                skills.append(item.group(1))
            elif line.strip() and not line.startswith((" ", "\t")):
                break
    return skills

def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    repo = Path(__file__).resolve().parent.parent
    if "--repo" in sys.argv:
        repo = Path(sys.argv[sys.argv.index("--repo") + 1]).resolve()
    if len(args) < 2:
        print(__doc__)
        return 2
    home, persona = Path(args[0]), args[1]
    failures = []

    def check(cond, label):
        print(("  ok  " if cond else " FAIL ") + label)
        if not cond:
            failures.append(label)

    check(home.is_dir(), f"profile home exists: {home}")
    yaml_path = repo / "personas" / persona / "persona.yaml"
    check(yaml_path.is_file(), f"persona manifest exists: {yaml_path}")
    if not (home.is_dir() and yaml_path.is_file()):
        print("\nVERIFY FAILED (prerequisites missing)")
        return 1

    mem = home / "memories" / "MEMORY.md"
    check(mem.is_file(), "seed memory installed (memories/MEMORY.md)")
    if mem.is_file():
        size = len(mem.read_text(encoding="utf-8"))
        check(size <= 2200, f"seed memory size {size} chars (limit ~2200)")

    declared = parse_skills(yaml_path.read_text(encoding="utf-8"))
    check(bool(declared), f"persona declares skills: {declared}")
    skills_root = home / "skills"
    for skill in declared:
        found = skills_root.is_dir() and any(
            p.is_dir() and p.name == skill and (p / "SKILL.md").is_file()
            for p in skills_root.rglob("*")
        )
        check(found, f"skill installed: {skill}")

    persona_file = (home / "persona.md").is_file() or (home / "SOUL.md").is_file()
    check(persona_file, "persona file present in profile home (persona.md or SOUL.md)")

    if failures:
        print(f"\nVERIFY FAILED — {len(failures)} check(s) failed")
        return 1
    print("\nVERIFY PASSED — install matches the repo")
    return 0

if __name__ == "__main__":
    sys.exit(main())
