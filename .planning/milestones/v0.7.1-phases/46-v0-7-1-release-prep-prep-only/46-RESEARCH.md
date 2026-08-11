# Phase 46: v0.7.1 Release Prep (prep-only) - Research

**Researched:** 2026-08-11
**Domain:** Release engineering / prep-only release phase (version bump, CHANGELOG curation, live-run
evidence collection, CI verification, handoff) — no product code changes
**Confidence:** HIGH (nearly every claim below is a direct measurement against the live tree taken
this session, not training recall)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Every measured value below was taken **this session (2026-08-10)** against the live tree, not from
recall. Where a measurement contradicts a prior artifact, the contradiction is stated explicitly
rather than silently corrected.

**Version number and how breakage is framed**

- **D-01: The release ships as `0.7.1`.** `0.7.1` is locked; do not propose `0.8.0`.
- **D-02: Breakage is marked three ways.** (a) lead paragraph states plainly this patch release can
  break a working configuration; (b) each of CONF-10/CONF-11/CONF-12 carries a `**Breaking:**`
  prefix; (c) a `### Removed` section is created — the first in this CHANGELOG's history.
- **D-03: The silent failure of a leftover `typst_authors` is accepted, documentation-only.** No
  `typsphinx/` shim. Zero hits for `typst_authors` across `typsphinx/`, `docs/source/`, `examples/`,
  `tests/`.
- **D-04: The published-notice contradiction is stated in both places, split by kind.** The fact
  (removal despite a prior "future major release" promise) goes in the CHANGELOG `### Removed`
  bullet; the rationale goes in the migration guide.

**The `## [0.7.1]` CHANGELOG entry**

- **D-05: Bullets are cut at user-visible-change granularity — 6 to 8 of them — with requirement IDs
  in trailing parentheses.**
- **D-06: The lead paragraph's axis is "the configuration the documentation promises actually takes
  effect."**
- **D-07: CONF-08's callout names both measured facts** (filename rename AND untemplated→templated
  structure change) — quote `44-GATE-EVIDENCE-03.md` § 7 rather than re-deriving.
- **D-08: `### Verified` carries the same three items as 0.6.5/0.7.0, dependency claim scoped to
  runtime** — "No new **runtime** dependencies" (the `docs` extra gained `myst-parser`, which is not
  a runtime dependency).
- **D-09: `docs/source/changelog.rst` gains a "Migrating from 0.7.0 to 0.7.1" section with
  before/after code fragments** — three items: `typst_authors` → `typst_template_function` `params`
  route; params exclusivity (enumerate all nine); `lang` starts failing without declaring it on a
  custom template.
- **D-10 [derived]: section split is `### Added` / `### Changed` / `### Fixed` / `### Removed` /
  `### Verified`.** Only fixed assignment: `typst_authors` (CONF-10) → `### Removed`.

**SC#3 — what "green" means and where the evidence comes from**

- **D-11: The branch CI run on the post-bump commit is the authority for pytest/lint/type; local
  `tox` supplies what CI does not run.** **Amended (a):** Phase 45.2 discharged the "local tox does
  not run at all" premise. **Amended (b):** local half is per-environment, not the whole
  `env_list` — `.venv/bin/ruff` is a generic-linux ELF NixOS's stub loader rejects (exit 127), so a
  bare `tox` still cannot go green locally; local evidence is `tox -e docs-html`, `tox -e docs-pdf`
  and the full-corpus `-b typstpdf` gate, invoked per-environment.
- **D-12: The `ja` evidence is a single local `SPHINX_LANGUAGE=ja` docs-pdf build**, not Phase 41's
  four-check glyph bar (both triggers re-measured and neither holds this milestone).
- **D-13 [correction of record]: nothing to remove in `typsphinx-doc-translations`**; the `ja` build
  exercises this repository's own files (the `lang` workaround lived only in `docs/source/conf.py`,
  already removed by 45.1).
- **D-14 [SUPERSEDED by D-21]** — kept as a record only; use D-21's anchor.
- **D-15 [derived]: evidence is NOT written to `46-VERIFICATION.md`** — that name is reserved by the
  verifier and will be clobbered (the Phase 41 `41-RELEASE-EVIDENCE.md` precedent).

**Close-out disposition**

- **D-16: Every pending todo is explicitly deferred, each with its reason recorded** — 12 records,
  not 10. `2026-08-11-windows-path-separator-breaks-contract-claims-gate` is **not** deferred (D-22
  resolves it in-phase; filed to `todos/completed/` at close).
- **D-17 [RETRACTED 2026-08-11]** — PR #131 IS merged. See D-28.

**Routed out of this phase**

- **D-18: The `tox-uv` → `tox-uv-bare` repair shipped in Phase 45.2, before Phase 46.** Already
  complete — not this phase's work.
- **D-19: Phase 45.2's change gets no `## [0.7.1]` CHANGELOG bullet** (dev-extra only, not
  user-visible).

**Taking `origin/main` into the release branch**

- **D-20: `origin/main` (`9b2b76b`) is merged into the milestone branch at the head of Phase 46.**
  `git merge-tree --write-tree HEAD origin/main` reports exactly one conflict, `CHANGELOG.md`, in the
  `## [Unreleased]` block. Merging first (not inside the CHANGELOG plan, not by rebase, not deferred
  to `/gsd-complete-milestone`) means the tree SC#3 proves green and the tree that eventually gets
  tagged are the same tree. Reversible — the merge commit can be dropped before anything is tagged.
- **D-21: SC#4's invariant sweep is anchored at the `v0.7.0` tag (commit `75fd8ed`), re-measured on
  the post-merge HEAD.** Supersedes D-14. Pre-merge figures (must be re-taken after D-20's merge):
  `v0.7.0..HEAD` excluding `.planning/` → 126 files / +10,582 / −932.

**The Windows CI lanes**

- **D-22: The Windows CI failure is repaired inside Phase 46, in the test module only.**
  `tests/test_docs_contract_claims_gate.py::TestContractClaimPageEnumerationIsClosed` fails on
  Windows because `_discovered_claim_pages()` at `:170` builds `str(page.relative_to(REPO_ROOT))`,
  which yields backslash paths. Test-module-only edit; does not breach the prep-only fence (Phase 41
  D-12 precedent for a non-`typsphinx/` edit inside a prep phase).
- **D-23: Two CI runs back SC#3 — a check run and an authority run.** Run 1 carries D-20's merge plus
  D-22's Windows repair (confirms Windows lanes go green — cannot be verified locally, no Windows on
  this machine). Run 2 carries the bump and the `## [0.7.1]` entry and **is** SC#3's authority
  per D-11.

**PR #131 in the release notes**

- **D-24: PR #131's `[Unreleased]` entry is compressed to house granularity, not moved verbatim.**
  `origin/main`'s bullet is ~14 lines of prose; house style is 3–5 lines. Keep the user-visible fact
  (image-conversion extension or downloaded image copied no image, aborted the Typst compile), drop
  the internal mechanism. This is the milestone's **sixth** user-visible change.
- **D-25: The bullet credits `@christianwehe` in its trailing parentheses.** No prior
  contributor-attribution precedent in this CHANGELOG; fits the existing identifier-parenthesis
  convention.
- **D-26: PR #131 gets no requirement ID, and `REQUIREMENTS.md` is not touched.** Identify via
  `Issue #130` / `PR #131` only. Coverage stays 19/19 mapped, zero orphans.

**The `_track_image()` defects that arrive with PR #131**

- **D-27: Both `_track_image()` defects ship in v0.7.1 unfixed, disclosed internally only.** No
  `### Known Limitations` CHANGELOG section, no GitHub issue filed. Both stay in `todos/pending/` and
  are named in `46-HANDOFF.md`. Fixing them in Phase 46 was rejected on prep-only-fence consistency
  grounds (same reasoning as D-03).
- **D-28 [correction of record]: PR #131 is merged and ships in v0.7.1; `STATE.md` was right and
  D-17 was wrong.** No correction to `STATE.md` needed. Issue #130 is closed, not carried.

### Claude's Discretion

- The exact wording of the `[0.7.1]` entry, lead paragraph phrasing, which 6–8 bullets D-05 resolves
  to, and how requirement IDs are attached.
- Which requirements land in `### Added` vs. `### Changed` vs. `### Fixed` (D-10 fixes only
  `typst_authors` → `### Removed`).
- The migration section's exact fragments and headings (D-09 fixes only that it exists and its three
  covered items).
- **Plan decomposition and ordering, and the `uv.lock` regeneration procedure** (acceptance:
  `uv sync --extra dev --locked` green).
- **The mechanical method for the invariant sweep** (D-21's anchor).
- **The format and heading structure of `46-HANDOFF.md`.**
- Where live-run evidence is recorded, subject to D-15 (not `46-VERIFICATION.md`).
- Whether `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py:49-63` gains `"0.7.1"` in this
  phase — mechanical, but must not be done before the CHANGELOG entry exists.
- **The exact form of D-22's repair** at `tests/test_docs_contract_claims_gate.py:170` (`.as_posix()`
  is the obvious shape, planner owns it) and whether `EXCLUDED_CLAIM_PAGES` literals move to the same
  normalisation.
- The compressed wording of D-24's PR #131 bullet, and exactly where `@christianwehe` sits.
- Whether the `## [0.7.1]` heading is created before or as part of resolving D-20's CHANGELOG
  conflict.
