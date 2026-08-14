# Phase 51: Two-Layer Output Documentation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-14
**Phase:** 51-two-layer-output-documentation
**Areas discussed:** Placement and page structure, Stale-claim sweep scope, How limitations are written, SC#3 verification mechanism

---

## Gray area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Placement and page structure | New page vs. extending `builders.rst` + `configuration.rst`; where "what changed" lives; README in scope | ✓ |
| Stale-claim sweep scope | How far to hunt falsified claims; whether the collision hard-error is documented | ✓ |
| How limitations are written | `:numref:` depth, standalone-compile framing, shared-child behaviour | ✓ |
| SC#3 verification mechanism | Permanent gate vs. throwaway harness; how docs and fixtures share a source | ✓ |

**User's choice:** all four.

---

## Placement and page structure

### Q1 — Where does the two-layer explanation live?

| Option | Description | Selected |
|--------|-------------|----------|
| New page under `user_guide/` | `user_guide/output_layout.rst`, added to the toctree, holding the split, target-as-path, refusals, standalone behaviour, limitations; existing pages link to it | ✓ |
| Extend the two existing pages | Grow `builders.rst`'s Output/Manual Compilation sections and `configuration.rst`'s tuple element 2 | |
| New page + entry-point teasers | The new page plus short teasers in `quickstart.rst` and `index.rst` | |

**User's choice:** New page under `user_guide/`.
**Notes:** Measured context presented — `builders.rst`'s Output sections are four lines each and
`configuration.rst`'s tuple contract is lines 43-79, both plainly smaller than the material.

### Q2 — Where does "what changed from v0.7.x" live?

| Option | Description | Selected |
|--------|-------------|----------|
| `changelog.rst` Migration Guides | New `Migrating from 0.7.x to 0.8.0` subsection following the 0.7.0→0.7.1 pattern (123 lines, before/after code blocks, added in `27cff2af`) | ✓ |
| A section inside the new page | Keeps contract and migration in one read, at the cost of a third place saying the same thing | |
| Both (summary + link) | Two or three lines on the new page pointing at `changelog.rst` | |

**User's choice:** `changelog.rst` Migration Guides.

### Q3 — Is `README.md` in DOC-14 scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Include — false claims only | Fix `README.md:82-85` and `:228`, link to the new page, add no new explanation | ✓ |
| Include — false claims + short two-layer explanation | Also tell PyPI readers to compile the wrapper | |
| Exclude | Leave README to a separate todo; v0.8.0 ships with a false claim on PyPI | |

**User's choice:** Include — false claims only.
**Notes:** Measured — `README.md:82-85` says "each entry produces one emitted `.typ` file", false
after the split; `tests/test_quickstart_docs_gate.py` already reads `README.md` directly.

---

## Stale-claim sweep scope

### Q1 — How wide is the search for falsified claims?

| Option | Description | Selected |
|--------|-------------|----------|
| Repo-wide discovery + fix | grep `docs/source`, `README.md`, `examples/**/README.md` (excluding `.planning/`, `tests/`, `typsphinx/`) and fix everything found | ✓ |
| `docs/source` + `README.md` only | Leave `examples/**` to a separate todo | |
| Named pages only | Fix only the sites named in this discussion | |

**User's choice:** Repo-wide discovery + fix.
**Notes:** Presented measurement — `examples/advanced/README.md:60-64` claims
`advanced-example.typ` uses `#include()` directives; it is now the wrapper including `index.typ`,
with the chapter includes state-guarded inside `index.typ`.

### Q2 — Is the Phase 47 collision hard-error documented under DOC-14?

| Option | Description | Selected |
|--------|-------------|----------|
| Both contract + migration | Refusal rules on the new page, plus a `changelog.rst` migration bullet for `[("index","index.typ",…)]` | ✓ |
| Migration guide only | Keep the new page short; announce only in migration + Phase 52 CHANGELOG | |
| Leave to Phase 52 | SC#1/SC#2 do not name collisions, so out of DOC-14 | |

**User's choice:** Both contract + migration.
**Notes:** Measured — `builder.py:611` raises `ExtensionError("typst: N output path collision(s): …")`
and writes no output file; four claimant kinds; `[("index","index.typ",…)]` builds in v0.7.x and
fails in v0.8.0.

### Q3 — How are the `typst compile build/typst/index.typ` examples fixed?

| Option | Description | Selected |
|--------|-------------|----------|
| Rewrite to the wrapper name that config produces | Derive from each example's own `conf.py`; `<project>.typ` for an unset `typst_documents` | ✓ |
| Point at the builder's own `compile these:` line | No hard-coded names; fewer copy-pasteable commands | |
| Both | Concrete names plus one generic "look at the build output" recipe | |

**User's choice:** Rewrite to the wrapper name that config produces.
**Notes:** Measured — while a docname `index` exists, `index.typ` is always the content file, since
a target of `index.typ` for docname `index` is the self-collision the validator refuses. The
current commands therefore silently produce a child-less PDF.

---

## How limitations are written

### Q1 — How deeply is the `:numref:` divergence documented?

