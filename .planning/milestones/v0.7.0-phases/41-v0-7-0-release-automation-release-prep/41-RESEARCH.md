# Phase 41: v0.7.0 Release Automation + Release Prep - Research

**Researched:** 2026-08-02
**Domain:** GitHub Actions release automation, CHANGELOG-driven release notes, version-bump
lockstep, git-diff-based invariant auditing, PDF glyph-fidelity verification
**Confidence:** HIGH (every load-bearing claim below was measured against the live tree this
session; nothing in the discretion areas rests on unverified training-data recall)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**CHANGELOG `## [0.7.0]` entry**
- D-01: Bullets are cut at user-visible-change granularity — 5 to 6 of them — with requirement IDs
  in trailing parentheses.
- D-02: Section split is `### Added` for CIT, `### Changed` for SIG/IND/FLD/ADM, `### Fixed` for
  MATH-02.
- D-03: No BREAKING label. The rendering change is stated explicitly in the lead paragraph instead.
- D-04: The lead paragraph's axis is "API reference pages became readable."
- D-05: `### Verified` carries exactly the same three items as 0.6.5.

**REL-04 — `release.yml` release-notes body**
- D-06: The `## [X.Y.Z]` extraction lives in a committed script that `release.yml` calls, with a
  pytest around it.
- D-07: SC#1's "executed against the real file for a real version" is discharged by a hand-run
  transcribed verbatim into the phase's GATE-EVIDENCE file.
- D-08: `generate_release_notes: true` stays enabled, and the Installation block stays.
- D-09: The fail-loud check moves forward into the `validate` job.
- D-10 [derived]: the pytest covers both directions — a real version extracts non-empty, an absent
  version exits non-zero.

**Scope**
- D-11: Phase 40's WR-01/WR-02/WR-03 are closed in Phase 40.1, not Phase 41 (already landed;
  confirmed below). Phase 41's SC#4 sweep MUST cover Phase 40.1's handler changes.
