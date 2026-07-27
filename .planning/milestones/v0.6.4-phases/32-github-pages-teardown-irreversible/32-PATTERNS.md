# Phase 32: GitHub Pages Teardown (IRREVERSIBLE) - Pattern Map

**Mapped:** 2026-07-27
**Files analyzed:** 3 (1 workflow edit, 1 test-file addition, 1 doc-diff update) + evidence-only artifacts (no file)
**Analogs found:** 3 / 3

This phase is almost entirely CI/CD-config editing and remote git-state operations — there is
no application code. The "files" below are the only repo artifacts touched; everything else
(pre-teardown gate, `gh-pages` branch deletion, Settings→Pages toggle, draft-PR CI observation)
is a scripted evidence step with no corresponding source file, per RESEARCH.md's Validation
Architecture table.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|---------------|
| `.github/workflows/docs.yml` | config (CI workflow) | event-driven | itself (targeted text edit, not rewrite) | exact — edit in place |
| `tests/test_readthedocs_config.py` (new functions appended) | test | request-response (hermetic file-shape assertion) | `tests/test_readthedocs_config.py::test_build_python_matches_docs_workflow` (same file, existing raw-text-regex idiom) | exact |
| `.planning/codebase/INTEGRATIONS.md` | config/doc (planning artifact) | transform (diff update) | itself, `docs.yml` section (lines ~62-100, ~206-211) | exact — edit in place |

No controller/component/service/model/middleware files are in scope. Milestone invariant #3
(no `typsphinx/` runtime changes) confirmed by CONTEXT.md — nothing in that package is touched.

## Pattern Assignments

### `.github/workflows/docs.yml` (config, event-driven)

**Analog:** itself — this is a **targeted text edit**, not a new-file-from-template situation.
RESEARCH.md's Anti-Patterns section explicitly warns against a full YAML round-trip
(`yaml.safe_load` → mutate → `yaml.dump`) because it would reformat comments/quoting and produce
a noisy diff unrelated to CI-04's actual change. Use `Edit`'s old_string/new_string on the exact
two hunks below.

**Current full file** (verified 2026-07-27, RESEARCH.md Code Examples):
```yaml
name: Documentation

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs --locked
          uv pip install -e .

      - name: Build HTML documentation
        run: uv run tox -e docs-html

      - name: Build PDF documentation (English only)
        run: uv run tox -e docs-pdf

      - name: Upload HTML artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-html
          path: docs/_build/html

      - name: Upload PDF artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-pdf
          path: docs/_build/pdf/*.pdf

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
          cname: false

      - name: Upload PDF to Release
        if: startsWith(github.ref, 'refs/tags/v')
        uses: softprops/action-gh-release@v3
        with:
          files: docs/_build/pdf/*.pdf
          draft: false
          prerelease: false
```

**Required edit hunk 1 — permissions block** (D-05):
```diff
 permissions:
   contents: write
-  pages: write
-  id-token: write
```
Keep `contents: write` (required by the retained `softprops/action-gh-release@v3` step for tag
pushes).

**Required edit hunk 2 — remove the deploy step, keep the Release step byte-unchanged** (D-05, D-07):
```diff
-      - name: Deploy to GitHub Pages
-        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
-        uses: peaceiris/actions-gh-pages@v4
-        with:
-          github_token: ${{ secrets.GITHUB_TOKEN }}
-          publish_dir: ./docs/_build/html
-          cname: false
-
       - name: Upload PDF to Release
         if: startsWith(github.ref, 'refs/tags/v')
         uses: softprops/action-gh-release@v3
```

**Post-edit verification pattern (Pitfall 3 guard):** run
`git diff -- .github/workflows/docs.yml` and confirm the hunk touches *only* the `permissions:`
block and the "Deploy to GitHub Pages" step — no line from `- name: Upload PDF to Release`
onward should appear in the diff.

**Everything else stays byte-unchanged:** checkout, Setup Python, Install uv, Install
dependencies, Build HTML documentation, Build PDF documentation, Upload HTML artifact, Upload PDF
artifact (all four kept per D-07).

---

### `tests/test_readthedocs_config.py` (test, request-response / hermetic shape assertion)

**Analog:** the same file's existing `_extract_docs_workflow_python_version()` +
`test_build_python_matches_docs_workflow()` pair (lines 52-65, 122-140) — the raw-text-regex idiom
for asserting facts about `docs.yml` without a full YAML parse, since GitHub Actions
`permissions:`/`uses:` semantics are simplest to assert as substring/regex checks.

**Imports pattern** (lines 20-24, already present — no new imports needed):
```python
import importlib.util
import re
from pathlib import Path

import yaml
```

**Module-level path constant** (line 29, already present):
```python
DOCS_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "docs.yml"
```

**Core pattern to copy — raw-text read + substring/regex assertion** (mirrors lines 52-65):
```python
def _extract_docs_workflow_python_version() -> str:
    """Parse the raw text of `docs.yml` for its `python-version:` line."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    match = _PYTHON_VERSION_RE.search(text)
    assert match, (
        f"Could not find a 'python-version: \"MAJOR.MINOR\"' line in "
        f"{DOCS_WORKFLOW_PATH} -- has the workflow's Python-setup step changed?"
    )
    return match.group("version")
```

