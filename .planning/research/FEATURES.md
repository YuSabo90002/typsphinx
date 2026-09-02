# Feature Research

**Domain:** Toolchain/CI maintenance for a mature, PyPI-published Python package (Sphinx extension) — NixOS-local dev-environment execution + dependabot/lockfile hygiene
**Researched:** 2026-09-02
**Confidence:** MEDIUM-HIGH (NixOS ecosystem claims verified against official nixpkgs manual + community sources; dependabot claims verified against GitHub's own changelog and Astral's official docs, both dated; some blog-post-sourced tradeoff claims are MEDIUM only)

This is a maintenance milestone on an already-shipped product — there are no end-user "features" in
the usual sense. "Table stakes / differentiators / anti-features" below are read as: what this
milestone must deliver to call itself done, what would be nice but isn't required, and what looks
tempting but should be explicitly rejected. Every item is cross-checked against the **binding
measurements already taken during scoping**, recorded in `PROJECT.md`'s Current Milestone section —
where research would suggest something PROJECT.md has already measured false, that is called out
rather than re-proposed.

## Feature Landscape

### Table Stakes (This Milestone Must Deliver These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| NixOS-local execution of generic-linux-ELF tools (`ruff`, `tox`'s downloaded CPython, `.venv/bin/uv`) | The milestone's stated goal is "every lint/type/test lane actually runs on the maintainer's NixOS machine" — currently `ruff check .` and `tox -e py312` both hard-fail with the stub-loader rejection (`.planning/todos/pending/2026-08-11-...md`, reproduced as recently as 2026-08-22) | MEDIUM | Already decided: `buildFHSEnv` wrapper + per-command PATH shims in `flake.nix`, chosen over the three alternatives below. See "Anti-Features" for why the alternatives were not chosen. |
| `flake.nix` devShell stays `mkShell`, not `buildFHSEnv`'s `.env` | PROJECT.md's binding measurements (2026-09-02): `buildFHSEnv`'s `.env` as a devShell does **not** put you inside FHS under `nix develop` *or* direnv — `ld-linux-x86-64.so.2` still resolves to `stub-ld` either way; a `shellHook` that `exec`s into the FHS wrapper doesn't work either (`nix develop` never runs the hook at all; under direnv the `exec` only replaces nix-direnv's capture subshell) | — | Already measured, not a research question — recorded here only so the shim design doesn't silently regress toward either rejected shape. Confirmed independently in the wild: `nix-community/nix-direnv#496` reports FHS-env-in-devShell interacting badly with direnv (infinite loop), consistent with "this combination is fragile," MEDIUM confidence (community issue, not official doc). |
| `flake.nix` per-system guard for `buildFHSEnv` | `buildFHSEnv` is Linux-only (binding measurement); `flake.nix` already declares two darwin systems (`x86_64-darwin`, `aarch64-darwin`) in `forAllSystems` | LOW | Structural — `lib.optionalAttrs`/`pkgs.stdenv.isLinux` style guard so darwin's `devShells.default` doesn't try to evaluate a Linux-only builder. |
| Shims resolve the project's own `.venv`/`uv.lock` versions, not nixpkgs' | Binding measurement: `ruff --version` must report `0.15.20` (the locked version), not nixpkgs' `0.15.14`, or local and CI lint diverge silently | MEDIUM | This is the concrete reason nixpkgs-provided `ruff` (todo's candidate #1) was not chosen as the whole answer — see Anti-Features. The shim must `exec` into the FHS sandbox and then invoke `.venv/bin/<tool>` / `.tox/<env>/bin/<tool>`, not a nix-store binary. |
| `tox-uv-bare` → `tox-uv` revert | QUA-04's original constraint (the bundled `tox-uv` `uv` wheel can't exec on NixOS) is dissolved once the FHS wrapper makes `uv.find_uv_bin()` resolve `.venv/bin/uv` successfully — already re-verified per binding measurement ("`tox -e type`/`-e lint`/`-e py312`/`-e py313` are all green with it") | LOW | Pure dependency + one `requires =` line + comment removal in `tox.ini`, `pyproject.toml`. Depends on the FHS/shim feature landing first — this revert has no independent value if the ELF-execution problem isn't solved. |
| `uv.lock` stays in sync so dependabot PRs actually run CI | Currently **100% of dependabot pip-ecosystem PR jobs fail** at the `uv sync --extra dev --locked` step across all eleven call sites, on every OS, because dependabot edits `pyproject.toml` and never touches `uv.lock` (`.planning/todos/pending/2026-08-16-...md`, measured 2026-08-16 on both open PRs) | LOW–MEDIUM | **The dominant real-world fix as of 2025–2026 is switching `dependabot.yml`'s `package-ecosystem` from `"pip"` to `"uv"`**, not any custom regeneration workflow — see below. GitHub shipped native `uv` support (reads `pyproject.toml` **and** `uv.lock` together, updates both in the same commit) to General Availability **2025-03-13** ([GitHub Changelog](https://github.blog/changelog/2025-03-13-dependabot-version-updates-now-support-uv-in-general-availability/), HIGH confidence — GitHub's own changelog). Confirmed current by [Astral's own integration guide](https://docs.astral.sh/uv/guides/integration/dependabot/) (`package-ecosystem: "uv"`, HIGH confidence — first-party). This directly satisfies the "ecosystem-native support" branch of the research question and should be the primary candidate, ahead of the todo's own candidate #1 (a custom regenerate-and-push workflow). |
| `--locked` stays in every CI step | Explicitly the thing NOT to sacrifice — dropping it was the todo's own candidate #3, filed "so it is explicitly rejected rather than silently rediscovered" | — | Confirmed correct by research: native `uv` ecosystem support makes keeping `--locked` free (the lockfile arrives already regenerated in the same PR commit), so there is no remaining reason to weaken it. |
| Existing `sphinx*`/`docutils*`/`typst*` PR grouping keeps working | The `groups:` block in `dependabot.yml` is a general dependabot.yml feature, not a `pip`-ecosystem-specific one | LOW | `groups:` config syntax (patterns/exclude-patterns) is unchanged when switching `package-ecosystem` from `pip` to `uv` — confirmed by example configs in multiple 2025-era migration write-ups (MEDIUM confidence, blog-sourced, but consistent across three independent posts: browniebroke.com, brtkwr.com, pydevtools.com). |
| Disposal of #123 (`ruff <0.17`) and #128 (`docutils <0.24`) on their merits, proven on a real dependabot PR | Explicit milestone target; PROJECT.md's binding measurement: "must be proven on a real dependabot PR... A hand-made branch carrying a fresh `uv.lock` does not count" | LOW (mechanically) / MEDIUM (judgment) | Switching the ecosystem does not retroactively fix PRs already open under the old `pip` config — #123/#128 will need either closing + a fresh dependabot run under the `uv` ecosystem, or `@dependabot recreate` (see Anti-Features/dependencies note below for why `recreate` alone is not sufficient here). |
| `CLAUDE.md`, `tox.ini`'s `tox-uv-bare` comment, `flake.nix`'s own structure notes updated | Explicit milestone target ("Documentation follow-through") | LOW | Mechanical once (a)–(d) land; the existing `tox.ini` comment block explaining why `-bare` was needed becomes actively misleading once reverted and must be replaced, not just deleted silently (future readers will otherwise wonder why the comment vanished). |

### Differentiators (Nice to Have, Not Required for This Milestone)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Discoverability convention for the shims (a banner/comment marking that `ruff`/`uv`/`tox` on `PATH` are FHS-wrapped, not the raw binary) | Prevents a future maintainer (or a future Claude session) from being confused about why `which ruff` doesn't point at `.venv/bin/ruff` | LOW | No single established convention was found in the wild for this specific case (see Research Notes below) — the practical answer is a `flake.nix` comment plus the `CLAUDE.md` documentation bullet already scoped in, not a runtime banner. A runtime banner on every invocation (e.g., `echo` before `exec`) would pollute tool output (breaks tools that parse `ruff check .` output, e.g. `pytest`/CI log scrapers) and should not be built. |
| An opt-out path for a future non-NixOS Linux dev machine that would rather use the raw `.venv` binaries directly | Portability if a second Linux dev machine (non-NixOS) is ever used | LOW | Comes essentially for free: `buildFHSEnv`-produced shims only take effect when they resolve first on `PATH` inside the nix devShell; a shell outside `nix develop`/direnv (or `direnv deny`) already gets the raw `.venv` binaries unmodified — no extra design needed, just worth stating in the `CLAUDE.md` bullet. |
| `dependency-type` (dev vs. production) grouping under the `uv` ecosystem | Would let dev-only bumps (e.g. `ruff`, `mypy`) be grouped/scheduled separately from runtime deps (`sphinx`, `docutils`) | MEDIUM, and **currently incomplete upstream** | `dependabot/dependabot-core#13202` (open as of this research): under the `uv` ecosystem, dependabot currently treats **all** dependencies as "production" regardless of whether they're declared under `[dependency-groups]`/`optional-dependencies.dev` — so the existing `sphinx*`/`docutils*`/`typst*` pattern-based grouping still works, but a dev/prod split does not. Not worth pursuing this milestone; the existing pattern-based groups are unaffected and sufficient. |
| `cooldown:` config synced to `uv lock --upgrade`'s `exclude-newer`, if the project ever adopts `exclude-newer` | Astral's docs flag this as a real failure mode: a mismatched `cooldown` produces dependabot PRs `uv` cannot actually lock | LOW | Not applicable today — the project's `uv.lock`/`pyproject.toml` do not currently set `exclude-newer` (not found in either file), so this is a documented tripwire for later, not a gap now. |

### Anti-Features (Commonly Proposed, Should Be Explicitly Rejected Here)

| Feature | Why Proposed | Why Problematic | Alternative |
|---------|---------------|------------------|-------------|
| System-wide `programs.nix-ld` NixOS module | The single most common fix for "generic-linux binary won't run on NixOS" in every NixOS wiki/blog on the topic — a shim at `/lib64/ld-linux-x86-64.so.2` that reads `NIX_LD`/`NIX_LD_LIBRARY_PATH` and fixes the *entire class* of unpatched binaries machine-wide | Already ruled out by this project's own prior decision: the todo explicitly frames it as "a system-level (not project-level) configuration change outside this repository's control" (D-03/D-18 precedent — the exact category D-18 already declined when it rejected `TOX_UV_PATH` in favor of a portable fix). It fixes the maintainer's one machine but leaves `flake.nix` non-self-contained for any other NixOS user/CI runner. | Per-project `buildFHSEnv` wrapper (already chosen) keeps the fix inside the repo, applies uniformly to any NixOS user of this flake, and needs no `sudo`/system-config access. |
| Per-project `NIX_LD`/`NIX_LD_LIBRARY_PATH` pinned inside `devShell` (a lighter-weight variant of nix-ld, scoped to the flake rather than the system) | Found in the wild as "Pattern 2" in NixOS uv guides (pydevtools.com) — narrower than a system module, still project-scoped | Not evaluated against this project's binding measurements (the FHS-wrapper decision predates and supersedes this research), and it only fixes the *interpreter*/dynamic-linking half of the problem for binaries it's applied to; it does not, by itself, solve exposing multiple differently-named commands (`ruff`, `tox`, `uv`, the CPython `tox` downloads) as clean PATH shims the way a `writeShellScriptBin`-per-command wrapper around one FHS env does. | Noted for completeness only — not recommended to revisit; `buildFHSEnv` + shims is already the locked choice. |
| `autoPatchelfHook` / a `patchelf` post-`uv sync` hook rewriting each installed binary's ELF interpreter to point at the nix-store glibc loader | nixpkgs' own manual calls `autoPatchelfHook` "the current preferred way to package binaries" for build-time patching, and the todo lists it as candidate #2 | Wrong lifecycle for this use case: `autoPatchelfHook` patches binaries **once, at Nix-build time**, for packages nixpkgs itself builds. Here the binaries arrive from `uv sync`/PyPI wheels, non-deterministically, on every dependency bump — the todo's own text is explicit that this "would need to run after every `uv sync`/`tox` provisioning step (a hook, not a one-shot fix)" — i.e. ongoing maintenance burden that grows with every lockfile change, versus `buildFHSEnv`'s one-time wrapper that needs no re-running. | `buildFHSEnv` wrapper (already chosen) — no per-sync patching step. |
| Swap PyPI-wheel `ruff` for `pkgs.ruff` (nixpkgs-provided) in the devShell | Todo's candidate #1; a version-compatible nixpkgs build exists today (`0.15.14`, inside the project's `ruff>=0.15,<0.16` floor) | Ruled out by binding measurement: the shim must report the *locked* version (`0.15.20`), and nixpkgs' `0.15.14` would silently diverge local lint results from CI/the lockfile the moment nixpkgs' channel and `uv.lock` disagree — a correctness regression disguised as a fix. Same objection applies to any "use nixpkgs' tool instead of the PyPI wheel" substitution for anything pinned in `uv.lock` (mypy, black, pytest, etc., were not proposed but the same argument generalizes). | `buildFHSEnv` executing the *locked* `.venv`/`.tox` binary, not a nix-store alternative. |
| `uv`'s `UV_PYTHON_DOWNLOADS=never` + `UV_PYTHON=<nixpkgs python path>` as the *whole* fix | A real, documented pattern (pydevtools.com "Pattern 2" equivalent) that stops `uv` from auto-downloading a generic-linux CPython build for `tox -e py312`'s missing interpreter | Solves only the interpreter-download half of the problem (the `tox -e py312` companion defect in the todo). It does nothing for wheel-installed compiled binaries like `ruff` that are *not* Python interpreters — so on its own it would leave `ruff check .` exactly as broken as today. Would need to be combined with a second, different mechanism for `ruff` — more moving parts than one `buildFHSEnv` wrapper covering both. | `buildFHSEnv` covering both the interpreter-download case and the wheel-binary case with one mechanism. |
| A GitHub Actions workflow that regenerates `uv.lock` and force-pushes onto each dependabot PR branch (todo's candidate #1, and the pre-2025 community-standard workaround) | Was the standard pattern before GA native `uv` ecosystem support (documented in detail at browniebroke.com, 2024-10-02) — trigger on `pull_request` touching `pyproject.toml`, `uv lock`, commit + push back | Strictly more moving parts than switching the ecosystem: needs a Personal Access Token (the post's own author calls this "isn't ideal") because `GITHUB_TOKEN`-authored pushes don't retrigger downstream CI, needs `contents: write` + `pull-requests: write`, and needs care about re-triggering CI on the pushed commit. Native `uv` ecosystem support (GA since 2025-03-13) produces the regenerated lockfile **in the same commit dependabot itself makes**, with no extra workflow, no extra token, no push-back step. | Switch `package-ecosystem: "pip"` → `"uv"` in `dependabot.yml` (table stakes, above). |
| Abandoning dependabot entirely, making the weekly `drift.yml` job the sole dependency-update path (todo's candidate #2) | Smallest possible diff; `drift.yml` already re-resolves latest allowed versions weekly and is unaffected by this whole class of bug (it runs `uv lock --upgrade` *before* `uv sync --locked`, so its lockfile is current by construction) | Loses per-package PR granularity and reactivity — dependabot can react same-day to e.g. a security advisory on a pinned range; `drift.yml` only samples weekly and files a single dedup'd issue rather than a mergeable, testable PR per bump. Now unnecessary: native `uv` ecosystem support removes the reason this tradeoff was ever on the table. | Keep both: dependabot (fixed via the `uv` ecosystem) for per-bump PRs, `drift.yml` unchanged for its existing weekly "does the newest resolvable set still work" signal — they answer different questions and already coexist without conflict. |
| `@dependabot recreate` alone, without first fixing `dependabot.yml`'s ecosystem | Documented GitHub-native command; closes and reopens a PR fresh against current `main`, and is GitHub's own advertised fix for "stale/conflicted PR" | Recreate re-runs dependabot's update logic **for the ecosystem the PR was originally opened under**. #123/#128 were opened under `package-ecosystem: "pip"`, which does not understand `uv.lock` at all — recreating them under the same (unfixed) config reproduces the identical `uv sync --locked` failure, it does not regenerate `uv.lock`. Only useful *after* `dependabot.yml` is switched to the `uv` ecosystem, and even then a `pip`-ecosystem PR generally needs to be closed and a fresh `uv`-ecosystem PR opened rather than "recreated" in place. | Switch the ecosystem first; then either close #123/#128 and let a fresh `uv`-ecosystem dependabot run open new PRs, or use `@dependabot recreate` only once the config change is live. |

## Feature Dependencies

```
(a) buildFHSEnv wrapper + PATH shims in flake.nix
    └──requires──> mkShell devShell stays as-is (buildFHSEnv used only to build the shim
                    derivations, NOT as the devShell itself — the .env-as-devShell and
                    shellHook-exec shapes are both measured-broken, per PROJECT.md)
    └──requires──> per-system (Linux-only) guard, since flake.nix declares two darwin systems

(b) tox-uv-bare -> tox-uv revert
    └──requires──> (a)  [uv.find_uv_bin() must resolve .venv/bin/uv through the shim before
                         the revert has any effect; reverting first would just reproduce the
                         original QUA-04 failure]

(c) uv.lock stays in sync on dependabot PRs
    ── independent of (a) and (b) — this is a GitHub-side config change (dependabot.yml
       package-ecosystem: pip -> uv), not a NixOS-execution change

(d) Disposal of #123 / #128 on their merits
    └──requires──> (c)  [PROJECT.md: "proven on a real dependabot PR... a hand-made branch
                         does not count" — need a PR that actually ran CI against a
                         dependabot-produced uv.lock]
    ──overlaps with──> (a)/(b) only incidentally: #123 IS the ruff bump, so judging it "on
                        its merits" plausibly wants ruff to actually run locally (via the (a)
                        shim) during evaluation, not just pass CI

(e) Documentation follow-through (CLAUDE.md, tox.ini comment, flake.nix notes)
    └──requires──> (a), (b), (c) settled  [documents the landed shape, not the plan for it]
```

### Dependency Notes

- **(b) requires (a):** the entire reason `tox-uv-bare` existed was that the bundled `tox-uv`
  `uv` wheel is itself a generic-linux ELF unrunnable on NixOS (QUA-04). Reverting the tox
  runner package without first landing the FHS shim would just reproduce the original failure
  under a different package name.
- **(c) is independent of (a)/(b):** it is entirely a `dependabot.yml` config change (switching
  `package-ecosystem` from `pip` to `uv`) plus disposing of the two stale PRs; it requires no
  NixOS-side work and does not depend on the maintainer's local machine at all — this is worth
  stating explicitly because the two problem statements read as related (both are "toolchain
  repair") but share no implementation.
- **(d) requires (c):** proving the fix "on a real dependabot PR" (PROJECT.md's binding
  constraint) needs the ecosystem switch live first, so a genuinely dependabot-authored
  `uv.lock` update exists to observe passing CI on.

## MVP Definition

### Launch With (v0.9.3, per PROJECT.md's already-locked scope)

- [ ] `buildFHSEnv` wrapper + command-name shims (`ruff`, `tox -e py312`, `.venv/bin/uv`, the
  `tox`-downloaded CPython) in `flake.nix`, `mkShell` devShell unchanged — table stakes, blocks
  everything else in this milestone
- [ ] Linux-only guard around the FHS wrapper so the two darwin systems still evaluate
- [ ] `tox-uv-bare` → `tox-uv` revert in `pyproject.toml`/`tox.ini`
- [ ] `dependabot.yml`: `package-ecosystem: "pip"` → `"uv"` (keeps the existing `groups:` block
  as-is; `docutils*`/`sphinx*`/`typst*` patterns are ecosystem-agnostic)
- [ ] Dispose of #123 (`ruff <0.17`) and #128 (`docutils <0.24`) — close and let the fixed
  ecosystem reopen fresh PRs (or judge in place if `@dependabot recreate` proves sufficient once
  the config is live), each bump evaluated on its own merits
- [ ] `CLAUDE.md` NixOS/worktree section, `tox.ini`'s `tox-uv-bare` rationale comment, and
  `flake.nix`'s structure notes updated to describe the landed shape

### Add After Validation (not this milestone, explicitly out of scope per PROJECT.md)

- [ ] A `nix` CI job giving `flake.nix` any coverage — PROJECT.md accepts this as a "new
  standing risk" deliberately, since CI stays unchanged this milestone
- [ ] Pinning `astral-sh/setup-uv`'s eleven `version: "latest"` steps
- [ ] SEED-003 (PEP 735 `[dependency-groups]`) — explicitly stays dormant

### Future Consideration (beyond v0.9.3)

- [ ] `dependency-type` (dev vs. prod) grouping under the `uv` dependabot ecosystem, once
  upstream (`dependabot-core#13202`) actually supports it
- [ ] A `cooldown:` block, only if/when the project adopts `uv lock`'s `exclude-newer`

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| FHS wrapper + shims (a) | HIGH — unblocks all local lint/type/test lanes | MEDIUM | P1 |
| Linux-only guard | HIGH (blocks darwin evaluation otherwise) | LOW | P1 |
| tox-uv revert (b) | MEDIUM — cosmetic/consistency once (a) lands | LOW | P1 |
| dependabot.yml uv ecosystem switch (c) | HIGH — unblocks all future dependency PRs, not just these two | LOW | P1 |
| Dispose of #123/#128 (d) | MEDIUM — clears backlog, validates (c) | LOW–MEDIUM (judgment) | P1 |
| Documentation follow-through (e) | MEDIUM — prevents future confusion/regression | LOW | P1 |
| Shim discoverability banner | LOW | LOW | P3 (rejected — output pollution) |
| dependency-type grouping | LOW (not currently usable upstream) | MEDIUM | P3 |
| `cooldown:` sync | LOW (not applicable — no `exclude-newer` set) | LOW | P3 |

## Research Notes: What Was and Wasn't Found

- **No single named convention exists in the Nix ecosystem for "command shim discoverability."**
  Searches for a formal pattern (banner text, `_REAL` env var escape hatch, etc.) turned up
  nothing established — projects that expose `buildFHSEnv`-wrapped tools under their own names
  typically rely on documentation (a README/CLAUDE.md note) rather than a runtime signal, because
  a runtime banner would corrupt tool output parsed by CI/other tooling (`ruff check .`'s own
  output, `pytest` collection, etc.). This confirms the milestone's existing "Documentation
  follow-through" bullet is the correct mechanism, not a gap to fill with new tooling.
- **`buildFHSEnv` itself only produces one wrapper binary per invocation** (named via its `name`
  attribute, invoking a single `runScript`). Exposing several independently-named PATH commands
  (`ruff`, `tox`, `uv`, `python`) from one FHS sandbox is a composition the maintainer will need
  to build explicitly — e.g. one `writeShellScriptBin "<cmd>"` wrapper per command name that
  `exec`s into the shared FHS derivation and then runs the real command inside it — not something
  `buildFHSEnv` hands you for free. This is a planning-relevant complexity note, not a blocker.
- **GitHub's own "Dependabot supported ecosystems and repositories" reference page did not surface
  `uv` when fetched during this research** (2026-09-02) — likely a caching/mirroring artifact of
  the fetch tool rather than the feature being unsupported, since GitHub's own dated changelog
  post and Astral's current first-party integration guide both independently and consistently
  describe it as GA since 2025-03-13. Flagged here per the quality gate rather than silently
  smoothed over — recommend a direct, fresh confirmation (`gh api` or the live docs page) during
  planning before committing to the ecosystem-switch approach, even though two independent HIGH
  and MEDIUM confidence sources agree.
- **Known open rough edges on the native `uv` dependabot ecosystem**, as of this research (all
  MEDIUM confidence — live `dependabot-core` GitHub issues, not resolved/closed as of the search):
  `dependabot-core#14416` (fails on non-alphabetical `extras` ordering with a
  "Dependency file content did not change" error), `#14119` (fails when a dependency's case
  differs between `pyproject.toml` and `uv.lock`), `#13202` (dev/prod dependency-type split not
  yet implemented — all deps treated as production for grouping purposes), and reports of
  workspace-handling confusion (`#14004`). None of these currently apply to this repository (no
  extras-ordering irregularity, no case mismatches, no workspace, and the existing pattern-based
  `groups:` block doesn't need dependency-type splitting) — noted so planning can watch for them
  rather than be surprised if the switch surfaces one.

## Sources

- [Dependabot version updates now support uv in general availability — GitHub Changelog, 2025-03-13](https://github.blog/changelog/2025-03-13-dependabot-version-updates-now-support-uv-in-general-availability/) — HIGH confidence (GitHub first-party, dated)
- [Using uv with Dependabot — Astral Docs](https://docs.astral.sh/uv/guides/integration/dependabot/) — HIGH confidence (Astral first-party, current)
- [dependabot/dependabot-core#11913 "Support scanning uv.lock for dependencies"](https://github.com/dependabot/dependabot-core/issues/11913) — MEDIUM confidence (upstream issue tracker)
- [dependabot/dependabot-core#14416, #14119, #13202, #14004 — open uv-ecosystem edge cases](https://github.com/dependabot/dependabot-core/issues) — MEDIUM confidence (live issue tracker, unresolved as of research date)
- [Keep uv.lock file up-to-date with Dependabot updates — browniebroke.com, 2024-10-02](https://browniebroke.com/blog/2024-10-02-keep-uv-lock-file-up-to-date-with-dependabot-updates/) — MEDIUM confidence (blog, pre-dates GA native support, useful for the superseded-workaround comparison)
- [Setting up Dependabot for uv projects — brtkwr.com, 2025-09-15](https://brtkwr.com/posts/2025-09-15-dependabot-with-uv/) — MEDIUM confidence (blog, post-GA)
- [Dependabot pull request comment commands — GitHub Docs](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-pull-request-comment-commands) — HIGH confidence (GitHub first-party)
- [nix-community/nix-ld README](https://github.com/nix-community/nix-ld/blob/main/README.md) — HIGH confidence (project's own docs)
- [Packaging/Binaries — official NixOS Wiki](https://wiki.nixos.org/wiki/Packaging/Binaries) — HIGH confidence (official wiki; describes `autoPatchelfHook` as "the current preferred way to package binaries" for build-time patching, and `buildFHSEnv` as "a last resort... for programs that download and run other executables")
- [buildFHSEnv — nixpkgs manual](https://ryantm.github.io/nixpkgs/builders/special/fhs-environments/) — HIGH confidence (official manual mirror; confirms single `runScript`/single wrapper-binary shape)
- [How to use uv on NixOS — pydevtools.com](https://pydevtools.com/handbook/how-to/how-to-use-uv-on-nixos/) — MEDIUM confidence (blog; documents the `NIX_LD`/`UV_PYTHON_DOWNLOADS=never` interpreter-only patterns, explicitly does not cover compiled-wheel binaries like `ruff`)
- [nix-community/nix-direnv#496 "Infinite Looping when entering a flake that has a FHSenv"](https://github.com/nix-community/nix-direnv/issues/496) — MEDIUM confidence (live issue tracker; corroborates PROJECT.md's own direnv+FHS measurement independently)
- `.planning/PROJECT.md` — Current Milestone: v0.9.3 section (binding measurements, 2026-09-02) — this repo's own primary source, treated as ground truth throughout
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — this repo's own primary source
- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — this repo's own primary source
- `.github/dependabot.yml`, `.github/workflows/drift.yml` — this repo's own current state

---
*Feature research for: typsphinx v0.9.3 "Toolchain and dependency-update repair"*
*Researched: 2026-09-02*