- Which plan owns the merge, and whether D-22's repair rides in that plan or its own.

**Ordering interaction the planner must resolve:** D-09 adds migration fragments to
`docs/source/changelog.rst` (in `EXCLUDED_CLAIM_PAGES`). CONTEXT.md states that page "currently makes
*no* contract claim under the gate's scan." **This research's direct measurement (below, Pitfall 3)
found the page already satisfies the claim predicate on this Linux machine** — the Windows failure is
a pure path-separator string-mismatch bug, not an absence of claim content. This does not change what
D-22 or D-09 must do; see Pitfall 3 for the full reconciliation and what the planner should verify
post-edit.

### Deferred Ideas (OUT OF SCOPE)

- A fail-loud shim for the removed `typst_authors` (re-register + raise). Declined for v0.7.1 by
  D-03; kept as option of record.
- Unifying the 5 test files that hard-code `["uv", "run", "sphinx-build", …]` onto
  `sys.executable -m sphinx`. A follow-up worth filing, not part of this phase.
- Raising `v0.8.0` instead of `0.7.1`. Declined by D-01.
- The two `TypstBuilder._track_image()` defects (D-27) — deferred to a post-v0.7.1 phase, not
  disclosed externally in v0.7.1.
- A `### Known Limitations` CHANGELOG entry and a public GitHub issue for the above — declined by
  D-27.
- Every pending todo not resolved by this phase (D-16), each with its reason recorded in
  `46-CONTEXT.md`'s `<deferred>` block.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-06 | v0.7.1 is released — `pyproject.toml` bumped as the sole version literal with `uv.lock` and `README.md` in lockstep, a curated `## [0.7.1]` CHANGELOG entry, the post-bump tree proven green live, and the publish executed at `/gsd-complete-milestone`. **This phase discharges everything except the publish.** | Code Examples § "Version-literal bump and editable-install regen" gives the exact `uv lock` → `uv sync --extra dev --locked` sequence and the three files whose version literal must move (`pyproject.toml:7`, `README.md:342`, `uv.lock:1467`). Architecture Patterns § "CHANGELOG entry shape" gives the section-order template and the D-20 merge-conflict resolution mechanics. Validation Architecture maps SC#1–SC#5 to concrete rerunnable commands. |
| REL-04 | The GitHub Release body is the curated `## [X.Y.Z]` CHANGELOG section, proven by a real tag push whose `create-release` job runs to completion. **This phase discharges only the in-phase precondition-verification share; the requirement itself does not close here.** | Code Examples § "REL-04's in-phase share" gives the exact `extract_changelog_section.py` invocation and its documented interface (`scripts/extract_changelog_section.py`). Confirmed via direct read: `release.yml:162-168` already carries the `astral-sh/setup-uv` + `Set up Python` steps ahead of the `uv run python scripts/extract_changelog_section.py` call in `create-release` (`release.yml:190-197`). |

</phase_requirements>

## Summary

