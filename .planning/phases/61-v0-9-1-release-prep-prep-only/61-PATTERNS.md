# Phase 61: v0.9.1 Release Prep (prep-only) - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 7 (1 product-tree edit + 6 planning artifacts)
**Analogs found:** 7 / 7

**Note on scope:** this is a document-producing phase. There is no `typsphinx/` source file in
scope — the "closest existing analog" for every artifact below is a **prior phase's document**,
not a source module. Concrete excerpts are the real heading structure, table shapes, and
probe-command blocks a planner can specify a matching artifact against directly.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `CHANGELOG.md` (`## [Unreleased]` block only) | config/doc | transform (authoring prose from requirement text) | `CHANGELOG.md`'s own `## [0.9.0]` section (in-file) + `52-CONTEXT.md`'s "authoring from scratch" framing | exact (same file, same house style; different heading target) |
| `61-CHANGELOG-EVIDENCE.md` | test/evidence doc | request-response (command → verbatim stdout capture) | `57-CHANGELOG-EVIDENCE.md` | exact |
| `61-GREEN-TREE-EVIDENCE.md` | test/evidence doc | batch (multi-command transcript) | `52-GREEN-TREE-EVIDENCE.md` (docs-build local half), `57-GREEN-TREE-EVIDENCE.md` (provisioning + full pytest) | exact (compose both) |
| `61-CI-EVIDENCE.md` | test/evidence doc | event-driven (dispatch → poll → capture) | `57-CI-EVIDENCE.md` / `57-CI-EVIDENCE-RUN3.md`; `52-CI-EVIDENCE.md` for the "report failure honestly, don't paper over it" shape | exact |
| `61-SC4-INVARIANTS.md` | test/evidence doc | batch (anchor → diff → per-invariant proof) | `57-SC4-INVARIANTS.md` (more recent, has the "hunk-level argument" escalation pattern); `52-SC4-INVARIANTS.md` (anchor-coincidence measurement pattern) | exact |
| `61-CLOSEOUT-GUARD.md` | test/evidence doc | request-response (checksum + grep, recorded twice) | `57-CLOSEOUT-GUARD.md` | exact |
| `61-HANDOFF.md` | doc/checklist | request-response (structured checklist, Owner/Ordering per item) | `57-HANDOFF.md` (most recent structure), `52-HANDOFF.md` (older sibling) — **both must be structurally inverted per D-12/D-13, see Pattern note below** | role-match (structure identical; polarity of opening section must invert) |

## Pattern Assignments

### `CHANGELOG.md` (`## [Unreleased]` block)

**Analog:** `CHANGELOG.md`'s own `## [0.9.0]` `### Fixed` section (lines 105-124), and
`52-CONTEXT.md`'s "authoring from scratch" precedent (Phase 52 also started from a bullet-free
`## [Unreleased]`).

**Section vocabulary observed directly in the file** (measured this session, per RESEARCH.md):
`### Fixed` (19 uses across the file), `### Added` (14), `### Changed` (13), `### Verified` (9),
`### Removed` (5). `### Known Limitations` exists exactly once (inside `0.1.0b1`) — **do not add
one here**, D-05 forbids any public-surface disclosure of the inline-image blocker.

**House style, bullet shape** (verbatim, `CHANGELOG.md:105-113`):
```markdown
- **A driveless-absolute Windows image URI is classified like its sibling (BLD-09).** An absolute
  image URI written by a third-party extension in the driveless Windows shape (or the UNC shape)
  now reaches the relocate-and-warn path on Python 3.13, where it was previously left untouched —
  which mattered because an untouched rooted URI reached the image copy step, whose platform-native
  destination join discards the output directory for a rooted path.
```

Pattern: **bold lead sentence** stating the user-visible fix in plain language, requirement ID(s)
in trailing parentheses inside the bold span, then 1-3 sentences of prose explaining what changed
and why it matters — never internal module/function names as the subject.

**Requirement-ID convention** (house style since Phase 33, confirmed live against this file):
IDs go in trailing parentheses at the end of the bold lead sentence, e.g. `(XREF-05)`,
`(BLD-07)`, `(BLD-08)`, `(BLD-09)`, `(IMG-03)`. Phase 61's bullets should cite `PATH-01`,
`IMG-04`, `IMG-05`, `IMG-06`, `IMG-07`, `MSG-01`..`MSG-05` per CONTEXT's specific idea #2 (three
defect families, in ROADMAP's naming order).

