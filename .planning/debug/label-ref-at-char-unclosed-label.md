---
status: fixing
trigger: "Corpus gate fatal #10: TypstError: unclosed label at usage/domains/c.typ:311 (also directives.typ, authors.typ). C-domain anonymous entities (@data/@alias) produce docutils ids containing '@' (e.g. c.Data.@data.a); translator emits them verbatim as Typst labels/refs. '@' is invalid in a Typst label token -> unclosed label."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "The translator emits Typst label NAMES (in <...> anchors, #label(\"...\") strings, and link(<...>, ...) refs) directly from docutils node ids without sanitizing the id to Typst's valid label charset. Typst 0.15 labels accept ONLY [A-Za-z0-9_-.:] (empirically verified). Docutils ids for Sphinx C-domain anonymous entities (@data/@alias) contain '@' (e.g. c.Data.@data.a). An anchor `[#metadata(none) <c.Data.@data.a>]` and a reference `link(<c.Data.@data.a>, ...)` both emit the raw '@', which Typst cannot parse as a label token -> 'unclosed label' aborts the whole compile."
  confirming_evidence:
    - "Empirical typst 0.15 test: '@' (and /,+,#,*,?,!,~,%,&,=,space,punct) are INVALID in <label>; only [A-Za-z0-9_-.:] valid. Leading '.'/':' also invalid; '_',digit,'-',letter valid as leading."
    - "Bug #9 resolution note documents the pre-existing #10 fatal: link(<c.Data.@data.a>, ...) with '@'; 3 corpus files carry @-labels (usage/domains/c.typ, usage/restructuredtext/directives.typ, authors.typ)."
    - "grep of translator.py finds 15 label/ref NAME emission sites, all deriving the name from a docutils id/name verbatim (node ids, refid, refuri[1:], names[0], fn-<refid>)."
  falsification_test: "If, after applying a shared _sanitize_label() at every def+ref site, a corpus/fixture id containing '@' STILL emits a raw '@' in <...> OR typst.compile still raises 'unclosed label', the hypothesis/fix is wrong. Also: if the anchor's sanitized name != the reference's sanitized name for the same id, links break."
  fix_rationale: "One shared _sanitize_label(name) mapping each char outside [A-Za-z0-9_-.:] to a collision-resistant codepoint token '_u{ord:x}_'. Applied at EVERY def AND ref site so the same id sanitizes identically on both sides (def==ref) -> links keep resolving. Codepoint encoding is deterministic + collision-resistant (distinct chars -> distinct tokens), uses only valid label chars, and leaves already-valid ids byte-identical (zero churn/regression on the 155 working files). Addresses root cause (raw id -> label) not a per-file symptom."
  blind_spots: "Leading '.'/':'-only ids would still be invalid, but docutils make_id guarantees letter-leading ids so this cannot arise on the corpus. pending_xref's pre-existing '.'/'_'->'-' transform is a separate unresolved-ref fallback; wrapped in the sanitizer for safety but its links were already best-effort. Verified via full corpus gate re-run."
hypothesis: CONFIRMED (see reasoning_checkpoint)
test: add _sanitize_label helper; apply at all 15 sites; rebuild @-fixture; typst.compile; fast suite + lint; corpus gate
expecting: fixture emits sanitized <c.Data._u40_data.a> in both anchor and link; compiles to %PDF; corpus advances past c.typ:311 unclosed-label
next_action: Implement _sanitize_label and wire all emission sites, then add regression test.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; C-domain anonymous entities (@data/@alias) emit valid Typst labels/refs.
actual: "Typst compilation failed: TypstError: unclosed label" at usage/domains/c.typ:311 (representative). Anchor `[#metadata(none) <c.Data.@data.a>]` and ref `link(<c.Data.@data.a>, ...)` emit a raw '@', invalid in a Typst label token.
errors: "TypstError: unclosed label"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate after bugs #1-#9 unblocked the compile path (masked behind bug #9 at earlier line 107).

## Eliminated

## Evidence

- timestamp: charset-empirical
  checked: typst 0.15 compile of `#[test <a{ch}b>] #link(<a{ch}b>)[ref]` for each candidate char.
  found: VALID in <label> = [A-Za-z0-9_-.:]; INVALID = @ / + # * ? ! ~ $ % & = space , ; ( ) [ ] { } < > ' " \ | ^ `. Leading '.'/':' invalid; leading '_'/digit/'-'/letter valid.
  implication: Sanitizer must replace every char outside [A-Za-z0-9_-.:]. '_u{ord:x}_' tokens use only valid chars and are safe as leading (start with '_').

