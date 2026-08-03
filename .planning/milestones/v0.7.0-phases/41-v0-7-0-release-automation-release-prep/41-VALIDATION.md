---
phase: 41
slug: v0-7-0-release-automation-release-prep
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 41 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by `/gsd-plan-phase` from `41-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (existing project dependency) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths=tests`, strict markers) |
| **Quick run command** | `uv run pytest tests/test_changelog_extraction.py -v` (new module — Wave 0) |
| **Full suite command** | `uv run pytest tests/` |
| **Estimated runtime** | quick ~2s · full suite several minutes (integration + PDF compile tests) |

**Worktree note (CLAUDE.md, mandatory):** every executor runs in an isolated git worktree and MUST
first run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then invoke every
command above through `uv run`. Without this, pytest imports the MAIN checkout's package and gates
stay RED after a correct fix.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_changelog_extraction.py -v` for tasks
  touching the extraction script; otherwise the nearest existing module
  (`tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`).
- **After every plan wave:** `uv run pytest tests/` plus the lint/type trio
  (`uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`).
- **Before `/gsd-verify-work`:** full suite must be green.
- **Max feedback latency:** ~5s for the quick gate.

**Phase-gate exception (SC#3).** The green-tree evidence run — full suite, lint/type trio,
full-corpus `-b typstpdf` gate, both docs dogfooding builds, and the `ja` four-check glyph bar —
is a **once, at the end, post-bump** requirement. It cannot be sampled incrementally: it validates
the tree AFTER the version bump and CHANGELOG entry land, not before.

---

## Per-Task Verification Map

*Seeded at plan time; task IDs are filled in by `/gsd-validate-phase` once PLAN.md task IDs exist.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | REL-04 | — | Version string reaches the extractor as a single quoted CLI arg, never an `eval`'d shell fragment | unit | `uv run pytest tests/test_changelog_extraction.py::test_extracts_real_version -x` | ❌ W0 (new, D-06) | ⬜ pending |
| TBD | TBD | 1 | REL-04 | — | Absent version fails loudly rather than emitting an empty release body | unit | `uv run pytest tests/test_changelog_extraction.py::test_absent_version_fails -x` | ❌ W0 (new, D-10) | ⬜ pending |
| TBD | TBD | 1 | REL-04 | — | `validate` job's existence check fires before `build`/`publish-pypi` (D-09) | manual (CI-only) | N/A — read `release.yml`'s `needs:` graph + SC#1 hand-run transcript (D-07) | N/A | ⬜ pending |
| TBD | TBD | 2 | REL-05 | — | N/A | unit (existing) | `uv run pytest tests/test_readme_version_sync.py -x` | ✅ | ⬜ pending |
| TBD | TBD | 2 | REL-05 | — | N/A | unit (existing) | `uv run pytest tests/test_preview_version_sync.py -x` | ✅ | ⬜ pending |
| TBD | TBD | 3 | REL-05 | — | N/A | integration | `uv run pytest tests/` | ✅ | ⬜ pending |
| TBD | TBD | 3 | REL-05 | — | N/A | integration | full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` gate | ✅ | ⬜ pending |
| TBD | TBD | 3 | REL-05 | — | N/A | integration | `uv run tox -e docs-html && uv run tox -e docs-pdf` | ✅ | ⬜ pending |
| TBD | TBD | 3 | REL-05 | — | Clone content is read-only input to `pypdf`, never executed (D-17) | manual | one-off `ja` four-check bar hand-run — NOT committed, per D-15/D-16 | N/A by design | ⬜ pending |
| TBD | TBD | 3 | REL-05 | — | N/A | manual | one-off SC#4 sweep (`git diff` over `51e02b6..HEAD` + handler census) — NOT committed, per D-07 | N/A by design | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/extract_changelog_section.py` — the `## [X.Y.Z]` extractor (D-06)
- [ ] `tests/test_changelog_extraction.py` — stubs for REL-04 covering both directions (D-10)
- [ ] No shared fixture/`conftest.py` changes anticipated — the extractor needs only `CHANGELOG.md`'s
      existing content, already present

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SC#1 "executed against the real file for a real version" | REL-04 | D-07 discharges it by a hand-run transcribed verbatim into the phase evidence file, not by a committed test | Run the extractor against the real `CHANGELOG.md` for a real version; paste command + input + output verbatim into `41-RELEASE-EVIDENCE.md` |
| `validate`-job existence check ordering | REL-04 | Cannot execute outside a real tag push; the job graph is the proof | Read `release.yml`'s `needs:` chain (`validate` → `build` → `publish-pypi` → `create-release`) and record it |
| `ja` glyph bar check 4 — owner visual confirmation | REL-05 (SC#3) | Typst font fallback is silent; checks 1–3 cannot detect substituted glyphs that extract as correct characters | Build `ja` docs from `main` and from `HEAD` locally (D-15); pick pages by measured CJK density (Phase 30.1 method); owner inspects and signs off (D-16, `39-ADM04-SIGNOFF.md` shape) |
| SC#4 invariant sweep | REL-05 | One-off mechanical sweep over a SHA-anchored range, not a standing test | Run the handler census + dependency diff + `@preview` sync-site check over `51e02b6..HEAD`; transcribe output |
| SC#5 "no irreversible action taken" | REL-05 | Proving absence — a test cannot assert it | `git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0` must BOTH be empty at phase close; transcribe both |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s for the quick gate
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
