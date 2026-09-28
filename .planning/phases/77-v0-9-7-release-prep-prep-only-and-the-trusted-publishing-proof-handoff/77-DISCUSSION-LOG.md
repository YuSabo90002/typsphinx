# Phase 77: v0.9.7 Release Prep (prep-only) and the Trusted-Publishing Proof Handoff - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-28
**Phase:** 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
**Areas discussed:** D. Failure branches and rollback placement

Areas offered: A (ATT-04 grep wording alignment), B (`[0.9.7]` section shape), C (provenance
wording), D (failure branches / rollback placement). Owner selected D only, then chose to write
context with A–C at the presented defaults.

---

## D. Failure branches and rollback placement

### Q1 — Upload succeeds but ATT-03 fails (shape ③)

| Option | Description | Selected |
|--------|-------------|----------|
| HALT, fix inside the milestone | Skip ATT-05/DOC-25, record evidence, suspend close, insert 77.1, re-prove on 0.9.8 | ✓ |
| Ship 0.9.7, defer | Close REL-17; move ATT-03/05/DOC-25 to Future | |
| Yank 0.9.7 | Not recommended — missing provenance is not a user-facing defect | |

**User's choice:** 1 (HALT, fix inside the milestone)

### Q2 — Nothing uploaded and re-run cannot fix: 0.9.8 regardless?

| Option | Description | Selected |
|--------|-------------|----------|
| Always 0.9.8 | ATT-06 literal; delete tag locally + origin; no judgement at close | ✓ |
| Branch on upload state | Zero 0.9.7 files on Simple JSON → re-tag 0.9.7; else 0.9.8; AMENDED reading | |

**User's choice:** 1 (always 0.9.8)

### Q3 — When is restoring `password:` used?

| Option | Description | Selected |
|--------|-------------|----------|
| Last resort behind explicit owner approval | Procedure written verbatim; using it makes ATT-03 fail by construction → handled like shape ③ | ✓ |
| Default step of the 0.9.8 path | Ship first, fix TP separately — conflicts with Q1 | |
| Record only | Name it without a procedure or condition | |

**User's choice:** 1

### Q4 — Where does the rollback procedure live?

| Option | Description | Selected |
|--------|-------------|----------|
| Section inside `77-HANDOFF.md` | Keeps SC#4's self-contained reading; ATT-06 evidence = commit SHA + tag-absence probes | ✓ |
| Separate `77-ROLLBACK.md` | Clear ATT-06 boundary, but handoff then depends on a phase file | |
| Both | Drift risk | |

**User's choice:** 1

---

## Claude's Discretion

- A: REQUIREMENTS.md / ROADMAP.md left literal; reframing recorded in CONTEXT; handoff uses the
  two-grep ATT-04 pair from Phase 76 D-08 AMENDED.
- B: lead paragraph (modest upgrade register), Changed = Trusted Publishing, Fixed = MSG-06,
  Known Limitations re-states NUM-01, Verified with measured invariance claims.
- C: mechanism wording + "audit provenance, not an install-time gate"; any PyPI UI description
  measured before written.

## Deferred Ideas

None.
