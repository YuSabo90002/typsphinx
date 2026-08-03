# Phase 36: Shared-Emission Seam Cleanup - Research

**Researched:** 2026-08-01
**Domain:** Internal refactor — `typsphinx/translator.py` node-handler decoupling + a one-line
list-item separator bookkeeping fix. No external technology, no new dependency, no ecosystem survey.
**Confidence:** HIGH — every claim below is either read directly from `typsphinx/translator.py` at
the cited line numbers or produced by a real `sphinx-build -b typst` / `-b typstpdf` run executed
this session (`uv run python -m sphinx …`), not from training-data assumption.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: `visit_strong`'s body is copied into each handler, not shared.** No `_open_inline_wrapper`
  helper, no parameterised call string, no shared `_enter_bold_wrapper`. `visit_desc_signature` /
  `depart_desc_signature` and `visit_rubric` / `depart_rubric` each get their own full copy of the
  logic they currently borrow (paragraph separator, `_enter_inline_concat_element` /
  `_exit_inline_concat_element`, `in_paragraph` / `in_list_item` /
  `list_item_needs_separator` save-restore, the `_in_markup_mode` `#` prefix). Rationale: Phase 37
  and Phase 39 will each take these two in different directions, so triplication now buys
  unconstrained divergence later. Accepted cost: three copies of the same state machine until 37/39
  make them genuinely different.
- **D-02: keep the existing single-slot state attributes; do not fix the `par()`-loss bug here.**
  All three copies keep using `_strong_was_in_paragraph` / `_strong_was_in_list_item` /
  `_strong_was_list_item_needs_separator`. Renaming them per handler would repair the leak described
  in Deferred Ideas, but it changes emitted bytes for the "rubric containing inline markup"
  construct and would put an exception into SC#2, this phase's only acceptance criterion. File the
  bug as a todo instead.
- **D-03: the implementation form is unconstrained as long as byte-identity holds.** Verbatim copy
  versus a pruned copy (dropping branches proven unreachable from `desc_signature` / `rubric`) is a
  planner/implementer call — the binding constraint is that the decoupling change alone produces a
  zero diff.
- **D-04: RED lives in the emitted `.typ`; the PDF gets an invariance guard, not a RED assertion.**
  Structural assertion on the emitted `.typ` (two blank lines after the math expression pre-fix →
  RED; one blank line post-fix → GREEN). The compiled PDF gets a *regression* assertion that the
  extracted text is unchanged across the fix — which turns "this change is inert" into a test rather
  than a claim. Measured basis, this session, on a list-item block-math fixture compiled through the
  real `typst.compile()`: current output and the intended post-fix output produce **byte-identical
  PDFs** (22,855 bytes each), identical page counts (3), and identical `pypdf`-extracted text. A
  PDF-text RED for MATH-02 is therefore impossible — it is green before and after.
- **D-05: ROADMAP SC#3 is corrected via `/gsd-phase` before planning.** Two errors, both measured
  this session:
  - "exactly one blank line **before** it" — the redundant blank line is **after** the math
    expression, between `mitex(…)` / `$ … $` and the following `parbreak()`. There is already zero
    blank line before it.
  - "asserted … on the compiled PDF's extracted text, with the assertion recorded RED" — impossible
    per D-04. Rewrite to the `.typ`-RED + PDF-invariance-guard form.
  The correction goes into ROADMAP.md (not just here) because the verifier reads ROADMAP success
  criteria directly; a stale SC re-opens the argument at verify time.
- **D-06: take the todo's option (a) — drop the `list_item_needs_separator` bookkeeping — and
  additionally reset the flag to `False`.** Option (b) (gating the pre-existing unconditional
  `"\n\n"` to `not in_list_item`) yields **zero** blank lines after the math inside a list item, not
  one, so it does not satisfy SC#3 as corrected. Option (a) yields exactly one. **But a naive (a) is
  incomplete:** for a `:label:`-carrying equation, `_emit_id_anchors` sets
  `list_item_needs_separator = True` *before* the math is emitted, so merely deleting the trailing
  `if self.in_list_item: self.list_item_needs_separator = True` leaves the flag set and the next
  sibling still emits its own leading `"\n"` — two blank lines again. Measured this session on a
  `.. math:: :label: eq-labeled` inside a bullet item. The fix must clear the flag, not just refrain
  from setting it, and the fixture must cover both the plain and the `:label:` paths on both the
  mitex and native (`-D typst_use_mitex=0`) emission paths.
- **D-07: split the phase into a byte-identical decoupling change and a byte-changing MATH-02
  change, in separate plans and separate commits, decoupling first.** SC#2's recorded diff of two
  real `sphinx-build -b typst` runs is taken against the **decoupling commit alone** — mixing
  MATH-02 into the same diff destroys the only evidence this phase has that the rewiring was
  harmless.

### Claude's Discretion

None was marked "Claude's Discretion" separately from the two measurement-derived items (D-06,
D-07) already listed above as locked — CONTEXT.md folds both into `<decisions>` rather than a
separate discretion bucket, and states explicitly: "Neither of these was selected for discussion;
decided from measurement, recorded here so planning does not re-open them." Treat D-06/D-07 as
locked, not as open discretion.

### Deferred Ideas (OUT OF SCOPE)

- **`par()` loss after a rubric containing inline markup.** `visit_strong` saves caller state into
  three single-slot instance attributes and `depart_strong` `delattr`s them
  (`typsphinx/translator.py:1244-1275`). A rubric containing a real `strong` child (e.g.
  `.. rubric:: **強調** 入り見出し`) causes the inner `depart_strong` to consume and delete those
  slots, so the outer `depart_rubric`'s dummy depart restores nothing and `in_list_item` leaks
  `True` for the rest of the document, dropping every subsequent `par({...})` wrapper. Measured,
  reproduced. **Not fixed here** (D-02) — file a todo, natural home is Phase 39 (owns `rubric`).
  Real-corpus incidence not measured.
- Any change to `visit_strong`'s own behaviour for plain `**bold**` markup.
- The `emphasis` dummy-node delegations (`visit_title_reference`, `visit_inline`'s
  `versionmodified` branch) — ROADMAP SC#1 names only the `strong` delegations. **See Common
  Pitfall 1 below**: this phase found a THIRD `strong` delegation site (`visit_literal_strong` /
  `depart_literal_strong`) that CONTEXT.md's decision text does not enumerate — it is equally
  out of scope and needs the same grep-scoping care as the `emphasis` ones.
- Todos reviewed and NOT folded: `2026-07-22-add-sphinx-linkcheck-ci-job.md`,
  `2026-07-22-citation-node-support-untracked.md` (→ Phase 40),
  `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`,
  `2026-07-25-derive-typst-lang-duplicated-warning-block.md`.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADM-06 | `rubric` no longer routes through the shared `visit_strong` dummy-node delegation, so it and `desc_signature` can be styled independently. | Architecture Patterns §"Exact current bodies" gives the precise call-order to reproduce for `rubric`; Common Pitfall 1 gives the exact grep that must not false-positive on `visit_literal_strong`. |
| MATH-02 | Block math inside a list item emits no redundant blank line. | Architecture Patterns §"MATH-02 fix shape" gives the exact single-line fix (`= True` → `= False` at `translator.py:4087-4088`) verified against both the plain and `:label:` paths, mitex and native, with real measured bytes. |

