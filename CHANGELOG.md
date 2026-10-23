# Changelog

Newest first. Every change to this repo gets a dated entry in the same pass.

## 2026-10-23 — review improvements: paste helper, operator verifier, python3 pre-flight
- `tools/make_paste.py <persona-id>`: fills the persona and repo path
  into `prompt.md` and writes `paste-ready.md` — no manual editing
  before pasting.
- `tools/verify_profile.py <profile-home> <persona-id>`: independent,
  operator-side verification of an install (seed-memory presence/size,
  every declared skill present on disk, persona file present). Exits
  non-zero on any miss — trust the checker, not the agent's report.
- `prompt.md` Step 0: the installing agent must prove `python3` exists in
  its own executing shell (container included) before the validator
  step, and stop if it doesn't.
- README quick start + safety model updated to match; `paste-ready.md`
  gitignored.

## 2026-10-23 — v0.1.0: initial public release
- `prompt.md`: the one-paste installer — an agent-executed install of one
  persona bundle into a Hermes profile (validate → locate bundle → back up
  → install skills + persona + seed memory → verify → unled smoke test →
  fixed seven-item report ending in a mandatory "anything not in the
  steps" confession).
- Safety rails as design, not decoration: throwaway test profiles,
  backup-before-overwrite, no secrets, no sudo, stop-and-report instead of
  improvising, and operator-side read-only verification (a report is a
  claim, not a result).
- `tools/validate.py`: minimal bundle checker (structure, skill list
  consistency, seed-memory size) + secret scan.
- `bundles/demo-researcher/`: a complete worked example — persona,
  one skill (`source-summary`), seed memory, user template, and a
  MANIFEST with install + verify lines.
- README: quick start, the safety model, a beginner-plain wipe-and-retry
  troubleshooting procedure, and adaptation steps.
