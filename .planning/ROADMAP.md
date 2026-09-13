# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- ✅ **v0.9.0 — per-document templates** — Phases 53–57 (+54.1) (shipped 2026-08-22) → [archive](milestones/v0.9.0-ROADMAP.md)
- ✅ **v0.9.1 — Windows path correctness** — Phases 58–61 (completed 2026-08-30, **never published**) → [archive](milestones/v0.9.1-ROADMAP.md)
- ✅ **v0.9.2 — Inline image blocker fix and release** — Phases 62–63 (shipped 2026-08-31) → [archive](milestones/v0.9.2-ROADMAP.md)
- ✅ **v0.9.3 — Toolchain and dependency-update repair** — Phases 64–69 (completed 2026-09-13, merged to `main`, **not published**) → [archive](milestones/v0.9.3-ROADMAP.md)
- 🚧 **v0.9.4 — Typing Modernization** — Phases 70–71 (active, started 2026-09-13)

**Active milestone: v0.9.4 — Typing Modernization.** Two phases (70–71). It retires a lint
deferral that has stood since 2026-07-22: `pyproject.toml` stops suppressing ruff's `UP006`/`UP035`,
and every `typing.Dict`/`List`/`Set`/`Tuple` use in `typsphinx/` and `tests/` moves onto builtin
generics, with `typing.Iterator` moving to `collections.abc`. **Runtime behaviour and emitted Typst
output must be evidenced unchanged**, by measurement rather than by the rewrite being mechanical.
The one sanctioned visible change is API-reference type text: the autodoc'd modules render
`dict[str, Any]` where they rendered `Dict[str, Any]`.

**This milestone is not published** (owner decision 2026-09-13, the same shape as v0.9.3). No tag,
no PyPI upload, no GitHub Release; `pyproject.toml` stays at **`0.9.2`** and the CHANGELOG bullet
goes under the existing `## [Unreleased]`. The milestone branch **is** merged to `main` through a
PR. That is **REL-13**, and it closes at `/gsd-complete-milestone`, on the observed merge.

Phase numbering is **continuous across milestones**: v0.9.3 ran Phases 64–69, so v0.9.4 starts at
**Phase 70**.

## Phases

**Phase Numbering:**