**One bullet with NO trailing parenthesis exists** (`CHANGELOG.md:118-124`, the Windows
`repr()`-escaping message fix) — noted because it landed as an unplanned mid-phase fix before its
own requirement existed; Phase 61's bullets, each backed by a real REQ-ID, should carry the
parenthesis form, not omit it.

**What NOT to add (D-04):** no `[0.9.1]` heading, no tail link-reference line. The tail block
(verbatim, `CHANGELOG.md` last line) stays exactly:
```
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD
```

**Framing constraint (Specific Idea #1):** do not write "Windows-only" — Phase 60's D-01 AMENDED
records that `quote_path()` closes an apostrophe by doubling it, affecting POSIX paths too.

---

### `61-CHANGELOG-EVIDENCE.md`

**Analog:** `57-CHANGELOG-EVIDENCE.md`

**Structure to copy** (verbatim heading/shape, lines 1-9):
```markdown
# Phase 57 — CHANGELOG Evidence (SC#2)

## SC#2 — the release body, in both directions

Command: `uv run python scripts/extract_changelog_section.py 0.9.0`

Exit code: `0`

stdout (verbatim — this is exactly what the GitHub Release body will be for `v0.9.0`, byte for
byte, through `scripts/extract_changelog_section.py`):
```

**Divergence for Phase 61:** `scripts/extract_changelog_section.py` is **not invoked** this
phase (D-13/RESEARCH — no `## [0.9.1]` section exists to extract). `61-CHANGELOG-EVIDENCE.md`
should instead show: (a) the authored bullets' before/after diff against `## [Unreleased]`, (b)
the docs-html/docs-pdf warning-count comparison against the 3/5 baseline (per RESEARCH.md's
Pitfall 3 — this IS still required even though the extraction script is skipped), (c) a
confirmation that `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple is untouched.

---

### `61-GREEN-TREE-EVIDENCE.md`

**Analogs:** `52-GREEN-TREE-EVIDENCE.md` (docs-build local-half shape) + `57-GREEN-TREE-EVIDENCE.md`
(provisioning-proof shape).

**Provisioning-proof pattern to copy verbatim** (`57-GREEN-TREE-EVIDENCE.md:1-52`):
```markdown
## Provisioning and tree identity

Command (per `CLAUDE.md` § "Worktree-isolated execution"):
```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev --extra docs
```

...

**Step 1 — confirm the tree, three commands:**

```
$ grep -n '^version = ' pyproject.toml
7:version = "0.9.0"

$ grep -c '^## \[0\.9\.0\]' CHANGELOG.md
1

$ uv run python -c "import typsphinx; print(typsphinx.__version__, typsphinx.__file__)"
0.9.0 /home/.../worktrees/agent-a3585ee232160d75c/typsphinx/__init__.py
```
```

**For Phase 61:** the `__file__` absolute-path check is the load-bearing anti-stale-editable-
install proof — copy it exactly, substituting the new worktree path. There is **no version
bump this phase**, so the `grep -n '^version ='` check should assert `0.9.0` is UNCHANGED (a
different assertion polarity than 52/57, which asserted the NEW version landed).

**Authority-split framing to copy** (`52-GREEN-TREE-EVIDENCE.md:14-18`): state explicitly which
evidence file is authoritative for what — CI is authoritative for pytest/black/ruff/mypy/OS
matrix; this file covers what CI structurally does not (both docs builds, warning-count
comparison, any full-corpus / local spot-check).

---

### `61-CI-EVIDENCE.md`

**Analogs:** `57-CI-EVIDENCE.md` + `57-CI-EVIDENCE-RUN3.md` (dispatch-and-capture mechanics,
most recent); `52-CI-EVIDENCE.md` (the "report a real failure honestly, do not paper over it"
shape, in case the fresh dispatch is not clean).

**Exact dispatch-and-capture sequence to copy** (from RESEARCH.md, sourced from
`57-CI-EVIDENCE-RUN3.md:32-97`):
```bash
uv sync --extra dev --locked   # confirm no lockfile drift
git push origin gsd/v0.9.1-windows-path-correctness
gh workflow run ci.yml --ref gsd/v0.9.1-windows-path-correctness
gh run list --workflow=ci.yml --branch gsd/v0.9.1-windows-path-correctness --limit 1
gh run watch <run-id>
gh run view <run-id> --json jobs --jq '.jobs[] | "\(.conclusion)\t\(.name)"'
gh run view <run-id> --json jobs --jq '.jobs[] | select(.name | contains("windows-latest"))'
```

**Pre-dispatch confirmation pattern to copy** (`57-CI-EVIDENCE.md:22-33`):
```
$ grep -n '^version = ' pyproject.toml
7:version = "0.9.0"

$ grep -c '^## \[0\.9\.0\]' CHANGELOG.md
0
```
For Phase 61, invert the second check's expectation: confirm the tip DOES carry the newly
authored `## [Unreleased]` bullets (grep for one of the new requirement IDs, e.g.
`grep -c 'PATH-01' CHANGELOG.md` returning a nonzero count), since D-09 requires the dispatch to
run on the tip that **includes** this phase's own CHANGELOG edit (RESEARCH.md Pitfall 2).

