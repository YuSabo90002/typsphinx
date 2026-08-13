---
status: diagnosed
phase: 48-compile-time-cross-reference-guard
source: [48-VERIFICATION.md]
started: 2026-08-12T07:05:00Z
updated: 2026-08-13T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Accept the label-collision false-negative trade-off
expected: Owner accepts that a coincidental docname/label-namespace collision (`a/b` vs `a_u2f_b`, via the `/`→`_u2f_` sanitize transform) makes the guard render a WORKING link to the wrong (decoy) document instead of degrading to plain text. Read `48-EVIDENCE.md` § "Accepted limit — label-collision false negative". Filed as todo `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`; also flagged WARNING by `48-REVIEW.md` (WR-02).
result: pass

### 2. Accept the D-11 compile-time cost tier outcome
expected: Owner confirms the -2.37% full-corpus compile-time delta (28.92s/27.21s after vs. 28.93s/28.56s before) is acceptable — bottom tier, "record only", no todo/blocker created. The verifier independently re-derived the arithmetic and confirmed the tier thresholds were fixed before measurement; only the ACCEPTANCE is outstanding. Read `48-EVIDENCE.md` § "D-11 compile-time cost".
result: pass

### 3. Accept the D-01 diagnostic-visibility loss
expected: Owner confirms it is acceptable that, post-Phase-48, a reference to a deliberately `:orphan:`-marked target now degrades with ZERO diagnostic at any layer — the D-01 cross-document degrade warning was deleted with no replacement, and Sphinx itself emits no warning for an `:orphan:` target that resolved successfully. The verifier confirmed no published-docs contract broke. Read `48-EVIDENCE.md` § "D-01 — no published contract changed".
result: pass

### 4. Visually confirm PDF cross-reference links navigate to the correct destination
expected: Opening the built `docs/_build/pdf/typsphinx.pdf` and clicking a handful of internal `:ref:`/`:doc:` cross-reference links jumps to the CORRECT target section — not merely to any destination or the wrong page. The verifier ran `tox -e docs-pdf` (exit 0, "build succeeded, 5 warnings", no "does not exist in the document"), producing a valid 119-page PDF with 502 `/Link` annotations all carrying a `/Dest` or `/A` action; only semantic correctness of each destination is unverified.
result: issue
reported: "ファイルにアクセスできませんでした / 移動、編集、削除された可能性があります。/ ERR_FILE_NOT_FOUND / P6のWhat's nextはリンクが死んでいるようです"
severity: major

## Summary

total: 4
passed: 3
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-48-4
  truth: "Clicking an internal `:doc:` cross-reference in the built PDF jumps to the correct target section"
  status: failed
  reason: "User reported: ファイルにアクセスできませんでした / ERR_FILE_NOT_FOUND / P6のWhat's nextはリンクが死んでいるようです"
  severity: major
  test: 4
  root_cause: |
    A whole-document `:doc:` reference (a refuri with NO `#anchor`) is emitted as an
    EXTERNAL URI link to a nonexistent file, not as an internal PDF destination.
    `_resolve_xref_docname` (typsphinx/translator.py:4812) returns `None` for any refuri
    without `#`, documented as deliberate ("whole-document refs with no `#anchor` (kept as
    a string-url link, per requirement -- there is no single anchor to target)"). The
    caller therefore falls into `visit_reference`'s external-reference `else` branch
    (typsphinx/translator.py:5177) and emits `link("user_guide/configuration.pdf", ...)`,
    which the PDF viewer resolves as a file:// URI -> ERR_FILE_NOT_FOUND.
    PRE-EXISTING, not a Phase 48 regression: `git log -L 4786,4800:typsphinx/translator.py`
    attributes this region solely to 510f8e17 (Phase 15, 2026-07-12). Phase 48 changed the
    `xref is not None` branch (anchored cross-references) only; the `xref is None`
    whole-document path is untouched by this phase.
  measured_scope: |
    Re-built `docs/_build/pdf/typsphinx.pdf` via `uv run tox -e docs-pdf` (exit 0, "build
    succeeded, 5 warnings"), then enumerated every `/Link` annotation with pypdf:
      internal /Dest: 37   URI actions: 465   other: 0   (502 total)
      URI actions ending in `.pdf`: 40 across 20 distinct targets — ALL broken
    Verbatim, PDF page 6 (Quickstart "What's Next?" — the link the owner clicked):
      /A {'/Type': '/Action', '/S': '/URI', '/URI': 'user_guide/configuration.pdf'}
      /A {'/Type': '/Action', '/S': '/URI', '/URI': 'user_guide/builders.pdf'}
      /A {'/Type': '/Action', '/S': '/URI', '/URI': 'user_guide/templates.pdf'}
      /A {'/Type': '/Action', '/S': '/URI', '/URI': 'examples/index.pdf'}
    Page 7 by contrast carries a correct internal destination, confirming the anchored
    (`#anchor`) path works and the defect is specific to the whole-document path:
      /Dest user_guide_u2f_configuration:author-information
    4 of the 40 (`genindex`, `py-modindex`, `search`, and their `../` forms) have no PDF
    equivalent at all and need a separate decision (drop the link vs. leave it).
  artifacts:
    - path: "typsphinx/translator.py:4812"
      issue: "`if \"#\" not in refuri: return None` sends whole-document refs to the external-link branch"
    - path: "typsphinx/translator.py:5177"
      issue: "emits `link(\"<docname>.pdf\", ...)` — a URI action to a file that is never produced"
  missing:
    - "A stable per-document anchor each content .typ emits for itself (e.g. `<docname:__doc>`), so a whole-document ref has a label to target"
    - "Route the `xref is None` whole-document case through `_label_existence_guard` against that anchor instead of the string-url branch"
    - "A decision for genindex/py-modindex/search, which have no PDF counterpart"
  debug_session: ""
