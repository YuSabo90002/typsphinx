# Phase 33: v0.6.4 Release Prep — Release Evidence

This file records SC#3 and SC#4 of ROADMAP Phase 33, with verbatim command output backing every
claim. Every command below was re-run during this plan's execution (2026-07-28); no figure is
carried forward from `33-CONTEXT.md`, `33-RESEARCH.md`, or `33-PATTERNS.md` as evidence — those
documents are inputs to be re-verified, not evidence themselves.

**Filename note:** this file is deliberately not named `33-VERIFICATION.md` — that name is
reserved by the `/gsd-verify-work` verifier, which overwrites it wholesale.

---

## SC#3: `Documentation` metadata URL — real HTTP re-verification

**Claim:** `pyproject.toml`'s `[project.urls] Documentation` value resolves over real HTTP to a
2xx terminal status on the prepared tree.

### Step 1 — parse the URL from `pyproject.toml` (not assumed, not quoted from a planning doc)

Command:
```
$ uv run python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['urls']['Documentation'])"
```

Verbatim output:
```
https://typsphinx.readthedocs.io/
```

This confirms the value in the prepared tree's `pyproject.toml` is the one fetched below. Phase 31
already set this value to the Read the Docs root; this plan makes no edit to it (confirmed by the
SC#4 `git diff main..HEAD -- pyproject.toml` section below, which shows only the version-bump
hunk — no `[project.urls]` change from this phase).

### Step 2 — un-followed fetch (records the redirect status and `Location`)

Command:
```
$ curl -s -o /dev/null -w "HTTP_CODE:%{http_code}\nLOCATION_HEADER_FOLLOWS\n" -D - "https://typsphinx.readthedocs.io/"
```

Verbatim output (headers, truncated to the load-bearing lines — full response included
cookies/CDN headers omitted here for brevity, none of which affect the verdict):
```
HTTP/2 302
date: Mon, 27 Jul 2026 21:15:25 GMT
content-type: text/html; charset=utf-8
content-length: 0
location: https://typsphinx.readthedocs.io/en/latest/
x-rtd-project: typsphinx
x-rtd-project-method: public_domain
x-rtd-redirect: system
x-rtd-version-method: path
server: cloudflare

HTTP_CODE:302
```

### Step 3 — followed fetch (records the terminal status code and effective URL)

Command:
```
$ curl -s -L -o /dev/null -w "TERMINAL_HTTP_CODE:%{http_code}\nEFFECTIVE_URL:%{url_effective}\nREDIRECT_COUNT:%{num_redirects}\n" "https://typsphinx.readthedocs.io/"
```

Verbatim output:
```
TERMINAL_HTTP_CODE:200
EFFECTIVE_URL:https://typsphinx.readthedocs.io/en/latest/
REDIRECT_COUNT:1
```

### Verdict

**SC#3: MET.** The `Documentation` URL parsed live from the prepared tree's `pyproject.toml`
(`https://typsphinx.readthedocs.io/`) redirects once (302 → `location:
https://typsphinx.readthedocs.io/en/latest/`, `x-rtd-project: typsphinx` confirming this is the
correct RTD project) and terminates at HTTP 200 on `https://typsphinx.readthedocs.io/en/latest/`.
This is a 2xx terminal status, so SC#3 is met with an honest, freshly-taken verdict.

### Observation timestamp

**2026-07-27T21:15:32Z** (ISO-8601, UTC). This is a point-in-time observation of a live external
service (Read the Docs), not a fact this repository holds any re-verification mechanism for.

### Deliberately excluded from CHANGELOG.md

Per D-03 (`33-CONTEXT.md`), this live-serving observation is **not** recorded in `CHANGELOG.md`.
The project's `### Verified` CHANGELOG convention (plan 33-02) is restricted to invariants a `git
diff` can mechanically re-prove at any future point; a point-in-time HTTP fetch against an external
service has no standing re-verification mechanism and would go stale the moment RTD's content or
routing changes. It is recorded here, in this dated evidence file, instead.

---

## SC#4: Milestone invariants asserted over the full milestone diff

**Claim:** the three milestone invariants — zero new runtime dependencies, no `@preview` package
version bump across the four version-sync surfaces, and zero changes under `typsphinx/` — hold
over the **full milestone diff** (`main..HEAD`), not merely this phase's diff. Every command below
was re-run during this task; per Milestone Invariant #4, no count is carried forward from any
planning document — the commit count has already drifted three times across this phase's own
artifacts (254 at discussion, 256 at research, 258 at planning) as completion commits accumulated.

### Diff range re-measurement (source of truth for this section)

Command:
```
$ git merge-base main HEAD
```
Verbatim output:
```
771ec56fa3e9a863ac0bca865476bdc423fbb3e7
```

Command:
```
$ git log --oneline main..HEAD | wc -l
```
Verbatim output:
```
279
```

The merge-base SHA (`771ec56f`) matches the figure recorded in `33-CONTEXT.md`'s `## Specific
Ideas` table (measured at discussion time); the commit count has drifted again since planning
(258 → 279) as this phase's own task commits (33-01, 33-02, 33-03, and this plan's own tasks)
landed on the branch — exactly the drift the invariant anticipates.

### Invariant 1 of 3 — zero changes under `typsphinx/`

Command:
```
$ git diff main..HEAD --stat -- typsphinx/
$ echo "EXIT_CODE:$?"
```
Verbatim output:
```
EXIT_CODE:0
```
Output was empty (no lines printed by `git diff --stat`) and the command's own exit status was 0
(success — the command ran and matched, it did not error). **This empty result is the invariant
PASSING**: it means the pathspec `typsphinx/` matched zero changed files across the full milestone
diff, not that the check was skipped or the command failed to run.

**Positive control** (proves the diff range and pathspec machinery is actually working — an empty
result on a broken pathspec would look identical to a genuine pass without this control):
```
$ git diff main..HEAD --stat -- pyproject.toml
```
Verbatim output:
```
 pyproject.toml | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```
Non-empty, as expected — `pyproject.toml` is known to have changed (the `Documentation` URL in
Phase 31, the version bump in plan 33-01). This proves `git diff main..HEAD --stat -- <pathspec>`
is a working comparison against the correct range, so the `typsphinx/` empty result above is a
genuine pass, not a silently-broken check.

**Invariant 1: PASS.**

### Invariant 2 of 3 — zero new runtime dependencies

Command:
```
$ git diff main..HEAD -- pyproject.toml
```
Verbatim full diff:
```diff
diff --git a/pyproject.toml b/pyproject.toml
index 79e28c3..e101643 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"
 
 [project]
 name = "typsphinx"