**Failure-honesty pattern to copy** (`52-CI-EVIDENCE.md:7-13`): if a job fails, "do not paper
over it: report the failure with its log excerpt and stop" — do not silently retry or accept a
non-green run as evidence.

**Dispatch count:** D-09 defaults to **one** dispatch (no pre-bump/post-bump split exists this
phase, since there is no bump) — unlike 57's two-run file, `61-CI-EVIDENCE.md` should normally
be single-run shaped like `52-CI-EVIDENCE.md`, not dual-run shaped like `57-CI-EVIDENCE.md`.

**12-job census to transcribe literally, never paraphrase** (RESEARCH.md, read directly from
`.github/workflows/ci.yml`):
```
test:        Test Python 3.12 on ubuntu-latest / windows-latest / macos-latest   (x2 = 6)
lint:        Lint and Format Check                                               (1)
type-check:  Type Check                                                          (1)
coverage:    Code Coverage                                                       (1)
build:       Build Package                                                       (1)
integration: Integration Test - basic / Integration Test - advanced              (2)
                                                                        TOTAL = 12
```

---

### `61-SC4-INVARIANTS.md`

**Analogs:** `57-SC4-INVARIANTS.md` (most recent — has the "hunk-level argument" escalation
when an empty-diff assertion no longer holds), `52-SC4-INVARIANTS.md` (anchor-coincidence
measurement pattern, `git merge-base` vs. tag equality check).

**Anchor-and-coincidence block to copy verbatim shape** (`57-SC4-INVARIANTS.md:20-40`):
```bash
git rev-parse v0.8.0^{commit}
git rev-parse origin/main
git merge-base origin/main HEAD
git merge-base --is-ancestor v0.8.0 HEAD && echo tag-is-ancestor
git merge-base --is-ancestor origin/main HEAD && echo main-is-ancestor
git rev-list --count v0.8.0..HEAD
git diff v0.8.0..HEAD --stat -- . ':(exclude).planning' | tail -1
git diff "$(git rev-parse origin/main)"..HEAD --stat -- . ':(exclude).planning' | tail -1
```
For Phase 61, the anchor is `v0.9.0` (the tag this milestone diffs against), not `v0.8.0` — per
RESEARCH.md's Anti-Pattern warning, this must be measured fresh, not copied from either prior
document.

**Anti-pattern warning to carry forward verbatim** (RESEARCH.md, sourced from
`52-SC4-INVARIANTS.md`): do not copy forward a prior milestone's "no new `typst_*` config
value" or "no new runtime dependency" assertion unexamined — Phase 57's own milestone falsified
that pattern (it DID add a config value). Re-measure against `v0.9.0..HEAD` fresh.

