# Phase 35: v0.6.5 Release Prep - Pattern Map

**Mapped:** 2026-07-29
**Files analyzed:** 10 (4 release-metadata edits, 2 test/fixture edits, 1 HANDOFF, 1 evidence file, 2 todo files)
**Analogs found:** 10 / 10

This is a release-prep phase, not a source-code phase. "Analogs" here are prior release artifacts and
document forms — the same distinction RESEARCH.md's Architectural Responsibility Map already draws
(Documentation/Release artifact tier, not a source-code tier). Everything CONTEXT.md/RESEARCH.md
already transcribed verbatim (the `## [0.6.1]` entry model, the WR-02/03/04 Fix-field candidates, the
tail-link-block current lines) is cited by section rather than re-quoted; only what those documents
did not already spell out is added below (exact surrounding lines, real current file content, and the
todo frontmatter shape).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` (`:7` version literal) | config | transform (text substitution) | same file, prior bump commit (`git log -L 7,7:pyproject.toml`) | exact |
| `uv.lock` (`:1379` version stanza) | config (generated) | transform (regenerate via tool) | same file, prior bump's regeneration diff | exact |
| `README.md` (`:317` Status line) | config/doc | transform (text substitution) | same file, prior bump commits | exact |
| `CHANGELOG.md` (`## [0.6.5]` entry + tail link block) | doc | CRUD (insert) | `## [0.6.4]` entry (many-section model) + `## [0.6.1]` entry (small-release model, already transcribed in RESEARCH.md) | exact |
| `tests/fixtures/inline_math_after_text_render_gate/index.rst` (Construct G) | test fixture | transform (reST → compiled output) | Constructs A-F already in the same file | exact |
| `tests/test_inline_math_after_text_render_gate.py` (3 new assertions) | test | request-response (subprocess build + assert) | existing numbered assertions in both test methods, same file | exact |
| `35-HANDOFF.md` | doc | CRUD (create) | `33-HANDOFF.md` | exact |
| release-evidence file (not `35-VERIFICATION.md`) | doc | CRUD (create) | `33-RELEASE-EVIDENCE.md`; secondary: `34-GATE-EVIDENCE.md` | exact |
| 2 todo files under `.planning/todos/pending/` | doc | CRUD (create) | any of the 5 existing pending todo files (frontmatter shape identical across all 5) | exact |

## Pattern Assignments

### `pyproject.toml` (config, transform)

