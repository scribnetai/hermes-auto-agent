#!/usr/bin/env python3
"""Minimal bundle checker + secret scan for hermes-auto-agent.

Verifies that every persona declared under personas/ has a complete,
consistent bundle under bundles/, and that no text file in the repo
contains anything shaped like a secret.

Usage: python3 tools/validate.py
Exit code 0 and 'ALL CHECKS PASSED' on success; 1 otherwise.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SECRET_PATTERNS = [
    r"ghp_[A-Za-z0-9]{20,}",            # GitHub personal access token
    r"github_pat_[A-Za-z0-9_]{20,}",    # GitHub fine-grained PAT
    r"AKIA[0-9A-Z]{16}",                # AWS access key id
    r"sk-[A-Za-z0-9]{20,}",             # generic API secret key
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*\S{8,}",
]

failures = []


def check(cond, label):
    print(("  ok  " if cond else " FAIL ") + label)
    if not cond:
        failures.append(label)


def parse_skills(yaml_text):
    """Pull the list under 'skills:' out of a persona.yaml (no yaml dep)."""
    skills, in_list = [], False
    for line in yaml_text.splitlines():
        if re.match(r"^skills\s*:", line):
            in_list = True
            continue
        if in_list:
            m = re.match(r"^\s*-\s*([A-Za-z0-9._-]+)\s*$", line)
            if m:
                skills.append(m.group(1))
            elif line.strip() and not line.startswith((" ", "\t")):
                break
    return skills


personas = sorted(p.parent for p in (ROOT / "personas").glob("*/persona.yaml"))
check(bool(personas), f"personas found: {len(personas)}")

for pdir in personas:
    pid = pdir.name
    bundle = ROOT / "bundles" / pid
    check(bundle.is_dir(), f"{pid}: bundle folder exists")
    if not bundle.is_dir():
        continue
    check((bundle / "MANIFEST.md").is_file(), f"{pid}: MANIFEST.md present")
    check((bundle / "persona.md").is_file(), f"{pid}: persona.md present")
    check((bundle / "memories" / "MEMORY.md").is_file(),
          f"{pid}: memories/MEMORY.md present")
    mem = bundle / "memories" / "MEMORY.md"
    if mem.is_file():
        size = len(mem.read_text(encoding="utf-8"))
        check(size <= 2200, f"{pid}: seed MEMORY.md {size} chars (limit ~2200)")
    declared = parse_skills((pdir / "persona.yaml").read_text(encoding="utf-8"))
    check(bool(declared), f"{pid}: persona.yaml declares skills {declared}")
    for skill in declared:
        sk = bundle / "skills" / skill / "SKILL.md"
        check(sk.is_file(), f"{pid}: skill '{skill}' has SKILL.md")
        if sk.is_file():
            head = sk.read_text(encoding="utf-8")[:600]
            check("name:" in head and "description:" in head,
                  f"{pid}: skill '{skill}' frontmatter has name + description")

print("secret scan...")
hits = 0
for f in ROOT.rglob("*"):
    if f.is_file() and ".git" not in f.parts and f.suffix in {
        ".md", ".py", ".yaml", ".yml", ".txt", ".toml", ".json", ""
    }:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in SECRET_PATTERNS:
            for m in re.finditer(pat, text):
                # allow the patterns' own definitions inside this file
                if f.name == "validate.py":
                    continue
                print(f" FAIL possible secret in {f.relative_to(ROOT)}: {pat}")
                hits += 1
check(hits == 0, f"secret scan: {hits} hits")

if failures:
    print(f"\n{len(failures)} CHECK(S) FAILED")
    sys.exit(1)
print("\nALL CHECKS PASSED")
