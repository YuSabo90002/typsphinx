---
phase: 21
slug: residual-fidelity-fixes-clusters-c-d-e-f
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-20
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from 21-RESEARCH.md `## Validation Architecture` (all mechanisms proven against real `typst.compile()` this research session).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`); real-compile GATE-01 fixtures shell out via `sys.executable -m sphinx -b typstpdf` (NEVER `uv run`, per the NixOS-sandbox PATH hazard) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest tests/test_<finding>_render_gate.py -x` (per-finding, once fixtures exist) |
| **Full suite command** | `uv run pytest` (excludes `-m slow` corpus gate by default) |
| **Estimated runtime** | ~a few seconds per per-finding render gate (single real compile each); corpus gate (`-m slow`) is minutes |

---

## Sampling Rate

- **After every task commit:** Run the specific finding's `test_<finding>_render_gate.py` (fast, single fixture, real compile)
- **After every plan wave:** Run all Phase 21 render-gate modules together
- **Before `/gsd-verify-work`:** Full suite green (`uv run pytest`) + `tests/test_corpus_gate.py -m slow` (~684-page corpus regression) + `tests/test_preview_version_sync.py` all GREEN
- **Max feedback latency:** seconds for per-finding gates

---

## Per-Finding Verification Map

Task IDs are assigned during planning; this map is keyed by requirement/finding and lifted into per-task `<automated>` verify blocks.

| Req ID | Behavior | Verification Method (D-07..D-10) | Automated Command | File Exists |
|--------|----------|----------------------------------|-------------------|-------------|
| FID-10 | Long inline-`literal` run wraps at token boundaries; no mid-token clip; all role tokens present (no content loss) | structural `.typ` assert (conditional leading ZWSP present in `raw(...)` for colon-prefixed tokens) + real compile + pypdf adjacency assert (all role-token strings present) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` → pypdf extract | ❌ Wave 0 |
| FID-11 | Intra-paragraph soft newline collapses to a single space (no hard break) | structural `.typ` assert ONLY — assert NO intra-paragraph `\n` escape in the affected `text(...)` call (D-08: pypdf NOT used, non-extractable vertical property) + real compile | `sys.executable -m sphinx -b typstpdf <fixture> <build>` | ❌ Wave 0 |
| FID-12 | Captioned code block in a list item does NOT leak the codly config wrapper as visible text | structural `.typ` assert (wrapper opening is `#{` in the captioned+list-item case) + real compile + pypdf adjacency assert (`codly(` / bare `{`/`}` wrapper text ABSENT from extracted prose) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` → pypdf extract | ❌ Wave 0 (extend/`codly_config_leak_render_gate` or new) |
| FID-13 (styling) | External reference gets `show link:` styling; internal ref unaffected | structural assert (`show link:` rule present in rendered `base.typ`; `link("url", …)` emitted for external ref) + real compile (D-10: no pypdf, non-extractable visual property) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` | ❌ Wave 0 |
| FID-13 (boundary) | No stray/double space before a following period/word after a named external reference | structural `.typ` assert (no leading `\n` before `#label(...)` in `visit_target`) + real compile + pypdf adjacency assert (single space, not double, before following text) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` → pypdf extract | ❌ Wave 0 (may share FID-13 styling fixture) |
| FID-14 | `*`/`/` PEP-separator abbr hover-title text absent from signature; genuine `:abbr:` STILL expands inline | structural `.typ` assert (no explanation text for astext()=="*"/"/"; explanation STILL present for a genuine `:abbr:` in the same fixture) + real compile + pypdf adjacency assert (title strings absent for `*`/`/`, present for genuine `:abbr:`) | `sys.executable -m sphinx -b typstpdf <fixture> <build>` → pypdf extract | ❌ Wave 0 |

*Every fixture MUST fail against the pre-fix translator and produce a valid `%PDF` (GATE-01).*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/<fid10>/` (conf.py + index.rst) — long inline-literal-role run repro (colon-prefixed role-name tokens as literal double-backtick markup), matching audit `usage/domains/cpp` p.85
- [ ] `tests/fixtures/<fid11>/` — a paragraph with a source-level soft line break with no other inline markup at the break point (single-merged-`Text`-node shape); plus a break inside an inline-literal-adjacent context
- [ ] `tests/fixtures/<fid12>/` (or extend `codly_config_leak_render_gate`) — a captioned `code-block` nested inside a numbered-list `list_item` (`extdev/i18n` p.232 shape)
- [ ] `tests/fixtures/<fid13>/` — an external named reference (`` `text <url>`_ ``) immediately followed by a period with an intervening RST-boundary space, PLUS a same-document internal reference (tests D-02 scoping in one compile)
- [ ] `tests/fixtures/<fid14>/` — a `py:function` signature with a `*` (keyword-only) AND `/` (positional-only) separator, PLUS a genuine `:abbr:` role usage (tests D-Disc-3 in one compile)
- [ ] `tests/test_corpus_gate.py` — no new file; re-run at phase gate (`-m slow`) to confirm none of the five fixes regress the ~684-page corpus
- [ ] Confirm `pypdf` is present in `[project.optional-dependencies].dev` (already true per research — 6.14.2); never promote to runtime

*Canonical fixture shape to copy: `tests/test_desc_signature_concat_render_gate.py` (emitted-`.typ` structural assert + real `-b typstpdf` compile + `%PDF` magic).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual confirmation of color+underline link styling in a rendered PDF (beyond the structural `show link:` presence assert) | FID-13 (styling) | Rendered visual appearance is non-extractable; rasterization was explicitly rejected as a REQUIREMENT (Phase 19 D-06). The structural assert is the automated floor. | Optional: open the compiled fixture PDF and confirm external link renders colored+underlined, internal ref does not. Not a gate. |

*All GATE-blocking behaviors have automated verification (structural + pypdf where extractable).*

---

## Security Notes (from RESEARCH.md §Security Domain)

- **No new threat surface.** All five fixes narrow/correct existing rendering behavior; none adds a new author-controlled data path into emitted `.typ`.
- **V5 Input Validation** remains covered by the single choke point `escape_typst_string` (`translator.py:24-55`). FID-11's `\n`→`" "` collapse runs BEFORE escaping (does not bypass it); FID-14's explanation text still routes through `visit_Text` → `escape_typst_string` (only the emit CONDITION changes); FID-10's ZWSP is a Python-side constant `chr(0x200B)`, not node-derived; FID-12's prefix fix touches only fixed `#`/`""` literals; FID-13's `#label(...)` id stays routed through existing `_namespace_label` sanitization.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING fixture references (5 new render-gate fixtures)
- [ ] No watch-mode flags
- [ ] Feedback latency < ~seconds for per-finding gates
- [ ] `nyquist_compliant: true` set in frontmatter (by validate-phase)

**Approval:** pending
