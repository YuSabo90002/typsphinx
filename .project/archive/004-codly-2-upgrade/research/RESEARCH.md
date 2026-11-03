# Research Handoff

Phase: research
Status: complete
Intent: `.project/intent/INTENT.md`

## Dispatch

- `domain` — skipped → none — no RESEARCH question concerns domain rules or terminology; the Sphinx code-block option semantics are fixed by Sphinx and the existing translator
- `stack` — dispatched → `.project/research/evidence-stack.md` — codly 2.0.0 API fields, codly-languages compatibility and the deps.typ import/export shape decide the implementation
- `pitfalls` — dispatched → `.project/research/evidence-pitfalls.md` — figure kind detection around codly.new and offset/highlight coordinate traps can silently break captioned listings and emphasize-lines
- `similar` — skipped → none — no comparable-product question; the change is an upstream package migration with an official migration guide

## Question assignments

- `` [RESEARCH] Exact codly 2.0 field names/semantics for line numbers off, start number (`offset` value for `:lineno-start: N`), and whole-line highlights relative to offset. `` → `stack`, `pitfalls`
- `` [RESEARCH] Does `figure(codly.new(raw(...)), caption: ...)` keep `kind: raw` auto-detection, or must typsphinx pass `kind: raw`? (User expects it works — codly 2.0 docs show captioned listings; captioned blocks get no SC2 exception either way.) `` → `pitfalls`
- `` [RESEARCH] Is codly-languages 0.1.10 compatible with codly 2.0, and which version is current? `` → `stack`
- `` [RESEARCH] Which names should deps.typ export (`import "@preview/codly:2.0.0" as codly` vs `*`)? `` → `stack`
