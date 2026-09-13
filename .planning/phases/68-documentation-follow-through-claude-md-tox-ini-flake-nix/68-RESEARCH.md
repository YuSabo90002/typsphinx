# Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` - Research

**Researched:** 2026-09-12
**Domain:** Documentation-only edit (Nix `#` comments, Markdown, tox `.ini` comment, two pytest docstrings/messages) — no runtime code, no new dependency
**Confidence:** HIGH — every claim below is either a direct `Read` of the file at HEAD, a command run in this session, or a quote from an existing phase evidence file (all `[VERIFIED]`); nothing rests on training-data recall of Nix/tox/uv behavior.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**SC#1's boundary — corrected by measurement**

- **D-01: ROADMAP SC#1 gets an `AMENDED 2026-09-12` block correcting "unaffected and unassisted by `flake.nix`"; the original text stays.** Measured (Phase 64 NIX-05, `64-NIX05-WORKTREE-EVIDENCE.md`
  and `64-GAP-REMEASURE-EVIDENCE.md`): a fresh worktree's `uv sync` builds `.venv` on uv-managed
  CPython 3.14, a generic-linux ELF that NixOS refuses outside FHS (rc 127). `uv run …` in a
  worktree therefore works **only because** the `uv` shim enters the FHS sandbox, and every process
  under it inherits the sandbox. So on the maintainer's NixOS machine, worktree executors are
  **assisted by, and depend on,** `flake.nix`. The shims reach a worktree solely through the `PATH`
  inherited from the launching session (the worktree's own `.envrc` was never allowed:
  `Found RC allowed 1`); direnv never loads there. The substantive boundary SC#1 exists to protect is
  unchanged and binding: **the provisioning recipe stays mandatory, byte-identical, and is not
  replaced by `flake.nix`**. Text CLAUDE.md must carry, in its own words: the recipe is unchanged and
  mandatory; `flake.nix` does not substitute for it; on this NixOS machine the recipe itself runs
  through the shims; the shims arrive by inheritance from a session launched in the direnv-loaded
  main checkout, not by direnv in the worktree. The verifier reports SC#1's literal reading and its
  amended reading separately (Phase 65 D-01 precedent). Owner-approved.

- **D-02: The "retire the manual `ln -sf` / `patchelf` guidance" clause is closed as vacuously satisfied, with evidence, plus one negative sentence in CLAUDE.md.** Measured: `git log --oneline -S "ln -sf" -- CLAUDE.md` and `git log --oneline -S patchelf -- CLAUDE.md` both return
  zero commits — the guidance was never in `CLAUDE.md`; it lived only in the maintainer's
  out-of-repository auto-memory. Evidence transcribes both `git log -S` outputs and
  `git grep -nE 'ln -sf|patchelf' -- ':!.planning'` verbatim. CLAUDE.md gains one sentence: no
  manual `ln -sf` / `patchelf` step exists or is needed; a `Could not start dynamically linked
  executable` (stub-ld) error means the shim is not on `PATH` (the session was not launched from the
  direnv-loaded checkout) — **not** a code regression (Pitfall 3's detection signal). The D-01
  `AMENDED` block records the vacuity in one line.

- **D-03: CLAUDE.md states the launch prerequisite and adds a shim check before the unchanged provisioning line.** On the maintainer's NixOS machine, Claude Code must be launched from a shell in
  which direnv has loaded the main checkout's devShell. Before provisioning a worktree, confirm
  `command -v uv` resolves to a `/nix/store/…` shim containing `typsphinx-fhs-run` (e.g.
  `grep -q typsphinx-fhs-run "$(command -v uv)"`) — the head check Phase 64/65 executors actually
  ran (64 D-09). The provisioning line `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
  and "run everything via `uv run`" stay **byte-identical**. The check must be scoped as
  NixOS-only: CI and non-NixOS contributors have no shims and need none.

**CLAUDE.md content**

- **D-04: A new subsection sits immediately before "Worktree-isolated execution"; that section keeps its recipe and gains one boundary paragraph pointing at it.** The new subsection (name at
  Claude's discretion, e.g. "NixOS development shell") carries: what the shims are (the seven
  documented bare commands run the tree's own `.venv/bin/<tool>` inside an FHS sandbox; a missing
  `.venv/bin/<tool>` fails loudly with exit 127 and a provisioning hint; `uv` alone falls back, to
  nixpkgs' `uv`, for bootstrapping; once `.venv` exists `uv --version` reports the `uv.lock` pin),
  the D-03 prerequisite and check, the D-02 sentence, D-05 and D-06, and a pointer to `flake.nix`'s
  header notes for the rationale.

- **D-05: One sentence on locale, plus an `LC_ALL=C` pre-check.** NIX-08 measured REPRODUCES: the
  sandbox passes `LANG=ja_JP.UTF-8` through unchanged, so Sphinx warning bodies stay Japanese inside
  it exactly as on the host. CI runs in English, so a test asserting warning text should also be run
  under `LC_ALL=C` locally. (Fulfils 64 D-08's promise that this is written up in Phase 68.)

- **D-06: One caution sentence on interpreters.** A fresh worktree's `.venv` is uv-managed CPython
  (3.14 at measurement) while the main checkout's is nixpkgs `python3` (3.13.13, re-measured
  2026-09-12 from `.venv/pyvenv.cfg`); compare both `pyvenv.cfg` `home` / `version_info` before
  comparing test counts between them. Do not name versions as permanent facts — phrase as "may
  differ".

- **D-07: CLAUDE.md carries operational facts only; rationale lives in `flake.nix`'s notes.**
  CLAUDE.md is loaded every session. "What happens / what to do" goes in CLAUDE.md; why `mkShell`
  stays, the falsified alternatives, and namespace inheritance go in `flake.nix` (D-09), referenced
  by one pointer.

- **D-08 — CLAUDE.md:11 and :77 are rewritten to the landed `tox-uv`.** Line 11: `tox` (with
  `tox-uv`). Line 77: `tox.ini` pins `tox-uv~=1.35`, keeping the ini-parser explanation (a single-line
  `requires` is split on commas, so `>=1.35,<2` breaks tox's startup; `~=1.35` is the comma-free
  equivalent), plus a short note that the earlier `tox-uv-bare` pin was needed only because the
  bundled `uv` could not exec on NixOS, which the FHS shims now handle. The "Do not simplify it back
  to `tox-uv`" instruction is removed — it now points the wrong way.

**`flake.nix` notes**

- **D-09: Self-contained prose with no `D-NN` IDs and no time-relative phrasing ("until Phase 65"); the header block ends with a short list of measurement sources.** Source citations must survive
  milestone archival: `.planning/phases/6x-*/` moves to `.planning/milestones/v0.9.3-phases/` at
  `/gsd-complete-milestone`, so cite by milestone + phase + file name (e.g. "v0.9.3 Phase 64,
  `64-NIX05-WORKTREE-EVIDENCE.md`") or by a path that does not move (`.planning/PROJECT.md`), never
  by a `.planning/phases/…` path. The existing `64-LIBZ-FIX-EVIDENCE.md` citation at `flake.nix:30`
  is restated under the same rule.

- **D-10: Layout is a header overview above `outputs` plus short notes beside each element.** Header
  covers: (a) the FHS wrapper — why the devShell stays `mkShell` and the two falsified alternatives
  (`buildFHSEnv`'s `.env` as the devShell leaves `/lib64/ld-linux-x86-64.so.2` resolving to stub-ld
  under both `nix develop` and direnv; a `shellHook` that `exec`s into the wrapper is never run by
  `nix develop` and under direnv replaces only nix-direnv's capture subshell); (b) which commands are
  shimmed and why — the seven are the bare commands `CLAUDE.md` documents, and namespace inheritance
  across `fork`/`exec` means only top-level entrypoints need shims (everything tox/uv spawns is
  already inside); (c) the darwin guard (D-11). Per-element notes: `fhsRun` (why `zlib`), `venvWalk`
  (bounded walk stopping at the first `.git` ancestor; survives `changedir = docs`; a nested worktree
  never resolves the main checkout's `.venv`), the strict shims (no fallback, exit 127), `uvShim`
  (D-12).

- **D-11: The darwin note carries SC#3's mandatory content plus what was actually checked.**
  Mandatory: darwin is unverified by construction — `buildFHSEnv` is Linux-only, no maintainer
  machine can exercise the guard's darwin branch, and no CI lane evaluates `flake.nix` at all — so a
  darwin contributor should report breakage directly (a GitHub issue) rather than assume CI would
  have caught it. Added: the only check performed is `nix eval` of all four systems on a Linux
  evaluator (NIX-06); the darwin shell has never been built or entered; on darwin the shell simply
  carries nixpkgs' `uv`, with no shims.

- **D-12: The `uv` two-leg resolution is described by role, without version numbers, and marked as the single deliberate exception.** Leg 1: the tree's own `.venv/bin/uv` (the `uv.lock` pin, present
  since the `tox-uv` revert). Leg 2: nixpkgs' `uv` at a store path fixed at evaluation time — the
  bootstrap for a fresh clone or worktree that has no `.venv` until its first `uv sync`. State
  plainly that this is the only fallback in the file, so nobody "fixes" the six strict shims into
  being lenient (64 specifics). The stale "does not exist until Phase 65" wording is removed.

**Edit footprint beyond the three named files**

- **D-13: `tests/test_toolchain_config_gate.py` — text only.** The docstring at `:302-304` and the
  assertion message at `:366-368` say CLAUDE.md "still names `tox-uv-bare` as deliberate until
  Phase 68 (DOC-19/DOC-20) rewrites it", which becomes false the moment this phase lands. Rewrite
  those strings to the post-Phase-68 state. Assertion logic, the compared names, and the file's
  other tests are untouched.

- **D-14: `tests/test_pdf_render_gate.py:167` — add one sentence.** The docstring says the `.venv/bin`
  `uv` exit-127 cause "was removed by QUA-04 (`tox-uv` -> `tox-uv-bare`)". Keep that historical
  sentence and add that the `tox-uv` revert put `.venv/bin/uv` back, and on NixOS it now runs through
  the FHS shims; the closing "`sys.executable -m sphinx` is kept regardless" reasoning stays. No code
  change.

- **D-15: SC#2's repository-wide grep excludes `.planning/` and `uv.lock` and classifies every remaining hit.** Command: `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'`. Every hit
  is transcribed into the evidence table and classified as *historical and accurate*, *named by a test
  as the forbidden value*, or *rationale presented as current*. SC#2 is MET only when the last class
  has zero rows. `uv.lock` is excluded because `tox-uv-bare` is legitimately `tox-uv`'s exact-version
  transitive dependency there.

- **D-16: `tox.ini`'s new comment keeps a one-to-two-sentence history.** Required content: the current
  `tox-uv~=1.35` pin; the ini-parser constraint stated in full (tox's ini-list loader splits a
  single-line `requires` on commas, so `>=1.35,<2` is parsed as two bogus requirements and tox fails
  to start; `~=1.35` is the comma-free equivalent); why `tox-uv` is safe now (on NixOS the FHS shims
  run `tox`, so its bundled `uv` executes; CI runners were never affected). Plus: the pin was briefly
  `tox-uv-bare` because the bundled `uv` could not exec on NixOS outside FHS. The old
  `D-07` / `04-01-SUMMARY.md` citations follow D-09's rule (restate self-contained, or cite in an
  archive-stable form).

