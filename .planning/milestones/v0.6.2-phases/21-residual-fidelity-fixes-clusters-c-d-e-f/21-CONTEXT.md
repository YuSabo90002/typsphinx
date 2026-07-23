# Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

The tail of the coherent v0.6.2 translator-fix series: the remaining smaller-root-cause silent
mis-render findings (FID-10..FID-14 = F6/F9/F11/F8/F10), each isolated to its own node handler in
`typsphinx/translator.py`, plus **one** deliberate `templates/base.typ` `show link:` rule (FID-13
styling — see D-01). These are independent, small-blast-radius edits landing after the two large
clusters (Phase 19 block separation, Phase 20 token spacing).

**The five findings (audit catalogue rows):**
- **FID-10 (F6, row 6, Cluster C)** — a long run of inline `literal` roles (`:cpp:any:`
  `:cpp:class:` …) overflows the right text margin and is clipped mid-token; trailing roles are
  not rendered = content loss. `usage/domains/cpp` p.85. Medium.
- **FID-11 (F9, row 9, Cluster D)** — reST semantic/soft line breaks inside a paragraph render as
  HARD line breaks (ragged short lines) instead of collapsing to a single space. Systemic,
  corpus-wide. Medium.
- **FID-12 (F11, row 11, Cluster E)** — a `literal_block` with BOTH a `:caption:` AND nested in a
  `list_item` leaks its codly config wrapper as literal visible text (`{ codly(number-format:
  none)` … `}`). `extdev/i18n` p.232. Medium.
- **FID-13 (F8, row 8, Cluster F)** — external named `reference` hyperlinks flatten to plain,
  undistinguished text (+ a stray boundary space where adjacent inline text exists). Link styling
  is meaning-bearing (catalogue D-06). Systemic, corpus-wide. Low.
- **FID-14 (F10, row 10, Cluster F)** — `*` (PEP 3102 keyword-only) and `/` (PEP 570
  positional-only) separators inject their `<abbr>` hover-title text inline ("* (Keyword-only
  parameters separator (PEP 3102))"), cluttering every affected signature. `extdev/*`. Low.

