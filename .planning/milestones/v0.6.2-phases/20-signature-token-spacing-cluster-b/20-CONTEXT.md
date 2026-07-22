# Phase 20: Signature Token Spacing (Cluster B) - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Restore lost **intra-signature / intra-field token spacing** across three audit findings
(FID-07..FID-09 = F2/F3/F5) — the token-level counterpart of Phase 19's block-level cluster —
as a set of `visit_*`/`depart_*` spacing fixes in `typsphinx/translator.py`, so Python and
C/C++ signatures and object-description fields render with the inter-token spacing the
`-b html` / `-b text` authority shows instead of concatenating.

**Root cause (confirmed in code):** the token-level analog of Phase 19's "code-mode `\n` is
cosmetic-only" invariant. `visit_desc_sig_space` (translator.py:4812) emits a **bare space
`" "`** into `self.body`. Inside a Typst code block (`strong({ … })` content, where
desc_signature tokens live) adjacent content values join and interior whitespace is
insignificant — so `text("class") text("sphinx…")` joins to "classsphinx…" and the space is
swallowed. A **real content-space token** (e.g. `text(" ")`, concat-aware) is required to
render, exactly as Phase 19 needed `parbreak()`/`linebreak()` instead of `\n`.

**The three findings (per audit catalogue rows 2 / 3 / 5):**
- **FID-07 (F2, row 2)** — `desc_annotation` "class "/"exception " keyword prefix loses its
  trailing space on every `py:class`/`py:exception`/`autoclass`: "classsphinx.builders…" →
  should be "class sphinx.builders…". Systemic, ~20 pp.55–67, corpus-wide. Space-node-backed
  (`visit_desc_sig_space`).
- **FID-08 (F3, row 3)** — C/C++ `desc_signature` and inline `c:expr`/`cpp:expr` lose **all
  inter-token spaces**: around `*`/`&`, type↔identifier, after the keyword prefix, and
  operator spacing: "Py_ssize_tnitems" → "Py_ssize_t nitems"; "a*f(a)" → "a * f(a)"; also
  "structData", "inta", "constData*", "classWrapper template<typenameTOuter>". Systemic across
  the C/C++ domain (pp.71–86). Mostly `desc_sig_space`-backed; some forms may route through
  `desc_sig_operator`/`desc_sig_punctuation` — a completeness check is required (see D-08).
- **FID-09 (F5, row 5)** — `field_list` `:type:`/`:default:` object-description fields lose
  colon-space and field boundaries: "the_answer Type:int (a number)Default:42" → should be
  "Type: int (a number)  Default: 42". `depart_field_name` (translator.py:4691) emits
  `text(":")` with no trailing space; sibling fields also merge with no inter-field
  separation. (Same class seen in `c:alias` `:options:` "Options:maxdepth: int".)

**Out of scope:** all Cluster A block-separation findings (Phase 19, done); Cluster C margin
overflow / no-wrapping (FID-10, Phase 21); Clusters D/E/F residual findings (FID-11..FID-14,
Phase 21); Issue #117 PDF naming (PDF-01, Phase 22). This phase is intra-token spacing
restoration only — no new constructs, no `@preview` bump, no version-sync-surface changes.

</domain>

<decisions>
## Implementation Decisions

### FID-09 field rendering shape
- **D-01:** Render `:type:`/`:default:` object-description fields **inline with restored
  spacing** — keep the current inline structure and restore (a) the colon-space after each
  field name and (b) inter-field boundary separation — targeting the exact ROADMAP SC#3
  string `"Type: int (a number)  Default: 42"`. Central edit: `depart_field_name`
  `text(":")` → colon-space.
- **D-02:** Rejected the **stacked definition-list block** form (Type:/Default: on separate
  lines, value indented) that the `-b html`/`-b text` authority technically uses. Rationale:
  SC#3 explicitly pins the *inline* target string, so inline-with-spacing IS the acceptance
  bar for this phase (not an "under-delivery"); a stacked block is a larger structural change
  the SC does not require and would diverge from the pinned target. (Contrast Phase 19 D-01/D-02,
  where no SC pinned an inline form so the HTML-faithful block form won — here the SC decides.)

### FID-08 C/C++ scope / completeness
- **D-03:** Fix **all audited C/C++ inter-token forms** — `*`/`&`-adjacent, type↔identifier,
  keyword prefix, operator spacing ("a * f(a)"), `const…*`, `template<typename T…>`. SC#2
  literally requires "preserve **all** inter-token spaces," and if the root fix lands at the
  shared `desc_sig_space` handler most forms are covered uniformly at low marginal cost.
