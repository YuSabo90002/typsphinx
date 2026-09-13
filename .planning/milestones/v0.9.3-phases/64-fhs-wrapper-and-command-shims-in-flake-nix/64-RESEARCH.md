# Phase 64: FHS Wrapper and Command Shims in `flake.nix` - Research

**Researched:** 2026-09-03
**Domain:** Nix (`pkgs.buildFHSEnv` / bubblewrap sandboxing), `mkShell` devShell PATH composition, git-worktree-aware shell invocation, GitHub Actions dispatch/observation
**Confidence:** MEDIUM-HIGH — the nixpkgs mechanism (etc/HOME/TMPDIR/network passthrough, `/etc/profile` sourcing, PATH-ordering precedence) is now **HIGH confidence, read directly from the pinned nixpkgs source and cross-checked with three live experiments this session**; the exact locale-defect-class interaction (NIX-08) and cold-provisioning timing remain genuinely unmeasured and are flagged LOW/ASSUMED below, to be closed by the phase's own execution, not by this document.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Shim surface**

- **D-01: The shim roster is exactly seven command names — `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`.** This is `research/ARCHITECTURE.md` Pattern 1's six plus `sphinx-build`,
  which `CLAUDE.md:39-40` documents as a bare manual-exercise command
  (`sphinx-build -b typst source build/typst`) and which exists in `.venv/bin` (measured 2026-09-03:
  `sphinx-build 9.1.0`). The phase goal says "every documented bare command", so the roster is
  derived from CLAUDE.md's documented command list, not from the NIX-01 success criterion's shorter
  enumeration. Pattern 2's namespace inheritance means nothing below these seven needs a shim.
  — **Reversibility:** reversible — adding or removing a name is one list entry in `flake.nix`.

- **D-02: The `uv` shim resolves in two steps — `.venv/bin/uv` first, then the nixpkgs `uv` store path — and enters the FHS sandbox either way.** Measured 2026-09-03: `.venv/bin/uv` **does not
  exist today**; `tox-uv-bare` ships no `uv` wheel, so that path only appears after Phase 65's
  revert. Meanwhile `command -v uv` resolves to `/nix/store/…-uv-0.11.25/bin/uv`, a properly linked
  nix binary. A shim demanding `.venv/bin/uv` would therefore fail today and on every fresh clone.
  Both legs are absolute and un-shadowable (the nix store path is fixed at flake-evaluation time), so
  NIX-07's "absolute path, no bare-name resolution, no self-recursion" standard is preserved. Sending
  the nixpkgs leg through the sandbox too is what makes `uv run <tool>` — the mandatory worktree
  idiom — carry FHS into every downstream process, which is what NIX-05 actually depends on.
  — **Reversibility:** reversible — the fallback leg is a few lines and can be dropped once Phase 65
  guarantees `.venv/bin/uv` exists.

- **D-03: The other six shims have no fallback at all — a missing `.venv/bin/<tool>` is a hard, loud failure.** Print a message naming the tool and the directory the upward walk started from,
  then exit non-zero. This is Pitfall 10 / ROADMAP constraint 6 in shim form: degrading to some other
  binary replaces "doesn't run" with "runs but disagrees with CI". `uv`'s two-step in D-02 is the
  single, deliberate, documented exception, and it falls back to a fixed store path rather than to
  whatever `PATH` happens to hold.
  — **Reversibility:** reversible.

**Verification locus**

