---
phase: 17-rendering-fidelity-audit
plan: 03
type: execute
wave: 3
requirements: [AUD-01]
status: complete
---

# 17-03 SUMMARY — Central human confirmation gate (D-01a)

## What was done

The central human gate (D-01/D-01a) of the rendering-fidelity audit. The operator reviewed
Claude's entire 15-row candidate list from Plan 17-02, ruled **accept/reject + final severity**
on every row, resolved all previously-uncertain candidates, and performed a clean-set
spot-check. Results were recorded into `17-AUDIT-CATALOGUE.md` (Task 2), which is now the
human-confirmed evidentiary basis for the Phase 18 FID-01 backlog.

**Per-row disposition (14 accepted / 1 rejected):**

- **Accepted — 14 rows:** F1, F2, F3, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15.
  - Final severities: **1 high** (F12 — wide-table inter-column collision + right-margin clip,
    the Phase 18 FID-01 core), **2 low** (F8 external-reference stray-space; F10 `*`/`/`
    separator abbr-title inline expansion), **11 medium** (the rest).
- **Rejected — 1 row (F4):** "No-contents-entry:/No-index-entry: field-label leak" on
  `usage/domains/c`. Rejected at the gate after verifying (page image PDF p.72 + baselines) that
  the `-b html` authority AND the `-b text` baseline **both** render those labels — the corpus
  deliberately authors `:no-contents-entry:`/`:no-index-entry:` to demonstrate the options
  (`doc/usage/domains/c.rst` §57–62), so the labels are builder-independent (SC#3-style
  out-of-scope), and the only real divergence on that line (concatenation) is already covered by
  F5/F1. Preserved with reason in the new "Rejected candidates" subsection (not deleted).

**Uncertain candidates resolved (D-03 → D-01a):** the 4 rows Claude flagged uncertain
(F4, F6, F8, F10) each received a page-image review at the gate and a final human ruling —
F6/F8/F10 accepted (F6 confirmed as genuine content-loss: `:cpp:enumerator:` clipped off the
right margin on p.85), F4 rejected. Zero rows remain in an undecided state.

**Clean-set spot-check (D-01a miss-rate):** 6 pages across 4 `✅ AUDITED — no issues` docnames
(`usage/quickstart` pp.22,24; `tutorial/describing-code` pp.36,38; `usage/domains/mathematics`
p.89; `man/index` p.300) were re-rendered and reviewed. **0 misses → miss-rate 0/6 = 0%.**
Every known finding visible on the sampled pages belonged to an adjacent non-clean docname
(already flagged) or to the already-accepted systemic F9 — no false "clean" call was found.

## How it was verified

- 17-03 Task 2 automated check passes:
  `grep -qi "miss-rate" 17-AUDIT-CATALOGUE.md && ! grep -qi "uncertain" 17-AUDIT-CATALOGUE.md`
  → confirmations-recorded (miss-rate recorded; every "uncertain" flag/word cleared).
- Active Issue Table = 14 rows, each carrying an explicit `accepted` disposition and a final
  severity of exactly high/medium/low; the rejected F4 lives only in "Rejected candidates".
- Page images for every judged-at-the-gate row (F4/F6/F8/F10/F12) and the 6 spot-check pages
  were reviewed against the `-b html`/`-b text` authorities before ruling.

## Deviations

- The plan's Task 2 automated one-liner scans the whole document up to the first "Excluded"
  string (snagging the earlier SC#3 reference table); scope-restricted verification was used
  instead (documented in 17-02's Task 2 note). No functional impact on the confirmed catalogue.
- This gate was conducted by the orchestrator directly with the operator (page-image review +
  interactive rulings) rather than via a spawned checkpoint sub-agent, then recorded inline —
  the human made every accept/reject/severity decision; no self-approval occurred.

## Output

`17-AUDIT-CATALOGUE.md` is human-confirmed and severity-final. Ready for Plan 17-04: group the
high-severity accepted rows (F12) by root cause and append `FID-01a…` to `REQUIREMENTS.md`,
plus a single medium/low Future-Requirements pointer, then run the five mechanical consistency
checks.
