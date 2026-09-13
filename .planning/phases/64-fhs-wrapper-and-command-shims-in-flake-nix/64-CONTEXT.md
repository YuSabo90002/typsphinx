# Phase 64: FHS Wrapper and Command Shims in `flake.nix` - Context

**Gathered:** 2026-09-03
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase makes the whole generic-linux-ELF class executable on the maintainer's NixOS machine by
adding one Linux-guarded `pkgs.buildFHSEnv` derivation plus per-command `writeShellScriptBin` shims
to `flake.nix`, and it **measures** the sandbox's behaviour for this project's actual invocation
shape rather than reasoning about it. It closes NIX-01 through NIX-08 and carries constraint 10's
branch-to-`origin` + 3-OS CI baseline.

**In scope:** `flake.nix` (the FHS derivation, the shims, the per-system guard), the measurements
NIX-05 / NIX-07 / NIX-08 require, and the evidence files that record them; pushing the canonical
milestone branch and dispatching one CI run.

**Out of scope, by construction:** anything under `typsphinx/` (standing milestone invariant); any
`.github/workflows/` edit (ROADMAP constraint 3 — no `nix` job, no `setup-uv` pinning, no `@v7`→`@v10`
bump); the `tox-uv-bare` → `tox-uv` package swap (that is Phase 65, and reverting before this phase
is proven reintroduces the exact QUA-04 defect `-bare` was chosen to avoid); `.github/dependabot.yml`
(Track B, Phases 66–67); the documentation follow-through in `CLAUDE.md` / `tox.ini` / `flake.nix`
comments (Phase 68 — DOC-19, DOC-20, DOC-21); `patchelf` / `autoPatchelfHook` / `nix-ld` /
`pkgs.ruff` (all in REQUIREMENTS.md's binding Out of Scope table).

**Already settled upstream — do not re-derive.** Two designs were falsified by live measurement
during scoping and are recorded in PROJECT.md § Binding measurements: `buildFHSEnv`'s `.env` used as
the devShell does **not** put you inside FHS under either `nix develop` or `direnv`
(`/lib64/ld-linux-x86-64.so.2` still resolves to `stub-ld` in both), and a `shellHook` that `exec`s
into the wrapper fails differently in each (`nix develop` never runs the hook; under direnv the
`exec` only replaces nix-direnv's environment-capture subshell). The devShell therefore stays
`mkShell` and the FHS is exposed as PATH command shims. `buildFHSEnv` is a plain alias for
`buildFHSEnvBubblewrap` and is the name to write; `buildFHSEnvChroot` was removed from
nixos-unstable and referencing it hard-fails flake evaluation.

</domain>

<decisions>
## Implementation Decisions

### Shim surface

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

### Verification locus

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

### FHS sandbox environment

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

### Worktree reachability (NIX-05)

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

### Folded Todos

- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — already tagged
  `resolves_phase: 64` at roadmap time. It is this milestone's source todo for Track A: `ruff` cannot
  run on the maintainer's NixOS machine because `.venv/bin/ruff` is a generic-linux ELF the stub
  loader rejects and no other `ruff` is on PATH. Its own candidate remedies (`pkgs.ruff`, `patchelf`,
  system `nix-ld`) were all rejected in favour of the FHS route and now sit in REQUIREMENTS.md's Out
  of Scope table — the todo is closed by this phase's mechanism, not by its suggestions.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope, requirements and binding constraints
- `.planning/ROADMAP.md` § "Phase 64: FHS Wrapper and Command Shims in `flake.nix`" — goal, the five
  success criteria, and the RESOLVED constraint-9 note (the decoy-branch pair was corrected
  2026-09-02; a Phase 64 executor must re-measure rather than trust the note, and must expect the
  decoy to be re-created by any later `commit` helper call).
- `.planning/ROADMAP.md` § "Binding constraints this roadmap is built on" — constraints 1 (track
  ordering), 3 (CI unchanged), 5 (the five unverified items closed by measurement), 6 (assert exact
  versions, not exit codes), 8 (`flake.nix` becomes load-bearing with zero CI coverage; `nix eval` /
  `nix flake show` must succeed for all four declared systems), 10 (branch reaches `origin` in the
  first phase with a completed 3-OS CI run), 11 (worktree isolation is not replaced by the FHS
  wrapper), 13 (standing invariants), 15 (**UI hint: no**).
- `.planning/REQUIREMENTS.md` § "NixOS execution (NIX)" — NIX-01 … NIX-08 verbatim.
- `.planning/REQUIREMENTS.md` § "Out of Scope" — binding; `patchelf`/`autoPatchelfHook`, `nix-ld`,
  `pkgs.ruff`, a `nix` CI job, and trimming `glibcLocales` are all excluded with reasons.
- `.planning/PROJECT.md` § "Binding measurements taken during scoping (2026-09-02)" — the two
  falsified devShell designs, the Linux-only guard, the exact-0.15.20 rule, and the standing
  zero-CI-coverage risk.

### Research
- `.planning/research/ARCHITECTURE.md` — Pattern 1 (one shared FHS derivation + N thin shims, with a
  shape sketch), Pattern 2 (namespace inheritance answers the tox subprocess-tree question), Pattern 3
  (`mkShell` stays the devShell), and the Data Flow section's OPEN QUESTION on worktree/direnv
  reachability that D-09 answers.
- `.planning/research/SUMMARY.md` — the milestone-level synthesis, including the amended Track B
  scope (read for context; Track B is not this phase's work).
- `.planning/research/PITFALLS.md` — Pitfalls 2 (shim self-recursion), 3 (version skew hidden behind
  exit 0) and 10 (graceful degradation replaces "doesn't run" with "runs but lies").
- `.planning/research/STACK.md` — the nixpkgs facts read from source on 2026-09-02
  (`buildFHSEnv` = `buildFHSEnvBubblewrap`; `buildFHSEnvChroot` removed).

### Repository surfaces this phase reads or edits
- `flake.nix` — the only file this phase modifies. Currently 40 lines: four declared systems at
  `flake.nix:11-15`, one `mkShell` with `nodejs`, `pnpm`, `git`, `python3`, `uv`.
- `.envrc` — a single `use flake`; git-tracked, so it lands in every worktree, while `/.direnv/` is
  gitignored (`.gitignore:114-116`) and machine-local.
- `CLAUDE.md` § "Commands" (the documented bare-command list D-01 derives from, incl. lines 39-40's
  `sphinx-build`) and § "Worktree-isolated execution" (the provisioning line D-04 and D-09 both build
  on). **This phase does not edit CLAUDE.md** — that is DOC-19, Phase 68.
- `uv.lock:1208-1210` — the `ruff` pin, confirmed `version = "0.15.20"`, which NIX-01 asserts exactly.
- `tox.ini:4-11` and `pyproject.toml:38` — the `tox-uv-bare` declarations. Read-only here; Phase 65
  edits them.

### Source todo
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`
  (`resolves_phase: 64`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`pkgs.steam-run`'s idiom** is the prior art for D-01/D-02: one `buildFHSEnv` whose `runScript`
  is `exec "$@"`, then N cheap `writeShellScriptBin` wrappers. One rootfs derivation, N thin shims.
- **`flake.nix`'s existing `forAllSystems` / `pkgsFor` helpers** already give the per-system
  structure the Linux guard hangs off; no restructuring is needed to add
  `lib.optionals stdenv.hostPlatform.isLinux`.
- **The project's existing evidence-file convention** (`*-EVIDENCE` / `*-VERIFICATION` markdown in the
  phase directory, with verbatim transcripts) is what D-05 uses; nothing new is invented.

### Established patterns and measured constraints
- **`.venv/bin` inventory, measured 2026-09-03:** `black`, `blackd`, `coverage`, `mypy`, `pre-commit`,
  `pytest`, `python`/`python3`/`python3.13`, `ruff`, `sphinx-build`, `sphinx-apidoc`, `sphinx-intl`,
  `tox`, `twine`, `virtualenv` — and **no `uv`**. Six of the seven D-01 names have a target today;
  `uv` does not, which is precisely why D-02 exists.
- **Every one of those binaries currently runs in the main tree** (`ruff 0.15.20`, `black 26.5.1`,
  `mypy 2.1.0`, `pytest 9.1.1`, `tox 4.56.1`, `Python 3.13.13`, `sphinx-build 9.1.0`, all rc=0). This
  is the trap D-04 avoids.
- **Session `PATH` is direnv-derived and frozen at session start** (D-09's measurement). Note the
  practical consequence for planning: an executor's Bash calls inherit the *launching* session's
  environment, not one re-derived per directory.
- **`tox.ini`'s comma-free `~=` form** is a live ini-parser constraint (`tox.ini:4-11`). Phase 64 does
  not touch it, but any incidental edit must preserve it.

### Integration points
- `flake.nix` `devShells.<system>.default.packages` — where the shims are appended on Linux, and
  where `pkgs.uv` is dropped on Linux only.
- The shims' host-side resolution walks up from `$PWD` to find `.venv/bin/<tool>`; this must survive
  `tox`'s `changedir = docs` (the `docs-*` environments run from `docs/`, a subdirectory), and must
  work from an arbitrary worktree path.
- `uv run <tool>` is the entry point that carries FHS into the whole worktree flow, which is why D-02
  routes both `uv` legs through the sandbox.

</code_context>

<specifics>
## Specific Ideas

- The `uv` two-step is explicitly framed as **the one documented exception** to D-03's no-fallback
  rule. When Phase 68 writes DOC-19/DOC-20, that asymmetry is the thing worth stating plainly, so a
  future reader does not "fix" the six strict shims into being lenient like `uv`.
- NIX-07's proof must be the rename-the-target experiment, not a `--version` smoke test: rename or
  remove `.venv/bin/ruff`, invoke the shim, and record that it exits with a clear not-found message
  rather than hanging, fork-bombing, or resolving to another `ruff`.
- The NIX-08 record should state, in one sentence each: whether `$HOME`, `TMPDIR`, `/etc` and the
  locale pass through unchanged, and whether the sandbox **reproduces or masks** the repository's
  locale-dependent defect class. "Masks it" is a legitimate finding and must be written as such.
- SC#5's CI baseline is a *pre-revert* baseline that Phase 65's TOX-04 will be compared against —
  transcribe each job's conclusion literally, naming the `windows-latest` and `macos-latest` lanes
  individually. `ci.yml`'s push/PR triggers are scoped to `main`/`develop`, so the run must be
  dispatched with `gh workflow run CI --ref <branch>`; a push alone runs nothing.

</specifics>

<deferred>
## Deferred Ideas

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

</deferred>

---

*Phase: 64-FHS Wrapper and Command Shims in `flake.nix`*
*Context gathered: 2026-09-03*