</phase_requirements>

## Summary

Phase 36 has no external unknowns — the whole risk surface is `typsphinx/translator.py` and the
existing `tests/` suite, and CONTEXT.md has already measured most of the shape. This research
verified CONTEXT.md's claims against the current code (all confirmed) and added three things
CONTEXT.md did not cover: (1) a third, out-of-scope `visit_strong` dummy-delegation site
(`visit_literal_strong`) that a naive SC#1 grep would false-flag; (2) the exact byte-level trace of
*why* a naive copy of `visit_strong`'s body into `rubric` would NOT be byte-identical if "cleaned
up" during the copy (measured: a rubric with a propagated target inside a list item currently emits
**two** blank lines between its anchor and its `strong({` open, an apparent redundancy that D-01's
verbatim-copy mandate requires preserving exactly); and (3) a directly reusable evidence-artifact
template from this milestone's immediate predecessor, Phase 34, whose `34-GATE-EVIDENCE.md` already
solved "how do we record a RED→GREEN proof for a structural (non-fatal) assertion, plus a
pre-change baseline for the regression sweep" for the exact same GATE-01-redefined-for-this-milestone
situation Phase 36 is in.

**Primary recommendation:** Follow Phase 34's plan/evidence shape almost verbatim — one plan for the
byte-identical decoupling (SC#1, SC#2) producing `36-GATE-EVIDENCE.md`'s `## Pre-decoupling
baseline` / `## Post-decoupling diff` sections, one plan for the MATH-02 structural-RED→GREEN fix
(SC#3) appending `## RED — pre-fix run` / `## GREEN` sections to the same evidence file (mirroring
`34-GATE-EVIDENCE.md`'s heading structure), and a closing regression-sweep plan (SC#4) reusing Phase
34's exact full-suite / lint-type-trio / corpus-gate command set. The MATH-02 RED/GREEN assertions
should be added directly to the **existing** `tests/test_inline_math_after_text_render_gate.py` —
its fixture's Construct E (plain) and Construct G (`:label:`-carrying) already have the exact shape
needed (block math inside a list item, followed by more list-item content), on both mitex and native
paths, via the file's existing `extra_args=("-D", "typst_use_mitex=0")` parameterization — no new
fixture is required for MATH-02. SC#2's byte-identity fixture (signatures + siblings + rubric
incl. `.. rubric:: Options` + bold) **does** need a new combined fixture, since no existing fixture
combines all four constructs in one file.

## Architectural Responsibility Map

Not applicable in the browser/server/API/CDN/DB sense — this is a single-process, single-tier
document compiler (docutils doctree → Python translator → Typst source → PDF). The one relevant
"tier" distinction inside the translator itself:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `desc_signature` open/close emission | Translator (`visit_desc_signature`/`depart_desc_signature`) | — | Owns its own state machine after decoupling; currently borrows `visit_strong`'s |
| `rubric` open/close emission | Translator (`visit_rubric`/`depart_rubric`) | — | Same; ADM-06's target |
| Plain `**bold**` markup | Translator (`visit_strong`/`depart_strong`) | — | Untouched — the shared body other handlers currently borrow |
| List-item separator bookkeeping | Translator (`self.list_item_needs_separator` instance state) | `_emit_id_anchors` (a shared helper that also writes this flag) | MATH-02's defect lives entirely in this cross-cutting flag; Phase 36 must not touch its OTHER ~25 read/write sites |
| Byte-identity verification | Test suite (`tests/`) + `.planning/phases/36-…/` evidence | — | New: a golden-snapshot / recorded-diff pattern this repo has not used before (see Architecture Patterns §"Byte-identity proof mechanics") |

## Standard Stack

No new stack. Every tool this phase needs is an existing dev dependency, already pinned:

### Core (already present, no version changes)
| Library | Version [VERIFIED: `pyproject.toml`, this session] | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | `>=8.4,<10` (tox.ini pin), `9.1.1` installed [VERIFIED: `uv run pytest --version`, this session] | Test runner | Project standard, `pyproject.toml` `[tool.pytest.ini_options]` |
| typst-py | pinned via `uv.lock` | Real `typst.compile()` for GATE-01/GATE-02 fixtures | Every node-handler phase in this project uses it; zero-CLI-dependency compile |
| pypdf | pinned via `uv.lock` | PDF text extraction for the MATH-02 invariance guard | Already the extraction library used by `test_inline_math_after_text_render_gate.py`, `test_desc_sig_space_render_gate.py` |
| black / ruff / mypy | `>=26,<27` / `>=0.15,<0.16` / `>=1.13,<3.0` [VERIFIED: `pyproject.toml`, this session] | Lint/type trio | CI-pinned, matches CLAUDE.md commands |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing existing render-gate assertion style (substring/regex on `.typ`) for SC#2 | A full golden-file diff / snapshot library (e.g. `syrupy`) | Rejected — adds a new runtime dependency (violates milestone invariant #1: zero new deps) for a one-off byte-diff need `difflib`/plain string equality already covers |

**Installation:** none — no new packages.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero new packages (milestone invariant #1: zero new runtime
dependencies, `.planning/REQUIREMENTS.md` "Milestone invariants" §1). `typst-py`/`pypdf` are
pre-existing dev dependencies already pinned in `pyproject.toml`/`uv.lock` and used across the
existing render-gate suite.

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (from Sphinx's own parse + domain/autodoc transforms)
        │
        ▼
TypstTranslator.visit_*/depart_* dispatch (typsphinx/translator.py, one method pair per node type)
        │
        ├── visit_strong/depart_strong ─────────┐  (the ONE real implementation, unaffected)
        │                                        │  emits: strong({ ... })
        ├── visit_desc_signature/depart_* ───────┤  BEFORE: constructs nodes.strong(), calls
        │   (API declaration heading)            │  visit_strong/depart_strong on it (dummy-node
        │                                        │  delegation) — SAME emitted bytes as bold
        ├── visit_rubric/depart_rubric ──────────┤  AFTER (this phase): each gets its own COPY of
        │   (section subheading)                 │  strong's body — byte-identical output, but a
        │                                        │  separate code path Phase 37/39 can diverge
        └── visit_literal_strong/depart_* ───────┘  UNTOUCHED — a THIRD, unrelated dummy-node
            (bold literal in field lists, FLD-03)   delegation to visit_strong; stays as-is
        │
        ▼
self.body: List[str]  (accumulated Typst source fragments, joined by astext())
        │
        ▼
TypstWriter.translate() → TemplateEngine (master docs only) → .typ file
        │
        ▼ (typstpdf builder only)
pdf.py: typst.compile() → .pdf file
```

The MATH-02 defect is a SEPARATE, orthogonal seam — a single cross-cutting instance attribute
(`self.list_item_needs_separator`) written by ~30 visit/depart method pairs and `_emit_id_anchors`,
read by the same set to decide whether to emit a leading `"\n"` before their own content:

```
visit_math_block(node)
   │
   ├─ _emit_id_anchors(node)      # if node has ids (:label:), MAY set the flag True
   │                                # BEFORE the leading check below even runs
   ├─ [leading] if in_list_item and needs_separator: add "\n"   # consumes but does NOT reset
   ├─ emit "mitex(`...`)" or "$ ... $"
   ├─ add "\n\n"                   # UNCONDITIONAL block-separator (correct, keep)
   └─ [trailing] if in_list_item: needs_separator = True   # THE BUG — see fix below
                                      ↓
              next sibling (e.g. visit_paragraph) sees needs_separator == True,
              adds its OWN leading "\n" on top of the "\n\n" already emitted
              → 2 blank lines instead of 1 (MATH-02)
```

### Exact current bodies being copied (D-01/D-03) — call-order measured this session

**`visit_strong`/`depart_strong`** (`typsphinx/translator.py:1203-1280`) [VERIFIED: direct read]:

```python
# visit_strong (1203-1246)
self._add_paragraph_separator()                      # no-op unless self.in_paragraph
if not self._enter_inline_concat_element():           # pushes to _inline_concat_stack;
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
was_in_paragraph = self.in_paragraph
self.in_paragraph = False
was_list_item_needs_separator = self.list_item_needs_separator
was_in_list_item = self.in_list_item
self.in_list_item = True
self.list_item_needs_separator = False
prefix = "#" if self._in_markup_mode else ""
self.add_text(f"{prefix}strong({{")
self._strong_was_in_paragraph = was_in_paragraph
self._strong_was_in_list_item = was_in_list_item
self._strong_was_list_item_needs_separator = was_list_item_needs_separator

# depart_strong (1248-1280)
self.add_text("})")
if hasattr(self, "_strong_was_in_paragraph"):
    self.in_paragraph = self._strong_was_in_paragraph
    delattr(self, "_strong_was_in_paragraph")
if hasattr(self, "_strong_was_in_list_item"):
    self.in_list_item = self._strong_was_in_list_item
    delattr(self, "_strong_was_in_list_item")
if hasattr(self, "_strong_was_list_item_needs_separator"):
    if self.in_list_item:
        self.list_item_needs_separator = True
    delattr(self, "_strong_was_list_item_needs_separator")
self._exit_inline_concat_element()
```

**`visit_desc_signature`/`depart_desc_signature`** (`typsphinx/translator.py:4664-4722`)
[VERIFIED: direct read] — delegation call sites relative to the surrounding logic:

```python
# visit_desc_signature
if not self._is_first_desc_signature:
    self._emit_forced_break("linebreak()")   # BEFORE the delegation — sibling separator
self._is_first_desc_signature = False
dummy_strong = nodes.strong()
self.visit_strong(dummy_strong)              # ← delegation point
self._is_first_desc_signature_line = True

# depart_desc_signature
dummy_strong = nodes.strong()
self.depart_strong(dummy_strong)             # ← delegation point
docname = self._current_docname()
seen_labels: set[str] = set()
for node_id in node.get("ids", []):          # AFTER the delegation — hand-rolled anchor loop,
    label_id = self._namespace_label(docname, node_id)   # NOT a call to _emit_id_anchors()
    if label_id in seen_labels:
        continue
    seen_labels.add(label_id)
    self.body.append(f"\n[#metadata(none) <{label_id}>]")   # NOTE: no trailing "\n" after "]"
self.body.append("\n")
```

**`visit_rubric`/`depart_rubric`** (`typsphinx/translator.py:5034-5076`) [VERIFIED: direct read]:

```python
# visit_rubric
self._emit_id_anchors(node)     # ← BEFORE the delegation, via the SHARED helper (unlike
                                 #   desc_signature's own hand-rolled loop). If ids present,
                                 #   emits "\n[#metadata(none) <id>]\n" AND sets
                                 #   list_item_needs_separator = True.
self.body.append("\n")          # unconditional extra newline, ALWAYS, regardless of ids
dummy_strong = nodes.strong()
self.visit_strong(dummy_strong) # ← delegation point

# depart_rubric
dummy_strong = nodes.strong()
self.depart_strong(dummy_strong)  # ← delegation point
self.add_text("\n")               # required — depart_strong's "})" carries no trailing
                                   # separator; omitting this fails "expected semicolon or
                                   # line break" (verified via real compile per the existing
                                   # code comment)
self._emit_forced_break("linebreak()")   # FID-04's unconditional trailing linebreak()
```

### Ordering subtlety a naive copy would NOT reproduce byte-identically (D-03 hazard)

**Measured this session**, building a minimal fixture (`.. _t:` target immediately before
`.. rubric::`, inside a list item):

```rst
* First bullet text.

  .. _my-rubric-in-list-target:

  .. rubric:: A Rubric In A List Item

  More text after the rubric.
```

produces (via `sphinx-build -b typst`, `cat -A`-verified) [VERIFIED: real build, this session]:

```
[#metadata(none) <index:my-rubric-in-list-target>]
                                    ← blank 1
                                    ← blank 2  (from the double-consumption below)
strong({text("A Rubric In A List Item")})
```

i.e. **two blank lines**, not one, between the propagated-target anchor and the rubric's
`strong({` open. This is because THREE separate pieces of code each contribute a newline against
the SAME still-`True` `list_item_needs_separator` flag, and none of them resets it to `False`
after consuming it:

1. `_emit_id_anchors` internally does `if in_list_item and needs_separator: add_text("\n")`
   (consumes the flag from the PRECEDING sibling) then unconditionally re-sets
   `needs_separator = True` at its own end (because it just emitted a body element).
2. `visit_rubric`'s own `self.body.append("\n")` (unconditional, ids or not).
3. The copied-in `visit_strong` body's own leading check — `if self.in_list_item and
   self.list_item_needs_separator: self.add_text("\n")` — fires AGAIN because step 1 left the flag
   `True` and nothing reset it.

**This is existing, pre-decoupling behaviour that D-01's verbatim-copy mandate requires the
decoupled `visit_rubric` to reproduce exactly.** An implementer who "cleans up" this apparent
triple-redundancy while copying (e.g. by deduplicating the leading-newline checks, since they look
like an obvious bug) would violate SC#2's byte-identity requirement even though the result would
arguably be a BETTER fix — that class of improvement is explicitly out of this phase's scope (the
owner's framing: "分離だけ実施して…バイトに差が出ないように分離するだけ" — decouple only, zero byte
delta). Flag this prominently in the plan so an implementer does not "fix" it mid-copy.

`desc_signature` has no equivalent id-anchor-before-delegation step (its anchor loop runs AFTER
`depart_strong`, not before `visit_strong`), so this specific triple-newline hazard is
**rubric-only**. `desc_signature`'s own hazard is narrower: its hand-rolled anchor loop must be
copied verbatim (not swapped for a call to `_emit_id_anchors`), because `_emit_id_anchors` emits a
*trailing* `"\n"` after each `]` that the `desc_signature` loop deliberately omits — swapping them
would add bytes.

### Provably unreachable branches when entered from `desc_signature`/`rubric` (D-03 input)

All three verified this session by direct code + docutils grammar reasoning, none require a
runtime check because they follow from structural node-nesting rules docutils enforces:

- **`_add_paragraph_separator()`'s body is always a no-op.** It only acts when
  `self.in_paragraph` is `True`. Neither `desc_signature` (child only of `desc`) nor `rubric` (a
  structural sibling of paragraphs, docutils grammar) can ever be a descendant of a `paragraph`
  node, so `self.in_paragraph` is always `False` on entry.
- **The `#` markup-mode prefix (`"#" if self._in_markup_mode else ""`) is always `""`.**
  `_in_markup_mode` is set `True` only transiently inside `visit_target`'s
  `_in_reference_with_target` branch (`translator.py:2956`) and unconditionally cleared to `False`
  before that method returns (`translator.py:2975`) — it never stays `True` across a dispatch
  boundary, so it is always `False` when the general walker later invokes
  `visit_desc_signature`/`visit_rubric`.
- **`_enter_inline_concat_element()`'s `ctx` is always `None`** (so the `+`-concat branch inside it
  never fires, and `_exit_inline_concat_element()`'s corresponding `setattr(...)` branch never
  fires either) for both `desc_signature` and `rubric`. The five concat contexts
  (`in_desc_parameter`, `_in_link`, `_in_term`, `_in_field_body`, `_in_attribution`) are all
  populated only by node types that cannot contain a `desc` or `rubric` per docutils/Sphinx
  grammar — a definition-list term and a link body carry only inline content, a `desc_parameter`
  carries only `desc_sig_*` inline nodes, and a collapsed inline `field_body` (the only case
  `_in_field_body` is `True`) is defined by `visit_field_body` itself as "all children are
  `nodes.Inline`" — a nested `desc`/`rubric` is neither, so `_in_field_body` is `False` whenever
  one is present.

**NOT unreachable — must stay live in both copies:** the `in_list_item`/`list_item_needs_separator`
leading-check and the `in_paragraph`/`in_list_item`/`list_item_needs_separator` save-restore dance
around the `strong({`/`})` open-close pair. Both `desc_signature` and `rubric` CAN legally sit
inside a `list_item`'s body content (docutils permits arbitrary body elements inside list items),
and the existing `rubric_propagated_target_render_gate` fixture already exercises `desc`-adjacent
id-anchoring inside list items, so this is a real, tested code path, not a theoretical one.

### Byte-identity proof mechanics (SC#2) — new pattern for this repo

This repo has **no existing golden-snapshot / full-file-diff test pattern** [VERIFIED: repo-wide
grep this session for `golden`, `snapshot`, `difflib`, `assert typ_text ==`, `read_text() ==` across
`tests/*.py` — zero hits of that kind]. Every existing render-gate test
(`test_desc_signature_concat_render_gate.py`, `test_desc_signature_anchor_render_gate.py`,
`test_desc_sig_space_render_gate.py`, `test_rubric_option_concat_render_gate.py`,
`test_rubric_propagated_target_render_gate.py`) asserts **substrings/regex/token-counts** on the
emitted `.typ`, not full-file equality, and all five drive `-b typstpdf` via
`subprocess.run([sys.executable, "-m", "sphinx", "-b", "typstpdf", …])` (never bare `sphinx-build`,
per the NixOS PATH-shadowing note in `test_*_render_gate.py` docstrings), then check
`result.returncode == 0`, absence of specific fatal-error substrings, and `index.pdf` starts with
`%PDF`.

SC#2 needs something these files don't provide: proof that **the SAME fixture produces the SAME
`.typ` bytes before and after a code change**. Since the "before" and "after" outputs come from two
different git states of the SAME code, the practical mechanism is:

1. **Before writing the decoupling code**, run `sphinx-build -b typst` (not `-typstpdf` — SC#2 is
   about the emitted `.typ`, no compile needed) once against a new combined fixture (see below) and
   capture the output verbatim.
2. **Record it** as the phase's `## Pre-decoupling baseline` evidence (see Q5/Validation
   Architecture below for the exact template, borrowed from Phase 34's `34-GATE-EVIDENCE.md`).
3. **After the decoupling code lands**, run the identical build again and diff the two outputs
   (`diff pre.typ post.typ`, or Python `==` on the two strings). An empty diff is the SC#2 proof.
4. **Answer to Q1's (a)/(b)/(c) framing: BOTH.**
   - **(a) A committed golden `.typ` snapshot** belongs under `tests/fixtures/` alongside a NEW
     regression test (e.g. `tests/test_desc_rubric_decoupling_render_gate.py`) that re-builds the
     fixture and asserts equality against the golden snapshot on every future test run — this gives
     the decoupling **permanent** regression protection (a later phase accidentally touching
     `desc_signature`/`rubric` emission would be caught), matching this repo's standing convention
     of "every node-handler change ships a real regression fixture."
   - **(b) A recorded diff artifact under `.planning/phases/36-…/`** is ALSO needed because SC#2's
     wording is explicit: "proven by a recorded diff of two real `sphinx-build -b typst` runs" — a
     ONE-TIME, human-readable evidence trail (the `diff` command's literal output, or `git diff`
     showing zero delta between two run outputs) belongs in `36-GATE-EVIDENCE.md`, mirroring every
     other GATE-01 evidence file in this project's history.
   - Neither alone satisfies both the "recorded diff" wording (needs (b)) and the "regression net
     that catches future breakage" spirit CONTEXT.md explicitly names ("These are the natural
     regression net for 'nothing changed'") (needs (a)).

**Autodoc's "Options" rubric — resolved.** [VERIFIED: read of the cached Sphinx `doc/` corpus at
`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/`, this session]. This is **not** Python-generated
autodoc output — it is a literal `.. rubric:: Options` directive hand-written in Sphinx's own
`doc/usage/extensions/autodoc.rst` (documenting the autodoc extension's own directive options), and
the identical construct (`.. rubric:: Options` immediately followed by `.. option::` directives)
recurs at `doc/usage/domains/c.rst:242`, `doc/usage/restructuredtext/directives.rst` (10+
occurrences), and `doc/man/sphinx-quickstart.rst:30` (`.. rubric:: Structure Options`) — the EXACT
construct `tests/fixtures/rubric_option_concat_render_gate/index.rst` already reproduces
(`.. rubric:: Structure Options` + `.. option:: --sep`). **No autodoc execution or new construct is
needed** — SC#2's new combined fixture can reuse this exact `.. rubric:: <heading>` + `.. option::`
shape verbatim.

### MATH-02 fix shape (D-06) — verified, exact statement to change

Read `typsphinx/translator.py:4014-4091` (`visit_math_block`) [VERIFIED: direct read + real build,
this session]. CONTEXT.md's D-06 claim is **confirmed exactly**, and the fix is a **single-line
change**:

```python
# typsphinx/translator.py, current (defective) end of visit_math_block, ~line 4087-4088:
if self.in_list_item:
    self.list_item_needs_separator = True     # ← BUG: re-arms the flag the next sibling reads

# The fix (D-06):
if self.in_list_item:
    self.list_item_needs_separator = False    # ← the ONLY line that changes
```

**Verified this is sufficient for BOTH the plain and `:label:` paths**, because the trailing
unconditional reset to `False` overwrites whatever state the LEADING checks (including
`_emit_id_anchors`'s own internal flag-setting for a `:label:`-carrying equation) left behind —
D-06's "must clear, not just refrain from setting" requirement is satisfied precisely because this
one-line change runs unconditionally AFTER math emission, regardless of how the flag got set
beforehand.

**Measured before/after bytes** (via a real `sphinx-build -b typst` on
`tests/fixtures/inline_math_after_text_render_gate/index.rst`'s existing Construct E, mitex path,
this session):

```
# BEFORE (current defect) — cat -A verified:
mitex(`E = m c^2`)$
$
$
parbreak()$

# AFTER (predicted from the one-line fix, D-06 logic traced by hand — not yet applied to code):
mitex(`E = m c^2`)$
$
parbreak()$
```

Construct G (labeled, mitex path) shows the identical pattern one line later — the closing `` `) ``
of the `mitex(...)` call is followed by two blank lines before `parbreak()` today, one after the
fix. **Verified the native path (`-D typst_use_mitex=0`) has the byte-identical defect shape** — the
same two-line drop applies to `$ E = m c^2 $` and `$ G = m a … $` forms.

**Blast radius on existing exact-string assertions — CONFIRMED ZERO** (CONTEXT.md's Folded Todos
correction is accurate). `tests/test_inline_math_after_text_render_gate.py` pins two
`\n`-bearing strings that both concern the LEADING side of the math expression, never the trailing
side:
- Line ~175: `'text("Text before block math.")\nmitex(`E = m c^2`)'` — single leading `\n`, unaffected.
- Line ~265: `"[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\nmitex(`G = m a"` — the
  leading anchor-to-math gap, unaffected (this gap is produced by `_emit_id_anchors`'s own trailing
  `\n` plus the leading-check's `\n`, neither of which this phase's fix touches).
`tests/test_math_mitex.py`, `tests/test_math_native.py`, `tests/test_math_fallback.py` contain zero
`\n`-bearing assertions (confirmed via grep, this session) — they are unit tests on a bare
translator instance with no `in_list_item` context at all.

### Every `list_item_needs_separator` writer/reader (blast-radius map, so the fix stays scoped)

**~30 method pairs read/write this one instance attribute** [VERIFIED: full-file grep, this
session]. Categorized so the plan knows exactly what NOT to touch:

| Pattern | Example sites | Notes |
|---|---|---|
| Leading-check, consumes AND resets to `False` | `visit_definition_list` (1831-1833), `visit_figure` (2140-2142), `visit_table` (2444-2446), `visit_field_list` (4912-4914) | The "correct" idiom — `visit_math_block`'s own LEADING check (line 4054-4055) does **not** follow this idiom (no reset), but that is pre-existing behaviour, out of this phase's fix scope (only the TRAILING bookkeeping at 4087-4088 is in scope per D-06) |
| Leading-check, consumes WITHOUT resetting | `visit_Text` (1068-1069), `visit_math` (inline, 3968), `visit_math_block` (4054-4055) | Harmless in these cases because each of these methods unconditionally re-sets the flag `True` at its own end anyway — do not "fix" this as a drive-by, it is out of MATH-02's stated scope (block math only) |
| Trailing "mark next sibling needs separator", sets `True` | `depart_paragraph` (817), `depart_literal_block` (1804), `visit_desc_returns` (4737), `visit_transition` (4504), `_depart_admonition` (4167-4168), 15+ more | The general pattern every OTHER block-level handler uses — `visit_math_block` is the ONE place in this category that should instead reset to `False` (per D-06), because it already emits its own `"\n\n"` block-separator unconditionally (unlike e.g. `depart_paragraph`, whose sibling relies on the NEXT element's own leading newline for separation) |
| Save/restore stack (nesting-safe) | `visit_bullet_list`/`depart_bullet_list` (1476-1502), `visit_enumerated_list`/`depart_enumerated_list` (1531-1557), `visit_emphasis`/`depart_emphasis` (1119-1165), `visit_strong`/`depart_strong` (1229-1275), `visit_reference`/`depart_reference` (3678-3798) | Not touched by this phase; listed for completeness so the planner recognizes them as unrelated when grepping |
| Shared helper, both reads and writes | `_emit_id_anchors` (397-402) | Used by `visit_rubric`, `visit_math_block`, `visit_definition_list`, `_visit_admonition`, and others — NOT modified by this phase (both ADM-06's decoupling and MATH-02's fix only touch code that CALLS this helper, never its own body) |

**Nothing else in this list needs to change for MATH-02.** The fix is exactly the one line identified
above; this table exists so a plan/implementer does not accidentally "generalize" the fix into
`_emit_id_anchors` or another handler.

### Fixture matrix for SC#3 (Q4) — reuse existing fixture, no new one needed

`typst_use_mitex` is a Sphinx config value; the existing test file already parameterizes it via
`extra_args=("-D", "typst_use_mitex=0")` passed to the `_run_sphinx_build_typstpdf` helper
[VERIFIED: `tests/test_inline_math_after_text_render_gate.py:298-303`]. The
`inline_math_after_text_render_gate` fixture (`tests/fixtures/inline_math_after_text_render_gate/index.rst`)
already contains, in ONE `.rst` file:

- **Construct E** — plain block math inside a list item, followed by more prose in the SAME list
  item (`* Text before block math.\n\n  .. math::\n\n     E = m c^2\n\n  Text after block math.`).
- **Construct G** — `:label:`-carrying block math inside a list item, same shape, with
  `:label: construct-g-labeled-eq`.

Both are already driven through BOTH `test_typstpdf_separates_inline_math_mitex_path` (default) and
`test_typstpdf_separates_inline_math_native_path` (`-D typst_use_mitex=0`) — i.e. the full
{mitex, native} × {plain, labeled} matrix SC#3 needs already exists as a fixture; the phase's test
work is **adding new assertions to these two existing test methods** (RED pre-fix, GREEN post-fix
on the "exactly one blank line after" property), not building new fixture files.

### Baseline + green-gate mechanics (SC#4) — exact commands

[VERIFIED: `pyproject.toml`, `CLAUDE.md`, and a real run this session]:

- **Full suite:** `uv run pytest -q --tb=no -rf` — measured this session on the pre-phase-36 tree:
  **649 passed, 1 skipped**, matching Phase 34's own recorded post-fix baseline exactly (no drift
  since v0.6.5 closed). `pyproject.toml`'s `addopts = "-v --strict-markers"` does **not** exclude
  `slow`-marked tests by default, so a bare `pytest` run already includes the corpus gate when the
  corpus cache is present.
- **Lint/type trio:** `uv run black --check .` (measured this session: `173 files would be left
  unchanged`, exit 0), `uv run ruff check .` (measured: `All checks passed!`, exit 0),
  `uv run mypy typsphinx/`.
- **Full-corpus `-b typstpdf` gate, run explicitly:** `uv run pytest tests/test_corpus_gate.py -q -m
  slow` [VERIFIED: exact command used by Phase 34 Plan 03, `34-03-SUMMARY.md`]. The corpus is
  cached at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0` (present on this machine, this session) —
  `get_or_clone_corpus` `pytest.skip`s gracefully (never fails) when unavailable (no network), per
  `test_corpus_gate.py`'s own D-05 docstring note.
- **NixOS-sandbox environmental-failure class — RETIRED as of Phase 34 (2026-07-28), do not
  pre-emptively exclude files.** Project memory (`nixos-sandbox-test-env`, last updated 2026-07-28,
  3 days old at research time) documents that the previously-observed "~45 integration tests fail
  inside a fresh worktree" class (`tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py`
  + `test_examples_basic.py`, all of which `subprocess.run(["uv","run","sphinx-build",…])`) is a
  provisioning artifact: `uv sync` installs a generic-linux-ELF `uv` wheel into a fresh worktree
  venv, which NixOS's sandboxed `stub-ld` cannot exec. **Fix, verified clean in Phase 34, apply once
  per fresh worktree right after `uv sync`:**
  ```bash
  env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
  for t in uv ruff; do [ -x "$(command -v $t)" ] && ln -sf "$(command -v $t)" ".venv/bin/$t"; done
  ```
  This is a supplement to (not a contradiction of) CLAUDE.md's "Worktree-isolated execution"
  section, which documents the `uv sync` + `uv run` half but not this symlink step — the planner
  should carry both. With the shim applied, Phase 34's worktree executors reported full suites
  byte-identical to the main tree (0 environmental failures) — so **do not write acceptance criteria
  that pre-emptively exclude these files**; only fall back to exclusion if a specific worktree
  proves the shim insufficient.
- **Pre-change baseline storage convention (Q5) — confirmed via
  `.planning/milestones/v0.6.5-phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md`**
  [VERIFIED: read, this session]: a single phase-level `{phase}-GATE-EVIDENCE.md` file (NOT stored
  under `tests/`), with clearly delimited sections in this order:
  `## RED — pre-fix run (SC#…, D-…)` → `### Verbatim pytest failure output` → `## RED — verbatim
  Typst errors` (or, for this milestone's structural-RED, the structural-assertion failure output) →
  `## RED — construct reproduction matrix` → `## Pre-fix full-suite baseline` → `## GREEN — post-fix
  run` → `### Verbatim pytest passing output` → `### Post-fix full-suite baseline` → `## GREEN —
  emitted [output] per construct` → `## RED → GREEN verdict` (naming both commit SHAs) → `## Diff
  scope` → `## Regression sweep — suite, lint, invariants` → `## Regression sweep — corpus gate and
  docs dogfooding` → `## Phase verdict`. **Recommend Phase 36 create `36-GATE-EVIDENCE.md` following
  this exact heading shape**, with a `## Pre-decoupling baseline` / `## Post-decoupling diff` pair
  substituting for the RED/GREEN pair on the decoupling half (since decoupling has no compile-fatal
  RED, only a diff), and the classic RED→GREEN pair retained for the MATH-02 half.

### PDF invariance guard mechanics (D-04, Q6)

[VERIFIED: `tests/test_inline_math_after_text_render_gate.py:230-247`, this session] — the existing
pattern already used in this file:

```python
import pypdf
reader = pypdf.PdfReader(str(pdf_output))
full_text = "\n".join(page.extract_text() for page in reader.pages)
```

The **cheapest correct form** of the D-04 invariance guard: after the MATH-02 fix lands, compile the
same fixture and assert `pypdf`-extracted text is unchanged relative to a recorded baseline string
(captured once, before the fix, and hardcoded into the test as the golden comparison value) — this
directly implements D-04's own wording ("a *regression* assertion that the extracted text is
unchanged across the fix"). **Do not hardcode CONTEXT.md's measured "22,855 bytes" PDF size** — that
figure came from the owner's own ad hoc minimal single-construct fixture during discussion, not from
`inline_math_after_text_render_gate`'s actual multi-construct PDF, which will compile to a different
size. If a raw-byte-count assertion is wanted in addition to the text-extraction one, the plan must
re-measure it fresh against the actual fixture used, not copy the number from CONTEXT.md.

### Recommended Project Structure

No new files or directories beyond:
```
tests/
├── fixtures/
│   └── desc_rubric_decoupling_render_gate/   # NEW — SC#2's combined fixture
│       ├── conf.py
│       └── index.rst
└── test_desc_rubric_decoupling_render_gate.py   # NEW — SC#1 grep + SC#2 byte-identity test

.planning/phases/36-shared-emission-seam-cleanup/
└── 36-GATE-EVIDENCE.md   # NEW — evidence artifact, Phase 34 shape (see above)
```
`tests/test_inline_math_after_text_render_gate.py` and its existing fixture are MODIFIED in place
(new assertions), not replaced.

### Anti-Patterns to Avoid

- **"Cleaning up" the triple-newline redundancy found in the rubric-in-list-item trace above while
  copying `visit_strong`'s body.** It looks like an obvious bug fix; it is explicitly out of scope
  and would violate SC#2.
- **Swapping `desc_signature`'s hand-rolled anchor loop for a call to `_emit_id_anchors`.** Looks
  like a DRY improvement; changes bytes (extra trailing `\n` per anchor) and is out of scope.
- **Writing SC#1's repo-wide grep as a blanket `grep "self.visit_strong(dummy_strong)"` with no
  scoping.** Will false-positive on `visit_literal_strong`/`depart_literal_strong`
  (`translator.py:5138-5148`), a THIRD, legitimately-out-of-scope dummy-node delegation to
  `visit_strong` that CONTEXT.md's decision text does not name. See Common Pitfall 1.
- **Fixing `visit_math_block`'s LEADING-check (line 4054-4055) to also reset the flag to `False`.**
  It doesn't need to — it's already harmless because every entry point that sets the flag `True`
  before this check runs is followed (elsewhere) by something that re-establishes correctness. Only
  the TRAILING bookkeeping (4087-4088) is D-06's fix. Touching the leading check is scope creep.

## Don't Hand-Roll

Not applicable in the conventional sense (no third-party-library-replaceable problem here) — the one
relevant note: do not hand-roll a NEW "diff two builds" utility. Python's `str.__eq__` (or
`difflib.unified_diff` for a human-readable rendered diff in the evidence file) is sufficient; no
new dependency, no new helper module.

## Common Pitfalls

### Pitfall 1: A blanket `visit_strong` delegation grep false-flags `visit_literal_strong`

**What goes wrong:** SC#1 requires "a repo-wide grep finds no remaining dummy-node delegation to
`visit_strong`/`depart_strong`" from `desc_signature`/`rubric`. A literal, unscoped
`grep "dummy_strong = nodes.strong()" typsphinx/translator.py` finds **6 hits today**
(`4684`/`4693` = `desc_signature`, `5047`/`5065` = `rubric`, `5141`/`5147` = `visit_literal_strong`/
`depart_literal_strong`, for bold literal text in field lists — the node this repo's FLD-03
requirement, Phase 38, will eventually restyle). After this phase's decoupling, the correct grep
result is **2 hits, not 0** — the `literal_strong` pair must remain.

**Why it happens:** CONTEXT.md's "Out of scope" bullet explicitly names the `emphasis` delegations
(`visit_title_reference`, `visit_inline`'s `versionmodified` branch) as adjacent-but-out-of-scope,
but does not enumerate `visit_literal_strong` — it is a `strong` delegation, not an `emphasis` one,
and was not found during CONTEXT.md's discussion.

**How to avoid:** Write SC#1's verification grep scoped to function context — e.g. verify the count
of `dummy_strong = nodes.strong()` occurrences drops from 6 to exactly 2, AND verify (by line-number
proximity or an AST-aware check) that the 2 remaining occurrences are inside
`visit_literal_strong`/`depart_literal_strong`, not `visit_desc_signature`/`visit_rubric`.

**Warning signs:** A grep-based SC#1 check that returns a nonzero exit code / non-matching count
after a correct decoupling — investigate whether it is counting `literal_strong`'s legitimate,
unrelated occurrences before assuming the fix is incomplete.

### Pitfall 2: The rubric-in-list-item triple-newline "looks like a bug" and invites a drive-by fix

Covered in detail in Architecture Patterns §"Ordering subtlety" above. Repeated here as a pitfall
because it is the single most likely place an implementer accidentally breaks SC#2: the current
emission (two blank lines between a propagated-target anchor and a rubric's `strong({` open, inside
a list item) looks obviously wrong and an instinct to "fix while touching this code" is natural —
but D-01 requires reproducing it byte-for-byte in the decoupled copy.

### Pitfall 3: Assuming `visit_math_block`'s leading-check needs the same fix as its trailing one

D-06 is precise: only the TRAILING bookkeeping (`typsphinx/translator.py:4087-4088`) needs to change
from `= True` to `= False`. The LEADING check (`4054-4055`) does not reset the flag either, but this
is pre-existing, harmless-in-context behaviour outside MATH-02's stated scope (see the
`list_item_needs_separator` blast-radius table above) — do not "fix" it as a drive-by; doing so
risks changing the ALREADY-CORRECT leading-side byte shape the existing pinned assertions
(`test_inline_math_after_text_render_gate.py` lines ~175, ~265) depend on.

### Pitfall 4: Hardcoding CONTEXT.md's "22,855 bytes" PDF-size figure into a new test

That number is from the owner's own single-construct ad hoc fixture during CONTEXT gathering, not
from the actual multi-construct `inline_math_after_text_render_gate` fixture the plan should reuse.
Re-measure fresh if a byte-count assertion is wanted; prefer text-extraction equality (D-04's own
wording) over a raw byte-count, which is more fragile across pypdf/typst-py patch versions anyway.

## Code Examples

### The one-line MATH-02 fix (verified location, not-yet-applied)

```python
# Source: typsphinx/translator.py, visit_math_block, ~line 4087-4088 (existing code, cited
# location — this is the CURRENT/defective state, shown for the plan to locate and change)
        # Mark that content was added so the next list-item sibling
        # (visit_paragraph's _emit_forced_break, a nested list, another
        # block) newline-separates from this equation. The extra newline
        # this produces on top of the existing "\n\n" is cosmetic in Typst
        # code mode; consistency with the shared protocol is what prevents
        # the next sibling from juxtaposing.
        if self.in_list_item:
            self.list_item_needs_separator = True   # ← change this token to False (D-06)
```

### SC#1 verification grep (exact command + expected before/after counts)

```bash
# Before this phase (measured this session): 6 hits (3 pairs: desc_signature, rubric, literal_strong)
grep -n "dummy_strong = nodes.strong()" typsphinx/translator.py

# After decoupling: expect exactly 2 hits, both inside visit_literal_strong/depart_literal_strong
# (currently at translator.py:5141/5147 — line numbers will shift once desc_signature/rubric's
# dummy-node calls are removed, so match by surrounding function name, not literal line number)
```

### SC#2 fixture shape (reuses existing constructs, no autodoc execution needed)

```rst
.. Combines: a signature, sibling signatures, a rubric styled like autodoc's ".. rubric:: Options"
.. construct, and plain bold markup -- the exact four constructs ROADMAP SC#2 names.

.. py:function:: connect(host, port, timeout=30)

   Connect to *host*.

.. py:function:: connect(host, port, timeout=30)
   :noindex:

This is a paragraph with **bold text** for the regression control.

.. rubric:: Options

.. option:: --sep

   If specified, separate source and build directories.
```

(Modeled directly on `tests/fixtures/desc_signature_siblings_render_gate/` +
`tests/fixtures/rubric_option_concat_render_gate/index.rst`, both read this session.)

## State of the Art

Not applicable — no ecosystem drift, no deprecated API, no version bump involved in this phase.

**One repo-internal "state of the art" note:** this phase introduces the first golden-snapshot /
full-diff test pattern this project has used (see Architecture Patterns §"Byte-identity proof
mechanics"). Every prior GATE-01/GATE-02 fixture in this project's history asserted structural
substrings or a real-compile pass/fail, never full-file byte equality — Phase 36 is the first phase
whose PRIMARY acceptance criterion (SC#2) is "nothing changed," so this pattern is new but does not
require a new dependency (plain string/`difflib` equality is sufficient).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The MATH-02 fix's exact predicted post-fix byte output (`mitex(...)\n\nparbreak()`) is derived by hand-tracing the one-line change, not by actually applying the code change and re-running the build. | Architecture Patterns §"MATH-02 fix shape" | If the hand-trace is wrong, the plan's RED assertion (recorded before the fix) could target the wrong "GREEN" shape. Mitigate by having the implementing plan re-verify the exact bytes via a real build immediately after applying the one-line change, before finalizing the assertion text. Confidence: HIGH (the trace only depends on code already read directly, no external unknown), but flagged since it was not re-verified with the fix actually applied (that would require modifying source, out of scope for a research pass). |

**All other claims in this research were verified by direct code read or a real
`sphinx-build`/`typst.compile()` run performed this session** — no other assumption needs
confirmation before planning.

## Open Questions

1. **Should the SC#2 combined fixture be entirely new, or should it be composed by literally
   `#include`-style concatenating fragments already present in the five existing render-gate
   fixtures?**
   - What we know: no existing fixture combines signatures + siblings + rubric-with-Options +
     bold in one file; each existing fixture is narrowly scoped to its own historical bug.
   - What's unclear: whether reusing exact rst snippets from existing fixtures (verbatim) versus
     writing fresh minimal rst content is preferred style in this repo.
   - Recommendation: write fresh minimal content (as sketched in Code Examples above) mirroring the
     STYLE of existing fixtures' conf.py (no intersphinx, no domain resolution needed for signatures
     since they're plain `py:function` declarations with no cross-references) — this is the pattern
     `desc_sig_space_render_gate` and `rubric_option_concat_render_gate` both already use.

2. **Does the SC#2 combined fixture need `-b typst` only, or should it ALSO drive `-b typstpdf` for
   an additional "still compiles" sanity check?**
   - What we know: SC#2 itself only requires the emitted `.typ`, not a PDF.
   - What's unclear: whether a compile-sanity assertion adds meaningful protection beyond the
     byte-diff (it likely does, cheaply, and matches this repo's stated preference for real-compile
     evidence over `.typ`-only checks where feasible).
   - Recommendation: drive `-b typstpdf` (mirrors the five existing render-gate tests' own choice)
     so the same test proves BOTH byte-identity AND "still compiles cleanly," at negligible extra
     cost.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` | Real-compile GATE-01 fixtures (SC#2's optional `-typstpdf` check, SC#3's PDF invariance guard) | ✓ [VERIFIED, this session] | pinned via `uv.lock` | — |
| `pypdf` | PDF text extraction for D-04's invariance guard | ✓ [VERIFIED, this session] | pinned via `uv.lock` | — |
| Sphinx `doc/` corpus cache | SC#4's full-corpus `-b typstpdf` gate | ✓ [VERIFIED: `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0` present, this session] | v9.1.0, matches installed Sphinx | `pytest.skip`s gracefully (never fails) if absent, per `test_corpus_gate.py` D-05 |
| Network (for a fresh corpus clone) | Only if the cache above is absent | Not tested this session (cache already present) | — | Same graceful skip |
| NixOS sandbox `uv`/`ruff` symlink shim | Worktree-isolated executors (CLAUDE.md standing mode) | Not sandbox-dependent on the main tree (verified clean here); required inside fresh worktrees per project memory | — | Shim documented above; apply per-worktree, do not pre-emptively exclude test files |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** the corpus cache/network dependency (graceful skip already
implemented upstream).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED: `uv run pytest --version`-equivalent header, this session] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| Quick run command | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_inline_math_after_text_render_gate.py -q` (new/modified files only) |
| Full suite command | `uv run pytest -q --tb=no -rf` (measured this session: 649 passed, 1 skipped, pre-phase-36 baseline) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADM-06 (SC#1) | No remaining `visit_strong`/`depart_strong` dummy-node delegation from `desc_signature`/`rubric`; `literal_strong`'s stays | structural grep, scoped | `grep -n "dummy_strong = nodes.strong()" typsphinx/translator.py` (expect 2 hits post-fix, both inside `visit_literal_strong`/`depart_literal_strong`) | N/A — a shell assertion, not a pytest file; the planner should still wrap it in a small pytest test for CI enforcement |
| ADM-06 (SC#2) | Decoupling produces byte-identical `.typ` for a fixture exercising signatures, sibling signatures, rubrics (incl. Options-style), and bold | golden-diff regression test | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q` | ❌ Wave 0 — new file + new fixture, per Architecture Patterns §"Byte-identity proof mechanics" |
| MATH-02 (SC#3) | Block math in a list item followed by exactly one blank line, on both mitex/native paths, plain and `:label:` | real-compile structural RED→GREEN gate | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` (both test methods, new assertions added) | ✅ exists — modify in place, no new fixture (see Fixture Matrix section) |
| MATH-02 (D-04) | Compiled PDF text extraction is unchanged by the fix | invariance regression | Same file, new assertion using the existing `pypdf.PdfReader(...).pages[i].extract_text()` idiom already present in this file | ✅ pattern exists, extend it |
| SC#4 | Full suite, lint/type trio, full-corpus gate all green, pre-change baseline recorded | full-suite + slow-marked gate | `uv run pytest -q --tb=no -rf`; `uv run black --check .`; `uv run ruff check .`; `uv run mypy typsphinx/`; `uv run pytest tests/test_corpus_gate.py -q -m slow` | ✅ all exist |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_inline_math_after_text_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_desc_sig_space_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_rubric_propagated_target_render_gate.py -q` (the natural regression net for "nothing changed," per CONTEXT.md, plus the two new/modified files)
- **Per wave merge:** `uv run pytest -q --tb=no -rf` (full suite, includes the corpus gate by default when the cache is present)
- **Phase gate:** Full suite green, lint/type trio green, `uv run pytest tests/test_corpus_gate.py -q -m slow` explicitly re-confirmed, `36-GATE-EVIDENCE.md` complete with the pre-change baseline recorded (SC#4).

### Wave 0 Gaps
- [ ] `tests/fixtures/desc_rubric_decoupling_render_gate/{conf.py,index.rst}` — new fixture covering
  SC#2 (signatures, siblings, rubric incl. Options-style, bold markup).
- [ ] `tests/test_desc_rubric_decoupling_render_gate.py` — new test: SC#1's scoped grep assertion +
  SC#2's byte-identity assertion against a captured pre-decoupling golden `.typ` string/file.
- [ ] `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` — new evidence artifact
  (Phase 34 heading shape), required as a distinct deliverable before SC#4 can be marked complete.
- [ ] New assertions in `tests/test_inline_math_after_text_render_gate.py`'s two existing test
  methods, for SC#3's "exactly one blank line after" property (RED recorded pre-fix, GREEN post-fix)
  and D-04's PDF-text-invariance guard — no new file needed here, only new assertions.

*No framework-install gap: pytest, typst-py, and pypdf are all already installed dev dependencies.*

## Security Domain

**Not applicable — `security_enforcement` context does not change this determination, but stating
explicitly why:** this phase touches zero user input, zero authentication/session/access-control
surface, zero cryptography, and zero new external data path. It is a pure internal refactor
(duplicate a private code path) plus a one-line whitespace-bookkeeping fix inside a document
compiler that only ever processes trusted, locally-authored `.rst` source the SAME way it already
does today. No ASVS category applies beyond what every other translator phase in this project's
history has already inherited (V5 input validation, satisfied by docutils' own parser upstream of
this code, unchanged by this phase).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | no (unchanged by this phase) | docutils' own rST parser, upstream of `typsphinx` entirely |
| V6 Cryptography | no | — |

### Known Threat Patterns for this stack

None applicable — no new attack surface introduced.

## Sources

### Primary (HIGH confidence — direct code read + real builds this session)
- `typsphinx/translator.py` — full read of lines 95-330, 900-1360, 1780-1840, 2120-2150, 3990-4180,
  4640-4930, 5010-5150 (the complete scope of this phase's touched code plus every
  `list_item_needs_separator` and `visit_strong`/`dummy_strong` reference in the file).
- Real `sphinx-build -b typst` runs this session against
  `tests/fixtures/inline_math_after_text_render_gate/` (both mitex-default and
  `-D typst_use_mitex=0` native paths) and a hand-written scratch fixture reproducing a rubric with
  a propagated target inside a list item.
- `.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md` — the phase's own locked
  decisions, D-01 through D-07.
- `.planning/milestones/v0.6.5-phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md`,
  `34-01-SUMMARY.md`, `34-02-SUMMARY.md`, `34-03-SUMMARY.md`, `34-RESEARCH.md` — the immediately
  preceding phase in this repo, same milestone lineage, same GATE-01-redefined situation, providing
  the evidence-artifact template and exact command set reused above.
- `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/` — the cached Sphinx corpus, grepped to resolve
  the "autodoc's Options rubric" ambiguity.
- `/home/yuta/.claude/projects/-home-yuta-Documents-typsphinx/memory/nixos-sandbox-test-env.md` —
  project memory, 3 days old at research time, for the worktree environmental-failure shim.

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` — project-level
  requirement/roadmap/state context, cross-checked against CONTEXT.md and found consistent.

### Tertiary (LOW confidence)
- None. This phase's entire scope was verifiable by direct code inspection and real local builds;
  no web search or external documentation lookup was performed or needed (per the research-focus
  instruction to skip ecosystem surveys for this phase).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new stack, every command/version verified this session.
- Architecture: HIGH — every call-order claim traced against real code and confirmed with real
  `sphinx-build` output this session, including one net-new finding (`literal_strong`) and one
  net-new byte-level trace (the rubric-in-list-item triple-newline) beyond what CONTEXT.md recorded.
- Pitfalls: HIGH — all four pitfalls are grounded in measured code/output, not speculation.

**Research date:** 2026-08-01
**Valid until:** No expiry driver — this is a pure internal-code research pass with no external
dependency drift risk. Re-verify only if `typsphinx/translator.py` changes between now and planning
(unlikely within the same session/day).