- **D-04: NIX-01 through NIX-04 are measured in a freshly created git worktree, after the documented provisioning line (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`) — not in the main tree.** Measured 2026-09-03 in the main checkout: `.venv/bin/ruff --version` → `ruff 0.15.20`,
  and `black` / `mypy` / `pytest` / `tox` / `python3` / `sphinx-build` all exit 0, **with no shim
  present**. A main-tree run of SC#1 therefore passes before this phase changes anything. The hazard
  reproduces only where a fresh `uv sync` pulls the current wheels — PROJECT.md's Phase 57 lesson
  ("a main-tree measurement can never detect the hazard") and the 2026-08-22 retraction of the
  earlier "ruff runs here" claim. This also matches NIX-05's own wording ("freshly created git
  worktree") and the project's standing worktree-isolated execution mode.
  — **Reversibility:** reversible.

- **D-05: The NIX-07 rename test and the NIX-08 environment measurement are recorded verbatim in the phase's evidence markdown, and nowhere else.** No new script under `scripts/`, no new `tests/`
  file. Rationale: a pytest test would be permanently skipped on every CI runner (no `nix`, and the
  Windows/macOS lanes could never run it), adding an always-skipped test to the 1548-test suite; and
  a committed shell script is new repository surface this phase does not otherwise need. The project's
  existing evidence convention (the `*-EVIDENCE` / `*-VERIFICATION` family) carries it.
  — **Reversibility:** reversible — a script can be added later if re-measurement becomes routine.

**FHS sandbox environment**

- **D-06: The sandbox passes the caller's environment through; it is not cleared or normalized.**
  `bwrap` does not clear the calling environment by default and `buildFHSEnv`'s generated wrapper
  does not either, so a plain `exec "$@"` entry script is the shape to write. This is load-bearing,
  not stylistic: `CLAUDE.md`'s mandatory `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync` idiom
  only works if the `-u` unsets survive into `uv`, and `docs-pdf` needs `$HOME` to reach
  `~/.cache/typst`.
  — **Reversibility:** reversible.

- **D-07: If `tox -e docs-pdf` cannot reach its `@preview` packages from inside the sandbox, it is fixed inside Phase 64 — not deferred.** Confirm `$HOME` passthrough first, and add `cacert` to
  `targetPkgs` if a cold cache turns out to need TLS. Measured 2026-09-03:
  `~/.cache/typst/packages/preview` already holds nine packages (`codly`, `codly-languages`,
  `mitex`, `gentle-clues`, `fontawesome`, `linguify`, `modern-cv`, `xarrow`, `charged-ieee`), so a
  warm cache likely needs nothing but `$HOME`. SC#2 requires a real PDF (`%PDF` magic bytes, not
  exit 0) and names `docs-pdf` as the one invocation exercising font resolution, subprocess spawning
  and exit-code propagation through the sandbox, so NIX-03 cannot close without it.
  — **Reversibility:** reversible.

- **D-08: If the locale measurement shows the sandbox changing behaviour, record it and stop there.**
  NIX-08 requires the measurement and the record, not a behavioural change. Measured 2026-09-03:
  `LANG=ja_JP.UTF-8` on the maintainer's machine, and this repository has a documented
  locale-dependent "local green, CI red" defect class. Whether the sandbox **reproduces or masks**
  it must be stated explicitly either way; the consequence is written up in Phase 68 (DOC-19 /
  DOC-21). Do **not** pin `LC_ALL` in the shims (it would silently change the maintainer's working
  locale and hide ja_JP-specific behaviour), and do **not** run the 1548-test suite twice under two
  locales in this phase.
  — **Reversibility:** reversible.

**Worktree reachability (NIX-05)**

- **D-09: Reachability rests on session PATH inheritance, and the procedure gains a `command -v` check at its head.** Measured 2026-09-03 in this session: `DIRENV_DIR=-/home/yuta/Documents/typsphinx`,
  `DIRENV_FILE=/home/yuta/Documents/typsphinx/.envrc`, `IN_NIX_SHELL=impure`, and the head of `PATH`
  carries the flake devShell's own store paths (`nodejs-24.16.0`, `pnpm-11.9.0`, `git-2.54.0`,
  `python3-3.13.13`, `uv-0.11.25` — exactly `flake.nix`'s `packages` list). The harness's
  non-interactive Bash calls never fire direnv's prompt hook, so this `PATH` is frozen at session
  start and survives `cd` into a worktree — the shims should be reachable there by inheritance, with
  no per-worktree `direnv allow`. That inheritance does **not** hold for a session launched outside
  the project, which is why the check goes in: confirm `command -v ruff` (and `uv`) points at the
  shim before provisioning. Rejected: a per-worktree `direnv allow` step (irrelevant to the
  non-interactive path that actually runs, and manual work every time) and wrapping the provisioning
  line in `nix develop --command` (it would change `CLAUDE.md`'s mandatory line and ripple through
  every GSD worktree procedure — the opposite of research's "NO other CLAUDE.md wording needs to
  change" success shape).
  — **Reversibility:** reversible — if observation contradicts the inheritance finding, the
  `nix develop --command` wrapper is still available, at the cost of a CLAUDE.md wording change in
  Phase 68.

### Claude's Discretion

- `targetPkgs` contents beyond what measurement forces. Start from the minimal
  `_: [ ]` shape in `research/ARCHITECTURE.md` Pattern 1 and add only what a failing measurement
  demands (D-07's `cacert` being the anticipated case). Note that REQUIREMENTS.md's Out of Scope
  table already forecloses *trimming* `glibcLocales` out of the closure.
- Dropping `pkgs.uv` from the Linux devShell's `packages` so the `uv` shim wins PATH ordering
  (`research/ARCHITECTURE.md` Data Flow calls for this); the darwin branch keeps today's package list
  byte-for-byte.
- Exact wording and exit code of the shim's not-found message, and the shape of the upward `.venv`
  walk.
- Whether the shim list and FHS derivation stay inline in `flake.nix` — research recommends inline
  (the file is 40 lines and single-purpose) and this phase follows that unless the diff argues
  otherwise.
- Plan split granularity, and the name/location of the evidence file(s) D-05 refers to.
- Which SHA the SC#5 CI baseline is dispatched against, beyond it being the phase's pushed tip.

### Deferred Ideas (OUT OF SCOPE)

- **A committed, re-runnable FHS verification script** (e.g. `scripts/verify-fhs-shims.sh` covering
  the rename test, version reconciliation and an environment dump). Considered as D-05's alternative
  and declined for this phase to avoid new repository surface. Worth revisiting if re-measurement
  becomes routine, or as a partial mitigation for ROADMAP constraint 8's zero-CI-coverage risk.
- **Running the full suite under two locales** (`ja_JP.UTF-8` and `LC_ALL=C`) to pre-empt the
  CI-only locale defect class locally. Declined for Phase 64 (roughly doubles the phase's gate time);
  it is a general testing-practice change, not part of this phase's mechanism.
- **Cold-`@preview`-cache behaviour of `docs-pdf` inside the sandbox** — if D-07's investigation shows
  the warm cache is doing the work and TLS/network from inside the sandbox stays unexercised, record
  it rather than manufacture a cold-cache scenario. A follow-up belongs under REQUIREMENTS.md
  § Future Requirements.
- **Reviewed todos, not folded:**
  - `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — matched on the word "ruff"
    only. `CLAUDE.md` and ROADMAP constraint 13 both forbid typing-import modernization this
    milestone.
  - `2026-07-22-add-sphinx-linkcheck-ci-job.md` — matched on tox environment names. It is a workflow
    addition, which ROADMAP constraint 3 excludes by construction.
  - `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — a docs-rendering
    defect, unrelated to this phase's domain.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| NIX-01 | `ruff check .` runs to completion and reports **0.15.20** (`uv.lock:1209-1210`), not nixpkgs' 0.15.14 | Shim shape (Code Examples §1), `uv.lock` line-verified pin, D-02/D-03 two-tier resolution design |
| NIX-02 | `tox -e lint`, `-e type`, `-e py312`, `-e py313` each run to completion | Namespace-inheritance argument (Pattern 2), network-namespace-shared finding (`unshareNet=false`, source-verified) for CPython download |
| NIX-03 | `tox -e cov`, `-e docs-html`, `-e docs-pdf` each run to completion, `docs-pdf` produces a real PDF | `$HOME`/`/etc` bind-mount findings (source-verified: `/home` bound, `/etc/ssl/certs`+`ca-certificates`+`pki`+`fonts` bound from host), D-07's warm-cache measurement |
| NIX-04 | Full 1548-test suite runs with no environment-caused failures | Validation Architecture §, D-04's worktree-only verification locus |
| NIX-05 | Executor in a fresh worktree runs provisioning + every gate, no manual `ln -sf`/`patchelf` | Open Question 1 procedure (Code Examples §4), D-09, live `nix develop path:<worktree>` experiment this session |
| NIX-06 | `flake.nix` evaluates on all four declared systems including both darwin | Open Question 2 procedure (Code Examples §5), live `nix flake check --all-systems` experiment this session |
| NIX-07 | Each shim resolves by absolute, un-shadowable path; rename-test proves no self-recursion | Open Question 5 procedure (Code Examples §6), shim shape source-verified against `pkgs.steam-run` idiom |
| NIX-08 | `$HOME`/`TMPDIR`/`/etc`/locale measured for this invocation shape; locale-defect-class effect recorded | Open Question 6 procedure (Code Examples §7), nixpkgs `etcProfile`/`etcBindEntries` source read |
</phase_requirements>

## Summary

This phase adds exactly one new piece of Nix surface to a 40-line `flake.nix`: a Linux-guarded
`pkgs.buildFHSEnv` derivation with an `exec "$@"` passthrough `runScript`, plus seven
`pkgs.writeShellScriptBin` shims (`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`)
added to the existing `mkShell`'s `packages` list on Linux only. This is the `pkgs.steam-run` idiom,
and it is well-precedented in nixpkgs itself. The milestone-level research (`research/ARCHITECTURE.md`,
`STACK.md`, `PITFALLS.md`) already established the shape; this document goes one level deeper — the
exact nixpkgs mechanics (read from the pinned source, not recalled) and the exact measurement
procedures the phase's own plans will execute for NIX-05, NIX-06, NIX-07 and NIX-08.

Three things were newly established this session, each by a live, isolated experiment (never against
the real `flake.nix` — see the Runtime State Inventory-equivalent note in Open Questions about one
accidental edit, immediately reverted):

1. **`nix develop path:<dir>#default --command <cmd>` works cleanly from a real git worktree** (tested
   against an actual `git worktree add`-created directory in an isolated scratch clone), taking
   ~0.4–0.5s of pure-evaluation overhead, no `--impure` needed, and it picks up **uncommitted edits
   to tracked files** (verified: a dirty, uncommitted change to `flake.nix`'s `description` field was
   visible to `nix flake metadata` without a commit). This directly answers the open question of how
   an executor exercises the just-edited devShell from inside a worktree during the phase's own
   execution, before any commit lands.

2. **`mkShell`'s `packages` list resolves same-named-binary collisions by list order — the earlier
   entry wins `command -v`.** Verified with a throwaway `writeShellScriptBin "uv"` placed before vs.
   after `pkgs.uv` in two sibling devShells: `packages = [ fakeUv pkgs.uv ]` → shim wins;
   `packages = [ pkgs.uv fakeUv ]` → nixpkgs' real `uv` wins. This means D-02's `uv` shim only needs
   to be listed **before** `pkgs.uv` to take effect — dropping `pkgs.uv` (the discretion item) is a
   belt-and-suspenders simplification, not a hard requirement, but it is the safer choice because it
   removes the possibility of a future package-list reorder silently un-shimming `uv`.