### Claude's Discretion

- Exact wording, subsection name, and sentence order in CLAUDE.md, within D-04..D-08.
- Exact wording of the `flake.nix` header and per-element notes, within D-09..D-12.
- Whether the header lists the seven shim names or refers to the `venvShimNames` list plus `uv`.
- Plan split and evidence file naming (Phase 64 D-05 convention: verbatim transcripts in phase
  evidence markdown; no new script, no new test).

### Deferred Ideas (OUT OF SCOPE)

- Maintainer auto-memory `nixos-sandbox-test-env.md` still carries pre-Phase-64 "ruff does not run in
  a fresh worktree" guidance. Outside the repository and not a phase deliverable; updated by the
  orchestrator at discussion close.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — keyword match only; forbidden by
  `CLAUDE.md` and constraint 13.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` —
  translator defect; `typsphinx/` change, constraint 13.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — docs rendering,
  unrelated.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` —
  `typsphinx/` change, constraint 13.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — workflow addition, constraint 3.

**Out of scope (from ROADMAP/CONTEXT, restated for the planner):** anything under `typsphinx/`;
any `.github/workflows/` edit; `pyproject.toml`, `uv.lock`, the `requires` value itself; the
shell-script bodies inside `flake.nix`; the CHANGELOG (Phase 69).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-19 | `CLAUDE.md`'s NixOS / worktree-provisioning section describes the landed mechanism and no longer instructs a manual shim step | § Current Text Inventory (CLAUDE.md), § Measured Facts the New Text Must Report, § Wave Plan |
| DOC-20 | `tox.ini`'s `tox-uv-bare` rationale comment is replaced by one describing the current pin, keeping the `~=` ini-parser constraint stated | § Current Text Inventory (tox.ini), § D-15 Grep Classification (proves this edit is necessary and sufficient for SC#2) |
| DOC-21 | `flake.nix` carries notes explaining the FHS wrapper, which commands are shimmed and why, and the darwin guard | § Current Text Inventory (flake.nix), § Measured Facts the New Text Must Report, § Derivation-Identity Gate |
</phase_requirements>

## Summary

This is a pure documentation-correction phase: three files (`CLAUDE.md`, `tox.ini`, `flake.nix`)
plus two test files' prose (`tests/test_toolchain_config_gate.py`,
`tests/test_pdf_render_gate.py`) get their text brought into line with what Phases 64–65 actually
built and measured. No product code, no `pyproject.toml`/`uv.lock`, no CI workflow, and no new
dependency is touched. The research below is therefore not "which library to use" but three things
the planner cannot get from CONTEXT.md alone: (1) the **exact current text** at every cited site,
quoted verbatim so the executor edits the right bytes; (2) the **exact measured facts** the new
text must report, quoted from the Phase 64/65 evidence files that are the sole source of truth;
(3) a **hazard census** proving no test, script, or workflow other than the two named test files
parses the content of these three documents, so the edit is safe to parallelize.

