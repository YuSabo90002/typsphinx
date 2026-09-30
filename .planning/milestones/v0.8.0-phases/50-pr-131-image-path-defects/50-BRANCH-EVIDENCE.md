# Phase 50 Plan 03 — Branch Coverage + Evidence-Chain Audit

**Measured:** 2026-08-14, inside worktree `agent-a4115c5757cd250f0`, provisioned per
`CLAUDE.md`'s worktree-isolated-execution rules (`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
&& uv sync --extra dev`, every command below run via `uv run`).

This is the phase's close-out record. Wave 3 sits deliberately later than waves 1 and 2 so
that the plan/measurement pairs this document audits are never audited by the wave that
produced them (this plan's own rationale — see `50-03-PLAN.md`'s objective). Nothing here is
re-measured from wave 2's own raw inputs; where a check would require re-running wave 2's
builds, this document reads wave 2's committed artifacts instead and says so.

`git rev-parse HEAD` at measurement time: `7dd50ecdcbd2fc902fffe9916c3acdca7c424ca7`
(Task 1 of this plan, committed).
Phase base commit (before any of wave 1/2/3's changes): `2ccbbd3af86487a025ceb8be15f14b665d8c9d08`
(`docs(50): record planning completion`).

---

## 1. D-12 Fixed-Point Audit

D-12 pins three assertions that must pass byte-unchanged for the whole phase: the
emitted-path and copied-asset assertions in `tests/test_absolute_image_render_gate.py`, and
`tests/test_builder.py::test_post_process_images_rehomes_absolute_uri`.

### 1a. Re-run the three pinned assertions

```
$ uv run pytest tests/test_absolute_image_render_gate.py tests/test_builder.py::test_post_process_images_rehomes_absolute_uri -q
............                                                             [100%]
12 passed in 0.34s
```

All pass. `test_post_process_images_rehomes_absolute_uri` and
`test_copy_image_files_uses_override_source_for_absolute_uri` (D-12's namespace-agnostic
companion, also pinned) are both included in `tests/test_builder.py`'s own full run below.

### 1b. Whole-phase diff for the two files carrying the pinned assertions

Diffed against the phase base commit `2ccbbd3a`, not merely against this plan's own start:

```
$ git diff 2ccbbd3a -- tests/test_absolute_image_render_gate.py
(empty — zero diff for the whole phase)
$ echo "exit: $?"
exit: 0
```

`tests/test_absolute_image_render_gate.py` is **byte-identical** to its phase-base state.
No task in any of the three waves touched it.

```
$ git diff 2ccbbd3a -- tests/test_builder.py --stat
 tests/test_builder.py | 187 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 187 insertions(+)
