# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-11
**Phase:** 47-two-layer-output-content-wrapper-split-target-as-path-collision-detection
**Areas discussed:** Self-collision policy (BLD-03), Duplicate-target handling (BLD-02), Case-differing collisions (BLD-04), Content-file preamble and build log

---

## Self-collision policy (BLD-03, open question #4)

Evidence presented before the question: `typsphinx/builder.py:275`'s CR-01 guard reads
`if effective != docname and (...)`, so a target equal to its own docname is deliberately allowed
today — correct while a master's file *is* the docname's file, and a real wrapper-vs-content
collision once every docname unconditionally gets a content file.

| Option | Description | Selected |
|--------|-------------|----------|
| Fail with a configuration error | Invents no filename, identical in both builders, one-line fix for the user; breaks `("index", "index.typ", ...)`, which works in v0.7.x | ✓ |
| Fall back to the derived default with a warning | Extends CR-01's warn-and-fall-back convention; the fallback is `make_filename_from_project(project) + ".typ"`, already documented under CONF-08, so not an invented name; build always succeeds but the warning is easy to miss | |
| Skip the wrapper with a warning only | `-b typst` exits 0 with incomplete output while `-b typstpdf` raises through `finish()`'s "Master document not found" — behaviour diverges between builders | |

**User's choice:** Fail with a configuration error.
**Notes:** The preview the user selected specified exit 2 with no file written, in both builders.

---

### Follow-up: detection point and reporting granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Validate before write, enumerate every collision | One `ExtensionError` listing all offending entries; placed on `TypstBuilder` so `TypstPDFBuilder` inherits it; carries forward `finish()`'s "attempt everything, then report together" spirit | ✓ |
| Validate before write, stop at the first collision | Simplest message and implementation, but a three-collision config costs three fix-and-rebuild rounds | |
| Write what can be written, fail at the end | Reuses `finish()`'s `failures` list directly, but leaves the output directory half-updated on an error — contradicts the "no file written" property just chosen | |

**User's choice:** Validate before write, enumerate every collision.

---

### Follow-up: fate of the existing CR-01 guard

Evidence presented: after the split, a target colliding with **another** docname is the same hazard
as a self-collision, and CR-01's existing remedy — fall back to the docname — lands the wrapper on
that docname's own content file, i.e. produces a self-collision. The old fallback is unusable, not
merely lenient.

| Option | Description | Selected |
|--------|-------------|----------|
| One validator, every collision kind an error | Self-collision, other-document content collision, the reserved `_template.typ`, and duplicate targets all treated as "two logical files want one physical path"; existing tests move from warning to error expectations under binding constraint #6 | ✓ |
| Only self-collision errors, keep the rest as-is | Two-stage behaviour whose warning blames a docname the user never wrote, before erroring anyway | |
| Separate the `_template` reserved-name message | One validator, but a distinct message explaining why that basename is reserved | |

**User's choice:** One validator, every collision kind an error.

---

## Duplicate-target handling (BLD-02)

Largely settled by the unified-validator decision above. The remaining question was whether a
repeated docname is itself an error.

| Option | Description | Selected |
|--------|-------------|----------|
| Allow — different paths are not a collision | The validator only asks whether two logical files want one physical path; two wrappers over one content file is coherent and becomes a feature under CONF-13 | ✓ |
| Error on a repeated docname | Promotes `writer.py:33-35`'s silent first-match convention to an explicit refusal; would have to be reopened for CONF-13 | |

**User's choice:** Allow.
**Notes:** This question was first asked while per-entry template configuration was still a
candidate for this milestone; it was re-asked and answered after the milestone split.

---

## Case-differing collisions (BLD-04, open question #5)

| Option | Description | Selected |
|--------|-------------|----------|
| Always `casefold()` the comparison, error on every OS | Rejects a configuration that genuinely works on ext4, but fails on the developer's machine rather than only in the Windows and macOS CI lanes; closest reading of BLD-04's wording | ✓ |
| Branch on the running filesystem's case sensitivity | Refuses only what actually breaks on that platform, at the cost of the same `conf.py` behaving differently per OS — the shape milestone invariant #5 exists to prevent | |
| Exact-match comparison plus an advisory warning | Breaks no existing configuration, but a missed warning on a case-insensitive filesystem is exactly the silent overwrite this phase is closing | |

**User's choice:** Always `casefold()` the comparison.
**Notes:** The selected preview explicitly excluded Unicode normalization (NFC/NFD) — case folding
only, applied to comparison and not to the written filename.

---

## Content-file preamble and build log

| Option | Description | Selected |
|--------|-------------|----------|
| Give every content file today's included-document preamble | `writer.py:208-218` verbatim: four `@preview` imports plus `codly-init`; exact status quo for included documents, and only masters gain a preamble; double `codly-init` application to be measured by the GATE-01 fixture | ✓ |
| Imports only, `codly-init` in the wrapper alone | Structurally avoids the double show rule, but a content file compiled standalone loses code-block decoration | |

**User's choice:** Give every content file today's included-document preamble.

| Option | Description | Selected |
|--------|-------------|----------|
| `-b typst` reports each wrapper it wrote | The symmetric message `-b typstpdf` already has; after the split nothing in a filename distinguishes wrapper from content | ✓ |
| Leave the build log unchanged | Keeps the phase's change surface minimal; the shape change is explained by DOC-14 and the CHANGELOG instead | |

**User's choice:** `-b typst` reports each wrapper it wrote.

---

## Claude's Discretion

- Which files `-b typstpdf` compiles to PDF (wrappers only is the natural continuation of
  `builder.py:967`'s existing rule).
- Where the unified validator lives, provided it runs before the write phase, is a single code
  path for every collision kind, and is owned by `TypstBuilder` so both builders inherit it.
- The wording of every new warning and error message.

## Deferred Ideas

- **Per-entry template configuration via a named template key in the fifth tuple element.** Raised
  mid-discussion by the user as a scope gap: `typst_template` / `typst_package` /
  `typst_package_imports` / `typst_template_function` are all global, so a multi-master build forces
  one template and one parameter set on every master, and a declared `params` discards each entry's
  own title and author with no warning. The user proposed unifying the template source and its
  function settings into a single named definition keyed from the fifth tuple element. Verified
  against installed Sphinx 9.1.0 (`docname, targetname, title, author, themename = entry[:5]`
  followed by `theme = self.themes.get(themename)`), which is the exact same mechanism. The user
  first considered restructuring the milestone to include it, then chose to split it into its own
  milestone. Recorded as the rewritten CONF-13 in `.planning/REQUIREMENTS.md`, commit `a54b794`.
- **A fail-loud warning for the global-`params` silent discard in v0.8.0.** Offered as a small
  scope addition once the split was decided. The user chose complete status quo for v0.8.0 — the
  limitation ships documented and is resolved by CONF-13.