The most load-bearing finding of this research: **the CONTEXT.md edit footprint is not merely
plausible, it is measured-exhaustive for SC#2.** Running `git grep -n tox-uv-bare -- ':!.planning'
':!uv.lock'` today and classifying all 27 hits shows exactly six lines fall into "rationale
presented as current" (`CLAUDE.md:11`, `CLAUDE.md:77`, `tox.ini:4`, `tox.ini:7`,
`tests/test_toolchain_config_gate.py:302-304`, `tests/test_toolchain_config_gate.py:366-368`) —
and every one of those six lines is already inside the D-08/D-13/D-16 edit footprint. No sixth
file, no missed line, needs discovery.

**Primary recommendation:** run the CLAUDE.md, tox.ini, flake.nix, and test-file edits as four
independent wave-1 plans (they touch disjoint files and nothing parses their prose except the two
named tests), then run the D-15 repository-wide grep classification and the green-tree gate as a
single wave-2 evidence plan that reads the *merged* wave-1 tree — never in the same wave as the
edits it measures.

## Architectural Responsibility Map

This phase has no browser/API/database tiers — it is pure prose living beside build/tooling
config. The map below substitutes "which surface owns which fact" for the usual tier table.

| Capability | Primary Owner | Secondary Owner | Rationale |
|------------|---------------|------------------|-----------|
| "What to do" (operational recipe: provisioning line, shim check, `LC_ALL=C` pre-check) | `CLAUDE.md` (loaded every session, D-07) | — | Executors read this file first; it must be actionable without following a pointer |
| "Why it's built this way" (falsified `buildFHSEnv`/`shellHook` alternatives, two-leg `uv` resolution, namespace inheritance) | `flake.nix` header comment (D-07, D-09) | `CLAUDE.md` pointer sentence | Rationale that only a Nix maintainer needs, kept out of the session-loaded file per D-07 |
| tox `requires=` parser workaround rationale | `tox.ini`'s own comment (D-16) | `CLAUDE.md:77` (one-line summary, D-08) | The comment lives directly beside the line it explains; `configparser` strips comments, so this text carries zero runtime coupling |
| "This assertion's forbidden/required value is X" | Python assertion code + message (`tests/test_toolchain_config_gate.py`, untouched logic) | — | D-13 touches only the *stale self-reference* inside the message, not the assertion itself |
| "Darwin is unverified by construction" | `flake.nix` per-system guard note (D-11) | ROADMAP constraint 8 (already states this) | The only place a darwin contributor will look before filing an issue |

## Current Text Inventory (verbatim, HEAD, read this session)

Every quote below was obtained via `Read` in this session against the files at the tip of
`gsd/v0.9.3-toolchain-and-dependency-update-repair` (`89416753`). Line numbers match `git grep -n`
output taken in the same session — **no line-number drift** between the two tools was observed.

### `CLAUDE.md`

`CLAUDE.md:11` [VERIFIED: CLAUDE.md:11] — the D-08 target:
```
Development uses `uv` for env/dependency management and `tox` (with `tox-uv-bare`) as the task runner.
```

`CLAUDE.md:77` [VERIFIED: CLAUDE.md:77] — the D-08 target (one line, wrapped in source):
```
- `tox.ini` pins `tox-uv-bare~=1.35` (not `>=1.35,<2`) deliberately — see the comment in that file; tox's ini parser splits a single-line `requires` on commas and breaks otherwise. The `-bare` package is also deliberate (QUA-04, Phase 45.2): the plain `tox-uv` meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()` searches `.venv/bin` first and reads no environment variable. Do not "simplify" it back to `tox-uv`.
```

`CLAUDE.md:73` (section header, for context — this string is NOT edited; a test pointer at
`tests/test_toolchain_config_gate.py:164` refers to it by name and must keep resolving):
```
## Conventions & gotchas
```

`CLAUDE.md:80-96` [VERIFIED: CLAUDE.md:80-96] — the "Worktree-isolated execution" section D-04
says gains one boundary paragraph, and whose recipe (lines 87-89) D-01/D-03 require to stay
**byte-identical**:
```
### Worktree-isolated execution

**Detection rule:** you are running inside an isolated git worktree when `.git` is a FILE (a `gitdir:` pointer), not a directory — check with `test -f .git`. Sequential main-tree execution has `.git` as a directory and needs none of the steps below.

When operating inside a worktree, provision the worktree's own environment before running anything:

    env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
    uv run pytest   # run ALL subsequent commands via `uv run`

1. **Provision first.** `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` unsets those two vars so `uv` creates a fresh worktree-local `.venv` instead of syncing into an already-activated main venv and re-pointing it at the worktree.
2. **Run everything via `uv run`.** e.g. `uv run pytest …`. Inside the test fixtures, Sphinx is still invoked as `sys.executable -m sphinx`, which under `uv run` resolves to the worktree venv's python — so `import typsphinx` binds to the worktree's editable copy. This complements the existing NixOS `sys.executable -m sphinx` guidance and does not contradict it.

**Rationale:** the main `.venv` holds a PEP-660 editable finder (`__editable__.typsphinx-*.pth`) that resolves `import typsphinx` to the MAIN checkout's absolute path (`/…/typsphinx/typsphinx`), and `.venv` is gitignored so a fresh worktree starts with no venv of its own. Without the per-worktree `uv sync` + `uv run`, a worktree executor edits files in the worktree but pytest imports the UNCHANGED main-tree package — gates stay RED after a correct fix, and later waves don't see earlier waves' changes. Verified 2026-07-20 that a worktree `uv sync` + `uv run` is isolated (main `.venv` untouched) and works under the NixOS sandbox.

**Applicability — worktree isolation is the STANDING execution mode (project owner's decision, 2026-07-20).** ...
```
(the `Applicability` paragraph continues to the file's last line, 96; its content is standing
project policy about worktree defaults, not about `flake.nix`, and D-04 does not ask for it to be
touched — the new boundary paragraph is additive, placed per D-04's instruction "immediately before"
this whole section, i.e. as a new `###` subsection inserted between `## Conventions & gotchas`'s
last bullet (line 78, CI/drift/release description — untouched) and this `### Worktree-isolated
execution` heading).

**Pitfall for the planner:** do not rename or remove the `## Conventions & gotchas` heading (line
73) or its position — `tests/test_toolchain_config_gate.py:164` cites it by exact string
(`CLAUDE.md 'Conventions & gotchas'`) as a pointer, and that citation is **not** part of the D-13
edit footprint (only `:302-304` and `:366-368` are). If the heading text changes, that pointer goes
stale silently (no test currently checks it), which would be a new, unplanned defect this phase
should not introduce.

### `tox.ini`

`tox.ini:1-11` [VERIFIED: tox.ini:1-11] — the full rationale block D-16 replaces (lines 4-10) plus
the untouched `requires=` line (11) that D-16 explicitly must NOT change:
```
[tox]
env_list = py312, py313, lint, type, cov, docs
isolated_build = True
# tox-uv-bare pinned via ~= (not >=1.35,<2): tox's own ini-list loader splits
# single-line `requires` values on "," (only multi-*entry* lists preserve
# newline-splitting), so a literal ">=1.35,<2" is parsed as two bogus
# requirements ("tox-uv-bare>=1.35" and "<2") and tox fails to even start.
# ~=1.35 is the packaging-spec equivalent of >=1.35,<2 (see D-07) with no
# comma, sidestepping the parser bug. Verified equivalent via
# `packaging.specifiers.SpecifierSet` in 04-01-SUMMARY.md.
requires = tox-uv~=1.35
```