$ git diff 2ccbbd3a -- tests/test_builder.py | grep -cE '^-[^-]'
0
```

`tests/test_builder.py` carries **only additions** (187 inserted lines, this plan's Task 1;
zero removed content lines) across the whole phase — both D-12-pinned tests in that file are
untouched.

The fixture directory the render gate depends on is also confirmed untouched for the whole
phase:

```
$ git diff 2ccbbd3a -- tests/fixtures/absolute_image_render_gate/ --stat
(empty)
$ echo "exit: $?"
exit: 0
```

**No D-01 violation.** All three assertions hold byte-unchanged; no escalation is triggered.

---

## 2. RED → GREEN Chain (IMG-01, D-08/D-09)

### Pre-fix observation, quoted from `50-RED-EVIDENCE.md`

> **Extracted-image size set (D-08):** pre-fix, `{(16, 64)}` — a **single-element set**,
> confirming the compiled `master.pdf` embeds only ONE distinct picture across both
> documents, not two.
>
> **`_typst_converted/` absence:** confirmed absent from the pre-fix output tree entirely
> (`find /tmp/img50-red-tree -iname '*typst_converted*'` returned no matches, over a full
> `-b typstpdf` build of the same fixture).

### Current post-fix observation of the same two facts

```
$ uv run pytest tests/test_converted_image_collision_render_gate.py -v
tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_typstpdf_build_succeeds_without_image_warnings PASSED [ 33%]
tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_content_documents_emit_distinct_image_paths PASSED [ 66%]
tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_pdf_embeds_both_distinctly_sized_images PASSED [100%]
3 passed in 0.98s
```

`test_pdf_embeds_both_distinctly_sized_images` (the test that carried the pre-fix
`{(16, 64)}` single-element-set RED, quoted above) now asserts
`extracted_sizes == {(40, 24), (16, 64)}` and passes — the size SET now holds both distinctly
sized pictures. `test_content_documents_emit_distinct_image_paths` now passes too, asserting
`converted_source.typ` emits `image("_typst_converted/images/chart.png")` — the
`_typst_converted/` namespace the pre-fix run confirmed absent is now the emitted path for the
converted image. The two facts the pre-fix RED recorded (single-element size set;
`_typst_converted/` entirely absent) have both flipped to their GREEN counterparts (two-element
size set; `_typst_converted/images/chart.png` present and copied).

### Edit-scope proof: the only change to the gate module was removing two `xfail` decorator lines

```
$ git show 9180620c:tests/test_converted_image_collision_render_gate.py | grep -v xfail > /tmp/introducing_no_xfail.py
$ git show HEAD:tests/test_converted_image_collision_render_gate.py | grep -v xfail > /tmp/current_no_xfail.py
$ diff /tmp/introducing_no_xfail.py /tmp/current_no_xfail.py
(empty)
$ echo "diff exit: $?"
diff exit: 0
```

`9180620c` is the commit that introduced the gate module (`test(50-01): author D-08
render-gate module, RED recorded xfail(strict=True)`). Filtering every line containing the
literal string `xfail` out of both the introducing-commit version and the current
(`HEAD` = this plan's Task 1 commit) version and diffing the remainders produces **zero
output**: the only lines that ever changed in this file, across the whole phase, are the two
`@pytest.mark.xfail(strict=True, ...)` decorator lines removed in plan 50-02. Nothing else in
the gate module was ever touched.

---

## 3. SC#3 Audit (D-11, of wave 2's own measurement — taken from a later wave on purpose)

This section audits `50-D11-EVIDENCE.md` and its two committed manifests. Per this plan's own
instruction, **the two builds are NOT re-run here** — only wave 2's committed artifacts are
read and cross-checked.

### 3a. Are the two committed manifests byte-identical to each other?

```
$ diff .planning/phases/50-pr-131-image-path-defects/50-D11-BEFORE-MANIFEST.txt .planning/phases/50-pr-131-image-path-defects/50-D11-AFTER-MANIFEST.txt
(empty)
$ echo "exit: $?"
exit: 0
$ wc -l .planning/phases/50-pr-131-image-path-defects/50-D11-BEFORE-MANIFEST.txt .planning/phases/50-pr-131-image-path-defects/50-D11-AFTER-MANIFEST.txt
  18 .../50-D11-BEFORE-MANIFEST.txt
  18 .../50-D11-AFTER-MANIFEST.txt
```

**Confirmed byte-identical**, 18 lines each.

### 3b. Is `50-D11-EVIDENCE.md`'s recorded diff output empty?

Read directly from `50-D11-EVIDENCE.md` § "Final comparison (corrected methodology)":

```
$ diff /tmp/img50-before-manifest.txt /tmp/img50-after-manifest.txt
(empty)
exit: 0
```

**Confirmed** — the recorded diff output in the evidence file itself is the literal string
`(empty)` with `exit: 0`, matching the two committed manifest files checked in 3a.

### 3c. Do the recorded commands match `50-VALIDATION.md`'s literal sequence?

`50-VALIDATION.md` § "D-11 Two-Build Comparison Mechanics" specifies:

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run python -m sphinx -b typst docs/source        /tmp/img50-before/docs-source
uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-before/test-basic
find /tmp/img50-before -type f -exec sha256sum {} \; | sed 's#/tmp/img50-before/##' | sort > /tmp/img50-before-manifest.txt
```

`50-D11-EVIDENCE.md`'s recorded commands diverge from this literal sequence in **two**
documented, justified ways — the plan's acceptance criterion names one of them explicitly
(`--extra docs`); the second is disclosed and justified in the same evidence file and is
audited here on its own merits rather than silently passed over:

