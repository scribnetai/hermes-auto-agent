# hermes-auto-agent

**Install an AI agent persona into [Hermes](https://github.com/NousResearch/hermes-agent) by pasting one file.**

Most agent setups are installed by a human following a README. This repo
flips that: `prompt.md` is an instruction file written for the *agent*.
You paste it into a fresh Hermes profile, name the persona you want, and
the agent installs it — skills, persona, seed memory — then proves the
install with this repo's own checker and a smoke test, and reports back in
a fixed shape whose last item must confess anything it did that wasn't in
the steps.

## Quick start

```bash
git clone https://github.com/scribnetai/hermes-auto-agent.git
cd hermes-auto-agent
python3 tools/validate.py
# expect: ALL CHECKS PASSED, exit code 0
```

1. Start a Hermes session on a **fresh profile** (a throwaway profile is
   the right place for a first run).
2. Build the paste — no manual editing. This fills in the persona and the
   repo path and writes a ready-to-paste file:
   ```bash
   python3 tools/make_paste.py demo-researcher
   # writes paste-ready.md — copy the whole file, paste it into the session
   ```
   (By hand works too: first line `PERSONA=demo-researcher,
   REPO=<absolute path to this clone>`, then everything in `prompt.md`
   below the `---` line.)
3. Read the report. Item 7 — "anything not in the steps" — is the result:
   empty means the install was fully by the book. Then verify it yourself
   (next section) — the report is a claim, this is the result:
   ```bash
   # Docker (run from your compose folder; adjust the repo path to yours):
   docker compose exec hermes python3 /opt/data/hermes-auto-agent/tools/verify_profile.py /opt/data/profiles/<name> demo-researcher
   # Bare metal (run from your clone):
   python3 tools/verify_profile.py ~/.hermes/profiles/<name> demo-researcher
   ```
   (For the default profile, the profile home is the Hermes home itself:
   `/opt/data` in Docker, `~/.hermes` bare metal.)

Two environment notes:

- **The agent's shell needs `python3`.** The prompt's Step 0 checks for it
  and stops if it's missing, because every later step (validator,
  builder) runs through it, including inside a container.
- **The agent can only see what its environment can see.** `REPO=` must
  be a path that exists *where the agent runs*. Bare metal: the path as
  cloned. **Docker: a host path is invisible inside the container** —
  bind-mount the clone into the container, or copy it in, and use the
  in-container path:
  ```bash
  # run from the folder holding your docker-compose.yml
  docker compose cp ./hermes-auto-agent hermes:/opt/data/hermes-auto-agent
  # then: REPO=/opt/data/hermes-auto-agent
  ```
  If the agent reports the repo path doesn't exist, this is almost
  always why.

The bundled `demo-researcher` persona is a small, harmless example
(summarizes sources with citations). Replace it with your own — see
"Make it yours".

## What's in the box

```
prompt.md                     The installer. The whole point.
tools/validate.py             Bundle checker + secret scan. The gate.
tools/make_paste.py           Builds paste-ready.md with variables filled in.
tools/verify_profile.py       Operator-side install verification (no trust).
personas/<id>/persona.yaml    Source manifest: id, skills, memory scope.
bundles/<id>/                 A ready-to-install bundle:
  MANIFEST.md                   Install + verify instructions (authority).
  persona.md                    Who the agent is.
  skills/<skill>/SKILL.md       What it can do (agentskills.io format).
  memories/MEMORY.md            Seed memory (what it knows on day one).
  memories/USER.template.md     Optional user-profile seed.
```

## The safety model (read this — it's the actual design)

A written instruction is advice; a fence is physics. This kit leans on
fences:

- **Throwaway profile first.** Test installs land in a disposable profile,
  never your daily driver.
- **Back up before overwrite.** The prompt requires timestamped backups of
  any memory file it would replace — and a full data-dir backup before
  experimenting is the operator's job (see the wipe section).
- **No secrets, no sudo — stop and report.** The installing agent must
  never ask for a password or token, never elevate, and must halt on the
  first unexpected output instead of improvising around it.