`tox.ini:19-32` [VERIFIED: tox.ini:19-32] — **confirmed distinct and NOT part of the edit
footprint** (the `package = editable` rationale CONTEXT.md's Measured State paragraph names):
```
[testenv]
description = Run tests with pytest
# package = editable (uv-venv-lock-runner's own default, stated explicitly here
# rather than left implicit): a non-editable `package = wheel` build was the
# prior setting here, and 45.2-05's CI dispatch (SC#4) proved it silently
# dropped `typsphinx/templates/base.typ` from the installed package under
# CI's uv (0.12.3), though not under this machine's (0.11.25) -- 23 pytest
# failures across py312/py313/cov, all `FileNotFoundError: Default template
# not found`. Those three environments' pytest had previously always
# resolved against the OUTER editable `.venv` via the exact same
# PATH-shadowing mechanism D-04 diagnosed for `lint`'s tools, so this wheel-
# mode packaging gap was never actually exercised until `extras = dev` (D-02)
# made each environment self-contained. `package = editable` matches what the
# outer `uv sync --extra dev` already does successfully, and removes the
# wheel-build step. See 45.2-05-SUMMARY.md and
# 45.2-TOOLCHAIN-EVIDENCE.md Step 8 for the transcript.
package = editable
```
This confirms CONTEXT.md's own measured-state claim ("the unrelated `package = editable` comment
(lines 19-32) are untouched") is accurate — the two blocks are topically and structurally distinct
(one explains the `requires=` line's comma-parsing hazard, the other explains a packaging-mode
choice for `[testenv]`), separated by 8 blank/section lines. Low risk of accidental cross-edit, but
worth flagging explicitly since both blocks mention `tox`, `uv`, and Phase 45.2.

**Safety note (verified this session):** `configparser` (what
`tests/test_toolchain_config_gate.py::_load_tox_ini` uses, confirmed by `Read`) strips `#`-comment
lines before returning key/value pairs. Editing either comment block therefore cannot affect any
gate's parsed result — the `requires = tox-uv~=1.35` value and the `package = editable` value are
the only bytes any test observes structurally.

### `flake.nix`

All five ranges below are `[VERIFIED: flake.nix:<range>]`, read this session, and match the
orchestrator's cited ranges exactly.

`flake.nix:26-31` (the D-10 `fhsRun` per-element note target):
```
          fhsRun = pkgs.buildFHSEnv {
            name = "typsphinx-fhs-run";
            # Pillow's `_imaging` extension carries a bare `NEEDED libz.so.1`, and
            # uv-managed CPython links zlib statically, so nothing in the process
            # ever maps it without this entry. See 64-LIBZ-FIX-EVIDENCE.md.
            targetPkgs = p: [ p.zlib ];
```

`flake.nix:37-42` (the D-10 `venvWalk` per-element note target):
```
          # Bounded upward walk from $PWD looking for .venv/bin/<tool>, stopping
          # at the first ancestor holding a .git entry (a file in a worktree, a
          # directory in the main checkout) or at /. This survives tox's own
          # `changedir = docs` (docs-html/docs-pdf) and never leaves the
          # checkout it started in, so a nested executor worktree can never
          # resolve the main checkout's .venv.
```

`flake.nix:63-66` (the D-10 "strict shims, no fallback" note target):
```
          # D-03: the six venv shims have no fallback. A missing
          # .venv/bin/<tool> is a hard, loud failure -- naming the tool and the
          # directory the walk started from, then exiting non-zero (127, the
          # shell's own command-not-found status).
```

`flake.nix:74-75` (the D-09 "no `D-NN` IDs" target — this comment names both D-01 and D-02):
```
          # D-01: the full seven-name roster is these six strict venv shims
          # plus `uv` (uvShim below, D-02's sole documented exception).
```

`flake.nix:92-97` (the D-12 `uvShim` note target — carries the stale "does not exist until Phase
65" phrasing D-09/D-12 both explicitly require removed):
```
          # D-02: `uv` resolves in two legs. Leg 1 is the same bounded upward
          # walk for .venv/bin/uv (it does not exist until Phase 65's tox-uv
          # revert installs it). Leg 2, the on-stop fragment, is the fixed
          # nixpkgs store path -- fixed at flake-evaluation time and therefore
          # un-shadowable. Both legs enter the sandbox, which is what makes
          # `uv run <tool>` carry FHS into every downstream process.
```

**Verified fact that changes the phrasing:** `.venv/bin/uv` does **not** "not exist until Phase
65" anymore — Phase 65 already landed (`65-REVERT-EVIDENCE.md`, `65-01`/`65-02` merged). The main
checkout's `.venv/bin/uv` exists today:
```
$ command -v uv && grep -c typsphinx-fhs-run "$(command -v uv)"
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
2
```
[VERIFIED: session command, 2026-09-12] — confirms CONTEXT.md's "Measured state at discussion
time" paragraph and gives the exact D-03 check shape (`grep -c typsphinx-fhs-run` returns 2 for
`uv`'s shim, since its body references `typsphinx-fhs-run` on both the venv-walk leg and the
nixpkgs-fallback leg — matches `64-NIX05-WORKTREE-EVIDENCE.md`'s identical `grep -c … uv` = 2
finding for a worktree's shim).

Also present, `flake.nix:76-83` (`venvShimNames` list, quoted verbatim so the planner does not
have to guess the "seven-name roster" D-10's Claude's-Discretion note references):
```
          venvShimNames = [
            "tox"
            "ruff"
            "black"
            "mypy"
            "pytest"
            "sphinx-build"
          ];
```
(six strict names; the seventh is `uv`, defined separately as `uvShim` at line 98.)

### `tests/test_toolchain_config_gate.py`

`:302-304` [VERIFIED: tests/test_toolchain_config_gate.py:302-304] — the D-13 docstring target
(self-referential, becomes false the moment this phase lands):
```
    CLAUDE.md's own "Conventions & gotchas" sentence still names `tox-uv-bare` as
    deliberate -- that sentence goes stale as of this revert and is rewritten in
    Phase 68 (DOC-19/DOC-20), not here (D-06).
```

`:358-369` [VERIFIED: tests/test_toolchain_config_gate.py:358-369] — the full assertion whose
message's tail (`:366-368`) is the D-13 target; the assertion **code** (`:359`) and the earlier
message lines (`:360-365`) are untouched:
```
    # G5 requirement 2 (Phase 65 revert): dev extra MUST NOT name tox-uv-bare directly.
    assert canonicalize_name("tox-uv-bare") not in dev_names, (
        "dev extra names 'tox-uv-bare' directly (on normalized distribution name) -- "
        "this is the stale Phase 45.2 workaround pin that Phase 65's revert (TOX-01) "
        "removes now that Phase 64's FHS shims dissolve the stub-ld defect (QUA-04) that "
        "motivated it. tox-uv-bare stays present only as tox-uv's own exact-version "
        "transitive dependency in uv.lock, which is expected and not what this assertion "
        "forbids -- it forbids the dev extra naming tox-uv-bare as a literal entry in "
        "pyproject.toml. See 65-REVERT-EVIDENCE.md for the lock regeneration proof "
        "(TOX-01, D-04) and CLAUDE.md 'Conventions & gotchas', which still names "
        "tox-uv-bare as deliberate until Phase 68 (DOC-19/DOC-20) rewrites it."
    )
```
(`:366-368` is the last three string-literal lines above, starting `"pyproject.toml. See
65-REVERT-EVIDENCE.md…"` through the closing `)`.)

### `tests/test_pdf_render_gate.py`

`:150-171` [VERIFIED: tests/test_pdf_render_gate.py:150-171] — the D-14 target docstring (`:167`
is the historical sentence D-14 says to *keep*; D-14 adds new content after it, before `:168-171`'s
closing reasoning, which also stays):
```
def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as `sys.executable -m sphinx` (the sphinx-build console entry
    point's module form) rather than shelling out to `uv run sphinx-build`:
    this guarantees the exact interpreter/venv already running this test is
    reused, with no dependency on external PATH resolution of a `uv`
    executable. This mattered in this project's dev sandbox specifically --
    a stray non-Nix `uv` binary installed into `.venv/bin` (shadowing the
    correct Nix-provided `uv` earlier on PATH for subprocess children) made
    `["uv", "run", ...]` exit 127 ("Could not start dynamically linked
    executable") when invoked from inside a pytest-launched subprocess, even
    though the same command succeeded when run directly in a shell. That
    cause was removed by QUA-04 (2026-08-10; `tox-uv` -> `tox-uv-bare` drops
    the bundled generic-linux `uv` wheel binary). `sys.executable -m sphinx`
    is kept regardless, because it depends on no PATH resolution at all --
    a better reason than the hazard ever was, and one that holds no matter
    what is installed in `.venv/bin`.
```
D-14's required addition: the `tox-uv` revert (Phase 65) put `.venv/bin/uv` back, and on this
machine it now runs through the Phase 64 FHS shims rather than bare — so the QUA-04-era hazard
this docstring recalls no longer applies to a fresh `.venv/bin/uv`, but `sys.executable -m sphinx`
is kept regardless (closing sentence, unchanged) because it depends on no PATH resolution at all.

## Measured Facts the New Text Must Report

Every fact below is `[VERIFIED: <evidence file>]` — a direct quote or transcription from a Phase
64/65 evidence file, re-checked this session where a live command was cheap to re-run.

**The seven shim names** [VERIFIED: flake.nix:76-83, 98]: `tox`, `ruff`, `black`, `mypy`, `pytest`,
`sphinx-build` (the six strict `venvShimNames`), plus `uv` (`uvShim`, the sole documented
exception with a fallback leg).

**Strict-shim exit 127 and its message** [VERIFIED: flake.nix:67-72]:
```
          venvShimOnStop =
            tool:
            ''
              echo "typsphinx-shim: ${tool}: no executable .venv/bin/${tool} found walking up from $start (stopped at $dir); provision with: env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev" >&2
              exit 127
            '';
```
This is the exact stderr line and exit code CLAUDE.md's D-04 subsection should describe ("a
missing `.venv/bin/<tool>` fails loudly with exit 127 and a provisioning hint") — the shim's own
message already contains the provisioning line verbatim, so CLAUDE.md can quote it rather than
re-derive it.

**The `uv` two-leg resolution, observed live in a worktree** [VERIFIED:
`64-NIX05-WORKTREE-EVIDENCE.md` lines quoted below]:
```
+ '[' -x /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.venv/bin/uv ']'
+ '[' -e /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.git ']'
+ break
+ exec /nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv --version
```
(pre-Phase-65 worktree, `.venv/bin/uv` absent, so leg 1 falls through and leg 2's fixed nixpkgs
store path fires). Post-Phase-65, on the main checkout, leg 1 fires instead
(`65-REVERT-EVIDENCE.md` "Addendum: main-checkout re-sync"): `uv --version` reports `0.12.13` —
the `uv.lock`-pinned version — once `.venv/bin/uv` exists.

**NIX-05 (worktree PATH inheritance, not direnv)** [VERIFIED: `64-NIX05-WORKTREE-EVIDENCE.md`]:
```
$ direnv status 2>&1 | grep -E 'RC'
Loaded RC path /home/yuta/Documents/typsphinx/.envrc
Loaded RC allowed 0
...
Found RC path /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5539e9d70a2734f2/.envrc
Found RC allowed 1
```
"`Loaded RC`" (allowed 0 = allowed) is the **main checkout's** `.envrc`, the source of this
session's frozen PATH; "`Found RC`" (allowed 1 = **not** allowed) is the worktree's own `.envrc`,
walked-up-to by `direnv status` but never individually `direnv allow`-ed. This is the single
sentence that resolves the AMENDED block's substance: the shim PATH in a worktree is inherited,
never locally granted.

**Worktree `.venv` on uv-managed CPython, host-incompatible** [VERIFIED:
`64-NIX08-ENV-EVIDENCE.md`]:
```
$ .venv/bin/python -c "..."
Could not start dynamically linked executable: .venv/bin/python
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```
and `.venv/pyvenv.cfg` in that same worktree: `home =
/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin`, `version_info = 3.14`
[VERIFIED: `64-NIX05-WORKTREE-EVIDENCE.md`]. The main checkout's own `.venv/pyvenv.cfg` (re-read
this session):
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
version_info = 3.13.13
```
[VERIFIED: `65-REVERT-EVIDENCE.md` "Addendum" — `sed -n 's/^home = //p;s/^version_info = //p'
.venv/pyvenv.cfg` output, re-derivable in this session via the identical command]. This is D-06's
exact evidence: a fresh worktree's `.venv` is uv-managed CPython while the main checkout's is
nixpkgs `python3` — compare both `pyvenv.cfg`s before comparing test counts.

**NIX-08 locale finding: REPRODUCES** [VERIFIED: `64-NIX08-ENV-EVIDENCE.md` § "Four-cell matrix"]:
```
| Cell | Warning line |
| H-ja | ...ドキュメントはどの toctree にも含まれていません [toc.not_included] |
| H-C  | ...document isn't included in any toctree [toc.not_included] |
| S-ja | ...ドキュメントはどの toctree にも含まれていません [toc.not_included] |
| S-C  | ...document isn't included in any toctree [toc.not_included] |
```
"**Finding: REPRODUCES**" — the FHS sandbox passes `LANG=ja_JP.UTF-8` through unchanged; a
warning's locale-dependent body text behaves identically inside the sandbox and on the bare host.
This is exactly D-05's "one sentence on locale, plus an `LC_ALL=C` pre-check" content.

**NIX-06 (four-system `nix eval`), re-confirmed live this session** [VERIFIED: session command,
2026-09-12, main checkout, current HEAD]:
```
$ for s in x86_64-linux aarch64-linux x86_64-darwin aarch64-darwin; do
    nix eval --raw .#devShells.$s.default.drvPath; done
warning: Git tree '/home/yuta/Documents/typsphinx' is dirty
/nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv
warning: Git tree '/home/yuta/Documents/typsphinx' is dirty
/nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv
warning: Git tree '/home/yuta/Documents/typsphinx' is dirty
evaluation warning: Nixpkgs 26.05 will be the last release to support x86_64-darwin; ...
/nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv
warning: Git tree '/home/yuta/Documents/typsphinx' is dirty
/nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv
```
All four systems evaluate successfully (matches `64-FLAKE-EVIDENCE.md`/`64-LIBZ-FIX-EVIDENCE.md`'s
NIX-06 values exactly, byte-for-byte, since no `flake.nix` code has changed since Phase 64). Total
wall time for all four: **1.6 seconds** (`time` output, this session) — cheap enough to run
before-and-after inside a single plan without a noticeable cost. `nix --version` in this
environment: `nix (Nix) 2.34.8`.

**The `zlib` reason** [VERIFIED: `64-LIBZ-FIX-EVIDENCE.md` "The edit" and "RED" sections]: Pillow's
`_imaging` extension carries a bare `NEEDED libz.so.1`; uv-managed CPython links zlib statically,
so nothing in the FHS sandbox process ever maps `libz.so.1` without `targetPkgs = p: [ p.zlib ];`.
Reproduced (RED) for all three interpreter builds (`.venv` uv-cp3.14, `.tox/py312` uv-cp3.12,
`.tox/py313` nix-cp3.13) before the fix, and fixed (GREEN) for all three after — this is a
Pillow/CPython-linkage fact, not a `tox`/`uv` fact, so it belongs in `flake.nix`'s `fhsRun`
per-element note, not in CLAUDE.md (D-07's split).

**65-REVERT's `using bundled uv from: <tree>/.venv/bin/uv`** [VERIFIED:
`65-REVERT-EVIDENCE.md` § "TOX-03 D-02 observation inside FHS"]:
```
py312: 87 D using bundled uv from: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3ca8472e956ebe27/.venv/bin/uv [tox_uv/_venv.py:237]
```
This is the observed-from-inside-tox proof that `tox-uv`'s bundled-`uv` discovery branch resolves
the worktree's own `.venv/bin/uv` under the Phase 64 shims — the mechanism `flake.nix`'s D-12 note
and `tox.ini`'s D-16 comment both need to state as "why `tox-uv` is safe now."

**ROADMAP SC#1 AMENDED block is already present** [VERIFIED: `.planning/ROADMAP.md:646-658`,
read this session] — confirmed verbatim; D-01 requires no further ROADMAP edit in this phase, only
that CLAUDE.md's text agree with it.

## Hazard Census — what reads the content of these three files

Searched `tests/`, `scripts/`, `docs/`, `.github/` for the filenames `CLAUDE.md`, `tox.ini`,
`flake.nix`, and for the strings `tox-uv-bare`, `requires`, `typsphinx-fhs-run`, `venvShimNames`,
`Worktree-isolated` [VERIFIED: session `git grep` commands].

| File / mechanism | What reads it | Risk to this phase |
|---|---|---|
| `tests/test_toolchain_config_gate.py` | Parses `tox.ini` **structurally** via `configparser` (comments stripped — verified: only `requires=` and `package=` values are read) and `pyproject.toml` via `tomllib`; also contains **prose** referencing `CLAUDE.md` by quote (`:164`, `:302-304`, `:367`) | D-13's exact scope (`:302-304`, `:366-368`); `:164`'s pointer must survive (heading text untouched) |
| `tests/test_pdf_render_gate.py` | Prose only, no structural parse of any of the three files | D-14's exact scope (`:167` extended) |
| `.github/workflows/*.yml` (`ci.yml`, `docs.yml`, `drift.yml`, `links.yml`, `release.yml`) | `grep -rliE 'nix\|flake\|CLAUDE\.md' .github/workflows/` → **zero hits** [VERIFIED: session command] | None — confirms ROADMAP's "zero CI coverage for `flake.nix`" claim (D-11) directly, not just by citation |
| `docs/source/*.rst` | `docs/source/contributing.rst:130` mentions "The tox configuration is defined in ``tox.ini``" but does not quote its rationale comment or `tox-uv-bare` | None — no `tox-uv-bare` or `flake.nix` string anywhere under `docs/source/` [VERIFIED: session `grep`] |
| `scripts/*.py` | No match for `tox-uv-bare`, `flake.nix`, or `CLAUDE.md` [VERIFIED: session `grep`] | None |
| `CHANGELOG.md` | Two old, unrelated `CLAUDE.md` mentions from prior milestones (v0.6.3-era DOC-01–05); no `tox-uv-bare`/`flake.nix` string | None — and CHANGELOG is explicitly Phase 69's scope, not this phase's |
| `tests/fixtures/**/*.typ` | ~16 fixture files reference `CLAUDE.md` by name, but only for the unrelated `@preview` version-sync hazard ("fourth/fifth version-lockstep site") — a different section of CLAUDE.md than any line this phase edits | None |

**Conclusion:** the only test assertions that can regress from this phase's edits are the two
named in D-13/D-14, and both are in-scope, text-only changes with no logic touched. No CI workflow
observes `flake.nix` at all (re-confirmed live, not just cited). No script or doc file needs a
companion edit.

## D-15 Grep Classification (measured today, before any Phase 68 edit)

Command run this session, exactly as D-15 specifies: `git grep -n tox-uv-bare -- ':!.planning'
':!uv.lock'` [VERIFIED: session command, 27 hits]. Classified per D-15's three buckets.

| # | Location | Class | Why |
|---|---|---|---|
| 1 | `CLAUDE.md:11` | **C3 — rationale presented as current** | States `tox-uv-bare` is the task runner now; false since Phase 65 |
| 2 | `CLAUDE.md:77` | **C3** | States the `tox-uv-bare~=1.35` pin and "do not simplify back to `tox-uv`" — inverted by the Phase 65 revert |
| 3 | `tests/test_pdf_render_gate.py:167` | C1 — historical, accurate | Correctly describes the QUA-04-era `tox-uv → tox-uv-bare` move as a past event |
| 4 | `tests/test_toolchain_config_gate.py:6` | C1 | "Phase 45.2's migration from tox-uv to tox-uv-bare" — accurate history |
| 5 | `:36` | C2 — named as forbidden value | Gate docstring states the current MUST/MUST NOT pair |
| 6 | `:41` | C1 | "stub-ld defect QUA-04 fixed by moving to tox-uv-bare no longer bites" — accurate |
| 7 | `:46` | C1 | Citation to `65-REVERT-EVIDENCE.md` |
| 8 | `:51` | C2 | Names the gate's two compared distribution names |
| 9 | `:269` | C2 | Docstring MUST/MUST NOT statement |
| 10 | `:276` | C1 | Accurate mechanism history |
| 11 | `:289` | C1 | "Naming trap" substring explanation — still true today |
| 12 | `:297` | C1 | Accurate current-state explanation of the transitive dependency |
| 13 | `:300` | C2 | States what the assertion forbids |
| 14 | `:302` (block `302-304`) | **C3 — self-referential, becomes false** | "CLAUDE.md's own sentence still names tox-uv-bare as deliberate ... rewritten in Phase 68" — this line itself goes stale once Phase 68 lands |
| 15 | `:307` | C1 | Citation |
| 16 | `:358` | C2 | Comment naming the forbidden value |
| 17 | `:359` | C2 | Assertion code (untouched) |
| 18 | `:360` | C2 | Assertion message |
| 19 | `:363` | C1 | Accurate: describes `tox-uv-bare`'s legitimate transitive presence |
| 20 | `:365` | C2 | Assertion message, states forbidden literal-entry meaning |
| 21 | `:368` (block `366-368`) | **C3 — self-referential** | "...until Phase 68 (DOC-19/DOC-20) rewrites it." — same class as #14 |
| 22 | `:373` | C2 | Docstring MUST NOT list |
| 23 | `:395` | C2 | Forbidden-list description |
| 24 | `:437` | C2 | Code: `forbidden_packages` set (untouched) |
| 25 | `:444` | C1 | Historical: Phase 45.2's original toolchain-package move |
| 26 | `tox.ini:4` | **C3** | Opening line of the stale rationale block |
| 27 | `tox.ini:7` | **C3** | Mid-block line, part of the same stale rationale block |

**C3 total: 6 rows, spanning exactly 4 locations** — `CLAUDE.md` (2 lines), `tox.ini` (2 lines,
one contiguous comment block), `tests/test_toolchain_config_gate.py` (2 blocks: `302-304` and
`366-368`). **Every C3 row is already inside the D-08/D-13/D-16 edit footprint.** This is a
positive, falsifiable proof that the CONTEXT.md edit footprint is sufficient for SC#2 — the
planner does not need to search for a fifth file or a missed line; none exists as of this
measurement. (A second run of the identical grep, after the wave-1 edits land, is still required
as evidence — see § Wave Plan — because this table is a *prediction* based on today's tree, not a
substitute for measuring the merged tree.)

## Derivation-Identity Gate (for the `flake.nix` comment-only edit)

Because D-09..D-12 touch only `#` comments outside any `''…''` string, the devShell's derivation
must be byte-identical before and after. Recommended procedure inside the `flake.nix` plan's own
worktree:

1. Before editing, record `nix eval --raw .#devShells.{system}.default.drvPath` for all four
   systems (fast: **1.6s total**, measured this session).
2. Make the comment-only edit.
3. Re-run the same four `nix eval` commands; assert each drvPath is byte-identical to step 1.
4. Also re-run `nix flake check --all-systems --no-build` (used previously in
   `64-FLAKE-EVIDENCE.md`/`64-LIBZ-FIX-EVIDENCE.md` for the identical purpose) as a second,
   independent confirmation.

**Confirmed this session: `nix eval` evaluates the working tree including uncommitted edits to
tracked files.** Running the four-system eval against this session's tree (which had one
uncommitted modification to a tracked `.planning/` file) printed `warning: Git tree
'/home/yuta/Documents/typsphinx' is dirty` on every invocation and still returned the correct,
current drvPaths — so step 1/step 3 do **not** require a commit between them; an uncommitted
edit is visible to the evaluator (with a stderr warning, not an error) [VERIFIED: session
command].