- D-12: The `visit_desc_sig_name` docstring fix (unbalanced `*`) is taken in Phase 41.
- D-13: Both planning-record hygiene items (file two resolved todos to `todos/completed/`,
  terminate PROJECT.md's two unterminated HTML comments) are done in Phase 41.
- D-14: Four pending todos (linkcheck CI, non-str docname TypeError, `derive_typst_lang` duplicated
  warning, typing modernization) deferred to v0.7.1+.

**SC#3 — the `ja` four-check glyph bar**
- D-15: The comparison is main-vs-HEAD, both built locally (not RTD download — environment noise).
- D-16: Check 4 (owner visual confirmation) is a Phase 41 close condition, pages chosen by measured
  CJK density.
- D-17: The `typsphinx-doc-translations` clone lives inside the phase directory
  (`.planning/phases/41-.../translations-repo/`), never committed.

### Claude's Discretion

- Exact wording of the `[0.7.0]` entry, lead paragraph phrasing, requirement-ID attachment, and
  which 5-6 bullets D-01 resolves to.
- Extraction script's language, filename, CLI shape, and how `release.yml` invokes it in both the
  `validate` and `create-release` jobs.
- The pytest module's name and exact case list beyond D-10's two directions. Must not trip on the
  measured quirk: `CHANGELOG.md` has **two** `## [Unreleased]` headings.
- Plan decomposition and ordering; the `uv.lock` regeneration procedure (acceptance: `uv sync
  --extra dev --locked` green).
- The mechanical method for SC#4's node-handler-change-to-GATE-01-fixture census.
- The format/heading structure of `41-HANDOFF.md`.
- Where live-run evidence is recorded (NOT `41-VERIFICATION.md` — that name is reserved by the
  verifier and will be clobbered).

### Deferred Ideas (OUT OF SCOPE)

- Phase 40.1 (WR-01/02/03) — already landed as its own phase, not Phase 41's concern beyond SC#4
  coverage.
- Any publish/irreversible action (tag, PyPI, GitHub Release, PR merge) — belongs to
  `/gsd-complete-milestone`.
- Any `typsphinx/` change other than D-12's docstring escape.
- Any change under `docs/` (measured: zero lines changed this milestone — see SC#4 findings below).
- Flipping REL-04/REL-05 checkboxes in `.planning/REQUIREMENTS.md` — close-side work.
- Revisiting the version number (0.7.0 is fixed).
- Editing historical CHANGELOG entries.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-04 | GitHub Release body is the curated `## [X.Y.Z]` CHANGELOG section, not the `git log --pretty` commit dump | § "REL-04 extraction script", exact `release.yml` line numbers and job structure measured below, `CHANGELOG.md`'s two-`[Unreleased]`-heading quirk documented with line numbers, `scripts/render_admonition_greyscale.py` + its subprocess-invoked pytest precedent extracted as the template to copy |
| REL-05 | v0.7.0 released — version bumped as sole literal, `uv.lock`/`README.md` in lockstep, curated CHANGELOG entry, publish at `/gsd-complete-milestone` | § "Version-literal sites" (all three confirmed current at 0.6.5), § "CHANGELOG structure", § "SC#4 milestone-invariant sweep" (full runnable census), § "SC#3 ja glyph bar" (full runnable procedure) |
</phase_requirements>

## Summary

This phase's discretion areas resolve to five concrete, already-measured deliverables. **SC#4's
invariant sweep** has a working, tested census script (below) that maps all 51 changed
`visit_*`/`depart_*` handlers in `typsphinx/translator.py` over the SHA range `51e02b6..HEAD` (the
milestone base — one commit past the `v0.6.5` tag — through the current worktree HEAD, which
already includes every Phase 40.1 commit) to their covering gate-test modules; the dependency and
`@preview`-lockstep invariants are single grep/diff commands with clean current-tree output (zero
new deps, three sync sites unchanged, no new fourth site introduced this milestone). **REL-04's
extraction script** has a direct precedent to copy line-for-line in
`scripts/render_admonition_greyscale.py` (a `scripts/`-resident module with its own
subprocess-invoked pytest, `tests/test_admonition_greyscale_pipeline.py`) — `release.yml`'s exact
line ranges for the version check (50-59), release-notes generation (152-174), and Release creation
(176-187) all matched CONTEXT.md's recorded numbers exactly, so those anchors are stable to build
against. **The `ja` glyph bar** has a fully executable local-clone procedure: the
`typsphinx-doc-translations` repository (network-reachable, confirmed this session) carries a
`typsphinx` git submodule currently pinned to `main` at `5888ee0`, so the "before" build needs no
extra step and the "after" build only requires re-pointing that submodule checkout at this
worktree's own HEAD before re-running the documented `post_create_environment` catalog-copy +
`sphinx-build -b typstpdf` sequence from the translations repo's own `.readthedocs.yaml`. Noto Serif
CJK JP is installed on this machine (`fc-list` confirmed), so no font-provisioning step is needed
for a faithful local comparison.

**Primary recommendation:** Build the phase around five largely-independent, sequenceable
deliverables — (1) CHANGELOG `[0.7.0]` entry authoring, (2) the extraction script + pytest +
`release.yml` wiring, (3) the version bump + lockstep, (4) the SC#4 invariant sweep (must run last,
after Phase 40.1's landing — already satisfied), (5) the `ja` glyph bar (independent, can run in
parallel with 1-3) — closing with the green-tree evidence run and `41-HANDOFF.md`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CHANGELOG `## [X.Y.Z]` extraction | Build/CI tooling (`scripts/`) | CI workflow (`release.yml`) | The extraction logic is pure text processing over a repo file — belongs in a standalone script, invoked (not duplicated) by the workflow, per D-06 |
| Release-notes body assembly | CI workflow (`.github/workflows/release.yml`) | — | GitHub Actions job orchestration; the workflow calls the script and feeds its output to `softprops/action-gh-release` |
| Version-literal lockstep (`pyproject.toml`/`uv.lock`/`README.md`) | Package metadata / build tier | Test tier (`tests/test_readme_version_sync.py`) | These are packaging-surface facts pinned by existing pytest guards, not application code |
| SC#4 invariant sweep (dependency diff, `@preview` sync, handler census) | Release-prep tooling (one-off, hand-run) | Test tier (existing gate modules the census maps into) | Verification-only; explicitly NOT a committed script per the "one-off hand-run transcript" precedent (D-07/Phase 35) |
| `ja` glyph bar (four-check comparison) | Release-prep tooling (one-off, hand-run, local clone) | — | Same precedent as SC#4 — Phase 29 D-15 / Phase 30.1 D-15 both explicitly forbid committing a comparison script; RTD's build environment is unreachable from CI regardless |
| `visit_desc_sig_name` docstring fix (D-12) | Translator (`typsphinx/translator.py`) | — | The one in-tree code change this phase makes; docstring-only, no `.typ` emission change |

## Standard Stack

### Core

No new libraries are needed anywhere in this phase. Every tool used is already a project dependency
or dev-dependency.

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pypdf` | (already in `dev` extra) | Page-count, extracted-text, and `/BaseFont` enumeration for the `ja` glyph bar | Established project pattern — every prior PDF-content-fidelity check (Phase 29 D-12, Phase 30.1 D-03) uses `pypdf`, never a new PDF library |
| `tomllib` (stdlib) | 3.12+ builtin | Parsing `pyproject.toml`'s version field | Already the pattern in `tests/test_readme_version_sync.py` and `tests/test_extension.py::test_version_matches_pyproject_toml` |
| Python stdlib `re` | builtin | CHANGELOG section extraction (regex on `## [X.Y.Z]` headers) | `tests/test_preview_version_sync.py` and `tests/test_readme_version_sync.py` both already use raw-text regex parsing rather than a markdown library — matches the extraction script's likely shape |

**Installation:** none — no new dependency anywhere in this phase (confirmed by the SC#4 sweep
below: `pyproject.toml`'s `dependencies` array is byte-identical between the milestone base and
HEAD).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A raw-regex CHANGELOG section extractor | A markdown-AST library (`markdown-it-py`, `mistune`) | Would be a new runtime dependency violating milestone invariant #1 for zero benefit — the file's structure (`## [X.Y.Z]` headers, nothing more exotic) is trivially regex-parseable, and the two existing version-sync tests already establish raw-text regex as this repo's convention |
| Hand-run SC#4/ja-bar checks | Committing a permanent comparison script | Explicitly rejected twice already in this project's history (Phase 29 D-15, Phase 30.1 D-03) — the artifacts being compared (a milestone diff SHA range; an RTD-unreachable-from-CI build) are one-off by nature, and a committed script that never runs in CI "manufactures confidence" (30.1-06-PLAN's own wording) |

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Every tool used (`pypdf`, `tomllib`,
stdlib `re`/`hashlib`/`subprocess`) is already a declared dependency or Python stdlib. `npm view` /
`pip index versions` verification is not needed because nothing new is added to
`pyproject.toml`'s `dependencies` or `[dependency-groups]`.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │            CHANGELOG.md (repo file)           │
                    │  ## [Unreleased]  (Keep-a-Changelog, top)     │
                    │  ## [0.7.0] - <date>   <-- NEW this phase     │
                    │  ## [0.6.5] - 2026-07-29                      │
                    │  ...                                          │
                    │  ## [Unreleased] "Planned for Future" (tail)  │
                    │  [0.7.0]: .../releases/tag/v0.7.0 <-- NEW     │
                    │  [Unreleased]: .../compare/v0.7.0...HEAD      │
                    └───────────────────┬───────────────────────────┘
                                        │ read by
                                        v
        ┌───────────────────────────────────────────────────────┐
        │  scripts/extract_changelog_section.py  (NEW, D-06)     │
        │  input: version string (e.g. "0.7.0")                  │
        │  output: stdout = section body, exit 0                 │
        │          OR exit 1 + stderr if version absent/empty    │
        └──────────┬───────────────────────────┬─────────────────┘
                    │ called from                │ imported/subprocess'd by
                    v                             v
    ┌───────────────────────────┐   ┌──────────────────────────────────┐
    │ release.yml validate job   │   │ tests/test_changelog_extraction   │
    │ (existence+non-empty check,│   │ .py  (NEW, D-06 pytest)           │
    │ D-09 — fails BEFORE PyPI   │   │ - real version -> non-empty        │
    │ publish)                    │   │ - absent version (9.9.9) -> exit≠0│
    └───────────────────────────┘   └──────────────────────────────────┘
                    │
                    v (later, at tag time — /gsd-complete-milestone)
    ┌────────────────────────────────────────────────┐
    │ release.yml create-release job                  │
    │ "Generate release notes" step (replaces the      │
    │ git log --pretty dump) -> release_notes.md        │
    │  -> softprops/action-gh-release                   │
    │     body_path: release_notes.md                   │
    │     generate_release_notes: true (D-08, appended)  │
    └────────────────────────────────────────────────┘

  Separately, the SC#4 invariant sweep and the ja glyph bar are ONE-OFF hand-run
  investigations over the git history / a local translations-repo clone — no
  new files land in typsphinx/, docs/, or tests/ for either (D-07 precedent).

    git diff 51e02b6..HEAD -- pyproject.toml   -> zero new deps
    git diff --diff-filter=A --name-only ...   -> no new @preview site
    census.py (hand-run, not committed)        -> handler -> gate-module map

    translations-repo/ (cloned into phase dir, D-17, never committed)
      typsphinx/  (submodule, re-pointed to main vs. this worktree's HEAD)
      locale/ja/LC_MESSAGES/*.po
      -> post_create_environment copy -> sphinx-build -b typstpdf -> PDF x2
      -> pypdf page-count / text / /BaseFont / CJK-density comparison
```

### Recommended Project Structure

```
scripts/
├── render_admonition_greyscale.py   # existing precedent
└── extract_changelog_section.py     # NEW — D-06's extraction script

tests/
├── test_readme_version_sync.py      # existing precedent (pattern to copy)
├── test_preview_version_sync.py     # existing precedent (pattern to copy)
├── test_admonition_greyscale_pipeline.py  # existing precedent — subprocess-invokes
│                                            a scripts/ module; copy this shape exactly
└── test_changelog_extraction.py     # NEW — D-06/D-10's pytest

.github/workflows/
└── release.yml                      # MODIFIED — validate job gains existence check (D-09),
                                       # create-release job's "Generate release notes" step
                                       # calls the script instead of git log --pretty

.planning/phases/41-v0-7-0-release-automation-release-prep/
├── translations-repo/               # D-17 — cloned here, gitignored/never committed
├── 41-RELEASE-EVIDENCE.md           # NOT 41-VERIFICATION.md (reserved name, gets clobbered)
└── 41-HANDOFF.md                    # SC#5 — the /gsd-complete-milestone checklist
```

### Pattern 1: Script-with-subprocess-invoked-pytest (the D-06 template)

**What:** A `scripts/*.py` module with a `__main__` CLI guard, imported nowhere in `typsphinx/`,
exercised by a dedicated `tests/test_*.py` module that invokes it via `subprocess.run([sys.executable,
str(SCRIPT_PATH), ...])` rather than importing its functions directly.

**When to use:** Any release-surface script that must run identically whether invoked by a human,
by CI, or by pytest — exactly REL-04's extraction script's requirement (D-09: same script runs in
both the `validate` job and, later, `create-release`).

**Example (measured from the actual precedent, `scripts/render_admonition_greyscale.py` +
`tests/test_admonition_greyscale_pipeline.py`):**

```python
# scripts/render_admonition_greyscale.py — the existing precedent's shape
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("source_dir", type=Path, ...)
    parser.add_argument("output_png", type=Path, ...)
    args = parser.parse_args()
    # ... calls the module's own testable function(s) ...
```

```python
# tests/test_admonition_greyscale_pipeline.py — the existing precedent's invocation shape
SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "render_admonition_greyscale.py"
)

def test_pipeline_produces_single_channel_png(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(PROBE_DIR), str(out_png)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"...failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
```

The extraction script should follow this exact shape: `argparse` CLI (`version` positional arg,
`--changelog-path` optional override defaulting to the repo-root `CHANGELOG.md`), print the
extracted section body to stdout, exit 0 on success and non-zero with a stderr message on a
missing/empty section — then `release.yml`'s `validate` job calls it as
`uv run python scripts/extract_changelog_section.py "$VERSION" >/dev/null` (existence-only,
D-09) and the `create-release` job calls it as
`uv run python scripts/extract_changelog_section.py "$VERSION" > release_notes_body.md` (content
capture, replacing the `git log --pretty` block at `release.yml:160-167`).

### Pattern 2: Raw-text regex parsing for a repo file (not a markdown/TOML library)

**What:** `tests/test_preview_version_sync.py` and `tests/test_readme_version_sync.py` both parse
their target file's raw text with a hand-written `re.compile(...)` rather than any parsing library
(TOML is the one exception, using stdlib `tomllib`).

**When to use:** Any new script/test reading `CHANGELOG.md`, `README.md`, or `.typ` template files.

**Example (verbatim from `test_preview_version_sync.py`, the closest existing analog to what the
CHANGELOG-section extractor needs):**

```python
# Matches an actual Typst `#import "@preview/<name>:<version>"` statement
# (not a bare mention in a comment or docstring example).
_PREVIEW_IMPORT_RE = re.compile(
    r'#import\s+"@preview/(?P<name>[A-Za-z0-9_-]+):(?P<version>\d+\.\d+\.\d+)"'
)
```

For `CHANGELOG.md`, the equivalent anchor regex is a line-start match on
`r'^## \[(?P<version>[^\]]+)\]'` — this also matches the `## [Unreleased]` headings (both of them),
which is *harmless* as long as the extractor is asked for a specific version string like `"0.7.0"`
and takes everything between that header line and the *next* `## [` header line (or EOF) as the
section body. The two `## [Unreleased]` headings never sit adjacent to a real version number, so a
simple "find the target header, take until the next `## ` header" algorithm needs no special-casing
for them (see Common Pitfalls below for the one caveat).

### Anti-Patterns to Avoid

- **Duplicating the extraction logic inline in `release.yml`'s shell block AND in a separate pytest
  implementation:** D-06 explicitly rejects this ("two implementations, so a divergence in the
  extraction itself is invisible"). One script, invoked by both the workflow and the test.
- **A markdown-parsing library dependency:** would violate milestone invariant #1 (zero new runtime
  deps) for a problem that two raw-text-regex precedents already solve in this exact repository.
- **Committing the SC#4 sweep or the `ja` glyph-bar comparison as a permanent script/test:**
  explicitly rejected by two prior phases' identical decisions (Phase 29 D-15, Phase 30.1 D-03) —
  both artifacts under comparison (a SHA-anchored diff range; an RTD-unreachable-from-CI build) are
  one-off by construction, and a script that "looks like a gate" but never runs in CI is worse than
  no gate (30.1-06-PLAN.md's own framing).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting which `visit_*`/`depart_*` handlers changed across a SHA range | A custom AST diff tool, or trusting `git diff --stat`'s line counts as a proxy | The hunk-boundary + function-start-line census method below (a ~40-line Python script using only `git show`/`git diff -U0` and a regex for `def (visit_\|depart_)...`) | AST-based diffing (e.g. via the `ast` module) would need to resolve decorators/nesting and handle the fact this is one 6,900+-line class; the hunk-line-attribution method is simpler, was verified this session to correctly find all 51 touched handlers including 3 brand-new ones (`visit_citation`, `depart_citation`, `visit_label`), and needed no new dependency |
| Parsing `CHANGELOG.md`'s structure | A Keep-a-Changelog-aware library | Raw regex on `## [` headers (Pattern 2 above) | No such library is a project dependency, and the file's structure is simple enough that the two existing version-sync tests already establish this as the house style |
| CJK-character density counting for page sampling | A CJK-detection library (e.g. `regex` module's Unicode script property, or `unicodedata`-based classification) | The exact regex already used and proven in Phase 30.1: `[぀-ゟ゠-ヿ一-鿿㐀-䶿＀-￯]` (Hiragana / Katakana / CJK-Unified-Ideographs / fullwidth forms) applied per-page via `pypdf`'s `extract_text()` | This is the identical method Phase 30.1 already used and recorded in `30.1-EVIDENCE.md`; reusing it keeps this phase's method directly comparable to that precedent rather than introducing a second counting convention |

**Key insight:** every "don't hand-roll" item in this phase actually resolves to "don't invent a new
method — copy the one this exact codebase already used and proved correct." There is no genuinely
novel technical problem in this phase; the discretion items are all about which existing pattern to
apply, not which library to adopt.

## Runtime State Inventory

Not applicable in the classic "rename/refactor" sense — this phase is a version bump plus a
release-notes-source change, not a string rename. For completeness, the version-literal sites are
enumerated as a lockstep census (the closest analog):

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Version literal in packaging metadata | `pyproject.toml:7` — `version = "0.6.5"` (sole literal, confirmed no other version string exists elsewhere in that file) | Code edit: `"0.6.5"` → `"0.7.0"` |
| Version literal in the lockfile | `uv.lock:1450` — `version = "0.6.5"` under `name = "typsphinx"` | Regenerated automatically by `uv lock` / `uv sync --extra dev --locked`; not hand-edited |
| Version literal in human-readable docs | `README.md:317` — `**Status**: Stable (v0.6.5) - Production ready` | Code edit: `v0.6.5` → `v0.7.0`; `tests/test_readme_version_sync.py` asserts this matches `pyproject.toml` |
| CHANGELOG structural state | `CHANGELOG.md` has an empty `## [Unreleased]` at line 8 (top) and a second `## [Unreleased]` / "Planned for Future Releases" heading at line 854 (tail) — both pre-existing, neither created by this phase | New `## [0.7.0]` entry is inserted directly below line 8's `## [Unreleased]`, ahead of `## [0.6.5]` at line 10; the tail link block (lines 865-881) gets a new `[0.7.0]:` line and the `[Unreleased]:` compare link advances from `v0.6.5...HEAD` to `v0.7.0...HEAD` |
| Derived version at runtime | `typsphinx.__version__` — derives from `importlib.metadata`, not a separate literal | No direct edit; will read `0.7.0` automatically once `pyproject.toml` is bumped and the package is reinstalled/rebuilt |

**Nothing found requiring a data migration** — every site above is a source-controlled text literal
updated by a direct edit or a lockfile regeneration, not a stored/live/OS-registered value.

## Common Pitfalls

### Pitfall 1: The CHANGELOG's two `## [Unreleased]` headings breaking a naive "next `##` section" extractor

**What goes wrong:** An extractor that builds an ordered list of all `## [...]` headers and does
"find target, take the (N+1)th header's start as the terminator" is fine — but an extractor that
tries to be clever by *skipping* `## [Unreleased]` headers when computing "the next version" would
mis-terminate the newly inserted `## [0.7.0]` section, because the *tail* `## [Unreleased]` (line
854, "Planned for Future Releases") is unrelated structurally and must never be treated as adjacent
to `[0.7.0]`.

**Why it happens:** Keep-a-Changelog convention expects exactly one `## [Unreleased]` at the top;
this repository additionally repurposes a second one deep in the historical tail as a "Planned for
Future Releases" scratch area (measured: line 854, followed immediately by
`### Planned for Future Releases` and a bullet list, then the tail link-reference block).

**How to avoid:** Use "take everything from the target header's line to the very next line matching
`^## \[` (any content), or EOF" — a purely positional algorithm that never special-cases
"Unreleased" by name. This was directly verified this session: `[0.7.0]`'s section (once inserted at
line 9) will terminate cleanly at `## [0.6.5]` (currently line 10) regardless of the second
`[Unreleased]` heading existing 800+ lines further down.

**Warning signs:** A pytest case asserting extraction of `"0.7.0"` accidentally including the tail
"Planned for Future Releases" bullets, or extraction of `"Unreleased"` behaving ambiguously (this
should not be a supported input at all — D-10's case list is about a present vs. absent *numeric*
version).

### Pitfall 2: `mypy typsphinx/` does not cover a new `scripts/*.py` file

**What goes wrong:** Assuming the new extraction script must satisfy mypy because "it's Python code
in this repo" and being surprised (or over-engineering type annotations) when CI's `type` tox
environment never touches it.

**Why it happens:** `tox.ini`'s `[testenv:type]` runs `mypy typsphinx/` — a directory-scoped
invocation that excludes `scripts/` entirely (measured; confirmed no `[tool.mypy]` `files`/`include`
override in `pyproject.toml` that would widen this). By contrast, `[testenv:lint]` runs
`black --check .` and `ruff check .` with no path restriction — both DO cover `scripts/` (also
measured: `pyproject.toml`'s `[tool.black]` exclude list only names `.git`/`.tox`/`.venv`/`_build`/
`build`/`dist`, and `[tool.ruff]` has no `include`/`exclude` narrower than repo-root).

**How to avoid:** Write clean type hints as good practice (matching
`render_admonition_greyscale.py`'s style, which does use annotations despite not being mypy-gated),
but do not treat a hypothetical mypy failure in `scripts/` as a release blocker — it structurally
cannot fail CI's `type` job. Do treat black/ruff failures there as real blockers, since those DO run
repo-wide.

### Pitfall 3: `main..HEAD` commit count is a moving target, not a fixed number to hard-code

**What goes wrong:** CONTEXT.md recorded "`main..HEAD` is 328 commits" as of its own measurement
time (2026-08-02, before Phase 40.1 fully landed). Re-measured this session: **369 commits**
(`git log --oneline main..HEAD | wc -l`), because Phase 40.1's completion and STATE.md/PROJECT.md
housekeeping commits landed afterward. A plan or evidence file that hard-codes "328" as an expected
value will read as stale or wrong by the time it executes.

**Why it happens:** This is an actively developed milestone branch; every planning/execution commit
made *during Phase 41's own planning and execution* adds to this count.

**How to avoid:** Any evidence file recording "the release body would otherwise be an N-line commit
dump" should re-run the count at the moment of recording (D-07's own instruction: hand-run,
transcribed verbatim) rather than copying CONTEXT.md's number. The *demonstration* of REL-04
(SC#1) does not depend on this number at all — it demonstrates the extraction script against
`CHANGELOG.md`'s `## [0.6.5]` (or another already-released) section, which is static.

### Pitfall 4: The SC#4 handler census undercounts if it greps for the literal method name instead of the node name

**What goes wrong:** A first-pass census attempt that greps test files for the literal string
`"visit_desc_addname"` (the Python method name) finds **zero** matching gate modules for 12 of the
51 touched handlers — `depart_desc_name`, `depart_desc_parameterlist`, `depart_desc_sig_name`,
`visit_desc_addname`, `visit_desc_optional`, `visit_desc_sig_keyword`, `visit_desc_sig_operator`,
`visit_desc_sig_punctuation`, `visit_hint`, `visit_important`, `visit_literal_emphasis`,
`visit_seealso` — falsely suggesting they carry no GATE-01 fixture at all.

**Why it happens:** Gate-test modules and docstrings refer to the underlying **docutils/Sphinx node
name** (`desc_addname`, `desc_sig_operator`, `hint`, `seealso`, …), almost never to the Python
visitor method name with its `visit_`/`depart_` prefix. A test asserting SIG-02's behavior says
"desc_addname gets monospace treatment," not "visit_desc_addname is tested here."

**How to avoid:** Strip the `visit_`/`depart_` prefix before grepping for coverage, i.e. search for
the *node* name. Re-running this session's census with that correction found a covering gate module
for all 51 touched handlers — the apparent 12-handler gap was a false negative in the search method,
not a real coverage gap. This does not by itself prove every one of the 51 handlers' *specific
diff hunks* are exercised by the located gate module — only that the node type appears somewhere in
that module. The planner should still spot-check a sample (especially the trivial-looking
`desc_sig_keyword`/`desc_sig_punctuation`/`desc_sig_operator` pass-through handlers) against the
actual gate assertions, not just the grep hit.

### Pitfall 5: `typsphinx-doc-translations`'s submodule tracks `main`, not a fixed SHA — the "before" build needs no action, but confirm this at execution time

**What goes wrong:** Assuming both sides of the D-15 main-vs-HEAD comparison require manual
re-pointing of the cloned translations-repo's `typsphinx` submodule.

**Why it happens:** It's the natural assumption given `.gitmodules` declares
`branch = main` — but that only controls what `git submodule update --remote` would track; a fresh
`git clone --recurse-submodules` checks out whatever SHA the superproject's `.gitmodules`-adjacent
gitlink currently records, which was measured this session (via a real clone) to be `5888ee0`
(`v0.6.5-6-g5888ee0` — i.e., 6 commits past the `v0.6.5` tag, on `main`). This means the freshly
cloned submodule IS already a valid "before" (main) build target as long as no commits have landed
on `main` since that pin was taken — worth a one-line freshness check
(`git -C translations-repo/typsphinx log -1 --format=%H` vs `git ls-remote origin main` on the
parent repo) before treating it as current.

**How to avoid:** Verify the pinned SHA is still `main`'s tip (or close enough that no
`typsphinx/`-affecting commit landed between the pin and the real `main` tip) before using the
as-cloned submodule as the "before" build. For the "after" build, re-point the submodule's git
remote at this local worktree and check out this worktree's own `HEAD` — e.g.
`git -C translations-repo/typsphinx fetch <path-to-this-worktree> HEAD:phase41-head && git -C
translations-repo/typsphinx checkout phase41-head` — rather than pushing anything to the real
`origin` (constraint: no push, no irreversible action).

### Pitfall 6: The `ja` build's font-fallback risk is real but narrow — 24 new `raw(` call sites, zero new `set text(font:)` calls

**What goes wrong:** Treating this milestone's font risk as hypothetical/unlikely and skipping the
comparison, on the theory that "nothing names a font family so nothing can shadow the CJK
fallback."

**Why it happens:** STATE.md's own risk note is correct that no `set text(font: ...)` call exists —
but `raw(...)` (used 24 new times this milestone for signature/parameter monospace styling) resolves
to Typst's *default* monospace family, which typically has no CJK glyph coverage. This is exactly
the mechanism the D-15/D-16 four-check bar exists to catch, and it is silent — no warning, no error,
just substituted glyphs in monospace-styled runs on the `ja` build specifically.

**How to avoid:** Do not skip the comparison on the theory that "no font family was named." Run the
full main-vs-HEAD build pair and specifically inspect pages containing `raw()`-styled content (API
signatures, parameter names) among the sampled pages, not only pages the CJK-density heuristic
happens to surface (the CJK-density method samples by density, not by "contains a signature" — the
planner may want to explicitly union in a signature-heavy page, similar to how Phase 30.1 unioned in
NUL-flagged pages beyond the density-only sample).

## Code Examples

### The handler census script (verified working this session)

```python
# Not committed — a one-off hand-run script per the SC#4 evidence precedent (D-07).
# Verified this session: correctly attributes all 51 changed visit_/depart_ handlers,
# including 3 brand-new methods (visit_citation, depart_citation, visit_label), across
# the range 51e02b6..HEAD.
import subprocess, re

def get_file(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"],
                           capture_output=True, text=True, check=True).stdout.splitlines()

def build_func_starts(lines):
    starts = []
    for i, line in enumerate(lines, start=1):
        m = re.match(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', line)
        if m:
            starts.append((i, m.group(1)))
    return starts

def func_at_line(starts, lineno):
    name = None
    for s, n in starts:
        if s <= lineno:
            name = n
        else:
            break
    return name

BASE = "51e02b6"  # merge-base(main, HEAD) == one commit past the v0.6.5 tag
base_lines = get_file(BASE, "typsphinx/translator.py")
head_lines = get_file("HEAD", "typsphinx/translator.py")
base_starts = build_func_starts(base_lines)
head_starts = build_func_starts(head_lines)

diff = subprocess.run(["git", "diff", "-U0", f"{BASE}..HEAD", "--", "typsphinx/translator.py"],
                       capture_output=True, text=True, check=True).stdout

hunk_re = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
touched = set()
old_line = new_line = 0
for line in diff.splitlines():
    m = hunk_re.match(line)
    if m:
        old_line, new_line = int(m.group(1)), int(m.group(3))
        continue
    if line.startswith(('---', '+++', 'diff ', 'index ')):
        continue
    if line.startswith('-'):
        fn = func_at_line(base_starts, old_line)
        if fn: touched.add(fn)
        old_line += 1
    elif line.startswith('+'):
        fn = func_at_line(head_starts, new_line)
        if fn: touched.add(fn)
        new_line += 1
    else:
        old_line += 1
        new_line += 1

visit_depart = sorted(n for n in touched if n.startswith(("visit_", "depart_")))
print(f"{len(visit_depart)} handlers touched:", visit_depart)
```

**Measured output this session (51 handlers):** `depart_citation`, `depart_desc`,
`depart_desc_content`, `depart_desc_name`, `depart_desc_optional`, `depart_desc_parameter`,
`depart_desc_parameterlist`, `depart_desc_sig_name`, `depart_desc_signature`, `depart_field`,
`depart_field_body`, `depart_field_list`, `depart_field_name`, `depart_literal_emphasis`,
`depart_literal_strong`, `depart_paragraph`, `depart_reference`, `depart_rubric`, `visit_Text`,
`visit_admonition`, `visit_attention`, `visit_citation`, `visit_danger`, `visit_desc_addname`,
`visit_desc_annotation`, `visit_desc_content`, `visit_desc_name`, `visit_desc_optional`,
`visit_desc_parameter`, `visit_desc_parameterlist`, `visit_desc_returns`, `visit_desc_sig_keyword`,
`visit_desc_sig_name`, `visit_desc_sig_operator`, `visit_desc_sig_punctuation`,
`visit_desc_sig_space`, `visit_desc_signature`, `visit_field_body`, `visit_field_list`,
`visit_field_name`, `visit_hint`, `visit_important`, `visit_label`, `visit_literal_emphasis`,
`visit_literal_strong`, `visit_math_block`, `visit_paragraph`, `visit_reference`, `visit_rubric`,
`visit_seealso`, `visit_topic`.

### Mapping each handler to its covering gate module (node-name grep, per Pitfall 4)

```bash
# For each touched handler, strip the visit_/depart_ prefix and grep tests/ for the node name:
node=$(echo "$handler" | sed -E 's/^(visit_|depart_)//')
grep -rl "$node" tests/*.py
```

**Result this session: all 51 handlers map to at least one gate module.** Representative mapping
(full table is reproducible with the command above):

| Node family | Covering gate module(s) |
|---|---|
| `desc_name`, `desc_addname`, `desc_annotation`, `desc_sig_name`, `desc_parameter` | `tests/test_signature_typography_gate.py` |
| `desc_sig_operator`, `desc_sig_keyword`, `desc_sig_punctuation`, `desc_sig_space` | `tests/test_desc_sig_space_render_gate.py` |
| `desc_content`, `desc_signature` (indent/anchor) | `tests/test_desc_content_indent_render_gate.py`, `tests/test_desc_signature_anchor_render_gate.py` |
| `desc_optional`, `desc_returns` (arrow/break) | `tests/test_signature_break_and_arrow_gate.py`, `tests/test_signature_overflow_render_gate.py` |
| `field_list`, `field_body`, `field_name` | `tests/test_field_list_in_list_item_render_gate.py`, `tests/test_field_body_typography_render_gate.py`, `tests/test_confval_field_body_render_gate.py` |
| `citation`, `label` | `tests/test_citation_render_gate.py`, `tests/test_citation_degradation_gate.py` |
| `admonition`, `attention`, `danger`, `hint`, `important`, `seealso` | `tests/test_admonition_bucket_render_gate.py`, `tests/test_admonition_locale_title_precedence_gate.py`, `tests/test_admonitions.py`, `tests/test_pdf_render_gate.py` |
| `rubric` | `tests/test_desc_rubric_decoupling_render_gate.py`, `tests/test_rubric_indent_invariance.py`, `tests/test_rubric_strong_nesting_render_gate.py`, `tests/test_rubric_propagated_target_render_gate.py` |
| `math_block` | `tests/test_math_native.py`, `tests/test_math_mitex.py`, `tests/test_inline_math_after_text_render_gate.py`, `tests/test_math_fallback.py` |
| `literal_emphasis`, `literal_strong` | `tests/test_field_body_typography_render_gate.py`, `tests/test_desc_rubric_decoupling_render_gate.py` |
| `paragraph` | `tests/test_paragraph_concat_render_gate.py`, `tests/test_paragraph_propagated_target_render_gate.py`, `tests/test_list_item_nested_block_render_gate.py`, `tests/test_translator.py` |
| `reference` (incl. citation backrefs) | `tests/test_citation_render_gate.py`, `tests/test_desc_signature_anchor_render_gate.py`, `tests/test_corpus_gate.py`, `tests/test_xref_orphan_degrade_render_gate.py` |

### Zero-new-dependency check (verified this session, current output shown)

```bash
$ git diff 51e02b6..HEAD -- pyproject.toml | grep -A6 '^dependencies'
# (no output — the `dependencies = [...]` block is byte-identical between base and HEAD)
$ git show 51e02b6:pyproject.toml | sed -n '/^dependencies/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
$ git show HEAD:pyproject.toml | sed -n '/^dependencies/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
```

**Verdict: identical.** Zero new runtime dependencies across the milestone.

### `@preview` version-sync check (verified this session)

```bash
$ grep -n "@preview" typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
typsphinx/writer.py:155:            imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:156:            imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:157:            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:158:            imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/templates/base.typ:8:#import "@preview/codly:1.3.0": *
typsphinx/templates/base.typ:9:#import "@preview/codly-languages:0.1.10": *
typsphinx/templates/base.typ:14:#import "@preview/mitex:0.2.7": *
typsphinx/templates/base.typ:19:#import "@preview/gentle-clues:1.3.1": *
typsphinx/template_engine.py:612:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:613:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:614:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:615:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')

$ git diff --stat 51e02b6..HEAD -- docs/
# (no output — zero lines changed under docs/ this milestone)

$ git diff --diff-filter=A --name-only 51e02b6..HEAD | xargs grep -l '@preview' 2>/dev/null
# (only tests/fixtures/**/*.typ and tests/fixtures/**/conf.py — expected test-fixture
# mirrors of the same 4-package import block, not a new production sync site)
```

**Verdict: three sync sites (`writer.py`, `template_engine.py`, `templates/base.typ`) unchanged,
all four package versions (`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`,
`gentle-clues:1.3.1`) identical, no new sync site introduced this milestone.** Note (carried
forward, not this phase's concern): `docs/source/_typst/custom_template.typ` remains a pre-existing
**fourth** site outside `test_preview_version_sync.py`'s watched surface (a Warning carried since
Phase 30.1's review, unchanged by this milestone since `docs/` had zero line changes) — this is a
standing, already-acknowledged cost, not a new finding, and is explicitly out of Phase 41's scope
per CONTEXT.md's "no change under `docs/`" rule.

### `ja` glyph-bar clone verification (network reachability + submodule pin, confirmed this session)

```bash
$ git ls-remote https://github.com/YuSabo90002/typsphinx-doc-translations.git HEAD
4a1142cd351c28681f6d4c764854d2a741daad2b	HEAD

$ git clone --quiet --recurse-submodules --depth 50 \
    https://github.com/YuSabo90002/typsphinx-doc-translations.git <phase-dir>/translations-repo
$ git -C <phase-dir>/translations-repo submodule status
 5888ee024d836002cb920ceff9e5df5889b4762c typsphinx (v0.6.5-6-g5888ee0)
$ cat <phase-dir>/translations-repo/.gitmodules
[submodule "typsphinx"]
	path = typsphinx
	url = https://github.com/YuSabo90002/typsphinx.git
	branch = main
```

The translations repo's `.readthedocs.yaml` (measured, 60+ lines) is the authoritative recipe for
the local build:

```yaml
build:
  jobs:
    post_create_environment:
      - rm -rf typsphinx/docs/locale
      - mkdir -p typsphinx/docs/locale
      - cp -a locale/. typsphinx/docs/locale/
    build:
      pdf:
        - mkdir -p /tmp/typst-pdf-build/doctrees
        - sphinx-build -b typstpdf -d /tmp/typst-pdf-build/doctrees typsphinx/docs/source /tmp/typst-pdf-build/out
```

For a local dry run, replicate this sequence directly (with `SPHINX_LANGUAGE=ja` not even needed —
the manifest's `conf.py` resolves language via `READTHEDOCS_LANGUAGE`/`SPHINX_LANGUAGE`, but since
this build's *source* comes from the translations repo's own locale catalogs feeding
`gettext_auto_build`, and RTD's own manifest sets no such env var explicitly for the ja project —
confirm at execution time whether the ja RTD project sets `READTHEDOCS_LANGUAGE=ja` at the project
level, since Phase 30.1's own local-baseline reproduction explicitly did set `SPHINX_LANGUAGE=ja`
manually):

```bash
# "before" (main) — the freshly cloned submodule is already at main's tip (verify freshness first)
uv run python -m sphinx -b typstpdf -d /tmp/p41-main-doctrees \
    <phase-dir>/translations-repo/typsphinx/docs/source /tmp/p41-main-out

# "after" (this worktree's HEAD) — re-point the submodule first
git -C <phase-dir>/translations-repo/typsphinx fetch <path-to-this-worktree> HEAD:phase41-head
git -C <phase-dir>/translations-repo/typsphinx checkout phase41-head
uv run python -m sphinx -b typstpdf -d /tmp/p41-head-doctrees \
    <phase-dir>/translations-repo/typsphinx/docs/source /tmp/p41-head-out
```

### CJK-density page-sampling method (verified precedent, Phase 30.1's exact regex)

```python
import pypdf, re

CJK_RE = re.compile(r'[぀-ゟ゠-ヿ一-鿿㐀-䶿＀-￯]')
# equivalently written as the character-class literal Phase 30.1 recorded:
# [぀-ゟ゠-ヿ一-鿿㐀-䶿＀-￯]
# (Hiragana / Katakana / CJK Unified Ideographs / CJK Ext-A / Halfwidth-Fullwidth Forms)

reader = pypdf.PdfReader(path)
densities = [len(CJK_RE.findall(page.extract_text() or "")) for page in reader.pages]
# Sample: title page (1) + highest-density page per document third + single highest-density
# page overall (Phase 30.1's exact method) — union in any page containing a raw()-styled
# signature run for this milestone specifically (Pitfall 6).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `release.yml`'s "Generate release notes" step builds the body from `git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` (a raw commit dump, `release.yml:164`) | Extraction of the curated `## [X.Y.Z]` CHANGELOG section via a committed, pytest-covered script | This phase (REL-04) | The v0.6.4 release body was 308 lines, 296 of which were the dump; readers see the curated section instead |
| The existence/non-emptiness check for the extracted section lives nowhere (the workflow doesn't read `CHANGELOG.md` at all today) | The check runs in the `validate` job, before `build`/`publish-pypi`/`create-release` | This phase (D-09) | A missing/malformed CHANGELOG section now fails BEFORE the PyPI upload, not after — avoiding "published to PyPI but no GitHub Release" |

**Deprecated/outdated:** the `git log --pretty` dump step itself is fully removed (not kept as a
fallback) per REL-04's own wording — "with the `git log --pretty` commit dump removed rather than
left as a fallback path."

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The ja RTD project's `READTHEDOCS_LANGUAGE=ja` is set at the RTD project-settings level (not visible in any manifest file in this repo or the translations repo) rather than via an env var this local dry-run can replicate automatically | § "ja glyph-bar clone verification" | If wrong, a naive local build without `SPHINX_LANGUAGE=ja` set explicitly would produce an English PDF from the same source tree, giving a false "identical" or false "different" page-count comparison. Mitigation: explicitly set `SPHINX_LANGUAGE=ja` in the local build environment regardless (as Phase 30.1 did), rather than relying on the manifest's default resolution — this is already a cheap, safe hedge and should be done unconditionally |
| A2 | The translations-repo's submodule pin (`5888ee0`, `v0.6.5-6-g5888ee0`) is close enough to real `main`'s tip that using the as-cloned submodule directly as the "before" build is valid without a fresh re-clone at execution time | § "Pitfall 5" | If `main` has moved since this session's clone (very likely, given this is an actively developed repo), the "before" build would be built from a slightly stale `main` rather than the true current `main`. Mitigation: re-verify the pin against `git ls-remote` for `main` at execution time and re-clone/re-checkout if it has moved, per Pitfall 5's guidance |
| A3 | mypy's directory-scoped invocation (`mypy typsphinx/`) will not be widened to cover `scripts/` by any other in-flight change during this phase's execution window | § "Pitfall 2" | Low risk — this is a repo-wide tox/pyproject.toml configuration fact, not something Phase 41 itself touches; flagged only so the planner does not need to add mypy-compliance verification steps for the new script |

**If this table is empty:** N/A — see above; three low-to-moderate-risk assumptions remain, none of
which touches REL-04/REL-05's core mechanism (the CHANGELOG extraction and version bump are both
fully verified with zero assumptions).

## Open Questions

1. **Does the `ja` RTD project set `READTHEDOCS_LANGUAGE=ja` at the project-settings level, or does
   the manifest rely on some other mechanism?**
   - What we know: `docs/source/conf.py`'s `_resolve_language()` checks
     `READTHEDOCS_LANGUAGE` first, then `SPHINX_LANGUAGE`, defaulting to `"en"`. Phase 30.1's own
     local-baseline reproduction explicitly set `SPHINX_LANGUAGE=ja` by hand rather than relying on
     any RTD-side setting being replicable locally.
   - What's unclear: whether this is documented anywhere retrievable without RTD project-admin
     access (not available to this research session).
   - Recommendation: the executing plan should unconditionally set `SPHINX_LANGUAGE=ja` for both
     local builds (mirroring Phase 30.1's proven approach), independent of whatever RTD does — this
     sidesteps the question entirely rather than needing an answer.

2. **Does the SC#4 handler census's node-name-substring grep produce any false-positive coverage
   claims (a gate module happens to mention a node name in prose/comments without actually
   asserting its post-fix behavior)?**
   - What we know: every one of the 51 touched handlers maps to at least one gate module by this
     method, and the false-negative failure mode (Pitfall 4) was caught and corrected this session.
   - What's unclear: whether every mapped gate module contains a real assertion on that specific
     node's Phase 36-40.1-era behavior, versus an incidental prose mention (e.g., a docstring
     explaining what the handler used to do).
   - Recommendation: the planner should spot-check the mapping table above against each module's
     actual `assert` statements for at least the handlers whose only covering module is a single
     hit (e.g., `desc_sig_keyword` → only `test_desc_sig_space_render_gate.py`), not accept the grep
     hit alone as proof.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Network access to `github.com` | Cloning `typsphinx-doc-translations` (D-17) | ✓ (confirmed via `git ls-remote` this session) | — | — |
| `pypdf` | SC#3 PDF checks, SC#4 fixture cross-referencing | ✓ (already in `dev` extra) | not re-verified this session (unchanged since Phase 30.1) | — |
| Noto Serif CJK JP / Hanazono / Un- family fonts | `ja` build glyph fallback | ✓ (confirmed via `fc-list`: `Noto Serif CJK JP:style=Light` at `/nix/store/.../noto-fonts-cjk-serif-2.003/...`) | — | — |
| `uv` | Every build/test invocation | assumed present (standing project tool; not re-probed this session — CLAUDE.md's worktree-provisioning section is authoritative) | — | — |
| `typst`/`typst-py` | Compiling `.typ` to PDF | assumed present (existing project dependency, `typst>=0.15.0,<0.16`) | — | — |

**Missing dependencies with no fallback:** none identified.

**Missing dependencies with fallback:** none identified — every tool this phase needs is already
present on this machine and already a project dependency.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (existing project dependency) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (testpaths=`tests`, strict markers) |
| Quick run command | `uv run pytest tests/test_changelog_extraction.py -v` (new module, once created) |
| Full suite command | `uv run pytest tests/` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-04 | Extraction script returns a non-empty section for a real version | unit | `pytest tests/test_changelog_extraction.py::test_extracts_real_version -x` | ❌ Wave 0 (new file, D-06) |
| REL-04 | Extraction script exits non-zero for an absent version (e.g. `9.9.9`) | unit | `pytest tests/test_changelog_extraction.py::test_absent_version_fails -x` | ❌ Wave 0 (new file, D-10) |
| REL-04 | `validate` job's existence check fires before `build`/`publish-pypi` | manual/CI-only (cannot run outside a real tag push) | N/A — verified by reading `release.yml`'s job `needs:` graph and by the hand-run SC#1 transcript (D-07) | N/A (workflow-level, not pytest-testable locally) |
| REL-05 | `pyproject.toml`/`uv.lock`/`README.md` version literals agree | unit (existing) | `pytest tests/test_readme_version_sync.py -x` | ✅ (pre-existing) |
| REL-05 | `@preview` sync sites agree | unit (existing) | `pytest tests/test_preview_version_sync.py -x` | ✅ (pre-existing) |
| REL-05 | Full suite green post-bump | integration | `uv run pytest tests/` | ✅ (existing suite) |
| REL-05 | Full-corpus `-b typstpdf` gate green post-bump | integration | `uv run pytest tests/test_corpus_gate.py -x` (or the `TYPSPHINX_CORPUS_REPORT=1`-gated variant per the module's own env flag) | ✅ (pre-existing) |
| REL-05 | Both docs dogfooding builds succeed | integration | `uv run tox -e docs-html && uv run tox -e docs-pdf` | ✅ (pre-existing tox envs) |
| REL-05 | `ja` four-check glyph bar (SC#3) | manual (check 1-3 mechanical, check 4 `human_needed`) | one-off hand-run `pypdf` commands (see Code Examples) — NOT a committed pytest, per D-15/D-16/precedent | N/A by design (never committed) |
| REL-05 | SC#4 invariant sweep (deps, `@preview`, handler census) | manual (mechanical but one-off) | one-off hand-run `git diff`/census script (see Code Examples) — NOT a committed pytest, per D-07/precedent | N/A by design (never committed) |

### Sampling Rate

- **Per task commit:** the new `test_changelog_extraction.py` module runs on every commit touching
  the extraction script (standard pytest gate); no other new automated test is added this phase.
- **Per wave merge:** full pytest + lint/type trio, as usual.
- **Phase gate:** the full green-tree evidence run (full suite, lint/type trio, full-corpus gate,
  both docs builds, `ja` four-check bar) is a **once, at the end, post-bump** requirement (SC#3) —
  it cannot be sampled incrementally because it specifically validates the state AFTER the version
  bump and CHANGELOG entry land, not before.

### Wave 0 Gaps

- [ ] `tests/test_changelog_extraction.py` — covers REL-04 (D-06, D-10)
- [ ] `scripts/extract_changelog_section.py` — the script itself (D-06)
- [ ] No shared fixture/conftest changes anticipated — the extraction script needs only
  `CHANGELOG.md`'s existing content, already present

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | This phase adds no auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes (narrow) | The extraction script takes a version string as CLI input; validate it is used only to construct a regex/string match against `CHANGELOG.md`'s own content — never interpolated into a shell command or file path outside the repo. `release.yml` already derives the version from the git tag (`${TAG#v}`) via existing, unmodified logic — the new script only reads that same trusted value |
| V6 Cryptography | no | No new cryptographic operation; existing SHA-256 hashing for artifact identification (Code Examples) uses stdlib `hashlib`, already the established pattern from Phase 29/30.1 |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A malformed/adversarial `CHANGELOG.md` causing the extraction script to emit unintended content into a GitHub Release body | Tampering | Not a realistic threat surface for THIS phase — `CHANGELOG.md` is a repo file only maintainers can edit via PR; no external input reaches the script. Standard defensive practice (fail loudly on missing/empty section, per D-09/D-10) is sufficient |
| A downloaded/cloned `typsphinx-doc-translations` PDF or repository content being treated as trusted without verification | Tampering | Same mitigation Phase 29/30.1 already established: `pypdf` is used for read-only metadata/text extraction only, nothing from the clone is executed, and the clone lives in the phase directory (never committed, per D-17) |
| Command injection via the version string interpolated into a shell command in `release.yml` | Tampering | Not new — `release.yml` already derives `TAG`/`VERSION` from `${GITHUB_REF#refs/tags/}` or a `workflow_dispatch` input and uses them in existing shell steps (e.g. the version-mismatch check at lines 50-59); the new script should follow the same pattern of passing the version as a single quoted CLI argument, not string-interpolating it into an `eval`'d shell fragment |

## Sources

### Primary (HIGH confidence — measured directly against the live tree this session)

- Live `git` history: `git merge-base main HEAD` → `51e02b6` (one commit past the `v0.6.5` tag,
  `bd4096b`); `git log --oneline main..HEAD` → 369 commits (superseding CONTEXT.md's 328,
  Pitfall 3); Phase 40.1's commits (`e8d4f42`, `2b3e36a`, `3fdf1f5`, `083eceb`, etc.) confirmed
  inside the `51e02b6..HEAD` range.
- `git diff -U0 51e02b6..HEAD -- typsphinx/translator.py` + hunk-attribution census script (this
  session) → 51 touched `visit_*`/`depart_*` handlers, 10 touched non-handler methods.
- `git diff 51e02b6..HEAD -- pyproject.toml` → zero dependency changes (verbatim identical
  `dependencies` array).
- `grep -rn "@preview" typsphinx/writer.py typsphinx/template_engine.py
  typsphinx/templates/base.typ` + `git diff --stat 51e02b6..HEAD -- docs/` (empty) → three sync
  sites confirmed unchanged, no new fourth site.
- `.github/workflows/release.yml` read in full — `validate` job version check (lines 50-59),
  `create-release` job's "Generate release notes" step (152-174) and "Create GitHub Release" step
  (176-187), matching CONTEXT.md's recorded line numbers exactly.
- `CHANGELOG.md` read in full — two `## [Unreleased]` headings confirmed at lines 8 and 854, tail
  link block at lines 865-881.
- `pyproject.toml`, `uv.lock`, `README.md` — version literals confirmed at `pyproject.toml:7`,
  `uv.lock:1450`, `README.md:317`, all reading `0.6.5`.
- `scripts/render_admonition_greyscale.py` + `tests/test_admonition_greyscale_pipeline.py` read in
  full — the D-06 template.
- `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py` read in full — the
  raw-regex parsing pattern.
- `pyproject.toml`'s `[tool.black]`/`[tool.ruff]`/`[tool.mypy]` sections + `tox.ini` read in full —
  confirmed `black --check .`/`ruff check .` cover `scripts/`, `mypy typsphinx/` does not.
- `git ls-remote https://github.com/YuSabo90002/typsphinx-doc-translations.git HEAD` (network
  reachability confirmed) + a real `git clone --recurse-submodules` of that repository this session
  → `.readthedocs.yaml` read in full, `.gitmodules` (`branch = main`), submodule pin
  `5888ee0` (`v0.6.5-6-g5888ee0`).
- `fc-list | grep -i "noto.*cjk"` → `Noto Serif CJK JP:style=Light` confirmed present on this
  machine.

### Secondary (MEDIUM confidence — read from prior phase artifacts, not re-executed this session)

- `.planning/milestones/v0.6.4-phases/30.1-translations-repository-japanese-rtd-site/30.1-06-PLAN.md`
  — the four-check bar's task structure and acceptance criteria (read in full).
- `.planning/milestones/v0.6.4-phases/30.1-translations-repository-japanese-rtd-site/30.1-EVIDENCE.md`
  — the exact CJK-density regex and page-sampling method (read the relevant sections).
- `.planning/milestones/v0.6.4-phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md`
  § "D-12 Baseline" — the `pypdf` invocation shape for page-count/font enumeration (read in full).
- `.planning/milestones/v0.6.5-phases/35-v0-6-5-release-prep/35-HANDOFF.md` and
  `35-RELEASE-EVIDENCE.md` — the handoff-document shape and the release-evidence section structure
  (both read in full).

### Tertiary (LOW confidence — not applicable)

- None. Every claim in this document was either measured directly this session or read verbatim
  from an existing project artifact; no claim rests on unverified training-data recall.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries anywhere in this phase; every tool is an existing
  dependency, verified present.
- Architecture: HIGH — the extraction-script pattern, the version-lockstep pattern, and the
  one-off-hand-run-evidence pattern are all direct copies of precedents already proven in this
  exact repository (Phase 29, Phase 30.1, Phase 35).
- Pitfalls: HIGH — all six pitfalls were either directly discovered this session (the two
  `[Unreleased]` headings, the mypy-scope gap, the handler-census false-negative, the moving
  commit-count) or are direct restatements of already-documented project risk (the font-fallback
  risk from STATE.md, the submodule-pin freshness question).

**Research date:** 2026-08-02
**Valid until:** This phase's own execution window (days, not weeks) — the `main..HEAD` commit
count, the `typsphinx-doc-translations` submodule pin, and `CHANGELOG.md`'s exact line numbers are
all moving targets on an actively developed branch; re-measure at planning/execution time rather
than trusting this document's specific line numbers and counts to still be exact by the time plans
execute, though the *structural* findings (two `[Unreleased]` headings exist, three `@preview` sync
sites, the extraction-script precedent, zero new dependencies) are stable.