**Open question flagged by RESEARCH.md (must be resolved before writing this file):** D-10's
literal wording lists exactly four fence items (tag probe, no-publish probe, `typsphinx/` diff,
REQUIREMENTS.md checksum) and does **not** explicitly require the milestone-invariant sweep
(dependency/`@preview`/config-value) that 52/57 both ran to back a `### Verified` section.
Since Phase 61 defers `### Verified` authorship to v0.9.2 (Claude's Discretion), the planner
should confirm whether `61-SC4-INVARIANTS.md` needs the full invariant sweep or only D-10's
four narrower items — do not default to "always run the full 52/57 shape" without checking.

**Positive-control requirement (Discretion item):** if a milestone-diff sweep IS run, its
"no new X" claims must be backed by an argument that would fail on a real violation — follow
`57-SC4-INVARIANTS.md`'s "hunk-level argument" pattern (quoting the actual `pyproject.toml`
diff hunk and explaining why an empty-diff assertion no longer suffices), not a bare "diff is
empty" claim.

---

### `61-CLOSEOUT-GUARD.md`

**Analog:** `57-CLOSEOUT-GUARD.md` — copy this file's structure almost exactly, substituting
REL-08 → REL-09 and the new checksum/line numbers.

**Full structure to copy** (`57-CLOSEOUT-GUARD.md`, entire file is short enough to mirror
1:1):
```markdown
# Phase 61 Plan NN — REL-09 Checkbox-Flip Closeout Guard

Follows the `57-CLOSEOUT-GUARD.md` mechanism ... This task changes NO requirement state —
REL-09 stays `[ ]` and Pending; `.planning/REQUIREMENTS.md` is read and quoted here only,
never edited.

## Baseline

```
$ sha256sum .planning/REQUIREMENTS.md
<hash>  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
<N> .planning/REQUIREMENTS.md

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
<timestamp>
```

## The lines under guard

```
$ grep -n 'REL-09' .planning/REQUIREMENTS.md
127:- [ ] **REL-09**: v0.9.1 released to PyPI ...
206:| REL-09 | Phase 61 | Pending |
220:Phase 60 → 4 (...) · Phase 61 → 1 (REL-09).
```

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **five consecutive** release-prep
closes (Phase 61 increments the running count that 57-CLOSEOUT-GUARD.md recorded as "four").

## Re-verification protocol

```bash
sha256sum .planning/REQUIREMENTS.md   # compare against Baseline
git diff --name-only -- .planning/REQUIREMENTS.md   # expect: no output
```
```

**Live baseline values, already measured this session** (from RESEARCH.md, reusable verbatim
as the phase-head recording if no plan has landed yet at the time the guard-recording task
runs):
```
$ sha256sum .planning/REQUIREMENTS.md
4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1  .planning/REQUIREMENTS.md

$ grep -n 'REL-09' .planning/REQUIREMENTS.md
127:- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
206:| REL-09 | Phase 61 | Pending |
220:Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```
**Important:** this is a same-session measurement, not necessarily the exact phase-head moment
a plan will run at — the plan that authors `61-CLOSEOUT-GUARD.md` should re-run these two
commands itself rather than transcribing the above as final, per RESEARCH.md's own caveat.

**Count note (D-10):** the "N consecutive" language must say **five**, not four (57's own
count) — Phase 61 increments it.

**Reversion instruction to copy verbatim if a flip is later detected:**
```
git checkout -- .planning/REQUIREMENTS.md
```
then report it — do not commit the flip.

---

### `61-HANDOFF.md`

**Analogs:** `57-HANDOFF.md` (structure, most recent), `52-HANDOFF.md` (older sibling, same
skeleton). **The opening section's polarity must be inverted per D-12/D-13/RESEARCH Pitfall 4.**

**Inherited skeleton (do not discard):**
```markdown
# Phase 61: v0.9.1 Release Prep (prep-only) — <retitled per D-12, not "Publish Checklist">

This document is the standalone <...> `/gsd-complete-milestone` reads for this milestone. ...

## What this phase satisfied, and what it did not

**REL-09**, quoted verbatim from `.planning/REQUIREMENTS.md`:
> ...

Citing each success-criterion's own evidence artifact and section, not restating it:
- **SC#1** ... — DROPPED (D-11), state this explicitly rather than reporting MET/NOT-MET
- **SC#2** ... — REWORDED (D-11), cite 61-CHANGELOG-EVIDENCE.md
- **SC#3** ... — RETAINED, cite 61-GREEN-TREE-EVIDENCE.md + 61-CI-EVIDENCE.md
- **SC#4** ... — RETAINED, cite 61-SC4-INVARIANTS.md + 61-CLOSEOUT-GUARD.md
- **SC#5** ... — RETAINED/RE-AIMED, cite this document itself

**REL-09 remains open.** [same "closes at /gsd-complete-milestone, not here" framing as 52/57]

## Checklist
Each item names its Owner and its Ordering dependency on the items before it.
### 1. ...
```

