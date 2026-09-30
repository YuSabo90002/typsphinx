# Phase 52: v0.8.0 Release Prep (prep-only) - Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 8 (2 pure edits, 1 test-tuple edit, 1 test-class extension, 4 planning/evidence
artifacts named by CONTEXT/RESEARCH)
**Analogs found:** 8 / 8

This is a release-prep phase (fifth iteration of an established shape: Phases 23/28/33/35/41/46).
There is no new architecture — every file either edits an existing release-surface literal, extends
an existing test module, or is a planning/evidence artifact whose direct structural analog is
Phase 46's own artifact family. Two families below; both need concrete analogs per phase guidance.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `pyproject.toml:7`, `README.md:347`, `uv.lock` | config | batch (release-literal bump) | Phase 46's own bump (`46-02-PLAN.md` / `46-BUMP-EVIDENCE.md`) | exact — identical mechanism, only the version strings differ |
| `CHANGELOG.md` (`## [0.8.0]` entry + tail link-block rollover) | config/docs | batch (append + template-shaped prose) | `## [0.7.1]` entry (same file, lines 17-96) + tail link block (lines 1019, 1038) | exact — same file, immediately-preceding entry is the structural template |
| `tests/test_changelog_page_gate.py:49-63` (`RELEASE_VERSIONS`) | test | CRUD (tuple append) + request-response (drives a Sphinx build) | same file, same tuple, previous append (`"0.7.1"` was the last one added at the v0.7.1 close per `46-03-PLAN.md` Task 3) | exact — self-analog, mechanical tuple/comment edit |
| `tests/test_state_guard_shapes_gate.py::TestThreeMasterGate` (extension) | test | file-I/O (Sphinx build → PDF) + request-response (pypdf/typst.query assertions) | same class's own `test_three_masters_each_render_shared_children_once` method (lines 442-494) | exact — extend in place; see Pitfall 1 note below |
| `52-HANDOFF.md` | planning artifact | batch (checklist document) | `46-HANDOFF.md` | exact — same milestone-close shape, fewer items (no D-23 dual-run, no submodule ja-tag step is optional here) |
| `52-*-EVIDENCE.md` family (bump / CI / green-tree / release roll-up / SC#4 invariants) | planning artifact | batch (transcript recording) | `46-BUMP-EVIDENCE.md`, `46-CI-EVIDENCE.md`, `46-GREEN-TREE-EVIDENCE.md`, `46-RELEASE-EVIDENCE.md`, `46-SC4-INVARIANTS.md` | exact — same five-file shape, minus the D-20 merge-tracer and REL-04 precondition sections Phase 46 needed and this milestone doesn't |
| `COVERAGE.md` (if an external-API coverage declaration is required) | planning artifact | batch | `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/COVERAGE.md` | exact — one-line "not applicable" declaration; confirm this phase also has no external API surface before assuming it's needed |

**Hard constraint carried from CONTEXT/RESEARCH into this file: no evidence artifact may be named
`52-VERIFICATION.md`** — reserved for `gsd-verifier`, which clobbers any file with that exact name
(46-CONTEXT D-15, confirmed live in the 46 directory: `46-VERIFICATION.md` exists there as the
verifier's own output, distinct from all six `46-*-EVIDENCE.md`/`46-HANDOFF.md` planning artifacts).

---

## Pattern Assignments

### 1. `pyproject.toml:7`, `README.md:347`, `uv.lock` (config, batch bump)

**Analog:** Phase 46's own bump — read `46-02-PLAN.md` Task 1 at plan-write time for the exact
command sequence rather than re-deriving it; the mechanism is unchanged.

**Current values to move (verified this session, 52-RESEARCH.md Pattern 1):**
```
pyproject.toml:7 -> version = "0.7.1"          =>  version = "0.8.0"
README.md:347    -> **Status**: Stable (v0.7.1) - Production ready
                 =>  **Status**: Stable (v0.8.0) - Production ready
```

**Exact command sequence (copy verbatim, substituting nothing but the version string):**
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
# edit pyproject.toml:7  -> version = "0.8.0"
# edit README.md:347     -> **Status**: Stable (v0.8.0) - Production ready
uv lock
uv sync --extra dev --locked
uv run python -c "import typsphinx; print(typsphinx.__version__)"   # expect 0.8.0
uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
  tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v
```

**Why `uv sync --extra dev --locked` (not just the edit) is the load-bearing step:**
`typsphinx.__version__` is derived from `importlib.metadata`, not the literal — editing
`pyproject.toml` alone does not move it; only regenerating the editable-install `.dist-info`/`.pth`
metadata does.

**Guard tests that must stay green (all three, no new test needed for this family):**
- `tests/test_extension.py::test_version_matches_pyproject_toml`
- `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject`
- `tests/test_preview_version_sync.py` (three functions — spot-check only; this bump changes no
  template/import code)

---

### 2. `CHANGELOG.md` — `## [0.8.0]` entry + tail link-block rollover

**Analog:** `## [0.7.1]` entry, same file, lines 17-96 (quoted in full below as the skeleton to
copy), plus the tail link block, lines 1019 and 1038.

**Skeleton to copy (structure only — content is this phase's own authored work per D-04/D-05/D-06/
D-07):**
```markdown
## [0.7.1] - 2026-08-11

This release closes the gap between what typsphinx's documentation promises and what a `conf.py`
actually gets: ... Because several of these fixes tighten previously-loose configuration handling,
**this patch release can break a working configuration** — read the `### Changed` and `### Removed`
sections below, and see the "Migrating from 0.7.0 to 0.7.1" guide in the published documentation
for the exact rewrite each breaking change needs.

### Added

- **`typst_documents` now has a default, so following the Quick Start produces a PDF (CONF-08,
  DOC-11)** — with `typst_documents` unset, ... . For a project that never set `typst_documents`,
  the emitted Typst filename changes from ... . If you `#include()` the old file from your own
  Typst source, update the include path.

### Changed

- **An explicit `typst_documents` entry's title and author now reach the rendered PDF (CONF-09)**
  — ...
- **Breaking:** a declared `typst_template_function` `params` dict is now the complete parameter
  set (CONF-11) — ...
- **Breaking:** the auto-derived `lang` now reaches every non-package template route ... (CONF-12,
  DOC-13) — ...

### Fixed

- **Nested tables and figures no longer corrupt the enclosing structure ... (TBL-04, TBL-05,
  FIG-01, TOC-01)** — ...
- **Absolute image URIs from Sphinx's image converter or downloader no longer abort the Typst
  compile (Issue #130, PR #131, @christianwehe)** — ...
- **A malformed docname fails with an actionable typsphinx error, and the published changelog page
  is current (BLD-01, DOC-12)** — ...

### Removed

- **Breaking:** the `typst_authors` config value is removed (CONF-10) — ...

### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.
```

**Bullet vocabulary to reuse verbatim (D-04):**
- Lead paragraph: 2-4 sentences, states the breaking-change fact **in its second half** (not the
  opening sentence) — e.g. "Because several of these fixes tighten previously-loose configuration
  handling, **this patch release can break a working configuration**".
- Each breaking bullet's bold lead starts with the literal string `**Breaking:**` immediately
  followed by a short clause naming the change, then an em-dash, then the detail. Do not invent a
  new marker (no `### Breaking Changes` heading — D-04 explicitly rejected that shape).
- Requirement IDs are trailing, parenthesized, comma-separated, inside the bold span:
  `(CONF-08, DOC-11)`.
- `### Removed` is a section that appears **only when there is a real candidate** — v0.7.1 had one;
  v0.8.0 measured to have **none** (`git diff v0.7.1..HEAD -- typsphinx/__init__.py | grep
  add_config_value` is empty), so this phase's entry should **omit `### Removed` entirely**, not
  emit an empty heading.
- `### Verified` is **exactly three items, unchanged wording** across 0.7.0/0.7.1 — D-06 says copy
  it verbatim for v0.8.0 too, do not add a fourth item for SC#4's config invariant or a fifth for
  the round-trip evidence (those live in the phase's own evidence artifacts instead).

**Tail link-block rollover (exact two-line edit, verified this session):**
```
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.7.1...HEAD
```
becomes (insert new line immediately above the `[0.7.1]:` line; edit only the final line's compare
base):
```
[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.8.0...HEAD
```

**`## [Unreleased]` body is untouched** — its current content ("### Planned for Future Releases",
5 items) is not v0.8.0 material and stays where it is, above the new `## [0.8.0]` heading.

**Cross-check obligation, not a new-file task:** `docs/source/changelog.rst`'s "Migrating from
0.7.x to 0.8.0" section (already written by Phase 51) must **agree** with whatever three breaking
bullets this entry states — read that file in full (not just its first ~40 lines) before finalizing
the `### Changed` bullets, per RESEARCH Open Question 1 (unclear whether the collision-hard-error
breaking change already has migration-guide text).

---

### 3. `tests/test_changelog_page_gate.py:49-63` — `RELEASE_VERSIONS` tuple + comment

**Analog:** self — the same tuple/comment pair, previous append cycle (documented in
`46-03-PLAN.md` Task 3).

**Current state (verified this session, 13 entries):**
```python
# The 13 releases the published page was frozen without (0.4.4 through 0.7.1,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
# below so the two builders are held to the identical bar.
RELEASE_VERSIONS = (
    "0.4.1", "0.4.2", "0.4.3", "0.4.4", "0.5.0", "0.6.0", "0.6.1",
    "0.6.2", "0.6.3", "0.6.4", "0.6.5", "0.7.0", "0.7.1",
)
```

**Required edit:** append `"0.8.0"` and move the comment's count/range: 13 → 14, "0.4.4 through
0.7.1" → "0.4.4 through 0.8.0".

**Hard ordering constraint (Pitfall 2, recurring across every prior curation phase):** this append
is only valid **after** `## [0.8.0]` exists in `CHANGELOG.md` — `TestChangelogPageContentCoverage`
asserts every listed release's content actually appears in the built page. Sequence it as the
**last** sub-step of the CHANGELOG plan, gated on a precondition that the heading exists, exactly as
`46-03-PLAN.md` Task 3 encodes it.

**Run with the docs extra, and check the skip count, not the summary line:**
```bash
uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v
```
(plain `--extra dev` silently skips `TestChangelogPageContentCoverage` and
`TestChangelogIncludeCompilesToPdf` without ever asserting the tuple reaches the built page.)

---

### 4. `tests/test_state_guard_shapes_gate.py::TestThreeMasterGate` (extension, D-10)

**Analog:** the class's own existing method, same file, lines 442-494 — extend in place rather
than writing a new module or new fixture (RESEARCH Pattern 3 / Pitfall 1's recommendation; the
planner owns the final call per CONTEXT's Claude's Discretion, but no fixture edit is implied
either way — the fixture directory carries its own "do NOT touch" header comment).

**Imports already present (reuse, do not duplicate):**
```python
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

try:
    import typst
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
```

**The `pdf_text()` idiom to copy verbatim (lines 125-128, the `_Build` dataclass helper already
used by the existing test):**
```python
def pdf_text(self, target: str) -> str:
    pdf_path = self.pdf_dir / target.replace(".typ", ".pdf")
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)
```

**Core existing-test pattern (lines 453-494) — build once, assert marker counts + heading levels +
wrapper-text distinctness:**
```python
def test_three_masters_each_render_shared_children_once(self, all_builds):
    build = all_builds["state_guard_three_master_gate"]
    assert build.pdf_result.returncode == 0

    m1_text = build.pdf_text("manual1.typ")
    m2_text = build.pdf_text("manual2.typ")
    m3_text = build.pdf_text("manual3.typ")

    assert _marker_count(m1_text, "COMMON-A-MARKER") == 1
    assert _marker_count(m2_text, "COMMON-A-MARKER") == 1
    assert _marker_count(m1_text, "COMMON-B-MARKER") == 1
    assert _marker_count(m2_text, "COMMON-B-MARKER") == 1
    assert _marker_count(m3_text, "COMMON-B-MARKER") == 1

    m1_levels = build.heading_levels("manual1.typ", "<common_b:common-b>")
    m2_levels = build.heading_levels("manual2.typ", "<common_b:common-b>")
    m3_levels = build.heading_levels("manual3.typ", "<common_b:common-b>")
    assert m1_levels == [3]
    assert m2_levels == [2]
    assert m3_levels == [2]

    w1 = build.wrapper_text("manual1.typ")
    w2 = build.wrapper_text("manual2.typ")
    w3 = build.wrapper_text("manual3.typ")
    assert w1 != w2 != w3 != w1
```

**What D-10 needs the extension to add (RESEARCH Pattern 3, three concrete gaps, none requiring a
fixture edit):**
1. **Own-heading presence per master** — assert each master's own unique heading text is present
   in its own PDF (`"M1" in m1_text`, `"M2" in m2_text`, `"M3" in m3_text`) — proves non-shared
   content isn't silently dropped, the half the existing test never checks.
2. **Absence where not toctree'd** — `m3.rst` never reaches `common_a` (its toctree lists `[mid,
   common_b]`... verify against the fixture's actual `m3.rst` toctree at plan time), so assert
   `_marker_count(m3_text, "COMMON-A-MARKER") == 0`. One-line addition, closes "nothing extra leaked
   in".
3. **Page-count / page-level assertion** — SC#3 explicitly names "text/page assertions"; the
   existing test has text-occurrence and heading-level (via `typst.query`) but no `len(reader.pages)`
   or page-index query. Add a page-count sanity check per master PDF.

**Idiom for the new assertions (from RESEARCH Code Examples section, already-shaped):**
```python
m3_text = build.pdf_text("manual3.typ")
assert "M3" in m3_text                                    # own heading present
assert _marker_count(m3_text, "COMMON-A-MARKER") == 0      # not reachable from m3 -- must be absent
```

**Fixture is load-bearing and marked do-not-touch** (`tests/fixtures/state_guard_three_master_gate/
conf.py:17-27`) — no fixture edit is implied by any of the three additions above; all three read
off content the fixture already contains (own headings, non-membership, page structure).

**Skip/pass discipline to preserve:** the class inherits the module's
`skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE))` guard and `@pytest.mark.slow` marker — do not
loosen either to force a green run (Security Domain § Known Threat Patterns, "test gate silently
weakened").

---

### 5. `52-HANDOFF.md` (planning artifact)

**Analog:** `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-HANDOFF.md`

**Heading structure to copy (verified this session):**
```
# Phase 52: v0.8.0 Release Prep (prep-only) — Publish & Owner-Manual Handoff Checklist

## What this phase satisfied, and what it did not

## Checklist
### 1. Open the pull request and merge it to `main`
### 2. Push the `v0.8.0` tag on the merge commit
### 3. Let `release.yml` run to completion: `validate` → `build` → `publish-pypi` → `create-release`
### 4. [46's item 4 was the doc-translations submodule tag -- confirm this milestone still needs it,
     or drop the item; not asked as a locked decision in 52-CONTEXT]
