---
status: complete
phase: 48-compile-time-cross-reference-guard
source: [48-VERIFICATION.md, 48-05-SUMMARY.md, 48-06-SUMMARY.md, 48-07-SUMMARY.md]
started: 2026-08-12T07:05:00Z
updated: 2026-08-14T14:25:00Z
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
result: pass
first_run: issue
first_run_reported: "ファイルにアクセスできませんでした / 移動、編集、削除された可能性があります。/ ERR_FILE_NOT_FOUND / P6のWhat's nextはリンクが死んでいるようです"
first_run_severity: major
resolved_by: 48-05-PLAN.md, 48-06-PLAN.md, 48-07-PLAN.md
note: "Gap G-48-4 — closed by plans 48-05/48-06/48-07 and re-confirmed by the owner on 2026-08-14; the re-run is recorded verbatim as test 5. This entry keeps the original failing observation as first_run_* for the audit trail."

### 5. G-48-4 修正後の PDF 内リンクを再確認
expected: 再ビルド済みの `docs/_build/pdf/typsphinx.pdf`（2026-08-14 13:56 生成）を開き、6ページ目 Quickstart の「What's Next?」にある4本のリンク（configuration / builders / templates / examples）をクリックすると、ERR_FILE_NOT_FOUND ではなく PDF 内の該当文書の先頭へジャンプする。計測上は 35本の壊れた `/URI` file アクションがすべて内部 `/Dest` に変換済み（内部 `/Dest` 37→72、`.pdf` 終わりの URI アクション 40→5）。
result: pass

### 6. option-a の残存リンク切れ（Sphinx 生成ページ）の受容確認
expected: index ページの `genindex` / `py-modindex` / `search`、および api/index の `../genindex` / `../py-modindex` の計5本は、Task 2 チェックポイントでオーナーが選んだ option-a の方針どおり **意図的にリンク切れのまま**（クリックすると ERR_FILE_NOT_FOUND）。これら5本は PDF に対応ページが存在しない Sphinx 生成の仮想ページであり、この状態が受容可能であることを確認。
result: pass

### 7. Pre-fix dead-link population measured and bucketed (48-05 D1)
expected: Pre-fix G-48-4 dead-link population measured, bucketed, and split into two sub-populations against a real `uv run tox -e docs-pdf` build.
result: pass
source: automated
coverage_id: 48-05-D1

### 8. Post-fix expected values pre-declared (48-05 D3)
expected: Every post-fix expected value was fixed in `48-EXPECTED-STRUCTURE.md` before plans 48-06/48-07 existed; git diff shows additions-only against `typsphinx/` and `tests/`.
result: pass
source: automated
coverage_id: 48-05-D3

### 9. Two-outcome acceptance fixture (48-06 D1)
expected: Real two-outcome `sphinx-build` → `typst.compile()` acceptance fixture — probe build exit 0, `grep -c 'link("' index.typ` == 2.
result: pass
source: automated
coverage_id: 48-06-D1

### 10. Offline unit gate on resolver/policy/self-anchor (48-06 D2)
expected: `tests/test_whole_document_xref_unit.py` — 5 passed, 4 xfailed (RED at the time of plan 06).
result: pass
source: automated
coverage_id: 48-06-D2

### 11. Real render gate (48-06 D3)
expected: `tests/test_xref_whole_document_guard_render_gate.py` — 3 passed, 5 xfailed (RED at the time of plan 06).
result: pass
source: automated
coverage_id: 48-06-D3

### 12. RED evidence provenance recorded (48-06 D4)
expected: `48-RED-EVIDENCE.md` carries the new provenance-headed section with verbatim transcripts.
result: pass
source: automated
coverage_id: 48-06-D4

### 13. Whole-document refs onto real docs now guarded (48-07 D1)
expected: Every whole-document reference resolving onto a real `found_docs`-member document is guarded — render gate 8 passed / 0 xfailed / 0 XPASS; unit gate 9 passed / 0 xfailed / 0 XPASS.
result: pass
source: automated
coverage_id: 48-07-D1

### 14. No duplicated guard-string derivation (48-07 D2)
expected: `grep -c 'query(<{label}>)' typsphinx/translator.py` == 1 — no second guard-string derivation point, no second label helper.
result: pass
source: automated
coverage_id: 48-07-D2

### 15. Post-fix PDF dead-link population matches pre-declared value (48-07 D3)
expected: `48-EVIDENCE.md` "G-48-4 post-fix re-measurement" — measured post-fix `.pdf`-suffixed URI actions == 5, matching the pre-declared expected value exactly.
result: pass
source: automated
coverage_id: 48-07-D3

### 16. Phase closes green (48-07 D4)
expected: `uv run pytest -q` — 1083 passed, 1 skipped, 0 failed/errors/xfailed/XPASS; black and mypy clean.
result: pass
source: automated
coverage_id: 48-07-D4

## Summary

total: 16
passed: 16
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-48-4
  truth: "Clicking an internal `:doc:` cross-reference in the built PDF jumps to the correct target section"
  status: resolved
  resolved_by: 48-05-PLAN.md, 48-06-PLAN.md, 48-07-PLAN.md
  resolved_at: 2026-08-14
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
    5 of the 40 have no PDF equivalent at all and need a separate decision (drop the link
    vs. leave it): `genindex`, `py-modindex`, `search`, `../genindex`, `../py-modindex`.
    (Corrected during gap planning — this entry first said 4, miscounting the `../` forms
    against the enumeration above, which lists all five at 1 occurrence each.)
  post_fix_measurement: |
    `48-EVIDENCE.md` § "G-48-4 post-fix re-measurement" (2026-08-14):
      internal /Dest: 37 -> 72 (+35)   URI actions: 465 -> 430 (-35)   total: 502 -> 502 (0)
      URI actions ending in `.pdf`: 40 -> 5 (-35); distinct targets 20 -> 5
      Sub-population A (resolves onto a real docname): 15 targets/35 annotations -> 0/0
      Sub-population B (Sphinx-generated pages, option-a): 5 targets/5 annotations, unchanged
    Measured 5 matches the pre-declared expected value of 5 exactly.
  artifacts:
    - path: "typsphinx/translator.py:4812"
      issue: "`if \"#\" not in refuri: return None` sends whole-document refs to the external-link branch"
    - path: "typsphinx/translator.py:5177"
      issue: "emits `link(\"<docname>.pdf\", ...)` — a URI action to a file that is never produced"
  missing:
    - "A stable per-document anchor each content .typ emits for itself (e.g. `<docname:__doc>`), so a whole-document ref has a label to target"
    - "Route the `xref is None` whole-document case through `_label_existence_guard` against that anchor instead of the string-url branch"
    - "A decision for the 5 Sphinx-generated virtual pages (genindex/py-modindex/search and two `../` forms), which have no PDF counterpart"
  debug_session: ""
