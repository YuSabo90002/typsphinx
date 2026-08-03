# Phase 37: Signature Typography — the `desc_*` Family - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 37-Signature Typography — the `desc_*` Family
**Areas discussed:** strong wrapper replacement, parameter typography, long-signature overflow
**Areas offered but not selected:** definition of "exactly one break" (SIG-08)

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| パラメータの書体 | SIG-04/05 — reference uses italic proportional params while SIG-05 fixes the delimiters as monospace; DejaVuSansMono-Oblique measured available | ✓ |
| strong ラッパーの置き換え先 | What replaces `strong({...})`; decides where SIG-07/09 hook in and where the Phase 38 boundary falls | ✓ |
| 長い署名のはみ出し対策 | SIG-07 — only break opportunity today is the space inside `text(", ")` | ✓ |
| 「区切り1つ」の定義 | SIG-08 — measured doubled `parbreak()` from nested + outer `depart_desc` | |

**Notes:** Presented alongside four measured facts from a real `-b typst` / `-b typstpdf` / `-b html`
build of a `py:` sample taken in-session.

---

## Newly found defect — scope gate

| Option | Description | Selected |
|--------|-------------|----------|
| このフェーズで直す | Phase 37 rewrites exactly the `desc_optional`/`desc_parameter` handlers where the comma is dropped | ✓ |
| todo に切って先送り | Keep scope strictly to SIG-01..09 and file the defect for later | |

**User's choice:** Fix it in Phase 37.
**Notes:** The defect (`[timeout]**kwargs` vs Sphinx HTML's `[timeout, ]**kwargs`) is covered by no
SIG requirement, so it needs its own criterion/fixture rather than being folded into a SIG-05
assertion.

---

## Area 1 — strong wrapper replacement

| Option | Description | Selected |
|--------|-------------|----------|
| `block(sticky: true, {...})` | Signature becomes its own block; sticky satisfies SIG-09 without touching `desc_content`; block spacing shifts the SIG-08 arithmetic | |
| 素の内容ブロック `{...}` | Strip `strong(` only; smallest diff; no hook for SIG-07/09 on the signature side | |
| Claude が決めて | Decide after measuring SIG-07 corpus signatures and a real page-break experiment | ✓ |

**User's choice:** Claude's discretion (→ CONTEXT D-10).
**Notes:** Both candidates were compiled successfully in-session; the binding constraint recorded is
"must not double-wrap with Phase 38's `desc_content` wrapper".

### Follow-up: 37/38 boundary

| Option | Description | Selected |
|--------|-------------|----------|
| 触らない | `desc_content` stays Phase 38's; SIG-09 solved on the signature side alone | ✓ |
| 最小限なら触ってよい | Allow a `desc_content` wrapper if SIG-09 needs it, with an explicit hand-off note | |

**User's choice:** Do not touch `desc_content` (→ CONTEXT D-09).

### Follow-up: Phase 36 `golden.typ` migration

| Option | Description | Selected |
|--------|-------------|----------|
| 差分だけ手導出して同じ golden を更新 | Hand-rewrite only the signature lines; the diff itself proves nothing else changed | |
| 36 の golden を凍結し 37 用に新規 | Split the roles per phase; weakens Phase 36's whole-file regression net | |
| Claude が決めて | Choose after measuring the real diff size | ✓ |

**User's choice:** Claude's discretion (→ CONTEXT D-14), with "no copying new output into expected
values" recorded as non-negotiable.

---

## Area 2 — parameter typography

First round (three full-signature renderings compiled with typst 0.15 and shown as PNG):

| Option | Description | Selected |
|--------|-------------|----------|
| 案A 参照踏襲 | Params italic proportional inside monospace delimiters — the LaTeX recipe | ✓ (first round) |
| 案B 全部等幅 | Whole signature monospace, params italic mono | |
| 案C 全部等幅・イタリック無し | Params distinguished from the name by weight only | |

Second round — scope of the italic, after finding that SIG-04 says "including any inline type
annotation" while the rendering shown had italicised only the parameter name:

| Option | Description | Selected |
|--------|-------------|----------|
| A-1 パラメータ名だけ | Type and default stay monospace | |
| A-2 desc_parameter 丸ごと | Matches `\sphinxparam{…} = \emph{…}` applied to the whole node in Sphinx's own LaTeX writer | |

**User's response:** "B だとどうなる？" — asked to see 案B under both italic scopes.

Third round — 案B rendered at both scopes alongside A-2:

| Option | Description | Selected |
|--------|-------------|----------|
| B-1 全部等幅・名前だけイタリック | Name / type / default readable as three layers | ✓ |
| B-2 全部等幅・desc_parameter 丸ごと | Matches SIG-04's wording literally; the name/type boundary disappears | |
| A-2 参照と同一 | Narrowest line, serif italic mixed into monospace | |

**User's choice:** B-1 (→ CONTEXT D-01).
**Notes:** The deciding evidence was `build(docnames: Iterable[str] | None = None, …)` — a realistic
annotation reads as code under B but not under A. Measured widths: A-2 < B-1 ≈ B-2.

---

## Area 3 — long-signature overflow (SIG-07)

Four strategies rendered on A4 with 2.5 cm side margins, plus a 9 cm forced-overflow probe:

| Option | Description | Selected |
|--------|-------------|----------|
| hanging-indent ＋ ドットに U+200B | Comma wrapping with a stepped continuation, plus break opportunities in unbreakable dotted names | ✓ |
| hanging-indent のみ | Skip U+200B unless the real corpus proves it necessary | |
| Claude が決めて | Decide from the corpus signature-length distribution | |

**User's choice:** hanging-indent + U+200B (→ CONTEXT D-06, D-07).
**Notes:** `grid(columns: (auto, 1fr))` — the direct analogue of LaTeX's `\py@sigparams` parbox —
measured worst of the four and was rejected on the rendering. Font shrinking was ruled out.

### Follow-up: where the indent constant lives

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 37 で共有定数を導入、38 が使う | First writer of the number owns it; structurally prevents a second definition | ✓ |
| 37 はローカル値、38 で統合 | Phase responsibility matches requirement ownership exactly | |

**User's choice:** Introduce the shared constant in Phase 37 (→ CONTEXT D-08).

### Follow-up: U+200B injection scope

| Option | Description | Selected |
|--------|-------------|----------|
| desc_addname のドットの後だけ | Only the site measured to overflow | |
| 長いドット名全般（型注釈も含む） | Also dotted type annotations | ✓ |
| Claude が決めて | Pick the minimum after measuring the corpus | |

**User's choice:** All long dotted names, type annotations included (→ CONTEXT D-07).

---

## Claude's Discretion

- **SIG-08 — the definition of "exactly one break"** (area offered, not selected). CONTEXT D-12
  records the measured cause: `depart_desc` emits an unconditional `parbreak()` for both the nested
  and the outer `desc`.
- **SIG-06 — the arrow glyph.** Never raised in discussion; CONTEXT D-13 records U+2192 as the
  default, verified to compile and to survive `pypdf` extraction.
- **The replacement wrapper** (D-10) and **the `golden.typ` migration strategy** (D-14), both with
  binding constraints recorded.

## Deferred Ideas

None. The discussion stayed inside SIG-01..09 plus the `desc_optional` comma defect, which lives in
the handlers this phase rewrites.