**Can this run from inside a worktree?** Yes — already proven, not merely assumed. Both
`64-NIX05-WORKTREE-EVIDENCE.md`... no — correction: `64-FLAKE-EVIDENCE.md` and
`64-LIBZ-FIX-EVIDENCE.md` both ran `nix eval --raw .#devShells.{system}.default.drvPath` from
*inside* a freshly created git worktree (`.git` a file, confirmed via `test -f .git && echo
IS_WORKTREE` in the same evidence file) and got correct results, including all four systems and
`nix flake check --all-systems --no-build`. The planner does not need a fresh read-only probe for
this — it is already observed, twice, in the cited evidence.

## Green-Tree Gate Method

D-06 establishes that a worktree's `.venv` may run a different CPython than the main checkout
(uv-managed 3.14 vs. nixpkgs 3.13.13), so a naive "compare this run's test count to a number
written in an old evidence file" is fragile — the numbers can differ for reasons unrelated to this
phase's edits. Recommended method, robust to that divergence:

1. **Compare within the same worktree, not across worktrees or against a stale baseline.**
   Immediately after `uv sync --extra dev` provisions the plan's worktree, run
   `pytest --collect-only -q` and record the "N tests collected" line — this is the pre-edit
   baseline for *that* worktree's own interpreter.