**Suggested new guard-test functions (D-06), following the same idiom** — file/path reused,
docstring style matches existing module (references the requirement ID, explains *why*):
```python
def test_docs_workflow_has_no_github_pages_deploy():
    """CI-04 guard: docs.yml must never regain a GitHub Pages deploy step."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "peaceiris/actions-gh-pages" not in text, (
        "docs.yml must not contain a GitHub Pages deploy step -- "
        "CI-04 tore this down permanently"
    )
    assert "pages: write" not in text, (
        "docs.yml's permissions block must not request pages: write -- "
        "unused once the peaceiris deploy step is removed"
    )
    assert "id-token: write" not in text, (
        "docs.yml's permissions block must not request id-token: write -- "
        "release.yml declares its own copy for PyPI trusted publishing; "
        "docs.yml never needed this"
    )
    assert "contents: write" in text, (
        "docs.yml must retain permissions.contents: write -- required by "
        "the Upload PDF to Release step (softprops/action-gh-release)"
    )


def test_docs_workflow_still_uploads_pdf_to_release():
    """CI-04 guard: the tag-time Release attachment step must survive."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "softprops/action-gh-release" in text
    assert "Upload PDF to Release" in text
```

**Test-file placement:** append near the existing `test_build_python_matches_docs_workflow`
(module already scoped to `docs.yml` + `.readthedocs.yaml` shape guards) — no new file, no new
fixture, no new dependency (`re`/`pathlib` stdlib, already imported).

**Run command (per-task, hermetic, no network):**
```bash
uv run pytest tests/test_readthedocs_config.py -x
```

---

### `.planning/codebase/INTEGRATIONS.md` (config/doc, transform)

**Analog:** itself — targeted prose edit reflecting D-07's requirement to update the existing
docs.yml/GitHub Pages description.

**Current text to update** (verified via grep, lines 95-96 and 211):
```
line 95-96: `docs.yml` — Builds HTML (furo) and PDF (`typstpdf`) documentation, uploads both as
            artifacts, **deploys HTML to GitHub Pages** on pushes to `main` (still present as of
            this writing; its removal is scheduled for Phase 32)...
line 211:   `peaceiris/actions-gh-pages@v4` - Deploy built HTML to GitHub Pages (docs.yml;
            scheduled for removal in Phase 32)
```

**Pattern:** remove the "deploys HTML to GitHub Pages" clause and the `peaceiris/actions-gh-pages`
row entirely once torn down (this line's own "scheduled for removal" language becomes stale after
this phase lands) — replace with a short note that publishing is RTD-only now, consistent with
Phase 31's URL-cutover language already present elsewhere in the same file (line 62 area). Match
this file's existing prose register (dense reference paragraphs with backticked identifiers, not
bullet-per-fact).

---

## Shared Patterns

### Evidence-recording format (Phase 29 D-15, reused by every non-file step in this phase)
**Source:** Established convention, not a repo file — verbatim command + verbatim output, no
paraphrase. **Applies to:** SC#1 pre-teardown gate (4 curl checks), SC#2 `git ls-remote` proof +
404 check, SC#3 CI-run citation + `git diff` proof.

```bash
$ curl -s -o /dev/null -w "en html: %{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/
en html: 200

$ curl -s -L https://typsphinx.readthedocs.io/ja/latest/user_guide/builders.html | grep -o 'ビルダー' | head -1
ビルダー

$ git ls-remote origin | grep -i pages
f97862dfea151dd904591a18d2ddbd0bf72fd851	refs/heads/gh-pages
```

### Remote branch deletion + proof
**Source:** RESEARCH.md Pattern 3. **Applies to:** SC#2's `gh-pages` removal — proof must be
`git ls-remote`, never a local `git branch -a` (SC#2's explicit wording).
```bash
git push origin --delete gh-pages
# or: gh api -X DELETE repos/YuSabo90002/typsphinx/git/refs/heads/gh-pages
git ls-remote origin | grep -i pages   # expect: no output
```

### Least-privilege `permissions:` edit
**Source:** `.github/workflows/docs.yml` itself (this phase's own change). **Applies to:** the
workflow file only — do not touch `release.yml`'s independently-declared `id-token: write`
(confirmed textually distinct, serves PyPI trusted publishing, unrelated to `docs.yml`'s copy).

## No Analog Found

None — every file this phase touches already exists and has an established in-file pattern to
follow (targeted edit or extend-in-place). No new file is created.

## Metadata

**Analog search scope:** `.github/workflows/`, `tests/test_readthedocs_config.py`,
`.planning/codebase/INTEGRATIONS.md` — all read directly, no broader glob/grep search needed
since CONTEXT.md/RESEARCH.md already name the exact files and line ranges.
**Files scanned:** 3 (all touched files also served as their own analogs)
**Pattern extraction date:** 2026-07-27
