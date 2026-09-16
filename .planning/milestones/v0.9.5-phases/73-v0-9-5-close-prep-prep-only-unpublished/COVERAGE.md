# Phase 73: External API Coverage Declaration

No external API integration: this phase edits `CHANGELOG.md` only, runs the project's own
tooling (`uv`, `tox`, `pytest`, `black`, `mypy`, `ruff`, `sphinx-build`, including Sphinx's own
`linkcheck` builder), pushes the milestone branch once and dispatches the project's own `ci.yml`
once (D-12), measures a trial merge with `git merge-tree` (D-09), and writes planning evidence.

## Detector result

Plan-time detector run, recorded verbatim. Scope: the concatenated bodies of every
`73-0*-PLAN.md` in this phase directory, plus
`node /home/yuta/Documents/typsphinx/.claude/gsd-core/bin/gsd-tools.cjs query roadmap.get-phase 73` — the same scope the seal-time
`api-coverage.verify-pre` gate re-runs.

```json
{"detected":true,"signals":[{"verb":"integration","noun":"api","snippet":"contains: 'No external API integration: '"},{"verb":"(surface)","noun":"api","snippet":"| worktree → origin, GitHub API, PyPI (read-only) | `git ls-remote`, `gh release/run/pr list`, `curl` status probes; no "}],"terms":{"verbs":["integrate","integrates","integrating","integration","wrap","wraps","wrapping","connect","connects","connecting","consume","consumes","consuming","wire","wires","wiring","onboard","onboarding","adopt","adopts","adopting"],"nouns":["api","apis","sdk","sdks","rest","graphql","grpc","endpoint","endpoints","oauth","oauth2","webhook","webhooks","mcp"]}}
```

`detected: true`, with two signals. Neither is an integration:

1. **`verb: "integration", noun: "api"`, snippet `contains: 'No external API integration: '`.**
   This is `73-02-PLAN.md`'s own frontmatter `must_haves.artifacts` entry naming this very
   `COVERAGE.md` file's required opening line — the declaration this file provides. It is prose
   *about* the detector's own false-positive shape, quoting the exact sentence this document must
   open with, not a description of an API this phase integrates. Both Phase 69's and Phase 71's
   `COVERAGE.md` name the identical pattern: a bare integration-verb-plus-API-noun detector
   matching words that describe the detector itself.

2. **`verb: "(surface)", noun: "api"`, snippet `\| worktree → origin, GitHub API, PyPI (read-only) \| ...`.**
   This is `73-02-PLAN.md`'s own `<threat_model>` "Trust Boundaries" table row, which names
   `GitHub API` and `PyPI` explicitly as **read-only** boundaries this phase's plans cross with
   `git ls-remote`, `gh release/run/pr list`, and `curl` status-code probes. The row's own text
   states "no write crosses" that boundary — it is a security-review artifact documenting the
   absence of a write path to those services, not a description of a service this phase
   integrates, wraps, connects to, or consumes as a client.

## What the phase's network use actually is

- `git fetch`/`git ls-remote` against `origin` (this repository's own remote), and one
  fast-forward `git push` of the milestone branch (73-04).
- `gh workflow run CI` once (73-04), dispatching this project's own `ci.yml` — never
  `release.yml` and never `update-pin.yml`, both of which are named in the plans only to forbid
  them.
- Read-only `gh run list`/`gh run view`, `gh release list`, `gh pr list`, and one
  `gh api .../branches/main/protection` call (73-02, 73-04, 73-05) — all against this project's
  own GitHub repository, never a third party.
- Four `curl -sS -o /dev/null -w '%{http_code}'` status-code probes of
  `pypi.org/pypi/typsphinx/<version>/json` (this phase's own package's public metadata endpoint,
  read-only, no authentication, no payload, for versions `0.9.2`, `0.9.3`, `0.9.4` and `0.9.5`) —
  never an upload, and never any endpoint other than this project's own package page.
- Sphinx's own `linkcheck` builder (`tox -e linkcheck`) requesting the documentation's own
  outbound links — a read-only check of URLs the project's own docs already cite, run by a
  builder Sphinx ships, not a client this phase writes.
- `uv` fetching only what `uv.lock` already pins — no new dependency is added this phase.

`release.yml` and `update-pin.yml` are named in the plans only to forbid them; neither is
triggered by anything this phase does.

## Why this file exists

The seal-time `api-coverage.verify-pre` gate re-runs the same detector over plan prose that is
unavoidably dense with `gh`, workflow, and API-adjacent wording — CI dispatch, release-list
probes, tag probes, a Trust Boundaries table naming "GitHub API" and "PyPI", and this very
COVERAGE.md's own required declaration sentence quoted inside `73-02-PLAN.md`'s frontmatter. That
density is exactly the false-positive surface a bare integration-verb-plus-API-noun detector is
prone to matching on (Phase 69's and Phase 71's `COVERAGE.md` recorded the identical hazard for
their own `gh`-and-workflow-dense plan prose, and Phase 61's before them). This file meets that
detection with a reasoned declaration — naming each signal and explaining why it is not an
integration — rather than a fabricated capability matrix. A matrix for an API this phase does not
touch would be worse than no matrix.

## Seal-time gate result

```
$ node /home/yuta/Documents/typsphinx/.claude/gsd-core/bin/gsd-tools.cjs check api-coverage.verify-pre .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished
```

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
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 02*
