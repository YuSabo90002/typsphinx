# Phase 52: v0.8.0 Release Prep (prep-only) — Release Evidence

**Filename note:** this file is deliberately **not** named `52-VERIFICATION.md`. That name is
reserved by the `/gsd-verify-work` verifier, which overwrites it wholesale when it runs — writing
this roll-up under that name would mean it gets clobbered the next time the verifier runs (46-CONTEXT
D-15). This follows the `41-RELEASE-EVIDENCE.md` / `46-RELEASE-EVIDENCE.md` precedent.

This file rolls up all five ROADMAP success criteria (SC#1-SC#5) for Phase 52. It **cites** the five
sibling evidence files that already discharge SC#1 through SC#4 — quoting their own verdict language
rather than re-deriving it — and takes **fence observation 1 of 2** for SC#5 directly, because no
sibling plan owns SC#5. Observation 2 of 2 is recorded separately, at a later moment, in
`52-HANDOFF.md` § "Proof the fence held".

**Provisioning note:** this plan's own commands (the ones run directly below, not the ones quoted
from sibling files) were run inside this plan's isolated git worktree, after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, per this project's `CLAUDE.md`
§ "Worktree-isolated execution".

**Recorded:** 2026-08-15, at HEAD `e84e9d813ebe6a2915c995b4d5a88a6eb938ef3c`.

---

## SC#1

Quoted verbatim from `.planning/ROADMAP.md` § "Phase 52: v0.8.0 Release Prep (prep-only)":

> 1. **Version literals move in lockstep.** `pyproject.toml` is the sole `0.8.0` literal, with
>    `uv.lock` and `README.md` moved with it and the editable-install metadata regenerated so
>    `typsphinx.__version__` reports `0.8.0`; all three version-sync guard tests stay green.

**Evidence file:** `52-BUMP-EVIDENCE.md` (produced by plan 52-01).

**Verdict, cited verbatim from that file's own "Combined battery" and read-back sections:**

> `$ uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.8.0`
>
> JUnit `testsuite` element: `tests="5"`, `skipped="0"`, `failures="0"`, `errors="0"`. 5 tests
> (1 version-match + 1 readme-sync + 3 preview-sync), zero skips, zero failures — matching this
> plan's acceptance bar exactly.

**Figures quoted from that same file, for the record (not re-measured here):** `pyproject.toml`
line 7 moved `0.7.1` → `0.8.0`; `README.md` line 347's Status line moved in lockstep
(`Stable (v0.8.0) - Production ready`); `uv.lock`'s `typsphinx` entry reads `version = "0.8.0"`;
`uv lock --check` exited 0; the `[project] dependencies` array is byte-identical before/after (zero
dependency added or removed).

**SC#1 roll-up verdict:** **MET.** All three surfaces (`pyproject.toml`, `README.md`, `uv.lock`)
agree on `0.8.0`; the editable-install metadata was regenerated (`uv sync --extra dev --locked`,
uninstall `0.7.1` / install `0.8.0`); `typsphinx.__version__` reports `0.8.0`; and all three
version-sync guard tests pass with zero failures/errors.

---

## SC#2

Quoted verbatim from `.planning/ROADMAP.md`:

> 2. **`CHANGELOG.md` carries a curated `## [0.8.0]` entry covering every v1 requirement this
>    milestone delivered, with both user-visible changes called out explicitly** — (a) the
>    **output-shape change**: the target file is now a thin wrapper and the body moved to
>    `<docname>.typ`, named with the measured before/after file pair for a concrete config and
>    distinguished from v0.7.1's own `index.typ` → `<project>.typ` rename; and (b) the
>    **target-as-path reversal** of v0.7.1 Phase 44's D-05/D-06/D-07, stated as a deliberate
>    behaviour change with its security half retained. Any limitation Phase 49 measured and
>    documented appears here too — **except open question #2's `:numref:` divergence, which is
>    explicitly excluded** … The tail link block advances (new tag link + `Unreleased` compare), and
>    `docs/source/changelog.rst` is confirmed still rendering live from the repo-root file (DOC-12's
>    mechanism) rather than needing a second hand edit.

