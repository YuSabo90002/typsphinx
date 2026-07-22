---
phase: 23-v0-6-2-release-prep-regression-gate-close
record_type: execution-evidence
status: evidence-only
execution_date: 2026-07-23
plan: 23-02
---

# Phase 23 Plan 02 — Execution Evidence

**This file is an execution-time evidence record, NOT a verification verdict.** `/gsd-verify-work` owns
the verdict for this phase and will regenerate this exact filename with its own report when it runs. Per
D-10, all gate evidence for this phase is aggregated here rather than into a separate `23-GATE.md` file
(no such file exists or is created by this plan).

## Corpus Gate Raw Evidence (SC#3, D-09/D-12)

Command run (per plan Task 1, with `-s` added on the second invocation solely to surface the test's
own `print()` calls — no code was added to `tests/test_corpus_gate.py`; the first invocation below is the
literal command the plan specifies verbatim, the second is that same node id with `-s` appended to
capture the `Unknown Visit Catalogue:` line that pytest suppresses on a passing test by default):

```
$ uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [100%]

============================== 1 passed in 14.10s ==============================
```

```
$ uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
PASSED

============================== 1 passed in 12.90s ==============================
```

**Verdict facts, mechanically confirmed:**

- The final summary line reads `1 passed` (both runs) — the word "passed", not "skipped".
- `grep -c 'SKIPPED'` over both captured logs returns `0` — zero SKIPPED lines anywhere.
- The node id `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
  is followed by `PASSED` in both runs.
- Elapsed time is `14.10s` and `12.90s` respectively — well inside the plausible 10-25s real-build range
  (a skip would be near-instant, sub-second).
- The `Unknown Visit Catalogue:` line reads `[]` — an empty list. No node type was silently dropped.
- `git status --porcelain tests/test_corpus_gate.py` returned empty (0 lines) — the gate file was not
  modified to make this pass.
- `git tag --list 'v0.6.2'` returned empty both before and after this run.

**Conclusion: SC#3 is satisfied and demonstrably PASSED, not skipped.** The corpus at
`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` (confirmed present and cache-hit, no network clone
needed) compiled through `-b typstpdf` fatal-free, produced a valid `%PDF`-magic-byte output, and the
`unknown_visit` catalogue is clean.

## Milestone Invariant Evidence (SC#4)

### Check 1 — Zero new runtime dependencies

```
$ git diff v0.6.1..HEAD -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index 9682f71..5cbcec3 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"
 
 [project]
 name = "typsphinx"
-version = "0.6.1"
+version = "0.6.2"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
@@ -119,8 +119,8 @@ ignore = [
     "E501",   # Line too long (handled by black)
     "T201",   # print found (used in tests for debugging)
     "B017",   # asserting blind exception in tests
-    "UP035",  # typing.Dict/List/Set deprecation (Python 3.10+ support)
-    "UP006",  # Use dict instead of Dict (Python 3.10+ support)
+    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
+    "UP006",  # Use dict instead of Dict; same deferral as UP035 above
     "UP028",  # yield from (minor optimization)
     "N802",   # Function naming (docutils visitor pattern uses PascalCase)
     "A001",   # Shadowing builtins (copyright in conf.py is Sphinx convention)
```

**Verdict:** The only substantive changes in the whole file since `v0.6.1` are (a) the `version` literal
bump `0.6.1` → `0.6.2` (this milestone's own version bump, plan 23-01) and (b) two ruff `ignore` list
comment-text edits (`UP035`/`UP006`) clarifying the deferral rationale — no ignore code was added or
removed, only the trailing comment prose changed. **The `dependencies = [...]` array itself is untouched**
— no line was added, removed, or modified inside it. Zero new runtime dependencies confirmed.

### Check 2 — No `@preview` version bump

```
$ git diff v0.6.1..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ | grep -E '^[+-].*@preview'
(no output)
```

**Verdict:** Empty output — no line touching an `@preview/...` string was added or removed in any of the
three declaration sites since `v0.6.1`. Per the research's cited interpretation, this does not require the
three files to be byte-identical overall (`typsphinx/writer.py` legitimately changed in Phase 22.1 for an
unrelated fix); it isolates only `@preview` version lines, which is the correct reading of "3-way surface
untouched."

### Check 3 — 3-way version-sync surface still in lockstep

```
$ uv run python -m pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python3
plugins: cov-7.1.0
collected 2 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 50%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [100%]

============================== 2 passed in 0.02s ===============================
```

**Verdict:** 2 passed. Together with Check 2, this is sufficient proof of SC#4's `@preview` half per
Claude's Discretion in `23-CONTEXT.md` — no additional tooling built.

### Check 4 — 23-01's outputs still hold at this point in the wave sequence

```
$ uv sync --extra dev --locked
Resolved 88 packages in 0.63ms
Checked 80 packages in 0.55ms
$ echo "EXIT=$?"
EXIT=0
```

```
$ uv run python -m pytest tests/test_readme_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python3
plugins: cov-7.1.0
collected 1 item

tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [100%]

============================== 1 passed in 0.01s ===============================
```

Combined run (matches the plan's acceptance criterion wording "3 passed"):

```
$ uv run python -m pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python3
plugins: cov-7.1.0
collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [100%]

============================== 3 passed in 0.02s ===============================
```

**Verdict:** `uv sync --extra dev --locked` exits 0 (no drift) and `tests/test_readme_version_sync.py`
passes, confirming 23-01's version-bump and README-sync deliverables still hold at this point in the wave
sequence.

**SC#4 overall verdict: satisfied.** Zero new runtime dependencies, no `@preview` version bump, 3-way
version-sync surface still in lockstep, and 23-01's prior outputs hold.

## Scope Fence Evidence (SC#5)

### Check 5 — No `v0.6.2` tag exists

```
$ git tag --list 'v0.6.2'
(no output)
```

### Check 6 — `.github/workflows/release.yml` untouched since `v0.6.1`

```
$ git diff v0.6.1..HEAD -- .github/workflows/release.yml
(no output)
```

### Check 7 — No release-workflow commit landed

```
$ git log --oneline v0.6.1..HEAD -- .github/workflows/
(no output)
```

**Verdict:** No git tag named `v0.6.2` (or any other tag) was created or pushed by this plan. No PyPI
upload, no GitHub Release creation, and no manual or scripted trigger of `.github/workflows/release.yml`
occurred — the workflow file is byte-identical to `v0.6.1` and no commit under `.github/workflows/`
landed in the 301+ commits since that tag. All publish steps remain deferred to
`/gsd-complete-milestone`, exactly as SC#5 requires.

## Note on this file's lifecycle

Per D-10, this project aggregates regression-gate evidence into the phase's `23-VERIFICATION.md` rather
than a separate `23-GATE.md` report file (the Phase 18 / v0.6.1 GATE-03 precedent, confirmed at
`.planning/milestones/v0.6.1-phases/18-fidelity-fixes-regression-gate-close/18-VERIFICATION.md`).
`/gsd-verify-work` writes its own verification report to this exact same filename later in the phase's
lifecycle and may overwrite this content entirely — that is expected and by design (this file's own
frontmatter declares `status: evidence-only`, not a verdict). Because this filename is not
non-clobberable, `23-02-SUMMARY.md` carries a duplicate verbatim copy of the same corpus-gate log as the
durable, executor-owned record that survives any later overwrite of this file.
