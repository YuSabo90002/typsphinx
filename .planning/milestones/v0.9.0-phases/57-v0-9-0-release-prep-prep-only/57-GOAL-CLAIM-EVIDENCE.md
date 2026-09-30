# Phase 57 — Goal-Claim Evidence (SC#3, multi-template half)

**Provisioning note:** all commands below were run inside this plan's isolated git worktree
(`.claude/worktrees/agent-aa97c63158c21be1b`, branch `worktree-agent-aa97c63158c21be1b`), after
`uv sync --extra dev` with `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` unset, per this project's
`CLAUDE.md` § "Worktree-isolated execution". Every command below was invoked through `uv run`.

## The claim

ROADMAP Phase 57 SC#3, multi-template clause, quoted verbatim:

> a real multi-template `-b typstpdf` build producing two differently-typeset PDFs

Beside it, the milestone goal sentence from `PROJECT.md` § "Current Milestone: v0.9.0
per-document templates":

> every `typst_documents` entry can use its own template, Typst Universe package, and
> template-function arguments — instead of one globally-configured template being applied to
> every master.

**What would have to be true for the claim to be false:** the `-b typstpdf` build over the
fixture's two registry keys would have to fail outright, or the two produced PDFs would have to
share identical page geometry despite their two bundled templates declaring different `paper:`
values — either would mean per-entry template selection is not actually reaching the compiled
output.

## D-14 — why no new gate was authored

The previous release-prep phase (v0.8.0, Phase 52) had to author a brand-new gate for its own
goal claim (the three-master state-guard fixture), because no permanent multi-master regression
test existed yet at that point. This milestone is different: Phase 54 already shipped a permanent
gate for exactly this claim —
`tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate` — which drives a real
`-b typstpdf` build over `tests/fixtures/two_key_selection_gate/`, a fixture whose `conf.py`
declares `typst_document_templates` with two keys (`"report"`, `"memo"`) and three
`typst_documents` entries, two of which share the `"report"` key at different nesting depths and
one of which uses the distinct `"memo"` key. D-14 (`57-CONTEXT.md`) therefore discharges SC#3's
multi-template half by **re-running** that existing permanent gate on the post-bump tree, not by
writing a new one.

No test module, test class, test function or fixture was added or edited in this plan. Confirmed
directly, on the post-bump tree, after Task 1's full measurement sequence:

```
$ git diff --name-only -- tests/
```
(no output)

## Post-bump re-proof

Version and `__file__` read-back, confirming this is the post-bump tree and that `typsphinx`
resolves inside this worktree, not the main checkout:

```
$ uv run python -c "import typsphinx; print(typsphinx.__version__, typsphinx.__file__)"
0.9.0 /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa97c63158c21be1b/typsphinx/__init__.py
```

Full `-v` pytest transcript of the existing permanent gate, re-run on this tree:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa97c63158c21be1b/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa97c63158c21be1b
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items

tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_build_succeeds PASSED [ 16%]
tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_three_pdfs_produced PASSED [ 33%]
tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_both_report_wrappers_emit_an_identical_import_string PASSED [ 50%]
tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_memo_wrapper_imports_its_own_key PASSED [ 66%]
tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_both_bundles_are_published PASSED [ 83%]
tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_the_two_templates_produce_different_pdfs PASSED [100%]