**No sibling evidence file owns this criterion** — plan 52-02 delivered the underlying change
(`52-02-SUMMARY.md`), which is cited here rather than re-measured, per this plan's own
`must_haves` instruction to cite sibling verdicts rather than re-derive them.

**Facts, drawn from `52-02-SUMMARY.md`:**

- `CHANGELOG.md` carries a `## [0.8.0] - 2026-08-15` heading (`grep -c '^## \[0\.8\.0\]' CHANGELOG.md`
  → `1`, re-confirmed live by this plan below).
- The lead paragraph's axis is the milestone goal itself (multi-master composition), with the
  breaking-change declaration in its second half, per D-05/D-04.
- Exactly three `**Breaking:**` bullets (the wrapper/content split, the target-as-path reversal, the
  collision hard error) and no `### Removed` heading — the milestone diff of `typsphinx/__init__.py`
  has zero `add_config_value` churn.
- The two Phase 49/51-documented behaviours (a standalone content file rendering only its own body;
  a shared document rendering once per reaching master, heading level varying per master) are folded
  into the descriptive `### Added`/`### Changed` bullets rather than a limitations section, per D-02.
- `:numref:` appears **zero** times in the entry — `51-CONTEXT.md` D-07's exclusion held.
- The tail link block advances: `[0.8.0]: .../releases/tag/v0.8.0` was inserted directly above
  `[0.7.1]`, and `[Unreleased]:` was re-pointed to compare `v0.8.0...HEAD`.
- `docs/source/changelog.rst` needed no hand edit — re-measured live and all three
  `**Breaking:**` items were already present in the "Migrating from 0.7.x to 0.8.0" section
  (`TestPublishedChangelogPageDelegates` 2/2 passed).
- `RELEASE_VERSIONS` was extended to 14 entries ending `"0.8.0"`, proven to reach both the built
  HTML page and the compiled PDF (`tests/test_changelog_page_gate.py` — 6 passed, `skipped="0"`,
  `failures="0"`, `errors="0"`).

**Re-confirmed live by this plan:**

```
$ grep -c '^## \[0\.8\.0\]' CHANGELOG.md
1
$ grep -c '^### Known Limitations' CHANGELOG.md
1
```

The one `### Known Limitations` heading in `CHANGELOG.md` sits at line 970, inside the historical
`## [0.1.0b1]` entry (heading range 848–1021) — not inside `## [0.8.0]` (heading range 17–90).
`awk '/^## \[/{print NR": "$0}' CHANGELOG.md` confirms the boundary directly. No limitations section
was added to the `[0.8.0]` entry, matching D-01.

**SC#2 roll-up verdict:** **MET.** The curated `## [0.8.0]` entry exists, covers this milestone's
requirements with both required user-visible-change callouts (output-shape change, target-as-path
reversal) explicitly marked `**Breaking:**`, excludes `:numref:` per D-07, the tail link block is
rolled over, and `docs/source/changelog.rst` renders it live with no second hand edit needed.

---

## SC#3

Quoted verbatim from `.planning/ROADMAP.md`:

> 3. **The post-bump tree is proven green live, not inherited — including the milestone goal
>    itself.** Full pytest, `black`/`ruff`/`mypy`, the full-corpus `-b typstpdf` GATE-02 gate, and
>    both docs builds (`docs-html`, `docs-pdf`) are re-run against the bumped tree. Alongside them,
>    the goal claim is discharged on generated evidence: a real `sphinx-build -b typstpdf` over a
>    **multi-master project with ≥2 masters and ≥1 shared child**, its PDFs opened via `pypdf`, with
>    specific text/page assertions proving each master's full content is present — not "the code
>    looks correct" and not "one representative fixture compiles".

This criterion is discharged in three parts: the CI authority run (toolchain half), the local half
(docs builds + full-corpus gate), and the goal-claim half (multi-master PDF round trip). **The CI
authority half did not clear on the first dispatch — it took three live runs to reach all-green, and
that history is recorded here in full rather than collapsed into a single "CI passed" statement.**

### CI authority

**Evidence file:** `52-CI-EVIDENCE.md` (plan 52-04's first dispatch; plans 52-08 and 52-09 each
appended a further run's section to the same file, in place — the file is one continuous,
append-only record of all three runs).

**Run 1 (plan 52-04) — RED.** Dispatched on pushed SHA `aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e`,
run id `31855486993`. Verdict quoted verbatim:

