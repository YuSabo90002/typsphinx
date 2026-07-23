# Phase 15 Corpus Report: GATE-02 Full-Corpus Validation

**Measured:** 2026-07-13
**Requirement:** GATE-02 (D-06, D-07)
**Test module:** `tests/test_corpus_gate.py`

## Preamble: Corpus Provenance

- **Resolved corpus tag:** `v9.1.0` (`f"v{sphinx.__version__}"`, matching the installed Sphinx version)
- **Clone commit SHA:** `cc7c6f435ad37bb12264f8118c8461b230e6830c` (from
  `git -C ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0 rev-parse HEAD`)
- **Source:** `https://github.com/sphinx-doc/sphinx.git`, shallow clone
  (`--depth 1 --branch v9.1.0`), cached at
  `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc`

**SC#1 (fatal-free compile) — PASSED.** `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
ran the full `sphinx-build -b typstpdf` pipeline against Sphinx's own `doc/`
tree (the FULL tree, D-02, with the real `doc/conf.py` as-is plus a 2-line
`typsphinx` wiring append, D-03) and compiled to a valid PDF with no fatal
`TypstCompilationError`. A manual re-run of the same `-b typstpdf` build
(same cached corpus, same wired conf) confirms the emitted `index.pdf` is
**15,124,122 bytes (~14.4 MiB)**, starts with the `%PDF` magic bytes, and the
build reports `build succeeded, 66 warnings` (0 errors).

## Table 1 — SC#2: `unknown_visit` Frequency Catalogue

Residual node types with no `visit_*`/`depart_*` handler in `typsphinx/translator.py`,
captured from the SC#1 build's stderr (`Unknown Visit Catalogue:` line under `-s`).
This is **not** a failure signal — the gate is "no fatal error," not "zero
warnings" — it is raw material for the next milestone's node-handler backlog.

| Node Type    | Count |
|--------------|-------|
| `todo_node`  | 10    |
| `manpage`    | 10    |

Both node types are unsurprising given Sphinx's own `doc/` tree: `todo_node`
comes from `sphinx.ext.todo` (used throughout Sphinx's contributor-facing
pages), and `manpage` comes from the `:manpage:` role (used in the
reStructuredText reference pages). Neither has a `visit_*`/`depart_*` handler
in `typsphinx/translator.py` as of this measurement, so both nodes fall
through to `unknown_visit` and are dropped from output (rendered as nothing,
not as an error) — candidates for the next milestone's handler backlog.

## Table 2 — SC#3: Empty-URL Before/After (D-07)

Both builds are `-b typst` (translate-only, never `-b typstpdf`/`typst.compile()`,
per Pitfall 2 — the reverted `depart_term` would leave a dangling `:term:`
glossary label that could fatally abort a full PDF compile) against the
**same** cached corpus (`v9.1.0`, SHA `cc7c6f...830c` above), holding the
corpus constant per D-07.

| Empty-URL Warnings (`Reference node has empty URL`) | Before | After | Delta |
|-------------------------------------------------------|--------|-------|-------|
| `tests/test_corpus_gate.py::test_empty_url_before_after` | 1      | 1     | 0     |

### Methodology note (read before interpreting the delta)

**Why "before" is not the original `79c9d45~1` checkout.** D-07's original
wording called for reverting the whole tree to the commit immediately before
`79c9d45 fix(12-02): emit bracket-wrap <label> anchor in depart_term`. By the
time this measurement ran, Phase 15's in-flight campaign had landed 55
commits after `79c9d45`, fixing 25 pre-existing production bugs (spanning
Phases 13-14's entire node-handler surface and a heavy overhaul of
`translator.py`'s reference/anchor handling) to reach GATE-02 green. A
`79c9d45~1`-vs-HEAD diff today would conflate the XREF-01 effect with that
entire campaign — technically matching D-07's literal wording but violating
its actual intent ("quantify the reduction delivered by the XREF-01 fix").

**What was actually measured instead.** The "before" translator is current
HEAD with **only** XREF-01's `depart_term` label-anchor emission disabled
(the `if node.get("ids"):` block `79c9d45` added — see
`checkout_pre_xref01_translator` in `tests/test_corpus_gate.py`), applied via
an isolated `git worktree` branched from `HEAD` (not `79c9d45~1`) with a
targeted in-place source edit. The "after" translator is HEAD as-shipped,
unmodified. This holds Phases 11-14 and all 25 campaign fixes constant in
**both** builds, varying only the one `depart_term` anchor line — a clean,
single-variable isolation of the XREF-01 change itself, rather than the
whole 55-commit campaign.

**Interpreting `delta == 0` honestly.** The measured before/after empty-URL
warning count is identical (1 in both builds) against the full `v9.1.0`
`doc/` corpus. This is not evidence that XREF-01 had no effect — it reflects
that XREF-01's `depart_term` change is a **definition-side** fix: it emits a
Typst label anchor (`<label>`) at the glossary **term definition** so that
`:term:` cross-references can resolve to it. The `Reference node has empty
URL` warning fires on the **reference side**, in `visit_reference`, when a
reference node's `refuri` is empty and (per `translator.py`'s comment) no
`refid` fallback resolves it either — a largely orthogonal code path from
`depart_term`'s anchor emission. Put differently: XREF-01 makes `:term:`
links that *do* resolve render as working intra-document links instead of
broken/mismatched ones; it does not by itself change how many references
have *no resolvable target at all* (which is what `Reference node has empty
URL` counts). The corpus's single residual empty-URL warning in **both**
builds is a genuinely unresolvable reference in Sphinx's own `doc/` tree,
unrelated to the glossary/term-anchor mechanism XREF-01 touches — the
reduction claim for THIS specific warning class was quantified (not
assumed) and found to be zero on this corpus, which is itself a useful,
honest data point for the next milestone rather than the reduction the
original D-07 wording anticipated.

## Fast-Suite Regression Check

`pytest -m "not slow" -q` remains green (see `15-03` execution log); no
`typsphinx/` source files were modified by this measurement task.