2. Make the text-only edit (CLAUDE.md / tox.ini / flake.nix / the two test files, whichever this
   plan owns).
3. Re-run `pytest --collect-only -q` in the same worktree. The collected count must be identical
   (text-only edits to docstrings/messages/comments cannot add or remove test functions).
   [VERIFIED, this session, main checkout: `1548 tests collected` — matches the count independently
   recorded in `64-NIX05-WORKTREE-EVIDENCE.md`'s fresh-worktree run, so this number is stable
   across at least two different interpreter/tree combinations and is a safe sanity anchor,
   **not** the gate itself — the gate is the plan's own before/after match, not this absolute
   number.]
4. For the plan touching the two test files specifically, additionally run
   `pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q` before and after
   — both must report the same pass count (4 passed for the toolchain gate file, per
   `65-REVERT-EVIDENCE.md`'s own transcript), proving the docstring/message edit did not
   accidentally touch executable code.
5. `black --check .` and `ruff check .` on the full tree (or scoped to the two edited files if the
   plan prefers a faster check) — both tools ignore comments/docstrings for correctness but do
   enforce formatting *inside* them (line length, quote style); run them for real rather than
   assuming text edits are exempt.
6. CI remains the authority for the Windows/macOS lanes per project convention, but this phase
   touches no code CI executes differently — a CI dispatch is not required by any Success
   Criterion here (contrast with Phase 65's TOX-04, which explicitly required one). No plan in
   this phase should add one on its own initiative.

## Wave Plan Recommendation

**Wave 1 — four independent plans, disjoint files, no shared state:**

| Plan | Files | Decisions | Notes |
|---|---|---|---|
| A | `CLAUDE.md` | D-01..D-08 | Also carries the D-02 evidence transcription (`git log -S` × 2, `git grep`) as this plan's own supporting evidence, since it directly motivates this plan's new sentence |
| B | `tox.ini` (lines 4-10 only) | D-16 | Verify `tox config -e py312 --core -k requires` still prints `tox-uv~=1.35` after the comment edit (it will — `configparser`/tox's parser never reads comments) |
| C | `flake.nix` (comments only) | D-09..D-12 | Includes the before/after derivation-identity gate (§ above) inside this same plan, since it is a self-check on this plan's own edit, not a cross-plan audit |
| D | `tests/test_toolchain_config_gate.py`, `tests/test_pdf_render_gate.py` | D-13, D-14 | Both files are prose-only edits with no shared state with A/B/C; can be one plan (two files) or split further at the planner's discretion |

**Coordination note for the planner:** Plan A decides the new CLAUDE.md subsection's exact name
(D-04's "Claude's Discretion"). Plan D's docstring edits should describe CLAUDE.md's post-Phase-68
state **without quoting an exact new heading name** (e.g., say "CLAUDE.md's NixOS section" rather
than a specific `###` string chosen by a parallel plan) — this avoids a soft cross-plan wording
coupling that no test currently enforces but a careless choice could introduce. The one heading
string that *is* load-bearing (`## Conventions & gotchas`, cited at `:164`) is not touched by any
wave-1 plan.

**Wave 2 — one evidence/closure plan, dispatched only after wave 1 merges:**

- Re-run `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'` against the **merged** tree and
  classify every hit exactly as § D-15 Grep Classification does above; confirm the "rationale
  presented as current" class is now empty (0 rows) — this is SC#2's literal acceptance test.
- Re-run the green-tree gate (§ above, steps 1/3/4/5) against the merged tree in a fresh worktree,
  recording the same-worktree before/after counts.
- Produce the evidence file as `68-CLOSURE-EVIDENCE.md` (or similar `68-*-EVIDENCE.md` name) —
  **not** `68-VERIFICATION.md`, which is reserved for the verifier per this project's standing
  convention.

This split follows the project's own recorded lesson that an audit placed in the *same* wave as
the edit it measures cannot see the sibling worktree's merged result (auto-memory:
"same-wave-evidence-dependency-blind-spot"). The D-15 table above is deliberately phrased as "if
run today" so the planner can see the *predicted* post-edit state without treating it as a
substitute for the wave-2 re-measurement.

## Common Pitfalls

### Pitfall 1: Editing the wrong `tox.ini` comment block
**What goes wrong:** `tox.ini:19-32`'s `package = editable` rationale is topically adjacent
(mentions `tox`, `uv`, Phase 45.2) and could be mistaken for part of the `requires=` rationale.
**Why it happens:** both blocks discuss toolchain history and sit within ~20 lines of each other.
**How to avoid:** the D-16 edit touches only lines 4-10 (bounded above by `isolated_build = True`,
below by `requires = tox-uv~=1.35`). Verify with `sed -n '1,11p' tox.ini` after editing that line
11 (`requires = tox-uv~=1.35`) is unchanged and line 19 onward is untouched.
**Warning signs:** a diff touching `tox.ini` with more than ~10 changed lines, or any change
inside `[testenv]`.

### Pitfall 2: A comment edit that accidentally lands inside a `''…''` string in `flake.nix`
**What goes wrong:** Nix `#` comments outside `''…''` strings never enter any derivation; text
*inside* a `writeShellScript`/`writeShellScriptBin` body does, and changes the store path.
**Why it happens:** several of D-09..D-12's target comments sit immediately above or inside `let`
bindings whose *values* are `''…''` script bodies (e.g. `venvShimOnStop`, `uvShim`) — an edit that
drifts one line down changes shipped shell-script text, not a comment.
**How to avoid:** run the § Derivation-Identity Gate before/after every `flake.nix` edit in this
phase, not just at phase end — it is cheap (1.6s) and catches this class of mistake immediately.
**Warning signs:** any drvPath differing after a "comment-only" edit.

### Pitfall 3: Leaving `D-NN` IDs or time-relative phrasing in `flake.nix`
**What goes wrong:** D-09 explicitly forbids both, because `.planning/phases/6x-*/` (where the
`D-NN` decisions are defined) is deleted/archived at milestone close, and "until Phase 65" becomes
false the instant Phase 65 lands (already true today at `flake.nix:93`, per the CONTEXT.md
Measured State paragraph).
**Why it happens:** the *existing* comments being rewritten already contain `D-01`/`D-02`/`D-03`
(see `flake.nix:63,74-75,92`) — the path of least resistance is to lightly edit the existing text
and inherit its ID references.
**How to avoid:** treat D-09's citation rule as a hard rewrite requirement, not a light edit;
cite by milestone + phase + filename (e.g., "v0.9.3 Phase 64, `64-LIBZ-FIX-EVIDENCE.md`") instead.
**Warning signs:** `grep -n 'D-[0-9]' flake.nix` returning any hit after the edit.

### Pitfall 4: Comparing pytest counts across mismatched interpreters without checking `pyvenv.cfg`
**What goes wrong:** a worktree's fresh `.venv` may run uv-managed CPython 3.14 while another
comparison point runs nixpkgs 3.13.13; a genuine environment-caused difference (e.g., the
`libz.so.1`/Pillow class already fixed in Phase 64, or an unrelated future one) could be
misattributed to this phase's text edit.
**Why it happens:** D-06 is exactly this hazard, already observed once (`64-NIX05-WORKTREE-EVIDENCE.md`'s 1543/5 → 1548-collected-with-1-failure divergence, since resolved by the
`zlib` fix).
**How to avoid:** always diff `pyvenv.cfg`'s `home`/`version_info` between the two runs being
compared before drawing a conclusion from a differing test count; prefer same-worktree
before/after (§ Green-Tree Gate Method) over cross-worktree comparison.
**Warning signs:** a test-count mismatch with no corresponding code diff in `typsphinx/` or
`tests/`.

### Pitfall 5: Breaking the `CLAUDE.md 'Conventions & gotchas'` pointer
**What goes wrong:** `tests/test_toolchain_config_gate.py:164` cites this exact heading string as
a human-readable pointer inside an assertion message. No test currently checks that the heading
still exists (it is prose inside a message, not parsed), so breaking it produces a silent
dangling reference, not a test failure.
**Why it happens:** D-04 adds a new subsection "immediately before" the `Worktree-isolated
execution" heading, which is easy to misread as "replace/reorganize the `Conventions & gotchas`
section."
**How to avoid:** treat `## Conventions & gotchas` (line 73) as an anchor that is never renamed
in this phase; the new D-04 subsection is an addition, not a restructuring.
**Warning signs:** `grep -c "Conventions & gotchas" CLAUDE.md` returning 0 after the edit.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact subsection name Claude chooses for D-04 (e.g. "NixOS development shell") will not need to match any string a wave-1-parallel plan quotes | § Wave Plan Recommendation | Low — flagged as a coordination note; the one test-cited heading (`Conventions & gotchas`) is verified untouched, and D-13's docstring rewrite is recommended to avoid quoting the new heading verbatim |
| A2 | No `.planning/` file outside the ones read in this session references `CLAUDE.md`'s "Conventions & gotchas" heading or the exact `tox.ini`/`flake.nix` comment text in a way that would need updating | § Hazard Census | Low — `.planning/` is explicitly excluded from D-15's grep scope and from this phase's edit footprint; a stale `.planning/` reference is not a runtime hazard |

**If this table is empty:** N/A — two low-risk assumptions are logged above; everything else in
this document is `[VERIFIED]` against a file read this session or a command run this session.

## Open Questions

None outstanding. Every open question anticipated by the orchestrator notes (current text at each
site, measured facts, hazard census, read-only measurement transcripts, green-tree gate method,
wave split) is answered above with a session-verified command or a direct quote from an existing
evidence file.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `nix` | Derivation-identity gate (`flake.nix` plan) | ✓ | 2.34.8 | — |
| `git` | `git grep`/`git log -S` evidence commands | ✓ | 2.54.0 | — |
| `uv` (shim) | Provisioning line, `.venv/bin/uv` two-leg check | ✓ (resolves to `/nix/store/…-uv/bin/uv` containing `typsphinx-fhs-run` ×2) | shim wraps `uv.lock`-pinned `uv` (0.12.13) once `.venv/bin/uv` exists | — |
| `tox` (shim) | `tox config -e py312 --core -k requires` sanity check | ✓ | 4.56.1 (`uv.lock`) | — |
| `pytest`, `black`, `ruff` (shims) | Green-tree gate | ✓ | pinned via `uv.lock` | — |
| A darwin machine | Confirming D-11's darwin note beyond `nix eval` | ✗ | — | None — DOC-21 itself states this is unverified by construction; no fallback needed because the note's job is to *say so*, not to close the gap |

**Missing dependencies with no fallback:** none block this phase — the one structurally
unavailable item (a darwin machine) is the exact fact DOC-21 requires the text to state, not a
blocker to writing that text.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (`uv.lock`-pinned), config in `pyproject.toml` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, unedited by this phase) |
| Quick run command | `pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q` |
| Full suite command | `pytest -q` (or the bare `pytest` shim once provisioned) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DOC-19 | `CLAUDE.md` no longer names `tox-uv-bare` as current; no manual shim instruction remains | prose/grep-gate | `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock' \| grep '^CLAUDE.md'` returns nothing after the edit | ✅ (grep-based, no new file needed) |
| DOC-20 | `tox.ini`'s rationale comment describes the current pin; `~=` constraint kept; `requires=` value structurally unchanged | prose/grep-gate + structural | above grep for `tox.ini`; `tox config -e py312 --core -k requires` still prints `tox-uv~=1.35` | ✅ |
| DOC-21 | `flake.nix` explains the FHS wrapper, shimmed commands, and the darwin guard; no `D-NN` IDs; derivation unchanged | prose review + derivation-identity gate | `nix eval --raw .#devShells.{system}.default.drvPath` ×4, before/after equality; `grep -n 'D-[0-9]' flake.nix` returns nothing | ✅ |

There is no unit/integration test that can assert prose *content* correctness (a human/`plan-checker` review is the actual gate for wording quality); the automated commands above catch the two things that *are* mechanically checkable: the stale-string regression (grep) and the derivation-identity invariant (`nix eval`).

### Sampling Rate
- **Per task commit:** the plan-scoped commands above (grep for the file(s) that plan owns; derivation-identity gate for the `flake.nix` plan only)
- **Per wave merge:** wave 2's full re-grep (§ Wave Plan Recommendation) plus the green-tree gate
- **Phase gate:** wave 2's evidence file green before `/gsd-verify-work`

### Wave 0 Gaps
None — existing test infrastructure (the two named pytest files, `tox config`, `nix eval`) covers
every mechanically-checkable claim this phase introduces. No new test file or fixture is needed.

## Security Domain

This phase changes prose only — no user input, no authentication/session/access-control surface,
no cryptography, no new external package. ASVS categories are not applicable to a documentation
edit with zero runtime code change.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no code changed |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | no | N/A — no new input surface; the two edited pytest files' assertion *logic* is explicitly untouched (D-13/D-14) |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack
None apply — no new dependency, no new subprocess invocation pattern, no new file-path handling.
The one operational-security-adjacent fact this phase documents (D-03's `command -v uv | grep -q
typsphinx-fhs-run` shim check) is a correctness/diagnostic check, not a security control, and its
existing form (already in production use across Phases 64/65) is unchanged by this phase.

## Sources

### Primary (HIGH confidence — read/run this session)
- `CLAUDE.md`, `tox.ini`, `flake.nix` — full-file `Read`, this session, at HEAD (`89416753`)
- `tests/test_toolchain_config_gate.py`, `tests/test_pdf_render_gate.py` — targeted `Read`, this
  session
- `.planning/ROADMAP.md` § "Phase 68" (lines 620-679) and its AMENDED block (646-658) — `Read`,
  this session
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md` (partial), `.planning/config.json` — `Read`,
  this session
- Session commands: `git log --oneline -S "ln -sf"/-S patchelf -- CLAUDE.md` (both empty);
  `git grep -nE 'ln -sf|patchelf' -- ':!.planning'` (empty); `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'` (27 hits, classified above); `tox config -e py312 --core -k requires`;
  `command -v uv` + `grep -c typsphinx-fhs-run`; `nix eval --raw .#devShells.{system}.default.drvPath` ×4; `pytest --collect-only -q`; `grep -rliE 'nix|flake|CLAUDE\.md' .github/workflows/`
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX05-WORKTREE-EVIDENCE.md`,
  `64-NIX08-ENV-EVIDENCE.md`, `64-FLAKE-EVIDENCE.md`, `64-LIBZ-FIX-EVIDENCE.md` — full `Read`,
  this session
- `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md` — full `Read`, this session
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CONTEXT.md` —
  full `Read`, this session (source of all D-01..D-16 quotes above)

### Secondary (MEDIUM confidence)
None used — every claim in this document traces to a primary source above.

### Tertiary (LOW confidence)
None — no WebSearch or training-recall claim appears in this document; this phase's domain is
entirely this repository's own history, which is fully inspectable.

## Metadata

**Confidence breakdown:**
- Current-text quotes: HIGH — every quote is a direct `Read` this session, line numbers
  cross-checked against `git grep -n` in the same session
- Measured facts: HIGH — every fact is a verbatim transcription from an existing phase evidence
  file, several independently re-confirmed live this session (`nix eval`, `command -v uv`, `git
  log -S`, `git grep`, `pytest --collect-only`)
- Hazard census: HIGH — exhaustive `git grep` across `tests/`, `scripts/`, `docs/`, `.github/`,
  not a sampled search
- D-15 grep classification: HIGH — full 27-hit table, each row classified against the file it
  appears in (also read this session)
- Wave plan: MEDIUM — a recommendation, not a measured fact; the planner retains discretion per
  CONTEXT.md's "Claude's Discretion" section on plan split

**Research date:** 2026-09-12
**Valid until:** This research is tied to the exact HEAD commit (`89416753`) and the exact content
of the cited Phase 64/65 evidence files; it is valid until either (a) `CLAUDE.md`/`tox.ini`/
`flake.nix`/the two test files are edited by anything other than this phase's own plans, or (b)
more than a few days pass and a fresh `git grep -n tox-uv-bare` should be re-run before planning
proceeds, since this is a fast-moving toolchain milestone with several phases landing per day.