> **Status: Task 1 not accepted as SC#3's authority run. The dispatched run reports `failure`, not
> `success`, for eight of twelve jobs — a real, reproducible result, not a transcription error.**

Root cause: three independent, pre-existing defects, none introduced by this phase — a `ruff I001`
unsorted-import violation, a locale-dependent hardcoded-Japanese warning-baseline assertion, and a
Windows-only backslash-doubling assertion mismatch. All three were filed to `.planning/WINDOWS.md`
(entries 3-5) rather than fixed in-plan, since fixing them required touching `tests/` files outside
plan 52-04's declared file scope while running alongside sibling wave-3 plans.

**Run 2 (plan 52-08) — 11/12.** Plan 52-08 fixed all three of run 1's defects, pushed
(`aaeec804..21eb4398`), and re-dispatched, run id `31856929828`. Verdict quoted verbatim:

> **Status: NOT accepted as SC#3's authority run either. 11 of 12 jobs report `success` -- all
> three defects the first run found are confirmed fixed by this run's own evidence -- but
> `Test Python 3.13 on windows-latest` fails on a DIFFERENT assertion than the one plan 52-08 fixed,
> for what this section's own log-reading measures to be a fourth, previously-unknown, Python-3.13-
> specific defect.**

The new finding — CPython 3.13 narrowed `ntpath.isabs()` so a driveless leading-separator path is no
longer absolute on Windows, silently skipping `TypstBuilder._track_image()`'s rehome branch — was
filed as `.planning/WINDOWS.md` entry 6 rather than fixed blind, per plan 52-08's own stop-and-record
instruction.

**Run 3 (plan 52-09) — GREEN.** Plan 52-09 drive-qualified the affected test fixture (test-side only,
per an explicit owner decision preserving Phase 52's zero-`typsphinx/`-lines fence; the underlying
product-side inconsistency in `_track_image()` was filed as a todo instead —
`.planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md`), pushed
(`21eb4398..6924a0be`), and re-dispatched, run id `31858016832`. Verdict quoted verbatim:

> **Status: ACCEPTED as SC#3's authority run. All 12 of 12 jobs report `success`, including
> `Test Python 3.13 on windows-latest` -- the lane that carried the fourth defect the second run
> found. `[.jobs[].conclusion]|unique` is `["success"]`.**

**Accepted authority SHA:** `6924a0bec916227569f5332a99951972c1dafdaf` (run `31858016832`, 12/12
jobs `success`).

**Proof the authority run covers the whole source delta**, re-measured directly by this plan:

Command:
```
$ git diff --name-only 6924a0bec916227569f5332a99951972c1dafdaf..HEAD -- . ':(exclude).planning'
```
Verbatim output:
```
(no output)
```

Empty — every commit since the accepted authority run's SHA touches only `.planning/`. Confirmed by
the commit log over the same range:
```
$ git log --oneline 6924a0bec916227569f5332a99951972c1dafdaf..HEAD
e84e9d81 docs(phase-52): update tracking after wave 5
27688af0 chore: merge executor worktree (worktree-agent-a5824f004f203070c)
fa51dd6c docs(52-09): add plan summary
5ee9433a docs(52-09): record the green CI authority run and close the Broken Windows ledger
```
All four are planning/docs commits (plan 52-09's own SUMMARY/tracking, this wave's tracking merge).
The dispatched run's green result genuinely covers this phase's entire source delta.

### Local half

**Evidence file:** `52-GREEN-TREE-EVIDENCE.md` (produced by plan 52-05).

**Verdict quoted verbatim:**

> Per D-08's authority split, **this file records no claim of authority for pytest, `black`,
> `ruff`, or `mypy`** — the dispatched CI run plan 52-04 collects is the authority for those (and
> for the OS matrix, which local Linux-only runs cannot exercise). This file covers exactly what
> CI structurally does not: both docs builds, the full-corpus `-b typstpdf` GATE-02 gate, and an
> honest local suite spot-check.