- **The report is a claim, not a result.** Verify it yourself:
  `python3 tools/verify_profile.py <profile-home> <persona-id>` checks the
  seed memory (presence + size) and every declared skill against the
  filesystem and exits non-zero on any miss. Then open a *fresh* session
  on the profile and ask it — unled — what its role is. If it answers as
  the installed persona with no install conversation in its history, the
  install is real.

## If an install goes wrong: wipe the one profile and retry

Deletes **only the named profile**; every other profile is untouched.
Every step below comes in two flavors — use the one that matches how
*your* Hermes runs:

- **Docker** (Compose deployment): run from the folder holding your
  `docker-compose.yml`; the Hermes data dir is `/opt/data` in-container.
- **Bare metal** (direct install, e.g. a venv): `$HERMES_HOME` is your
  Hermes home — `~/.hermes` by default.

**Step 0 — back up first.** A wipe cannot be undone without one:

```bash
# Docker (backs up the compose data folder):
tar czf data-backup-$(date +%Y%m%d-%H%M%S).tar.gz data/
# Bare metal:
tar czf hermes-backup-$(date +%Y%m%d-%H%M%S).tar.gz $HERMES_HOME
```

**Step 1 — close the profile.** Exit any open session on it; a live
session can recreate files while you delete them.

**Step 2 — delete the profile** (it asks you to type the name to confirm):

```bash
# Docker:
docker compose exec hermes hermes profile delete <profile-name>
docker compose exec hermes hermes profile list
# Bare metal:
hermes profile delete <profile-name>
hermes profile list
```

If the delete ends with "session/routing identity settlement is still
pending", run the command it names:

```bash
# Docker:
docker compose exec hermes hermes profile purge-identity <profile-name>
# Bare metal:
hermes profile purge-identity <profile-name>
```

**Step 3 — check for leftovers** (an empty folder sometimes survives):

```bash
# Docker:
docker compose exec hermes ls /opt/data/profiles/
# if <profile-name> is still listed:
docker compose exec hermes rm -rf /opt/data/profiles/<profile-name>
docker compose exec hermes ls /opt/data/profiles/   # confirm it is gone
# Bare metal:
ls $HERMES_HOME/profiles/
rm -rf $HERMES_HOME/profiles/<profile-name>        # only if still listed
ls $HERMES_HOME/profiles/                          # confirm it is gone
```

**Step 4 — if the failure was permissions** (the agent reported files it
could not delete or rebuild): the agent works as a specific user; files
owned by anyone else are outside its reach, so ownership is fixed by
*you, the operator* — never by the agent. Verify writability **as the
agent's user**, not as root:

```bash
# Docker (the agent's uid inside the container):
docker compose exec hermes sh -c 'id -u; ls -ld /opt/data/<repo>'
docker compose exec -u <agent-uid> hermes sh -c 'touch /opt/data/<repo>/.wtest && rm /opt/data/<repo>/.wtest && echo WRITABLE-AS-AGENT'
# Bare metal (the agent runs as your user — check the repo folder):
ls -ld <repo>
touch <repo>/.wtest && rm <repo>/.wtest && echo WRITABLE
```

**Step 5 — retry clean:** recreate the profile and repeat the one-paste
install:

```bash
# Docker:
docker compose exec hermes hermes profile create <profile-name>
# Bare metal:
hermes profile create <profile-name>
```

⚠️ **Never** delete the whole data dir (`/opt/data`, `$HERMES_HOME`) or
the whole `profiles/` folder. Every command above names exactly one
profile. If reality doesn't match this page, stop and restore from the
Step 0 backup instead of guessing.

## Make it yours

1. Copy `personas/demo-researcher/persona.yaml` to
   `personas/<your-id>/persona.yaml` and edit the skill list.
2. Copy `bundles/demo-researcher/` to `bundles/<your-id>/`; write your
   `persona.md`, drop skills (agentskills.io `SKILL.md` format) into
   `skills/`, and keep the seed `memories/MEMORY.md` under ~2,200
   characters.
3. Update the bundle's `MANIFEST.md` (install + verify lines).
4. Run `python3 tools/validate.py`, then install with `prompt.md` —
   into a test profile first.

## License

MIT. See `LICENSE`.
