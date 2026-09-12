# Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` - Context

**Gathered:** 2026-09-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Rewrite three documentation surfaces so they describe the mechanism that **actually landed** in
Phases 64 and 65, not the one that was planned: `CLAUDE.md` (DOC-19), `tox.ini`'s `requires`
rationale comment (DOC-20), and `flake.nix`'s own notes (DOC-21). Two boundaries must be stated
explicitly because both have already been inferred wrongly: how worktree executors relate to
`flake.nix`, and that darwin is unverified by construction.

**Edit footprint (exhaustive):**
- `CLAUDE.md` — line 11's `tox-uv-bare`, line 77's Conventions bullet, a new NixOS subsection, and
  one boundary paragraph in "Worktree-isolated execution".
- `tox.ini` — the `requires` rationale comment block (currently lines 4-10) **only**. The
  `requires = tox-uv~=1.35` line itself and the unrelated `package = editable` comment (lines 19-32)
  are untouched.
- `flake.nix` — Nix `#` comments only (see D-12's derivation-identity gate).
- `tests/test_toolchain_config_gate.py` and `tests/test_pdf_render_gate.py` — docstring / assertion
  message text only (D-13, D-14); no assertion logic change.
- `.planning/ROADMAP.md` — the SC#1 `AMENDED` block (D-01), written and committed with this CONTEXT.

**Out of scope:** anything under `typsphinx/` (constraint 13); any `.github/workflows/` edit
(constraint 3); `pyproject.toml`, `uv.lock`, the `requires` value; any change to the shell-script
bodies inside `flake.nix`; the CHANGELOG (Phase 69).

**Measured state at discussion time (2026-09-12):** `tox.ini:11` already reads
`requires = tox-uv~=1.35` (Phase 65) while its comment still says "tox-uv-bare pinned via ~=";
`CLAUDE.md:11` and `:77` still call `tox-uv-bare` deliberate and say not to go back to `tox-uv`;
`flake.nix:92-94` still says `.venv/bin/uv` "does not exist until Phase 65's tox-uv revert installs
it", but the main checkout now has `.venv/bin/uv` and `uv --version` reports `uv 0.12.13`.

</domain>

<decisions>
## Implementation Decisions

### SC#1's boundary — corrected by measurement

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

### CLAUDE.md content

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

- **D-08: CLAUDE.md:11 and :77 are rewritten to the landed `tox-uv`.** Line 11: `tox` (with
  `tox-uv`). Line 77: `tox.ini` pins `tox-uv~=1.35`, keeping the ini-parser explanation (a single-line
  `requires` is split on commas, so `>=1.35,<2` breaks tox's startup; `~=1.35` is the comma-free
  equivalent), plus a short note that the earlier `tox-uv-bare` pin was needed only because the
  bundled `uv` could not exec on NixOS, which the FHS shims now handle. The "Do not simplify it back
  to `tox-uv`" instruction is removed — it now points the wrong way.

### `flake.nix` notes

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

### Edit footprint beyond the three named files

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract
- `.planning/ROADMAP.md` § "Phase 68" — goal and SC#1..SC#3, **including the SC#1 AMENDED block
  (D-01)**
- `.planning/ROADMAP.md` § binding constraints 3 (CI unchanged), 8 (zero CI coverage for
  `flake.nix`, darwin unverifiable), 11 (worktree isolation not replaced by the FHS wrapper), 13
  (standing invariants), 15 (UI hint: no)
- `.planning/REQUIREMENTS.md` — DOC-19, DOC-20, DOC-21; § Future Requirements "Arising from this
  milestone" (the zero-CI-coverage risk D-11 states)

### The mechanism being documented
- `flake.nix` — whole file (120 lines); stale comment at `:92-94`
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CONTEXT.md` — D-01 (seven-name
  roster), D-02 (two-leg `uv`), D-03 (strict shims), D-08 (locale write-up owed here), D-09 (PATH
  inheritance + `command -v` head check), § Specific Ideas (the `uv` exception must be stated)
- `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CONTEXT.md`
  — D-05 (nixpkgs leg stays as bootstrap; documentation left to Phase 68), D-06 (stale surfaces left
  for Phase 68)
- `.planning/PROJECT.md` § "Binding measurements taken during scoping (2026-09-02)" — the two
  falsified devShell designs, the Linux-only guard

### Measurements the text reports
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX05-WORKTREE-EVIDENCE.md` —
  shims reachable by inheritance, `Found RC allowed 1`, worktree `.venv` on uv-managed 3.14, bare
  `.venv/bin/ruff` rc 127
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-GAP-REMEASURE-EVIDENCE.md` —
  NIX-01..NIX-05 MET after the `zlib` fix
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX08-ENV-EVIDENCE.md` —
  `$HOME`/`TMPDIR`/`/etc`/locale passthrough; Finding: REPRODUCES
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-LIBZ-DIAGNOSIS.md` and
  `64-LIBZ-FIX-EVIDENCE.md` — why `zlib` is in `targetPkgs`
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-FLAKE-EVIDENCE.md` — NIX-06
  (`nix eval` on all four systems)
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX07-RENAME-EVIDENCE.md` —
  the strict shims' not-found behaviour
- `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md`
  — `using bundled uv from: <tree>/.venv/bin/uv`, `uv 0.12.13`, the outside-FHS control

### Research
- `.planning/research/ARCHITECTURE.md` — Pattern 1 (one FHS derivation + thin shims), Pattern 2
  (namespace inheritance), Pattern 3 (`mkShell` stays)
- `.planning/research/PITFALLS.md` — Pitfall 3 (worktree executors skipping provisioning)

### Files edited
- `CLAUDE.md` (`:11`, `:77`, new subsection, § "Worktree-isolated execution")
- `tox.ini:4-10`
- `flake.nix` (comments only)
- `tests/test_toolchain_config_gate.py:302-304`, `:366-368`
- `tests/test_pdf_render_gate.py:160-171`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `flake.nix`'s existing comments already hold correct material to restate (the `zlib` reason at
  `:28-30`, the `venvWalk` description at `:37-42`, the strict-shim behaviour at `:63-66`) — rewrite
  to D-09's style rather than start from scratch.
- `venvShimOnStop`'s message already prints the exact provisioning line — CLAUDE.md can quote the
  exit-127 behaviour from it.

### Established Patterns
- Evidence recorded verbatim in phase `*-EVIDENCE.md` (Phase 64 D-05); `AMENDED` blocks append and
  keep the original text (Phase 65 D-01); the verifier reports literal and amended readings
  separately.
- Nix `#` comments outside `''…''` strings do not enter any derivation. Text inside the
  `writeShellScript` / `writeShellScriptBin` bodies **does**, and would change store paths.

### Integration Points
- `tests/test_toolchain_config_gate.py` asserts the `pyproject.toml` dev extra; D-13 touches its
  strings only, so the suite count must not change.
- `tox.ini`'s `requires` line is parsed by tox at startup; the comment edit must leave
  `tox config -e py312 --core -k requires` printing `tox-uv~=1.35`.

</code_context>

<specifics>
## Specific Ideas

- **Derivation-identity gate for the `flake.nix` edit.** Because D-09..D-12 are comment-only, record
  `nix eval --raw .#devShells.<system>.default.drvPath` for all four systems before and after the
  edit; they must be byte-identical. That proves no script body changed and doubles as NIX-06's
  "evaluates on all four systems" re-check.
- **D-03 check shape** (from 64-02's evidence): `command -v uv` → `/nix/store/…-uv/bin/uv`, and
  `grep -c typsphinx-fhs-run "$(command -v uv)"` ≥ 1.
- **Green-tree gate:** full pytest suite unchanged in count (text-only test edits), `black --check .`
  and `ruff check .` clean on the two edited test files; CI remains lint authority.
- **The `uv` leg-2 bootstrap** is the fact most likely to be "cleaned up" by a future reader; the
  note should say what breaks without it (a fresh clone or worktree cannot run its first `uv sync`).

</specifics>

<deferred>
## Deferred Ideas

- Maintainer auto-memory `nixos-sandbox-test-env.md` still carries pre-Phase-64 "ruff does not run in
  a fresh worktree" guidance. Outside the repository and not a phase deliverable; updated by the
  orchestrator at discussion close.

### Reviewed Todos (not folded)
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — keyword match only; forbidden by
  `CLAUDE.md` and constraint 13.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` —
  translator defect; `typsphinx/` change, constraint 13.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — docs rendering,
  unrelated.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` —
  `typsphinx/` change, constraint 13.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — workflow addition, constraint 3.

</deferred>

---

*Phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix*
*Context gathered: 2026-09-12*