Figures quoted from that same file: `tox -e docs-html` and `tox -e docs-pdf` both exit 0
(`build succeeded, 3 warnings` / `build succeeded, 5 warnings`); `docs/_build/pdf/typsphinx.pdf`
produced, 2,614,546 bytes, 128 pages, title page reads version `0.8.0`; the full-corpus gate
(`tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`) is
**PASSED**, in words, not merely absent from a failure count — `4 passed, 1 skipped` (the one skip
is the opt-in `TYPSPHINX_CORPUS_REPORT=1` measurement, unrelated to the gate's own pass/fail
criterion); a local suite spot-check ran `1170 passed, 5 skipped` (explicitly recorded as a
spot-check, not authority, per D-08).

**No `human_needed` marker applies** — the full-corpus gate PASSED; it did not skip.

### Goal-claim half

**Evidence file:** `52-GOAL-CLAIM-EVIDENCE.md` (produced by plan 52-03).

**Verdict quoted verbatim:**

> Full `-v` pytest transcript, both methods PASSED:
> ```
> tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_render_shared_children_once PASSED [ 50%]
> tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_carry_their_full_include_set_in_pdf PASSED [100%]
> ============================== 2 passed in 4.07s ===============================
> ```

The fixture (`tests/fixtures/state_guard_three_master_gate/`) carries **three** masters (`m1`, `m2`,
`m3`) and **two** shared children (`common_a`, `common_b`), exceeding SC#3's "≥2 masters and ≥1
shared child" minimum on both axes. The new gate method
(`test_three_masters_each_carry_their_full_include_set_in_pdf`) asserts, per master's own compiled
PDF opened via `pypdf`, presence of every document in that master's include set (including the
non-marker-bearing `mid` document), absence of documents outside that set, and cross-master
isolation — at both full-text and page level. A non-vacuity control (an inverted assertion, run in a
never-committed scratch edit) confirmed the detector genuinely FAILS on a real violation
(`assert 0 >= 1`) before being reverted, so the PASSED result is not vacuous.

### SC#3 roll-up verdict

**MET, on the third CI dispatch.** All three parts are MET with no gap: the CI authority run
(`31858016832`, accepted SHA `6924a0be`) reports all twelve jobs `success`; the local half proves
both docs dogfooding builds and the full-corpus gate, all green (PASSED, not skipped); the
goal-claim half proves the milestone's own goal sentence on generated evidence — a real multi-master
PDF round trip with per-master completeness and cross-master isolation assertions, non-vacuity
confirmed. No `human_needed` marker applies to any part. The two earlier CI runs (RED, then 11/12)
are part of this criterion's honest history, not its accepted evidence — only run 3
(`31858016832`) is cited as the authority.

---

## SC#4

Quoted verbatim from `.planning/ROADMAP.md`:

> 4. **The standing invariants are asserted mechanically over the SHA-anchored full milestone diff**
>    (merge-base to HEAD, excluding `.planning/`), with a positive control: zero new runtime
>    dependencies, and the `@preview` package count still **four** with no new version-lockstep site
>    across `writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`. No new
>    `typst_*` config value was added.

**Evidence file:** `52-SC4-INVARIANTS.md` (produced by plan 52-06).

**Verdict, cited verbatim from that file's own roll-up table:**

| Invariant / Control | Verdict | Evidence |
|---|---|---|
| Invariant 1 — zero new runtime dependencies | **MET** | `[project] dependencies` byte-identical `v0.7.1` → HEAD |
| Invariant 2 — `@preview` count still four, no new lockstep site | **MET** (substance) | All four versions agree across the three canonical sites; `test_preview_version_sync.py` 3/3 passed. The literal repo-wide file-count proxy grew (37→39, both additions test-assertion consumers, not new production declaration sites — named and content-classified, not waved through) |
| Invariant 3 — no new `typst_*` config value | **MET** | `typsphinx/__init__.py` byte-identical `v0.7.1` → HEAD |
| Control 1 — dependency detector fires | **FIRED** | historical commit `63f4284c` vs. parent: non-empty diff |
| Control 2 — `@preview` detector fires | **FIRED** | scratch-copy mutation: cross-surface comparison reports mismatch |
| Control 3 — config-value detector fires | **FIRED** | historical commit `10100b9d` vs. parent `e87e852b`: sets differ |