**Analog:** the same line's own git history. RESEARCH.md's Verified Facts table already re-confirmed
`:7` is `version = "0.6.4"` and is the sole version literal (grep-verified 2026-07-29, unchanged from
CONTEXT.md). No new excerpt needed beyond the one-line diff: change `"0.6.4"` to `"0.6.5"` on that
line only. Confirmed live (this session):
```
7:version = "0.6.4"
```
Do not touch any other line in `[project]` — `[project.urls]`, `dependencies`, `classifiers` etc. are
all untouched by every prior bump (see the `## [0.6.4]`/`## [0.6.3]` entries' own "Zero new runtime
dependencies" Verified lines, both already citing an unchanged `pyproject.toml` dependency block).

### `uv.lock` (config/generated, transform)

**Analog:** Phase 33's regeneration outcome, already characterized in RESEARCH.md § Pitfall 3: the
correct post-bump diff shape is **exactly** a 1-insertion/1-deletion single-line change
(`33-RELEASE-EVIDENCE.md` SC#4's own recorded shape). Confirmed live this session:
```
1378:name = "typsphinx"
1379:version = "0.6.4"
1380:source = { editable = "." }
```
Procedure (Claude's Discretion per CONTEXT.md, but the acceptance check is fixed): run
`uv sync --extra dev --locked` after bumping `pyproject.toml`, or `uv lock` then re-sync; afterward run
`git diff --numstat uv.lock` and require it to read `1  1  uv.lock` — anything larger means a
transitive dependency was silently re-resolved and must be investigated before proceeding (RESEARCH.md
Pitfall 3, verbatim).

### `README.md` (config/doc, transform)

**Analog:** the same line's prior bump commits. Confirmed live this session, exact current text at
`:317`:
```
317:**Status**: Stable (v0.6.4) - Production ready
```
Change only the `v0.6.4` token to `v0.6.5`; the surrounding `**Python**: 3.12+ | **Sphinx**: 9.1+ |
**Typst**: 0.15+` line (`:318`) is untouched (no prior bump has ever needed to change it, and this
milestone's dependency diff is empty per RESEARCH.md's SC#4 evidence). `tests/test_readme_version_sync.py`
is the mechanized adjudicator — run it after the edit, do not eyeball-verify only.

### `CHANGELOG.md` (doc, CRUD insert)

**Analog:** `## [0.6.4]` (many-section: lead + Added/Changed/Removed/Fixed/Verified, lines 9-45 of the
current file) as the wide-end model, and `## [0.6.1]` (lead + Fixed + Verified — already transcribed
verbatim in RESEARCH.md § "Pattern: CHANGELOG entry structure") as the **exact structural match** for
this phase's D-01–D-04 shape. Per D-01/D-02/D-03, the new `## [0.6.5]` entry needs **only** a lead
paragraph, `### Fixed`, and `### Verified` — no `### Added`/`### Changed`/`### Removed`, since this
release adds/changes/removes nothing at the user-facing level (pure bug fix).

Concrete current insertion point (confirmed live this session, matches RESEARCH.md's re-measurement):
```
7:
8:## [Unreleased]
9:
10:## [0.6.4] - 2026-07-28
```
Insert the new `## [0.6.5]` section between line 8 (`## [Unreleased]`) and line 10 (`## [0.6.4] -
2026-07-28`), i.e. immediately after the blank line 9, leaving `## [Unreleased]` itself empty (as it
already is — the current file has nothing accumulated under it, consistent with every prior release
having fully drained it at bump time).

**Tail link-block rollover** — RESEARCH.md's "Pattern: tail link-block rollover" section already gives
the exact current line numbers (842/857) and the required edit (insert a `[0.6.5]:` line above 842;
rewrite line 857's compare range from `v0.6.4...HEAD` to `v0.6.5...HEAD`). Not re-quoted here; that
section is the load-bearing source. One addition: the URL template every existing line follows is
`https://github.com/YuSabo90002/typsphinx/releases/tag/vX.Y.Z` — do not vary the owner/repo segment
even though the working directory's remote may resolve elsewhere; every historical line uses this
exact literal string.

**"### Verified" wording precedent** — the `## [0.6.4]` entry's own Verified section (already excerpted
above under "Reusable Assets") is the closest model for D-04's three-item form: "Milestone invariant
held: zero new runtime dependencies, no `@preview` package version bump, the four-surface
version-sync guard … untouched, and zero changes under `typsphinx/`" — reuse this exact sentence
skeleton, substituting "the full-corpus `-b typstpdf` gate re-run is fatal-free" as D-04's third item
(this milestone, unlike 0.6.4, does touch `typsphinx/translator.py`, so the corpus-gate item is added
rather than omitted — CONTEXT.md D-04 states this explicitly).

### `tests/fixtures/inline_math_after_text_render_gate/index.rst` (test fixture, transform)

**Analog:** Constructs A-F in the same file (read in full above — 47 lines total). Every construct
follows an identical two-part convention:
1. A "Construct X: <name> -- <one-line purpose clause>." lead-in paragraph (no blank line inside the
   sentence; a two-line wrap is used when the sentence runs long, e.g. Construct C's).
2. The reST body itself, with a blank line separating the lead-in from the body.

Exact excerpt of the two most structurally relevant precedents for Construct G (labeled block math
inside a list item — closest existing analog is Construct E, unlabeled block math in a list item):

```rst
Construct E: display math inside a list item -- the visit_math_block scope.

* Text before block math.

  .. math::

     E = m c^2

  Text after block math.

Construct F: list item whose sole content is inline math -- the
single-element edge.

* :math:`a+b`
```

RESEARCH.md's "Where Construct G goes" section already drafts the exact new reST body to append
(labeled `.. math:: G = m a` with `:label: newtons-second-law` inside a list item) — follow that
verbatim as the starting point, matching Construct E's indentation exactly (2-space list-item
continuation, blank line before/after the directive block). Construct G is new content distinct from
E specifically because it must exercise `_emit_id_anchors`'s label-anchor bookkeeping, which E's
unlabeled block never touches (RESEARCH.md, same section).

### `tests/test_inline_math_after_text_render_gate.py` (test, request-response)

**Analog:** the existing numbered assertions in both test methods of the same file (416 total lines
across the two tests). Two concrete excerpt sets, chosen because they are the immediate structural
neighbors of the three new assertions:

**Mitex-path exact-string assertion convention** (`:174-176`, Construct E — the direct sibling to the
new Construct-G mitex assertion):
```python
# 7. Construct E exact-string positive (visit_math_block, D-01).
assert 'text("Text before block math.")\nmitex(`E = m c^2`)' in typ_text, (
    "Construct E (display math in a list item) did not newline-"
```
(truncated at the excerpt boundary; the full failure-message string continues past this).

**Native-path exact-string assertion convention** (`:293`, `:304`, `:309-311` — the exact convention
WR-04's target assertion must match):
```python
assert "$E = m c^2$" in typ_text, (
...
assert 'text("Text before math ")\n$E = m c^2$' in typ_text, (
    "Construct B (bullet list item, native path) did not emit "
...
assert 'text("Term ") + $E = m c^2$' in typ_text, (
    "Construct D (definition-list term, native path) did not '+' "
```
**Key convention fact (not in RESEARCH.md's own excerpt):** every native-path math literal in this
file is written with **no interior spaces** around `=` inside the `$...$` delimiters (`$E = m c^2$` —
note: spaces *around* the algebraic operators are fine, the "no interior space" rule is specifically
about the delimiter-adjacent characters, i.e. `$E` and `2$`, never `$ E` or `2 $`). RESEARCH.md's own
Pitfall/Caution section already flags this exact mismatch risk for WR-04's candidate string — this
excerpt is the concrete evidence backing that caution; derive the real Construct-G native string from
an actual build (`-D typst_use_mitex=0`), matching this no-space-at-delimiter convention.

**Failure-message convention:** every assertion pairs its condition with a named-construct, English
prose second argument (`"Construct X (<parenthetical context>) did not <expected behavior>"`) — follow
this exact two-part message shape for the three new assertions (Construct G mitex, Construct G native,
and Construct F's WR-03 exact-string, per the Fix-field candidates RESEARCH.md already transcribed
verbatim under "Pattern: gate-test assertion additions").

**Numbering convention:** assertions are numbered sequentially in a leading comment (`# 7. Construct
E ...`, `# 8. Construct A ...`) within the mitex test (currently through at least 8) and unnumbered-but-
commented in the native test (currently at least 4 numbered comments present, e.g. `# 3. Construct B
native exact-string positive.`, `# 4. Construct D native exact-string positive.`). New assertions
should continue each test's own numbering sequence — do not renumber existing comments.

## Shared Patterns

### CHANGELOG lead-paragraph register

**Source:** `## [0.6.3]` and `## [0.6.4]` lead paragraphs (both already read above/in RESEARCH.md).
**Apply to:** the `## [0.6.5]` lead paragraph.
Convention: 2-4 sentences — (1) what changed from the user's perspective, (2) the scope/blast-radius of
the runtime change (e.g. "the only runtime change is one site in the translator" — CONTEXT.md D-03's
own phrasing, already essentially drafted), (3) a closing "Zero new runtime dependencies; the bundled
`@preview` version-sync surface is untouched" sentence, verbatim-reused across 0.6.1/0.6.3/0.6.4 with
only minor wording variance — reuse this exact closing sentence for 0.6.5 as well (it remains true per
RESEARCH.md's SC#4 evidence).

### Todo file frontmatter and body shape

**Source:** `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` (read in full).
**Apply to:** both new todo files (WR-01, `release.yml` release-notes rework).

Exact frontmatter block (YAML, delimited by `---`):
```yaml
---
created: 2026-07-22T23:55:07+09:00
title: `sphinx-build -b linkcheck` の CI ジョブを追加する
area: ci, docs
files:
  - .github/workflows/ci.yml (既存の py312/py313 + lint/type/cov マトリクスに新ジョブを追加する候補先)
  - .github/workflows/docs.yml (ドキュメント系ワークフロー。linkcheck をここに追加する案もあり得る)
  - tox.ini (新 `[testenv:linkcheck]` の追加先)
  - docs/source/conf.py (`linkcheck_ignore` 等の Sphinx linkcheck 設定を書く先)
---

## Problem

<narrative, several paragraphs, mixing measured facts and citations to the discovering phase>

## Solution

<bulleted concrete next steps, each grounded in a specific file/mechanism>
```

**Observed fact to report plainly, per phase-mapper instructions (not to be decided here):** all five
existing pending todo files are written in Japanese — title, Problem, and Solution bodies. `created`
uses ISO-8601 with the project's local UTC+9 offset (`+09:00`), matching commit-time conventions
elsewhere in this repo. `area` is a short comma-separated tag list (`ci, docs`). `files` is a YAML list
where each entry is `path (Japanese-language parenthetical rationale for why that file is a candidate
edit site)` — not just a bare path. **Filename convention:** `YYYY-MM-DD-kebab-case-english-slug.md`
(date-prefixed, English slug even though the body is Japanese) — e.g.
`2026-07-22-add-sphinx-linkcheck-ci-job.md`, `2026-07-25-derive-typst-lang-duplicated-warning-block.md`.
The two new todo files (WR-01 and the `release.yml` rework) should use today's date (`2026-07-29`) as
the prefix and a slug describing the deferred fix, matching this exact form — the planner/executor
decides the precise wording per CONTEXT.md's Claude's Discretion note, but the filename/frontmatter/
body **shape** above is the observed, unambiguous convention to replicate.

### `35-HANDOFF.md` structure

**Source:** `33-HANDOFF.md` (read in full above). Reusable shape:
1. Opening section: "What this phase satisfied, and what it did not" — quote the governing
   requirement (REL-03 here, REL-02 there), list what THIS phase's plans satisfied with SC#
   cross-references, then explicitly name what remains structurally out of reach (the tag/publish
   half) and who owns it (`/gsd-complete-milestone` or "human (owner-manual)").
2. "## Checklist" — a numbered list, each item stating **Owner** and **Ordering** (dependency on prior
   items) before the action prose. Phase 35's known items are already enumerated in CONTEXT.md
   `<specifics>` § "Known items for `35-HANDOFF.md`" (6 items: PR merge, tag push, translations-repo
   submodule bump+tag per D-08, RTD stable confirmation, REL-03 checkbox flip per D-10, confirming the
   two todos are filed) — map each directly onto this numbered-checklist shape, following `33-HANDOFF.md`'s
   exact Owner/Ordering phrasing convention (e.g. "**Owner:** `/gsd-complete-milestone`." /
   "**Owner:** human (owner-manual — no automated acceptance criterion is possible; …)").
3. "## Not done in this phase, by design" — a bulleted absolute list of every irreversible action NOT
   taken (no tag, no PyPI publish, no GitHub Release, PR not merged, no RTD setting changed).
4. "## Proof the fence held" — verbatim `git tag -l vX.Y.Z` and `git ls-remote --tags origin vX.Y.Z`
   commands with transcribed (expected: empty) output, run at the very end of the phase's execution.
   RESEARCH.md's own Exact Commands table already lists these two commands for SC#5 — reuse them
   verbatim here as well, re-run fresh (not copied from a prior session).

### Release-evidence file structure

**Source:** `33-RELEASE-EVIDENCE.md` (read above) + `34-GATE-EVIDENCE.md` (cited in CONTEXT.md, RED→GREEN
recording form — not needed verbatim this phase per RESEARCH.md's own note that WR-02/03/04 are
coverage additions to already-fixed code, not new RED→GREEN proofs).
**Apply to:** the phase's evidence file (name must NOT be `35-VERIFICATION.md` — reserved by the
verifier, per project memory "gsd-verifier clobbers VERIFICATION.md" and RESEARCH.md Pitfall 5;
`35-RELEASE-EVIDENCE.md` is the exact naming precedent to reuse).

Reusable shape, section by section:
1. Opening note stating the filename deliberately avoids `{phase}-VERIFICATION.md`, and that every
   command was re-run live during execution (not carried forward from CONTEXT/RESEARCH/PATTERNS).
2. One `## SC#N: <claim>` section per success criterion, each with: a **Claim** line, then one or more
   numbered "### Step N — <purpose>" subsections, each containing a fenced `Command:` block (the exact
   shell invocation) immediately followed by a fenced `Verbatim output:` block (the real transcribed
   output, truncated only where explicitly marked "truncated … none of which affect the verdict"), and
   closing with a `### Verdict` stating **MET** or **NOT MET** plus the reasoning.
3. Point-in-time external observations (e.g. an HTTP fetch) get their own "### Observation timestamp"
   line (ISO-8601 UTC) and an explicit "### Deliberately excluded from CHANGELOG.md" note explaining
   why — this phase's analogous case is D-04's exclusion of the GATE-01 RED→GREEN record from the
   CHANGELOG (test machinery is not user-visible, already stated in CONTEXT.md D-04).
4. RESEARCH.md's own Exact Commands table is effectively the pre-drafted command list for this phase's
   SC#1/SC#3/SC#4/SC#5 evidence sections — reuse those exact commands, re-running each fresh rather
   than copying RESEARCH.md's already-captured output (which is now a day stale and, per RESEARCH.md's
   own drift analysis, the commit count in particular must never be trusted from that file).

## No Analog Found

None. Every file this phase touches or creates has a direct, well-established analog in the existing
repository (prior release-prep phases, or the same file's own pre-existing content).

## Metadata

**Analog search scope:** `.planning/milestones/v0.6.4-phases/33-v0-6-4-release-prep/`,
`.planning/phases/34-inline-math-after-text-separator-fix/`, `.planning/todos/pending/`,
`CHANGELOG.md`, `pyproject.toml`, `uv.lock`, `README.md`,
`tests/fixtures/inline_math_after_text_render_gate/index.rst`,
`tests/test_inline_math_after_text_render_gate.py`.
**Files scanned:** 12 (all read in full or via targeted `grep`/`sed` excerpts; no file in this phase's
scope exceeds ~900 lines, so no offset/limit-only strategy was required beyond `CHANGELOG.md`'s
targeted head/tail sections).
**Pattern extraction date:** 2026-07-29
</content>
