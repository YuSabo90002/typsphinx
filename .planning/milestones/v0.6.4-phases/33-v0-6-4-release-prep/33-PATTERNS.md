# Phase 33: v0.6.4 Release Prep - Pattern Map

**Mapped:** 2026-07-28
**Files analyzed:** 8 (pyproject.toml, uv.lock, README.md, CHANGELOG.md, .planning/PROJECT.md,
.planning/ROADMAP.md, .planning/MILESTONES.md, .planning/STATE.md) + 1 new deliverable
(SC#5 handoff checklist, location at Claude's discretion)
**Analogs found:** 9 / 9 — this is a docs-only release-prep phase with a direct precedent
(Phase 28, v0.6.3) for every file touched. No `typsphinx/` source files are in scope
(milestone invariant #3), so the usual controller/service/component classification does not
apply — every file here is role=`config`/`doc` and data-flow=`transform` (in-place text
rewrite of a stable, well-understood surface).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` (`:7` version bump only) | config | transform | same file, Phase 28 diff (`0.6.2`→`0.6.3`) | exact |
| `uv.lock` (`:1379` self-entry version) | config (lockfile) | transform | same file, Phase 28 `uv lock` regen | exact |
| `README.md` (`:317` Status line) | doc | transform | same file, Phase 28 diff (`:315` in old line numbering) | exact |
| `CHANGELOG.md` (new `## [0.6.4]` entry + tail link block) | doc | transform | `## [0.6.3]` entry in same file (lines 10–40) | exact |
| `.planning/PROJECT.md` (D-05 JA→EN, 108 lines) | doc (planning) | transform | own file's existing English Key Decisions prose (e.g. `:223-224`) as the target register | exact (self-referential) |
| `.planning/ROADMAP.md` (D-05 JA→EN, 10 lines) | doc (planning) | transform | own file's existing English phase-summary prose | exact (self-referential) |
| `.planning/MILESTONES.md` (D-05 JA→EN, 1 line, `:3` heading) | doc (planning) | transform | own file's existing English milestone headings (other entries, if any) | exact (self-referential) |
| `.planning/STATE.md` (D-05 JA→EN, 1 line, `:292`) | doc (planning) | transform | own file's existing English Deferred-Items table rows | exact (self-referential) |
| SC#5 handoff checklist (new file/section) | doc | transform | `.planning/phases/33-.../` specifics list already drafted in `33-CONTEXT.md` §specifics (8 numbered items) | exact |

## Pattern Assignments

### `pyproject.toml`

**Analog:** same file at the Phase 28 (v0.6.3) bump commit.

**Core transform pattern** (Phase 28 diff, reproduced verbatim from `33-RESEARCH.md` Code Examples):
```diff
 [project]
 name = "typsphinx"
-version = "0.6.3"
+version = "0.6.4"
```
Only `pyproject.toml:7`'s `version` key changes. `Documentation` metadata under
`[project.urls]` (`:54-58`) is already the RTD URL from Phase 31 — do not touch it; SC#3 is a
re-verification (`curl`), not an edit. `dependencies`/`optional-dependencies` arrays are
out of scope entirely (milestone invariant: zero new runtime deps).

**Follow-up command pattern** (Pitfall 1/3 in RESEARCH.md — mandatory after the edit, not optional):
```bash
uv lock                              # updates uv.lock's typsphinx self-entry
uv sync --extra dev --locked         # regenerates editable-install metadata (.egg-info/.dist-info/.pth)
uv run python -c "import typsphinx; print(typsphinx.__version__)"  # must print 0.6.4
```

---

### `uv.lock`

**Analog:** same file, self-entry at `:1379` (`version = "0.6.3"`).

**Core transform pattern:** Do not hand-edit. Run `uv lock` after the `pyproject.toml` bump;
verify the single-line diff:
```bash
git diff pyproject.toml uv.lock
# expect: pyproject.toml 1-line version bump; uv.lock: typsphinx self-entry version line only
# (no transitive dependency lines should change)
```

---

### `README.md`

**Analog:** same file, Status line (currently `:317`).

**Core transform pattern** (verbatim target, mirrors Phase 28's `:315`→`:317` line shift is
expected as the file grows — always grep for the current line number rather than trusting a
stale offset):
```diff
-**Status**: Stable (v0.6.3) - Production ready
+**Status**: Stable (v0.6.4) - Production ready
```

**Guarding test** (`tests/test_readme_version_sync.py`, full text read):
- Regex `_STATUS_LINE_RE = re.compile(r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)")`
  extracts the README version; `_extract_pyproject_version()` parses `pyproject.toml` via
  `tomllib`. `test_readme_status_version_matches_pyproject` asserts equality. Both files must
  be bumped in the same commit/task or this test goes red.

---

### `CHANGELOG.md`

**Analog:** the `## [0.6.3]` entry in the same file (lines 8–40), the most recent precedent
matching Keep-a-Changelog section ordering (Added/Changed/Removed/Fixed) that D-04 extends
with a 5th `Verified` section.

**Structure to copy** (verbatim excerpt, lines 8–15 read directly):
```markdown
## [Unreleased]

## [0.6.3] - 2026-07-25

Closes out the config & docs fidelity milestone: configuration values documented in `typst_elements`
now reliably reach the compiled Typst output ...
```
`## [0.6.4]` is inserted directly beneath `## [Unreleased]` and above `## [0.6.3]`, following
the same "lead paragraph → `### Added` → `### Changed` → `### Removed` → `### Fixed`" shape,
with a new `### Verified` section appended per D-03/D-04. **RESEARCH.md already contains a
complete drafted `[0.6.4]` entry** (its "Code Examples" section) built from this exact
template — use it as the starting text rather than re-deriving structure from scratch. D-01
means this entry must contain **zero** `- **BREAKING: ...**` bullets (contrast with 0.6.3's
CONF-04/CONF-05 BREAKING bullets — do not copy that label).

**Requirement-ID citation style** (from the same `## [0.6.3]` block):
```markdown
- **Captioned tables render as numbered, cross-referenceable figures (TBL-01, TBL-02)** — ...
```
Bold lead-in naming the user-visible change, requirement IDs in parens immediately before the
em-dash.

**Tail link block** (verbatim, last 16 lines of file, read directly):
```
[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
[0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.3...HEAD
```
Two edits: insert `[0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4`
immediately above the `[0.6.3]:` line, and rewrite the `[Unreleased]:` line's compare target
from `v0.6.3...HEAD` to `v0.6.4...HEAD`. The new `[0.6.4]` link will 404 until
`/gsd-complete-milestone` cuts the tag — this is the same transient state Phase 28/23/10 all
passed through and is an accepted project convention, not a defect to fix here.

---

### `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/MILESTONES.md`, `.planning/STATE.md` (D-05)

**Analog:** no external analog needed — this is meaning-preserving translation of existing
prose, not new-pattern authorship. The "pattern" to copy is the **surrounding English prose
register already present in each file** (e.g. `PROJECT.md`'s own Key Decisions bullets at
`:223-224`, `:341-360`, all of which are English prose describing the same kind of technical
decision) — new translations should match that voice, not introduce a different one.

**Discovery command (mandatory, do not trust CONTEXT.md's line counts — RESEARCH.md Pitfall 2
proved a 2-file divergence)**:
```bash
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/PROJECT.md
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/ROADMAP.md
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/MILESTONES.md
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/STATE.md
```
Re-run at plan/execution time — RESEARCH.md documented that `ROADMAP.md` and `MILESTONES.md`
counts had already drifted between the discuss session and the research session (12→10 and
11→1 respectively). `MILESTONES.md`'s sole match is a heading (`:3`,
`## v0.6.3 config & docs 実測整合 + captioned tables (Shipped: 2026-07-25)`) — translate the
Japanese words in place, keep the structural Markdown/date format untouched.

**HTML-comment gotcha (Pitfall 5):** `PROJECT.md`'s `<!-- Prior: ... -->` footer comments
(read directly at `:341-362` above) contain Japanese prose that grep catches but casual
visual/rendered scanning misses (GitHub does not render HTML comments). These lines are
in scope for D-05 — CONTEXT.md's "no rendering-visibility exclusion" applies. Translate the
Japanese clauses inside the comments too, preserving the comment delimiters, the
`Prior: *Last updated: ... Prior footer retained below.*` wrapping convention, and all
non-Japanese structural content (dates, phase numbers, requirement IDs) unchanged.

**Non-goals per CONTEXT.md D-05:** do not alter YAML frontmatter, progress-table cell
structure, or any handler-managed field — translate only the Japanese textual content in
place; this is D-05's "content-unchanged, translation-only" boundary.

---

### SC#5 handoff checklist (new deliverable)

**Analog:** `33-CONTEXT.md` §specifics already contains the complete 8-item content list
(reproduced below); no other repo file has this exact shape (it's new to this phase), so the
"pattern" is really "assemble a checklist from already-decided content," not "copy structure
from an existing checklist file."

**Content to copy verbatim (order and substance), from `33-CONTEXT.md` lines 205–218:**
```
1. PR #124 ready 化 → マージ（/gsd-complete-milestone）
2. tag v0.6.4 push → release.yml → PyPI + GitHub Release
3. 翻訳リポジトリ typsphinx-doc-translations にも submodule バンプ + タグ
   (REL-02 standing cost, D-07 — /ja/stable/ はこちらのタグに解決)
4. 3 つの post-merge flip: 親 RTD Default branch → main / ja RTD Default branch → main /
   .gitmodules branch → main
5. tag ビルド緑の後: en Default Version latest → stable flip + ja プロジェクトの独立
   バージョンアクティベーション再確認 (/ja/stable/ が /en/stable/ と同一タグを指すこと)
6. Issue #119 クローズ (31-ISSUE-119-REPLY-DRAFT.md 使用、オーナーレビュー後)
7. git ls-remote で origin/gh-pages 不在の再確認 (Phase 32 の復活ハザード緩和、推奨)
8. 解決済み todo 2 件 (github.io 404 / orphan クラス) の pending/ からの整理
```
Given D-05 (public-facing English), this checklist — being a phase deliverable that may end
up merged to `main` — should be authored in English directly rather than translated after the
fact. Placement (a dedicated `33-HANDOFF.md` vs. a section inside `33-VERIFICATION.md`) is
explicitly Claude's discretion per CONTEXT.md.

## Shared Patterns

### Version-sync guard tests (apply to `pyproject.toml` + `README.md` together)
**Source:** `tests/test_readme_version_sync.py` (full file read, ~75 lines)
**Apply to:** any task that edits `pyproject.toml:7` or `README.md`'s Status line — the two
edits must land in the same commit/task, never split, or the suite goes red between them.
```python
_STATUS_LINE_RE = re.compile(
    r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)"
)
```
Run: `uv run python -m pytest tests/test_readme_version_sync.py -v`

### `@preview` 4-surface sync guard (apply as a no-op regression check, not an edit)
**Source:** `tests/test_preview_version_sync.py` (docstring + regex read, lines 1-60)
**Apply to:** SC#4's "no `@preview` bump" invariant claim — run this test as evidence, do not
touch `writer.py`/`template_engine.py`/`templates/base.typ`/`examples/**/*.typ`.
```python
_PREVIEW_IMPORT_RE = re.compile(
    r'#import\s+"@preview/(?P<name>[A-Za-z0-9_-]+):(?P<version>\d+\.\d+\.\d+)"'
)
```
Run: `uv run python -m pytest tests/test_preview_version_sync.py -v`

### Editable-install metadata resync (apply after any `pyproject.toml` version edit)
**Source:** `33-RESEARCH.md` Pattern 1 / Pitfall 1 (this session's direct `uv`/`.venv` probing)
```bash
uv lock
uv sync --extra dev --locked
uv run python -c "import typsphinx; print(typsphinx.__version__)"  # -> 0.6.4
```

### Milestone-invariant diff assertion (SC#4, applies once at phase end)
**Source:** `33-RESEARCH.md` Summary #1 (this session's `git diff` probing) + Phase 28
precedent (`28-VERIFICATION.md` pattern of recording live command output verbatim)
```bash
git merge-base main HEAD                       # expect 771ec56 (re-verify, may differ by session)
git log --oneline main..HEAD | wc -l           # re-verify count at execution time, do not trust CONTEXT.md's "254"
git diff main..HEAD --stat -- typsphinx/       # expect empty
git diff main..HEAD -- pyproject.toml          # expect only the Documentation URL line (already done) + version bump
```

## No Analog Found

None. Every file in scope has a direct same-file historical analog (its own prior version
bump, its own prior CHANGELOG entry, or its own existing English prose register). This is
expected for a prep-only release phase with an established Phase 28 precedent — there is no
genuinely new architectural pattern being introduced.

## Metadata

**Analog search scope:** `CHANGELOG.md`, `README.md`, `pyproject.toml`, `uv.lock`,
`tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
`.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/MILESTONES.md`, `.planning/STATE.md`,
`.planning/phases/28-v0-6-3-release-prep-regression-gate-close/` (Phase 28 precedent — note:
`28-PATTERNS.md` does not exist as a file in that phase directory; the Phase 28 CHANGELOG/
README/pyproject diffs themselves, and `28-VERIFICATION.md`'s recorded prose, served as the
analog instead).
**Files scanned:** 10
**Pattern extraction date:** 2026-07-28
