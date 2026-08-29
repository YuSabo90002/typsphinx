# Phase 59: Path-Shape Predicate and Image-URI Correctness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-28
**Phase:** 59-path-shape-predicate-and-image-uri-correctness
**Areas discussed:** IMG-07 gate material, IMG-06 bound + gate observation point, key
separator-free scope, PATH-01 identity proof — all four delegated to Claude's recommendation

---

## Gray areas presented

The four areas below were offered as one multi-select question. Before presenting them, four real
`typst.compile()` runs and several filesystem probes were executed so every option description was
measured rather than recalled.

| Option | Description | Selected |
|--------|-------------|----------|
| A: IMG-07 gate material | A backslash-only URI is closed by IMG-04 alone, so SC#2's "neither alone would have closed it" would be unprovable; a basename carrying both a backslash and a `"` makes both halves load-bearing but is POSIX-creatable only | ✓ (delegated) |
| B: IMG-06 bound + gate | What the 255 bytes are measured against, and how the gate observes a failure `copy_image_files()` swallows into a warning | ✓ (delegated) |
| C: separator-free scope | Backslash only (requirement's literal text) vs. also stripping the drive-colon | ✓ (delegated) |
| D: PATH-01 identity proof | Permanent characterization test vs. one-off recorded measurement | ✓ (delegated) |

**User's choice:** 「おすすめで進める」 — all four delegated to Claude's recommendation, the same
disposition the owner took for Phase 58's four areas.

**Notes:** Because every area was delegated, each recommendation was locked as a D-NN decision in
CONTEXT.md rather than left open. The measurements behind them are recorded inline there so the
planner can check them instead of re-deriving.

---

## Measurements taken during this session

Against the live tree at `7d809b83`, using the project's own `.venv` typst-py:

| Probe | Result |
|---|---|
| `image("dir\logo.png")` | `TypstError: path must not contain a backslash` |
| `image("dir\\logo.png")` (escaped) | same error — refusal is by value, not by syntax |
| `image("we"ird.png")` | `TypstError: unclosed delimiter` |
| `image("we\"ird.png")` | compiles |
| backslash removed from the path | compiles |
| create POSIX file named `dir\we"ird.png` | succeeds on ext4 |
| `posixpath.basename("C:\imgs\logo.png")` raw / normalized | whole URI / `logo.png` |
| `posixpath.basename("C:logo.png")` normalized | `C:logo.png` — colon survives |
| 250-byte filename, then `{sha1[:8]}-` prefixed (259 bytes) | creatable / `OSError 36 ENAMETOOLONG` |
| `copy_image_files()` exception handling | `except Exception` → `logger.warning`, `OSError` never propagates |

---

## Claude's Discretion

All four areas. Beyond them, CONTEXT.md leaves the planner: plan decomposition inside ROADMAP
constraint 3, whether the key construction is extracted into a module-level helper, fixture/test
module naming, and the exact boundary-safe truncation idiom.

---

## Deferred Ideas

- The drive-relative colon in a relocation key (`C:logo.png` → an illegal NTFS destination) — sized
  as its own requirement, deliberately not folded into IMG-04's literal scope.
- The non-escape key branches (`builder.py:1783`) can still carry a literal backslash on POSIX;
  outside IMG-04's requirement text.
- `57-REVIEW.md` IN-01 (a path containing a literal single quote) — Phase 60, MSG-02's gate.