- Integer phases (70, 71): Planned milestone work
- Decimal phases (70.1, 70.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.3 ran Phases 64–69, so this milestone starts at **Phase 70**.

<details>
<summary>✅ v0.9.3 Toolchain and dependency-update repair (Phases 64–69) — COMPLETED 2026-09-13, MERGED, NOT PUBLISHED</summary>

- [x] Phase 64: FHS Wrapper and Command Shims in `flake.nix` (6/6 plans) — completed 2026-09-12
- [x] Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves (2/2 plans) — completed 2026-09-12
- [x] Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem (4/4 plans) — completed 2026-09-12
- [x] Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 (5/5 plans) — completed 2026-09-12
- [x] Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` (4/4 plans) — completed 2026-09-13
- [x] Phase 69: v0.9.3 Close Prep (prep-only, unpublished) (6/6 plans) — completed 2026-09-13

21/21 v1 requirements complete; REL-12 checked at the close on the observed merge of PR #143.
`override_closeout` (all six verifications fingerprint-stale after later legitimate edits; the
same-day audit stood in). Full phase detail, the 15 binding constraints, success criteria and
decisions: [milestones/v0.9.3-ROADMAP.md](milestones/v0.9.3-ROADMAP.md). Audit:
[milestones/v0.9.3-MILESTONE-AUDIT.md](milestones/v0.9.3-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.2 Inline image blocker fix and release (Phases 62–63) — SHIPPED 2026-08-31</summary>

- [x] Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate (4/4 plans) — completed 2026-08-30
- [x] Phase 63: v0.9.2 Release Prep (prep-only) (6/6 plans) — completed 2026-08-30

7/7 v1 requirements complete; `verified_closeout`. Full phase detail, the 14 binding constraints,
success criteria and decisions: [milestones/v0.9.2-ROADMAP.md](milestones/v0.9.2-ROADMAP.md)

</details>

<details>
<summary>✅ v0.9.1 Windows path correctness (Phases 58–61) — COMPLETED 2026-08-30, NOT PUBLISHED</summary>

- [x] Phase 58: `repr()`-Format Decoupling (test-side only) (3/3 plans) — completed 2026-08-28
- [x] Phase 59: Path-Shape Predicate and Image-URI Correctness (5/5 plans) — completed 2026-08-29
- [x] Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere (5/5 plans) — completed 2026-08-29
- [x] Phase 61: v0.9.1 Release Prep (prep-only) (4/4 plans) — completed 2026-08-30

10/11 v1 requirements complete. REL-09 (publish to PyPI) deliberately unmet — the release was
cancelled, not missed. It carried forward into v0.9.2 and closed there. Full phase detail:
[milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.9.0 (Phases 1–57) — SHIPPED 2026-07-05 → 2026-08-22</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## 🚧 v0.9.4 — Typing Modernization (ACTIVE)

**Milestone Goal:** close the deferral recorded in the 2026-07-22 modernize todo (QUA-09) without
changing anything a user of typsphinx can observe, except the one thing that must change. The
ignore stayed because the Python 3.10 → 3.12 floor raise in v0.5.0 missed it (the todo's own finding),
not because of any technical constraint. Since then `CLAUDE.md` has actively forbidden the rewrite,
and every executor auto-loads that instruction. This milestone serves the core value indirectly: it
moves the code that produces the output onto the idiom the project's own Python floor has permitted
all along, and it has to prove that it moved nothing else.

**Binding constraints this roadmap is built on** (settled decisions and measured facts, not open
questions):

1. **Three orderings inside Phase 70, and their reasons** (owner decision 2026-09-13, resolving
   research's open question as option (a)). **(i)** `CLAUDE.md:75`'s "Don't 'modernize' typing
   imports until that todo lands" prohibition is rewritten **before any conversion plan runs**,
   because every executor auto-loads `CLAUDE.md` as a standing instruction and would otherwise be
   told not to do its own task. The rewrite must be **true both before and after the ignore flip**:
   no present-tense claim that ruff ignores (or enforces) `UP006`/`UP035`, and no instruction whose
   truth depends on which side of the flip the reader is on. **(ii)** The `pyproject.toml` ignore
   removal lands **after every file is converted**, so every merged state of the milestone branch
   stays `ruff check .`-green. Flipping first makes CI red on the unconverted remainder. **(iii)**
   After-side evidence is measured on the **post-flip** tree, in a wave after the flip and never
   co-located with the work it audits. This project has recorded an audit that abstained on its own
   criterion because it shared a wave with its subject. It has also recorded a residue that a later
   repo-wide re-measure could surface in a file no conversion plan touched.

2. **The todo's `pending/` path is cited in exactly two tracked files outside `.planning/`**
   (measured 2026-09-13 with `git grep`): `CLAUDE.md:75` and `pyproject.toml:128`. This is the same
   multi-location-sync shape that drifted Phase 65 → Phase 68. The resolution follows from the
   orderings above. The rewritten `CLAUDE.md` sentence cites **no** todo path, so it survives the
   move. The todo moves to `.planning/todos/completed/` **in the same commit that deletes
   `pyproject.toml:128-129`**, so the last reference to the pending path and the pending file leave
   together. DOC-22 requires the rewrite to land first but does not say when the move lands, so this
   split satisfies it.

3. **Never hard-code the violation count.** "113 (93 UP006 + 20 UP035) across 10 files" holds for
   ruff **0.16.6** (`uv.lock:1257-1258`; spec `>=0.15,<0.17` at `pyproject.toml:40`) on 2026-09-13
   and for nothing else. Success is **zero** findings on a fresh repo-wide
   `ruff check . --select UP006,UP035` (the CLI `--select` overrides the config ignore, so the count
   is observable while the ignores are still present), plus bare `ruff check .` passing. The
   pre-conversion count and the ruff version are recorded **fresh at execution time**, and discovery
   is repo-wide. The todo's own file list is stale: it predates `template_registry.py`, misses
   `writer.py`'s `Tuple`, and names no `tests/` file. `examples/`, `docs/` and `scripts/` are in
   `ruff check .` scope too, and were clean at research time.

4. **Dependabot must not move the baseline mid-conversion.** Since v0.9.3, dependabot is on the `uv`
   ecosystem and can bump `ruff` (#138 moved 0.15.20 → 0.16.6 and widened the spec). At roadmap time
   **no PR is open** (measured: `gh pr list --state open` empty; positive control — the `--state all`
   listing returns #138–#142, all merged). A `ruff` bump is **not merged** into the milestone branch
   while Phase 70's conversion is in flight. If one lands on `main` meanwhile, Phase 71's
   non-committing trial merge of `origin/main` re-lints the merged tree under the merged lock's
   `ruff`, and any new count is authoritative.

5. **Conversion mechanics are fixed by measurement.** `ruff check --fix` is AST-aware and resolves
   all but two findings in one pass. The two survivors are both on **`typsphinx/__init__.py:15`**
   (`from typing import Any, Dict`): ruff treats package `__init__.py` imports as probable
   re-exports and gates that F401 fix behind `--preview`, so the line is **hand-edited** to
   `from typing import Any`, and **`--preview` is never enabled** (CI and `tox -e lint` never pass
   it). **No `sed`-style substitution anywhere:** `tests/test_authors_pipeline_stage_gate.py:515`
   uses `ast.Dict` (the stdlib dict-literal node), and a blind rewrite would corrupt it into the
   nonexistent `ast.dict`. `tests/test_include_ledger_removal_gate.py:47`'s `Iterator` moves to
   `collections.abc`, the form `typsphinx/builder.py:11` already uses. Refused outright: a PEP 604
   `X | None` sweep (nothing to convert, no active rule), `from __future__ import annotations`
   (changes runtime annotation semantics), any public API or signature change, any edit to the
   `@preview` version-sync lines near the rewritten imports in `builder.py` / `writer.py` /
   `template_engine.py`, and running `ruff --fix` or `black` beyond the files the fresh measurement
   names.

6. **"Behaviour unchanged" has five measured legs (QUA-12), and each has a known trap.** (a) A
   **masked-AST hash** per converted file, equal between `git show <base>:<path>` and the converted
   tree. The harness is prior art from v0.9.3 Phase 68
   (`.planning/milestones/v0.9.3-phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md:248-326`;
   code at `68-02-PLAN.md:253` and `:305`), but the **mask target is different**: annotation
   subtrees (`arg.annotation`, `FunctionDef.returns`, `AnnAssign.annotation`) plus the `typing`
   import line, not docstrings and assert messages. The normalization is new code, so planning
   pilots it on one file (e.g. `translator.py`) before wiring it into an automated verify block.
   (b) Pytest **collected and passed** counts identical. (c) **Zero** pre-existing test-assertion
   edits, measured with `git diff`. (d) **Byte-identical `.typ`** output over the existing golden /
   render-gate fixture corpus, enumerated at the base by the executing plan. (e) **`mypy typsphinx/`
   output string-identical**, not merely the same exit code. The traps: the main checkout's `.venv`
   carries mypy 2.1.0 while `uv.lock` resolves 2.3.1 (pre-existing, out of scope), and a fresh
   worktree venv may be built on uv-managed CPython 3.14.x while the main checkout runs nixpkgs'
   3.13.13. Before and after are therefore always measured under the **same lock and the same
   interpreter version**, each side's `.venv/pyvenv.cfg` recorded. A difference between the two
   checkouts is never attributed to the typing change.

7. **DOC-23's docs diff needs a clean build.** `rm -rf docs/_build` before every docs build, on both
   sides. An incremental rebuild under-reports, which is how this project once manufactured a false
   "baseline match". `docs/source/api/index.rst` autodocs `typsphinx.builder`, `.pdf`, `.writer`,
   `.translator` and `.template_engine` through `sphinx_autodoc_typehints` with
   `autodoc_typehints = "description"` (`docs/source/conf.py:40`, `:114`), and that is where the
   type text changes. A base-vs-base control build separates build nondeterminism from the
   conversion, so "confined to type text" is a measured claim.

8. **CI holds lint authority, and only CI reaches Windows and macOS.** `ci.yml`'s `push` /
   `pull_request` triggers are scoped to `main` / `develop`, so a push alone runs no CI. The run is
   dispatched with `gh workflow run CI --ref gsd/v0.9.4-typing-modernization`, and `ruff`'s verdict
   is read from that run's **`Lint and Format Check`** job, step **`Run lint with tox`**
   (`ci.yml:52`, `:69`). **Milestone invariant #5** applies: the branch reaches `origin` in the
   **first** phase (Phase 70), evidenced by a completed run including the `windows-latest` and
   `macos-latest` lanes, not first at the release PR. No separate pre-conversion dispatch is needed.
   The branch's tree outside `.planning/` is identical to `main`'s tip `d14ca458` (measured:
   `git diff --name-only main..HEAD` lists only `.planning/` files), whose push-triggered CI run
   **`34730969392`** completed `success`. That run is the baseline a later red lane is compared
   against.

9. **Branch census at roadmap time (measured 2026-09-13).** Canonical
   `gsd/v0.9.4-typing-modernization` is at `4a6701c7` (`main` + 3, all `.planning/`-only) and
   carries HEAD. It is **local only**: `git ls-remote` returns `refs/heads/main` as positive control
   and nothing for `gsd/v0.9.4-*`. **No `gsd/v0.9.4-milestone` decoy exists yet**, but the `commit`
   helper has re-created one in every milestone since v0.9.1, so expect it after the next
   `gsd-tools` commit. Phase 70's push re-measures the census first. If a decoy has appeared and
   carries commits, the canonical ref is fast-forwarded to it, HEAD is re-pointed with
   `git symbolic-ref`, and only **then** is the decoy deleted. Deletion-first would orphan commits
   (v0.9.3 constraint 9).

10. **The release-requirement flip hazard is fenced again.** `phase.complete`-family tooling has
    auto-flipped the release requirement to `[x]` against an explicit CONTEXT decision at close-prep
    phases eight times, most recently REL-12 in v0.9.3's Phase 69 (reverted before commit). Phase 71
    reuses the procedure that caught it: a SHA-256 + `wc -l` + `PHASE_BASE_SHA` fence on
    `.planning/REQUIREMENTS.md`, re-verified at phase close **and once more after `phase.complete`
    has run**. **This is also why DOC-23 is in Phase 70, not 71**: a whole-file checksum fence only
    works in a phase where no other requirement checkbox is meant to move.

11. **Worktree isolation is the standing execution mode** (`CLAUDE.md` § Worktree-isolated
    execution). Every executor provisions with
    `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs everything via
    `uv run`. Without that, pytest imports the main checkout's unconverted package and every gate
    measures the wrong tree. On the maintainer's NixOS machine the recipe runs through the FHS shims
    inherited from the direnv-loaded session. The worktree `dev` extra lacks `myst-parser`, so the
    CHANGELOG page gate skips there, and Phase 71's zero-skip reading is taken where the `docs`
    extra is present.

12. **Standing invariants carried forward:** zero new runtime dependencies; no new `typst_*` config
    value; the `@preview` package count stays at **four** with no version change, and
    `tests/test_preview_version_sync.py` stays green; no workflow file is edited; SEED-003 (PEP 735
    `[dependency-groups]`) stays dormant; MSG-06 (`translator.py`'s two hardcoded-delimiter DEBUG
    logs) stays deferred even though `translator.py` is edited here, and a conversion plan must not
    absorb it opportunistically; and every phase closes green on the full pytest suite.

13. **Not a frontend UI milestone** (standing project note). `ui.plan-gate` false-positives on
    words this milestone cannot avoid: "page", "render", "docs-html", "API reference". Each phase
    detail therefore carries an explicit `**UI hint**: no` line, the override `ui-safety-gate.cjs`
    reads.

**`research/SUMMARY.md`'s one code phase + close prep shape is adopted as two phases.** Its Wave 1
(file-disjoint conversions A–E) and Wave 2 (plan F) become Phase 70's middle and final code waves,
with DOC-22's `CLAUDE.md` rewrite moved *ahead* of the conversions (constraint 1(i)) and the todo move
kept with the flip (constraint 2). Phase 71 is this project's standing prep-only final phase. That
convention has held for ten consecutive milestones under `branching_strategy: milestone`: the phase
takes zero irreversible action and the merge executes at `/gsd-complete-milestone`. REL-13 is
therefore mapped to Phase 71 for coverage purposes only.

- [ ] **Phase 70: Typing Modernization and Its Behaviour-Identity Evidence** - Every `typing.Dict`/`List`/`Set`/`Tuple` use in `typsphinx/` and `tests/` is on builtin generics and `Iterator` is on `collections.abc`, `ruff check .` enforces it with the `UP006`/`UP035` ignores gone, `CLAUDE.md` no longer forbids it, and five measurements show nothing changed except API-reference type text
- [ ] **Phase 71: v0.9.4 Close Prep (prep-only, unpublished)** - One CHANGELOG bullet lands under `## [Unreleased]` with `pyproject.toml` still at `0.9.2`, the tree is proven green on runs executed in this phase, and the PR to `main` is prepared behind a checksum fence with zero irreversible action taken

## Phase Details

### Phase 70: Typing Modernization and Its Behaviour-Identity Evidence

**Goal**: a contributor opening any module under `typsphinx/` or `tests/` finds builtin generics
(`dict[str, Any]`, `list[str]`, `set[...]`, `tuple[...]`) and `collections.abc.Iterator`. `ruff
check .` enforces that shape instead of suppressing it, and `CLAUDE.md` no longer tells an executor
not to write it. A reader of the API reference sees `dict[str, Any]` where they saw
`Dict[str, Any]`, and **nothing else changes**: no byte of emitted Typst, no test count, no line of
mypy output. That "nothing else" is the harder half of the phase, and it is carried by five
measurements, not by the rewrite being mechanical.

**Expected wave shape** (constraint 1; plan-phase decides the plans, but these orderings are
binding). **First:** DOC-22's `CLAUDE.md:75` rewrite, lint-neutral, together with the pre-conversion
baseline: `PHASE_BASE_SHA`, the fresh `ruff check . --select UP006,UP035` count and ruff version, and
the before side of QUA-12's legs (b), (d), (e) and of DOC-23's clean docs build. **Then:**
file-disjoint conversion plans under the still-present ignores. Research's split is `translator.py`
/ `builder.py` / `template_engine.py` + `template_registry.py` / `writer.py` + `__init__.py` (with
the hand edit) / the four `tests/` files (with the `Iterator` move). Each is lint-green on merge,
and each shows zero `UP006`/`UP035` on its own files. **Then:** the single plan touching
`pyproject.toml`, which removes the two ignores and their comments, moves the todo in the same
commit, re-measures repo-wide, and runs the gate quartet. **Last:** the after-side evidence and the
CI dispatch on the post-flip tip.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: QUA-09, QUA-11, QUA-12, DOC-22, DOC-23
**Success Criteria** (what must be TRUE):

  1. **`CLAUDE.md` stops forbidding the work before the work starts, and the todo leaves
     `pending/` together with the ignores.** The commit rewriting `CLAUDE.md:75` is an ancestor of
     every conversion commit (`git merge-base --is-ancestor`, checked per commit). The rewritten text
     carries no "don't modernize" instruction and no claim whose truth depends on whether
     `pyproject.toml` still ignores `UP006`/`UP035`: it is read at the last pre-flip commit and at
     the post-flip tip and is true at both. It cites no `todos/pending/` path. The 2026-07-22 todo is
     in `.planning/todos/completed/`, absent from `pending/`, and moved in the **same commit** that
     deleted `pyproject.toml:128-129`. After that commit, `git grep` over tracked files outside
     `.planning/` finds **zero** references to its `pending/` path (DOC-22; constraints 1, 2).

  2. **Zero `UP006`/`UP035` findings, discovered repo-wide and measured fresh, with no suppression
     left and no forbidden rewrite made.** `pyproject.toml`'s `[tool.ruff.lint] ignore` contains
     neither `"UP006"` nor `"UP035"` nor their deferral comments. A fresh repo-wide
     `ruff check . --select UP006,UP035` reports **zero**, against a non-zero pre-conversion count
     and ruff version recorded fresh at the base, never copied from this roadmap. Bare
     `ruff check .` passes with no `--preview` anywhere. No `from typing import` line under
     `typsphinx/` or `tests/` names `Dict`, `List`, `Set`, `Tuple` or `Iterator`, and
     `typsphinx/__init__.py:15` reads `from typing import Any`. The count of
     `from __future__ import annotations` and of `Optional[`/`Union[`/`X | None` annotations equals
     the base count, and no `@preview` version-sync line appears in the milestone diff.
     `tests/test_authors_pipeline_stage_gate.py` is absent from the diff, with its `ast.Dict` at
     `:515` intact (QUA-09, QUA-11; constraints 3, 5).

  3. **Nothing but annotations and typing imports changed in the code — measured three ways.** For
     every converted file, the masked-AST hash of the converted tree equals the hash of
     `git show <PHASE_BASE_SHA>:<path>`, with annotation subtrees and the `typing` import line
     masked (QUA-12 (a)). The pilot on one file is recorded before the check is automated. Every
     changed line under `tests/` is an import or annotation line, and no pre-existing test-assertion
     line is edited, read off `git diff` and not asserted (QUA-12 (c)). `mypy typsphinx/` output is
     **string-identical** before and after, not just the same exit code. Both sides use the same
     `uv.lock` mypy and the same interpreter version, with each `.venv/pyvenv.cfg` recorded (QUA-12
     (e); constraint 6).

  4. **Nothing changed in what the code produces, except API-reference type text — and that
     exception is recorded.** Pytest's collected and passed counts are identical before and after,
     measured under the same interpreter version (QUA-12 (b)). The `.typ` files the existing golden
     / render-gate fixture corpus emits are **byte-identical** before and after, compared by hash
     over a file list enumerated at the base (QUA-12 (d)). A clean docs build (`rm -rf docs/_build`
     first, both sides) of the converted tree differs from the pre-conversion base **only** in
     API-reference type text: `Dict[…]` → `dict[…]` and its siblings, on the autodoc'd module pages.
     A base-vs-base control build shows zero difference, so no diff line can be written off as
     nondeterminism. The diff is recorded as evidence (DOC-23; constraint 7).

  5. **The post-flip tree is green locally and on CI, and the milestone branch is on `origin`.**
     In the provisioned worktree venv, the gate quartet passes on the post-flip tip:
     `ruff check .`, `black --check .`, `mypy typsphinx/` and the full pytest suite. The branch
     census is re-measured first and any decoy is corrected per constraint 9. Then
     `gsd/v0.9.4-typing-modernization` is pushed with tracking. A CI run dispatched on that tip with
     `gh workflow run CI --ref gsd/v0.9.4-typing-modernization` has **completed**, with every job's
     conclusion transcribed literally, both `windows-latest` and both `macos-latest` lanes named
     individually and green, and `ruff`'s verdict taken from the **`Lint and Format Check`** job
     (step `Run lint with tox`), not from this machine (milestone invariant #5; constraint 8).

**Plans**: 8/13 plans executed (6 waves)

Plans:
**Wave 1**

- [x] 70-01-PLAN.md — DOC-22: rewrite CLAUDE.md:75 as an annotation-style instruction (wave 1)
- [x] 70-02-PLAN.md — baseline: PHASE_BASE_SHA, fresh UP006/UP035 census, SC#2 counts, legs (b)/(e) before (wave 1)
- [x] 70-03-PLAN.md — baseline: leg (d) corpus pilot, manifest and cross-path control; DOC-23 docs manifests (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 70-04-PLAN.md — tracer conversion of translator.py and the ledger gate, plus the masked-AST pilot (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 70-05-PLAN.md — convert builder.py (wave 3)
- [x] 70-06-PLAN.md — convert template_engine.py and template_registry.py (wave 3)
- [x] 70-07-PLAN.md — convert writer.py and __init__.py, with the one hand edit (wave 3)
- [x] 70-08-PLAN.md — convert the remaining three tests/ files (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 70-09-PLAN.md — the flip: drop both ignores and move the todo in one commit, then the gate quartet (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 70-10-PLAN.md — after side: SC#1 history, SC#2 static checks, legs (a), (c) and (e) (wave 5)
- [ ] 70-11-PLAN.md — after side: legs (b) and (d) on the post-flip tree (wave 5)
- [ ] 70-12-PLAN.md — DOC-23: clean docs diff with a base-vs-base control and hunk-by-hunk classification (wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [ ] 70-13-PLAN.md — gate quartet, branch census, first push, one CI dispatch, job transcript and SC roll-up (wave 6)

**Cross-cutting constraints:**

- mypy stdout hashes equal to MYPY_STDOUT_SHA256_BEFORE, and the full pytest result equals PYTEST_RESULT_BEFORE.

**UI hint**: no

### Phase 71: v0.9.4 Close Prep (prep-only, unpublished)

**Goal**: the milestone is packaged for a merge to `main` and nothing else. No version bump, no
tag, no PyPI upload, no GitHub Release. One CHANGELOG bullet goes under `## [Unreleased]` and stays
there, the same shape v0.9.3 used, decided up front.

The one irreversible action this milestone takes, opening and merging the PR to `main`, is
**REL-13**. Per this project's convention it executes at `/gsd-complete-milestone`, not inside this
phase. REL-13 is cited here for coverage only, its checkbox stays `[ ]` through every plan, and
constraint 10's checksum fence is what keeps it there.

**Depends on**: Phase 70
**Requirements**: REL-13
**Success Criteria** (what must be TRUE):

  1. **The tree is proven unpublished-shaped, probed with positive controls.** `pyproject.toml`
     still reads `0.9.2` and no commit in this milestone changes it. `git tag -l 'v0.9.4'` and
     `git tag -l 'v0.9.3'` and a remote tag probe for each come back **empty**. Each remote probe
     carries a positive control, so an empty result is distinguishable from a broken probe. PyPI
     has no `0.9.4` and there is no `v0.9.4` GitHub Release. Phase 71's own diff touches nothing
     under `typsphinx/` or `tests/`, and Phase 70's masked-AST equality is re-verified on the close
     tip, so no code change slipped in after Phase 70's verification.

  2. **The CHANGELOG carries this milestone's change under `## [Unreleased]` and creates no release
     section.** Exactly one new bullet sits under the existing `## [Unreleased]` → `### Changed`,
     in the register of the three already there: a bold summary, the requirement IDs, and "no
     effect on installing or using typsphinx". It names the API-reference type-text change
     (`Dict[str, Any]` → `dict[str, Any]`) and notes that the `ja` translation catalogs pick it up at
     the next published release. `grep` confirms no `## [0.9.4]` or `## [0.9.3]` heading and no
     matching tail link. The `[Unreleased]` compare base stays at `v0.9.2`, and
     `scripts/extract_changelog_section.py` is not run for any new section. The CHANGELOG page gate
     runs with **zero skipped** in an environment carrying the `docs` extra.

  3. **The tree is proven green on runs executed in this phase, including against `main` as it
     stands at close.** Proof comes from this phase's own runs, not a prior phase's word. Full pytest
     suite (once more under `LC_ALL=C`, since CI runs in English), `black --check .`,
     `mypy typsphinx/`, `ruff check .`, the `@preview` version-sync family, and both docs tox
     environments against a warning baseline taken from a **clean** build. One fresh CI run is
     dispatched on this phase's own tip, with every job conclusion transcribed, both `windows-latest`
     and both `macos-latest` lanes named, and `ruff` green in `Lint and Format Check`. A
     **non-committing** trial merge of `origin/main` into the branch passes `uv lock --check` and
     `ruff check .` on the merged tree. That catches a dependabot `ruff` bump that landed on `main`
     mid-milestone (constraint 4). `main`'s protection and merge method are read, not assumed.

  4. **The REL-13 checkbox is proven held by a recorded SHA-256, and the handoff is standalone.** A
     `71-CLOSEOUT-GUARD.md` records `sha256sum .planning/REQUIREMENTS.md`, `wc -l`, the
     `PHASE_BASE_SHA` and the verbatim guarded lines (`grep -n 'REL-13'`) at phase head. The same
     commands re-run and MATCH at phase close **and once more after `phase.complete`-family tooling
     has run**. That third observation is the one that actually catches the flip (constraint 10).
     Every plan's `SUMMARY.md` frontmatter declares `requirements-completed: []` for REL-13, and the
     checkbox is read directly out of `.planning/REQUIREMENTS.md` as `[ ]` at close, never inferred.
     A `71-HANDOFF.md` enumerates every step `/gsd-complete-milestone` must execute: the PR from the
     canonical milestone branch to `main`, the checks that must be green before merge, and the merge
     itself. It states that **no tag is pushed, no PyPI upload is made and no GitHub Release is
     created**, and that `typsphinx-doc-translations`' `update-pin.yml` dispatch and the Read the
     Docs `stable` check are **not applicable**. It lists the observations REL-13 is checked on after
     the merge: the merge commit on `origin/main`, `pyproject.toml` still `0.9.2`, no `v0.9.4` tag,
     PyPI 404 for `0.9.4`, and no `v0.9.4` Release.

**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:** 70 → 71. The arrow is a real dependency: close prep documents and fences what
Phase 70 landed, and its trial merge and CI run are only meaningful on the converted tree. Inside
Phase 70 the three orderings of constraint 1 are also real dependencies, not conventions.

Phases 1–69 shipped or completed across v0.4.4 → v0.9.3; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 70. Typing Modernization and Its Behaviour-Identity Evidence | v0.9.4 | 8/13 | In Progress | - |
| 71. v0.9.4 Close Prep (prep-only, unpublished) | v0.9.4 | 0/TBD | Not started | - |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.3's — the two-track structure
adopted from `research/SUMMARY.md`, the inverted `gsd/v0.9.3-milestone` decoy-branch correction, the
native-`uv`-ecosystem amendment that replaced a custom lockfile workflow, and the AMENDED blocks on
constraints 2 and 12 — live in [milestones/v0.9.3-ROADMAP.md](milestones/v0.9.3-ROADMAP.md).

- **2026-09-13** — v0.9.4 roadmap created: **Phases 70–71**, 6/6 v1 requirements mapped, zero
  orphans, zero duplicates, continuing numbering from v0.9.3's Phase 69. Two phases at
  `granularity: standard`, which nominally suggests 4–6. It sits below the range because the
  milestone is one mechanical, single-domain rewrite plus its evidence. Splitting out DOC-22, or the
  QUA-12 evidence, would manufacture a single-requirement phase or a phase that is pure verification
  of another phase's work, which is the anti-pattern the granularity guidance names. Four decisions
  are baked into the structure and should not be re-derived during planning:

  - **DOC-22 maps to Phase 70.** Its rewrite has to precede the conversions, and wave order inside
    one phase enforces that directly. A separate phase would hold one requirement and one sentence.

  - **DOC-23 maps to Phase 70, not 71.** Three reasons, each sufficient. Its diff is taken against
    Phase 70's pre-conversion base, alongside QUA-12's legs on the same converted tree. It is the
    positive half of "behaviour unchanged": the one sanctioned visible change, co-verified with the
    four legs that show nothing else moved. And Phase 71's whole-file checksum fence on
    `REQUIREMENTS.md` only works where no other checkbox is meant to move.

  - **The todo move lands with the ignore flip, not with the `CLAUDE.md` rewrite** (constraint 2).
    Measured: the todo's `pending/` path is cited only by `CLAUDE.md:75` and `pyproject.toml:128`.
    The rewritten sentence cites no path, and the pyproject comment and the pending file leave in
    one commit, so no intermediate state carries a dangling reference. This is the roadmapper's call
    on how to satisfy DOC-22 together with the owner's ordering decision, and it is surfaced for
    approval.

  - **The 3-OS CI run and milestone invariant #5 again carry no REQ-ID**, matching v0.9.1–v0.9.3.
    They are held by Phase 70 SC#5 (first push, post-flip tip) and Phase 71 SC#3 (close tip), each
    dispatched fresh on its own phase's tip and never inferred from a prior run. `main`'s run
    `34730969392` on `d14ca458` serves as the pre-conversion baseline without a separate dispatch.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Todo promoted into v0.9.4** (2026-09-13):

- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` → **Phase 70** (QUA-09, QUA-11,
  QUA-12, DOC-22). Deferred "doubly deliberately" through v0.9.3, because `CLAUDE.md` forbade it and
  it is a change under `typsphinx/`. Its own file list is stale: it names four `typsphinx/` files and
  no `tests/` file, against a measured 6 + 4. Discovery is therefore by fresh repo-wide measurement
  (constraint 3). It moves to `todos/completed/` in the commit that removes the ignores (constraint
  2).

**Still open and deferred** (5 of the 6 pending todos):

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — still excluded from every published surface by owner override D-07.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py:5047,5152` carry the same hardcoded-`'...'` delimiter shape
  Phase 60 closed in three other modules; the one-line fix is `quote_path()`, which now exists.
  **Adjacent to Phase 70 and explicitly not absorbed by it** (constraint 12). Phase 70 edits
  `translator.py`, but only its annotations and typing imports, and QUA-12's masked-AST equality
  would fail on this fix by design.

- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` — an HTML sidebar defect in
  this project's own docs `index.rst`.

- `2026-07-22-add-sphinx-linkcheck-ci-job` (Future QUA-08 / LNK-01) — deferred again; a CI job, and
  no workflow file is edited this milestone. Raised at seven consecutive closes.

- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line` (TRN-01, `severity: major`) —
  `doctest_block` has no translator handler, so `>>>` examples lose every line break. Captured
  2026-09-13 during the Issue #91 re-measurement; a behaviour change, out of this milestone's scope
  by construction.

**Dormant seeds:** `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by
v0.7.1's CONF-08 + DOC-11 and v0.8.0's DOC-14), **`SEED-003-tox-dependency-groups-per-env`** (Future
QUA-07 — splitting the `dev` extra into PEP 735 `[dependency-groups]`; a phase touching
`pyproject.toml` must not absorb it opportunistically), **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`**
— `typst-py` upstream maintenance is slowing and typsphinx may eventually need to carry an equivalent
compile path. Still the single largest structural risk on the horizon, and never scoped into any
milestone across six consecutive scopings. **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`**
— adopt GSD workstreams so independent roadmap tracks run in parallel; dormant since v0.9.3.

**Known limitations still shipped with no published surface** after v0.9.2, carried unchanged into
this milestone because it changes no product behaviour: WR-02's `confdir` gap, the tripled "Custom
template not found" warning, and NUM-01's `numref` per-master divergence. The `### Known
Limitations` decision stays open for the next *published* release; v0.9.4 publishes nothing, so it
does not force it.

**Standing risk carried from v0.9.3:** `flake.nix` is load-bearing while keeping **zero CI
coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only when the
maintainer next enters the shell, and the darwin branch of the per-system guard cannot be exercised
from a Linux machine at all. Accepted deliberately (owner decision 2026-09-02); documented on the
surface itself by v0.9.3's DOC-21. This milestone does not touch `flake.nix`.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. Active milestone: v0.9.4 (Phases 70–71), roadmap created 2026-09-13.*