**THE INVERSION (D-12, D-13, RESEARCH Pitfall 4) — the one piece that must NOT be copied
mechanically:** every prior `*-HANDOFF.md` opens by stating (implicitly, via the checklist
structure itself) that a publish is imminent, and item 1 of the checklist is always "open the
pull request." For `61-HANDOFF.md`:
- The **very first line/section** must state the negative explicitly: this milestone's
  `/gsd-complete-milestone` performs **no** tag, **no** PyPI publish, **no** GitHub Release, **no**
  PR — before any checklist item appears.
- The checklist that follows is relabeled as an **inheritance record for v0.9.2**, not
  "steps to execute now" — every version-specific value (the tag name, the CHANGELOG section
  version) must be written as a placeholder (e.g. `vX.Y.Z`), not hard-coded to `0.9.1`.
- The three items that MUST survive per D-13, drawn from `57-HANDOFF.md`'s own checklist
  section structure (Owner/Ordering items) but re-purposed as "what to remember" rather than
  "what to do":
  (a) the second-repository tag for `typsphinx-doc-translations`, advanced by dispatching
      **that repo's own `update-pin.yml`**, not a hand clone-edit-push;
  (b) the Read the Docs `stable` measurement for both projects (unauthenticated public API
      calls — doable, per RESEARCH's Environment Availability table);
  (c) the GitHub Release body being byte-identical to
      `scripts/extract_changelog_section.py <version>`'s stdout.
- Also name the inline-image blocker explicitly (D-07) so v0.9.2 does not have to
  rediscover it: cite `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-
  unseparated-expression.md`.

**Fence-proof-observation pattern to copy** (`57-HANDOFF.md:33-44` — the third/final probe
recorded inside the handoff itself, following `52-HANDOFF.md`'s "observation 2 of 2" placement):
```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(empty)

$ sha256sum .planning/REQUIREMENTS.md
<hash matching 61-CLOSEOUT-GUARD.md's baseline>
```
Two fence-probe observations total is the accepted minimum (Phase 52's shape, minutes apart);
Phase 57's three-observation shape is not required (RESEARCH.md Pattern 3 / Open Question 2).

## Shared Patterns

### Worktree-isolated execution provisioning
**Source:** `57-GREEN-TREE-EVIDENCE.md` lines 1-13, `52-GREEN-TREE-EVIDENCE.md` lines 1-9,
`52-CI-EVIDENCE.md` lines 1-4, `57-CI-EVIDENCE.md` lines 1-4, `52-SC4-INVARIANTS.md` lines
14-15, `57-SC4-INVARIANTS.md` lines 1-4.
**Apply to:** every evidence file this phase produces.
```bash
unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
uv sync --extra dev --extra docs   # or --extra dev, depending on the plan's scope
# every subsequent command runs through `uv run`
```
The absolute-`__file__` proof (`57-GREEN-TREE-EVIDENCE.md:52`) is the load-bearing anti-stale-
editable-install check — copy it into any evidence file that runs Python against `typsphinx`.

### Requirement-ID trailing-parenthesis house style
**Source:** `CHANGELOG.md` itself (19+14+13 bulleted entries measured), house style since
Phase 33.
**Apply to:** every new `## [Unreleased]` bullet.

### "Cite the evidence file's own section, don't restate it" cross-referencing style
**Source:** `57-HANDOFF.md`'s "Citing each success-criterion's own evidence artifact and
section, not restating it" framing (lines applied throughout its SC#1-SC#5 list).
**Apply to:** `61-HANDOFF.md`'s SC-by-SC summary — point at `61-*-EVIDENCE.md` § headings, do
not re-derive the verdicts.

### Checksum-guard reversion protocol
**Source:** `57-CLOSEOUT-GUARD.md` § "Re-verification protocol".
**Apply to:** any plan that re-checks `.planning/REQUIREMENTS.md` state at phase close.

## No Analog Found

None — every artifact this phase is expected to produce has a direct, structurally close
precedent in Phases 52 and 57. The only genuine novelty is the **polarity inversion** required
in `61-HANDOFF.md` (D-12/D-13), which is a content change to an otherwise well-precedented
skeleton, not a structure with no analog.

## Wave/Plan Decomposition Precedent (for the planner's discretion)

**Phase 52** (9 plans, 6 waves): W1 `52-01` (version bump + BUMP-EVIDENCE + COVERAGE) →
W2 `52-02` (CHANGELOG, depends on 52-01), `52-03` (goal-claim test, depends on 52-01) →
W3 `52-04` (CI-EVIDENCE), `52-05` (GREEN-TREE-EVIDENCE), `52-06` (SC4-INVARIANTS), all three
depending on 52-02+52-03 and running in parallel → W4 `52-08` (CI fix, depends on 52-04) →
W5 `52-09` (CI fix continuation, depends on 52-08) → W6 `52-07` (RELEASE-EVIDENCE + HANDOFF,
depends on 52-04/05/06/08/09 — the terminal synthesis plan).

**Phase 57** (11 plans, 4 waves): W1 `57-01` (bump+BUMP-EVIDENCE+CLOSEOUT-GUARD+COVERAGE),
`57-02` (CI-EVIDENCE run 1, pre-bump), `57-03` (CHANGELOG), `57-04` (migration docs), `57-10`
(Windows fix + evidence) — all wave-1, no interdependency among most → W2 `57-05` (CI-EVIDENCE
run 2 post-bump, depends on 01/02/03/04/10), `57-06` (GREEN-TREE-EVIDENCE, depends on
01/03/04), `57-07` (GOAL-CLAIM-EVIDENCE, depends on 01) → W3 `57-08` (SC4-INVARIANTS, depends
on 05/06/07), `57-11` (the one owner-approved mid-phase `typsphinx/` fix, no deps) → W4 `57-09`
(HANDOFF, depends on 08 — terminal synthesis plan).

**Pattern common to both:** the terminal HANDOFF/RELEASE-EVIDENCE plan is always the last wave,
depending on every evidence-producing plan. **Phase 61 has no version-bump plan and no
migration-docs plan** (D-01, out-of-scope migration guide) and — per the "one dispatch is the
default" (D-09) — likely needs no CI-fix wave either, absent a mid-phase discovery. A
minimal decomposition mirroring the shared spine would be: W1 (CHANGELOG authoring +
CLOSEOUT-GUARD baseline recording, parallel, no interdependency) → W2 (GREEN-TREE-EVIDENCE +
CI-EVIDENCE dispatch, both depending on W1's CHANGELOG landing) → W3 (SC4-INVARIANTS, depending
on W2) → W4 (HANDOFF, terminal, depending on W3). This is offered as a starting point, not a
mandate — plan decomposition is explicitly Claude's Discretion per CONTEXT.md.

## Hard Constraint

**No file this phase creates may be named `61-VERIFICATION.md`** — reserved by `gsd-verifier`,
overwritten wholesale on phase close. Every evidence file above uses the
`{padded_phase}-{TOPIC}-EVIDENCE.md` or `{padded_phase}-{TOPIC}.md` naming precedent instead
(`61-CHANGELOG-EVIDENCE.md`, `61-GREEN-TREE-EVIDENCE.md`, `61-CI-EVIDENCE.md`,
`61-SC4-INVARIANTS.md`, `61-CLOSEOUT-GUARD.md`, `61-HANDOFF.md`).

## Metadata

**Analog search scope:** `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/`,
`.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/`,
`.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/` (naming variant
only), `CHANGELOG.md` (in-file house style).
**Files scanned:** 52-{CHANGELOG,CI,GREEN-TREE,HANDOFF,SC4-INVARIANTS}-EVIDENCE-family (5),
57-{same family + CLOSEOUT-GUARD + CI-EVIDENCE-RUN3} (7), all 20 PLAN.md frontmatter blocks
across both phases (wave/dependency structure), `CHANGELOG.md` full head/tail + `## [0.9.0]`
section.
**Pattern extraction date:** 2026-08-29