============================== 6 passed in 1.00s ===============================
```

JUnit `testsuite` attribute line from the same run:

```
<testsuite name="pytest" errors="0" failures="0" skipped="0" tests="6" time="0.869" timestamp="2026-08-17T01:36:18.012804+09:00" hostname="Yuta-PC">
```

`skipped="0"`. This matters specifically because the gate class is availability-gated
(`@pytest.mark.skipif(not TYPST_AVAILABLE, ...)`) — `typst-py` was importable in this
worktree's provisioned environment (`uv sync --extra dev` installed `typst==0.15.0`, confirmed by
the sync transcript above), so the class collected and ran for real rather than being skipped. A
skipped run here would have proven nothing about the multi-template claim: it would mean the
build never happened, not that it happened and passed. `failures="0"` and `errors="0"` alongside
`tests="6"` confirm all six methods in the class passed, not just the one this evidence is
centrally about.

## What the committed assertion does and does not prove

`test_the_two_templates_produce_different_pdfs`'s own assertion, read in full this session
(`tests/test_two_key_selection_gate.py:145-157`), is:

```python
master_bytes = build["master_pdf"].read_bytes()
memo_bytes = build["memo_pdf"].read_bytes()
assert master_bytes != memo_bytes, (
    "the 'report'-templated and 'memo'-templated PDFs are byte-identical"
)
```

This is a **byte-inequality** check between the two produced PDFs — it proves the two output
files are not identical, and nothing more. A byte comparison cannot by itself judge whether the
two documents were *typeset* differently (as opposed to, say, differing only in an embedded
timestamp or a font-hinting artifact while still sharing the same page geometry).

The two-way typographic difference this claim rests on is baked into the fixture's two bundled
templates, not asserted by the gate itself. Read directly this session, with file paths and line
numbers:

- `tests/fixtures/two_key_selection_gate/_typst/report/base.typ:26` — `paper: "a4"`
- `tests/fixtures/two_key_selection_gate/_typst/report/base.typ:31` — `set text(size: 11pt, lang: lang)`
- `tests/fixtures/two_key_selection_gate/_typst/memo/base.typ:26` — `paper: "us-letter"`
- `tests/fixtures/two_key_selection_gate/_typst/memo/base.typ:31` — `set text(size: 14pt, lang: lang)`

So the committed gate proves the byte streams differ; it does not itself prove the two PDFs are
typeset differently. That gap is closed by the measurement in the next section, run as a
one-off transcript rather than folded into the committed gate (D-14).

## Page-geometry measurement (transcript, not a gate)

Standalone `sphinx-build -b typstpdf` build over the same fixture, outside the pytest harness,
capturing the build's own summary lines:

```
$ uv run sphinx-build -b typstpdf tests/fixtures/two_key_selection_gate /tmp/.../57-07-build
Sphinx v9.1.0 を実行中
...
typst: wrote 3 wrapper file(s) -- compile these: manuals/guide.typ, master.typ, memos/memo.typ
Compiling 3 master document(s) to PDF...
Generated PDF: /tmp/.../57-07-build/master.pdf
Generated PDF: /tmp/.../57-07-build/manuals/guide.pdf
Generated PDF: /tmp/.../57-07-build/memos/memo.pdf
build succeeded.
```

Emitted `.typ` tree (`find ... -name '*.typ' | sort`), showing the per-key bundle directories
published under the output tree alongside the wrapper files — the milestone's one output rule
(every used registry key's bundle copied wholesale to `<outdir>/_template/<key>/`) made concrete:

```
/tmp/.../57-07-build/_template/memo/base.typ
/tmp/.../57-07-build/_template/report/base.typ
/tmp/.../57-07-build/guide/index.typ
/tmp/.../57-07-build/index.typ
/tmp/.../57-07-build/manuals/guide.typ
/tmp/.../57-07-build/master.typ
/tmp/.../57-07-build/memo/index.typ
/tmp/.../57-07-build/memos/memo.typ
```

Target PDF filenames were read from the fixture's own `typst_documents` configuration
(`tests/fixtures/two_key_selection_gate/conf.py`) rather than assumed: `("index", "master", ...)`
→ `master.pdf` (`"report"` key), `("guide/index", "manuals/guide", ...)` → `manuals/guide.pdf`
(`"report"` key), `("memo/index", "memos/memo", ...)` → `memos/memo.pdf` (`"memo"` key).

`pypdf` read-back, per file: filename, page count, page-1 mediabox width and height, in points:

```
master.pdf:          pages=3  mediabox_w=595.2756  mediabox_h=841.8898
manuals/guide.pdf:    pages=3  mediabox_w=595.2756  mediabox_h=841.8898
memos/memo.pdf:       pages=3  mediabox_w=612.0     mediabox_h=792.0
```

Side by side, the two keys actually compared by the committed gate's own assertion:

```
  master.pdf      (report key): pages=3  w=595.2756  h=841.8898
  memos/memo.pdf  (memo key)  : pages=3  w=612.0     h=792.0
RESULT: mediaboxes are DIFFERENT
```

595.2756 × 841.8898 pt is A4 (210mm × 297mm at 72pt/in); 612.0 × 792.0 pt is US Letter
(8.5in × 11in) — matching the `report` template's `paper: "a4"` and the `memo` template's
`paper: "us-letter"` exactly, in the direction the two templates dictate. The two `"report"`-keyed
outputs (`master.pdf`, `manuals/guide.pdf`) share an identical mediabox with each other, as
expected — they import the same bundled template regardless of nesting depth (OUT-06), and this
plan's claim is about the two-*key* comparison, not the two-*depth* one.

This measurement closes the gap between "the bytes differ" (what the committed assertion proves)
and SC#3's literal "differently typeset" wording (what this transcript proves): the produced
`report`-keyed and `memo`-keyed PDFs differ in page geometry, not merely in incidental byte
content. It is deliberately a **transcript, not a committed gate** — no script was written to
`tests/` or `scripts/` for it, and no test module, class, function or fixture was added or edited,
per D-14.

## Division of authority

This file carries SC#3's multi-template goal claim only — the live re-proof that a real
multi-template `-b typstpdf` build over the post-bump tree produces two differently-typeset PDFs.

The toolchain half of SC#3 (full pytest suite, `black`/`ruff`/`mypy`, both docs tox environments,
and the built-wheel content check, all re-run after the bump) lives in `57-CI-EVIDENCE.md`
(plan 57-05) and `57-GREEN-TREE-EVIDENCE.md` (plan 57-06).
