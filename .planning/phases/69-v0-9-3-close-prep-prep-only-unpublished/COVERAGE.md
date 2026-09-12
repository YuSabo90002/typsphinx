# Phase 69: External API Coverage Declaration

No external API integration: this phase edits `CHANGELOG.md` only, runs the project's own tooling
(`uv`, `tox`, `pytest`, `black`, `mypy`, `ruff`, `sphinx-build`), pushes the milestone branch once
and dispatches the project's own `ci.yml` once, measures a trial merge with `git merge-tree`, and
writes planning evidence.

## Detector result

Plan-time detector run, recorded verbatim. Scope: the concatenated bodies of every
`69-0*-PLAN.md` in this phase directory, plus
`node /home/yuta/Documents/typsphinx/.claude/gsd-core/bin/gsd-tools.cjs query roadmap.get-phase 69` — the same scope the seal-time
`api-coverage.verify-pre` gate re-runs.

```json
{"detected":true,"signals":[{"verb":"integration","noun":"api","snippet":"contains: 'No external API integration: '"},{"verb":"(surface)","noun":"api","snippet":"| worktree → origin, GitHub API, PyPI (read-only) | `git ls-remote`, `gh release/run/pr list`, `curl` status probes; no "},"terms":{"verbs":["integrate","integrates","integrating","integration","wrap","wraps","wrapping","connect","connects","connecting","consume","consumes","consuming","wire","wires","wiring","onboard","onboarding","adopt","adopts","adopting"],"nouns":["api","apis","sdk","sdks","rest","graphql","grpc","endpoint","endpoints","oauth","oauth2","webhook","webhooks","mcp"]}}
```

`detected: true`, with two signals. Neither is an integration:

1. **`verb: "integration", noun: "api"`, snippet `contains: 'No external API integration: '`.**
   This is `69-02-PLAN.md`'s own frontmatter `must_haves.artifacts` entry naming this very
   `COVERAGE.md` file's required opening line — the declaration this file provides. It is prose
   *about* the detector's own false-positive shape, quoting the exact sentence this document must
   open with, not a description of an API this phase integrates. Phase 61's `COVERAGE.md` names
   the identical pattern: a bare integration-verb-plus-API-noun detector matching words that
   describe the detector itself.

2. **`verb: "(surface)", noun: "api"`, snippet `\| worktree → origin, GitHub API, PyPI (read-only) \| ...`.**
   This is `69-02-PLAN.md`'s own `<threat_model>` "Trust Boundaries" table row, which names
   `GitHub API` and `PyPI` explicitly as **read-only** boundaries this phase's plans cross with
   `git ls-remote`, `gh release/run/pr list`, and `curl` status-code probes. The row's own text
   states "no write crosses" that boundary — it is a security-review artifact documenting the
   absence of a write path to those services, not a description of a service this phase
   integrates, wraps, connects to, or consumes as a client.

## What the phase's network use actually is

- `git fetch`/`git ls-remote` against `origin` (this repository's own remote), and one
  fast-forward `git push` of the milestone branch (69-04).
- `gh workflow run CI` once (69-04), dispatching this project's own `ci.yml` — never
  `release.yml` and never `update-pin.yml`, both of which are named in the plans only to forbid
  them.
- Read-only `gh run list`/`gh run view`, `gh release list`, `gh pr list`, and one
  `gh api .../branches/main/protection` call (69-02, 69-04, 69-05) — all against this project's
  own GitHub repository, never a third party.
- Two `curl -o /dev/null -w '%{http_code}'` status-code probes of
  `pypi.org/pypi/typsphinx/<version>/json` (this phase's own package's public metadata endpoint,
  read-only, no authentication, no payload) — never an upload, and never any endpoint other than
  this project's own package page.
- `uv sync`/`uv lock --check` fetching only what `uv.lock` already pins — no new dependency is
  added this phase.

## Why this file exists

The seal-time `api-coverage.verify-pre` gate re-runs the same detector over plan prose that is
unavoidably dense with `gh`, workflow, and API-adjacent wording — CI dispatch, release-list
probes, tag probes, a Trust Boundaries table naming "GitHub API" and "PyPI", and this very
COVERAGE.md's own required declaration sentence quoted inside `69-02-PLAN.md`'s frontmatter. That
density is exactly the false-positive surface a bare integration-verb-plus-API-noun detector is
prone to matching on (Phase 61's `COVERAGE.md` recorded the identical hazard for its own
`gh`-and-workflow-dense plan prose). This file meets that detection with a reasoned declaration —
naming each signal and explaining why it is not an integration — rather than a fabricated
capability matrix. A matrix for an API this phase does not touch would be worse than no matrix.

## Seal-time gate result

```json
{
  "block": true,
  "passed": false,
  "coverage_present": false,
  "detected": true,
  "signals": [
    {
      "verb": "integration",
      "noun": "api"
    },
    {
      "verb": "(surface)",
      "noun": "api"
    }
  ],
  "message": "api-coverage: external-API integration detected without a coverage matrix. Produce COVERAGE.md enumerating the API surface (every capability INTEGRATE or OPT-OUT with a reason) before sealing. Full coverage is the default."
}
```

This run was taken **before** this `COVERAGE.md` existed on disk (`coverage_present: false`), to
show the gate's pre-declaration state for contrast. Re-run after this file was written:

```json
{
  "block": false,
  "passed": true,
  "coverage_present": true,
  "matrix": "COVERAGE.md",
  "counts": {
    "surface": 0,
    "integrate": 0,
    "optout": 0
  },
  "none_declared": true,
  "detected": true,
  "signals": [
    {
      "verb": "integration",
      "noun": "api"
    },
    {
      "verb": "(surface)",
      "noun": "api"
    }
  ],
  "message": "api-coverage: COVERAGE.md declares no external API integration, overriding 2 detected signal(s) — confirm the declaration is accurate"
}
```

`"passed": true` and `"none_declared": true` — the gate accepts this reasoned declaration over the
same two detected signals.

---
*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Plan: 02*