| Option | Description | Selected |
|--------|-------------|----------|
| Symptom + mechanism + detection | Symptom first, then why (Sphinx numbers once from `root_doc`; Typst counts per wrapper), plus the build-log warning as a detection signal | |
| Symptom only | One sentence stating the numbers can disagree | |
| Verbatim measured table | Reproduce the Phase 49 two-master measurement table | |
| *(free text)* | 「いずれ直すバグっぽい挙動なので文章に特筆しない」 | ✓ |

**User's choice:** free text — do not call it out in the documentation.
**Notes:** Follow-up asked in plain text, because the answer conflicted head-on with ROADMAP SC#3
and with Phase 49's own recorded "document rather than fix" decision. Three readings were offered:
(1) omit from the documentation entirely and amend SC#3; (2) no section, one inline sentence;
(3) omit from the user guide but keep a CHANGELOG line. **The user chose (1).** Also confirmed in
the same message that the standalone-content behaviour is still documented, per SC#1 — the user
raised no objection.

### Q2 — How is the standalone content-file compile presented?

| Option | Description | Selected |
|--------|-------------|----------|
| Inside "which file to compile", as prose | Reads as specification rather than as a caveat | ✓ |
| `.. note::` admonition | More visible, but a warning tone inconsistent with Q1's outcome | |
| Also document its use case | Add "useful for checking one document locally" — would need verification | |

**User's choice:** Inside "which file to compile", as prose.
**Notes:** Measured (Phase 49 real build) — compiling `shared.typ` with no wrapper succeeds and
yields only that document's own body, children absent, no error and no warning.

### Q3 — Is shared-child-across-masters behaviour documented?

| Option | Description | Selected |
|--------|-------------|----------|
| Document as two-layer specification | Once per master, at that master's own traversal position, heading level varying per master | ✓ |
| One line only | Just "a shared document appears in each master" | |
| Out of DOC-14 scope | Leave composition semantics to Phase 52's CHANGELOG | |

**User's choice:** Document as two-layer specification.
**Notes:** Measured (`state_guard_three_master_gate`) — `COMMON-B-MARKER` count = 1 in all three
masters' PDFs; `common_b` heading level `[3]` in m1, `[2]` in m2 and m3.

---

## SC#3 verification mechanism

### Q1 — Permanent gate or throwaway harness?

| Option | Description | Selected |
|--------|-------------|----------|
| One permanent gate under `tests/` | Follows `tests/test_quickstart_docs_gate.py`; catches the next drift | ✓ |
| Throwaway harness + recorded evidence | Phase 45.1's D-J pattern (twelve examples built in scratch, transcript recorded, nothing under `tests/`) | |
| Both | Full scratch sweep plus a permanent gate over the core claims | |

**User's choice:** One permanent gate.
**Notes:** Both precedents are real in this repo and were presented as measured, not remembered.

### Q2 — How do the page and the fixture share a source?

| Option | Description | Selected |
|--------|-------------|----------|
| Same shape as the existing gate | Fixtures under `tests/fixtures/`; the test reads the published `.rst`/`.md` and asserts against a real build, deriving expected values from the builder's own helpers | ✓ |
| `literalinclude` the fixture `conf.py` | Removes duplication, but the docs build starts depending on `tests/` | |
| Parse config out of the page's code blocks | No duplication at all, but a fragile parser with no precedent here | |

**User's choice:** Same shape as the existing gate.

### Q3 — How far does the gate build?

| Option | Description | Selected |
|--------|-------------|----------|
| `-b typst` only, never skips | Asserts the emitted `.typ` file set, no `typst-py` dependency | ✓ |
| Both — file set always, PDF when available | Deeper verification where `typst-py` exists | |
| `typstpdf` required | Strongest, but skips or fails in environments without `typst-py`, including this project's NixOS sandbox | |

**User's choice:** `-b typst` only, never skips.

---

## Closing question — ROADMAP SC#3

| Option | Description | Selected |
|--------|-------------|----------|
| Amend `ROADMAP.md` now | Remove the `:numref:` clause from SC#3 and record the owner decision inline | ✓ |
| Record in CONTEXT.md only | Leave the ROADMAP text standing but false | |
| Keep it in the Phase 52 CHANGELOG | Change the policy so a CHANGELOG line survives, and amend SC#3 to match | |

**User's choice:** Amend `ROADMAP.md` now. Done in this session — SC#3 (`.planning/ROADMAP.md`
§"Phase 51") now excludes `:numref:` explicitly and names the owner decision and its tracking todo.

---

## Claude's Discretion

- The new page's filename, title, and section order.
- The specific worked-example configurations, provided they cover a bare target, an explicit path
  target, and the refusal cases, and provided each is actually built (SC#3).
- Whether the sweep also edits `examples/**/conf.py`, as long as no documented claim stays false.
- All wording, including the user-facing name for the docname-named file ("wrapper" is already
  user-visible in `builder.py:767-770` and stays).

## Deferred Ideas

- `:numref:` numbering divergence — not documented in v0.8.0; tracked as a bug for a later
  milestone.
- Whether the v0.8.0 CHANGELOG mentions the `:numref:` behaviour — Phase 52's own call; its SC#2
  still asks for measured limitations.
- A short two-layer explanation in `README.md` — declined.
- Cross-reference degradation on standalone compile — the owner already declined a handoff for this
  in Phase 48 Q4; not reopened.
