---
created: 2026-08-16T13:40:00Z
title: "Every dependabot PR dies before running a single test: it bumps `pyproject.toml` without regenerating `uv.lock`, and all eleven `uv sync --locked` steps refuse the stale lockfile"
area: ci, tooling
severity: major
files:
  - .github/dependabot.yml
  - .github/workflows/ci.yml:37,67,88,109,174,202
  - .github/workflows/docs.yml:29
  - .github/workflows/release.yml:36,113
  - .github/workflows/drift.yml:29-32
---

## Problem

dependabot opens PRs that change **only** `pyproject.toml` — measured, both open PRs are
`pyproject.toml (+1/-1)` and touch nothing else. It does not understand `uv.lock` and never
regenerates it. Every CI job then begins with

```
uv sync --extra dev --locked
```

which refuses a lockfile that no longer matches the manifest:

```
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
##[error]Process completed with exit code 1.
```

The failure is at the *dependency-install* step, so **no test, lint, or type check ever runs**.
The PR carries zero signal about whether the proposed bump actually works — which is the entire
reason the PR exists.

### Measured 2026-08-16

Both open dependabot PRs, 100% of jobs failing, on every OS:

| PR | Bump | Files changed | Run | Jobs |
|----|------|---------------|-----|------|
| #128 | `docutils` `<0.23,>=0.21` → `>=0.21,<0.24` | `pyproject.toml` only | 31861132557 | 11 fail, 1 cancelled |
| #123 | `ruff` `<0.16,>=0.15` → `>=0.15,<0.17` | `pyproject.toml` only | 30398777260 | all fail |

Same `error:` line in every failing job of both runs. #123 has been dead since **2026-07-27** —
about three weeks of a completely non-functional dependency-update path at the time of filing.

### Blast radius

`--locked` appears in **eleven** steps across four workflows, so there is no lane that
accidentally still works:

- `ci.yml:37,67,88,109,174,202` — tests, coverage, integration, build
- `docs.yml:29`
- `release.yml:36,113`
- `drift.yml:32` — but see below, this one is fine

`drift.yml` is the one workflow that is **not** affected, and it is also the shape of the answer:
it runs `uv lock --upgrade` (line 29) *before* `uv sync --locked` (line 32), so its lockfile is
always current by construction.

## Not the same failure as main's red CI

Do not conflate these. `main`'s CI was also red when this was filed, at run `31862249232`, but for
an unrelated reason — `tests/test_state_guard_shapes_gate.py` reading
`.planning/phases/49-.../49-SHAPES-RED-EVIDENCE.md`, which moved when the v0.8.0 milestone was
archived. That one already has a fix (`d1eff100`) sitting on `gsd/v0.9.0-per-document-templates`
and resolves itself when the milestone merges. This todo's failure survives that merge untouched:
it is a lockfile/manifest mismatch, not a test defect.

## Solution

TBD — three candidate shapes, in rough order of preference. This needs a decision, not just an edit.

1. **Regenerate the lockfile on dependabot PRs.** A workflow triggered on
   `pull_request` from `dependabot[bot]` that runs `uv lock` and pushes the result back onto the PR
   branch, so the existing `--locked` steps then pass. Keeps `--locked`'s reproducibility guarantee
   intact everywhere. Costs a `permissions: contents: write` on that workflow and care about
   re-triggering CI on the pushed commit.
2. **Let `drift.yml` be the only dependency-update path and stop dependabot from opening pip PRs.**
   `drift.yml` already re-resolves weekly and files an issue on breakage; the pip half of
   `.github/dependabot.yml` would be dropped, keeping the `github-actions` half (Actions bumps do
   not touch `uv.lock` and are unaffected). Smallest change; loses per-package PR granularity.
3. **Drop `--locked`** from the CI steps. Cheapest to write and the worst of the three — it removes
   the guarantee that CI installs exactly the resolved set, which is the property the flag was added
   for. Recorded only so it is explicitly rejected rather than silently rediscovered.

Whichever lands must be proven on a **real dependabot PR** — reopening/rerunning #123 or #128 and
observing the install step succeed — not on a hand-made branch that happens to carry a fresh
`uv.lock`. The defect is specifically about what dependabot itself produces.

Also decide what to do with the two PRs already open: they are ~3 weeks and ~2 weeks stale, and
their bumps (`docutils <0.24`, `ruff <0.17`) may want re-evaluating on their merits rather than
being merged just because CI finally goes green.

## Related

- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — #123 is the
  `ruff` bump specifically; the two are independent (that one is a local NixOS execution problem,
  this one is a CI lockfile problem) but both currently block acting on `ruff` versions.