Phase 46 is a **prep-only release phase** in the standing v0.5.0-Phase-10 / v0.6.5-Phase-35 /
v0.7.0-Phase-41 pattern: bump the version, curate the CHANGELOG, prove the tree green with *live*
evidence (not inherited from an earlier phase), discharge REL-04's verifiable half, and hand off a
checklist — with **zero irreversible action**. There is no new technology to research here; the
domain is entirely this repository's own established release-engineering machinery
(`scripts/extract_changelog_section.py`, `release.yml`, the three `tests/test_*version_sync.py`-style
guards, `tox.ini`'s env matrix) plus one genuinely new mechanical step this milestone introduces:
merging `origin/main` into the milestone branch before the bump (D-20), because PR #131 landed on
`main` independently of this milestone's phase chain and must ship in v0.7.1 (D-28).

Every command shape in this document was executed against the live tree this session (not
speculated): `uv lock --check` (clean), `tox -e lint` (confirmed dying on `ruff check .` with exit
127 — the exact NixOS ELF failure D-11 amendment (b) predicts), `tox -e docs-html` and
`tox -e docs-pdf` (both green, ~1–3s), `pytest tests/test_corpus_gate.py -v` (4 passed / 1 skipped in
30s, network available), `pytest tests/test_docs_contract_claims_gate.py -v` (8/8 green on this Linux
machine), and `git merge-tree --write-tree HEAD origin/main` (exactly one conflict, `CHANGELOG.md`,
matching D-20's own measurement). One genuinely new finding surfaced beyond what `46-CONTEXT.md`
recorded: `tox -e py312` cannot provision locally on this machine either (uv tries to download a
standalone CPython 3.12 build that is itself a generic-linux ELF NixOS's stub loader rejects) — only
`tox -e py313` (matching this machine's system Python) succeeds locally. This does not weaken D-11
(pytest/lint/type authority is already CI, not local, per amendment (b)) but narrows which tox
environments are even worth attempting locally as a sanity check.

**Primary recommendation:** Sequence the phase as (1) merge `origin/main` + push for the Windows
check-CI run (D-20, D-22, D-23 run 1), (2) version bump + `uv lock`/`uv sync --locked` regen +
CHANGELOG curation + push for the authority CI run (D-23 run 2), (3) local evidence collection
(`tox -e docs-html`, `tox -e docs-pdf`, `pytest tests/test_corpus_gate.py -v`, the `ja` docs-pdf
build), (4) the SC#4 invariant sweep re-measured post-merge, (5) REL-04's precondition checks
(`release.yml` static read + `extract_changelog_section.py` hand-run against `## [0.7.1]`), (6) write
`46-HANDOFF.md` following the `41-HANDOFF.md` shape, (7) confirm `git tag -l v0.7.1` /
`git ls-remote --tags origin v0.7.1` are both empty at close.

## Architectural Responsibility Map

This phase touches no runtime tier — typsphinx has no client/server split; its only "architecture" is
build-time (Sphinx extension) and release-time (CI workflow) tooling. The map below is therefore a
release-engineering tier map, not a client/server one.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-literal sync (`pyproject.toml` / `uv.lock` / `README.md` / editable-install metadata) | Build tooling (`uv`) | Test suite (guard tests) | `uv lock`/`uv sync` own the on-disk lock and `.dist-info`/editable-pth regeneration; `typsphinx.__version__` reads it back via `importlib.metadata` at import time, never re-derived by hand. |
| CHANGELOG curation (`CHANGELOG.md` + `docs/source/changelog.rst`) | Documentation source | Docs build (Sphinx/`myst-parser`) | `CHANGELOG.md` is hand-edited; `docs/source/changelog.rst` mechanically `.. include::`s it, so the release-history propagation is automatic — only the migration-guide tail is hand-maintained. |
| Live-run green-tree proof | CI (GitHub Actions) | Local `tox`/`pytest` | D-11: CI is the authority for pytest/lint/type; local supplies only what CI structurally cannot cover locally-invokable (`docs-html`, `docs-pdf`, the full-corpus gate) — inverted from a typical app where local usually leads. |
| `origin/main` → milestone-branch merge | Git (local working tree) | — | A local merge commit, never pushed as a tag; entirely pre-publish, reversible by dropping the commit. |
| Release-body extraction (REL-04's mechanism) | `scripts/extract_changelog_section.py` | `release.yml`'s `validate`/`create-release` jobs | The extractor is the single source of truth for "what text becomes the release body"; both CI jobs call the same committed script, never a second inline implementation. |
| Publish (tag, PyPI, GitHub Release) | `/gsd-complete-milestone` | — | Explicitly **out of this phase's tier** — the prep/publish fence (D-20's own reversibility note, and the milestone's binding constraint). |

## Standard Stack

### Core

No new libraries are introduced by this phase — it is release engineering over an already-pinned
stack. Confirmed via direct diff (`git diff v0.7.0..HEAD -- pyproject.toml`, this session):
`[project] dependencies` is byte-identical to `v0.7.0`; only the `dev` extra (`tox-uv` →
`tox-uv-bare`, Phase 45.2) and the `docs` extra (`+myst-parser>=5.0`, Phase 45) moved.

| Tool | Verified version (this session) | Purpose | Why standard |
|------|------|---------|--------------|
| `uv` | 0.11.25 (`/nix/store/…-uv-0.11.25/bin/uv`, resolved via PATH — `.venv/bin/uv` no longer exists post-Phase-45.2) | Lockfile, venv provisioning, editable installs | Project's sole package manager (`[VERIFIED: uv --version, this session]`) |
| `tox` | 4.56.1 + `tox-uv-bare` 1.35.2 (registered plugin, `.venv/lib/python3.13/site-packages/tox_uv/plugin.py`) | Task runner / env matrix | `[VERIFIED: tox --version, this session]` |
| `python` | 3.13.13 (this machine's only working interpreter; 3.12 cannot provision locally, see Pitfall 1) | Runtime | `[VERIFIED: .venv/bin/python3 --version, this session]` |
| `sphinx` | 9.1.0 | Doc builder | `[VERIFIED: import sphinx; sphinx.__version__, this session]` |
| `docutils` | 0.22.4 | Doctree | `[VERIFIED: import docutils, this session]` |
| `typst` (typst-py) | 0.15.0 | PDF compile | `[VERIFIED: import typst, this session]` |
| `pytest` | 9.1.1 | Test runner | `[VERIFIED: pytest --version output header, this session]` |
| `pypdf` | 6.14.2 | PDF text extraction in tests | `[VERIFIED: import pypdf, this session]` |
| `gh` | 2.97.0 (nixpkgs) | GitHub CLI — for verifying PR #131 / tag / CI-run state | `[VERIFIED: gh --version, this session]` |
| `git` | 2.54.0 | VCS, merge-tree dry runs | `[VERIFIED: git --version, this session]` |

### Supporting

Not applicable — this phase adds no new tooling. The `docs` extra's `myst-parser` (used to render
`docs/source/changelog.rst`'s `.. include::` of `CHANGELOG.md`) was already added by Phase 45 and is
unchanged here.

### Alternatives Considered

Not applicable — no library selection decisions exist in this phase; every tool is already the
project's locked standard (CLAUDE.md, `pyproject.toml`).

**Installation:** No new install step. The existing `uv sync --extra dev` provisions everything this
phase's plans need (docs-build evidence additionally needs `--extra docs`, or the `tox -e docs-html`
/ `tox -e docs-pdf` envs, which provision their own isolated venvs with `extras = docs` — see
Pitfall 4).

**Version verification:** N/A — no package versions are bumped by this phase; only `typsphinx`'s own
version literal moves (`0.7.0` → `0.7.1`), which is not a registry lookup but a first-party value.

## Package Legitimacy Audit

**No external packages are installed or added by this phase.** Confirmed by direct diff
(`git diff v0.7.0..HEAD -- pyproject.toml`, this session): the only dependency-adjacent lines
changed across the entire milestone are `tox-uv` → `tox-uv-bare` (Phase 45.2, `dev` extra) and
`+myst-parser>=5.0` (Phase 45, `docs` extra) — both already landed in prior phases, not this one.
`[project] dependencies` (the runtime surface) is byte-identical to `v0.7.0`. The Package Legitimacy
Gate protocol is therefore not applicable; no table is produced.

**Packages removed due to `[SLOP]` verdict:** none (n/a — no packages evaluated).
**Packages flagged as suspicious `[SUS]`:** none (n/a).

## Architecture Patterns

### System Architecture Diagram

```
 origin/main (9b2b76b, PR #131 merged)
        │
        │  git merge --no-ff  (D-20; local, un-pushed until later)
        ▼
 milestone branch HEAD ──┐
        │                │ ONE conflict: CHANGELOG.md ## [Unreleased] block
        │                │ (resolve = the D-05..D-10 curation work itself)
        ▼                ▼
 [Windows CI check push]     merged tree, CHANGELOG.md still [Unreleased]
   (D-22's repair rides       │
    with or separate from     │  bump pyproject.toml 0.7.0→0.7.1
    the merge — D-23 run 1)   │  uv lock   (regenerate uv.lock's typsphinx entry)
        │                     │  uv sync --extra dev --locked (regen .venv dist-info/editable pth)
        │                     │  curate ## [0.7.1] entry + tail link-block rollover
        │                     │  add "Migrating from 0.7.0 to 0.7.1" to docs/source/changelog.rst
        │                     ▼
        │              [bump + CHANGELOG commit]
        │                     │
        │                     │  push  (D-23 run 2 — SC#3's CI authority)
        │                     ▼
        │              CI: pytest / lint / type / build / integration ×
        │              {ubuntu, macos, windows} × {py312, py313}
        │                     │
        └──── both runs cross-checked ─────┤
                                            ▼
                          Local evidence (D-11's per-environment half):
                          tox -e docs-html │ tox -e docs-pdf │
                          pytest tests/test_corpus_gate.py -v │
                          SPHINX_LANGUAGE=ja docs-pdf build
                                            │
                                            ▼
                          SC#4 invariant sweep, anchored v0.7.0 (75fd8ed) → post-merge HEAD:
                          diff pyproject.toml [dependencies] block (must be empty)
                          grep -rl '@preview/' (must equal the known 4-surface + examples set)
                                            │
                                            ▼
                          REL-04 precondition checks (never acceptance):
                          static read of release.yml:162-168 (setup-uv + Set up Python present)
                          uv run python scripts/extract_changelog_section.py 0.7.1  (exit 0)
                                            │
                                            ▼
                          46-HANDOFF.md (41-HANDOFF.md shape) — merge→tag→release.yml→
                          PyPI+GitHub Release→2nd tag→RTD stable, all deferred to
                          /gsd-complete-milestone
                                            │
                                            ▼
                          Fence proof: git tag -l v0.7.1  (empty)
                                       git ls-remote --tags origin v0.7.1  (empty)
```

### Recommended Plan/Wave Structure

Not a source-code directory structure (this phase touches no `typsphinx/` code) — instead, the
natural wave split mirrors the dependency chain the diagram above shows:

```
Wave 1: merge origin/main (D-20) + D-22's one-line test repair, pushed for the Windows check run (D-23 run 1)
Wave 2 (after wave 1's CI is at least dispatched, does not need to wait for completion to start editing):
        version bump + uv.lock/editable regen + CHANGELOG.md curation (D-05..D-10) +
        docs/source/changelog.rst migration section (D-09) + RELEASE_VERSIONS append (after the
        CHANGELOG entry exists) + tail link-block rollover, pushed for the authority run (D-23 run 2)
Wave 3: local evidence collection (docs-html, docs-pdf, corpus gate, ja build) — can run in parallel
        with wave 2's CI, since none of it depends on the push having completed
Wave 4: SC#4 invariant sweep (needs the post-merge HEAD from wave 1+2 combined)
Wave 5: REL-04 precondition checks + 46-HANDOFF.md + fence-proof + close-out todo filing
```

### Pattern 1: Version-literal bump and editable-install metadata regeneration

**What:** `typsphinx.__version__` is derived at import time via
`importlib.metadata.version("typsphinx")` (`[VERIFIED: typsphinx/__init__.py:14-22]` —
`import importlib.metadata` / `__version__ = importlib.metadata.version("typsphinx")` /
`except importlib.metadata.PackageNotFoundError: __version__ = "unknown"`). This reads Python's
installed-package metadata, not `pyproject.toml` directly. In an editable install, that metadata
lives in two places whose filenames literally embed the version string — confirmed by directory
listing this session: `.venv/lib/python3.13/site-packages/typsphinx-0.7.0.dist-info/`,
`__editable__.typsphinx-0.7.0.pth`, and `__editable___typsphinx_0_7_0_finder.py`. Editing
`pyproject.toml`'s version literal alone does **not** change what `importlib.metadata.version()`
returns — the `.dist-info`/editable-pth pair must be regenerated by re-running the installer.

**When to use:** The exact acceptance criterion CONTEXT.md's Claude's Discretion section states:
`uv sync --extra dev --locked` green.

**Verified mechanism (this session, non-mutating checks only — no in-place `pyproject.toml` edit was
performed, per this project's standing constraint against mutating the live manifest and syncing
against it):**

```bash
# Confirms the CURRENT lock already matches the CURRENT pyproject.toml (read-only, safe to run
# any time as a sanity check before/after the bump):
$ uv lock --check
Resolved 89 packages in 0.94ms
$ echo $?
0
```

```bash
# uv.lock's own typsphinx entry embeds the version literal too — [VERIFIED: uv.lock:1466-1468]
$ grep -n -A2 'name = "typsphinx"' uv.lock
1466:name = "typsphinx"
1467:version = "0.7.0"
1468:source = { editable = "." }
```

**The regeneration sequence (planner executes; not run this session against the real manifest):**

```bash
# 1. Edit pyproject.toml:7 — version = "0.7.0" -> "0.7.1"
# 2. Regenerate the lock so its cached typsphinx entry (uv.lock:1467) picks up the new version:
uv lock
# 3. Sync --locked to PROVE the lock now matches pyproject.toml (fails loudly if step 2 was
#    skipped or the lock is otherwise stale) AND to regenerate .venv's dist-info/editable-pth pair:
uv sync --extra dev --locked
# 4. Verify the regenerated metadata is actually read back correctly:
python -c "import typsphinx; print(typsphinx.__version__)"   # expect: 0.7.1
# equivalently, the repo's own drift guard:
pytest tests/test_extension.py::test_version_matches_pyproject_toml -v
```

`[VERIFIED: typsphinx/__init__.py:14-22]` for the derivation mechanism;
`[VERIFIED: .venv dist-info directory listing, this session]` for the filename-embeds-version fact;
`[VERIFIED: pyproject.toml:33-38]` for the current `dev` extra (post-Phase-45.2, no bundled `uv`);
the four-command sequence itself is `[ASSUMED]` in the sense that it was reasoned from the verified
mechanism above rather than executed end-to-end against a real 0.7.0→0.7.1 bump this session (doing
so would have mutated the shared repository state this research session must leave untouched). The
individual `uv lock --check` and `uv sync --locked` command *shapes* are directly verified working on
this machine (the `--check` invocation above ran clean; `uv sync --locked --extra dev` is exactly the
invocation `tox`'s own `uv-venv-lock-runner` already runs successfully every time an env provisions —
confirmed in this session's `tox -e docs-html`/`tox -e docs-pdf`/`tox -e py313`/`tox -e lint --notest`
transcripts, all of which begin with a `uv sync --locked …` line that completed without error).

**NixOS constraint carried forward from CONTEXT.md `<specifics>` items 1–6 (and CLAUDE.md's QUA-04
note):** do **not** invoke `.venv/bin/uv` directly or rely on a bare `uv run` inside a stale `.venv`
that still has a bundled `uv`/`uvx` binary — confirmed this session that this repository's current
`.venv/bin/` (post-Phase-45.2) has **no** `uv`/`uvx` entry at all
(`file .venv/bin/uv` → `cannot open … No such file or directory`), so `uv` on `PATH` now resolves
unambiguously to the working nix-store build
(`command -v uv` → `/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv`). Every `uv …`
invocation above is safe to run as a bare command (no `.venv/bin` shadowing hazard remains for `uv`
itself — that hazard was Phase 45.2's own subject and is now closed). `.venv/bin/ruff`, by contrast,
**is still** a generic-linux ELF NixOS's stub loader rejects — see Pitfall 1.

### Pattern 2: The CHANGELOG entry shape

`[VERIFIED: CHANGELOG.md:1-73]` — the established shape for a version section is:

```markdown
## [X.Y.Z] - YYYY-MM-DD

<lead paragraph — 2-4 sentences, user-facing framing>

### Added
- **<Bold user-visible summary> (REQ-ID, REQ-ID)** — <description>

### Changed
- ...

### Fixed
- ...

### Removed          <!-- NEW for v0.7.1 per D-02/D-10 -- first time this section exists -->
- ...

### Verified
- Zero new runtime dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx vX.Y.Z `doc/`) `-b typstpdf` re-run remains fatal-free.
```

The tail link block at the very end of `CHANGELOG.md` (`[VERIFIED: CHANGELOG.md tail, this session]`)
is a flat list of `[X.Y.Z]: https://github.com/YuSabo90002/typsphinx/releases/tag/vX.Y.Z` lines, most
recent first, terminated by
`[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.7.0...HEAD`. The v0.7.1 rollover
is two edits: insert `[0.7.1]: …/releases/tag/v0.7.1` above the `[0.7.0]` line, and change the
`[Unreleased]` line's compare base from `v0.7.0...HEAD` to `v0.7.1...HEAD`.

### Pattern 3: The D-20 merge-conflict mechanics

**Verified this session** (`git merge-tree --write-tree HEAD origin/main`, exit output identical to
CONTEXT.md's own D-20 measurement): exactly one conflict, `CHANGELOG.md`; `typsphinx/builder.py` and
`tests/test_builder.py` auto-merge clean.

The two sides of the conflict, read directly this session:

- **Local (`HEAD`) `## [Unreleased]` block** (`[VERIFIED: git show HEAD:CHANGELOG.md, this session]`):
  ```markdown
  ## [Unreleased]

  ### Planned for Future Releases
  - BibTeX/bibliography support
  - Glossary generation
  - Index generation
  - Pre-commit hooks
  - Additional Typst Universe template integration
  ```

- **`origin/main`'s `## [Unreleased]` block** (`[VERIFIED: git show origin/main:CHANGELOG.md, this
  session]`) — the PR #131 entry D-24 compresses, 13 body lines under one `### Fixed` bullet:
  ```markdown
  ## [Unreleased]

  ### Fixed

  - **Absolute image URIs from Sphinx's image converter/downloader break copy and path resolution
    (Issue #130)** — building with an image-conversion extension (`sphinxcontrib.rsvgconverter`,
    `sphinxcontrib.inkscapeconverter`, `sphinx.ext.imgconverter`) or a remote/downloaded image
    triggers Sphinx's `ImageConverter`/`ImageDownloader` post-transforms, which rewrite the image
    node's `uri` to an absolute filesystem path under `<doctreedir>/images/...` instead of the usual
    source-root-relative path. `copy_image_files()` previously joined that absolute URI onto both
    `srcdir` and `outdir` with `os.path.join()`, which silently discards the first argument once the
    second is absolute — collapsing source and destination onto the identical path ("are the same
    file") and copying nothing. The translator's path-adjustment logic then prepended a bogus
    `../..` depth prefix onto the still-absolute URI, producing a garbled path that made
    `typst.compile()` abort with "file not found". `TypstBuilder.post_process_images()` now rehomes
    an absolute resolved URI to a `doctreedir`-relative path and tracks the true absolute source
    location separately, so `copy_image_files()` copies from the real location to the correct
    relative destination.
  ```

**Resolution shape for the plan's `<action>`:** git will mark the conflict with `<<<<<<<`/`=======`/
`>>>>>>>` markers around the two `## [Unreleased]` bodies above (both sides have the *same* heading
line `## [Unreleased]`, so the block boundary itself is unambiguous — only the body differs). The
resolution is NOT a mechanical pick-one-side merge: it IS the D-05..D-10 curation work — the final
`## [0.7.1]` section (replacing both `## [Unreleased]` bodies) must (a) retain PR #131's compressed
bullet per D-24/D-25 inside the new section's `### Fixed`, and (b) leave a fresh, empty
`## [Unreleased]` heading with the local side's `### Planned for Future Releases` list intact above
the new `## [0.7.1]` section (Keep a Changelog convention this project already follows — see the
current file's own `## [Unreleased]` → `## [0.7.0]` transition as the template). Whichever plan
performs `git merge origin/main` will land in this exact conflict state and must resolve it by hand
(not `git merge -X ours`/`-X theirs`, both of which would silently drop real content).

### Pattern 4: Local evidence commands, verified working this session

| Evidence | Command | Result this session |
|----------|---------|---------------------|
| HTML docs build | `tox -e docs-html` (from repo root; the env internally `changedir`s to `docs/` and runs `sphinx-build -b html source _build/html`) | `docs-html: OK (0.95s)`, "build succeeded." |
| PDF docs build (dogfoods `typstpdf`) | `tox -e docs-pdf` | `docs-pdf: OK (3.18s)`, "Generated PDF: …/docs/_build/pdf/typsphinx.pdf", "build succeeded." |
| Full-corpus `-b typstpdf` gate | `pytest tests/test_corpus_gate.py -v` (direct, no tox needed — see Pitfall 4) OR `.venv/bin/pytest tests/test_corpus_gate.py -v` | `4 passed, 1 skipped in 30.34s` — `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` PASSED. The 1 skip is `test_empty_url_before_after`, gated on `TYPSPHINX_CORPUS_REPORT=1`, unrelated to the gate itself. |
| `ja` docs-pdf build (D-12's single-check bar) | `SPHINX_LANGUAGE=ja tox -e docs-pdf` — **not run this session** (pattern inferred from `docs/source/conf.py`'s existing language-detection scaffold; planner should verify the exact env-var name against `docs/source/conf.py` before relying on it) | `[ASSUMED]` — not executed this session |
| `test_readme_version_sync.py` + `test_preview_version_sync.py` | `tox -e py313 -- -k "test_readme_version_sync or test_preview_version_sync" -v` (works — matches this machine's system Python) OR `.venv/bin/pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | `4 passed in 0.83s` via the tox route |
| `tests/test_docs_contract_claims_gate.py` (D-22's target) | `.venv/bin/pytest tests/test_docs_contract_claims_gate.py -v` | `8 passed in 0.05s` — **all currently green on this Linux machine**, see Pitfall 3 |
| `uv.lock`/`pyproject.toml` sync check | `uv lock --check` | `Resolved 89 packages in 0.94ms`, exit 0 |

### Pattern 5: REL-04's in-phase share — the extractor's interface

`[VERIFIED: scripts/extract_changelog_section.py:1-148, read in full this session]`

- **CLI:** `python scripts/extract_changelog_section.py <version> [--changelog-path PATH]`, e.g.
  `python scripts/extract_changelog_section.py 0.7.1` (no leading `v`; `release.yml:197` strips it
  via `${TAG#v}` before calling). Default `--changelog-path` is `<repo-root>/CHANGELOG.md`.
- **Behavior:** purely **positional** parsing — finds the first `## [<version>]` heading line whose
  bracketed text equals the requested version, then takes every line up to (not including) the next
  `## [...]` heading (any heading, not name-filtered) or EOF, strips leading/trailing blank lines.
  Deliberately does **not** special-case the string `"Unreleased"` — `CHANGELOG.md` carries two
  `## [Unreleased]` headings (the standard placeholder near the top, and an unrelated "Planned for
  Future Releases" scratch heading in the tail) and the algorithm must not be tempted to "fix" that
  by name-matching.
- **Output:** prints the extracted, stripped section body to **stdout**. Never an empty string.
- **Failure modes (both exit 1, message to stderr):** no `## [<version>]` heading found; or the
  section's body is empty after stripping (e.g. a heading with nothing under it).
- **Both CI jobs call this exact script, never a re-implementation:** `validate` job
  (`release.yml:76`, `uv run python scripts/extract_changelog_section.py "$VERSION" >/dev/null` —
  existence-and-non-emptiness check, runs *before* `build`/`publish-pypi`/`create-release`) and
  `create-release` job (`release.yml:197`,
  `uv run python scripts/extract_changelog_section.py "${TAG#v}" > release_notes.md` — this becomes
  the actual GitHub Release body, with an `## Installation` block appended after).
- **In-phase exercise, mechanical and checkable (matches D-23's "precondition, never acceptance"
  framing):**
  ```bash
  # After the ## [0.7.1] section exists in CHANGELOG.md:
  uv run python scripts/extract_changelog_section.py 0.7.1
  echo "exit=$?"   # expect 0
  # Negative-path sanity check (proves the failure path still works, per the script's own docstring
  # security note that `version` is only ever a string-equality comparison, never shell-interpolated):
  uv run python scripts/extract_changelog_section.py 9.9.9   # expect exit 1, message to stderr
  ```
- **`release.yml`'s `create-release` job, confirmed carrying the fix this session**
  (`[VERIFIED: .github/workflows/release.yml:162-168]`):
  ```yaml
        - name: Install uv
          uses: astral-sh/setup-uv@v7
          with:
            version: "latest"

        - name: Set up Python
          run: uv python install 3.12
  ```
  — these two steps sit immediately before the `uv run python scripts/extract_changelog_section.py`
  call at `release.yml:197` (inside the "Generate release notes" step). The inline comment at
  `release.yml:156-161` names the exact failed run this fixes (`30848860064`). **This is the
  in-phase precondition to record — not to re-fix.**

### Pattern 6: The `41-HANDOFF.md` and `41-RELEASE-EVIDENCE.md` shapes (SC#5's precedent)

`[VERIFIED: read both files in full this session]`

**`41-HANDOFF.md`'s heading structure** (the shape SC#5 asks `46-HANDOFF.md` to follow):

```
# Phase 41: … — Publish & Owner-Manual Handoff Checklist
## What this phase satisfied, and what it did not
## Checklist
### 1. Open the pull request and merge it to `main`
### 2. Push the `v0.7.0` tag on the merge commit
### 3. Let `release.yml` run to completion: validate → build → publish-pypi → create-release
### 4. Advance the `typsphinx-doc-translations` submodule pin and push a matching tag
### 5. Confirm Read the Docs `stable` is green on BOTH projects (en and ja)
### 6. Flip REL-04's/REL-05's checkboxes and Traceability rows in REQUIREMENTS.md
### 7. File the two todos this phase's own code work resolved
## Not done in this phase, by design
## Deferred by decision, not oversight (D-14)
## Proof the fence held
```

Every numbered checklist item names an **Owner** (`/gsd-complete-milestone` and/or human) and an
**Ordering** dependency on the items before it. For Phase 46, the analogous items (owner in every
case is `/gsd-complete-milestone`, sequenced) are: open PR/merge → push `v0.7.1` tag → let
`release.yml` run to completion (**and this time, explicitly watch `create-release` succeed — this is
what closes REL-04**) → advance the `typsphinx-doc-translations` pin and tag it `v0.7.1` there →
confirm RTD `stable` green on both projects → flip REL-04's/REL-06's checkboxes and Traceability rows
→ file `46-HANDOFF.md`'s own closing todos (the two `_track_image` records stay pending per D-27; the
Windows-separator todo moves to `completed/` per D-16).

**`41-RELEASE-EVIDENCE.md`'s heading structure** (the shape SC#3/SC#4's live-run evidence should
follow, subject to D-15's naming constraint — **not** `46-VERIFICATION.md`):

```
# Phase 41: … — Release Evidence
## SC#1: <criterion>
## SC#2: <criterion, measured directly>
### <subsection per measured fact>
## SC#3: <criterion>
### Mechanical half — cite <sibling file> (plan …)
### <glyph-bar / other subsection> — cite <sibling file> (plan …)
### SC#3 roll-up verdict
## SC#4: <criterion>
### SC#4 roll-up verdict
## SC#5: no irreversible action taken — the fence, observation 1 of 2
### SC#5 (observation 1) verdict
## Phase verdict
## Executed versus skipped
```

Key conventions worth carrying forward: (a) this file **cites** sibling per-plan evidence files
rather than re-deriving their findings, quoting their own verdict language verbatim; (b) SC#5's fence
proof is **two independent observations at two separate moments** (`git tag -l …` +
`git ls-remote --tags origin …`, both empty), one recorded in the evidence file and the second in the
handoff document, timestamped apart; (c) an "Executed versus skipped" closing section states plainly
what was *not* run and why, rather than glossing over gaps.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Extracting a CHANGELOG section for a release body | A new script or inline shell/`awk`/`sed` parsing | `scripts/extract_changelog_section.py` (already committed, pytest-covered — `tests/test_changelog_extraction.py`) | It is the ONE implementation both `validate` and `create-release` call; a second parser risks silent divergence from what CI actually runs. |
| Detecting the version-sync drift class | A new ad-hoc grep/manual check | The three existing `tests/test_*_sync.py` / `test_changelog_page_gate.py` modules, rerun as-is | Already proven, already CI-covered, and the RELEASE_VERSIONS-tuple pattern is the established idiom for "N releases must all appear in the built page." |
| Verifying `release.yml`'s `create-release` job has the uv-setup fix | Manually eyeballing the YAML in an editor | A direct `Read`/`grep` of `release.yml:162-168` against the exact step names, recorded verbatim in evidence | Matches this project's "evidence culture" — commands and output transcribed verbatim, never asserted from memory. |
| Proving the tree is green | Trusting a stale/inherited CI badge from an earlier phase | A fresh push on the post-bump commit, read from the run itself (D-11/D-23) | The whole point of D-11/D-23 is that inherited green does not prove the *bumped* tree is green — this milestone's own REL-04/Windows failures happened precisely because the branch was never pushed until the release PR (milestone invariant #5). |

**Key insight:** every mechanism this phase needs already exists and is already tested — the entire
phase is orchestration (bump, curate, merge, push, observe, record) over existing tooling, not new
implementation. The one genuinely new procedural step is the `origin/main` merge (D-20), and even
that resolves to "run `git merge`, resolve one known conflict by hand, following the D-05..D-10
curation shape."

## Common Pitfalls

### Pitfall 1: `tox -e py312` cannot provision locally on this machine — new finding, not in
`46-CONTEXT.md`

**What goes wrong:** `tox -e py312` (targeting Python 3.12 specifically) fails at the `uv venv`
provisioning step with `Could not start dynamically linked executable` / `exit status: 127`, the same
NixOS stub-loader failure class D-11 amendment (b) already documents for `.venv/bin/ruff`.

**Why it happens:** measured this session — `uv venv -p cpython3.12 …` tries to resolve/download a
standalone CPython 3.12 build via `uv python install`-style resolution
(`/home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python3.12`), and that
downloaded build is itself a generic-linux ELF the NixOS stub loader rejects — a *different* instance
of the same root cause as the `.venv/bin/uv`/`.venv/bin/ruff` binaries, but on a completely different
binary this time (a uv-managed Python interpreter, not a project dependency).
`tox -e py313`, by contrast, succeeds locally, because this machine's already-installed system Python
IS 3.13 (`--python-preference system` resolves it directly, no download needed):

```
$ .venv/bin/tox -e py312 -- -k "test_readme_version_sync or test_preview_version_sync" -v
py312: venv> …uv venv -p cpython3.12 --allow-existing … --python-preference system …
error: Querying Python at `/home/yuta/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python3.12` failed with exit status exit status: 127
  py312: FAIL code 2 (0.09 seconds)

$ .venv/bin/tox -e py313 -- -k "test_readme_version_sync or test_preview_version_sync" -v
py313: venv> …uv venv -p cpython3.13 …
py313: uv-sync> …uv sync --locked --python-preference system --extra dev -p cpython3.13
py313: commands[0]> pytest -k … -v
4 passed, 989 deselected in 0.83s
  py313: OK (2.04s)
```

**How to avoid:** this does not weaken any locked decision — D-11 amendment (b) already assigns
pytest/lint/type authority to CI, not local, so `py312`'s local unavailability changes nothing about
what the phase must prove. But if the planner or a plan author wants a *local* pytest sanity check
before pushing (not the same as the CI authority run), use `tox -e py313` (or bypass tox entirely and
run `.venv/bin/pytest`/`uv run pytest` directly, which is the primary documented `CLAUDE.md` command
and does not hit this interpreter-provisioning path at all), never `tox -e py312` on this machine.

**Warning signs:** any plan `<action>` that says "run `tox -e py312` locally to confirm" will fail on
this development machine specifically — flag it in review rather than let an executor discover it
mid-task.

### Pitfall 2: `uv sync --extra dev` alone does not surface `myst-parser`

**What goes wrong:** `import myst_parser` fails against the main dev `.venv`
(`ModuleNotFoundError: No module named 'myst_parser'`, measured this session), even though
`tox -e docs-html`/`tox -e docs-pdf` both succeed.

**Why it happens:** `myst-parser` lives in the `docs` extra (`pyproject.toml:49-54`), not the `dev`
extra. `tox`'s `docs-html`/`docs-pdf` environments each provision their **own** isolated venv
(`.tox/docs-html/`, `.tox/docs-pdf/`) with `extras = docs` — separate from the shared `.venv` that
`extras = dev` provisions. This is also why `tests/test_changelog_page_gate.py`'s
`TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` classes are
`@pytest.mark.skipif(not MYST_PARSER_AVAILABLE, …)` — running `.venv/bin/pytest
tests/test_changelog_page_gate.py -v` directly (dev-extras-only venv) will **skip** both of those
classes, silently passing without ever asserting the RELEASE_VERSIONS content actually reaches the
built page/PDF.

**How to avoid:** either invoke the `docs`-extras-provisioned tox envs directly (`tox -e docs-html`,
`tox -e docs-pdf` — already proven working locally this session), or explicitly sync both extras into
one venv before running pytest directly (`uv sync --extra dev --extra docs`, not attempted this
session to avoid mutating the shared dev `.venv`'s installed-package set mid-research). Either way,
the RELEASE_VERSIONS assertion in `test_changelog_page_gate.py`'s slow classes needs `myst-parser`
present to run for real, not skip.

**Warning signs:** a plan that runs `pytest tests/test_changelog_page_gate.py -v` and reports "all
green" without checking for skips has not actually proven RELEASE_VERSIONS reaches the built page —
check the pytest summary line for `skipped` counts, not just `passed`.

### Pitfall 3: The D-22/D-09 "ordering interaction" — direct measurement partially contradicts
`46-CONTEXT.md`'s framing

**What goes wrong (as framed in `46-CONTEXT.md`):** "D-09 adds migration fragments to
`docs/source/changelog.rst`, which is listed in `EXCLUDED_CLAIM_PAGES`. That page currently makes *no*
contract claim under the gate's scan — which is why the Windows failure includes a second assertion
calling the exclusion stale."

**What this session's direct measurement found:** running the gate's own predicate against the
**current, unmodified** `docs/source/changelog.rst` on this Linux machine:

```python
>>> from test_docs_contract_claims_gate import _page_makes_contract_claim, _discovered_claim_pages
>>> _page_makes_contract_claim(Path('docs/source/changelog.rst').read_text())
True
>>> 'docs/source/changelog.rst' in _discovered_claim_pages()
True
```

and running the full module: `pytest tests/test_docs_contract_claims_gate.py -v` → **8 passed**,
including `test_every_excluded_page_still_makes_a_claim` (the "stale exclusion" assertion) — it does
**not** currently fail on this machine. The page already satisfies
`_page_makes_contract_claim()`'s predicate today, before any Phase 46 edit, because its existing
"Migrating from 0.5.x to 0.6.x" section already contains both a published-param-name literal
(`` ``papersize`` ``/`` ``fontsize`` ``/`` ``lang`` ``) and a route/config token
(`` ``typst_elements`` ``) — `[VERIFIED: docs/source/changelog.rst:27, tests/test_docs_contract_claims_gate.py:103-148, both read in full this session]`.

**Reconciliation, per `.planning/todos/pending/2026-08-11-windows-path-separator-breaks-contract-claims-gate.md`'s own verbatim CI failure text** (read this session): the *actual* Windows CI failure is a pure string-representation bug —
`_discovered_claim_pages()` builds `str(page.relative_to(REPO_ROOT))`, which on Windows renders
`docs\source\changelog.rst` (backslashes). Since `EXCLUDED_CLAIM_PAGES`'s key is the forward-slash
literal `"docs/source/changelog.rst"`, the backslash string can never equal it under Windows'
`pathlib`, so `set(EXCLUDED_CLAIM_PAGES) - discovered` incorrectly retains
`"docs/source/changelog.rst"` — not because the page fails to make a claim, but because the
*key never matches* under backslash rendering. `46-CONTEXT.md`'s phrasing describes this
Windows-computed symptom ("looks like no claim was discovered under that key"), not a genuine
content-level absence of claim text — the two are easy to conflate but are mechanically distinct.

**Practical consequence for the planner:** this does not change what either D-22 or D-09 must do.
D-22's fix (`.as_posix()` normalization on `_discovered_claim_pages()`'s comparison keys) is still
exactly correct and is what makes the comparison platform-independent. D-09's migration-section
addition will not "newly" satisfy the predicate (it is already satisfied); it will simply add *more*
matching text to a page that already passes. **The one thing genuinely order-independent that this
measurement confirms: neither D-22 nor D-09 depends on landing before the other for this specific
test module to stay green on Linux/macOS/CI-ubuntu** — the ordering hazard `46-CONTEXT.md` flags is
real only insofar as a *human* reviewing the diff should not assume D-09's fragments are what "fixes"
the exclusion; D-22's `.as_posix()` change is what fixes Windows, independent of D-09's content.
After both edits land, `pytest tests/test_docs_contract_claims_gate.py -v` (all 8 tests) is the
correct local acceptance check, but it cannot itself prove the Windows-specific repair — only a real
Windows CI run (D-23 run 1) does that, since backslash-path behavior cannot be reproduced on this
Linux machine.

**Warning signs:** if a plan's rationale for sequencing D-22 before/after D-09 cites "the page
currently makes no claim" as a *reason* for the ordering, that premise should be corrected against
this measurement before the plan is trusted.

### Pitfall 4: The two `## [Unreleased]` headings in `CHANGELOG.md`

**What goes wrong:** a naive "find the `[Unreleased]` heading" implementation (or a plan `<action>`
that describes the merge/curation work that way) would be ambiguous — `CHANGELOG.md` has **two**
`## [Unreleased]` headings: the standard placeholder near the top (line 8, the one D-20's merge
conflict lands in) and a second, unrelated one deep in the tail block under
"Planned for Future Releases" scratch ideas (`[VERIFIED: scripts/extract_changelog_section.py:23-34]`,
the script's own documented "load-bearing gotcha").

**Why it happens:** the tail scratch area was apparently modeled after the same heading syntax by a
past author, without realizing `extract_changelog_section.py`'s positional algorithm would need to
treat it carefully (it does, deliberately, by never name-filtering — see Pattern 5 above).

**How to avoid:** when writing the plan's `<action>` for the D-20 merge-conflict resolution and the
D-05..D-10 CHANGELOG curation, be explicit about *which* `## [Unreleased]` occurrence is being edited
(the first one, near the top) — a line-number or "the block immediately following the file's own
Keep-a-Changelog preamble" anchor is safer than a bare textual search for `## [Unreleased]`.

**Warning signs:** any automated find-and-replace over `## [Unreleased]` without an occurrence guard
would corrupt the tail scratch section.

## Code Examples

### Version-literal bump and editable-install regen (see Pattern 1 above for full context)

```bash
# after editing pyproject.toml:7 to version = "0.7.1"
uv lock
uv sync --extra dev --locked
python -c "import typsphinx; print(typsphinx.__version__)"   # expect 0.7.1
pytest tests/test_extension.py::test_version_matches_pyproject_toml -v
pytest tests/test_readme_version_sync.py -v   # after README.md:342 is also moved
```

### SC#4's invariant sweep — concrete, verified command shapes

**(a) Zero new runtime dependencies** — verified working this session:

```bash
# Diff ONLY the [project] dependencies array between the release anchor and HEAD:
diff <(git show v0.7.0:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p') \
     <(sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml)
# this session, against pre-merge HEAD: empty diff, exit 0 -- confirms [project] dependencies
# is byte-identical to v0.7.0.

# Broader sanity check -- confirm which lines in the WHOLE pyproject.toml changed at all
# (to eyeball that only dev/docs extras moved, never [project] dependencies):
git diff v0.7.0..HEAD -- pyproject.toml | grep -E '^[+-]' | grep -v '^+++\|^---'
# this session's actual output (pre-merge HEAD):
#   -    "tox-uv>=1.35,<2",
#   +    "tox-uv-bare>=1.35,<2",
#   +    "myst-parser>=5.0",
```

Re-run both commands against `v0.7.0..<post-merge-HEAD>` once D-20's merge lands (the anchor per D-21
is the `v0.7.0` **tag**, not `87f242a`).

**(b) `@preview` count still four, no new lockstep site** — verified working this session:

```bash
# The existing sync test already does the identity check mechanically:
pytest tests/test_preview_version_sync.py -v

# Repo-wide enumeration of every @preview import site (to eyeball no NEW file joined the set):
grep -rln '@preview/' --include='*.typ' --include='*.py' . \
  | grep -v '^\./\.git\|^\./\.tox\|^\./\.venv'
```

This session's enumeration returned the four canonical sync-guarded files
(`typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`), the
`examples/**/*.typ` set (test_preview_version_sync.py's fourth, drift-only surface), a set of test
files that merely *reference* `@preview/` syntax in fixtures/docstrings (not a lockstep hazard — the
sync test's regex only matches real `#import` statements), and one already-known, already-out-of-scope
unguarded surface: `docs/source/_typst/custom_template.typ` (flagged by the v0.6.4-era 30.1 review as
a standing Warning, carried in `STATE.md`'s Deferred Items — not new to this milestone, and not this
phase's responsibility to fix). **No new file appeared in this enumeration relative to what
`test_preview_version_sync.py`'s own docstring already documents as the sync surface** — re-run this
grep after the D-20 merge to confirm PR #131's `typsphinx/builder.py` changes did not introduce a
fifth surface (they should not — `_track_image()` is not template/import code).

### REL-04's in-phase precondition checks

```bash
# 1. Static confirmation the create-release job's uv-setup fix is present (already true this session):
grep -n -A2 "Install uv" .github/workflows/release.yml | sed -n '1,20p'
sed -n '162,168p' .github/workflows/release.yml

# 2. Mechanical exercise against the real ## [0.7.1] section, once it exists:
uv run python scripts/extract_changelog_section.py 0.7.1
echo "exit=$?"
```

### Local green-tree evidence, exact commands verified this session

```bash
tox -e docs-html            # OK, ~1s, "build succeeded."
tox -e docs-pdf             # OK, ~3s, writes docs/_build/pdf/typsphinx.pdf, "build succeeded."
pytest tests/test_corpus_gate.py -v    # 4 passed, 1 skipped, ~30s (network required, D-05 auto-skips otherwise)
uv lock --check              # confirms lock/pyproject agreement, read-only
```

## State of the Art

Not applicable in the usual "library X was superseded by Y" sense — this phase is entirely
first-party release engineering with no external ecosystem drift to track. The one relevant "state of
the art" fact is internal: this project's own release-body mechanism moved from a raw `git log
--pretty` commit dump (pre-Phase-41) to the curated `## [X.Y.Z]` CHANGELOG-section extraction
(`scripts/extract_changelog_section.py`, Phase 41) — REL-04 is the closing exercise of that same
change, not a new mechanism.

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `release.yml`'s `create-release` body built from `git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` | Curated `## [X.Y.Z]` CHANGELOG section via `scripts/extract_changelog_section.py` | Phase 41 (v0.7.0) | REL-04 exists to *prove* this end to end via a real tag push — v0.7.0's own tag push failed at this exact step (`uv: command not found`, no `astral-sh/setup-uv` in `create-release`), repaired by hand at the time, fixed on `main` afterward. This phase verifies the fix is still in place and exercises the extractor, but cannot itself complete the proof. |

**Deprecated/outdated:** the `git log --pretty` commit-dump code path is already fully removed from
`release.yml` (confirmed by direct read this session — no `git log --pretty` or `$PREV_TAG` fragment
remains in the file) — nothing to migrate away from in this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | The 4-command version-bump sequence (`edit pyproject.toml` → `uv lock` → `uv sync --extra dev --locked` → verify `__version__`) works end-to-end against a real `0.7.0`→`0.7.1` edit. | Architecture Patterns § Pattern 1 | Individually-verified sub-steps (`uv lock --check` clean; `uv sync --locked` shape proven by every `tox` env this session) make this low-risk, but the full sequence was deliberately not executed against a live mutation this session (see the pattern's own note). If wrong, `pytest tests/test_extension.py::test_version_matches_pyproject_toml` will fail loudly and immediately — cheap to detect. |
| A2 | `SPHINX_LANGUAGE=ja` (or an equivalent env var/conf override) is the correct mechanism to drive D-12's single `ja` docs-pdf build. | Architecture Patterns § Pattern 4 | Not executed this session; inferred from `docs/source/conf.py`'s existing language-detection scaffold (not directly read this session). If the actual mechanism differs, the planner must read `docs/source/conf.py`'s language-selection logic before writing this task's `<action>`. |
| A3 | The `## [0.7.1]` heading insertion point and the tail-link-block rollover are the only two edits needed to keep `CHANGELOG.md` structurally valid for `extract_changelog_section.py`'s positional parser. | Architecture Patterns § Pattern 2 | Low risk — the parser's algorithm was read in full and is genuinely heading-position-only; any two adjacent `## [...]` headings bound a section correctly regardless of naming. |

**If this table is empty:** N/A — three items above need light confirmation, none blocks planning.

## Open Questions

1. **Exact wording/mechanism of `docs/source/conf.py`'s language-selection hook for the `ja` docs-pdf
   build (D-12).**
   - What we know: Phase 45.1 removed the `lang` auto-derivation workaround that once lived in
     `docs/source/conf.py`, leaving a comment stating "do not re-add that workaround" (per
     `46-CONTEXT.md` D-13). `docs/source/_typst/custom_template.typ:64-75` declares all nine
     parameters including `lang`.
   - What's unclear: whether the `ja` build is driven by a `sphinx-build -D language=ja` CLI flag, an
     env-var read inside `conf.py`, or a separate `docs/source/conf.py`-adjacent `ja` build config.
     This research did not read `docs/source/conf.py` in full this session.
   - Recommendation: the plan that owns D-12's single `ja` build should `Read docs/source/conf.py`
     first (a five-minute check) and record the exact invocation in its own `<action>`, rather than
     assume `SPHINX_LANGUAGE=ja` sight-unseen.

2. **Whether `test_docs_contract_claims_gate.py`'s current 8/8-green state on Linux should be recorded
   as evidence anywhere, given Pitfall 3's reconciliation.**
   - What we know: the module passes cleanly today, pre-Phase-46, on this machine; the Windows
     failure is real but is a separate CI-only symptom.
   - What's unclear: whether the planner wants a plan-level acceptance criterion that explicitly reruns
     this module locally (cheap, ~0.05s) as a smoke check before relying on D-23 run 1's Windows-only
     confirmation, or whether that would be redundant busywork given the module already passes
     unconditionally on non-Windows platforms.
   - Recommendation: include the local rerun as a cheap pre-push sanity check in whichever plan owns
     D-22, but do not treat it as sufficient evidence for D-22's own acceptance — only a real Windows
     CI run proves the fix (this matches D-11/D-23's own "CI is the authority" philosophy).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `uv` (nix-store) | Every `uv lock`/`uv sync`/`tox` provisioning step | ✓ | 0.11.25 | — |
| `tox` + `tox-uv-bare` | `docs-html`, `docs-pdf`, `py313` local envs | ✓ | 4.56.1 / 1.35.2 | — |
| `.venv/bin/ruff` (generic-linux ELF) | `tox -e lint` locally | ✗ (exit 127, NixOS stub-ld) | — | CI is the authority per D-11 amendment (b); no local fallback needed — not this phase's job to fix (tracked as todo `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos`, out of scope) |
| Python 3.12 (standalone, uv-managed) | `tox -e py312` locally | ✗ (exit 127, NixOS stub-ld — new finding, Pitfall 1) | — | Use `tox -e py313` or direct `.venv/bin/pytest`/`uv run pytest` for a local pytest sanity check; CI is still the authority for the matrix |
| Python 3.13 (system) | `tox -e py313`, `.venv` itself | ✓ | 3.13.13 | — |
| `sphinx` | docs builds, full-corpus gate | ✓ | 9.1.0 | — |
| `typst` (typst-py) | PDF compile path | ✓ | 0.15.0 | — |
| `myst-parser` | `docs/source/changelog.rst`'s `.. include::` rendering | ✗ in `.venv` (dev extras only); ✓ in `.tox/docs-*` (docs extras) | — (see Pitfall 2) | Use `tox -e docs-html`/`tox -e docs-pdf`, or `uv sync --extra dev --extra docs` before a direct `pytest tests/test_changelog_page_gate.py -v` |
| Network (github.com) | Full-corpus gate's `git clone --depth 1` of Sphinx's `doc/` tree | ✓ (confirmed this session — clone + build completed in 30s) | — | `pytest.skip`s honestly (D-05 of the gate's own design) if unavailable — never a hard failure |
| `git` | Merge-tree dry runs, diffs, tag checks | ✓ | 2.54.0 | — |
| `gh` (GitHub CLI) | Verifying PR #131 / CI-run states referenced in `46-CONTEXT.md` | ✓ | 2.97.0 | — |

**Missing dependencies with no fallback:** none — every gap above has a working local or
CI-authoritative fallback.

**Missing dependencies with fallback:** `.venv/bin/ruff` (→ CI authority), Python 3.12 standalone
(→ `tox -e py313` or direct pytest), `myst-parser` in the dev-only `.venv` (→ `docs`-extras tox envs
or a combined `--extra dev --extra docs` sync).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, `addopts = "-v --strict-markers"`) |
| Quick run command | `pytest -k "<narrow selector>" -v` or a single-module invocation (e.g. `pytest tests/test_readme_version_sync.py -v`, sub-second) |
| Full suite command | `pytest tests/` (993 tests collected this session, no default `-m` filter — includes the slow full-corpus gate) — CI's authority run is `tox -e py312`/`tox -e py313` (`pytest {posargs:tests/}`), not this phase's job to invoke by hand except as a local sanity spot-check |

### Phase Requirements → Test Map

Every row below is a **rerun of an already-existing, already-passing test/gate** — this phase adds
exactly two mechanical data edits to existing test files (D-22's one-line repair,
`RELEASE_VERSIONS`'s `"0.7.1"` append) and zero new test modules.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|--------------|
| REL-06 (version literal) | `typsphinx.__version__` reports `0.7.1` after the bump+regen | unit | `pytest tests/test_extension.py::test_version_matches_pyproject_toml -v` | ✅ (existing) |
| REL-06 (README/pyproject lockstep) | README's Status line version matches `pyproject.toml`'s | unit | `pytest tests/test_readme_version_sync.py -v` | ✅ (existing) |
| REL-06 (`@preview` invariant, unchanged by this phase) | The 4-package sync surface stays identical | unit | `pytest tests/test_preview_version_sync.py -v` | ✅ (existing) |
| REL-06 (CHANGELOG page currency) | `docs/source/changelog.rst`'s built page/PDF carries every release incl. `0.7.1` | integration (slow, `myst-parser`-gated — see Pitfall 2) | `tox -e docs-html` then `pytest tests/test_changelog_page_gate.py -v` (or run inside a `docs`-extras venv) | ✅ (existing; requires `RELEASE_VERSIONS` append **after** the CHANGELOG entry lands) |
| REL-06 (Windows CI regression, D-22) | `_discovered_claim_pages()` path comparison is platform-independent | unit (Linux-provable) + CI-only (Windows-provable) | `pytest tests/test_docs_contract_claims_gate.py -v` (local, currently 8/8 green — see Pitfall 3) — **the actual proof is a real Windows CI run (D-23 run 1)**, not locally reproducible | ✅ (existing, one-line edit) |
| REL-06 (green tree — full suite / lint / type) | CI authority run, per D-11 | integration | CI: `uv run tox -e py312` / `py313` / `lint` / `type` / `cov` (already wired in `.github/workflows/ci.yml`) — this phase does not invoke these locally beyond a spot-check (D-11 amendment (b)) | ✅ (existing, CI-wired) |
| REL-06 (green tree — docs builds) | `docs-html`/`docs-pdf` build clean, locally invocable | integration | `tox -e docs-html`; `tox -e docs-pdf` | ✅ (existing; both verified green this session) |
| REL-06 (green tree — full-corpus gate) | Sphinx's own `doc/` corpus compiles fatal-free via `-b typstpdf` | integration (slow, network-gated, honest-skip) | `pytest tests/test_corpus_gate.py -v` | ✅ (existing; verified green this session) |
| REL-06 (`ja` build, D-12) | A single `SPHINX_LANGUAGE=ja` (or equivalent — Open Question 1) docs-pdf build succeeds | integration | To be confirmed against `docs/source/conf.py`'s actual mechanism | ✅ file exists (`docs/source/conf.py`); exact invocation `human_needed` until read |
| REL-06 (invariant sweep, D-21) | Zero new runtime deps; `@preview` count/surfaces unchanged | mechanical script/grep, not pytest | `diff`/`grep` shapes in Code Examples § "SC#4's invariant sweep" | N/A — ad hoc git/grep commands, not a test file |
| REL-04 (precondition only) | `release.yml`'s `create-release` job carries the uv-setup fix; extractor runs cleanly against `## [0.7.1]` | static read + script hand-run | `sed -n '162,168p' .github/workflows/release.yml`; `uv run python scripts/extract_changelog_section.py 0.7.1` | ✅ (existing script; no new file) |
| REL-04 (actual acceptance) | A real tag push runs `create-release` to completion | **`human_needed`** — structurally impossible before `/gsd-complete-milestone` | N/A | N/A — this phase must NOT report this row as closed |

### Sampling Rate

- **Per task/plan commit:** the narrow, fast guard tests relevant to that plan's own edit
  (`test_readme_version_sync.py`, `test_preview_version_sync.py`, `test_docs_contract_claims_gate.py`
  — all sub-second locally).
- **Per wave merge:** `tox -e docs-html`, `tox -e docs-pdf`, `pytest tests/test_corpus_gate.py -v`
  (the three local-authority items D-11 assigns), plus a push for the relevant CI run (check run or
  authority run per D-23).
- **Phase gate:** both CI runs (D-23) green (Windows-check + authority), the SC#4 invariant sweep
  commands re-run clean on the post-merge HEAD, REL-04's two precondition checks recorded, and the
  fence-proof (`git tag -l v0.7.1` / `git ls-remote --tags origin v0.7.1`, both empty) taken as two
  independent observations per the `41-HANDOFF.md` precedent, before `/gsd-verify-work`.

### Wave 0 Gaps

None — every test module, fixture, and gate this phase needs already exists and already passes (or
honestly skips) on this machine. The phase's own two test-file edits (D-22's `.as_posix()` repair;
`RELEASE_VERSIONS`'s `"0.7.1"` append) are one-line/one-tuple-entry mechanical changes to existing
files, not new test infrastructure. No new fixture, conftest addition, or framework install is
required.

## Security Domain

### Applicable ASVS Categories

This phase changes no runtime code path (`typsphinx/` is untouched except via D-22's test-module
edit) and introduces no new attack surface. The categories below are assessed for **regression risk
against the phase's own edits**, not as a fresh audit of the whole codebase.

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | No | N/A — no auth surface in this project |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal — `scripts/extract_changelog_section.py`'s `version` CLI argument | Already hardened, unchanged by this phase: the script's own docstring states the ASVS V5 rationale explicitly (`[VERIFIED: scripts/extract_changelog_section.py:36-41]`) — `version` is used only in a string-equality comparison against already-parsed text, never shell-interpolated, never `eval`'d, never used to build a filesystem path. This phase's in-phase exercise (`extract_changelog_section.py 0.7.1`) passes a first-party, non-attacker-controlled literal — no new risk. |
| V6 Cryptography | No | N/A |
| V14 Configuration / Secrets | Yes — `.github/workflows/release.yml` | Already-implemented, unchanged-by-this-phase control worth re-verifying intact through D-20's merge: every `${{ }}` GitHub Actions expression in `release.yml` is passed through `env:` rather than interpolated directly into a `run:` shell block (`[VERIFIED: .github/workflows/release.yml:38-44, 176]`, the file's own inline invariant comment: "Keep this invariant: no `${{ }}` inside any `run:` block in this file"). This is the standard mitigation against a maliciously crafted tag name (containing `` ` `` /`$()`/quotes — none of which git forbids in a tag name) executing arbitrary shell in a job holding `contents: write`/`id-token: write`. **Phase 46 does not edit `release.yml`** — confirm via `git diff` after D-20's merge that this file is untouched (PR #131 does not touch it either, per the merge-tree dry run's clean auto-merge of `typsphinx/builder.py`/`tests/test_builder.py` only). |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| GitHub Actions shell injection via an attacker-controlled tag name reaching a `run:` block | Tampering / Elevation of Privilege | `env:`-indirection pattern, already implemented and unchanged (see V14 row above) — verify it survives the D-20 merge untouched |
| A CHANGELOG merge-conflict resolution silently dropping real content (either side's `## [Unreleased]` body) | Tampering (of release-notes integrity, not a security vulnerability per se, but a data-integrity concern this project's "evidence culture" treats seriously) | Manual, reviewed conflict resolution per Pattern 3 above — never `git merge -X ours`/`-X theirs` |
| A stale/incorrect `EXCLUDED_CLAIM_PAGES`/`REVIEWED_CLAIM_PAGES` entry letting a real documentation-contract violation ship silently | Tampering (of published-documentation accuracy — this project's DOC-13 threat class) | `TestContractClaimPageEnumerationIsClosed`'s closed-both-directions set-equality checks, unchanged in intent by D-22 (only the string-normalization mechanics change) |

## Sources

### Primary (HIGH confidence — direct reads/executions this session)

- `.planning/phases/46-v0-7-1-release-prep-prep-only/46-CONTEXT.md` — full read, all 28 decisions
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md` — full reads
- `pyproject.toml`, `tox.ini`, `uv.lock` (relevant slices), `CHANGELOG.md`, `docs/source/changelog.rst`
  — full/relevant reads
- `typsphinx/__init__.py` (version-derivation lines), `.venv` dist-info/editable-pth listing — read
  and directory-listed this session
- `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
  `tests/test_changelog_page_gate.py`, `tests/test_docs_contract_claims_gate.py`,
  `tests/test_corpus_gate.py` (partial), `tests/test_extension.py` (relevant slice) — full/relevant
  reads
- `scripts/extract_changelog_section.py`, `.github/workflows/release.yml`,
  `.github/workflows/ci.yml` (relevant slice) — full/relevant reads
- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md`
  (full), `41-RELEASE-EVIDENCE.md` (heading structure + excerpts)
- `.planning/todos/pending/2026-08-11-windows-path-separator-breaks-contract-claims-gate.md` — full
  read
- Live command executions this session: `uv lock --check`, `tox -e lint`, `tox -e docs-html`,
  `tox -e docs-pdf`, `tox -e py312`/`py313` (both, contrasting outcomes),
  `pytest tests/test_corpus_gate.py -v`, `pytest tests/test_docs_contract_claims_gate.py -v`,
  `git merge-tree --write-tree HEAD origin/main`, `git show HEAD:CHANGELOG.md` /
  `git show origin/main:CHANGELOG.md`, `git diff v0.7.0..HEAD -- pyproject.toml`,
  `grep -rln '@preview/' …`, version probes for `uv`/`tox`/`sphinx`/`docutils`/`typst`/`pytest`/
  `pypdf`/`gh`/`git`/`myst_parser` (absence confirmed).

### Secondary (MEDIUM confidence)

- None — this phase required no external web research; every claim traces to this repository's own
  files or this session's own command executions.

### Tertiary (LOW confidence)

- The exact `docs/source/conf.py` mechanism for D-12's `ja` build (Open Question 1, Assumption A2) —
  not read this session, flagged explicitly rather than guessed with false confidence.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, every version number directly probed this session.
- Architecture (release mechanics): HIGH — every command shape either executed this session or
  reasoned from a fully-read source file with line numbers cited.
- Pitfalls: HIGH for Pitfalls 1/2/4 (all directly reproduced this session); HIGH for Pitfall 3's
  factual measurement, with an explicit, honest flag that it partially contradicts `46-CONTEXT.md`'s
  own framing (not a locked decision — a factual premise stated in passing).
- Version-bump procedure (Pattern 1): MEDIUM-HIGH — the individual primitives are verified working,
  but the full sequence was deliberately not executed end-to-end against a live mutation this
  session, to avoid mutating the shared repository state.
- `ja` build mechanism (D-12): LOW — explicitly flagged as an open question, not guessed.

**Research date:** 2026-08-11
**Valid until:** This phase itself supersedes this research once it executes (the tree state
measured here — `origin/main` four commits ahead, `.venv` post-Phase-45.2, `git tag -l v0.7.1` empty —
is exactly the phase's own starting precondition). Treat as valid until Phase 46's first plan begins
execution; re-verify any command shape whose underlying file this phase itself edits (`CHANGELOG.md`,
`pyproject.toml`, `uv.lock`, `README.md`, `docs/source/changelog.rst`,
`tests/test_docs_contract_claims_gate.py`, `tests/test_changelog_page_gate.py`) before relying on its
pre-edit line numbers.