The sweep is anchored at the `v0.7.1` tag (`48bf135`), which `52-SC4-INVARIANTS.md` confirms live is
byte-identical, `.planning`-excluded, to `origin/main`'s own diff (both give **344 files changed,
+15,308/−2,477**) — the anchor coincidence ROADMAP SC#4's "merge-base to HEAD" wording and
`46-CONTEXT.md` D-21's "the release tag" wording both resolve to, confirmed rather than assumed.

Each of the three invariant detectors was proven to fire on a real, independent historical or
scratch-mutated violation — closing the vacuity mode the v0.7.1-era sweep (`46-SC4-INVARIANTS.md`)
never attempted to close.

### SC#4 roll-up verdict

**MET.** All three standing milestone invariants hold over the SHA-anchored, live-re-verified
`v0.7.1..HEAD` range: zero new runtime dependencies, the `@preview` package count still four with
all four versions in lockstep across the three canonical production declaration sites, and no new
`typst_*` config value. Each detector's ability to fire on a real violation was independently
demonstrated, not merely asserted.

---

## SC#5: no irreversible action taken — the fence, observation 1 of 2

Quoted verbatim from `.planning/ROADMAP.md`:

> 5. **No irreversible action was taken, and the handoff is standalone.** `git tag -l v0.8.0` and
>    `git ls-remote --tags origin v0.8.0` are both empty at phase end, and a standalone checklist
>    exists for `/gsd-complete-milestone` covering merge → tag → `release.yml` (with an explicit item
>    to observe `create-release` succeed) → PyPI + GitHub Release → the second tag on
>    `typsphinx-doc-translations` → the Read the Docs `stable` measurement on both projects. The
>    phase's artifacts state that **REL-07 remains open until the publish**, and do not report it
>    complete on the strength of the prep being correct.

This section records **observation 1 of 2**. Observation 2 — a second, independent probe at a
separate moment — is recorded in `52-HANDOFF.md` § "Proof the fence held".

**Timestamp:** 2026-08-15T02:20:22Z (immediately before the four probes below).

Command:
```
$ git tag -l v0.8.0
```
Verbatim output:
```
(empty)
```

Command:
```
$ git ls-remote --tags origin v0.8.0
```
Verbatim output:
```
(empty)
```

Command:
```
$ gh pr list --head gsd/v0.8.0-multi-master-composition --json number,state
```
Verbatim output:
```
[]
```

Command:
```
$ gh run list --workflow=release.yml --limit 5 --json databaseId,createdAt,event
```
Verbatim output:
```
[{"createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push"},
 {"createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push"},
 {"createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push"},
 {"createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"event":"push"},
 {"createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"event":"push"}]
```

All five listed `release.yml` runs predate this phase by days to weeks (2026-08-11, 2026-08-03,
2026-07-28, 2026-07-27, 2026-07-25 — the v0.7.1, v0.7.0, v0.6.5, v0.6.4, and an earlier release
respectively); none was started by this phase or by this plan.

Four independent observations, all empty/absent as required: no `v0.8.0` tag locally, no `v0.8.0`
tag on `origin`, zero open pull requests against this branch, and no `release.yml` run newer than the
pre-existing v0.7.1 release run. State explicitly, for the record: no pull request has been opened
or merged by this phase, no package has been uploaded to PyPI, no GitHub Release has been created,
and no `git tag` command has been run against `v0.8.0` (or any tag) anywhere in this phase's
execution.

**This is observation 1 of 2.** `52-HANDOFF.md` carries observation 2 at a later moment.

### SC#5 (observation 1) verdict

**Observation 1: EMPTY on both tag probes, `[]`/pre-existing-only on both PR/workflow probes, exit 0
on all four.** This is one of the two independent observations SC#5 requires; observation 2 follows
in `52-HANDOFF.md` at a separate, later moment.

---

## Phase verdict

| Success Criterion | Status | Evidence |
|---|---|---|
| SC#1 — version-literal lockstep | **MET** | `52-BUMP-EVIDENCE.md` |
| SC#2 — curated `## [0.8.0]` entry, both breaking-change callouts, tail link rollover | **MET** | `52-02-SUMMARY.md`, cross-checked live above |
| SC#3 — post-bump tree green live (CI authority + local half + goal-claim half) | **MET** (on the third CI dispatch — see § SC#3 for the RED → 11/12 → GREEN history) | `52-CI-EVIDENCE.md` + `52-GREEN-TREE-EVIDENCE.md` + `52-GOAL-CLAIM-EVIDENCE.md` |
| SC#4 — milestone invariants proven mechanically, each detector fire-tested | **MET** | `52-SC4-INVARIANTS.md` |
| SC#5 — no irreversible action, fence proven twice, standalone handoff | **MET** (observation 1 of 2 here; observation 2 in `52-HANDOFF.md`) | this file, § SC#5, and `52-HANDOFF.md` § "Proof the fence held" |

