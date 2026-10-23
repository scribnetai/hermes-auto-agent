# One-paste install — a persona bundle into Hermes

Paste everything below the line into a fresh Hermes profile (or any agent
with shell + file access on the machine that hosts Hermes). It installs ONE
persona bundle, correctly, and proves it with the repo's own checker.

Rules the installing agent must follow:

- Change nothing in the repo except build output under `dist/`.
- Never print, copy, or ask for any password, token, or API key. If a step
  seems to need one, stop and report that instead of working around it.
- Never use or request elevated privileges (no `sudo`). If a step seems to
  need them, stop and report that instead.
- Do not overwrite an existing memory file in the profile without first
  copying it to a timestamped backup in the same folder.
- If any checker below does not produce the expected output, stop, report
  the exact output, and do not improvise a fix.

---

You are installing a persona bundle into Hermes.

**Inputs** (if I did not specify them in my paste, ask me for both before
starting — do not guess):

- PERSONA: the persona id (a folder name under `bundles/`)
- REPO: the absolute path where this repo is cloned on this machine

**Step 1 — Validate the repo first.**

```bash
cd <REPO>
python3 tools/validate.py
```

Expected: `ALL CHECKS PASSED`, exit code 0. If it fails, stop and show me
the output — do not install from a repo that does not validate.

**Step 2 — Locate the bundle and read its manifest.**

```bash
ls bundles/<PERSONA>/
cat bundles/<PERSONA>/MANIFEST.md
```

Expected: a bundle folder containing `MANIFEST.md`, `persona.md`, a
`skills/` folder, and a `memories/` folder (holding `MEMORY.md` and
`USER.template.md`). The MANIFEST is the authority for what gets installed
and where. If the manifest disagrees with the steps below, follow the
manifest and tell me about the difference.

If the bundle folder is missing, or any expected file is absent, STOP and
report the exact output. Do not delete, move, chmod, or chown anything, do
not use sudo, and do not substitute a different bundle — a bundle found
anywhere else does not count as Step 2 done.

**Step 3 — Back up before overwriting (only if the targets already exist).**

Your profile home is the directory in the `HERMES_HOME` environment
variable. Check for existing memory files there and back up any you find:

```bash
echo $HERMES_HOME
ts=$(date +%Y%m%d-%H%M%S)
[ -f $HERMES_HOME/memories/MEMORY.md ] && cp $HERMES_HOME/memories/MEMORY.md $HERMES_HOME/memories/MEMORY.md.bak-$ts
[ -f $HERMES_HOME/memories/USER.md ] && cp $HERMES_HOME/memories/USER.md $HERMES_HOME/memories/USER.md.bak-$ts
ls $HERMES_HOME/memories/
```

**Step 4 — Install skills, the persona, and seed memory.**

```bash
mkdir -p $HERMES_HOME/skills $HERMES_HOME/memories
cp -r bundles/<PERSONA>/skills/* $HERMES_HOME/skills/
cp bundles/<PERSONA>/memories/MEMORY.md $HERMES_HOME/memories/MEMORY.md
# Install the persona itself, per the MANIFEST's Install line:
# place persona.md where this Hermes setup loads its persona/SOUL from
# (back it up in Step 3 first if one already exists there), and report
# the exact destination path you used in your final report.
```

Seeding `USER.md` from the bundle's `memories/USER.template.md` is
optional and is **my** decision, not yours: ask me first, and only copy it
if I confirm (`cp bundles/<PERSONA>/memories/USER.template.md
$HERMES_HOME/memories/USER.md`).

**Step 5 — Verify the install.**

```bash
ls $HERMES_HOME/skills/
wc -c $HERMES_HOME/memories/MEMORY.md
```

Expected: every skill named in `personas/<PERSONA>/persona.yaml` is
present. The profile may also contain skills that ship with the platform
itself — those are normal; list them separately in your report instead of
treating them as a mismatch. `MEMORY.md` should be under ~2,200 characters
(the Hermes seed-memory limit); if it is over, stop and report the count
instead of truncating it yourself.

**Step 6 — Smoke test.**

Start a NEW session on this profile (not this one) and give it:

1. One synthetic task that matches one of the installed skills. Do not use
   any real personal data, and **do not name the skill in the task
   wording** — a skill only counts as fired if the session picks it up
   unprompted.
2. One separate, unled question: ask it to state its role.

Success: the session visibly uses the skill on the task, AND states a role
matching the installed persona.

**Report back to me, in this exact shape:**

1. Validator result (pass/fail + exit code)
2. Bundle path used
3. Skills installed (list) vs skills expected from `persona.yaml` (list),
   plus any platform-bundled skills you noticed, listed separately
4. The exact destination path where you placed the persona file
5. Any backup files created in Step 3 (names, or "none needed")
6. Smoke-test task used, whether the skill fired unprompted, and the
   role the new session stated
7. Anything you had to do that is NOT in these steps — if this list is not
   empty, say so plainly; that is the result of the test, not a failure
   to hide
