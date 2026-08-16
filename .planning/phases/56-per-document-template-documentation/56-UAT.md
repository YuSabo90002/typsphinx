---
status: testing
phase: 56-per-document-template-documentation
source: [56-VERIFICATION.md]
started: 2026-08-16T12:45:00Z
updated: 2026-08-16T12:45:00Z
---

## Current Test

number: 1
name: Rendered readability of the error-catalogue, key-naming, and removed-values tables
expected: |
  All three list-tables render fully legible in both HTML and PDF — no row clipped,
  no horizontal overflow past the PDF page margin.
awaiting: user response

## Tests

### 1. Rendered readability of the error-catalogue, key-naming, and removed-values tables

expected: All three tables are legible in both HTML and PDF, no row clipped, no horizontal overflow.
result: [pending]

**How to run this test:**

Build both outputs from a clean `_build` (an incremental build under-reports and will not
re-render unchanged pages):

```bash
cd /home/yuta/Documents/typsphinx
rm -rf docs/_build
uv run tox -e docs-html
uv run tox -e docs-pdf
```

Then open:

- `docs/_build/html/user_guide/configuration.html`
- `docs/_build/pdf/typsphinx.pdf`

In each, find these three tables under **Template Configuration → Per-Document Templates**:

1. **When the Build Stops** — the error catalogue (3 columns: `What went wrong` /
   `What the build says` / `What to change`; 7 data rows)
2. **Registry Key Naming Rules** — the seven CONF-18 key-shape rejection cases
3. **Removed Configuration Values** — the three removed values and their migration guidance

Confirm for each: every row is visible, nothing is clipped, and in the PDF nothing runs past
the page margin.

**Why this needs a human:** rendered legibility is a visual judgment with no assertable form —
this environment has no PDF text-overflow inspection tooling (`pdfinfo` is not installed).
This item was deliberately deferred to end-of-phase by `56-05-PLAN.md`'s own `<human-check>`
block and is listed in `56-VALIDATION.md`'s Manual-Only Verifications table.

**Already confirmed automatically (so only the visual judgment remains):**

- Both `tox -e docs-html` and `tox -e docs-pdf` succeed from a clean `_build`
  (3 and 5 warnings respectively — the measured baseline, all from `translator.py`
  docstrings and api docs, none from any page this phase touched)
- All three table headings are present in the rendered HTML
- The error catalogue renders with 3 columns and its header row in both builders
  (HTML `<thead>` and Typst `table.header(...)`)
- The `^^^^` heading level nests correctly in both builders (HTML `<h4>`,
  Typst `#heading(depth: 4, ...)`)

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
