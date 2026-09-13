# Phase 65: External API Coverage Declaration

No external API integration: this phase swaps one dev-extra package name (`tox-uv-bare` → `tox-uv`)
in `pyproject.toml` and `tox.ini`, regenerates `uv.lock` with `uv lock`, inverts one existing static
test in `tests/test_toolchain_config_gate.py`, and then runs the project's own tooling: `uv`, `tox`,
`pytest`, `ruff`, `black`. It pushes the milestone branch once as a fast-forward and dispatches the
project's own CI workflow once (`ci.yml`, never `release.yml`). It writes planning evidence under
this phase directory. It introduces no third-party API client, SDK, HTTP integration or webhook, and
touches no `typsphinx/` source file.

Plan-time detector result, recorded verbatim. It ran over the concatenated bodies of `65-01-PLAN.md`
and `65-02-PLAN.md` plus the ROADMAP Phase 65 section (`roadmap.get-phase 65`), which is the same
scope the seal-time gate re-runs:

```json
{"detected":false,"signals":[],"terms":{"verbs":["integrate","integrates","integrating","integration","wrap","wraps","wrapping","connect","connects","connecting","consume","consumes","consuming","wire","wires","wiring","onboard","onboarding","adopt","adopts","adopting"],"nouns":["api","apis","sdk","sdks","rest","graphql","grpc","endpoint","endpoints","oauth","oauth2","webhook","webhooks","mcp"]}}
```

**What this phase's network use is.**
- **Registry fetches.** `uv lock`, `uv sync` and the D-03 control venv's `uv pip install` fetch three
  already-vetted packages from PyPI (`tox-uv`, `tox-uv-bare`, `uv`). All three were in this
  repository's lock before Phase 45.2, and their legitimacy is recorded in `65-01-PLAN.md`'s threat
  model (T-65-SC).
- **GitHub calls.** Plan 65-02 runs one `git push`, one `gh workflow run CI --ref
  gsd/v0.9.3-toolchain-and-dependency-update-repair`, and read-only observation through `gh run
  list`, `gh run view` and `gh run watch` against this project's own repository.

That is package installation and the project's own CI, not a service integration. `release.yml` is
named in the plans only so that it can be forbidden.

**Why this file exists although the detector did not fire.** Phase 57's and Phase 64's plan-time
runs also returned `detected: false`. This declaration means a later re-run that matches wording
about the detector itself meets a reasoned statement, not a fabricated capability matrix.

---
*Phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves*
*Written by the planner at plan time (2026-09-12)*