- **D-04:** Rejected the **space-node-backed subset only** (defer rare operator/template forms
  to Phase 21) — it would fail SC#2's "all," and splitting a single systemic root cause across
  two phases is churn without benefit.

### FID-07/08 space token kind (wrap behavior)
- **D-05:** Restore spaces as **normal breakable spaces** — the `-b html` authority wraps long
  signatures naturally, and this keeps blast radius minimal. Margin-overflow / no-wrapping is
  explicitly **Cluster C's** concern (FID-10, Phase 21).
- **D-06:** Rejected **non-breaking spaces** (keep each signature on one line): they would
  pre-empt Cluster C and risk *introducing* the very right-margin overflow this milestone fixes
  elsewhere, on the longest C/C++ signatures.

### Verification strategy (GATE-01)
- **D-07:** Carry forward Phase 19's **D-05 structural floor** — every fixture MUST assert the
  generated `.typ` contains the expected content-space token at the correct site (pre-fix
  bare `" "` yields no such token → assert fails; post-fix passes) AND run a real
  `typst.compile()` producing a valid `%PDF`. **Additionally REQUIRED this phase:** a **pypdf
  extracted-text adjacency assertion** for the observable findings (e.g. "class sphinx" present
  / "classsphinx" absent for FID-07; "Py_ssize_t nitems" present / "Py_ssize_tnitems" absent
  for FID-08; "Type: int" / "Default: 42" spacing for FID-09). Rationale: unlike Phase 19's
  *vertical* spacing (not text-extractable, so pypdf was rejected in Phase 19 D-06), Cluster B
  is *horizontal* spacing that pypdf CAN detect — so the adjacency assert is cheap AND
  meaningful here, and directly proves the rendered-glyph fidelity the FID target describes.

### Claude's Discretion
- **Exact space-emission token & concat-awareness** — `text(" ")` vs a `+ text(" ") +` concat
  form vs `sym.space`/`~`; the fix at `visit_desc_sig_space` must be concat-context-aware
  (some `c:expr`/`cpp:expr` fire inside a paragraph/inline-concat context via `desc_inline`
  pass-through, others inside the `strong({…})` join block). Precise emission is a
  research/planning detail to settle against real compiles — the *intent* (a real content
  space, breakable, per D-05) is fixed.