### 5. Confirm Read the Docs `stable` is green and reports `0.8.0`
### 6. Flip REL-07's checkbox and Traceability row in `REQUIREMENTS.md`
### 7. Re-date the `## [0.8.0]` CHANGELOG heading if needed, and re-confirm the extractor

## Not done in this phase, by design
## Deferred by decision, not oversight
## Proof the fence held
```

**Content this phase's version must additionally carry (per 52-CONTEXT D-01/D-03, no 46 analog for
this specific content):** the four minor defects and the `:numref:` record, named individually with
their `todos/pending/*.md` filenames and reasons — 52-CONTEXT's own `<deferred>` section is the
source list to transcribe. 46-HANDOFF's "Deferred by decision, not oversight" section is the
structural slot this content goes in (46's own version records its own D-16-shaped deferrals in that
same slot — read it at plan-write time for the exact prose register to match).

**"Proof the fence held" section — copy the two-observation pattern verbatim:**
```bash
git tag -l v0.8.0                      # expect empty
git ls-remote --tags origin v0.8.0     # expect empty
```
recorded with its own `date -u` timestamp, as the **second** of two independent observations (the
first lives in the roll-up evidence file, item 6 below) — per the standing
`35-HANDOFF.md`/`41-HANDOFF.md`/`46-HANDOFF.md` convention.

**Reserved-name constraint:** this file must never be named `52-VERIFICATION.md`.

---

### 6. `52-*-EVIDENCE.md` family (planning artifacts)

**Analogs and heading structures (verified this session, grepped from the live 46 directory):**

`46-BUMP-EVIDENCE.md` → adapt as `52-BUMP-EVIDENCE.md`:
```
# Phase 52 Plan NN — Bump Evidence
## SC#1 — version-literal lockstep
### Before/after values of the three surfaces
### `uv lock` transcript
### `uv sync --extra dev --locked` transcript
### `uv lock --check` transcript
### `python -c "import typsphinx"` read-back
### Acceptance-criteria greps (all run against the post-bump tree)
### `[project] dependencies` byte-identity check
## Guard tests
### `tests/test_extension.py::test_version_matches_pyproject_toml`
### `tests/test_readme_version_sync.py`
### `tests/test_preview_version_sync.py`
### Combined battery (JUnit-XML)
## Invariant spot-check
## Executed versus skipped
```

`46-CI-EVIDENCE.md` → adapt as `52-CI-EVIDENCE.md` (this milestone needs only **one** run, not two —
RESEARCH Pattern 4 confirms no separate Windows-repair check run is needed this time, unlike 46's
D-23 dual-run):
```
# Phase 52 — CI Evidence
## The authority run
### Pre-push confirmation
### Pushed SHA
### Push
### Dispatch
### Job conclusions
### Why this run is the authority
### No irreversible action
```
(Drop 46's "run 1 — the Windows check run" section and its merge/conflict-resolution subsections —
those existed only because Phase 46 needed an `origin/main` merge this milestone doesn't.)

`46-GREEN-TREE-EVIDENCE.md` → adapt as `52-GREEN-TREE-EVIDENCE.md`:
```
# Phase 52 — Green-Tree Evidence (Local Half of SC#3)
## Local evidence — docs builds
### `tox -e docs-html`
### `tox -e docs-pdf`
### Produced PDF
## Local evidence — full-corpus gate
## Executed versus skipped
```
(Drop 46's "Local evidence — ja build (D-12)" section entirely — no CONF-12-shaped requirement this
milestone, per RESEARCH's wave decomposition note.)

`46-SC4-INVARIANTS.md` → adapt as `52-SC4-INVARIANTS.md`:
```
# Phase 52 — SC#4 Milestone-Invariant Sweep
## Anchor
## Scale of the swept diff
## Invariant 1 — zero new runtime dependencies
### The `[project] dependencies` array, both sides
### Broader eyeball check — the full `pyproject.toml` diff
### Verdict — Invariant 1
## Invariant 2 — the `@preview` count is still four, no new lockstep site
### The mechanical identity check
### Repo-wide `@preview/` enumeration
### Verdict — Invariant 2
## Invariant 3 — no new `typst_*` config value
### The mechanical identity check (`grep add_config_value`)
### Verdict — Invariant 3
## Positive control  <- NEW, RESEARCH Pattern 5 flags 46 never attempted this rigorously
## Roll-up verdict
```
Note the structural difference from 46: this milestone's invariant #3 is "no new `typst_*` config
value" (D-09), not 46's "the prep-only fence over Phase 46" (which was specific to catching Phase 46
scope creep against its own tree) — do not copy 46's Invariant 3 content, only its section-heading
shape. Add a genuine **positive control** section per RESEARCH Pattern 5 — cite
`tests/test_preview_version_sync.py`'s historical catch (the v0.6.3 close's `custom.typ` drift
incident, recorded in `STATE.md`) as the `@preview` invariant's control, and a known historical
`add_config_value` addition (e.g. the CONF-04 `typst_elements` era, `git diff v0.6.2..v0.6.3 --
typsphinx/__init__.py | grep add_config_value`) as the config-value invariant's control — 46 recorded
figures and reasoning but no independent detector-liveness proof; this is new work, not a repeat.

`46-RELEASE-EVIDENCE.md` → adapt as `52-RELEASE-EVIDENCE.md` (the roll-up):
```
# Phase 52: v0.8.0 Release Prep (prep-only) — Release Evidence
## SC#1
## SC#2
## SC#3
### CI authority
### Local half
### SC#3 roll-up verdict
## SC#4
### SC#4 roll-up verdict
## SC#5: no irreversible action taken — the fence, observation 1 of 2
### SC#5 (observation 1) verdict
## Phase verdict
## Executed versus skipped
```

`COVERAGE.md` → adapt as `52-COVERAGE.md` (or reuse the bare `COVERAGE.md` name if the phase
directory convention expects it un-prefixed — confirm against 46's placement: it sits at the phase
directory root, not phase-number-prefixed) — a one-line "not applicable, no external API surface"
declaration, same as 46's.

**None of the six files above may be named `52-VERIFICATION.md`** — `gsd-verifier` reserves and
clobbers that exact name (46-CONTEXT D-15, and the live 46 directory shows `46-VERIFICATION.md`
existing as a distinct, separate file from all six evidence artifacts and the handoff).

---

## Shared Patterns

### Evidence culture (applies to every artifact in family 2 and the HANDOFF)
**Source:** every `46-*-EVIDENCE.md` file, and the project's own standing convention (52-RESEARCH.md
§ Established Patterns).
Commands and their output are transcribed **verbatim**; `human_needed` is recorded honestly;
**abstain rather than assert without direct evidence**. Every figure in this phase's own CONTEXT/
RESEARCH documents was itself produced this way — the evidence files must hold to the same bar, not
merely restate CONTEXT's numbers as if re-verified.

### Sphinx build invocation (applies to any new/extended test)
**Source:** `tests/test_state_guard_shapes_gate.py:81-106` (`_run_sphinx_build`), reused identically
across 20+ gate modules.
```python
subprocess.run(
    [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
    capture_output=True, text=True,
)
```
Always `sys.executable -m sphinx`, never a bare `sphinx-build` on `PATH` — sidesteps the documented
NixOS-sandbox PATH-shadowing hazard.

### Skip-vs-pass discipline (applies to the D-10 extension and to corpus-gate evidence)
**Source:** `tests/test_corpus_gate.py:270-284` (skips, never fails, when the corpus is
unavailable) and `tests/test_state_guard_shapes_gate.py`'s own
`skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE))` guard.
Any evidence transcript must capture the per-test PASSED/SKIPPED distinction explicitly (`-v`, or a
JUnit XML with an explicit `skipped=` count check) — a bare summary line is not sufficient evidence
that a gate actually ran (Pitfall 4).

### CI dispatch and polling (applies to the CI-authority evidence file)
**Source:** `46-01-PLAN.md` / `46-04-PLAN.md` Task 1, re-verified live this session.
```bash
git push origin HEAD:refs/heads/gsd/v0.8.0-multi-master-composition
gh workflow run ci.yml --ref gsd/v0.8.0-multi-master-composition
gh run list --workflow=ci.yml --branch gsd/v0.8.0-multi-master-composition \
  --limit 5 --json databaseId,headSha,event,status
gh run watch "$RUN_ID"
gh run view "$RUN_ID" --json jobs
```
Never use `gh workflow run release.yml` or open a PR — both are publish-half actions and stay out
of scope (Pattern 6, prep/publish fence).

### Prep/publish fence (applies to every file in this phase)
**Source:** RESEARCH Pattern 6, unchanged since Phase 33.
Forbidden: `git tag v0.8.0`, triggering `release.yml` for real, PyPI/twine upload, `gh release
create`, `gh pr create`/`gh pr merge`, advancing the `typsphinx-doc-translations` submodule pin,
flipping REL-07's checkbox/Traceability row. Permitted: any tracked-file edit, `git commit`, a plain
fast-forward `git push`, `gh workflow run ci.yml` (not `release.yml`), `uv lock`/`uv sync`/`tox -e
<env>`/`pytest`, hand-running `scripts/extract_changelog_section.py` (no side effects — its own
docstring says the version arg is only ever used for string-equality comparison).

---

## No Analog Found

None. Every file this phase touches or creates has a direct, load-bearing analog in the codebase or
in Phase 46's own artifact family — this is expected for a release-prep phase, the fifth iteration
of an established pattern.

---

## Metadata

**Analog search scope:** repo root (`pyproject.toml`, `README.md`, `CHANGELOG.md`,
`docs/source/changelog.rst`), `tests/` (`test_changelog_page_gate.py`,
`test_state_guard_shapes_gate.py`, `test_state_guard_composition_gate.py`,
`test_readme_version_sync.py`, `test_preview_version_sync.py`, `test_extension.py`,
`test_corpus_gate.py`), `tests/fixtures/state_guard_three_master_gate/`, and
`.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/` (all `PLAN.md`/`SUMMARY.md`/
evidence/handoff files).
**Files scanned:** ~20 (direct reads) plus grep-located line ranges in `CHANGELOG.md` (1038 lines)
and `tests/test_state_guard_shapes_gate.py` (~500+ lines, targeted non-overlapping reads only).
**Pattern extraction date:** 2026-08-15
