# Phase 41 Plan 01 — REL-04 Evidence

This file records SC#1's live-run demonstration and the D-09 job-graph proof for REL-04, per
`41-01-PLAN.md` Task 3. Every command below was re-run live during this plan's execution
(2026-08-03), inside this plan's isolated git worktree, after `unset VIRTUAL_ENV
UV_PROJECT_ENVIRONMENT; uv sync --extra dev` and symlinking a working `uv`/`ruff` binary into
`.venv/bin/` (the standing NixOS dynamic-linker shim `CLAUDE.md` documents), with every command
invoked through `uv run`.

**Filename note:** this file is deliberately not named `41-VERIFICATION.md` — that name is reserved
by the `/gsd-verify-work` verifier and would be clobbered wholesale when it runs (per `41-CONTEXT.md`
Claude's Discretion). `35-RELEASE-EVIDENCE.md` is the recorded precedent for this naming choice.

**Explicit non-execution statement (D-07's own instruction, read literally):** `.github/workflows/
release.yml` itself was **not executed** during this plan. It cannot run outside a real tag push
(`on: push: tags: 'v*'`) or a `workflow_dispatch` invocation, and triggering either is forbidden by
this plan's own `<prohibitions>` fence (no `git tag`, no tag push, no `workflow_dispatch`). Every
claim below about the workflow's *behavior* is either (a) a direct hand-run of the same script the
workflow calls (SC#1), or (b) a static read of the workflow file's own YAML structure (D-09). Neither
is a workflow execution, and this is recorded honestly rather than glossed over — a skip is not a
pass.

---

## SC#1 — the extraction executed against the real file for a real version (D-07)

**Claim:** `scripts/extract_changelog_section.py`, run directly (not through the workflow), extracts
`CHANGELOG.md`'s real `## [0.6.5]` section on success and fails loudly, naming the version, on an
absent version.

### Step 1 — a real, already-released version (`0.6.5`)

Command:
```
$ uv run python scripts/extract_changelog_section.py 0.6.5
```
Verbatim stdout:
```
Fixes a compile-blocking defect where a document mixing prose and math could abort the Typst
compile: inline and display math no longer emit without a valid separator from surrounding text.
The runtime change is confined to the math handlers in `typsphinx/translator.py` — both the inline
and the display-math visitor gained separator participation — with no other file under `typsphinx/`
touched. Zero new runtime dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed

- **Inline math immediately after text no longer aborts the `typstpdf` compile (MATH-01)** — in
  bullet-list items, definition-list terms, and the like (including display math inside a list
  item, which is the same user-visible change), a missing separator between the preceding text
  emission and the `mi(...)` / `$...$` call previously produced Typst that failed to compile. Fixed
  on both emission paths — the mitex default and the native path.

### Verified

- Zero new runtime dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.
```
Exit code: **0**.

### Step 2 — an absent version (`9.9.9`)

Command:
```
$ uv run python scripts/extract_changelog_section.py 9.9.9
```
Verbatim stdout:
```
(empty)
```
Verbatim stderr:
```
No '## [9.9.9]' section found in the CHANGELOG. Add a curated entry for this version before releasing.
```
Exit code: **1**.

### SC#1 (D-07) verdict

**MET.** The extractor's success and failure paths were both hand-run against the real repository
tree: `0.6.5` extracts its curated section on stdout (exit 0), and `9.9.9` — a version absent from
`CHANGELOG.md` — prints nothing to stdout, names the requested version in stderr, and exits non-zero
(exit 1). This is the same script `release.yml` calls from both jobs (D-06); no separate
demonstration path exists.

The same six-case pytest contract (`tests/test_changelog_extraction.py`) additionally passed 6/6
during this plan's Task 1/Task 2 execution, covering the adjacency, empty-section, and ordering edge
cases beyond what this hand-run demonstrates directly.

---

## SC#1 — the commit dump is removed, not fenced off

**Claim:** the `create-release` job's `Generate release notes` step no longer contains the
`git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` dump or its `PREV_TAG`/`if`/`else`/`fi`
scaffolding, with no surviving fallback branch anywhere in the file.

### The whole-plan diff of `.github/workflows/release.yml`

Command:
```
$ git diff -- .github/workflows/release.yml
```
(captured immediately before staging Task 3's commit, so this is the exact diff that commit
contains)

Verbatim diff:
```diff
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
index 7e6ed2f..c8ff50f 100644
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -58,6 +58,14 @@ jobs:
             exit 1
           fi

+      - name: Verify CHANGELOG has a section for this version
+        run: |
+          VERSION="${{ steps.version.outputs.version }}"
+          if ! uv run python scripts/extract_changelog_section.py "$VERSION" >/dev/null; then
+            echo "::error::CHANGELOG.md has no usable '## [$VERSION]' section -- add a curated release-notes entry before tagging."
+            exit 1
+          fi
+
       - name: Run tests
         run: uv run pytest tests/ -v

@@ -154,17 +162,9 @@ jobs:
         run: |
           TAG="${{ steps.version.outputs.tag }}"

-          # Get previous tag
-          PREV_TAG=$(git describe --tags --abbrev=0 $TAG^ 2>/dev/null || echo "")
-
-          # Generate changelog
-          if [ -n "$PREV_TAG" ]; then
-            echo "## Changes since $PREV_TAG" > release_notes.md
-            echo "" >> release_notes.md
-            git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)" >> release_notes.md
-          else
-            echo "## Initial Release" > release_notes.md
-          fi
+          # Curated release-notes body, sourced from CHANGELOG.md's own
+          # `## [X.Y.Z]` section (REL-04) -- not a `git log` commit dump.
+          uv run python scripts/extract_changelog_section.py "${TAG#v}" > release_notes.md

           echo "" >> release_notes.md
           echo "## Installation" >> release_notes.md
