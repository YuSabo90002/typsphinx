---
phase: 37
slug: signature-typography-the-desc-family
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-01
---

# Phase 37 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time** — 8 of the 9 plans (`37-01` … `37-08`) carry a
parseable `<threat_model>` block; `37-09` (the post-Wave-3 spacing gap-closure plan) does not.
Audit mode: verify declared mitigations exist in the implementation — not a fresh threat scan.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `.rst` / docstring source → translator | Author-controlled build-time text; the only external input this phase touches | Documentation prose, API signature text (names, annotations, parameter defaults) |
| translator → emitted `.typ` string literal | Where unescaped text would become Typst syntax | Escaped string literals produced by `escape_typst_string` |
| emitted `.typ` → `typst.compile()` | Local, in-process compile of locally-generated source; no network | Generated Typst source |
| cached Sphinx `doc/` corpus → builders | Third-party source rendered through the full pipeline in the slow-marked corpus gate (1,445 real signatures) | Third-party reStructuredText |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-37-01 | Tampering | Typst string-literal injection via unescaped signature text | medium | mitigate | `escape_typst_string` is the sole escaping helper (`typsphinx/translator.py:32`); `_escape_signature_text` (`:1064`) calls it at `:1090` and injects ZWSP at `:1091` — escape-then-inject order confirmed, so injection cannot re-open an escaped sequence. Both new user-text sites route through it (`_emit_signature_leaf_wrapper` `:1115`, `visit_Text`'s signature branch `:1168`); every other new emission is a hardcoded literal. No second escaping helper exists in `typsphinx/`. | closed |
| T-37-02 | Information disclosure | none — no new network, file, subprocess, or dependency surface | low | accept | Verified mechanically, not on trust: `git diff 5a9b08f^..HEAD -- typsphinx/` adds zero lines matching `import\|subprocess\|open(\|urllib\|requests\|socket\|eval(\|exec(`; `pyproject.toml` byte-unchanged. See Accepted Risks Log R-37-01. | closed |
| T-37-03 | Tampering | SIG-07 probe concatenates a `context` measurement block onto the emitted `.typ` before compiling | low | mitigate | `tests/test_signature_overflow_render_gate.py:186` — `probe_source = base_source + "\n" + …`: the emitted `.typ` is appended to, never edited, so the artifact under test stays the translator's own output. Deviation from the plan's wording noted below (see Audit Notes). | closed |
| T-37-04 | Repudiation | An expected string fitted to the new code's output rather than derived from the specification would silently launder the phase's evidence | high | mitigate | Ordering verified by `git log --reverse`: `6ca21d6` (37-01 gate) and `fd16d73` (37-04 golden hand-derivation) both precede every translator-emission commit, so no output existed to copy. `golden.typ` was touched exactly twice in the phase (`fd16d73` pre-implementation, `76324bf` wrapper literal) — Waves 37-06/37-07 changed signature emission substantially without touching it, i.e. the hand-derived expectation matched output on first build. 37-09's golden change is byte-identical to `37-EMISSION-CONTRACT.md` §3's amended string and to `typsphinx/translator.py:4963-4964`. `37-GATE-EVIDENCE-04.md:16,26,37` corrects the plan's own miscounted check rather than the evidence. | closed |
| T-37-05 | Denial of service | `depart_desc` suppressing a structurally-required break, merging two `desc` blocks into one run of text | medium | mitigate | `typsphinx/translator.py:4851` — `if not self.in_table and self._desc_break_marker == len(self.body): return`; marker set only on emission (`:4854`). Named pins present and green: `tests/test_signature_break_and_arrow_gate.py:222` (content-follows-nested-member), `:254` (sibling body-less control). | closed |
| T-37-06 | Tampering | The `len(self.body)` marker mis-firing inside a table cell, where `add_text` routes elsewhere | low | mitigate | Explicit `not self.in_table` guard retains the pre-phase unconditional behaviour inside tables (`typsphinx/translator.py:4851`, contract §8). | closed |
| T-37-07 | Information disclosure | A resolved cross-reference silently losing its hyperlink while keeping its glyphs | medium | mitigate | `is_leaf` computed at `typsphinx/translator.py:5686`; rules 1/2 require it and rule 3 is a genuine no-op, so children dispatch under `in_signature_text` and the unmodified `visit_reference` still fires. The assertion targets the link call, not the type-name substring: `tests/test_signature_typography_gate.py:407` asserts `link(<index:Foo>, raw("Foo"))`. | closed |
| T-37-08 | Denial of service | The `desc_signature` block wrapper's vertical spacing inflating every signature and compounding across a document | medium | mitigate | **Declared mitigation reversed in Wave 4.** The explicit `above: 0pt, below: 0pt` zeroing is absent — the wrapper is `block(sticky: true, par(hanging-indent: 2.5em, {` (`typsphinx/translator.py:4963-4964`), reversed in `76324bf` because the zeroing caused every signature's glyphs to overlap its own body (`37-SPACING-FINDING.md`). Partial replacement present: exact-emission pins on the wrapper literal (`tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ:26,36,40,43,59` under `tests/test_desc_rubric_decoupling_render_gate.py:241`; `tests/test_translator.py:3384`) break immediately on any future `above:`/`below:` edit. The threat does not materialise empirically (auditor A4 measurement: `signature_typography_gate` 13 wrappers → 4 pages shipped and zeroed; `signature_break_and_arrow_gate` 9 wrappers → 3 pages both). **Remaining gap:** the named pin, `test_page_count_does_not_inflate`, had its baseline re-pinned 6→7, moving its firing point from ≥0.9em to ≥16em (~10× the current default), and its fixture holds exactly one signature so it never measured compounding. No committed assertion pins rendered vertical spacing or multi-signature page count. | open — below `high` threshold (non-blocking) |
| T-37-09 | Tampering | An unbalanced optional-group bracket aborting the entire Typst compile rather than failing one assertion | medium | mitigate | `visit_desc_optional` emits one `raw("[")` (`:5293`); `depart_desc_optional` emits the D-11 separator **before** the close (`:5327`, `:5329`) — bracket count unchanged. Nested-optional compiled-PDF control `tests/test_signature_break_and_arrow_gate.py:445`; its compile helper states and honours "no `try`/`except`" (`:120-125`), so a mismatch aborts loudly. | closed |
| T-37-10 | Tampering (supply chain) | A new runtime dependency or a new `@preview` package slipping in | high | mitigate | `git diff 5a9b08f^..HEAD -- pyproject.toml` empty. `find typsphinx -name "*.typ"` → only `templates/base.typ`; the phase added no `.typ` under the package. `uv run pytest tests/test_preview_version_sync.py` → 3 passed (the three lockstep sites agree). No package-manager install occurs anywhere in this phase, so the package-legitimacy gate has nothing to audit. | closed |
| T-37-11 | Denial of service | A font selection silently shadowing the Japanese build's CJK fallback — Typst emits neither a warning nor an error | medium | mitigate | `grep -rn "font:" typsphinx/` → no match anywhere in the package; D-04 makes the monospace primitive the only mechanism and no handler in this phase names a font. | closed |

*Status: open · closed · open — below {block_on} threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

`workflow.security_block_on: high` — T-37-08 is medium, so it is open but does **not** count toward
`threats_open` and does not block phase advancement.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-37-01 | T-37-02 | This phase adds styling to already-parsed, already-escaped content. No new network, file, subprocess, or dependency surface; milestone invariants #1 (zero new packages) and #5 (four `@preview` packages) hold. Verified by an empty `pyproject.toml` diff and a keyword scan over the `typsphinx/` diff. | Plan-time disposition (`37-01` … `37-08` threat models), confirmed by audit | 2026-08-01 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-01 | 11 | 10 | 1 (medium — non-blocking) | gsd-security-auditor (opus), ASVS L1, `block_on: high` |

## Security Audit 2026-08-01

| Metric | Count |
|--------|-------|
| Threats found | 11 |
| Closed | 10 |
| Open | 1 |
| Open at or above `high` (blocking) | 0 |

### Audit Notes

- **T-37-08's declared mitigation was reversed, on measured grounds.** `37-09` dropped
  `above: 0pt, below: 0pt` after re-measuring: the zeroing produced exactly 0pt on both sides
  (glyph overlap), while Typst's own default produces 13.2pt, byte-for-byte identical to plain
  paragraph flow. The reversal is correct; what did not survive with it is the *pin*. The
  auditor extended `37-GATE-EVIDENCE-09.md` §3.3's sweep past its 1.2em stopping point and
  measured the guard's post-re-pin firing point at ≥16em, against ≥0.9em before. The recorded
  justification's claim that the test "still catches … a per-signature spacing regression" is
  technically true and practically near-vacuous.
- **The 6→7 re-pin is a legitimate re-measurement, not evidence laundering** — T-37-04 stays
  closed. The requirement-bearing assertion (`test_primary_signature_and_body_share_a_page`)
  was untouched and green; the value 7 reproduced independently; disclosure is maximal
  (constant comment, test docstring, commit message, two gate-evidence sections, plus a filed
  todo). One factual correction for the record: the constant's comment says baseline 6 "is not
  reachable once SIG-09 is genuinely fixed"; measured, 6 *is* reachable with SIG-09 fixed — the
  accurate statement is "not reachable with SIG-09 fixed **and** non-zero spacing".
- **`37-09-SUMMARY.md`'s `## Threat Flags` under-reports.** It reads "None — the only production
  code change is dropping two named arguments … already reviewed under Phase 37's threat
  register." Dropping those two arguments *is* the reversal of T-37-08's declared mitigation.
  The reversal is documented thoroughly elsewhere (contract §3, `37-SPACING-FINDING.md`, gate
  evidence), but the threat-flag channel — the first thing this audit reads — said "None".
- **T-37-03 wording deviation (immaterial).** The plan says the probe suffix contains "no
  fixture-derived text"; in fact the `#context [SEG{i}WIDTH=…]` lines do carry fixture-derived
  segments, escaped by a local two-replace escaper at
  `tests/test_signature_overflow_render_gate.py:182`. Test-only — it never reaches the shipped
  artifact — so the threat stays closed, but the mitigation text overstates.
- **`golden.typ` phase-wide diff is 9 physical lines across 5 signatures**, not the 5 cited in
  `37-GATE-EVIDENCE-09.md` §3.2 — that figure describes plan 09's own commit, which is exactly
  the 5 wrapper-open lines. The rubric/plain-bold control, every `par({text(…)})` body, all
  `[#metadata(none) <…>]` anchors, and all `linebreak()`/`parbreak()` lines are byte-unchanged.
- No unregistered attack surface appeared — every new emission maps to a registered threat.

### What would close T-37-08

Add a committed multi-signature page-count assertion at real geometry — the
`signature_typography_gate` fixture (13 wrappers, measured at 4 A4 pages) — which is the
compounding detector the register named and the suite lacks. Optionally re-tighten the SIG-09
guard, or retire its inflation claim and let it assert only what it can
(`test_primary_signature_and_body_share_a_page` already carries SIG-09). Relevant because the
phase moved from an explicitly pinned spacing value to inheriting Typst's upstream default: a
`typst-py` bump changing default block spacing would inflate every signature in every document,
with only the ≥16em guard standing — and this repo re-resolves dependencies weekly via
`drift.yml`.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed (T-37-08 open at medium, below the `high` block threshold)
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-01
