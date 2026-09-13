# Project Research Summary

**Project:** typsphinx — milestone v0.9.3 "Toolchain and dependency-update repair"
**Domain:** Nix/CI developer-toolchain maintenance for a mature Python package (no product/runtime code)
**Researched:** 2026-09-02
**Confidence:** MEDIUM-HIGH

> **Provenance note.** This file was written by the orchestrator, not by `gsd-research-synthesizer`.
> The synthesizer read all four research documents and returned a complete synthesis, but its
> `Write` call was refused by a harness guardrail ("Subagents should return findings as text, not
> write report files"), so it could not persist the file itself. Its returned synthesis, the four
> source documents, and the orchestrator's own scoping measurements are the inputs here. The four
> researchers' own files (`STACK.md`, `FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md`) were written
> normally and are unaffected.

## Executive Summary

This is a toolchain and CI maintenance milestone with no product or runtime code changes. It repairs
NixOS-local execution — where `ruff`, `tox -e py312`, `.venv/bin/uv` and tox's downloaded CPython all
die on the stub loader — by adding a `buildFHSEnv` wrapper and per-command shims to `flake.nix`; it
reverts `tox-uv-bare` to `tox-uv` once that wrapper makes the revert safe; it repairs the
dependency-update path so dependabot PRs are actually tested; and it disposes of two long-stale
dependabot PRs on their merits.

The single most consequential architectural finding is that **Linux namespaces are inherited across
`fork`/`exec`**. Only the top-level entrypoints a human or CI types directly need FHS shims
(`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`); everything `tox` spawns beneath them — the
`uv-venv-lock-runner`, `.venv/bin/uv`, the downloaded CPython, each `.tox/<env>/bin/*` — inherits the
sandbox for free. That collapses the implementation from "shim every tool" to one shared
`buildFHSEnv` derivation plus a handful of thin `writeShellScriptBin` wrappers, and it means
`CLAUDE.md`'s existing worktree procedure (`uv sync`, then everything through `uv run`) carries FHS
into every downstream command without a single documented command string changing.

The second consequential finding **changed this milestone's scope after it was set**. The milestone
was scoped with a custom GitHub Actions workflow that would run `uv lock` on dependabot PRs and push
the result back. Two of the four researchers independently surfaced that Dependabot has supported
`package-ecosystem: "uv"` natively since GA on 2025-03-13, which makes that workflow unnecessary.
The orchestrator re-verified this against primary sources rather than accepting the researchers'
prose, the owner approved the change on 2026-09-02, and `PROJECT.md`'s Current Milestone section now
carries an `AMENDED` block recording it. **This document reflects the amended scope**; the custom
workflow is retained only as a fallback. The main risks now are that the milestone can leave the
maintainer's machine green while CI or another contributor's machine differs, that a fix might be
"proven" on something other than a real dependabot PR, and that `flake.nix` becomes load-bearing
while still carrying zero CI coverage.

## Key Findings

### Recommended Stack

Everything needed already exists in the pinned nixpkgs and in GitHub's own dependabot support; this
milestone adds **no new runtime dependency and no new third-party GitHub Action** under the amended
scope. The nix facts below were read directly from nixpkgs source at master on 2026-09-02, not
recalled.

**Core technologies:**

- **`pkgs.buildFHSEnv`** — the FHS sandbox. It is a plain **alias for `buildFHSEnvBubblewrap`**; that
  is the name to write. `buildFHSEnvChroot` was **removed** from nixos-unstable (throw-alias added
  2026-05-21) and referencing it hard-fails flake evaluation.
- **`writeShellScriptBin` per-command shims** — the `pkgs.steam-run` idiom: one shared
  `buildFHSEnv` with `runScript = exec "$@"`, then `map` a list of command names into thin wrappers
  that resolve `.venv/bin/<tool>` and `exec` the absolute path through the sandbox. One rootfs
  derivation, N cheap wrappers.
- **`lib.optionals` / `lib.optionalAttrs` on `stdenv.hostPlatform.isLinux`** — the darwin guard.
  Nix's laziness means the `buildFHSEnv` call is never evaluated on the two darwin systems
  `flake.nix` declares. This mirrors nixpkgs' own `flake.nix`.
- **`tox-uv`** — releases in **exact version lockstep** with `tox-uv-bare` (verified against the PyPI
  JSON API), and `tox-uv == tox-uv-bare + uv`. The revert is a drop-in package-name swap that keeps
  the existing `>=1.35,<2` range; `tox.ini`'s `~=` form must be preserved for the same ini-parser
  reason as before.
- **`package-ecosystem: "uv"` in `.github/dependabot.yml`** — a configuration change, not a new
  workflow.

**Do not add:** a lockfile-regeneration workflow, `git-auto-commit-action`, a PAT or deploy key,
`pull_request_target` handling, `nix-ld` (out of repository control), `autoPatchelfHook`/`patchelf`
hooks (wrong lifecycle — they must re-run after every `uv sync`), `pkgs.ruff` (version drift against
the binding "must report 0.15.20" constraint), or a `nix` CI job (CI is deliberately unchanged).

**Noted but out of scope:** `astral-sh/setup-uv`'s moving major tags ended at `v8` when immutable
releases began; current is `v10.0.1` while this repo's eleven steps are on `@v7`. Recorded as a fact,
not as work — CI stays unchanged this milestone.

### Expected Features

**Must have (table stakes):**

- Every `tox` environment and every documented bare command (`pytest`, `ruff check .`,
  `black --check .`, `mypy typsphinx/`) runs to completion on the maintainer's NixOS machine.
- The shims resolve the project's own `.venv` binaries, so local and CI run identical versions.
- Dependabot PRs arrive with `pyproject.toml` and `uv.lock` updated together, so the eleven
  `uv sync --locked` steps stop refusing them and tests actually run.
- The dependency-update fix is demonstrated on a **real dependabot PR**, not a hand-made branch.

**Should have:**

- The manual per-worktree `ln -sf` / `patchelf` step disappears entirely rather than becoming
  conditional — it is the step Phase 38-07 forgot, producing a 45-test false alarm.
- Documentation describes the landed shape, since no Nix-ecosystem convention exists for making a
  shim self-announcing (a runtime banner would corrupt tool output that CI and pytest parse).

**Defer / anti-features:**

- A custom lockfile-regeneration workflow — strictly more moving parts than the ecosystem switch,
  with failure modes the switch does not have. Fallback only.
- System-wide `nix-ld` — outside this repository, and already declined by this project's own D-03/D-18.
- `@dependabot recreate` on #123/#128 — it re-runs under the ecosystem the PR was *opened* with
  (`pip`), so it cannot fix them.
- Trimming `glibcLocales` to shrink the FHS closure — considered and dropped during scoping; the
  0.26 GiB increment is 0.2% of a 136 GiB store, and the override costs an overlay plus loss of
  binary-cache hits.

### Architecture Approach

Two independent tracks. The devShell stays `mkShell` (both alternatives were falsified by
measurement during scoping), and the FHS is exposed as PATH command shims from that shell. On the CI
side nothing about NixOS applies at all — GitHub's runners have a real loader — so the dependabot
work shares no implementation with the FHS work.

**Major components:**

1. **One shared `buildFHSEnv` derivation** in `flake.nix`, Linux-guarded — responsibility: provide a
   real `/lib64/ld-linux-x86-64.so.2` so generic-linux ELFs execute.
2. **Thin per-command shims** on the devShell's PATH — responsibility: resolve `.venv/bin/<tool>` by
   walking up from `$PWD` (never a hardcoded path, never a bare name), then `exec` the absolute path
   through the sandbox.
3. **`pyproject.toml` + `tox.ini` pin swap** — responsibility: return to the upstream `tox-uv`
   package now that its bundled `uv` wheel can execute.
4. **`.github/dependabot.yml` ecosystem switch** — responsibility: have dependabot maintain
   `uv.lock` alongside `pyproject.toml`.
5. **Documentation** in `CLAUDE.md`, `tox.ini` and `flake.nix` — responsibility: describe the landed
   mechanism and retire the manual shim guidance.

### Critical Pitfalls

1. **`tox-uv`'s discovery order is a different code path from the one the scoping measurement
   printed.** `tox-uv` resolves `TOX_UV_PATH` → bundled `uv` wheel → `PATH`, while the recorded
   measurement showed `uv.find_uv_bin()`. The real `tox -e type` / `-e lint` / `-e py312` / `-e py313`
   runs did pass inside FHS, so the mechanism is exercised — but the **outside-FHS control did not
   isolate the uv path** (it failed earlier, on `.venv/bin/python3`). Take an isolated control before
   claiming the revert is safe.
2. **Shim self-recursion.** A shim that resolves its target by bare name re-enters itself. Resolve an
   absolute, un-shadowable path before entering the sandbox. A one-off `--version` smoke test does
   not catch this.
3. **Version skew hidden behind exit 0.** Verification must assert that `ruff` reports exactly
   **0.15.20** — the `uv.lock` version — not merely that the command succeeded. nixpkgs' `ruff` is
   0.15.14 and would lint differently.
4. **Ordering: proving the dependency fix before disposing of #123/#128.** Closing them first removes
   the only real dependabot PRs to test against and forces the hand-made-branch shortcut the source
   todo explicitly rejects. Note also that neither PR exercises the grouped `sphinx-typst-stack`
   update.
5. **A green maintainer machine is not a green project.** CI holds lint authority because only CI
   reaches the Windows and macOS lanes, and locale-dependent failures are a recorded CI-only defect
   class. Whether `buildFHSEnv`'s `/etc` and locale bind behaviour reproduces or *masks* that class
   is genuinely unverified and must be measured early.

**If the fallback custom workflow is ever reached for**, its own pitfalls stand and are all specific
to it: dependabot-triggered `pull_request` runs get a **forced read-only `GITHUB_TOKEN`** regardless
of any `permissions:` block; `GITHUB_TOKEN`-authored pushes do not retrigger CI, so the workflow can
report success while the PR's checks stay stale; and dependabot force-pushes over commits on its own
branches unless the message carries `[dependabot skip]`.

## Implications for Roadmap

Two tracks. Within each, ordering is strict; across them, there is no dependency.

### Phase A1: FHS wrapper and command shims in `flake.nix`

**Rationale:** Nothing else in the local track is safe until this is proven — reverting the `tox-uv`
pin first reintroduces exactly the defect QUA-04 avoided.
**Delivers:** a Linux-guarded `buildFHSEnv` plus shims for the top-level entrypoints; the manual
per-worktree shim step retired from `CLAUDE.md`.
**Addresses:** every table-stakes item in the local track.
**Avoids:** pitfalls 2, 3 and 5. Must assert exact tool versions, must resolve absolute paths, and
must measure `$HOME` / `/etc` / locale passthrough rather than assume it.

### Phase A2: `tox-uv-bare` → `tox-uv` revert

**Rationale:** depends on A1's proof.
**Delivers:** `pyproject.toml` and `tox.ini` on the upstream package, `uv.lock` regenerated.
**Uses:** the verified version lockstep and the preserved `~=` ini form.
**Avoids:** pitfall 1 — its primary verification gate is printing the `uv` binary `tox` actually
resolves from inside a real tox run, with an isolated outside-FHS control.

### Phase B1: `package-ecosystem: "pip"` → `"uv"` in `.github/dependabot.yml`

**Rationale:** independent of A1/A2; CI never touches NixOS.
**Delivers:** dependabot maintaining `uv.lock` alongside `pyproject.toml`.
**Open questions to close here:** whether dependabot's stated **v0.11** uv support handles a
`uv.lock` at `version = 1, revision = 3` written by a 0.12.x uv (which `ci.yml`'s
`version: "latest"` installs); and whether the `sphinx-typst-stack` group, `labels` and
`open-pull-requests-limit` behave identically under the new ecosystem.

### Phase B2: Prove on a real dependabot PR, then dispose of #123 and #128

**Rationale:** strictly after B1 is live. #123 and #128 were opened under `pip`, so they must be
closed and fresh PRs allowed to open under `uv` — and it is those fresh PRs that constitute the
proof.
**Delivers:** an observed passing install step on a real dependabot PR, and a merit-based decision on
each bump.
**Avoids:** pitfall 4. Should explicitly record the grouped-update coverage gap rather than passing
over it.

### Phase C: Documentation follow-through

**Rationale:** last, so it describes what landed rather than what was planned.
**Delivers:** `CLAUDE.md`'s NixOS / worktree section, `tox.ini`'s `tox-uv-bare` rationale comment,
and `flake.nix`'s structure notes brought in line.

### Phase Ordering Rationale

- A1 → A2 is a hard dependency: the pin revert is only safe once the sandbox is proven.
- B1 → B2 is a hard dependency: the proof requires PRs that only exist once B1 is live.
- Track A and Track B share no files and no mechanism, so they can be planned and executed in
  parallel.
- C is last on both tracks so the documentation describes the landed shape.

### Research Flags

Phases likely needing deeper research or an explicit experiment during planning:

- **A1** — `buildFHSEnv`'s `$HOME` / `TMPDIR` / `/etc` / locale passthrough for this project's exact
  invocation, and whether the shim PATH is reachable in a freshly created worktree before
  `direnv allow` has run there (and whether the harness's non-interactive Bash calls trigger direnv's
  hook at all). Both are genuinely unverified; neither should be asserted.
- **B1** — the uv v0.11 / v0.12 lock-revision compatibility question, and grouped-update behaviour
  under the `uv` ecosystem. Measure against the live API, do not infer.

Phases with standard patterns (research can be skipped):

- **A2** — a mechanical package-name swap with a verified lockstep relationship.
- **C** — documentation only.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | nixpkgs facts read from source at master; PyPI and GitHub facts from live APIs |
| Features | MEDIUM-HIGH | Dependabot `uv` support confirmed by GitHub's changelog, GitHub's supported-ecosystems table and Astral's own docs; the edge-case issue list is a live tracker and may move |
| Architecture | MEDIUM | Namespace inheritance and the `steam-run` shim idiom are HIGH; env/locale passthrough and worktree PATH reachability are UNVERIFIED and flagged as experiments |
| Pitfalls | MEDIUM-HIGH | Repo-specific facts read directly; GitHub token/trigger behaviour from official docs cross-checked; `buildFHSEnv` sandbox internals LOW and labelled as such |

**Overall confidence:** MEDIUM-HIGH — the core mechanisms are verified end to end on a real worktree
by the orchestrator's own scoping measurements; the runtime behaviours flagged UNVERIFIED must be
closed during execution rather than assumed.

### Gaps to Address

- **`buildFHSEnv` environment passthrough** (`$HOME`, `TMPDIR`, `/etc`, locale) for this project's
  exact invocation — no source measures it in this shape. Measure early in A1; it bears on `uv`'s
  cache and python-install directories and on this repo's locale-dependent CI-only defect class.
- **Worktree shim reachability before `direnv allow`** — measure in A1 with a fresh worktree.
- **uv v0.11 vs 0.12 lock-revision compatibility** for dependabot — measure in B1.
- **Grouped `sphinx-typst-stack` behaviour under the `uv` ecosystem** — unconfirmed, and not
  exercised by either #123 or #128. Record the gap explicitly in B2 rather than passing over it.
- **`tox-uv` discovery-order control** — the outside-FHS control did not isolate the uv path.
  Take an isolated control in A2.
- **`flake.nix` has zero CI coverage** and this milestone makes it load-bearing. Accepted
  deliberately (CI unchanged), but it is a new standing risk that should be named in the roadmap
  rather than left implicit.

## Sources

### Primary (HIGH confidence)

- nixpkgs `pkgs/top-level/all-packages.nix`, `aliases.nix`, `doc/release-notes/rl-2611.section.md`,
  `pkgs/build-support/build-fhsenv-bubblewrap/{default.nix,buildFHSEnv.nix}`, and nixpkgs' own
  `flake.nix` (raw fetch, master, 2026-09-02) — `buildFHSEnv` alias, `buildFHSEnvChroot` removal, the
  full argument surface, and the darwin-guard idiom.
- PyPI JSON API for `tox-uv` and `tox-uv-bare` (2026-09-02) — version lockstep and `requires_dist`.
- GitHub Docs, supported ecosystems and repositories (2026-09-02) — the `uv` row: YAML value `uv`,
  supported versions `v0.11`, Version updates ✓, Security updates ✓, Private repositories ✓, Private
  registries ✓, Vendoring "Not applicable". Fetched and parsed by the orchestrator.
- Astral, `astral-sh/uv` `docs/guides/integration/dependabot.md` (read via the GitHub API,
  2026-09-02) — "Dependabot supports updating `uv.lock` files"; its "not yet working" caveat cites
  `astral-sh/uv#2512`, which is **closed** (last updated 2026-04-23).
- GitHub Changelog, "Dependabot version updates now support uv in general availability" (2025-03-13).
- GitHub Docs — Dependabot on Actions (forced read-only `GITHUB_TOKEN`), Dependabot PR comment
  commands, managing PRs for dependency updates (`[dependabot skip]`), securely using
  `pull_request_target`.
- `tox-dev/tox-uv` README — `uv` discovery order (`TOX_UV_PATH` → bundled wheel → `PATH`).
- NixOS Wiki, Packaging/Binaries; nixpkgs manual, `buildFHSEnv`.
- This repository: `PROJECT.md` (`## Current Milestone: v0.9.3`, including the binding measurements
  and the `AMENDED` block), `flake.nix`, `tox.ini`, `pyproject.toml`, `CLAUDE.md`, `.envrc`,
  `.github/dependabot.yml`, `.github/workflows/{ci,docs,drift,release}.yml`, and the two pending
  todos this milestone closes.

### Secondary (MEDIUM confidence)

- `dependabot/dependabot-core` issues #11913, #14416, #14119, #13202, #14004 — uv-ecosystem support
  and open edge cases; a live tracker, so subject to change.
- `nix-community/nix-direnv#496` — FHS-in-direnv looping; corroborates this project's own measurement
  independently.
- `nix-community/nix-ld` README; pydevtools.com "How to use uv on NixOS".
- GitHub Community Discussions #62346, #65321, #55906 — `GITHUB_TOKEN` pushes not retriggering
  workflows.
- Boost Security Labs, "Weaponizing Dependabot: Pwn Request at its Finest".
- NixOS Discourse "Simple uv usage"; the `pkgs.steam-run` prior art.

### Tertiary (LOW confidence)

- browniebroke.com (2024-10-02) and brtkwr.com (2025-09-15) — worked dependabot/`uv.lock` examples.
  The 2024 post predates native GA support and its action versions are stale; useful only as a record
  of the superseded workaround's shape.
- `NixOS/nixpkgs#31104` — `buildFHSUserEnv` inside a Nix build sandbox. A different context from this
  milestone's interactive-shell use; flagged as an analogy, not a hit.
- General `buildFHSEnv` runtime-environment behaviour (`HOME`, `TMPDIR`, `/etc`, locale) — **no source
  found** that measures it in the command-shim-from-an-outer-`mkShell` shape used here. Treat as
  unverified until measured.

---
*Research completed: 2026-09-02*
*Ready for roadmap: yes*
