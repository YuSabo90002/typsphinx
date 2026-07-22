# Phase 22: typstpdf Target-Name PDF Fix (Issue #117) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-21
**Phase:** 22-typstpdf Target-Name PDF Fix (Issue #117)
**Areas discussed:** Fix scope (.typ as well as .pdf), Target-name normalization, Backward compatibility, Regression-test shape, Output location for nested docnames

---

## Pre-discussion finding (drove the whole conversation)

Before presenting gray areas, a codebase measurement contradicted ROADMAP SC#2:

- `doc_tuple[1]` (target name) is **never read anywhere** in `typsphinx/`.
- `.typ` is written as `docname + suffix` (`builder.py:329`, `:646`), so `index.typ` — not
  `manual.typ`. SC#2's "already-correct `.typ` filename mapping" premise is false.
- `docs/configuration.rst:43` documents the target name as the output `.typ` filename, so the
  `.typ` side violates the published contract as much as the PDF side does.

A follow-up census of all 62 `typst_documents` entries under `tests/` + `docs/` showed only **2**
have `target != docname` (`tests/roots/test-basic` → `output.typ`; `docs/source` → `typsphinx`),
shrinking the apparent blast radius from "238 `index.typ` references" to two projects.

---

## Fix scope

| Option | Description | Selected |
|--------|-------------|----------|
| PDF only | Leave `index.typ`, emit `manual.pdf`. Smallest diff. | |
| Fix both `.typ` and `.pdf` | Honor the target name for both, matching the documented contract. Larger blast radius. | ✓ |

**User's choice:** 両方直す (fix both)
**Notes:** The user was initially presented a denser 4-area menu and asked for a plainer
explanation; the conversation was restarted from the bug description upward. The choice was made
once the two-project blast radius was measured rather than estimated.

---

## Target-name normalization

| Option | Description | Selected |
|--------|-------------|----------|
| Strip only a trailing `.typ` | `'output.typ'` → `output`; `'typsphinx'` → `typsphinx`. Preserves period-bearing stems. | ✓ |
| `os.path.splitext` | Simpler, but `'v1.2-manual'` → `'v1'`. | |
| Require an extension | Warn/error on extension-less names — but `docs/source/conf.py` itself uses one. | |

**User's choice:** 末尾の .typ だけ剥す
**Notes:** Extension-less target names are valid input, never a diagnostic.

---

## Backward compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Clean break | `index.pdf` stops being emitted. CHANGELOG documents the change. | ✓ |
| Emit both | Keep `index.pdf` alongside `manual.pdf` (copy or symlink). | |
| Clean break + build-time notice | Log an info line when the target differs from the docname. | |

**User's choice:** クリーンに切り替え
**Notes:** Treated as a bug fix restoring documented behavior. The user-visible filename change is
handed off to the Phase 23 CHANGELOG entry (CONTEXT D-08).

---

## Regression-test shape

| Option | Description | Selected |
|--------|-------------|----------|
| Drive `tests/roots/test-basic` with a real compile | It already declares `output.typ` — the exact Issue #117 condition. | ✓ |
| New dedicated `tests/fixtures/` render-gate project | Fully isolated, but duplicates an existing root. | |
| Unit tests + real compile | Table-driven stem cases plus the compile gate. | |

**User's choice:** test-basic を使って実コンパイル
**Notes:** The gate asserts both presence (`output.typ` / `output.pdf` + `%PDF` magic) and absence
(`index.typ` / `index.pdf`), so it fails pre-fix on both counts. Unit tests for the normalization
rule were not mandated but remain allowed (CONTEXT Claude's Discretion).

---

## Output location for nested docnames

| Option | Description | Selected |
|--------|-------------|----------|
| Rename basename in place | `sub/index` + `manual.typ` → `outdir/sub/manual.typ`. Relative include/image paths survive. | ✓ |
| Place at outdir root | LaTeX-builder-like, but invalidates every relative `include()`. | |
| Treat target as an outdir-relative path | Flexible, but pushes relative-path recomputation into this phase. | |

**User's choice:** docname と同じディレクトリ、名前だけ差し替え
**Notes:** Pinned by `_compute_relative_path()` (`translator.py:2932`) and the
`include("<rel>.typ")` emission at `translator.py:3428` — the master's physical location is
load-bearing.

---

## Path-bearing target name (guard)

Raised by the user after the initial CONTEXT.md was written: the original D-06 reduced a
path-bearing target to its basename *silently*, so a user writing `'sub/manual.typ'` would get
output somewhere they never asked for with no signal. Upgraded to an explicit guard.

| Option | Description | Selected |
|--------|-------------|----------|
| Warn + basename fallback | `logger.warning` naming the file actually written; build continues. Matches Sphinx's handling of config oddities; `-W` users get a hard failure for free. | ✓ |
| Raise `ExtensionError` | Impossible to miss, but breaks configs that build today (the path is already being ignored). | |
| Support paths properly | Interpret as outdir-relative and recompute every `include()`/image relative path. Far beyond Phase 22. | |

**User's choice:** 警告を出して basename にフォールバック
**Notes:** Detection must be portable — `/` plus `os.sep`/`os.altsep`, and `..` segments and
absolute/drive-qualified targets count as the same guarded case. `os.path.basename` alone is a
reducer, not a detector.

---

## Master-output layout (raised, deliberately not solved here)

The user pushed back on D-05: with multiple masters declared, the deliverables scatter across the
output tree (`_build/pdf/manual.pdf` + `_build/pdf/api/api-reference.pdf`), because the output tree
mirrors the source tree and masters sit wherever their docname sits.

Investigating that surfaced two further findings, neither of them about filenames:

- `compile_typst_to_pdf()` writes the master content to a temp file at **outdir root**
  (`pdf.py:140-149`) and compiles it there, so `-b typstpdf` resolves relative paths from the root
  while the translator emits them relative to the docname directory. Nested-docname masters are
  therefore already broken under `-b typstpdf`; only root-level masters work by coincidence. This
  corrected an inaccurate rationale in the originally-written D-05.
- `typst_output_dir` is registered (`__init__.py:60`) and documented (`docs/configuration.rst:255`)
  but read nowhere — the natural mechanism for collecting outputs is dead config.

**User's choice:** アイデア無いしまあそれしか無いかあ — accept D-05 as-is for Phase 22.
**Notes:** Collecting the deliverables means rebasing the relative-path computation onto the output
location, which is a `translator.py` change and a different bug from Issue #117. All three findings
captured at `.planning/todos/pending/2026-07-21-master-output-layout-and-dead-typst-output-dir.md`;
D-05 amended to record the accepted limitation explicitly rather than the wrong rationale.

---

## Claude's Discretion

- Exact factoring of the name-derivation helper across the three write/read sites in `builder.py`
  (invariant: all three must agree so `finish()` never looks for a `.typ` the write path did not
  produce).
- Whether to add table-driven unit tests for the normalization stem cases (allowed, not required).
- Whether to add a defensive warning for duplicate/colliding target names (no corpus case exists;
  no validation machinery).
- Whether `get_target_uri()` follows the rename or stays docname-based — decide deliberately after
  checking whether cross-document link resolution depends on it.

## Deferred Ideas

- `get_target_uri()` / Typst cross-document URI redesign.
- Duplicate / colliding target-name validation.
- Interpreting the target name as an outdir-relative path (rejected, D-06).
- Backlog 999.3 (`typst_package` path broken end-to-end) — reviewed as a todo match (score 0.6),
  not folded; different root cause and different files.
- Read the Docs hosting migration — reviewed as a todo match (score 0.2), not folded; unrelated.
