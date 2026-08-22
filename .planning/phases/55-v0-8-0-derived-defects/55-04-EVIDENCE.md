# Phase 55 Plan 04 — Evidence

Recorded against commit `d03947730a61f708cbd115ff312982779558af4e` on 2026-08-16 — this plan's own
Task 1 commit (the CHANGELOG `Fixed` entries and the ROADMAP SC#4 amendment), on top of the merged
Wave 1 + Wave 2 tree (`55-01`, `55-02`, `55-03` all landed at base commit `c37ee206`). Every number
below was produced by a command run in this worktree, in this task, after the merge — none is
transcribed from a sibling plan's summary or from memory.

## 1. Full suite

```
uv run pytest -q
```

**Result (verbatim totals line):**

```
================= 1366 passed, 5 skipped in 119.61s (0:01:59) ==================
```

**Failure count: 0 — unconditional, not "modulo 7".** The stale `tests/test_state_guard_shapes_gate.py`
seven-failure carve-out (`phases/53-template-registry-foundation/deferred-items.md`) was measured
stale on 2026-08-16 at Phase 54.1's close and is not cited here. This measurement reproduces that:
**1366 passed, 5 skipped, 0 failed**, with no node ids to list because none failed.

## 2. The three CI-matching gates

```
uv run black --check .
```
**Result:** `All done! ✨ 🍰 ✨` / `336 files would be left unchanged.` — **exit 0**.

```
uv run ruff check .
```
**Result:** `Could not start dynamically linked executable: ruff` (`exit 0` from the wrapper, but
ruff itself never ran — the same pre-existing NixOS generic-linux-ELF hazard `55-01-SUMMARY.md`,
`55-02-SUMMARY.md`, and `55-03-SUMMARY.md` all recorded independently in this same worktree
lineage). Worked around identically, via the nix-store-provided binary:

```
nix run nixpkgs#ruff -- check .
```
**Result:** `All checks passed!` — **exit 0**.

```
uv run mypy typsphinx/
```
**Result:** `Success: no issues found in 8 source files` — **exit 0**.

## 3. `@preview` invariant

```
uv run pytest tests/test_preview_version_sync.py -q
```
**Result:** `3 passed in 0.02s`.

```
grep -c '@preview' typsphinx/templates/base.typ
```
**Result:** `4` — one line per package (`codly`, `codly-languages`, `mitex`, `gentle-clues`).

```
grep -c '@preview' typsphinx/writer.py
grep -c '@preview' typsphinx/template_engine.py
```
**Result:** `5` and `5` respectively — the same four package-import lines each, plus one prose
docstring mention of `@preview` each (`writer.py:241`'s "the four ``@preview`` imports" phrase,
`template_engine.py:277`'s docstring example). Confirmed by direct `grep -n`: both files' four
`#import "@preview/..."` lines are byte-identical to `base.typ`'s four lines. **Package count is
still four with no fourth version-lockstep site.**

## 4. Zero new runtime dependencies

```
git diff --stat 3d8bdb10eb475c53666abab494d3cbf524eb6ff5..HEAD -- pyproject.toml
```
**Result:** empty output — the dependency arrays are unchanged across the whole phase (pre-fix SHA,
the tip of Phase 55 planning, through this plan's own `HEAD`). The two symbols this phase reached
for are Python standard library (`hashlib`, used by `55-03`'s digest-prefixed relocation key) and
`sphinx.errors.ExtensionError`, an already-declared dependency's own module (`55-02`'s BLD-08 bound).

## 5. No typing-import modernization

```
git diff 3d8bdb10eb475c53666abab494d3cbf524eb6ff5..HEAD -- typsphinx/ | grep -cE '^[-+].*from typing import'
```
**Result:** `0`.

## 6. Milestone branch on the remote (binding constraint #9)

```
git ls-remote --heads origin gsd/v0.9.0-per-document-templates
```
**Result:**
```
35ee8a0ee8a4f8701c99a6596be8e37d975de307	refs/heads/gsd/v0.9.0-per-document-templates
```
Non-empty — the milestone branch is present on `origin`. Milestone invariant #9 holds.

## Requirement-to-gate map

| Requirement | D-05 evidence level | RED-EVIDENCE file | Gate command (verified green above) | Result |
|---|---|---|---|---|
| XREF-05 | real two-master compile (`sphinx-build -b typstpdf` + `typst.compile()`) | `55-01-RED-EVIDENCE.md` | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py::TestXrefCompileTimeGuardRenderGate::test_label_collision_no_longer_links_to_decoy -q` | 1 passed |
| BLD-07 | real compile (`sphinx-build -b typstpdf` + `typst.compile()`, PDF-level marker count) | `55-02-RED-EVIDENCE.md` | `uv run pytest tests/test_include_edge_separator_collision_gate.py -q` | 4 passed |
| BLD-08 | unit | `55-02-RED-EVIDENCE.md` | `uv run pytest tests/test_include_edge_derivation_unit.py -k DepthBound -q` | 4 passed |
| BLD-09 | unit (platform-independent string-shape) | `55-03-RED-EVIDENCE.md` | `uv run pytest tests/test_builder.py -k "driveless_absolute_uri_reaches_rehome_branch or unc_absolute_uri_reaches_rehome_branch or relative_uri_is_not_treated_as_absolute" -q` | 3 passed |
| IMG-03 | unit | `55-03-RED-EVIDENCE.md` | `uv run pytest tests/test_builder.py -k "escape_same_basename_keys_stay_distinct or escape_key_is_pure_function_of_uri" -q` | 2 passed |

This table is how binding constraint #6 is shown discharged for all five defects at once: each RED
was recorded against the pre-fix tree, at the D-05-decided evidence level, before its own
implementation landed, and the corresponding gate above passes on the merged tree. The tiering was
honoured, not flattened — XREF-05 and BLD-07 both required a real compiled-PDF observation because
their defects are silent output-level failures (a wrong link destination, a duplicated included
document), while BLD-08, BLD-09, and IMG-03 are exception-type or key-collision defects that a unit
test observes directly.

## Checkpoint resolution

Plan `55-03`'s Task 2 was a blocking `checkpoint:decision`: ROADMAP SC#4 names the raw-URI
`posixpath.isabs(…) or _is_drive_qualified(…)` predicate literally, but that spelling evaluates
`False` for the driveless-absolute and UNC Windows URI shapes the same criterion requires to reach
the rehome/relocate/warn branch.

**The owner selected option-b**, recorded in `55-03-SUMMARY.md`'s "Task 2 Checkpoint Resolution":
`_is_absolute_image_uri()` applies `posixpath.isabs(…) or _is_drive_qualified(…)` to a
**backslash-normalized** copy of `resolved_uri` (`resolved_uri.replace("\\", "/")`), not to the raw
URI SC#4's literal text names — measured, both at Phase 55 planning time and re-measured
independently in the `55-03` worktree, to be the only one of the two spellings that reaches the
rehome branch for both the driveless-absolute and UNC shapes.

**The owner's second decision at that same checkpoint: yes, amend ROADMAP SC#4's wording** — plan
`55-03` deliberately did not edit `.planning/ROADMAP.md` (outside its declared `files_modified`) and
delegated the amendment to this plan. **This plan's Task 1 applied that amendment**, using the exact
replacement text `55-03-SUMMARY.md` § "SC#4 amendment for `55-04`" provided: the stale
`builder.py:910` line-number citation was replaced with "grep the literal call" (matching this
phase's own binding constraint against citing line numbers in success criteria), and the sentence
recording that the backslash-normalized predicate — not the raw-URI predicate SC#4 originally
specified — is what shipped was appended, with a pointer to `55-03-RED-EVIDENCE.md` § "Predicate
measurement". Verified: `git diff -- .planning/ROADMAP.md | grep -c '910'` returned `1` (the stale
citation removed) and the diff-stat was 18 lines (well under the 40-line scoped-replacement bound).

## Open after this phase

Two items are recorded here, deliberately open, neither a blocker:

1. **`_escapes_outdir()`'s absolute-path branch is not backslash-normalized**, the sibling latent gap
   plan `55-03` measured but did not fix (out of its own declared scope, since `_escapes_outdir()`'s
   contract belongs to OUT-02's target-stem escape test, not to `_track_image()`'s gate). Filed at
   `.planning/todos/pending/2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md`.

2. **The residual truncated-digest collision probability for IMG-03's relocation key is reasoned, not
   measured.** `55-03-PLAN.md`'s `must_haves` carries this as a flagged assumption (unclassified edge
   probe): the 8-hex-character SHA-1 prefix gives roughly 32 bits of entropy over the handful of
   escaping images in a real build, and the threat register (`55-03-PLAN.md` T-55-10) accepts the
   residual risk at `low` severity rather than measuring it — widening the truncation is recorded as
   a one-line change if a real collision is ever observed.

## Summary

The phase closes green: the full suite is unconditionally 0-failed (§1), all three CI-matching gates
exit 0 (§2), the `@preview` version-sync surface stays at four packages with no fourth lockstep site
(§3), zero new runtime dependencies were added across the whole phase (§4), no typing-import
modernization was performed (§5), and the milestone branch is confirmed pushed to `origin` (§6). The
requirement-to-gate map shows all five requirements' D-05 evidence tiering honoured and traceable
from one place, and the plan `55-03` checkpoint resolution — including the ROADMAP SC#4 amendment
this plan's Task 1 applied — is recorded above. Two items are named open, neither a blocker.