- timestamp: emission-site-scan
  checked: grep for <, label(, link(, metadata(none) in translator.py.
  found: 15 NAME-emission sites -- DEF: 426/428 (section ids), 1363 (code_block_label), 1368 (code names[0]), 1587 (term id), 1683 (figure id), 1843 (footnote def fn-<refid>), 2194 (#label string), 2232 (target metadata), 2975/3030 (math ids). REF: 1812 (footnote reuse fn-<refid>), 2269 (pending_xref), 2711 (reference refid), 2744 (reference refuri[1:]).
  implication: All derive the name from a docutils id/name; must route every one through _sanitize_label so def==ref.

## Resolution

root_cause: The translator emitted Typst label NAMES verbatim from docutils/Sphinx node ids at 15 sites (anchors <id>, label("id"), link(<id>,...), footnote(<id>)). Typst 0.15 labels accept only [A-Za-z0-9_.:-]; Sphinx C-domain anonymous entities (@data/@alias) produce ids like c.Data.@data.a. The '@' is an invalid label token char -> Typst PARSE error 'unclosed label' aborts the whole compile. (Masked behind bug #9's earlier 'expected expression' parse error; the parse phase aborts before Typst's semantic label-existence check runs, which is why the pre-existing dangling desc-anchor gap did not surface first.)
fix: Added one shared staticmethod _sanitize_label(name) that re.sub-replaces every char outside [A-Za-z0-9_.:-] with a collision-resistant codepoint token '_u{ord:x}_' (@ -> _u40_; uses only valid label chars incl. safe leading '_'; idempotent on already-valid ids so the 155 working files are byte-unchanged). Wired at ALL 15 label/ref NAME sites -- DEFINITIONS: section title primary+extra ids (426/428), captioned-code + :name: code labels (1365/1370), term anchor (1587), figure anchor (1683), footnote def (1848 via the single fn-<refid> derivation at 1800), target #label string (2199) + metadata anchor (2237), inline+block math ids (3036/3091); REFERENCES: footnote reuse (1817 via same derivation), pending_xref (2281, wrapped over its legacy .replace), reference refid branch (2772), reference #refuri branch (2805). Because the SAME function runs on both def and ref sides, a def and its ref sanitize to the identical string -> links keep resolving.
verification: New tests/test_label_at_char_render_gate.py PASSES with fix, FAILS pre-fix (git stash translator.py, both directions) with the exact 'unclosed label' fatal. Synthesized fixture injects (at doctree-resolved, bypassing PropagateTargets) a target anchor + same-document reference both carrying id myapp.@thing.a; emitted .typ has '[#metadata(none) <myapp._u40_thing.a>]' (anchor) and 'link(<myapp._u40_thing.a>, ...)' (ref) -- def==ref proven by grep -- no raw '@' in any <label>, compiles to %PDF. Fast suite 411 passed / 15 deselected (410 prior + 1 new; NO existing expectation updates -- none encoded a raw @-label; test_target_label_render_gate still green -> no anchor regression). black/ruff/mypy clean. Corpus gate: bug #10 FIXED -- corpus advances PAST 'unclosed label'; NOT GATE-02 green. Next distinct fatal #11 = TypstError 'expected semicolon or line break' (a PARSE error, pre-existing, masked behind #10's parse abort; confirmed NOT caused by this fix -- the offending leaf files contain zero _u40_ tokens). 3 leaf files fail on own content (usage/advanced/intl.typ, latex.typ, changes/6.1.typ) + aggregators (index.typ master, changes/index.typ, usage/index.typ). At least TWO distinct root constructs: (a) reference-immediately-followed-by-target inside an inline concat context -- intl.typ:27 `...[#link(...) #label("plantuml")]text(".)")` -- the _in_reference_with_target markup-wrapper closes `]` and juxtaposes the next inline sibling with no `+`/newline separator; (b) nested-list-in-list-item juxtaposition -- changes/6.1.typ:143 `})]` ... `})`. Reported, NOT fixed (distinct construct + error class, bounded scope).
files_changed: [typsphinx/translator.py, tests/test_label_at_char_render_gate.py, tests/fixtures/label_at_char_render_gate/conf.py, tests/fixtures/label_at_char_render_gate/index.rst]