3. **The FHS sandbox's environment/filesystem passthrough was read directly from the pinned nixpkgs
   source** (`pkgs/build-support/build-fhsenv-bubblewrap/default.nix` and `buildFHSEnv.nix`, at the
   store path this flake's own `nixpkgs.url` input resolves to), not inferred: `bwrap` is invoked with
   `unshareUser`/`unshareIpc`/`unsharePid`/`unshareNet`/`unshareUts`/`unshareCgroup` all **defaulted
   to `false`** and `privateTmp` **defaulted to `false`**, so the network namespace is shared with the
   host (network-dependent steps — `uv python install` for `-e py312`/`-e py313`, and any cold
   `@preview` fetch — are not blocked by the sandbox itself) and every top-level host directory not
   explicitly excluded (`/nix /dev /proc /etc`, plus `/tmp` only if `privateTmp`) is `--bind`-mounted
   real (writable), **including `/home` and `/tmp`**. A curated `etcBindEntries` list explicitly
   symlinks `resolv.conf`, `nsswitch.conf`, `hosts`, `passwd`, `group`, `localtime`, `zoneinfo`,
   `ssl/certs`, `ca-certificates`, `pki` and `fonts` from the host's real `/etc` into the sandbox's
   `/etc` (via a `/.host-etc` re-bind), with an explicit code comment that `fonts` and `ssl/certs` are
   deliberately taken from the host rather than the FHS closure. `LOCALE_ARCHIVE` is defaulted (not
   overridden) inside the FHS's own `/etc/profile`, which **is sourced** before `runScript` executes
   (`source /etc/profile; exec ${run} "$@"`) — this is the one place environment mutation is not pure
   passthrough: `PATH` is prefixed with `/run/wrappers/bin:/usr/bin:/usr/sbin:` and a handful of
   build-related vars (`XDG_DATA_DIRS`, `NIX_CFLAGS_COMPILE`, `PKG_CONFIG_PATH`, …) are appended to,
   but pre-existing values are preserved via `${VAR:-default}`/`${VAR:+…}` shell idioms, never
   clobbered. `glibcLocales` is unconditionally the first entry of `baseTargetPaths` — it cannot be
   omitted without overriding that list, which matches REQUIREMENTS.md's Out of Scope entry
   forbidding its removal.

**Primary recommendation:** write the `pkgs.steam-run`-idiom FHS derivation plus seven
`writeShellScriptBin` shims exactly as sketched in `research/ARCHITECTURE.md` Pattern 1, with the
upward-`.venv`-walk from D-01/D-03 (not a bare `$PWD/.venv/bin/<tool>`, since `tox.ini:65,73` proves
`docs-html`/`docs-pdf` run with `changedir = docs` — a shim invoked while `$PWD` is `docs/` must still
find `../.venv/bin/<tool>`); measure NIX-05/06/07/08 with the exact command sequences in Code Examples
below, all of which were smoke-tested this session against a scratch clone or the live (unmodified)
repository; and record everything in phase evidence markdown per D-05, using names that do not collide
with the verifier-reserved `64-VERIFICATION.md` (Phase 63 precedent: `63-CI-EVIDENCE.md`,
`63-GREEN-TREE-EVIDENCE.md`).

## Architectural Responsibility Map

This is Nix toolchain/build-environment work, not an application with web tiers. The table below maps
each capability to the layer that owns it in *this* stack (local dev machine → Nix evaluator →
bubblewrap sandbox → `.venv`/`.tox` → CI runners).

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Resolving `ruff`/`black`/`mypy`/`pytest`/`tox`/`sphinx-build`/`uv` to an absolute, project-owned binary | `writeShellScriptBin` shim (devShell PATH) | — | The shim is the only thing a human or `tox` types by bare name; everything else is a child process (Pattern 2: namespace inheritance) |
| Providing a working ELF interpreter (`/lib64/ld-linux-x86-64.so.2`) for generic-linux wheels | `buildFHSEnv` (bubblewrap sandbox) | Nix store (`/nix` bind-mount) | `bwrap` supplies `glibc`'s dynamic linker inside the mount namespace; `/nix` stays bind-mounted so store paths (incl. the shim's own absolute targets) remain reachable from inside |
| Namespace inheritance to `tox`'s own subprocess tree (`uv-venv-lock-runner`, `.tox/<env>/bin/*`, downloaded CPython) | Linux kernel (`fork`/`exec`) | `tox` shim (entry point only) | Once `tox` itself is running inside the sandbox, every child it spawns inherits the same mount namespace — no additional shim needed below the `tox` shim |
| `$HOME`, `/etc`, network, locale passthrough | bubblewrap sandbox config (`unshare*=false`, `etcBindEntries`) | Host OS | Read directly from nixpkgs source this session — sandbox is deliberately leaky-by-design for FHS compatibility, not a security boundary (see Security Domain) |
| devShell PATH composition and shim-vs-`pkgs.uv` precedence | `mkShell.packages` list order | — | Verified this session: earlier list entries win same-named-binary collisions |
| Multi-system (`x86_64-linux`/`aarch64-linux`/`x86_64-darwin`/`aarch64-darwin`) evaluation safety | `flake.nix`'s per-system `let`-binding laziness | `lib.optionals stdenv.hostPlatform.isLinux` guard | Nix's lazy evaluation means an unguarded reference to `pkgs.buildFHSEnv` would still be evaluated if placed outside the `optionals` thunk; the guard must wrap the `buildFHSEnv` *call site*, not just its use |
| Milestone branch CI baseline (SC#5) | GitHub Actions (`ci.yml`, GitHub-hosted runners) | `gh` CLI (dispatch + observation) | Runs on GitHub-hosted Linux/Windows/macOS runners with real dynamic loaders — entirely outside the NixOS/FHS mechanism this phase builds |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pkgs.buildFHSEnv` | nixpkgs `nixos-unstable` at this flake's pinned rev `65179426c83bb3f6bc14898b42ea1c6f01d374b0` | Bubblewrap-backed FHS sandbox providing a real dynamic linker for generic-linux ELFs | `[VERIFIED: nixpkgs source, read this session at /nix/store/wlk9a5827bc2pdqisypjkgcv5j72xia8-source/pkgs/build-support/build-fhsenv-bubblewrap/default.nix]` — plain alias for `buildFHSEnvBubblewrap`, matches `research/STACK.md`'s prior finding |
| `pkgs.writeShellScriptBin` | nixpkgs builtin | Builds each thin per-command shim derivation | `[VERIFIED: nixpkgs source]` — used by nixpkgs' own `steam-run` for the identical one-rootfs-N-shims pattern |
| `pkgs.writeShellScript` | nixpkgs builtin | Builds the shared `runScript = exec "$@"` passthrough | `[VERIFIED: nixpkgs source]` |
| `pkgs.lib.optionals` / `stdenv.hostPlatform.isLinux` | nixpkgs builtin | Darwin guard around the `buildFHSEnv` call site | `[VERIFIED: nix eval this session]` — laziness confirmed: `nix flake show --all-systems` and `nix eval --json .#devShells --apply builtins.attrNames` both succeed today (before any FHS derivation exists) in 1.2s / 0.04s respectively, establishing the pre-change baseline this phase's guard must preserve |

No new runtime dependency, no new PyPI/npm/cargo package, no new third-party GitHub Action — every
tool above is a nixpkgs builtin already reachable through the existing `nixpkgs.url` input. This
phase's own binding constraint 13 (ROADMAP.md) forbids new runtime dependencies, and this stack
satisfies that by construction.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `bubblewrap` (`bwrap`) | pulled in transitively by `buildFHSEnv` | The actual sandbox backend | Never invoke directly or add to `mkShell.packages` — `buildFHSEnv` already depends on it |
| `pkgs.glibcLocales` | forced, unconditional first entry of `baseTargetPaths` | Locale archive inside the sandbox | `[VERIFIED: nixpkgs source, buildFHSEnv.nix]` — cannot be trimmed without overriding `baseTargetPaths`; REQUIREMENTS.md's Out of Scope table already forbids trimming it |
| `pkgs.cacert` | not currently needed (discretion item, conditional) | TLS trust store for cold `@preview` fetches | Only add if D-07's live `docs-pdf` run shows a TLS failure — `[VERIFIED: nixpkgs source]` shows `/etc/ssl/certs`, `ca-certificates` and `pki` are already bound from the **host's** real `/etc` (not the FHS closure), so this is very likely unnecessary; do not add pre-emptively |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `buildFHSEnv` | `buildFHSEnvChroot` | **Never** — `[VERIFIED: nixpkgs source]` `pkgs/top-level/aliases.nix` throw-aliases it (`'buildFHSEnvChroot' is deprecated, please use 'buildFHSEnv'`); referencing it hard-fails flake evaluation on this pin |
| One shared `buildFHSEnv` + N `writeShellScriptBin` shims | N separate `buildFHSEnv { runScript = "<tool>"; }` derivations | Each `buildFHSEnv` call materializes its own rootfs closure; N of them multiplies the cost for zero benefit since all seven tools need the identical sandbox |
| `mkShell` staying the devShell type | `pkgs.buildFHSEnv.env` as the devShell | **Falsified by live measurement during scoping** (PROJECT.md) — `/lib64/ld-linux-x86-64.so.2` still resolves to `stub-ld` under both `nix develop` and direnv. Do not re-derive. |
| PATH-ordering (`packages` list order) to make the `uv` shim win | Dropping `pkgs.uv` entirely on Linux | `[VERIFIED this session]` — both work; dropping is simpler to reason about and is CONTEXT's discretion recommendation, but ordering alone is a sufficient, tested fallback if the drop is reverted later |

**Installation:** none — no `nix flake update`, no new flake input, no `pyproject.toml`/`uv.lock`
change. This phase edits `flake.nix` only.

**Version verification:** `nix flake metadata` (run 2026-09-03) confirms the flake's `nixpkgs` input
is pinned to `github:NixOS/nixpkgs/nixos-unstable` at the rev recorded in `flake.lock`
(`65179426c83bb3f6bc14898b42ea1c6f01d374b0`, matching the orchestrator's session-start measurement).
All source reads above were taken from the store path that pin resolves to
(`/nix/store/wlk9a5827bc2pdqisypjkgcv5j72xia8-source`), not from a web fetch of `master`, so they
reflect the exact code this phase's `flake.nix` will build against.

## Package Legitimacy Audit

**Not applicable to this phase.** No external package (npm/PyPI/crates or otherwise) is installed.
Every tool referenced (`buildFHSEnv`, `writeShellScriptBin`, `glibcLocales`, `cacert`) is a builtin or
attribute of the already-pinned `nixpkgs` input; there is no new registry dependency for the
Package Legitimacy Gate to check. The `nixpkgs` input itself is content-addressed and pinned via
`flake.lock`'s narHash, which is nixpkgs' own supply-chain integrity mechanism and predates this
phase.

## Architecture Patterns

### System Architecture Diagram

```
Maintainer types a bare command (or `tox` spawns one)
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│  mkShell "default" devShell (Linux)                                │
│  packages = [ nodejs pnpm git python3 (pkgs.uv?) ]                 │
│             ++ optionals isLinux [ uv-shim tox-shim ruff-shim       │
│                                     black-shim mypy-shim pytest-shim│
│                                     sphinx-build-shim ]             │
│                                                                       │
│  PATH lookup: FIRST matching entry in `packages` wins (verified)    │
└───────────────────────────────┬───────────────────────────────────┘
                                 │  shim resolves absolute .venv path
                                 │  (upward walk from $PWD, survives
                                 │   tox's `changedir = docs`)
                                 ▼
                 ┌───────────────────────────────┐
                 │  fhsRun (buildFHSEnv, shared)  │
                 │  runScript = exec "$@"          │
                 └───────────────┬───────────────┘
                                 │ bwrap invocation:
                                 │  --bind /nix /nix
                                 │  --bind /home /home  (auto_mounts)
                                 │  --bind /tmp /tmp     (privateTmp=false)
                                 │  symlink /etc/{resolv.conf,hosts,
                                 │    ssl/certs,ca-certificates,fonts,…}
                                 │    from host /.host-etc
                                 │  NO --unshare-net (network shared)
                                 │  source /etc/profile; exec "$@"
                                 ▼
                 ┌───────────────────────────────┐
                 │  .venv/bin/<tool>  (absolute)  │
                 │  or  /nix/store/…/bin/uv       │
                 └───────────────┬───────────────┘
                                 │ fork/exec — mount namespace
                                 │ INHERITED, no further shim needed
                                 ▼
        tox's own child processes: uv-venv-lock-runner,
        .tox/<env>/bin/*, downloaded CPython, sphinx-build
        invoked from docs/ under changedir — ALL run inside FHS
        for free (Pattern 2)
```

### Recommended Project Structure

No new files/directories — the entire change is additive lines inside the existing `flake.nix`
(currently 40 lines: `flake.nix:11-15` declares the four systems, one `mkShell` block with
`nodejs`/`pnpm`/`git`/`python3`/`uv`). Per CONTEXT's discretion note, keep the FHS derivation and
shim list inline in the existing `let` block rather than splitting into a separate `.nix` file — the
file stays single-purpose and under ~90 lines even with the addition.

### Pattern 1: One shared `buildFHSEnv` + N thin `writeShellScriptBin` shims (the `steam-run` idiom)

**What:** A single `buildFHSEnv` derivation whose `runScript` is a passthrough (`exec "$@"`),
combined with `map` over a command-name list to produce N cheap wrapper derivations that each resolve
an absolute target and `exec` it through the shared sandbox.
**When to use:** Whenever multiple command names need the identical sandbox — avoids rebuilding the
rootfs closure once per command.
**Example (adapted from `research/ARCHITECTURE.md` Pattern 1, updated with this session's upward-walk requirement and PATH-ordering finding):**
```nix
# Source: research/ARCHITECTURE.md Pattern 1, adapted with the changedir=docs
# upward-walk requirement (tox.ini:65,73) and the PATH-ordering finding
# verified this session (mkShell packages: earlier entry wins).
devShells = forAllSystems (
  system:
  let
    pkgs = pkgsFor system;

    fhsRun = pkgs.buildFHSEnv {
      name = "typsphinx-fhs-run";
      runScript = "${pkgs.writeShellScript "fhs-passthrough" ''exec "$@"''}";
      # targetPkgs/multiPkgs left empty: real tools live in .venv (uv/tox-uv
      # install them); glibcLocales is already forced into baseTargetPaths
      # unconditionally (verified in buildFHSEnv.nix), so nothing to add
      # there. Add `cacert` only if a live docs-pdf run demonstrates a TLS
      # gap (D-07) -- host /etc/ssl/certs is already bound (verified below).
    };

    # Upward walk from $PWD, not a bare "$PWD/.venv/bin/<tool>": tox.ini's
    # docs-html/docs-pdf environments set `changedir = docs`, and a human
    # can `cd docs && sphinx-build ...` per CLAUDE.md's documented command.
    findVenvBin = tool: ''
      dir="$PWD"
      while [ "$dir" != "/" ]; do
        if [ -x "$dir/.venv/bin/${tool}" ]; then
          echo "$dir/.venv/bin/${tool}"
          exit 0
        fi
        dir="$(dirname "$dir")"
      done
      echo "typsphinx: ${tool}: no .venv/bin/${tool} found walking up from $PWD" >&2
      exit 127
    '';

    venvShimNames = [ "tox" "ruff" "black" "mypy" "pytest" "sphinx-build" ];
    venvShims = map (
      cmd:
      pkgs.writeShellScriptBin cmd ''
        set -euo pipefail
        target="$(${pkgs.writeShellScript "find-${cmd}" (findVenvBin cmd)})"
        exec ${fhsRun}/bin/typsphinx-fhs-run "$target" "$@"
      ''
    ) venvShimNames;

    # uv is the one D-02 exception: two-tier resolution, .venv/bin/uv first
    # (doesn't exist pre-Phase-65), then the fixed nixpkgs store path.
    uvShim = pkgs.writeShellScriptBin "uv" ''
      set -euo pipefail
      if [ -x "$PWD/.venv/bin/uv" ]; then
        target="$PWD/.venv/bin/uv"
      else
        target="${pkgs.uv}/bin/uv"
      fi
      exec ${fhsRun}/bin/typsphinx-fhs-run "$target" "$@"
    '';
  in
  {
    default = pkgs.mkShell {
      packages = [
        pkgs.nodejs
        pkgs.pnpm
        pkgs.git
        pkgs.python3
      ] ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux (
        [ uvShim ] ++ venvShims
      ) ++ pkgs.lib.optionals (!pkgs.stdenv.hostPlatform.isLinux) [ pkgs.uv ];
    };
  }
);
```
This is a sketch to guide the plan's task breakdown, not a literal patch — the plan owns the exact
diff, the not-found message wording, and the exit code (CONTEXT's discretion items).

### Pattern 2: Namespace inheritance answers "does `tox`'s subprocess tree need its own shims?"

**What:** Linux mount namespaces (and the rest of the `unshare*` set bwrap can apply) are inherited
across `fork`/`exec`. Once a process is running inside the sandbox, every child it spawns — with no
special flag needed — inherits the same mount namespace.
**When to use:** To decide the shim roster's boundary. Only the top-level entrypoints a human or CI
config types directly need shims (D-01's seven names); `uv-venv-lock-runner`, `.tox/<env>/bin/*`, and
CPython downloaded by `uv python install` all run inside FHS for free once `tox`/`uv` themselves do.
**Verification this session:** confirmed conceptually via the source read (bwrap's mount namespace is
a kernel-level property of the process, standard `fork`/`exec` semantics) — this is not something a
research session can falsify by experiment without the real shim in place; it is the well-established
mechanism `pkgs.steam-run` itself relies on for launching arbitrary game binaries and their children.

### Pattern 3: `mkShell` stays the devShell type; FHS is exposed as PATH shims

**What:** Do not attempt `pkgs.buildFHSEnv.env` as the devShell, and do not use a `shellHook` that
`exec`s into the sandbox.
**When to use:** Always, for this project. Both alternatives were falsified by live measurement
during scoping (PROJECT.md's Binding measurements) and must not be re-derived — see the User
Constraints block above, which is authoritative.

### Anti-Patterns to Avoid

- **Bare-name resolution inside a shim** (e.g. `exec ruff "$@"` or `command -v ruff` inside the shim
  body): would either self-recurse (the shim re-invoking itself once it's on `PATH`) or silently fall
  through to nixpkgs' `ruff` if it were ever added to `packages`. NIX-07 requires an absolute,
  un-shadowable path — verified this session that this is achievable and testable (see Code Examples
  §6).
- **`$PWD/.venv/bin/<tool>` without the upward walk:** breaks for `tox -e docs-pdf`/`docs-html`
  (`changedir = docs`, verified `tox.ini:65,73`) and for the CLAUDE.md-documented manual
  `sphinx-build` invocation if run from `docs/`.
- **Adding `cacert`/other `targetPkgs` pre-emptively "just in case":** the source read shows
  `/etc/ssl/certs`, `ca-certificates`, `pki` and `fonts` are already bound from the **host's** real
  `/etc`, not synthesized inside the FHS closure — most anticipated TLS/font gaps are very likely
  already closed by the base mechanism. Confirm the actual failure (D-07) before adding anything.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Generic-linux-ELF execution on NixOS | A per-binary `patchelf` post-`uv-sync` hook, or system-wide `nix-ld` | `pkgs.buildFHSEnv` | Both alternatives are explicitly in REQUIREMENTS.md's Out of Scope table — `patchelf` must re-run after every `uv sync`/tox provisioning (wrong lifecycle), and `nix-ld` is outside this repository's control |
| Locale archive plumbing inside the sandbox | A custom `LOCALE_ARCHIVE` export in the shim | `pkgs.glibcLocales` (already forced into `baseTargetPaths`) + the FHS's own `/etc/profile` default | `[VERIFIED: nixpkgs source]` — the mechanism already exists and is unconditional; duplicating it in the shim risks divergence |
| CA trust store for network fetches inside the sandbox | Bundling `cacert` reflexively | The host's real `/etc/ssl/certs`/`ca-certificates`/`pki`, already bound | `[VERIFIED: nixpkgs source]` — only add `cacert` if a live failure proves it's needed (D-07) |

**Key insight:** almost everything this phase might be tempted to hand-build (locale archive, CA
bundle, font resolution, `$HOME` passthrough) is already handled by `buildFHSEnv`'s own generated
wrapper — the phase's job is to write two nix expressions (one derivation, one `map`) and then
*measure*, not to reimplement environment plumbing bwrap already does.

## Common Pitfalls

### Pitfall 1: Shim self-recursion via bare-name resolution
**What goes wrong:** A shim that looks up its target with `command -v <tool>` or a bare
`exec <tool> "$@"` can re-enter itself once it is on `PATH`, or silently resolve to a different
`<tool>` if one is ever added elsewhere on `PATH`.
**Why it happens:** `PATH` lookup by name doesn't distinguish "the real tool" from "the shim
providing the same name" — they share a name by construction.
**How to avoid:** Resolve an absolute path first (the upward `.venv` walk, or the fixed
`${pkgs.uv}/bin/uv` store path), then `exec` that absolute path.
**Warning signs:** A one-off `--version` smoke test passing is *not* sufficient evidence — NIX-07
explicitly requires the rename-the-target proof (Code Examples §6) because a self-recursive shim can
still print a correct `--version` if the recursion happens to bottom out coincidentally, or hang
only under specific invocation shapes.

### Pitfall 2: Version skew hidden behind exit 0
**What goes wrong:** A shim that gracefully falls back to *any* other `ruff` (e.g. nixpkgs' own, if
ever added) when `.venv/bin/ruff` is missing will exit 0 and look like success, while silently
running a different version (0.15.14 vs. the pinned 0.15.20).
**Why it happens:** "Runs" and "runs the right thing" are conflated if verification only checks the
exit code.
**How to avoid:** D-03's design (no fallback for six of the seven shims) plus NIX-01's exact-version
assertion (`ruff --version` must print `0.15.20`, not merely exit 0).
**Warning signs:** Any verification step written as `ruff check . && echo OK` without a preceding
`ruff --version` check.

### Pitfall 3: `nix flake check` without `--all-systems` silently skips darwin
**What goes wrong:** Running plain `nix flake check` on the Linux evaluator only checks the
**current** system's outputs.
**Why it happens:** `[VERIFIED this session]` — `nix flake check --no-build` (no `--all-systems`)
printed: `checking derivation devShells.x86_64-linux.default... all checks passed! warning: The
check omitted these incompatible systems: aarch64-darwin, aarch64-linux, x86_64-darwin. Use
'--all-systems' to check all.` A plan that runs bare `nix flake check` and reports success has not
verified NIX-06 at all for three of the four declared systems.
**How to avoid:** Always pass `--all-systems` explicitly for this phase's NIX-06 evidence. `nix flake
show --all-systems` and `nix flake check --all-systems --no-build` both succeeded in ~0.8–1.2s
against the current (pre-FHS) flake this session — establishing that the baseline is cheap and the
addition should stay cheap too, since darwin's `buildFHSEnv` thunk must never be forced (Pattern 3 /
the Linux guard).
**Warning signs:** A plan's SC#3 verification step that doesn't literally contain the string
`--all-systems`.

### Pitfall 4: `tox-uv`'s bundled-`uv` wheel silently reinstates the exact defect this milestone repairs
**What goes wrong:** Documented at length in `research/PITFALLS.md` Pitfall 1 and ROADMAP constraint
12 — `tox-uv` (not yet installed until Phase 65) resolves its own `uv` via `TOX_UV_PATH` → a bundled
generic-linux `uv` wheel → `PATH`, which can bypass the shim entirely once Phase 65 lands.
**Relevance to Phase 64:** none directly (this phase never touches `tox-uv-bare`/`tox-uv`), but the
`tox` shim itself must be un-shadowable (Pitfall 1 above) precisely because Phase 65's TOX-03
measurement depends on the `tox` process already running inside a sandbox that Phase 64 established.
Getting the `tox` shim's absolute-path resolution right here is a hard prerequisite for Phase 65's own
gate, not just this phase's NIX-02.
**How to avoid:** Same as Pitfall 1 — absolute path resolution, no bare-name lookups, and confirmed by
NIX-07's rename test applied to the `tox` shim's own target.

### Pitfall 5: Accidentally testing against the real repository instead of an isolated clone
**What goes wrong:** A `sed -i` or similar in-place edit run from a script whose `cd` into a scratch
directory silently failed leaves the shell in its previous working directory — which, absent an
explicit failure check, can be the real project checkout.
**Why it happens:** Cross-filesystem clones (`git clone --local` without `--no-hardlinks`, when the
target is on a different filesystem than the source, e.g. `/tmp` vs. the project's real disk) fail
with "invalid cross-device link", and a script without `cd ... || exit 1` continues in the wrong
directory.
**Concretely, this session:** exactly this happened during research measurement — a `git clone
--local` into this session's scratchpad (a different filesystem) failed, the following `cd` failed
silently, and a subsequent `sed -i` command ran against the **real** `/home/yuta/Documents/typsphinx/flake.nix`
(changing its `description` field). It was caught immediately (`git diff flake.nix` showed the
change) and reverted with `git checkout -- flake.nix` before any other action; `git status --short`
confirmed a clean tree afterward, and this file's own measurements past that point used
`git clone --local --no-hardlinks` (which succeeds across filesystems) with an explicit `cd ... ||
{ echo FAILED; exit 1; }` guard on every subsequent scratch-directory command.
**How to avoid, for the executing phase:** every scratch-directory script must guard `cd` with an
explicit failure path, and `--no-hardlinks` (or an equivalent filesystem check) is required when
cloning into a scratchpad/tmp location that may be a different filesystem than the checkout.
**Warning signs:** any tool-provided "changes since you last read this file" notice on a file the
plan did not intend to touch — treat it as a signal to `git diff`/`git status` immediately, not to
proceed.

## Code Examples

### 1. `ruff` shim shape (NIX-01) — see Pattern 1's full sketch above for the shared `fhsRun` + `findVenvBin` machinery. The `ruff` case specifically:
```nix
# Source: this session's Pattern 1 sketch, D-01/D-03
pkgs.writeShellScriptBin "ruff" ''
  set -euo pipefail
  dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -x "$dir/.venv/bin/ruff" ]; then
      exec ${fhsRun}/bin/typsphinx-fhs-run "$dir/.venv/bin/ruff" "$@"
    fi
    dir="$(dirname "$dir")"
  done
  echo "typsphinx: ruff: no .venv/bin/ruff found walking up from $PWD" >&2
  exit 127
''
```
Verification: `ruff --version` must print exactly `ruff 0.15.20` — `[VERIFIED: uv.lock:1209-1210]`
```
1209:name = "ruff"
1210:version = "0.15.20"
```
(read directly this session; nixpkgs' own `ruff` at this pin is `0.15.14` per `research/STACK.md`,
untouched — this phase never adds `pkgs.ruff` to `packages`, matching REQUIREMENTS.md's Out of Scope
table).

### 2. `uv` shim shape (NIX-01, D-02's two-tier exception)
See Pattern 1's `uvShim` above. Verification this session that the nixpkgs `uv` leg resolves to a
real store path in the current (unmodified) session environment:
```
$ command -v uv
/nix/store/…-uv-0.11.25/bin/uv
```
(session-frozen PATH, matches D-09's measurement; `.venv/bin/uv` does not exist today per D-02).

### 3. NIX-06 — evaluating all four systems on the Linux evaluator without ever forcing `buildFHSEnv` on darwin
```bash
# [VERIFIED this session against the current, pre-FHS flake.nix — 1.2s]
nix flake show --all-systems

# [VERIFIED this session — 0.8s, forces derivation evaluation (not build)
#  for all four systems; the bare form WITHOUT --all-systems silently
#  omits three of them, see Pitfall 3 above]
nix flake check --all-systems --no-build

# Cheaper, scriptable per-system check (0.3-0.8s each, [VERIFIED this session]):
for sys in x86_64-linux aarch64-linux x86_64-darwin aarch64-darwin; do
  nix eval --json ".#devShells.${sys}.default.drvPath"
done
```
The guard shape that keeps darwin's `buildFHSEnv` thunk unforced is `lib.optionals
pkgs.stdenv.hostPlatform.isLinux (...)` wrapping the shim list at its point of use inside the `let`
block (as in Pattern 1's sketch) — Nix's laziness means the `fhsRun`/`venvShims`/`uvShim` bindings are
never evaluated when `isLinux` is `false`, because `lib.optionals false x` never forces `x`. This is
the same idiom nixpkgs' own `flake.nix` uses (`research/STACK.md`, verified against nixpkgs source at
master 2026-09-02) — no `system == "x86_64-darwin" || …` string matching needed.

### 4. NIX-05 — exercising the edited devShell from a fresh git worktree, before or after committing
```bash
# [VERIFIED this session against a real `git worktree add`-created directory
#  in an isolated scratch clone — NOT the real repository]
nix develop path:<worktree-absolute-path>#default --command bash -c '<cmd>'
```
Measured cost: ~0.4–0.5s pure-evaluation overhead per invocation (no build, since the devShell's
inputs are already in the local nix store from prior use); no `--impure` flag needed. This picks up
**uncommitted edits to tracked files** without requiring a commit — verified by editing `flake.nix`'s
`description` field in an isolated scratch clone (never the real repo, after the Pitfall 5 recovery)
and confirming `nix flake metadata path:<dir>` reported the edited string, not the committed one.
Practical implication for the phase's own plans: an executor working inside their assigned worktree
can smoke-test each incremental `flake.nix` edit with `nix develop path:$(pwd)#default --command
<tool> --version` **before** committing the task, and does not need to wait for a commit for the
change to take effect.

This is a *diagnostic* invocation for iterating during execution — it does **not** replace D-04's
verification locus (a genuinely fresh worktree, provisioned via `env -u VIRTUAL_ENV -u
UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then exercised via the interactive-shell/session-PATH
inheritance path D-09 measured). NIX-05's actual pass condition is that the **inherited** session PATH
(no explicit `nix develop --command` wrapper) already carries the shims — D-09's finding — with a
`command -v ruff` / `command -v uv` check at the head of the provisioning procedure to confirm this
before relying on it, exactly as D-09 specifies.

### 5. NIX-07 — the rename-test procedure, concretely
```bash
# In the worktree where the shims are active on PATH:
which ruff                      # capture the shim's own resolved path
cat "$(command -v ruff)"        # confirms the shim body: absolute target,
                                 # no bare-name PATH lookup inside it
mv .venv/bin/ruff .venv/bin/ruff.bak
ruff --version                  # EXPECTED: shim's not-found message + exit
                                 # 127 (per Pattern 1's sketch) -- NOT a hang,
                                 # NOT a fork bomb, NOT nixpkgs' 0.15.14
                                 # (which would prove a silent fallthrough)
echo "exit code: $?"
mv .venv/bin/ruff.bak .venv/bin/ruff
ruff --version                  # restored -- must print 0.15.20 again
```
`cat "$(command -v ruff)"` is the proof that the resolution is by absolute path: the shim's own
source text (a Nix store path under `/nix/store/…-ruff/bin/ruff`, itself a `writeShellScriptBin`
output) will show the upward-walk loop and the `exec ${fhsRun}/bin/typsphinx-fhs-run "$dir/.venv/bin/ruff"`
line with **no** `command -v`/bare-name lookup anywhere in the body — record this transcript verbatim
per D-05.

### 6. NIX-08 — environment/locale measurement procedure
```bash
# Through the shim (inside FHS):
uv run python3 -c "import os; print('HOME=', os.environ.get('HOME')); \
  print('TMPDIR=', os.environ.get('TMPDIR')); \
  print('LANG=', os.environ.get('LANG')); print('LC_ALL=', os.environ.get('LC_ALL'))"
ls -la /etc | head -30          # which host /etc entries are visible/symlinked
locale                          # full locale report
python3 -c "import locale, sys; print(locale.getlocale()); print(sys.stdout.encoding)"

# Bare (outside FHS), same commands, for the diff:
.venv/bin/python3 -c "..."      # same probes, unshimmed
```
**Locale-defect-class probe** (per D-08 — record, do not pin `LC_ALL`):
```bash
LC_ALL=C LANG=C uv run python -m pytest tests/ -q   # OUTSIDE the sandbox (known pre-check per memory)
uv run python -m pytest tests/ -q                    # THROUGH the shim, maintainer's real LANG=ja_JP.UTF-8
```
Compare pass/fail sets between the two runs and against the maintainer's ordinary (unshimmed)
`LANG=ja_JP.UTF-8` run to determine whether the sandbox reproduces or masks the class. **This session
did not run the full suite** (explicitly out of scope for research measurement); the procedure above
is designed but not executed — flag this in Open Questions.

### 7. SC#5 — CI dispatch and lane identification
```bash
gh workflow run CI --ref <branch>              # ci.yml's `name: CI`; push/PR triggers
                                                 # are scoped to main/develop (ci.yml:4-9)
gh run list --branch <branch> --limit 5         # find the run id
gh run view <run-id> --json status,conclusion,jobs \
  --jq '.jobs[] | {name, conclusion}'
```
Job name templates read directly from `ci.yml` this session:
- `test`: `name: Test Python ${{ matrix.python-version }} on ${{ matrix.os }}` — with
  `os: [ubuntu-latest, windows-latest, macos-latest]` × `python-version: ['3.12', '3.13']`, so the
  actual per-run job names include **`Test Python 3.12 on windows-latest`**, **`Test Python 3.13 on
  windows-latest`**, **`Test Python 3.12 on macos-latest`**, **`Test Python 3.13 on macos-latest`**
  — these four (two Windows, two macOS) are the ones SC#5 requires named individually and green.
- `lint`: `Lint and Format Check`; `type-check`: `Type Check`; `coverage`: `Code Coverage`;
  `build`: `Build Package`; `integration`: `Integration Test - ${{ matrix.example }}`.
`gh auth status` confirms this session is authenticated (`YuSabo90002`, `github.com`) — the phase's
own dispatch can reuse this authentication.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| Manual `ln -sf`/`patchelf` per binary, per fresh worktree | One Linux-guarded `buildFHSEnv` + 7 `writeShellScriptBin` shims on the devShell PATH | This phase | Retires the exact step Phase 38-07 forgot (45-test false alarm, cited in ROADMAP constraint 11); every future worktree gets working tools with zero manual steps |
| `flake.nix` devShell = `mkShell` with plain nix-store packages only | Same `mkShell`, with 7 additional shim derivations appended on Linux | This phase | `flake.nix` becomes load-bearing for local dev correctness while remaining outside CI's reach (ROADMAP constraint 8's accepted risk) |

**Deprecated/outdated:** `buildFHSEnvChroot` — `[VERIFIED: nixpkgs source]` throw-aliased, hard-fails
evaluation on this pin; never reference it.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|-----------------|
| A1 | `LOCALE_ARCHIVE` is already set in the maintainer's interactive NixOS session (so the FHS `/etc/profile`'s `${LOCALE_ARCHIVE:-/usr/lib/locale/locale-archive}` default is never actually exercised) | Summary point 3, NIX-08 | If unset, the sandbox would fall back to a default archive path that may not exist inside the sandbox's own closure, producing a locale-related failure distinct from the maintainer's ordinary `LANG=ja_JP.UTF-8` behaviour — this is exactly what NIX-08's live measurement (Code Examples §6) must check, not assume |
| A2 | The maintainer's NixOS machine's real `/etc/ssl/certs`/`ca-certificates`/`pki` are populated (so no cold-cache TLS gap exists for `docs-pdf`'s `@preview` fetches) | Standard Stack (Supporting), D-07 | If the host's own trust store is somehow incomplete, adding `cacert` to `targetPkgs` would still be necessary — D-07 already provides this as the fallback, so the risk is bounded, not open-ended |
| A3 | Cold `tox` environment creation (first `-e py312`/`-e py313` run, including `uv python install 3.12`/`3.13` if not already cached) fits inside a single 10-minute executor Bash call | Environment Availability, Open Questions | This session found only **warm** timing data (existing `.tox` envs: `tox -e lint` ~3.2s, `docs-html`/`docs-pdf` ~4s each, full pytest ~121-124s) from `.planning/milestones/v0.9.2-phases/`; no cold-provisioning timing exists anywhere in this repository's history because this is the first phase to run `tox` inside a working NixOS sandbox. If wrong, the plan must split the first `tox -e py312`/`-e py313` invocation into its own task or background it |
| A4 | The FHS sandbox's `/etc/profile` sourcing (which prefixes `PATH` and appends a few build-related vars) has no observable effect on `ruff`/`black`/`mypy`/`pytest`/`sphinx-build`'s own behaviour, since none of them shell out to a `PATH`-resolved child by bare name in normal operation | Summary point 3, Pattern 1 | If any of these tools does shell out by bare name (e.g. a subprocess call to `git` or a compiler), the FHS's `/usr/bin`-prefixed `PATH` could resolve a different binary than the one on the maintainer's ordinary `PATH` — worth a spot-check during NIX-02/NIX-04 rather than a blocking gate |

## Open Questions

1. **Cold `tox` environment provisioning timing is unmeasured.** (See A3.) The phase's plans should
   budget the first `tox -e py312`/`-e py313` run as potentially the longest single step, and consider
   running it as an isolated first task (or backgrounded) rather than bundling it with faster steps
   in one Bash call, purely as a scheduling precaution — not because any evidence suggests it will
   fail, only because no evidence exists either way.

2. **NIX-08's actual locale-defect-class comparison was designed (Code Examples §6) but not executed
   this session** — running the 1548-test suite is explicitly the phase's own measurement, not
   research's. The procedure is ready; the phase's plans should budget one full-suite run through the
   shim and treat the `LC_ALL=C` pre-check (already a documented local convention per this project's
   own memory) as the comparison baseline, not a second full run under a different locale (D-08
   explicitly forbids doubling the suite run).

3. **A research-session tooling accident touched the real `flake.nix` and was reverted before any
   further action** (Pitfall 5) — recorded here for transparency since orchestrator notes explicitly
   constrained this session against editing tracked files. `git status --short` and `git diff` were
   both empty on the real repository at the end of this session; no further verification action is
   needed, but the phase's own executor should not assume this note implies anything about the
   phase's own start state — it should independently confirm `git status --short` is clean at task
   start, which is standard practice regardless.

4. **Whether `/etc/fonts` inside the sandbox genuinely reaches the maintainer's installed font set for
   Typst's font resolution (NIX-03's `docs-pdf` PDF-content requirement) was read from source
   (`etcBindEntries` includes `fonts`, explicitly sourced from the host) but not empirically confirmed
   against a real `typst.compile()` call inside the sandbox** — this session did not build or enter an
   actual FHS sandbox (out of scope for research measurement; would require materializing the full
   `baseTargetPaths` closure, a nontrivial build). NIX-03's own `docs-pdf` run is exactly this proof
   and must be taken as the phase's own primary evidence, not inferred from the source read alone.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `nix` | Entire phase | ✓ | 2.34.8 `[VERIFIED this session: nix --version-equivalent metadata already known from orchestrator notes, confirmed live via nix flake commands]` | — |
| `bubblewrap` (`bwrap`) | `buildFHSEnv`'s runtime backend | ✓ | 0.11.2, at `/nix/store/kxcgm56aqlvgffr88i2d76zhiklxj3r7-bubblewrap-0.11.2/bin/bwrap` per orchestrator notes; not independently re-verified this session (out of scope: building/running a real FHS sandbox) | — |
| `gh` (GitHub CLI) | SC#5 dispatch/observation | ✓ | 2.98.0, authenticated as `YuSabo90002` `[VERIFIED this session: gh auth status]` | — |
| `direnv` | Interactive maintainer reachability (not the executor path) | Assumed installed (`.envrc` is `use flake`, referenced by CONTEXT D-09) | not independently checked this session | N/A — D-09 explicitly routes NIX-05 through session-PATH inheritance, not direnv reload |
| Host `/etc/ssl/certs`, `ca-certificates`, `pki`, `fonts` | `docs-pdf`'s font/TLS needs inside the sandbox | Assumed present (standard on any real NixOS install) — `[VERIFIED: nixpkgs source]` shows these are *bound from the host*, so their actual presence/completeness is a host-configuration fact this research cannot verify remotely | `cacert` addition to `targetPkgs` (D-07) if a live failure demonstrates a gap |

**Missing dependencies with no fallback:** none identified.

**Missing dependencies with fallback:** the `cacert` package is available and cheap to add if D-07's
live measurement demonstrates a TLS gap; no other fallback paths are anticipated.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`; `sphinx.testing.fixtures` loaded as a plugin per `CLAUDE.md`) |
| Config file | `pyproject.toml` (pytest section) |
| Quick run command | `uv run python -m pytest tests/ -q -x` (fail-fast subset, seconds to ~2 min depending on scope) |
| Full suite command | `uv run python -m pytest tests/ -q` (1548 tests; **warm** `[VERIFIED: .planning/milestones/v0.9.2-phases/62-.../62-RED-EVIDENCE.md:680]** `1543 passed, 5 skipped in 123.57s`, closest prior measurement — count has grown by 5 to 1548 at this milestone's start per REQUIREMENTS.md) |

### Phase Requirements → Test Map

NIX-01 through NIX-08 are **measurement/observation requirements against a Nix/OS-level mechanism**,
not unit-testable product behaviour — D-05 explicitly forecloses adding a pytest test or a committed
script for them (a pytest test would be permanently skipped on every CI runner, since none has `nix`
or a Linux FHS-capable sandbox). The map below reflects that reality honestly rather than forcing a
pytest-shaped entry where none exists.

| Req ID | Behavior | Test Type | Automated Command | Evidence Location |
|--------|----------|-----------|---------------------|---------------------|
| NIX-01 | `ruff check .` runs, reports exact `0.15.20` | manual-only (shell transcript) | `ruff --version && ruff check .` (through the shim, in a fresh worktree) | phase evidence markdown (D-05) |
| NIX-02 | `tox -e lint/type/py312/py313` complete | manual-only (shell transcript) | `tox -e lint && tox -e type && tox -e py312 && tox -e py313` | phase evidence markdown |
| NIX-03 | `tox -e cov/docs-html/docs-pdf` complete, real PDF | manual-only + file-magic assertion | `tox -e cov && tox -e docs-html && tox -e docs-pdf && file docs/build/pdf/*.pdf` (or equivalent path) — `[VERIFIED: %PDF magic bytes, not exit 0]` per NIX-03's own wording | phase evidence markdown |
| NIX-04 | Full 1548-test suite, no environment-caused failures | automated (existing suite) | `uv run python -m pytest tests/ -q` inside a freshly provisioned worktree (D-04) | pytest's own output, quoted in evidence markdown |
| NIX-05 | Fresh worktree, provisioning line, then every gate, no manual step | manual-only (procedure + transcript) | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `command -v ruff`/`command -v uv` check (D-09), then the gates above | phase evidence markdown |
| NIX-06 | `flake.nix` evaluates on all 4 systems | automated (nix CLI) | `nix flake show --all-systems` and `nix flake check --all-systems --no-build` (Pitfall 3 — **must** include `--all-systems`) | phase evidence markdown, transcript |
| NIX-07 | Absolute-path resolution, rename-test proves no self-recursion | manual-only (procedure + transcript) | Code Examples §5's rename/restore sequence | phase evidence markdown |
| NIX-08 | `$HOME`/`TMPDIR`/`/etc`/locale measured; defect-class effect recorded | manual-only (procedure + transcript) | Code Examples §6's probe sequence | phase evidence markdown |

### Sampling Rate
- **Per task commit:** `uv run python -m pytest tests/ -q -x` (fast fail-fast check that nothing in
  `flake.nix` broke Python-level behaviour — largely a no-op safety net here since this phase touches
  no Python code, but keeps the standing convention).
- **Per wave merge / phase gate:** the full manual-command matrix above (NIX-01 through NIX-08), since
  none of it is pytest-automatable; `uv run python -m pytest tests/ -q` (full suite) as NIX-04's own
  gate.
- **Phase gate:** all eight NIX-* items' evidence transcripts present and green before
  `/gsd-verify-work`; full pytest suite green (NIX-04); CI dispatch completed (SC#5).

### Wave 0 Gaps
None — no new test file, no new fixture, no framework install. This phase deliberately does not add
test infrastructure (D-05); its verification surface is shell transcripts in evidence markdown, which
the plan(s) must create as their own deliverable (name/location left to CONTEXT's discretion item,
constrained only by "not `64-VERIFICATION.md`", the verifier-reserved name — Phase 63 precedent:
`63-CI-EVIDENCE.md`, `63-GREEN-TREE-EVIDENCE.md`).

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|---------------------|
| V1 Architecture | Partially | The FHS sandbox must not be mistaken for a security boundary — see Threat Patterns below |
| V2 Authentication | No | No auth surface — local dev tooling only |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | Shim scripts take no untrusted input beyond the invoking user's own shell arguments (`"$@"`), which are passed through unmodified via `exec` — no parsing, no injection surface beyond what the invoking shell already controls |
| V6 Cryptography | No | This phase adds no crypto; `docs-pdf`'s TLS (if any) relies on the host's own CA bundle, already the project's existing trust model |
| V12 Files and Resources | Yes | The sandbox binds substantial host filesystem surface (`/home`, `/tmp`, `/nix`, curated `/etc` entries) — see Threat Patterns |

Most ASVS web-application categories genuinely do not apply: this phase adds no network-facing
service, no authentication, no user input parsing beyond shell argument passthrough. The one
category worth stating explicitly is V12/V1: **`buildFHSEnv`'s bubblewrap sandbox is not a security
isolation boundary in this deployment.** `[VERIFIED: nixpkgs source]` — `unshareUser`/`unshareNet`/
`unsharePid`/etc. all default to `false`, `dieWithParent` defaults to `true` (process-lifecycle
convenience, not isolation), and the auto-mount loop binds essentially the entire host filesystem
(minus `/nix /dev /proc /etc`) read-write into the sandbox. This is correct and intentional for this
phase's purpose (FHS ABI compatibility for trusted local tooling the maintainer already runs
unsandboxed today), but it must not be described in DOC-19/DOC-21 (Phase 68) as a hardening or
isolation mechanism — it provides none. `pkgs.steam-run`, the idiom this phase copies, makes the
identical tradeoff for the identical reason.

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Shim self-recursion / bare-name PATH resolution (Pitfall 1) | Tampering (a future `PATH` addition could redirect a "trusted" bare-name lookup) | Absolute-path resolution only, never a bare `exec <tool>` inside a shim — NIX-07's rename test is the standing regression check |
| `buildFHSEnv`'s broad host-filesystem bind (V12) | Information Disclosure (in the abstract — a compromised process inside the sandbox sees nearly the same filesystem as outside it) | Not mitigated by design — this is a compatibility shim, not a sandbox against untrusted code; the tools it runs (`ruff`, `pytest`, etc.) are already trusted local tooling the maintainer runs unsandboxed today, so the sandbox does not *increase* the attack surface relative to the pre-Phase-64 baseline |
| Supply-chain integrity of the `nixpkgs` pin | Tampering | Already covered by `flake.lock`'s narHash pinning, predating this phase — this phase adds no new input |

## Sources

### Primary (HIGH confidence)
- `pkgs/build-support/build-fhsenv-bubblewrap/default.nix` and `buildFHSEnv.nix`, read directly this
  session from `/nix/store/wlk9a5827bc2pdqisypjkgcv5j72xia8-source` (the exact store path this
  flake's own `nixpkgs.url` input resolves to, confirmed via
  `nix eval --raw --impure --expr '(builtins.getFlake (toString ./.)).inputs.nixpkgs.outPath'`) —
  `etcBindEntries`, `bwrapCmd`'s auto-mount/ignore logic, `unshare*`/`privateTmp`/`chdirToPwd`/
  `dieWithParent` defaults, `baseTargetPaths`'s unconditional `glibcLocales`, `etcProfile`'s
  `LOCALE_ARCHIVE`/`PATH` handling, and the `realInit`/`source /etc/profile` sequencing.
- This session's live experiments (all against either the unmodified real repository read-only, or an
  isolated `git clone --local --no-hardlinks` scratch clone — never a write to the real repository
  after the one accidental edit, immediately reverted): `nix flake show --all-systems`, `nix flake
  check --all-systems --no-build`, `nix eval --json .#devShells --apply builtins.attrNames`, `nix
  develop path:<dir>#default --command` from both a plain clone and a real `git worktree add`
  directory, and the `mkShell` `packages`-order collision test.
- `uv.lock:1209-1210` (`name = "ruff"` / `version = "0.15.20"`), `tox.ini:11,65,73` (`requires =
  tox-uv-bare~=1.35`; `changedir = docs` for both `docs-html` and `docs-pdf`), `pyproject.toml:38`,
  `.github/workflows/ci.yml` (job names, matrix, trigger scoping), `flake.nix` (current 40-line
  content) — all read directly this session.
- `.planning/CONTEXT.md` (64-CONTEXT.md), `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`,
  `.planning/PROJECT.md`, `.planning/STATE.md` — this project's own locked decisions and binding
  measurements, read this session.

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md`, `STACK.md`, `PITFALLS.md`, `SUMMARY.md` — milestone-level
  research from 2026-09-02, read this session and extended rather than re-derived.
- `.planning/milestones/v0.9.2-phases/62-.../62-RED-EVIDENCE.md` and
  `63-.../63-GREEN-TREE-EVIDENCE.md` — prior-phase timing data (warm `.tox`/pytest run durations),
  used to estimate this phase's own time budget with an explicit caveat that cold-provisioning timing
  is absent from any prior evidence.

### Tertiary (LOW confidence / flagged unverified)
- Cold `tox` environment provisioning duration (first `-e py312`/`-e py313` run including a possible
  `uv python install` network fetch) — no measurement exists anywhere in this repository's history;
  flagged as Assumption A3 / Open Question 1.
- Whether the maintainer's actual NixOS machine has a complete `/etc/ssl/certs`/font set for the
  `docs-pdf` sandbox run to succeed without `cacert` — assumed based on "any real NixOS install has
  this", not independently confirmed against the specific maintainer machine this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every nixpkgs mechanism claim was read from the pinned source this session,
  not recalled from training data or an unauthenticated web fetch.
- Architecture: HIGH for the mechanism (namespace inheritance, PATH-ordering, dirty-tree `nix
  develop` behaviour — all live-tested this session); MEDIUM for the exact shape of the not-found
  message/exit code (explicitly CONTEXT's discretion, not a research fact).
- Pitfalls: HIGH for the five documented here (all either source-verified or reproduced live this
  session, including the Pitfall 5 self-report); MEDIUM for NIX-08's locale-defect-class interaction,
  which remains the phase's own measurement to take (Open Question 2).

**Research date:** 2026-09-03
**Valid until:** ~14 days (nixpkgs `nixos-unstable` moves; re-verify the pinned rev and the source
reads above if `flake.lock` changes before this phase executes) or immediately upon Phase 64
execution superseding it with live measurement, whichever comes first.
