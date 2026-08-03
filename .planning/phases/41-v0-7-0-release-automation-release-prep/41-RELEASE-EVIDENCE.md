# Phase 41: v0.7.0 Release Automation + Release Prep — Release Evidence

This file rolls up all five ROADMAP success criteria (SC#1-SC#5) for Phase 41. It **cites** the
sibling evidence files that already discharge SC#1, SC#3, and SC#4 — quoting their own verdicts
rather than re-deriving them — and **measures SC#2 directly**, because no sibling plan owns SC#2.
SC#5's fence proof is taken as two independent observations at two separate moments: observation 1
is recorded below; observation 2 is recorded in `41-HANDOFF.md` § "Proof the fence held".

**Filename note:** this file is deliberately **not** named `41-VERIFICATION.md`. That name is
reserved by the `/gsd-verify-work` verifier, which overwrites it wholesale when it runs — writing
this roll-up under that name would mean it gets clobbered the next time the verifier runs. This
follows the `35-RELEASE-EVIDENCE.md` precedent from the v0.6.5 release-prep phase (per
`41-CONTEXT.md` § "Claude's Discretion", last bullet: "`41-VERIFICATION.md` is a name reserved by
the verifier and will be clobbered — a plan that accumulates evidence must use a different name...
or plan a backup-and-remerge").

**Provisioning note:** all commands below were run inside this plan's isolated git worktree
(`worktree-agent-ab094334f060dff41`), after `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync
--extra dev` and symlinking a working `uv` binary into `.venv/bin/` (`ruff` was already a working
native `.venv/bin/ruff` entry point from this sync — no NixOS dynamic-linker shim was needed this
time), per this project's `CLAUDE.md` § "Worktree-isolated execution". Every command was invoked
through `uv run` where applicable.

**Recorded:** 2026-08-03, at HEAD `569f081` ("docs(phase-41): update tracking after wave 2" — the
merge point of waves 1 and 2 that this plan's worktree was based on).

---

## SC#1: release-notes body sourced from the curated CHANGELOG section

Quoted verbatim from `.planning/ROADMAP.md` § "Phase 41: v0.7.0 Release Automation + Release Prep":

> 1. `release.yml` builds the release body from the `## [X.Y.Z]` section of `CHANGELOG.md` — proven
>    by executing the extraction against the real file for a real version, with the `git log
>    --pretty` commit dump removed rather than left as a fallback path.

**Evidence file:** `.planning/phases/41-v0-7-0-release-automation-release-prep/41-REL04-EVIDENCE.md`
(produced by plan 41-01).

**Verdict quoted verbatim from that file's own "Overall verdict" section:**

> All three sections above are MET. `release.yml` itself was not executed (explicitly recorded, not
> glossed over) — SC#1's demonstration is a direct hand-run of the committed extractor, and D-09's
> proof is a structural read of the workflow's own job graph, both fully sufficient for what this
> plan's success criteria ask for without requiring a real tag push.

**The explicit non-execution statement, also quoted verbatim** (this is the "skip is not a pass"
disclosure this roll-up's "Executed versus skipped" section below draws from):

> **Explicit non-execution statement (D-07's own instruction, read literally):**
> `.github/workflows/ release.yml` itself was **not executed** during this plan. It cannot run
> outside a real tag push (`on: push: tags: 'v*'`) or a `workflow_dispatch` invocation, and
> triggering either is forbidden by this plan's own `<prohibitions>` fence (no `git tag`, no tag
> push, no `workflow_dispatch`). Every claim below about the workflow's *behavior* is either (a) a
> direct hand-run of the same script the workflow calls (SC#1), or (b) a static read of the
> workflow file's own YAML structure (D-09). Neither is a workflow execution, and this is recorded
> honestly rather than glossed over — a skip is not a pass.

**Roll-up verdict for SC#1:** MET. The `## [X.Y.Z]` extraction script was hand-run against the real
`CHANGELOG.md` for both a real, present version (`0.6.5`, exit 0, curated section on stdout) and an
absent version (`9.9.9`, exit 1, version named in stderr) — see `41-REL04-EVIDENCE.md` § "SC#1 — the
extraction executed against the real file for a real version (D-07)". The `git log $PREV_TAG..$TAG
--pretty=format:"- %s (%h)"` commit-dump block, its `PREV_TAG` lookup, and its `if`/`else`/`fi`
branch are all deleted (not fenced behind a fallback) in the same file's whole-plan diff of
`release.yml`, confirmed by a repo-wide grep for the dump's constituent fragments returning zero
hits. `release.yml` itself was never executed by this phase — that fact is recorded honestly, not
smoothed over, and does not weaken SC#1's own verdict because SC#1's own wording asks for the
extraction to be "executed against the real file for a real version," not for a live workflow run.

---

## SC#2: version bump, CHANGELOG entry, tail link-block rollover (measured directly)

Quoted verbatim from `.planning/ROADMAP.md`:

> 2. The version reads 0.7.0 as the sole literal in `pyproject.toml`, with `uv.lock` and
>    `README.md` moved in lockstep and `typsphinx.__version__` reporting it, and a curated
>    `## [0.7.0]` CHANGELOG entry is in place with the tail link block rolled over.

**No sibling evidence file owns this criterion** — plan 41-02 delivered the underlying change
(`41-02-SUMMARY.md`), but per this plan's own `<read_first>` instruction, SC#2 is measured directly
here rather than cited, because no sibling evidence file already carries a live re-run of these
specific transcripts. Every command below was run fresh in this worktree.

### `typsphinx.__version__`

Command:
```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
```
Verbatim output:
```
0.7.0
```

### `pyproject.toml`'s version literal

Command:
```
$ grep -n "^version" pyproject.toml
```
Verbatim output:
```
7:version = "0.7.0"
```

### README's Status line

Command:
```
$ grep -n "Status" README.md
```
Verbatim output (the relevant line):
```
317:**Status**: Stable (v0.7.0) - Production ready
```

### `uv.lock`'s `typsphinx` entry

Command:
```
$ git grep -n "0.7.0" -- uv.lock
```
This grep returns many hits across `uv.lock` (dependency `upload-time` timestamp strings that
happen to contain the substring `0.7.0`, e.g. `upload-time = "2026-07-02T08:40:05.92Z"`) —
irrelevant noise for this claim. The specific `typsphinx` self-entry, isolated by reading the file
directly around its `[[package]] name = "typsphinx"` block:
```
$ sed -n '1447,1452p' uv.lock
[[package]]
name = "typsphinx"
version = "0.7.0"
source = { editable = "." }
dependencies = [
    { name = "docutils" },
```
`uv.lock`'s `typsphinx` package entry reads `version = "0.7.0"`, in lockstep with `pyproject.toml`.

### `CHANGELOG.md`'s `## [0.7.0]` heading

Command:
```
$ grep -n "^## \[0.7.0\]" CHANGELOG.md
```
Verbatim output:
```
10:## [0.7.0] - 2026-08-03
```

### The two tail link-block lines

Command:
```
$ grep -n "^\[0.7.0\]:\|^\[Unreleased\]:" CHANGELOG.md
```
Verbatim output:
```
918:[0.7.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0
935:[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.7.0...HEAD
```
The `[0.7.0]:` release-tag line is present, and `[Unreleased]:` has been advanced to compare
`v0.7.0...HEAD` (not still pointing at `v0.6.5...HEAD`) — the tail link-block rollover SC#2 asks
for is in place.

### SC#2 verdict

**MET.** `typsphinx.__version__` reports `0.7.0`; `pyproject.toml:7` carries `0.7.0` as its sole
version literal; `uv.lock`'s `typsphinx` self-entry (line 1449) agrees; `README.md:317`'s Status
line reads `Stable (v0.7.0)`; `CHANGELOG.md` carries a `## [0.7.0] - 2026-08-03` heading at line 10;
and the tail link block carries both the new `[0.7.0]:` release-tag line (918) and an advanced
`[Unreleased]:` compare link (935, `v0.7.0...HEAD`). All five surfaces agree on `0.7.0` with no
straggler still reading `0.6.5`.

---

## SC#3: the post-bump tree is green end to end, including the `ja` glyph bar

Quoted verbatim from `.planning/ROADMAP.md`:

> 3. The post-bump tree is green across the full suite, the lint/type trio, the full-corpus
>    `-b typstpdf` gate, and both docs dogfooding builds — including a re-run of the `ja` build's
>    four-check glyph bar, because any new font selection introduced by this milestone can shadow
>    the `Noto Serif CJK JP` fallback silently, with no warning or error.

This criterion has two halves, cited from two different plans' evidence files.

### Mechanical half — cite `41-GREEN-TREE-EVIDENCE.md` (plan 41-05)

**Verdict quoted verbatim:**

> **Overall: SC#3's mechanical half is MET on this measurement.** Every command in this file was
> actually run in this worktree at commit range `aa9d2f0..` (this plan's own commits); nothing was
> edited to make any of it green (`git diff --stat -- typsphinx/ tests/ scripts/ .github/
> CHANGELOG.md pyproject.toml uv.lock` over this plan's own three commits is empty, confirmed
> per-task above and again at Step 8).

Individual figures quoted from that same file, for the record (not re-measured here):
- Full suite: **805 passed, 1 skipped in 75.85s** — the one skip is the pre-existing, intentionally
  env-gated `test_empty_url_before_after` (unrelated to REL-04/REL-05).
- `black --check .`, `ruff check .`, `mypy typsphinx/`: all exit 0.
- Full-corpus `-b typstpdf` gate: **EXECUTED, not skipped** — `test_corpus_compiles_with_no_fatal_error`
  PASSED against corpus tag `v9.1.0`.
- Both docs dogfooding builds (`tox -e docs-html`, `tox -e docs-pdf`): both exit 0; the PDF build
  produces `typsphinx.pdf` at 1,968,588 bytes / 93 pages.
- The `visit_desc_sig_name` docstring diagnostic (D-12's own fix) is confirmed **absent** from both
  build logs.

**This file explicitly does not speak to the `ja` glyph bar**, quoted verbatim:

> **This file does NOT speak to the `ja` four-check glyph bar — that is SC#3's other half, owned by
> plan 41-04, running in its own parallel worktree.** Nothing in this evidence file asserts,
> implies, or depends on that comparison's result.

### `ja` four-check glyph bar — cite `41-JA-GLYPH-BAR.md` + `41-JA-GLYPHBAR-SIGNOFF.md` (plan 41-04)

**Check 1 (page count) verdict, quoted verbatim from `41-JA-GLYPH-BAR.md`:**

> **Verdict:** a zero-page-count delta despite this milestone's substantial typography changes
> (signature typesetting, structural indentation, admonition/rubric redesign, citations) indicates
> the overall pagination/column-width envelope was not shifted by the redesign...

(94 pages on both the `main`-built "before" PDF and the HEAD-built "after" PDF — delta 0.)

**Check 2 (extracted text / CJK density) verdict, quoted verbatim:**

> **Verdict:** the document-total CJK character count is essentially unchanged (+34 out of ~6,050, a
> 0.56% increase, not a drop). This is the opposite of the failure signature the check is looking
> for...

**Check 3 (embedded `/BaseFont` enumeration) verdict, quoted verbatim:**

> **Verdict:** `NotoSerifCJKjp-ExtraLight` — the one CJK-coverage font — is present on BOTH builds,
> identically (no subset-tag-stripped difference). Neither symmetric-difference entry introduces a
> NEW font FAMILY...

**Check 4 (owner visual confirmation) verdict, quoted verbatim from `41-JA-GLYPHBAR-SIGNOFF.md`:**

> **Check 4 is MET.** The owner inspected the sampled pages of both PDFs and reported no
> substituted, missing, or mismatched Japanese glyphs — the response was an unqualified "approved"
> with no reported defect on any page or in either build.

The owner's verbatim answer, also quoted from that file:

> The owner's verbatim response, in full, was exactly one word:
>
> > approved

### SC#3 roll-up verdict

**MET.** Both halves are MET with no gap, skip, or NOT MET verdict recorded in either sibling
evidence file: the mechanical half's full suite (805 passed / 1 skipped, the one skip pre-existing
and unrelated), lint/type trio, full-corpus gate (executed, not skipped), and both docs dogfooding
builds are all green (`41-GREEN-TREE-EVIDENCE.md`); and the `ja` build's four-check glyph bar shows
no evidence of font-shadowing across all four checks, including the owner's own unqualified
"approved" on check 4 (`41-JA-GLYPH-BAR.md` + `41-JA-GLYPHBAR-SIGNOFF.md`).

---

## SC#4: milestone invariants proven mechanically over the SHA-anchored diff

Quoted verbatim from `.planning/ROADMAP.md`:

> 4. The milestone invariants are proven mechanically over the SHA-anchored full milestone diff:
>    zero new runtime dependencies, the `@preview` package count still four with no new
>    version-lockstep site, and every node-handler change carrying its recorded-RED GATE-01 fixture.

**Evidence file:** `.planning/phases/41-v0-7-0-release-automation-release-prep/41-SC4-INVARIANTS.md`
(produced by plan 41-06), measured over `BASE=51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD=
aa9d2f06ad854f6f96d285d669ba4bb91b053f31` (394 commits at that plan's own measurement — a moving
target, not the anchor).

**Its own per-invariant verdict table, reproduced by quotation:**

| Invariant | What was measured | By which command(s) | Verdict |
|---|---|---|---|
| 1 — zero new runtime dependencies | `pyproject.toml`'s `dependencies` array and `[dependency-groups]` table, both sides of the range; `uv.lock`'s third-party version movement | `git diff BASE..HEAD -- pyproject.toml`, `git show {BASE,HEAD}:pyproject.toml \| sed -n '/^dependencies/,/^\]/p'`, `git diff --stat/-- uv.lock`, `grep -E '^[+-]name = \|^[+-]version = '` | **PROVEN**, with a stated non-breaching finding: the `dev` extra (not `dependencies` or `[dependency-groups]`) gained one dev-only package (`pillow`, Phase 39 D-07) — outside the runtime-dependency scope the invariant and CHANGELOG claim 1 actually assert |
| 2 — the `@preview` surface | All three declaration sites, both sides of the range; every newly added file carrying a `@preview` import, classified | `grep -n "@preview" {writer.py,template_engine.py,base.typ}` on both `HEAD` and `git show BASE:...`; `git diff --diff-filter=A --name-only \| xargs grep -l "@preview"`; `uv run pytest tests/test_preview_version_sync.py -v` | **PROVEN** — three sites line-for-line identical, four package versions unchanged, no new production sync site, two genuine fixture-mirrors both current, `docs/`'s pre-existing fourth site named as a carried Warning |
| 3 — every node-handler change carries a recorded-RED GATE-01 fixture | The hunk-attributed handler census (51 handlers, re-derived); the node-name coverage map (all 51 mapped); the 3 single-hit handlers spot-checked against real assertions and a doctree-confirmed node occurrence; Phase 40.1's 4-row RED manifest folded in with existence + SHA-resolution confirmation; D-12's own change classified as docstring-only with its own proof | `census.py` (hunk attribution over `git diff -U0`), `coverage_map.py` (node-name grep over `tests/*.py`), `inspect_doctree.py` (real doctree node enumeration), `test -f` / `git cat-file -e` for the 40.1 fold-in, `git show c81ca29` for D-12 | **PROVEN**, within this plan's own defined scope: the 48 multi-hit handlers rest on the node-name coverage map's "necessary but not sufficient" strength (per-hunk assertion tracing for all 48 was not independently performed — only the 3 single-hit rows, per this plan's own acceptance criteria and `41-RESEARCH.md` Open Question 2's recommendation) |

**Overall verdict quoted verbatim:**

> **No invariant is NOT PROVEN.** Invariant 3's PROVEN verdict carries one explicit scope
> qualification (above) rather than an unqualified blanket claim — stated so a future reader does
> not read "PROVEN" as "every one of 51 handlers individually assertion-traced."

### SC#4 roll-up verdict

**MET (PROVEN on all three invariants).** No invariant in `41-SC4-INVARIANTS.md` is recorded as
PARTIAL or NOT PROVEN — Invariant 1 carries a stated non-breaching finding (a dev-only `pillow`
addition from Phase 39, outside the runtime-dependency scope the invariant asserts), and Invariant
3 carries an explicit scope qualification (only the 3 single-hit handlers were individually
assertion-traced; the other 48 rest on the node-name coverage map's "necessary but not sufficient"
strength). Both qualifications are carried forward here rather than smoothed into an unqualified
pass, per this roll-up's own prohibition against upgrading a caveated verdict.

---

## SC#5: no irreversible action taken — the fence, observation 1 of 2

Quoted verbatim from `.planning/ROADMAP.md`:

> 5. No irreversible action has been taken at phase close — local and remote `v0.7.0` tags are both
>    empty — and a standalone handoff checklist records exactly what `/gsd-complete-milestone` will
>    execute (merge, tag, `release.yml`, PyPI + GitHub Release, and the standing second tag on
>    `typsphinx-doc-translations`).

This section records **observation 1 of 2**. Observation 2 — a second, independent probe at a
separate moment — is recorded in `41-HANDOFF.md` § "Proof the fence held".

**Timestamp:** 2026-08-03T12:12:29Z (immediately before the two probes below).

Command:
```
$ git tag -l v0.7.0
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Command:
```
$ git ls-remote --tags origin v0.7.0
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Both probes returned genuinely empty output (not an error) — the release workflow
(`.github/workflows/release.yml`) fires only on a `v*` tag push, so an absent tag on both the local
repository and `origin` is what makes "nothing was published" a mechanical claim.

**Tree state at the moment of observation**, for the record:

Command:
```
$ git log --oneline -5
```
Verbatim output:
```
569f081 docs(phase-41): update tracking after wave 2
9922819 chore: merge executor worktree (worktree-agent-a42d10f0bf8d257ce)
2d3fa04 chore: merge executor worktree (worktree-agent-a07298901969db601)
45b7dfc chore: merge executor worktree (worktree-agent-a53198d22b20ea40f)
b4c48a8 docs(41-04): append self-check results to SUMMARY.md
```

State explicitly, for the record: no pull request has been opened or merged by this plan, no
package has been uploaded to PyPI, no GitHub Release has been created, and no `git tag` command has
been run against `v0.7.0` (or any tag) anywhere in this phase's execution.

### SC#5 (observation 1) verdict

**Observation 1: EMPTY on both probes, exit 0 on both.** This is one of the two independent
observations SC#5 requires; observation 2 follows in `41-HANDOFF.md` at a separate moment.

---

## Phase verdict

| Success Criterion | Status | Evidence |
|---|---|---|
| SC#1 — release body sourced from curated CHANGELOG section | **PROVEN** | `41-REL04-EVIDENCE.md` |
| SC#2 — version bump, CHANGELOG entry, tail link rollover | **PROVEN** | this file, § SC#2 (measured directly) |
| SC#3 — post-bump tree green, including `ja` glyph bar | **PROVEN** | `41-GREEN-TREE-EVIDENCE.md` + `41-JA-GLYPH-BAR.md` + `41-JA-GLYPHBAR-SIGNOFF.md` |
| SC#4 — milestone invariants proven mechanically | **PROVEN** (with two stated, non-breaching qualifications — see SC#4 section above) | `41-SC4-INVARIANTS.md` |
| SC#5 — no irreversible action, fence proven twice | **PROVEN** (observation 1 of 2 here; observation 2 in `41-HANDOFF.md`) | this file, § SC#5, and `41-HANDOFF.md` § "Proof the fence held" |

**No criterion is PARTIAL, NOT PROVEN, or OPEN.** Both stated qualifications (Invariant 1's dev-only
`pillow` addition; Invariant 3's scope limited to individually assertion-tracing only the 3
single-hit handlers) are explicitly non-breaching findings recorded on their own sibling evidence
file's authority, not gaps this roll-up is smoothing over.

---

## Executed versus skipped

A phase-wide list of every command, across all seven plans, that this phase's own evidence files
record as **not executed**, gathered from each sibling file's own executed-versus-skipped statement.
A skip is not a pass — this list exists so a skip cannot silently disappear at roll-up time.

| Command / action | Plan | Reason not executed |
|---|---|---|
| `.github/workflows/release.yml` itself (a real workflow run) | 41-01 | Cannot run outside a real tag push (`on: push: tags: 'v*'`) or a `workflow_dispatch` invocation; triggering either is forbidden by that plan's own prohibitions fence. SC#1 is instead discharged by a direct hand-run of the same script the workflow calls, plus a structural YAML read of the job graph. |
| `tests/test_corpus_gate.py::test_empty_url_before_after` | 41-05 (and every other plan's full-suite run in this phase) | Intentionally env-gated (`TYPSPHINX_CORPUS_REPORT=1` required) — a pre-existing, unrelated Phase 15/SC#3 concern, not something this phase's own scope covers. The ONE skip across the entire 805-item suite. |
| Per-hunk assertion tracing for the 48 multi-hit node handlers (as opposed to the 3 single-hit ones) | 41-06 | Explicitly out of this plan's own defined scope per its acceptance criteria and `41-RESEARCH.md` Open Question 2's recommendation — the 48 rest on the node-name coverage map's "necessary but not sufficient" strength rather than an individually-traced assertion, and this scope limitation is stated as part of Invariant 3's PROVEN verdict rather than hidden. |
| `git tag v0.7.0`, any tag push, `release.yml` trigger, PyPI upload, GitHub Release creation, PR open/merge | Every plan in this phase (41-01 through 41-07) | Forbidden by the prep/publish fence (Phase 33/35 precedent) that is absolute for this entire phase — these are exactly the actions `41-HANDOFF.md` records as the checklist for `/gsd-complete-milestone` to execute later, never for a release-prep phase to perform itself. |
| Flipping REL-04's / REL-05's checkbox or Traceability row in `.planning/REQUIREMENTS.md` | Every plan in this phase | Deliberately deferred to `/gsd-complete-milestone`'s own close-side run, per this plan's own `must_haves.prohibitions` and `41-CONTEXT.md`'s "Out of scope" list. |

**No skip listed above stands in for a pass anywhere in this phase's evidence.** Every skip is named
with its reason, sourced from the sibling file that actually recorded it.