```

### Repo-wide search for surviving dump-generator fragments

Command:
```
$ grep -n 'PREV_TAG\|git log \$PREV_TAG\|Changes since\|Initial Release' .github/workflows/release.yml
```
Verbatim output:
```
(empty — grep exit code 1, no match)
```

Command (confirming no residual `git log`/`git describe` invocation anywhere in the replaced step):
```
$ sed -n '/Generate release notes/,/Create GitHub Release/p' .github/workflows/release.yml | grep -n 'git log\|git describe'
```
Verbatim output:
```
7:          # `## [X.Y.Z]` section (REL-04) -- not a `git log` commit dump.
```
The single hit is the new step's own explanatory comment (prose referencing what was removed), not
an invocation — confirmed by inspection: no `git log` or `git describe` command executes anywhere in
the current `Generate release notes` step.

### SC#1 (dump removal) verdict

**MET.** The `PREV_TAG` lookup, the `if [ -n "$PREV_TAG" ]` / `else` / `fi` branch, and the
`git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` line are all deleted in this same diff, replaced
by a single call to the committed extractor. No conditional, `||` fallback, or dead branch retains the
old dump path — the repo-wide grep for its constituent fragments (`PREV_TAG`, `Changes since`,
`Initial Release`) returns zero hits.

---

## D-09 — the check runs before the publish

**Claim:** the new `Verify CHANGELOG has a section for this version` step runs in the `validate` job,
and the job `needs:` graph provably runs `validate` before `build`, `publish-pypi`, and
`create-release` — so a missing CHANGELOG section fails before any PyPI upload.

### Step ordering within the `validate` job

Command:
```
$ grep -n 'Verify version matches pyproject.toml\|Verify CHANGELOG has a section\|Run tests' .github/workflows/release.yml
```
Verbatim output:
```
50:      - name: Verify version matches pyproject.toml
61:      - name: Verify CHANGELOG has a section for this version
69:      - name: Run tests
```
Line 61 sits strictly between line 50 (the existing version-vs-pyproject.toml check) and line 69
(the first step after it, `Run tests`) — the new step is positioned immediately after the existing
"verify before publishing" precedent and before any test/lint/type-check step.

### The job `needs:` graph, transcribed with line numbers

Command:
```
$ grep -n '^  [a-z].*:\|needs:' .github/workflows/release.yml
```
Verbatim output (job-name and `needs:` lines only):
```
19:  validate:
81:  build:
83:    needs: validate
115:  publish-pypi:
117:    needs: build
135:  create-release:
137:    needs: [build, publish-pypi]
190:  publish-testpypi:
192:    needs: build
```
Read directly from the file: `validate` (line 19) carries no `needs:` key at all (it is the graph's
root); `build` (line 81) needs `validate` (line 83); `publish-pypi` (line 115) needs `build` (line
117); `create-release` (line 135) needs both `build` and `publish-pypi` (line 137).

### Mechanized corroboration (structural YAML parse)

Command:
```
$ uv run python -c "
import yaml
d = yaml.safe_load(open('.github/workflows/release.yml'))
n = d['jobs']
assert 'needs' not in n['validate']
assert n['build']['needs'] == 'validate'
assert n['publish-pypi']['needs'] == 'build'
assert set(n['create-release']['needs']) == {'build', 'publish-pypi'}
print('job graph ok (yaml)')
"
```
Verbatim output:
```
job graph ok (yaml)
```
`pyyaml` is available in this environment's `dev` extra (a transitive dependency), so the four facts
above were asserted mechanically via a structural YAML parse rather than by reading the file alone.

### Why this ordering is the mitigation

`validate` has no incoming dependency (GitHub Actions runs it first for this workflow); `build`
cannot start until `validate` succeeds; `publish-pypi` (the irreversible external side effect) cannot
start until `build` succeeds; `create-release` cannot start until both `build` and `publish-pypi`
succeed. Since the new "Verify CHANGELOG has a section for this version" step is one of `validate`'s
own steps (and `validate`'s steps run sequentially, each gating the next — a non-zero exit from any
step, including this new one, fails the whole job), a missing or empty `## [X.Y.Z]` section now fails
inside `validate`, before `build` runs, before `publish-pypi` uploads to PyPI, and before
`create-release` would have produced a GitHub Release from a bad or absent body. This is exactly the
"published to PyPI but no GitHub Release" failure mode D-09 exists to prevent — the check that used
to not exist at all now runs at the earliest possible point in the graph.

### D-09 verdict

**MET.** The step-ordering grep and the job `needs:` graph (both a direct file read and a mechanized
YAML parse) together prove the existence check runs in `validate`, strictly before `build`,
`publish-pypi`, and `create-release` can execute.

---

## Overall verdict

All three sections above are MET. `release.yml` itself was not executed (explicitly recorded, not
glossed over) — SC#1's demonstration is a direct hand-run of the committed extractor, and D-09's
proof is a structural read of the workflow's own job graph, both fully sufficient for what this
plan's success criteria ask for without requiring a real tag push.
