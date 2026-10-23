# Bundle manifest — demo-researcher (target: hermes)

Contents:

| File | Job |
|---|---|
| `persona.md` | Who the agent is; folded into the Hermes profile |
| `skills/` | agentskills.io skills this persona carries |
| `memories/MEMORY.md` | Seed memory installed into the profile |
| `memories/USER.template.md` | Optional user seed (operator's decision) |

## Install

1. Copy `skills/*` into the profile's skills folder.
2. Copy `memories/MEMORY.md` into the profile's memories folder
   (back up any existing file first).
3. Fold `persona.md` into the Hermes profile: place it where this Hermes
   setup loads its persona/SOUL from, and report the exact destination
   path in the install report.

## Verify

- The skills named in `personas/demo-researcher/persona.yaml` are present
  in the profile's skills folder.
- Seed memory is under ~2,200 characters.
- Ask the persona, in a fresh session, to state its role; it should
  answer as this persona.