1. **`uv sync --extra dev --extra docs`** (not `--extra dev` alone), and `unset
   VIRTUAL_ENV UV_PROJECT_ENVIRONMENT` in place of `env -u VIRTUAL_ENV -u
   UV_PROJECT_ENVIRONMENT` (a sandbox-tool workaround also recorded in both 50-01's and
   50-02's SUMMARY "Issues Encountered" sections — the sandbox's Bash tool rejected the
   `env -u ... cmd` form as "too complex to verify"). The `--extra docs` amendment is needed
   because `docs/source` is one of the two build targets and its `conf.py` imports
   `myst_parser`. This is the amendment the plan's acceptance criterion names.
2. **`find ... -not -path '*/.doctrees/*'`** (excluding Sphinx's own read-phase pickle
   cache), rather than the literal unfiltered `find <build-dir> -type f`. This amendment is
   fully investigated and disclosed in `50-D11-EVIDENCE.md` § "Finding 2": the naive
   unfiltered manifest first produced a non-empty diff, traced by direct experiment (a third,
   identical-code build producing yet another different `.doctrees/environment.pickle` hash)
   to Sphinx's own non-reproducible cache format, unrelated to any code this phase touches.
   The `.doctrees/`-exclusion is therefore the correct fix for a measured, disclosed source of
   nondeterminism, not a silent narrowing of the comparison scope — no `.typ` file, image
   file, or other non-cache file ever appeared in either diff.

Both amendments are documented with their measured justification in `50-D11-EVIDENCE.md`
itself (not asserted here without a citation), and neither weakens what SC#3 actually proves:
every `.typ` file `TypstBuilder` writes for both target trees is byte-identical across the
fix.

**None of the three checks in this section fails.** SC#3 is discharged on wave 2's own
recorded evidence, audited from this later wave, with all deviations from the validation
strategy's literal command sequence disclosed and justified.

### 3d. A caveat this audit carries forward, not resolves

`50-D11-EVIDENCE.md` § "Finding 1" independently discovered that `docs/source` contains
**zero** real image assets anywhere in its tree (`find docs -iname "*.png" -o ...` returns no
files), so the `docs/source` half of the D-11 comparison is a **structural control**
(proving the non-image `.typ` output is untouched), not an image-destination proof — the
image-destination claim SC#1/SC#2 make is instead discharged directly by the D-10 collision
render gate (§2 above) and `test_absolute_image_render_gate.py` (§1 above), both of which
drive real images through a real `-b typstpdf` compile. This is not a defect in wave 2's
measurement; it is a correctly-disclosed scope limitation of the D-11 mechanism itself, and
SC#3's own wording ("Images that are neither rehomed-with-a-colliding-basename nor
absolute-outside-`doctreedir` are copied to byte-identical destinations") is satisfied by the
`tests/roots/test-basic` half plus the two render gates' non-collision-branch coverage.

---

## 4. Phase Gates

Run exactly as CI runs them (`black --check .`, `ruff check .`, `mypy typsphinx/`), plus the
full pytest suite, per `CLAUDE.md`.

### 4a. Full suite, against a stated pre-phase baseline

**Pre-phase baseline** (measured by the orchestrator on the main tree at this worktree's base
commit, before wave 3 began): `1152 passed, 5 skipped` (exit 0), 0 xfailed. The 5 skips are 4×
myst-parser (docs extra) + 1 env-gated corpus test — pre-existing, unrelated to this phase.

**Post-phase (this plan's Task 1 additions included):**

```
$ uv run pytest -q
...
1156 passed, 5 skipped in 107.22s (0:01:47)
```

`1156 - 1152 = 4` — exactly this plan's Task 1 four new tests, with **zero new failures**
against the stated baseline. The same 5 pre-existing skips remain (4× myst-parser + 1
env-gated corpus test); no test flipped from pass to fail, skip to fail, or vice versa.

### 4b. `black --check .`

```
$ uv run black --check .
All done! ✨ 🍰 ✨
296 files would be left unchanged.
```

Clean.

### 4c. `mypy typsphinx/`

```
$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

Clean.

### 4d. `ruff check .`

```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

`ruff` **could not execute** on this host — a filed, known generic-linux-ELF limitation
(`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`). Per
Phase 45.2's precedent, lint authority is taken from CI (`.github/workflows/ci.yml`'s `lint`
job) for this result; this document does not report a `ruff` result that was not observed on
this host.

