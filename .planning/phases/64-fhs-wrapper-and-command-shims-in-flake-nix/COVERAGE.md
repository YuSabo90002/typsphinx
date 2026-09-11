# Phase 64: External API Coverage Declaration

No external API integration: this phase edits one tracked source file, `flake.nix`. It adds a
Linux-guarded `pkgs.buildFHSEnv` passthrough and seven `pkgs.writeShellScriptBin` command shims.
Everything else it does is run the project's own tooling: `ruff`, `black`, `mypy`, `pytest`,
`sphinx-build`, the tox environments, and the `nix` CLI for flake evaluation. It pushes the milestone
branch once and dispatches the project's own CI workflow once (`ci.yml`, never `release.yml`). It
writes planning evidence under
`.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/`. It introduces no third-party API
client, SDK, HTTP integration or webhook, and touches no `typsphinx/` source file.

Plan-time detector result, recorded verbatim. It ran over the concatenated bodies of `64-01-PLAN.md`
through `64-04-PLAN.md` plus the ROADMAP Phase 64 section, which is the same scope the seal-time gate
re-runs:

```json
{"detected":false,"signals":[]}
```

**What this phase's `gh` usage is.** Plan 64-04 makes these calls against this project's own GitHub
repository:

- one `git push -u origin gsd/v0.9.3-toolchain-and-dependency-update-repair`
- one `gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair`
- read-only observation: `gh run list`, `gh run view` and `gh run watch`

That is the project's own continuous-integration tooling, not a service integration. `release.yml`
is named in the plans only so that it can be forbidden, and it is never triggered.

**Why this file exists although the detector did not fire.** Phase 57's plan-time run also returned
`detected: false`. A later re-run over the finished plan prose then matched self-referential wording
about the detector itself. This declaration means any such re-run meets a reasoned statement rather
than a fabricated capability matrix for an API this phase does not touch.
`64-RESEARCH.md` § "Package Legitimacy Audit" records **zero registry packages** installed, so no
package-legitimacy checkpoint is owed.

---
*Phase: 64-fhs-wrapper-and-command-shims-in-flake-nix*
*Written by the planner at plan time (2026-09-11)*
