# Phase 40: Citations — Full Round Trip - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-02
**Phase:** 40-Citations — Full Round Trip
**Areas discussed:** Back-reference policy (owner-initiated), Reference-list layout, Back-reference
placement, Single-back-reference form, Cross-document scope and SC#3, `examples/charged-ieee/`
restoration scope

---

## Back-reference policy (raised by the owner before the gray-area menu)

The owner rejected the first gray-area menu and asked what a back-reference actually is, given that
a docutils citation — unlike a bibliography — is just prose quoted inline. Both of Sphinx's own
builders were measured and shown:

| Builder | Measured output for the same probe |
|---|---|
| HTML | `<span class="label">[Krizhevsky2012]</span><span class="backrefs">(<a href="#id1">1</a>,<a href="#id2">2</a>)</span>`; with one citing site instead, `[<a href="#id3">Forward2020</a>]` |
| LaTeX | `\begin{sphinxthebibliography}{Krizhevs}` + `\bibitem[Krizhevsky2012]{index:krizhevsky2012}` — no back-references at all |

**User's choice:** HTML 準拠 — back-references are rendered.
**Notes:** The owner then asked whether reproducing HTML forces building a Typst
`bibliography()`, since that is Typst's only reference-section construct. Answered by compiling a
probe: `link()` + `<label>` produced four `/Link` annotations in the PDF (two forward, two backward,
the back-link destinations byte-matching the citing sites' measured x positions), so no bibliography
machinery is involved. `bibliography()` was additionally shown to be incompatible with CIT-06's
"document order, unsorted" because it CSL-formats and reorders, and it was already ruled out at
v0.7.0 scoping.

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| 参照リストの組み方 | How CIT-02's hanging indent is realized | ✓ |
| 文書横断引用と SC#3 | SC#3's "every citing location" vs the measured same-document `backrefs` | ✓ |
| charged-ieee の復元範囲 | Verbatim restore vs expanded sample | ✓ |

**User's choice:** all three.

---

## Reference-list layout

| Option | Description (all figures measured this session via pypdf) | Selected |
|--------|-------------|----------|
| 1つの grid にまとめる | Consecutive citations in one `grid(columns:(auto,1fr))`; every body at x=104.35, past the longest label. Same idea as LaTeX's `sphinxthebibliography{Krizhevs}`. Cost: run detection | ✓ |
| エントリごとの grid | One grid per entry; bodies at x=104.35 and x=62.58 — CIT-02 holds per entry, ragged left edge across the list | |
| 固定値で下げる | `par(hanging-indent:)`; continuation lines share x=47.5 at 2.5em, but `[Krizhevsky2012]` is 84pt so they sit inside the label. HTML's own 4em=44pt fails the same way | |

**User's choice:** 1つの grid にまとめる
**Notes:** Selected against a measured preview. The accepted consequence — a non-citation node
between two citations breaks the run and the next run realigns — is recorded as D-06 rather than
left to be rediscovered as a bug.

---

## Back-reference placement

| Option | Description (base: body at x=104.35) | Selected |
|--------|-------------|----------|
| ラベルの直後（HTML と同じ） | Left column carries `[Label] (1,2)`; column widens 21.95pt, body moves to x=126.3, and under the single-grid choice every entry moves, including ones with no back-references | ✓ |
| ラベルの下に別行 | `(1,2)` on its own line inside the left column; column width unchanged, body stays at x=104.35; entry may grow a line | |
| エントリ本文の末尾 | `(1,2)` trails the body at x=274.8; body stays at x=104.35 but the marker's position moves per entry and does not match HTML's order | |

**User's choice:** ラベルの直後（HTML と同じ）
**Notes:** The 21.95pt push-out was shown as a measured cost before the choice, together with the
fact that the single-grid decision propagates it to every entry.

---

## Single-back-reference form

| Option | Description | Selected |
|--------|-------------|----------|
| HTML の作法に従う | One citing site → no `(1)`; the label text itself becomes the back-link, matching Sphinx HTML's measured `[<a href="#id3">Forward2020</a>]`. Cost: label has two emission shapes | ✓ |
| 常に (n) を出す | One emission shape, link position uniform across entries; diverges from HTML | |

**User's choice:** HTML の作法に従う
**Notes:** Raised because the previous question's preview had shown `[Li2001] (1)`, which
contradicted the already-locked "HTML 準拠". Flagged and settled rather than left inconsistent.

---

## Cross-document scope and SC#3

| Option | Description | Selected |
|--------|-------------|----------|
| SC#3 を実測に合わせて補正 | Scope the guarantee to `backrefs` (same-document), matching CIT-04's own wording and HTML; amend ROADMAP SC#3 with a Roadmap Evolution record, as Phase 36 SC#3 and Phase 39 D-12 did | ✓ |
| 文書横断の逆参照も張る | A typsphinx-owned env-wide index giving back-references neither HTML nor LaTeX provides; needs a new cross-document pre-pass and a rewrite of CIT-04 | |

**User's choice:** SC#3 を実測に合わせて補正
**Notes:** Driven by the measurement that `index.rst`'s definition carries `backrefs=['id1','id2']`
— the two index sites only — while the `second.rst` citing site is absent.

| Option | Description | Selected |
|--------|-------------|----------|
| 残す（用途を変える） | Keep the 2-document fixture, repurposed to prove cross-document forward-link resolution and that a duplicate key separates into `index:same2020` / `second:same2020` | ✓ |
| 単一文書に絞る | One document, forward reference and repeat citation only; leaves both measured hazards unverified | |

**User's choice:** 残す（用途を変える）

---

## `examples/charged-ieee/` restoration scope

| Option | Description | Selected |
|--------|-------------|----------|
| 逐語復元＋コメント削除 | Restore exactly what `8bed1a3` / `c014a0b` removed. Small, legible diff. Cost: one entry and one citing site, so neither `(1,2)` nor the widest-label alignment is visible in the sample | ✓ |
| 実在文献で拡張 | Add the real papers already named in the sample's prose (VGGNet, ResNet); exercises every decided shape but means writing new sample text | |

**User's choice:** 逐語復元＋コメント削除
**Notes:** The owner preferred the diff to read as restoring what was broken; feature demonstration
belongs in the phase's own fixtures.

| Option | Description | Selected |
|--------|-------------|----------|
| 完全に同一に戻す | Deleting both "no citations" comments makes `index.rst` identical across approaches, leaving template wiring as the only intended difference | ✓ |
| 差分を持たせる | Make one approach's citations heavier to compare rendering across templates; blurs the comparison's intent | |

**User's choice:** 完全に同一に戻す

---

## Claude's Discretion

- Grid `column-gutter` / `row-gutter` values and any extra vertical separation between entries.
- Implementation shape of consecutive-citation run detection (sibling look-ahead vs a pre-pass index).
- Mechanism for anchoring the citing site, subject to the non-regression constraint in D-14.
- Whether `visit_label` is a real handler or the `label` child is skipped positionally.
- Which document the SC#4 document-order assertion is taken from, and its `pypdf` extraction.

## Deferred Ideas

- Cross-document back-references (rejected as D-08; would need an env-wide pre-pass and a CIT-04
  rewrite).
- Expanding `examples/charged-ieee/` into a multi-entry reference list (rejected as D-11).
- CIT-07 — `sphinxcontrib-bibtex` support, where Typst's `bibliography()` becomes the right tool.
