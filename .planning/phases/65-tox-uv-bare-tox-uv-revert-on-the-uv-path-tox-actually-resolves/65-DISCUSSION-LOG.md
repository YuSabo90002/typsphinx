# Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-12
**Phase:** 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
**Areas discussed:** SC#3 wording, SC#3 pass criterion, outside-FHS control locus, ride-along versions

Before any question, a scratch pre-measurement was presented (tox-uv source read, `uv lock` diff,
inside/outside-FHS tox runs). The owner then asked whether the revert had already happened; it had
not (measured on `HEAD`, `origin/main` and the milestone branch — only `e603f36e` ever touched the
pin). The owner said to proceed, and the four questions were asked one at a time.

---

## SC#3 wording

| Option | Description | Selected |
|--------|-------------|----------|
| AMENDED block (recommended) | Keep SC#3 / constraint 12 text, append an owner-approved AMENDED block with the measurement; substantive "observe from inside tox" requirement stays; verifier reports both readings | ✓ |
| Record in CONTEXT only | Leave ROADMAP untouched, note the error as a D-NN | |
| Leave as is | Keep text, put the measurement in evidence only | |

**User's choice:** AMENDED block.

---

## SC#3 pass criterion

| Option | Description | Selected |
|--------|-------------|----------|
| Pass, no TOX_UV_PATH (recommended) | Bundled = the same `.venv/bin/uv` the shim hits, executable inside FHS; `-vv` path + outside control closes it | ✓ |
| Set TOX_UV_PATH explicitly | Export it in the `flake.nix` shim env (not `tox.ini`, which would reach CI); resolves to the same file | |
| Bundled winning = fail | Follow ROADMAP literally; require the recovery | |

**User's choice:** Pass, no `TOX_UV_PATH`.

---

## Outside-FHS control locus

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated venv in the worktree (recommended) | nix-python venv beside the provisioned one, lock-pinned tox-uv, same `tox.ini`, run outside FHS; not committed; evidence verbatim | ✓ |
| Main checkout `.venv` | Already nix 3.13.13; re-sync after merge and run there; leaves worktree mode, rewrites main venv mid-phase | |
| Scratch throwaway probe | Like the pre-measurement; measures a copy, not the changed tree | |

**User's choice:** Dedicated venv in the worktree.

---

## Ride-along versions

| Option | Description | Selected |
|--------|-------------|----------|
| Accept both and record (recommended) | Commit plain `uv lock` output (tox-uv-bare 1.35.2→1.36.0, uv 0.12.13 added); record the maintainer-machine uv switch 0.11.25→0.12.13; keep the shim's nixpkgs leg for bootstrap | ✓ |
| Hold at 1.35.2 | Pin tox-uv to 1.35.2 so only the name changes; extra lock step; uv switch happens anyway | |

**User's choice:** Accept both and record.

---

## Claude's Discretion

- Mechanism for printing the resolved uv version from inside the tox run (no committed observation-only `tox.ini` edit).
- How the control venv obtains lock-pinned versions and where it lives.
- Cold (`-r`) vs warm tox run for the observation.
- Timing of the main checkout `.venv` re-sync.
- Plan split and evidence file naming.

## Deferred Ideas

- Comment rewording in `tox.ini` / `CLAUDE.md` / `flake.nix` → Phase 68 (DOC-19..21).
- Dropping the `uv` shim's nixpkgs leg → not now (bootstrap).
- Six keyword-matched todos reviewed, none folded (see CONTEXT `<deferred>`).