-version = "0.6.3"
+version = "0.6.4"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
@@ -53,7 +53,7 @@ docs = [
 
 [project.urls]
 Homepage = "https://github.com/YuSabo90002/typsphinx"
-Documentation = "https://github.com/YuSabo90002/typsphinx#readme"
+Documentation = "https://typsphinx.readthedocs.io/"
 Repository = "https://github.com/YuSabo90002/typsphinx"
 Issues = "https://github.com/YuSabo90002/typsphinx/issues"
```
Exactly two hunks, as expected: the `version` bump (plan 33-01) and the `Documentation` URL
(Phase 31, already in place before this phase — see SC#3 above, which confirms this phase made no
further edit to it). No line inside `dependencies` or `optional-dependencies` changed.

Command:
```
$ git diff main..HEAD --stat -- uv.lock
```
Verbatim output:
```
 uv.lock | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```
A single-line change (the typsphinx self-entry version, per plan 33-01's SUMMARY — no transitive
dependency line changed).

**Invariant 2: PASS.**

### Invariant 3 of 3 — no `@preview` package version bump

The four declaration surfaces are `typsphinx/writer.py`, `typsphinx/template_engine.py`,
`typsphinx/templates/base.typ`, and `examples/**/*.typ`. The first three are already covered by
the empty `typsphinx/` diff above (Invariant 1). The fourth surface is checked separately:

Command:
```
$ git diff main..HEAD --stat -- examples/
```
Verbatim output:
```
 examples/advanced/README.md | 4 ++--
 examples/basic/README.md    | 2 +-
 examples/basic/index.rst    | 2 +-
 3 files changed, 4 insertions(+), 4 deletions(-)
```
Non-empty, but on inspection (`git diff main..HEAD -- examples/`, read in full) every changed line
is a `github.io`/placeholder-URL rewrite in `README.md`/`index.rst` prose (Phase 31's URL cutover:
`your-repo/typsphinx` → `YuSabo90002/typsphinx`). Zero `.typ` files under `examples/` appear in
this diff, so no `@preview` import line was touched.

Command (provisioned per this project's standing worktree-isolated execution mode:
`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev`, then run through `uv run`):
```
$ uv run python -m pytest tests/test_preview_version_sync.py -v
```
Verbatim output:
```
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

3 passed in 0.01s
```

**Invariant 3: PASS.**

### SC#1 evidence, carried from plan 33-01 (`33-01-SUMMARY.md`)

- `typsphinx.__version__` probe (`uv run python -c "import typsphinx; print(typsphinx.__version__)"`)
  printed `0.6.4`.
- `git diff --numstat uv.lock` recorded `1  1  uv.lock` (single-line diff, no transitive movement).
- `tests/test_readme_version_sync.py` and `tests/test_preview_version_sync.py` together: 4 passed,
  0 failed.

### SC#2 evidence, carried from plan 33-02 (`33-02-SUMMARY.md`)

- The `## [0.6.4]` CHANGELOG entry resolved its date via `date -I` at execution time: `2026-07-28`
  (not copied from any planning document).
- Tail release/compare link block updated in the same plan: `[0.6.4]:
  https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4` inserted immediately above
  `[0.6.3]:`; the final `[Unreleased]:` line's compare base rewritten from `v0.6.3...HEAD` to
  `v0.6.4...HEAD`. No `v0.6.4` tag was created (confirmed by that plan's own empty
  `git tag -l v0.6.4`, and re-confirmed independently in the SC#5 section of `33-HANDOFF.md`).

### Full test suite

Baseline from `33-RESEARCH.md`: 647 passed / 1 skipped. Command (provisioned per this project's
standing worktree-isolated execution mode):
```
$ uv run python -m pytest -q
```
Verbatim tail output:
```
647 passed, 1 skipped in 56.79s
```
647 passed matches the baseline exactly (at or above it), 1 skipped matches, and there are zero
failures. **Suite: GREEN.**

### SC#4 verdict

**SC#4: MET.** All three milestone invariants hold over the freshly re-measured full milestone
diff (`main..HEAD`, merge-base `771ec56f`, 279 commits at measurement time): zero changes under
`typsphinx/` (with a working positive control proving the check itself is functioning), zero new
runtime dependencies (the `pyproject.toml` diff is exactly the two already-known hunks, `uv.lock`
a single self-entry line), and no `@preview` version bump on any of the four declaration surfaces
(the three `typsphinx/`-internal surfaces via Invariant 1, the `examples/` surface via an
inspected non-`.typ` diff plus a green `test_preview_version_sync.py`). The full test suite is
green at 647 passed / 1 skipped / 0 failed, at or above the research-session baseline.
