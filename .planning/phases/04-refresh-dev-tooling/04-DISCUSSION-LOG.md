# Phase 4: Refresh Dev Tooling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-04
**Phase:** 4-refresh-dev-tooling
**Areas discussed:** pytest/mypy posture, bound style, GitHub Actions, verification gate, Python 3.9 cleanup

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| pytest/mypy posture | Rollback to 8.4/1.x vs accept green 9/2 | ✓ |
| Bound style | Bare `>=` floors vs `floor + <next-major` ceilings | ✓ |
| GitHub Actions | Verify-only vs SHA-pin | ✓ |
| Verification gate | push→observe PR vs local tox | ✓ |

**User's choice:** All four areas (multiSelect).

---

## pytest / mypy posture

Key finding surfaced before the question: `uv.lock` already resolves **pytest
9.1.1 / mypy 2.1.0** and Phase 3's PR #104 CI went green on that set — diverging
from the requirement's literal `pytest~=8.4` / `mypy>=1.13,<2.0` wording.

| Option | Description | Selected |
|--------|-------------|----------|
| Accept green 9/2 + next-major ceilings | Keep resolved versions, add `pytest<10` / `mypy<3` | ✓ |
| Rollback to 8.4/1.x per literal requirement | Cap + regenerate lock, downgrade pytest→8.x / mypy→1.x | |

**User's choice:** Accept the already-green 9/2, add next-major ceilings.
**Notes:** Deliberate, user-owned deviation from the literal TOOL-01 wording;
honors the "avoid major flip" spirit without rolling back a confirmed-green
baseline. To be logged in PROJECT.md Key Decisions.

---

## Bound style (black / ruff / tox)

| Option | Description | Selected |
|--------|-------------|----------|
| `floor + <next-major` ceilings | Phase 1 runtime-dep defensive pinning, extended to dev tools | ✓ |
| Bare `>=` floors bumped to resolved | Keep current dev-dep style, no ceilings | |

**User's choice:** `floor + <next-major` ceilings for all dev tools.
**Notes:** Consistent with the milestone's anti-drift theme and Phase 1 precedent;
floors bump to resolved versions (black 26.5.1, ruff 0.15.20, tox 4.56.1). Applied
in lockstep across `pyproject.toml [dev]` and `tox.ini` env deps.

---

## GitHub Actions

| Option | Description | Selected |
|--------|-------------|----------|
| Verify-only, no yaml edits | Actions already at latest majors | ✓ |
| SHA-pin actions this cycle | Supply-chain hardening | (deferred → Phase 5) |

**User's choice (via freeform):** Raised that lingering Python 3.9 test references
should be removed. Verification showed the CI matrix / classifiers / tox / tool
targets are already 3.9-free (Phase 3); only `README.md` (lines 36, 323) and two
ruff comment strings still say "3.9". User chose **(A)** — fold the README + ruff
comment cleanup into Phase 4. Action versions themselves confirmed **verify-only,
no yaml edits**.
**Notes:** SHA-pinning deferred to Phase 5 (durability guardrails).

---

## Verification gate

| Option | Description | Selected |
|--------|-------------|----------|
| Push PR → observe Actions run | Phase 2/3 pattern; catches transitive-dep shifts from lock regen | ✓ |
| Local tox green sufficient | Faster, but no observed-run guarantee | |

**User's choice:** Push a PR targeting `main` and observe ci.yml + docs.yml green.
**Notes:** Lock regeneration after floor/ceiling changes can shift transitive
deps, so an observed run is the milestone-consistent proof.

---

## Claude's Discretion

- Exact ceiling boundary syntax per tool (`~=` vs explicit `>=x,<y`).
- Whether a black floor bump triggers reformat (expected none; if it appears,
  include in the same batch per Phase 3 D-03).

## Deferred Ideas

- SHA-pin GitHub Actions to commit hashes (supply-chain hardening) → Phase 5.