**Out of scope:** Cluster A block-separation (Phase 19, done); Cluster B token spacing (Phase 20,
done); Issue #117 PDF naming (PDF-01, Phase 22); the Release phase (version bump + CHANGELOG).
Milestone invariant carried forward: **zero new runtime dependencies, no `@preview` version bump,
the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`'s four
`@preview` package versions) untouched.** Note the FID-13 `show link:` rule edits `base.typ` but
does NOT touch its `@preview` version declarations — the version-sync surface is those four
version strings, which stay unchanged.

</domain>

<decisions>
## Implementation Decisions

### FID-13 — external link styling (Cluster F)
- **D-01:** External hyperlinks render with **color + underline**. The translator keeps emitting
  `link(…)` unchanged; the **visual styling lives in a `show link:` rule in the default template
  `templates/base.typ`**, NOT per-node in the translator. This deliberately relaxes the phase's
  "translator-only, each isolated to its own node handler" default for FID-13's styling half —
  the user chose template-delegated styling as the correct Typst-idiomatic place.
- **D-02:** The `show link:` rule is **scoped to external URLs only** — active when `it.dest` is a
  string (a URL), inactive for label destinations. Internal cross-references (section/figure
  refs, which also emit `link(<label>, …)`) keep their current unstyled rendering. Rationale:
  FID-13's finding is specifically external named references; styling internal refs too would
  add print noise the finding never flagged, and the show rule can trivially distinguish the two
  by `it.dest` type.
- **D-03:** The **boundary stray-space** half of FID-13 (a stray space before a following period
  or word where adjacent inline text exists, per catalogue row 8) is a `reference`
  concat/boundary bug in the translator, NOT a styling preference — deferred to
  research/planning to root-cause and fix at the `visit_reference`/`depart_reference` boundary.
  This half IS text-extractable and gets a pypdf assert (see D-09).
- **Applicability note:** the `show link:` rule lives in the DEFAULT `base.typ`; a user-supplied
  `typst_template` is the user's responsibility (out of scope). Fidelity target is the default
  template output.

### FID-10 — inline-literal wrapping (Cluster C)
- **D-04:** **Boundary-only fix** — make the inter-literal spaces genuinely breakable so a long
  run of inline `literal` roles reflows at the spaces between role tokens (HTML parity). Do NOT
  break inside a single role token.
- **D-05:** **Keep the existing table ZWSP break-point primitive isolated.** The Phase 18 F12 fix
  (ZWSP U+200B inserted at `.`/`_` so Typst's line-breaker can wrap unbroken identifiers) is
  explicitly gated to `self.in_table` (`translator.py:1224-1236`, comment "prose/code-block
  literals stay byte-unchanged — F6 out of scope"). Do NOT extend that gate to prose. This honors
  the catalogue's kinship note (F6 is a DIFFERENT node kind — inline `literal` run vs.
  `table`/`tgroup` — and must not be conflated into F12's requirement) and keeps blast radius
  minimal. Rejected: reusing/extending the table ZWSP primitive to prose (broader blast radius,
  needs table-behavior regression re-verification for no clear FID-10 benefit).
- **D-06 (escape hatch, not a scope change):** SC#1's acceptance bar is "wraps within the text
  margin, no mid-token clip / no content loss." If a real `typst.compile()` shows the
  boundary-only fix is insufficient (e.g. a single role token alone exceeds the line width —
  unlikely for short `:cpp:xxx:` roles), the researcher/planner escalates rather than silently
  under-delivering. The intent (natural reflow at token boundaries, no content loss) is fixed;
  the exact break mechanism is settled against real compiles.

### Verification strategy (GATE-01)
- **D-07:** **Per-finding split by text-extractability**, extending the Phase 19 / Phase 20
  precedent. Every fixture keeps the standing floor: a structural `.typ` assert that FAILS
  against the pre-fix translator, PLUS a real `typst.compile()` producing a valid `%PDF`.
- **D-08 (FID-11 → Phase-19 family):** FID-11 uses the **structural `.typ` assert as its sole
  floor — pypdf is NOT used.** Confirmed mechanism: pre-fix, `visit_Text` → `escape_typst_string`
  turns an intra-paragraph source `\n` into a `\\n` escape inside `text("…line1\nline2…")`, which
  Typst decodes to a forced line break. The `.typ` assert is deterministic: assert the affected
  paragraph's emitted `text(…)` contains NO intra-paragraph `\n` escape post-fix (collapsed to a
  single space); pre-fix output contains it → assert fails. The symptom is a line-position /
  vertical-layout property pypdf extraction cannot reliably capture — same rationale as Phase 19
  D-06 (pypdf rejected for non-extractable vertical spacing).
- **D-09 (FID-10 / FID-12 / FID-13-boundary → Phase-20 family):** These carry a **pypdf
  extracted-text adjacency assert** on top of the structural floor, because their divergence
  manifests directly in extracted text:
  - FID-10 — assert **all** role tokens (including the trailing ones that were clipped, e.g.
    `:cpp:enumerator:`) are present in the extracted text = no content loss.
  - FID-12 — assert the leaked codly config string (`codly(number-format` / the bare `{` `}`
    wrapper) is **absent** from the extracted prose text.
  - FID-13 boundary — assert **no** stray space before the following period/word (the "… ."
    artifact is absent).
- **D-10 (FID-13-styling / FID-14 verification):** FID-13's color+underline is NOT text-extractable
  → verified by a **structural assert** (the `show link:` rule present in the rendered template +
  `link(…)` emitted for the external ref). FID-14's fix IS text-extractable → assert the abbr
  title string (`(Keyword-only parameters separator` / `(Positional-only parameter separator`) is
  **absent** from the extracted signature text (pypdf, Phase-20 family).
- **pypdf prerequisite:** pypdf is a **test-only** dependency (Phase 20 D-07 introduced the
  adjacency-assert pattern). Confirm it is already a dev dependency before a gate requires it;
  never promote it to a runtime dependency (milestone invariant).

### Claude's Discretion (settled defaults for the un-discussed findings)
- **FID-11 fix site (D-Disc-1):** collapse intra-paragraph source newlines to a single space in
  `visit_Text` for paragraph text, BEFORE escaping. MUST NOT touch `in_literal_block` text
  (already guarded, `translator.py:968`) nor inline `raw()` literal content (which legitimately
  escapes a wrapped-source `\n` to preserve it, `translator.py:1239-1243`), nor explicit hard
  breaks (`line_block`, etc.). Exact whitespace-collapse form (single `\n` vs. `\n`+surrounding
  spaces → one space) is a research/planning detail against real compiles; the intent (collapse
  soft newline to a space, reflow the paragraph) is fixed.
- **FID-12 fix (D-Disc-2):** pure bug fix. The `in_markup_context` guard
  (`translator.py:1582-1587`) wrongly assumes `captioned AND not in_list_item`; its comment
  claims the list-item `{ }` wrapper re-enters code mode inside the figure's `[…]` so the codly
  call is bare again, but the combined captioned + list-item case still leaks. Correct the
  prefix logic so the codly config call executes (carries the leading `#` / is in a real code
  context) in the captioned + list-item case too. Planner settles the exact predicate against a
  real compile of the `extdev/i18n` repro.
- **FID-14 scope (D-Disc-3):** **narrow scope** — suppress the inline abbr-title injection ONLY
  for the auto-generated `*` (PEP 3102) / `/` (PEP 570) separators, per SC#4 which pins only those.
  A genuine `:abbr:` role KEEPS its inline expansion (print has no hover, so the expansion is
  acceptable/useful there — catalogue row 10 explicitly allows this). Rejected the broad scope
  (strip hover-title from ALL `abbreviation` nodes) as over-reaching beyond the SC and the
  finding.
- **Shared-idiom vs. per-finding structure:** these five findings are genuinely independent
  (distinct node handlers, distinct mechanisms) — unlike Phase 19/20 there is no single shared
  root cause. Prefer per-finding edits; a planner may still reuse the Phase 20 "code-mode
  whitespace is cosmetic → emit a real content token" idiom where FID-10's breakable-space fix
  touches the same space-emission machinery.
- **Fixture granularity/placement:** default one render-gate fixture per finding, extending
  existing gate modules where a direct analog exists; consolidation allowed if a shared fixture
  project cleanly exercises multiple findings, provided each finding retains an assertion
  (structural + the D-09/D-10 pypdf assert where applicable) that would FAIL against the pre-fix
  translator.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source of record for every FID finding
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` — the
  audit catalogue. Issue Table **row 6 (F6/FID-10)**, **row 9 (F9/FID-11)**, **row 11
  (F11/FID-12)**, **row 8 (F8/FID-13)**, **row 10 (F10/FID-14)** carry docname + node kind +
  minimal repro + expected `-b html`/`-b text` output + page pointers for each finding.
  Severity-final, human-confirmed at the 17-03 gate. Also read the **Root-cause kinship note
  (lines ~134-142)** for F6↔F12 overflow-family reasoning (binding for D-05) and **D-06**
  (link-flattening is meaning-bearing) and **D-10** (root-cause grouping).

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` §"Residual Fidelity …" (FID-10..FID-14) — requirement text +
  F-number traceability; milestone invariant (zero new runtime deps, no `@preview` bump);
  GATE-01 standing bar.
- `.planning/ROADMAP.md` §"Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F)" — goal, the 5
  success criteria (note SC#1 no mid-token clip/content loss; SC#2 collapse to single space
  corpus-wide; SC#3 no codly-wrapper leak for caption+list-item; SC#4 external-link distinguishing
  styling + correct boundary spacing AND `*`/`/` separators without hover-title text; SC#5 real
  `typst.compile()` fixture + version-sync surface untouched).

### Prior-phase foundation (settled idioms this phase builds on)
- `.planning/phases/20-signature-token-spacing-cluster-b/20-CONTEXT.md` — Phase 20 decisions.
  D-07 established the **pypdf extracted-text adjacency-assert** pattern for horizontal/extractable
  spacing (directly reused here for FID-10/12/13-boundary/14, D-09/D-10).
- `.planning/phases/19-block-separation-fixes-cluster-a/19-CONTEXT.md` — Phase 19 D-05 structural
  `.typ`-assert floor and **D-06 pypdf rejection** for non-extractable (vertical/layout) spacing —
  the precedent for FID-11's structural-only verification (D-08).

### Code + established idioms to reuse (not modify beyond scope)
- `typsphinx/translator.py` — handler sites:
  - `visit_literal` (~1198, emits `raw("…")`; the `self.in_table` ZWSP break-point block at
    ~1224-1236 is the F12 primitive to leave isolated — FID-10, D-04/D-05).
  - `visit_Text` (~952) + `escape_typst_string` (~24, `\n`→`\\n` at line 52) — the FID-11
    soft-newline root cause and fix site (D-08 / D-Disc-1); note the `in_literal_block` guard at
    ~968.
  - `visit_literal_block` `in_markup_context` / `codly_prefix` guard (~1582-1593) — the FID-12
    leak root cause (D-Disc-2).
  - `visit_reference` (~3384) / `depart_reference` (~3561) — FID-13; the external-URL branch emits
    `link("url", …)` at ~3547 (styling delegated to `show link:`, D-01/D-02); the boundary
    stray-space bug lives in the concat/separator handling (D-03).
  - `visit_abbreviation` (~4293) / `depart_abbreviation` (~4301) and `visit_desc_sig_operator`
    (~4870) — the FID-14 abbr hover-title injection sites (D-Disc-3).
- `typsphinx/templates/base.typ` — the DEFAULT template; add the FID-13 `show link:` rule here
  (D-01/D-02). Touch styling only; leave the four `@preview` version declarations byte-unchanged
  (version-sync surface).
- `tests/test_desc_signature_concat_render_gate.py` — the canonical GATE-01 fixture shape
  (emitted-`.typ` structural assert + real `-b typstpdf` compile + `%PDF` magic; invoked via
  `sys.executable -m sphinx`, never `uv run`, per the NixOS-sandbox PATH hazard). Copy this shape;
  add the D-09/D-10 pypdf adjacency asserts where applicable.
- `tests/test_corpus_gate.py` — the standing full-corpus (~684-page) regression gate all changes
  must not regress.
- `tests/test_preview_version_sync.py` — asserts the 3-way `@preview` version-sync agreement; the
  base.typ edit must keep it GREEN.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase 20 pypdf adjacency-assert pattern** — the extracted-text presence/absence assertion
  reused for FID-10 (all tokens present), FID-12 (leaked config absent), FID-13-boundary (stray
  space absent), FID-14 (abbr title absent). (D-09/D-10)
- **Existing `self.in_table` ZWSP break-point primitive** (`translator.py:1224-1236`) — the F12
  overflow fix; kept isolated (D-05), documented here so the planner does NOT accidentally
  re-scope it into FID-10.
- **`escape_typst_string` single choke point** (`translator.py:24`) — the `\n`→`\\n` conversion
  that produces FID-11's hard break; the collapse must happen at the `visit_Text` layer (paragraph
  text only), NOT inside this shared helper (which literals also route through).
- **`show`-rule template extension point** — `templates/base.typ` is where document-wide styling
  belongs; the FID-13 link styling uses a Typst `show link:` rule there rather than per-node
  translator code.

### Established Patterns
- **Code-mode whitespace is cosmetic-only** (Phase 19/20 invariant) — a visible effect needs a
  real content token. FID-10's breakable inter-literal space and FID-11's collapse-to-space both
  live in this family.
- **Markup vs. code mode confusion** (`codly_prefix` `#` guard) — the FID-12 leak is the same
  class as the Phase-15 `block_quote` bug: a bare function call typeset as literal prose in a
  markup context.
- **`link(<label>, …)` for internal, `link("url", …)` for external** (`visit_reference`) — the
  `it.dest` string-vs-label distinction the FID-13 `show link:` rule keys off (D-02).

### Integration Points
- FID-10..FID-12 and FID-14 land in `typsphinx/translator.py` only. FID-13 adds ONE `show link:`
  rule to `typsphinx/templates/base.typ` (styling), with the translator `link()` emission and the
  boundary stray-space fix also in `translator.py`.
- No `builder.py` / `writer.py` / `template_engine.py` changes; the base.typ `@preview` version
  strings stay untouched (version-sync surface).

</code_context>

<specifics>
## Specific Ideas

- FID-13 styling: **color + underline**, applied via a `show link:` rule in `base.typ`, scoped to
  external URLs (`it.dest` is a string) only. Internal cross-refs unchanged.
- FID-10: **boundary-only** breakable-space fix; never break inside a role token; the table ZWSP
  primitive stays `in_table`-gated.
- Verification: FID-11 = structural `.typ` assert only (deterministic: no intra-paragraph `\n`
  escape post-fix); FID-10/12/13-boundary/14 = structural `.typ` assert + real compile + pypdf
  extracted-text adjacency assert; FID-13-styling = `show link:` present structural assert.
- FID-14: narrow scope — `*`/`/` PEP separators only; genuine `:abbr:` keeps inline expansion.
- Every fixture MUST fail against the pre-fix translator and must run a real `typst.compile()`
  producing a `%PDF` (GATE-01). Fidelity authority is `-b html` (secondary `-b text`).
- pypdf is test-only — confirm it is a dev dependency before a gate requires it; never a runtime
  dependency (milestone invariant).

</specifics>

<deferred>
## Deferred Ideas

- **Styling internal cross-references** (color+underline for section/figure refs) — deliberately
  NOT done (D-02); FID-13's finding is external-only. Could be revisited as a future fidelity
  enhancement if internal-ref discoverability in print proves lacking.
- **Extending the table ZWSP break-point primitive to prose / a shared "avoid right-margin
  overflow" primitive** — rejected for this phase (D-05, kinship-note-aligned); revisit only if a
  real compile shows the FID-10 boundary-only fix is insufficient (D-06 escape hatch).
- **Broad abbr-title suppression** (strip hover-title from ALL `abbreviation` nodes) — rejected
  (D-Disc-3); belongs to a separate discussion if genuine `:abbr:` inline expansion is ever
  deemed undesirable in print.
- Issue #117 PDF naming (PDF-01) → Phase 22. The Release phase (version bump + CHANGELOG) →
  final milestone phase. Explicitly out of Phase 21.

None from scope creep — discussion stayed within phase scope.

</deferred>

---

*Phase: 21-Residual Fidelity Fixes (Clusters C/D/E/F)*
*Context gathered: 2026-07-20*
