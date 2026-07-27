---
phase: 32-github-pages-teardown-irreversible
reviewed: 2026-07-28T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - .github/workflows/docs.yml
  - tests/test_readthedocs_config.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 32: Code Review Report

**Reviewed:** 2026-07-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

The diff is a clean, narrowly-scoped teardown: `permissions.pages`/`permissions.id-token` and the
`Deploy to GitHub Pages` (`peaceiris/actions-gh-pages@v4`) step are removed from `docs.yml`;
`permissions.contents: write` and the tag-gated `Upload PDF to Release`
(`softprops/action-gh-release@v3`) step are left untouched, matching stated intent. Verified the
resulting YAML still parses cleanly (`yaml.safe_load`), and ran the full
`tests/test_readthedocs_config.py` suite plus `black --check` / `ruff check` on the test file — all
pass (6 passed, 0 failed; lint/format clean). No secrets, injected untrusted input, or dangerous
constructs were introduced. No `Critical` findings.

Two lower-severity items: the new negative-permission guard test uses fragile raw-text substring
matching where a structural (YAML-parsed) assertion would be more robust against reformatting-driven
false negatives, and the module docstring is now stale relative to the module's actual scope.

## Warnings

### WR-01: Negative permission-key guards use fragile text matching, not structural YAML parsing

**File:** `tests/test_readthedocs_config.py:150-159`
**Issue:** `test_docs_workflow_has_no_github_pages_deploy` asserts `"pages: write" not in text` and
`"id-token: write" not in text` via raw substring search over the whole file. This is the test whose
explicit job (per its own docstring) is to be a *permanent* guard against permissions regressing —
"docs.yml must never regain a GitHub Pages deploy step." A raw-text guard is defeated by any
semantically-equivalent but differently-formatted YAML that still grants the same permission, e.g.:
- extra/no spacing: `id-token:  write` or `id-token:write`
- quoting: `"id-token": write` or `id-token: "write"`
- reordering under `permissions:` combined with a YAML formatter/auto-fixer touching whitespace

In each case the permission would functionally exist again, but this guard — the one test whose stated
purpose is to catch exactly that regression — would silently continue to pass, giving false confidence
that CI-04 is still enforced. Contrast with `_load_readthedocs_yaml`/`test_readthedocs_yaml_shape` in
the same module, which parses `.readthedocs.yaml` structurally via `yaml.safe_load` and indexes into
the resulting dict rather than grepping raw text — the more robust pattern already exists a few dozen
lines away in this same file and wasn't reused here.

This affects test reliability (a false-negative-prone regression guard), not just style, per the
review's test-file carve-out.

**Fix:** Parse `docs.yml` with `yaml.safe_load` and assert on the `permissions` dict directly, mirroring
the existing `.readthedocs.yaml` pattern:
```python
def _load_docs_workflow_yaml():
    data = yaml.safe_load(DOCS_WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_docs_workflow_has_no_github_pages_deploy():
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "peaceiris/actions-gh-pages" not in text, (...)

    data = _load_docs_workflow_yaml()
    permissions = data.get("permissions", {})
    assert "pages" not in permissions, (
        "docs.yml's permissions block must not request 'pages' -- "
        "unused once the peaceiris deploy step is removed"
    )
    assert "id-token" not in permissions, (
        "docs.yml's permissions block must not request 'id-token' -- "
        "release.yml declares its own separate copy for PyPI trusted "
        "publishing; this assertion is deliberately scoped to docs.yml alone"
    )
    assert permissions.get("contents") == "write", (
        "docs.yml must retain permissions.contents: write -- required by "
        "the Upload PDF to Release step (softprops/action-gh-release)"
    )
```
(The `peaceiris/actions-gh-pages` action-reference check is fine as raw text — it's an unambiguous
literal string with no realistic reformatting risk, unlike a YAML key:value pair.)

## Info

### IN-01: Module docstring doesn't mention the CI-04 guard tests it now contains

**File:** `tests/test_readthedocs_config.py:1-18`
**Issue:** The module docstring describes the file's purpose exclusively in terms of Phase 29's RTD
manifest shape and the `conf.py` language seam ("This module asserts the commit-1 (HTML-only) shape of
`.readthedocs.yaml` and the two-layer `READTHEDOCS_LANGUAGE` -> `SPHINX_LANGUAGE` -> `"en"` precedence
chain in `docs/source/conf.py`"). It does not mention `test_docs_workflow_has_no_github_pages_deploy`
or `test_docs_workflow_still_uploads_pdf_to_release`, which guard an unrelated concern (GitHub Pages
teardown permanence in `docs.yml`) added in this phase. A future reader skimming the module docstring
to decide whether this file is relevant to a `docs.yml` change would be misled into thinking it isn't.
**Fix:** Add a sentence to the module docstring noting the two CI-04 guard tests and what they protect
against, e.g.: "This module also guards `.github/workflows/docs.yml` against regaining a GitHub Pages
deploy step or its associated `pages`/`id-token` permissions (CI-04, Phase 32), while asserting the
tag-time PDF-to-Release step survives."

---

_Reviewed: 2026-07-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