- **Shared-idiom structure (D-03 of Phase 19 reaffirmed as default)** — prefer one small shared
  "code-mode space is cosmetic → emit real content space" idiom reused across the
  space-emission sites (paralleling Phase 19's shared break helper), over fully-independent
  per-finding edits. Planner may keep FID-09's colon-space (`depart_field_name`) separate since
  it is a distinct mechanism (field name/colon, not a `desc_sig_space` node).
- **Fixture granularity/placement** — recommended default one render-gate fixture per finding,
  extending existing gate modules where a direct analog exists; a planner may consolidate if a
  shared fixture project cleanly exercises multiple findings, provided each finding retains an
  assertion (structural + pypdf-adjacency) that would fail against the pre-fix translator.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source of record for every FID finding
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` —
  the audit catalogue. Issue Table **row 2 (F2/FID-07)**, **row 3 (F3/FID-08)**, **row 5
  (F5/FID-09)** carry docname + node kind + minimal repro + expected `-b text`/`-b html`
  output + page pointers for each of this phase's three findings. Severity-final,
  human-confirmed at the 17-03 gate.

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` §"Signature Token Spacing (Cluster B …)" — FID-07..FID-09
  requirement text + F-number traceability; milestone invariant (zero new runtime deps, no
  `@preview` bump); GATE-01 standing bar.
- `.planning/ROADMAP.md` §"Phase 20: Signature Token Spacing (Cluster B)" — goal, 4 success
  criteria (note SC#2 "all inter-token spaces" and SC#3's pinned inline target string
  `"Type: int (a number)  Default: 42"`), and the real-`typst.compile()` acceptance bar.

### Prior-phase foundation (settled idiom this phase builds on)
- `.planning/phases/19-block-separation-fixes-cluster-a/19-CONTEXT.md` — Phase 19 decisions
  (D-01 per-construct fidelity, D-03/D-04 shared-helper idiom, D-05 structural-assert gate,
  D-06 rasterization rejection). The "code-mode X is cosmetic-only → emit a real Typst token"
  root-cause family and the shared-helper structure carry directly into Cluster B.

### Code + established idioms to reuse (not modify beyond scope)
- `typsphinx/translator.py` — the handler sites: `visit_desc_sig_space` (~4812, the bare-space
  root cause for FID-07/FID-08); `depart_field_name` (~4691, the `text(":")` no-space root
  cause for FID-09); `visit_field_list`/`visit_field`/`visit_field_body` (~4636–4740, field
  boundary separation); `visit_desc_signature`→`visit_strong` `strong({…})` join block that
  makes interior code-mode whitespace insignificant; `desc_sig_operator`/`desc_sig_punctuation`
  (~4832–4846) to check for non-space-node C/C++ spacing forms; `desc_inline` pass-through
  (~4513) for inline `c:expr`/`cpp:expr` concat context.
- `tests/test_desc_signature_concat_render_gate.py` — the canonical GATE-01 fixture shape
  (emitted-`.typ` structural assert + real `-b typstpdf` compile + `%PDF` magic; invoked via
  `sys.executable -m sphinx`, never `uv run`, per the NixOS-sandbox PATH hazard). Extend the
  pattern with the required pypdf extracted-text adjacency assert (D-07).
- `tests/test_corpus_gate.py` — the standing full-corpus (~684-page) regression gate the
  spacing changes must not regress.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`visit_desc_sig_space` single choke point** (translator.py:4812): the one bare-space
  emitter behind both FID-07 and FID-08 space cases. One concat-aware fix here has the highest
  leverage.
- **Phase 19 shared-break-helper idiom** (`_emit_forced_break` and the
  `list_item_needs_separator` machinery): the structural precedent for a small shared
  space-emission idiom (D-03 discretion / Phase 19 D-03 reaffirmed).
- **Inline-concat machinery** (`_emit_inline_concat_separator` / `_mark_inline_concat_content`
  / `_enter_inline_concat_element`): the existing `+`-separation context the space fix must be
  aware of so it works both inside `strong({…})` join blocks and inline `c:expr` concat.
- **GATE-01 fixture template** (`test_desc_signature_concat_render_gate.py`): copy its shape;
  add the D-07 pypdf adjacency assert.

### Established Patterns
- **Code-mode whitespace (space AND `\n`) is cosmetic-only** — the invariant unifying Phase 19
  (block breaks) and Phase 20 (token spaces). Emit a real content token (`text(" ")` /
  `parbreak()` / `linebreak()`), never rely on raw whitespace for a visible effect.
- **`desc_signature` renders inside `strong({ … })`** — a content-join block where adjacent
  `text(...)` values concatenate and interior whitespace is dropped; this is *why* the bare
  space vanishes.
- **`field_name` → `strong({...}) + text(":")`** (translator.py:4691) — the FID-09 colon site;
  the fix appends a space to the colon and ensures inter-field boundary separation.

### Integration Points
- All three fixes land in `typsphinx/translator.py` only. No `builder.py`/`writer.py`/
  `template_engine.py`/`templates/base.typ` changes (version-sync surface stays untouched).
- Cluster C (Phase 21, FID-10 margin overflow) depends on the natural breakable spaces this
  phase restores (D-05) — do not pre-solve overflow here with non-breaking spaces.

</code_context>

<specifics>
## Specific Ideas

- Every fix ships or extends a **real** `typst.compile()` regression fixture that would FAIL
  against the pre-fix translator: structural `.typ` content-space-token assert **plus** a
  **required** pypdf extracted-text adjacency assert (D-07). String-agreement asserts alone
  never suffice (GATE-01).
- Expected target strings are pinned by the ROADMAP SCs and audit rows: FID-07
  "class sphinx.builders…"; FID-08 "Py_ssize_t nitems" / "a * f(a)"; FID-09
  "Type: int (a number)  Default: 42".
- Milestone invariant reaffirmed: **zero new runtime dependencies, no `@preview` version bump,
  the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`)
  stays untouched.** Flag during planning if any target is found to need otherwise. (pypdf is
  a test-only dependency — confirm it is already a dev dep before requiring it in a gate.)
- Fidelity authority is `-b html` (with `-b text` as the secondary baseline), per the audit
  catalogue convention.

</specifics>

<deferred>
## Deferred Ideas

- **Stacked definition-list rendering for object-description fields** (FID-09) — rejected for
  this phase (D-02) in favor of the SC-pinned inline form; could be revisited as a fidelity
  enhancement in a future milestone if the inline form proves insufficient.
- **Non-breaking-space signature cohesion** — rejected (D-06); belongs to the Cluster C margin
  discussion (FID-10, Phase 21) if signature wrapping turns out to read poorly.
- Cluster C margin overflow (FID-10) → Phase 21; Clusters D/E/F (FID-11..FID-14) → Phase 21;
  Issue #117 PDF naming (PDF-01) → Phase 22. Explicitly out of Phase 20.

None from scope creep — discussion stayed within phase scope.

</deferred>

---

*Phase: 20-Signature Token Spacing (Cluster B)*
*Context gathered: 2026-07-20*