**No criterion is PARTIAL or NOT MET.** SC#3's own path to MET required three live CI dispatches
across plans 52-04, 52-08, and 52-09 — that history is recorded above in full, not smoothed into a
single clean pass, because the record that defects were found and fixed is the honest shape and is
more valuable than a fabricated clean one.

**REL-07 is NOT closed by this phase.** Its checkbox in `.planning/REQUIREMENTS.md` stays `- [ ]`
and its Traceability row stays `Pending` — this phase discharges only the prep half of REL-07. The
requirement closes at `/gsd-complete-milestone`, on the publish, not here. Lesson 12b — a requirement
reported complete on the strength of the code being correct is exactly how v0.7.0 lost REL-04 — is
the reason this sentence is written explicitly rather than left implied.

---

## Executed versus skipped

A phase-wide list of every command this phase's own evidence files record as **not executed** or
**not authoritative locally**, gathered from each sibling file's own executed-versus-skipped
statement. A skip is not a pass — this list exists so a skip cannot silently disappear at roll-up
time.

| Command / action | Plan | Reason not executed |
|---|---|---|
| A bare `tox` (no `-e` selector) | 52-01, 52-05 | `tox.ini`'s `env_list` includes `lint`, which dies at exit 127 on this NixOS machine: `.venv/bin/ruff` is a generic-linux ELF the stub loader rejects. Filed, out-of-scope environmental defect (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`). Lint authority sits with CI per D-08 — the third (accepted) CI run's `Lint and Format Check` job reports `success`. |
| `tox -e py312` | 52-01, 52-05 | `uv venv -p cpython3.12` attempts to download a standalone CPython whose ELF the same NixOS stub loader rejects, so the environment cannot even provision. The accepted CI run proves both `py312` and `py313` lanes green on `ubuntu-latest`, `macos-latest`, and `windows-latest`. |
| `.venv/bin/ruff` (any direct local invocation) | every plan | Cannot run on this NixOS machine at all — never a case of a test failing, but of the toolchain being unrunnable locally. Every `ruff` finding in this phase (the `I001` defect run 1 found) was caught and confirmed fixed exclusively via the dispatched CI runs. |
| `tests/test_corpus_gate.py::test_empty_url_before_after` | 52-05 | Gated on `TYPSPHINX_CORPUS_REPORT=1`, an opt-in before/after reporting measurement (RESEARCH Open Question 1), unrelated to the gate's own pass/fail criterion — the gate's actual pass/fail test (`test_corpus_compiles_with_no_fatal_error`) PASSED, not skipped. |
| Windows/macOS execution of any kind | every plan | This machine is Linux-only; every Windows/macOS-specific finding and fix in this phase (defects B, the fourth defect) was proven exclusively through the dispatched CI runs' own Windows/macOS lanes, never reproduced locally. |
| `git tag v0.8.0`, any tag push, `release.yml` trigger, PyPI upload, GitHub Release creation, PR open/merge | every plan in this phase | Forbidden by the prep/publish fence (Phase 33/35/41/46 precedent) that is absolute for this entire phase — these are exactly the actions `52-HANDOFF.md` records as the checklist for `/gsd-complete-milestone` to execute later, never for a release-prep phase to perform itself. |
| Flipping REL-07's checkbox or Traceability row in `.planning/REQUIREMENTS.md` | every plan in this phase | Deliberately deferred to `/gsd-complete-milestone`'s own close-side run, per this phase's own prohibition. `git diff --name-only -- .planning/REQUIREMENTS.md` is empty over this phase's entire history (re-confirmed by this plan's own Task 3). |

**No skip listed above stands in for a pass anywhere in this phase's evidence.** Every skip is named
with its reason, sourced from the sibling file that actually recorded it.
