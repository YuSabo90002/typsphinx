# Phase 42: Captioned Table Drops Preceding Target Label - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-03
**Phase:** 42-captioned-table-drops-preceding-target-label
**Areas discussed:** Failing-shape scope, Fix-site choice, Figure handling
**Area offered but not selected:** Phase 41 reconciliation (SC#6) — recorded as Claude's discretion

---

## Area selection

Four areas were offered, each annotated with measurements taken before the question was asked
(reproduction, observed ids at the table departure handler, the no-`:name:` widening, and the
figure path being clean). The owner selected three; the fourth was closed as discretion at the end.

---

## Failing-shape scope

### Question 1 — how wide should the RED gate fixture matrix be?

| Option | Description | Selected |
|--------|-------------|----------|
| All four measured-failing shapes | target + `:name:`, target without `:name:`, table in a list item, two consecutive targets, plus the caption-less byte-invariance control | ✓ |
| Only the reported shape | target + `:name:` plus byte invariance — the literal TBL-03 text | |
| Four shapes + whitespace-title investigation | also determine whether the whitespace-only-title divergence is reachable from rST | |

**User's choice:** All four measured-failing shapes.
**Notes:** The three shapes beyond the report were measured failing during this discussion, so the
choice widens coverage without widening the fix.

### Question 2 — should the id that owns the figure label change when `:name:` is absent?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the current design | first id owns the figure label, remaining ids become metadata anchors | ✓ |
| Promote the human-authored id | select the named id for the figure label and push the auto id to a metadata anchor | |

**User's choice:** Keep the current design.
**Notes:** References are emitted as `link(<label>, …)`, so both anchor forms resolve; promoting the
named id would change output for existing documents with no functional gain.

### Question 3 — how deep should the GREEN-side assertion go?

| Option | Description | Selected |
|--------|-------------|----------|
| Compile success + structural assertions | both labels present, no label defined twice | ✓ |
| Compile success only | RED-to-GREEN flip only | |
| Also verify the PDF | add a `pypdf` page-count and extracted-text check | |

**User's choice:** Compile success + structural assertions.
**Notes:** Typst link destinations do not appear in extracted PDF text, so the PDF adds little here.

### Question 4 — how is the caption-less path's byte invariance proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Empty diff between two real builds | pre-fix and post-fix SHAs named in an evidence file, as in Phase 36 SC#2 | ✓ |
| Committed golden `.typ` | permanent comparison test, higher maintenance | |
| Both | diff evidence plus a committed golden | |

**User's choice:** Empty diff between two real builds.

---

## Fix-site choice

### Question 1 — where does the fix land?

| Option | Description | Selected |
|--------|-------------|----------|
| Call ordering inside the table departure handler | move the anchor call after the in-table flag is cleared; blast radius is the captioned-table path only | ✓ |
| Force body-direct emission via a new helper argument | avoids the ordering dependency but diverges from the other 20 call sites | |
| Harden `add_text` or the helper itself | structurally prevents misrouting, but an unconditional body target would break in-cell targets | |

**User's choice:** Call ordering inside the table departure handler.
**Notes:** Presented alongside the measurement that a target placed inside a table cell routes
correctly into the cell content today, which rules out the blanket hardening option.

### Question 2 — sweep the repo for the same misrouting?

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep; findings become todos only | keeps Phase 42's change to the one table site | |
| Sweep and fix findings here | risks fixture sprawl | |
| Do not sweep | shortest, but a sibling defect stays invisible | |

**User's choice (free text):** Sweep. Findings outside the image path become todos only; a finding
in the **image** path is fixed inside this phase.
**Notes:** This is a narrowing of the second option to a single named path, not either preset.

### Question 3 — how to treat the pre-measurement showing the image path is clean?

| Option | Description | Selected |
|--------|-------------|----------|
| Re-take it formally during the sweep | scratchpad measurement is reference only | ✓ |
| Also add a permanent image regression gate | matches the figure treatment | |
| Close it as already measured | depends on an unrecorded measurement | |

**User's choice:** Re-take it formally during the sweep.

### Question 4 — how to treat the out-of-scope whitespace-only-title divergence?

| Option | Description | Selected |
|--------|-------------|----------|
| File a todo | record the divergence and that rST reachability is unverified | ✓ |
| Check reachability during the sweep | close it either way inside this phase | |
| Do nothing | leave no record | |

**User's choice:** File a todo.

---

## Figure handling

### Question 1 — how much figure-side testing?

| Option | Description | Selected |
|--------|-------------|----------|
| Permanent regression gate | fixture plus test locking in that figures emit both labels | ✓ |
| Recorded measurement only | SC#2 asks only that the question be answered either way | |
| Fold figure rows into the table fixture | fewer files, but a table-gate failure hides the figure result | |

**User's choice:** Permanent regression gate.
**Notes:** Phase 25 modelled the table path on the figure path, so the gate guards against the
reverse contamination later.

### Question 2 — what does the figure gate cover?

| Option | Description | Selected |
|--------|-------------|----------|
| The three measured shapes | `:name:` + target, no-`:name:` + target, figure in a list item | ✓ |
| All four table shapes | adds two consecutive targets, which was never measured for figures | |
| One representative shape | cheapest, but leaves the auto-id-owns-label shape unguarded | |

**User's choice:** The three measured shapes.

---

## Claude's Discretion

- **SC#6 reconciliation with Phase 41.** Offered as a fourth area, not selected; the owner accepted
  the proposal as stated — add the TBL-03 line to the unreleased `## [0.7.0]` CHANGELOG section,
  re-measure the SC#4 invariant sweep over a range that includes Phase 42 into a **new** evidence
  file under this phase rather than editing `41-*` artifacts, and revert any `phase.complete`
  auto-flip of the REL-04 / REL-05 checkboxes before committing.
- Fixture layout, test module naming, plan and commit granularity.

## Deferred Ideas

- Whitespace-only table title: the visit-side and depart-side captioned checks disagree, so no
  anchor may be emitted on either path — todo to be filed, not fixed here.
- Any non-image misrouting the sweep discovers — todo only.
- Promoting the human-authored id to the figure label — rejected for this phase.