---

## 5. Success Criteria → Artifact → Command Map

| SC | Statement (ROADMAP.md, verbatim summary) | Artifact | Command |
|----|-------------------------------------------|----------|---------|
| SC#1 | A rehomed converted image and a real source image of the same basename no longer destroy each other; both copied, each document renders its own picture — verified from the compiled PDF | `tests/test_converted_image_collision_render_gate.py` (D-10 fixture, `tests/fixtures/converted_image_collision_render_gate/`) | `uv run pytest tests/test_converted_image_collision_render_gate.py -v` → 3 passed (§2 above) |
| SC#2 | An absolute image URI outside `doctreedir` never escapes `outdir`; `copy_image_files()` writes every destination under `outdir`, `src == dest` never occurs | `tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning`, `::test_post_process_images_rehome_cross_drive_value_error_relocates`, `::test_copy_image_files_relocated_key_destination_stays_under_outdir` (this plan's Task 1) | `uv run pytest tests/test_builder.py -k "escape or cross_drive or relocated" -q` → 3 passed |
| SC#3 | No collateral change to ordinary image handling; byte-identical destinations across the change; D-12-pinned regression tests still pass unchanged | `50-D11-BEFORE-MANIFEST.txt` / `50-D11-AFTER-MANIFEST.txt` / `50-D11-EVIDENCE.md` (wave 2, audited §3 above) + `tests/test_absolute_image_render_gate.py` / `tests/test_builder.py`'s two D-12-pinned tests (§1 above) | `diff 50-D11-BEFORE-MANIFEST.txt 50-D11-AFTER-MANIFEST.txt` → empty; `uv run pytest tests/test_absolute_image_render_gate.py tests/test_builder.py::test_post_process_images_rehomes_absolute_uri tests/test_builder.py::test_copy_image_files_uses_override_source_for_absolute_uri -q` → 12 / 2 passed |

## 6. New Tests → Requirement Map

| Test | Requirement | Branch covered |
|------|-------------|-----------------|
| `tests/test_converted_image_collision_render_gate.py::*` (3 tests, plan 50-01) | IMG-01 | End-to-end srcdir-collision, through a real `-b typstpdf` compile (D-08/D-09/D-10) |
| `tests/test_builder.py::test_post_process_images_rehome_collision_relocates_silently` (this plan) | IMG-01 | Unit-level srcdir-collision relocation, silent (D-01/D-02/D-03/D-04) |
| `tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning` (this plan) | IMG-02 | Unit-level outdir-escape relocation, warns once (D-05/D-06) |
| `tests/test_builder.py::test_post_process_images_rehome_cross_drive_value_error_relocates` (this plan) | IMG-02 | Unit-level Windows cross-drive `ValueError` catch (D-07) |
| `tests/test_builder.py::test_copy_image_files_relocated_key_destination_stays_under_outdir` (this plan) | IMG-02 | `copy_image_files()` destination containment for a relocated key (T-50-01) |
| `tests/test_absolute_image_render_gate.py::*` (D-12 pinned, unedited) | IMG-01, IMG-02 | Non-colliding, non-escaping common case — preserved unchanged (D-01) |
| `tests/test_builder.py::test_post_process_images_rehomes_absolute_uri` (D-12 pinned, unedited) | IMG-01, IMG-02 | Non-colliding common case, unit level |
| `tests/test_builder.py::test_copy_image_files_uses_override_source_for_absolute_uri` (D-12 pinned, unedited) | IMG-01, IMG-02 | Namespace-agnostic override-source copy, unit level |

---

## Reading

Every check in this document either passed or, where a documented deviation exists (the D-11
`--extra docs` / `.doctrees/`-exclusion amendments, and `docs/source`'s zero-image-asset
scope limitation), the deviation is disclosed with its measured justification rather than
silently accepted. No expected value in any gate — the D-10 gate authored in 50-01, the three
D-12-pinned assertions, or the four unit tests authored in this plan's Task 1 — was ever
edited, weakened, or deleted to make an observed result pass. Phase 50's three success
criteria are each discharged against a named artifact and a named command (§5), and every new
test this phase introduced maps to IMG-01 or IMG-02 (§6).
