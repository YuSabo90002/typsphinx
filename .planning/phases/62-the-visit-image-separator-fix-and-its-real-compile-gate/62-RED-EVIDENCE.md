# Phase 62 - RED Evidence

## Phase base SHA

`PHASE_BASE_SHA`: 5a837238aadc126611b175228cbed5ac8b1058f8

Measured by `git rev-parse HEAD` in this worktree (`<WORKTREE_ROOT>`, redacted here by plan 03
task 1 for the same absolute-path hygiene reason as the RED transcript's `<BUILD_DIR>`
substitution below -- the literal worktree path carries no evidentiary weight, only the SHA does)
BEFORE any file in this phase was created or edited. This equals the `worktree_branch_check`
expected base recorded by the orchestrator at dispatch time, cross-checked at task start.

## RED run (unfixed tree, 18 masters)

**Restore command:** `git checkout 5a837238aadc126611b175228cbed5ac8b1058f8 -- typsphinx/translator.py`
(the base SHA recorded in `## Phase base SHA` above). Confirmed real before proceeding:
`git diff HEAD --numstat -- typsphinx/translator.py` reported `0	9	typsphinx/translator.py` --
9 deletions, 0 additions, the exact inverse of plan 01's pure insertion -- and a read of
`typsphinx/translator.py:4748-4756` confirmed the `# IMG-08 (AMENDED D-08): mirrors visit_Text's
in_signature_text triad.` comment and the three separator calls it introduces are both absent.

**Build command:** `uv run python -m sphinx -b typstpdf tests/fixtures/inline_image_separator_render_gate <BUILD_DIR>`,
stdout and stderr captured to separate files, non-zero exit allowed. Measured exit code: `2`.

**Two substitutions were made to the transcript below, stated here explicitly so a reader knows
nothing else was touched:** every occurrence of the machine-specific absolute build directory was
replaced with `<BUILD_DIR>`, and the one occurrence of this worktree's own absolute repository
path inside Python's own traceback frame (`File ".../typsphinx/builder.py", line 2640, in
finish`) was replaced with `<REPO_ROOT>` -- required by this task's own acceptance criterion that
no machine-specific home-directory-rooted or user-directory-rooted path survive anywhere in this
file, and unavoidable because Sphinx's traceback renderer embeds the interpreter's own absolute
source-file path, not merely the build directory.

**Full verbatim stderr**, with only those two substitutions applied:

```
Typst compilation failed at <BUILD_DIR>/index-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/index-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/index-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_01_sub_mid_sentence-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_01_sub_mid_sentence-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_01_sub_mid_sentence-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_02_two_subs_adjacent-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_02_two_subs_adjacent-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_02_two_subs_adjacent-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_03_sub_in_list_item-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_03_sub_in_list_item-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_03_sub_in_list_item-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_04_block_image_second_in_list_item-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_04_block_image_second_in_list_item-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_04_block_image_second_in_list_item-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_05_image_in_table_cell-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_05_image_in_table_cell-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_05_image_in_table_cell-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_06_image_in_definition_list_body-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_06_image_in_definition_list_body-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_06_image_in_definition_list_body-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_07_image_in_admonition-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_07_image_in_admonition-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_07_image_in_admonition-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_08_image_in_footnote_body-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_08_image_in_footnote_body-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_08_image_in_footnote_body-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_09_image_in_legend_mid_text-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_09_image_in_legend_mid_text-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_09_image_in_legend_mid_text-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_10_two_images_in_legend-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_10_two_images_in_legend-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_10_two_images_in_legend-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_11_image_after_inline_literal-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_11_image_after_inline_literal-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_11_image_after_inline_literal-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_12_image_after_emphasis-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_12_image_after_emphasis-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_12_image_after_emphasis-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_13_image_after_reference-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_13_image_after_reference-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_13_image_after_reference-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_14_image_in_field_list_body-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_14_image_in_field_list_body-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_14_image_in_field_list_body-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_15_image_in_section_title-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_15_image_in_section_title-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_15_image_in_section_title-out.typ
Details: expected semicolon or line break
Typst compilation failed at <BUILD_DIR>/fail_16_image_with_width_mid_sentence-out.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile <BUILD_DIR>/fail_16_image_with_width_mid_sentence-out.typ: Typst compilation failed: TypstError: expected semicolon or line break
Location: <BUILD_DIR>/fail_16_image_with_width_mid_sentence-out.typ
Details: expected semicolon or line break

Extension error!

Versions
========

* Platform:         linux; (Linux-6.18.47-x86_64-with-glibc2.42)
* Python version:   3.13.13 (CPython)
* Sphinx version:   9.1.0
* Docutils version: 0.22.4
* Jinja2 version:   3.1.6
* Pygments version: 2.20.0

Last Messages
=============

    writing output... [pass_h_figure_first_in_list_item]
     done
    writing output... [pass_i_bare_image_first_in_list_item]
     done
    writing output... [pass_parent]
     done
    typst: wrote 18 wrapper file(s) -- compile these: fail_01_sub_mid_sentence-out.typ, fail_02_two_subs_adjacent-out.typ, fail_03_sub_in_list_item-out.typ, fail_04_block_image_second_in_list_item-out.typ, fail_05_image_in_table_cell-out.typ, fail_06_image_in_definition_list_body-out.typ, fail_07_image_in_admonition-out.typ, fail_08_image_in_footnote_body-out.typ, fail_09_image_in_legend_mid_text-out.typ, fail_10_two_images_in_legend-out.typ, fail_11_image_after_inline_literal-out.typ, fail_12_image_after_emphasis-out.typ, fail_13_image_after_reference-out.typ, fail_14_image_in_field_list_body-out.typ, fail_15_image_in_section_title-out.typ, fail_16_image_with_width_mid_sentence-out.typ, index-out.typ, pass_parent-out.typ
    Copying 1 image file(s)...
    Compiling 18 master document(s) to PDF...
    Generated PDF: <BUILD_DIR>/pass_parent-out.pdf

Loaded Extensions
=================

* sphinx.ext.mathjax (9.1.0)
* alabaster (1.0.0)
* sphinxcontrib.applehelp (2.0.0)
* sphinxcontrib.devhelp (2.0.0)
* sphinxcontrib.htmlhelp (2.1.0)
* sphinxcontrib.serializinghtml (2.0.0)
* sphinxcontrib.qthelp (2.0.0)
* typsphinx (0.9.0)

Traceback
=========

      File "<REPO_ROOT>/typsphinx/builder.py", line 2640, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 17 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/index-out.typ
    Details: expected semicolon or line break; fail_01_sub_mid_sentence: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_01_sub_mid_sentence-out.typ
    Details: expected semicolon or line break; fail_02_two_subs_adjacent: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_02_two_subs_adjacent-out.typ
    Details: expected semicolon or line break; fail_03_sub_in_list_item: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_03_sub_in_list_item-out.typ
    Details: expected semicolon or line break; fail_04_block_image_second_in_list_item: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_04_block_image_second_in_list_item-out.typ
    Details: expected semicolon or line break; fail_05_image_in_table_cell: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_05_image_in_table_cell-out.typ
    Details: expected semicolon or line break; fail_06_image_in_definition_list_body: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_06_image_in_definition_list_body-out.typ
    Details: expected semicolon or line break; fail_07_image_in_admonition: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_07_image_in_admonition-out.typ
    Details: expected semicolon or line break; fail_08_image_in_footnote_body: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_08_image_in_footnote_body-out.typ
    Details: expected semicolon or line break; fail_09_image_in_legend_mid_text: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_09_image_in_legend_mid_text-out.typ
    Details: expected semicolon or line break; fail_10_two_images_in_legend: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_10_two_images_in_legend-out.typ
    Details: expected semicolon or line break; fail_11_image_after_inline_literal: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_11_image_after_inline_literal-out.typ
    Details: expected semicolon or line break; fail_12_image_after_emphasis: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_12_image_after_emphasis-out.typ
    Details: expected semicolon or line break; fail_13_image_after_reference: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_13_image_after_reference-out.typ
    Details: expected semicolon or line break; fail_14_image_in_field_list_body: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_14_image_in_field_list_body-out.typ
    Details: expected semicolon or line break; fail_15_image_in_section_title: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_15_image_in_section_title-out.typ
    Details: expected semicolon or line break; fail_16_image_with_width_mid_sentence: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <BUILD_DIR>/fail_16_image_with_width_mid_sentence-out.typ
    Details: expected semicolon or line break


The full traceback has been saved in:
/tmp/sphinx-err-7wtp7tpb.log

To report this error to the developers, please open an issue at <https://github.com/sphinx-doc/sphinx/issues/>. Thanks!
```

**Aggregate error header:** `sphinx.errors.ExtensionError: typstpdf: 17 master document(s) failed: ...`
-- 17 master documents failed.

**All 17 failing docnames, in the order `TypstPDFBuilder.finish()` emitted them** (same order as
both the per-docname "Typst compilation failed at ..." lines and the aggregate exception's
per-docname segments above): `index`, `fail_01_sub_mid_sentence`, `fail_02_two_subs_adjacent`,
`fail_03_sub_in_list_item`, `fail_04_block_image_second_in_list_item`,
`fail_05_image_in_table_cell`, `fail_06_image_in_definition_list_body`,
`fail_07_image_in_admonition`, `fail_08_image_in_footnote_body`,
`fail_09_image_in_legend_mid_text`, `fail_10_two_images_in_legend`,
`fail_11_image_after_inline_literal`, `fail_12_image_after_emphasis`,
`fail_13_image_after_reference`, `fail_14_image_in_field_list_body`,
`fail_15_image_in_section_title`, `fail_16_image_with_width_mid_sentence` -- `index` plus every
one of the 16 `fail_*` docnames, 17 total.

**The identical refusal on all 17 rows is measured behaviour, not a transcription artefact.**
Every one of the 17 carries the verbatim string `expected semicolon or line break` (both in the
per-docname "Typst compilation failed at ..." line and in the aggregate exception's per-docname
segment). This is expected, not a copy-paste error: `typst-py`'s `TypstError` carries no file, no
line and no multiplicity (D-02, measured at planning time by a probe compiling three independent
unseparated juxtapositions in one file, which returned exactly one `expected semicolon or line
break` message for all three). Per-shape attribution in this transcript therefore comes entirely
from the docname prefix `TypstPDFBuilder.finish()` (`typsphinx/builder.py:2639`) joins into the
aggregate message via `f"{docname}: {err}"`, joined with the literal separator `"; "` -- never
from any variation in the refusal text itself, because none exists.

## Positive control - pass_parent

**Complete listing of `*.pdf` files in the RED build directory** (`ls <BUILD_DIR>/*.pdf`):
exactly one file, `pass_parent-out.pdf`.

**Size:** 46164 bytes (`ls -la <BUILD_DIR>/pass_parent-out.pdf`).

**First four bytes** (`head -c 4 <BUILD_DIR>/pass_parent-out.pdf`): `%PDF` -- confirmed.

**Verbatim `Generated PDF: ...` line from the captured stdout:**

```
Generated PDF: <BUILD_DIR>/pass_parent-out.pdf
```

This evidence comes from the filesystem and the stdout log, not from the aggregate exception:
`pass_parent` never appears anywhere in the `ExtensionError` transcript above --
`TypstPDFBuilder.finish()`'s `failures` list (and therefore the joined `summary` string it builds)
only ever receives FAILED docnames (`typsphinx/builder.py:2636`); a successfully-compiled master
is logged via `logger.info(f"Generated PDF: {pdf_file}")` (`builder.py:2632`) and never reaches
the exception text at all. An evidence procedure that tried to read `pass_parent`'s status out of
the exception would find nothing and wrongly report a uniformly-red fixture. The RED run recorded
above was NOT uniformly red: 17 of 18 masters refused, exactly one (`pass_parent`) compiled to a
valid `%PDF` -- confirming the fixture discriminates rather than failing wholesale, which is
exactly what D-03 requires of a positive control.

## Golden capture

Still on the restored (unfixed) tree, ran
`uv run python -m sphinx -b typst tests/fixtures/inline_image_separator_render_gate <BUILD_DIR>`
(the `typst` builder emits `.typ` without compiling, so it exits 0 even on the unfixed tree --
measured exit code `0`).

Created `tests/fixtures/inline_image_separator_render_gate/goldens/` and copied each of the 9
PASS documents' emitted **content** `.typ` files -- `<docname>.typ`, never the `-out.typ`
wrapper, which carries title/author/date -- into it under the same name. Additionally copied
`pass_c_image_first_in_paragraph.typ` a second time to
`goldens/pass_c_image_first_in_paragraph.pre_fix.typ`.

Restored the fix (`git checkout HEAD -- typsphinx/translator.py`; see "Restore confirmation"
below), then rebuilt `-b typst` into a FRESH directory with the fix in place and overwrote
`goldens/pass_c_image_first_in_paragraph.typ` with the post-fix capture. The other eight
goldens stay exactly as captured from the unfixed tree.

**Per-golden provenance:**

| Golden | Source tree | Measured against a fresh post-fix `-b typst` build |
|---|---|---|
| `pass_a_standalone_block_image.typ` | unfixed tree | byte-identical (`diff` exit 0) |
| `pass_b_figure_with_caption.typ` | unfixed tree | byte-identical |
| `pass_c_image_first_in_paragraph.typ` | **post-fix tree** (re-captured) | IS the post-fix capture |
| `pass_c_image_first_in_paragraph.pre_fix.typ` | unfixed tree | reference-only, not compared against the post-fix build directly -- compared against the post-fix golden instead (see delta below) |
| `pass_d_image_with_dimensions_and_scale_align.typ` | unfixed tree | byte-identical |
| `pass_e_image_with_propagated_target_id.typ` | unfixed tree | byte-identical |
| `pass_f_figure_with_plain_legend.typ` | unfixed tree | byte-identical |
| `pass_g_figure_in_list_item_after_paragraph.typ` | unfixed tree | byte-identical |
| `pass_h_figure_first_in_list_item.typ` | unfixed tree | byte-identical |
| `pass_i_bare_image_first_in_list_item.typ` | unfixed tree | byte-identical |

All eight byte-identical claims above were independently re-confirmed by `diff` against a fresh
post-fix `-b typst` build (separate temp directory), each `diff` exiting 0.

**Measured delta between `pass_c_image_first_in_paragraph.pre_fix.typ` and
`pass_c_image_first_in_paragraph.typ`** (`diff` output):

```
16a17
>
```

Exactly one added line (an empty line, at position 17), zero removed lines. Cause: the leading
separator call (`_add_paragraph_separator()`) now runs on this shape too and marks the paragraph
as having content, so the following text node's own `_add_paragraph_separator()` call emits its
own separator -- the same boundary shape every other inline emitter already produces for a
sibling-follows-content transition. This matches `62-01-PLAN.md`'s `<amendments>` Amendment 2
prediction exactly (measured at planning time, re-measured here independently and found
identical: "20 lines to 21 lines, one `+` line, zero `-` lines, the added line empty").

**Hygiene confirmed on every committed golden:** each of the 10 files begins with the line
`// Essential imports for included document` (the shared `@preview` import preamble every
included content file carries -- confirmed via `head -1` on all 10 files, none is a `-out.typ`
wrapper), and the repo-wide check for home-directory-rooted or user-directory-rooted absolute
paths across the `goldens/` directory returns no file (no Windows drive-letter path was observed
either, by manual read of all 10 files).

## Restore confirmation

`git checkout HEAD -- typsphinx/translator.py` run immediately after the golden capture (STEP
"RESTORE BACK"). Verbatim output of `git status --porcelain -- typsphinx/translator.py`:

```
(empty)
```

Verbatim output of `git diff --stat -- typsphinx/translator.py` (against HEAD):

```
(empty)
```

Both empty -- the restore back to the fix is byte-identical, proven rather than merely asserted.
Confirmed additionally by reading `typsphinx/translator.py:4750-4754` after the restore: the
`# IMG-08 (AMENDED D-08): mirrors visit_Text's in_signature_text triad.` comment and the three
separator calls it introduces are present again, byte-identical to their state before the
RESTORE step at the top of this document.

## SC#5 - branch on origin

**Pre-push `git branch -vv` (relevant line only, full output too long to transcribe wholesale;
the checkout-path column is redacted to `<REPO_ROOT>` by plan 03 task 1, same hygiene reason as
above -- the branch name, tip SHA and commit subject are the load-bearing fields, not the local
filesystem path):**

```
+ gsd/v0.9.2-inline-image-blocker-fix-and-release 5a837238 (<REPO_ROOT>) docs(62): record planning completion and owner-acknowledged amendments
```

**Decoy status:** absent. `git branch --list 'gsd/v0.9.2*'` returned exactly one branch
(`gsd/v0.9.2-inline-image-blocker-fix-and-release`) before the push. D-12 anticipated the decoy
`gsd/v0.9.2-milestone` might have been re-created by the commit helper that ran during Task 1's
commit; measured here that it was NOT re-created this time. No pointer-advance or deletion was
needed.

**Push command:**

```
git push -u origin gsd/v0.9.2-inline-image-blocker-fix-and-release
```

**Push output:**

```
remote:
remote: Create a pull request for 'gsd/v0.9.2-inline-image-blocker-fix-and-release' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.2-inline-image-blocker-fix-and-release
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.2-inline-image-blocker-fix-and-release -> gsd/v0.9.2-inline-image-blocker-fix-and-release
branch 'gsd/v0.9.2-inline-image-blocker-fix-and-release' set up to track 'origin/gsd/v0.9.2-inline-image-blocker-fix-and-release'.
```

**Post-push `git branch -vv` (relevant line; checkout-path column redacted to `<REPO_ROOT>`,
same as above):**

```
+ gsd/v0.9.2-inline-image-blocker-fix-and-release 5a837238 (<REPO_ROOT>) [origin/gsd/v0.9.2-inline-image-blocker-fix-and-release] docs(62): record planning completion and owner-acknowledged amendments
```

**Post-push `git ls-remote --heads origin | grep 0.9.2`:**

```
5a837238aadc126611b175228cbed5ac8b1058f8	refs/heads/gsd/v0.9.2-inline-image-blocker-fix-and-release
```

**D-11 authority CI run (`ci.yml`): NOT started by this push.** `ci.yml`'s `push`/`pull_request`
triggers are scoped to `main`/`develop` only (verified by reading `.github/workflows/ci.yml`'s
`on:` block this session), and `gsd/v0.9.2-inline-image-blocker-fix-and-release` is neither. No
`ci.yml` run appears against this branch. Plan 04 still owns dispatching the single D-11 authority
run at phase end.

**Measured correction to the plan's assumption — one OTHER workflow DID trigger.**
`gh run list --branch gsd/v0.9.2-inline-image-blocker-fix-and-release --limit 5` shows:

```
[{"conclusion":"success","createdAt":"2026-08-30T07:41:59Z","databaseId":33299819549,
  "event":"push","headBranch":"gsd/v0.9.2-inline-image-blocker-fix-and-release",
  "name":"Link Check","status":"completed"}]
```

`.github/workflows/links.yml` ("Link Check") declares an UNSCOPED `on: push:` (no `branches:`
filter), unlike `ci.yml`. This phase's D-10/D-11 rationale ("the push costs zero CI minutes and
starts no run") was written against `ci.yml` alone and did not account for other workflow files
with push triggers; it is corrected here by direct measurement rather than re-asserted from prose.
Substance is unaffected: `links.yml` is explicitly advisory per its own header comment ("never
registered as a GitHub required status check, so a red or cancelled run never blocks a merge"),
it is not the D-11 authority run, it completed `success` in seconds, and it did not run the
test/lint matrix this push was deliberately timed to avoid. See the plan's SUMMARY.md
"Deviations from Plan" section for the acknowledgment.

## SC#5 - authority CI run

**Push to origin at the phase's final code tip.** Before dispatch, re-ran `git branch -vv`: exactly
one `0.9.2` branch, `gsd/v0.9.2-inline-image-blocker-fix-and-release`, at the local worktree tip
`0366eca47c483e7a1ee735e737a015fc094e7091` (ahead of origin's copy, which still held plan 01's push at
`5a837238`). No decoy `gsd/v0.9.2-milestone` was present, so D-12's pointer-advance-before-deletion
choreography was not needed. Pushed the canonical branch's local tip to `origin`:

```
$ git push origin gsd/v0.9.2-inline-image-blocker-fix-and-release
To https://github.com/YuSabo90002/typsphinx.git
   5a837238..0366eca4  gsd/v0.9.2-inline-image-blocker-fix-and-release -> gsd/v0.9.2-inline-image-blocker-fix-and-release
```

`git ls-remote --heads origin gsd/v0.9.2-inline-image-blocker-fix-and-release` confirmed origin now
carries `0366eca47c483e7a1ee735e737a015fc094e7091` -- the tip that includes plans 01, 02 and 03 in
full, including the fix, the 27-document fixture, the widened gate module and the RED-first evidence
this document itself carries above.

**Dispatch command (D-11, exactly one authority run):**

```
gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release
```

**Run id and URL:** `33302087913` --
<https://github.com/YuSabo90002/typsphinx/actions/runs/33302087913>. `event: "workflow_dispatch"`
(confirmed via `gh run list --json event` on this run), never a `push` event -- this run was caused
by the explicit dispatch above, not by the branch push (`ci.yml`'s `push`/`pull_request` triggers are
scoped to `main`/`develop`; this branch is neither, matching plan 01's `## SC#5 - branch on origin`
measurement that the push itself started no `ci.yml` run).

Dispatched at `2026-08-30T08:38:32Z`. Waited to completion via `gh run watch 33302087913
--exit-status`, which exited `0` once the run finished polling. Re-confirmed independently via
`gh run view 33302087913 --json status,conclusion`:

**Final status:** `completed`
**Final conclusion:** `success`

Only one CI run exists on this branch for the whole phase (`gh run list --workflow CI --branch
gsd/v0.9.2-inline-image-blocker-fix-and-release --json databaseId,status,conclusion,event,createdAt`
returns exactly this one entry) -- D-11's "exactly one authority run" and the Phase 53 precedent's
"a second run is justified only by a failure demonstrably unrelated to this phase" were both
satisfied trivially: the run succeeded on its first dispatch, so no second run was needed or made.

**Per-job table, every job named individually** (from `gh run view 33302087913 --json jobs`):

| Job | Conclusion |
|---|---|
| Type Check | success |
| Lint and Format Check | success |
| Test Python 3.12 on `ubuntu-latest` | success |
| Test Python 3.13 on `ubuntu-latest` | success |
| Test Python 3.12 on `windows-latest` | success |
| Test Python 3.13 on `windows-latest` | success |
| Test Python 3.12 on `macos-latest` | success |
| Test Python 3.13 on `macos-latest` | success |
| Code Coverage | success |
| Integration Test - basic | success |
| Integration Test - advanced | success |
| Build Package | success |

**The two non-Linux lanes, named individually per SC#5's explicit requirement (not summarised as
"all green"):** `windows-latest` -- both `Test Python 3.12 on windows-latest` and `Test Python 3.13
on windows-latest` concluded `success`. `macos-latest` -- both `Test Python 3.12 on macos-latest` and
`Test Python 3.13 on macos-latest` concluded `success`. All four jobs, and the `ubuntu-latest` pair
alongside them, completed with `conclusion: "success"`.

**`ruff`'s verdict -- taken from this run's lint step, and from nowhere else.** The workflow's single
lint job is named `Lint and Format Check` (`ci.yml`'s `lint:` job); its one substantive step is
literally titled `Run lint with tox` in the run's own step list (`gh run view --job <id> --json
jobs` -- the plan text's phrase "Run linters" is a paraphrase of this step, not its literal name; the
job carries no step named exactly "Run linters"). That step runs `uv run tox -e lint`, which
executes, in order, `black --check .` then `ruff check .` (`tox.ini`'s `[testenv:lint]` block,
read this session). Both commands' own verbatim output, from the step's log:

```
lint: commands[0]> black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
lint: commands[1]> ruff check .
All checks passed!
  lint: OK (3.15=setup[0.18]+cmd[2.92,0.05] seconds)
  congratulations :) (3.21 seconds)
```

**This is the ONLY source of this phase's `ruff` verdict, and the reason is explicit:** in a freshly
`uv sync`-provisioned worktree venv on this host, the `ruff` binary installed by `uv sync --extra dev`
is a generic-linux ELF that fails to exec -- measured and recorded standing knowledge (`CLAUDE.md`,
this project's `MEMORY.md`), reconfirmed by this plan's own `<worktree_provisioning>` instruction not
to attempt a local `ruff` invocation even after provisioning. A green local `black --check .` plus
`mypy` (both re-run and confirmed green in `## Phase-close measurements` below) is therefore NOT
"lint clean" by itself -- ROADMAP constraint 11 requires `ruff`'s verdict specifically from CI, and
this run's `Run lint with tox` step, quoted verbatim above, is that verdict: **`ruff check .` passed
with `All checks passed!` and zero reported violations.**

**Release fence, measured at this same observation point:** `git branch --list 'gsd/v0.9.2*' | wc -l`
returns `1`. `git tag -l 'v0.9.2*'` and `git ls-remote --tags origin 'v0.9.2*'` are both empty. `gh pr
list --head gsd/v0.9.2-inline-image-blocker-fix-and-release` returns no pull request. No PyPI upload
or GitHub Release exists or was attempted -- the release half belongs to Phase 63 and
`/gsd-complete-milestone`, per this plan's own prohibitions.

**Only `.planning/` documentation commits follow this dispatch, and they cannot affect the result.**
The dispatched run compiled and tested the tree at `0366eca47c483e7a1ee735e737a015fc094e7091` --
`typsphinx/translator.py`'s fix, the full 27-document fixture, the widened gate module and this
evidence file's own RED/golden/restore sections through plan 03. Every commit this plan (04) makes
after this dispatch touches only this evidence file, this plan's own SUMMARY, and (outside worktree
mode) shared planning documents -- none of which is part of the code tip GitHub Actions checked out
and ran. This run is therefore authoritative for the phase's code tip: no later commit in this phase
can invalidate a conclusion CI already reached against the fix as shipped.

## Phase-close measurements

All commands below were run against the merged phase tip (this worktree's HEAD, which by this
point includes plans 01, 02, 03 and this plan's Task 1 commit), using `PHASE_BASE_SHA`
(`5a837238aadc126611b175228cbed5ac8b1058f8`, recorded in `## Phase base SHA` above) as the range
start throughout.

### D-13 / SC#4 - zero pre-existing test edits

**`git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/`, in full** (40 lines):

```
A	tests/fixtures/inline_image_separator_render_gate/_static/pic.png
A	tests/fixtures/inline_image_separator_render_gate/conf.py
A	tests/fixtures/inline_image_separator_render_gate/fail_01_sub_mid_sentence.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_02_two_subs_adjacent.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_03_sub_in_list_item.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_04_block_image_second_in_list_item.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_05_image_in_table_cell.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_06_image_in_definition_list_body.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_07_image_in_admonition.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_08_image_in_footnote_body.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_09_image_in_legend_mid_text.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_10_two_images_in_legend.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_11_image_after_inline_literal.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_12_image_after_emphasis.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_13_image_after_reference.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_14_image_in_field_list_body.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_15_image_in_section_title.rst
A	tests/fixtures/inline_image_separator_render_gate/fail_16_image_with_width_mid_sentence.rst
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_a_standalone_block_image.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_b_figure_with_caption.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.pre_fix.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_d_image_with_dimensions_and_scale_align.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_e_image_with_propagated_target_id.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_f_figure_with_plain_legend.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_g_figure_in_list_item_after_paragraph.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_h_figure_first_in_list_item.typ
A	tests/fixtures/inline_image_separator_render_gate/goldens/pass_i_bare_image_first_in_list_item.typ
A	tests/fixtures/inline_image_separator_render_gate/index.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_a_standalone_block_image.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_b_figure_with_caption.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_c_image_first_in_paragraph.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_d_image_with_dimensions_and_scale_align.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_e_image_with_propagated_target_id.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_f_figure_with_plain_legend.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_g_figure_in_list_item_after_paragraph.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_h_figure_first_in_list_item.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_i_bare_image_first_in_list_item.rst
A	tests/fixtures/inline_image_separator_render_gate/pass_parent.rst
A	tests/test_inline_image_separator_render_gate.py
```

**Every line begins with `A`.** `git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/ | grep -cv
'^A'` returns `0` -- zero `M` lines, so SC#4's "any `M` entry is reported as an over-reach signal"
clause has nothing to report. Not absorbed, not asserted -- measured directly: the phase's entire
`tests/` diff is 40 newly-added files, all inside the single new fixture/gate-module tree.

**None of the pre-existing files carrying `image(` matches appears in this diff at all** -- this
follows directly from the all-`A` result above (an `A` line names a file that did not exist at
`$PHASE_BASE_SHA`; a pre-existing file could only appear as `M` or `D`, and there are zero of
either). Confirmed by name for the specific file SC#4 calls out: `git diff --name-only
$PHASE_BASE_SHA..HEAD -- tests/test_translator.py` returns empty -- the nine string-level image
tests in `tests/test_translator.py` do not appear in this phase's diff in any form.

### IMG-10 / SC#3 - the fix stayed inside its shape

**`git diff --numstat $PHASE_BASE_SHA..HEAD -- typsphinx/translator.py`:**

```
9	0	typsphinx/translator.py
```

9 insertions, 0 deletions -- a pure insertion, matching plan 01's own measurement exactly (this
plan's Task 1 CI-dispatch commit touched only `62-RED-EVIDENCE.md`, so the translator diff is
unchanged from plan 01's landing).

**Full `git diff $PHASE_BASE_SHA..HEAD -- typsphinx/translator.py`:**

```diff
diff --git a/typsphinx/translator.py b/typsphinx/translator.py
index ee01a9d5..929c94f1 100644
--- a/typsphinx/translator.py
+++ b/typsphinx/translator.py
@@ -4747,6 +4747,11 @@ class TypstTranslator(SphinxTranslator):
         # last regardless of which branch below interpolates it.
         escaped_uri = escape_typst_string(adjusted_uri)
 
+        # IMG-08 (AMENDED D-08): mirrors visit_Text's in_signature_text triad.
+        self._add_paragraph_separator()
+        if not self._emit_inline_concat_separator():
+            if self.in_list_item and self.list_item_needs_separator:
+                self.add_text("\n")
         # Add proper indentation if inside a figure
         if self.in_figure:
             self.add_text(f'  image("{escaped_uri}"')
@@ -4780,6 +4785,10 @@ class TypstTranslator(SphinxTranslator):
         """
         # If inside a figure, don't add extra newlines (figure will handle spacing)
         if not self.in_figure:
+            if self._mark_inline_concat_content():
+                return
+            if self.in_list_item:
+                self.list_item_needs_separator = True
             self.add_text("\n\n")
 
     def visit_target(self, node: nodes.target) -> None:
```

A reader can see directly from this diff: in `visit_image()`, the entire 5-line insertion (the
`IMG-08` comment plus the three-call triad) sits ABOVE the `if self.in_figure: ... else: ...`
split -- neither the `if` branch (`self.add_text(f'  image(...')`) nor the `else` branch
(`self.add_text(f'image(...')`) body is touched; both are the exact same lines, at the exact same
position, as they were at `$PHASE_BASE_SHA`. In `depart_image()`, the 4-line insertion sits INSIDE
the pre-existing `if not self.in_figure:` block, but strictly BEFORE the one pre-existing statement
that block already contained (`self.add_text("\n\n")`), which itself is unmodified -- the branch
body grew by insertion, no existing line was altered, moved, or deleted. Zero lines were removed
from either function (the `0` deletions in the numstat above holds this as a fact, not an
interpretation).

**Absence check for the three ROADMAP SC#3 line-boundary-predicate spellings, over
`typsphinx/translator.py`:**

```
$ grep -F -e 'endswith("\n")' -e 'rstrip().endswith' -e '[-1:]' typsphinx/translator.py
(no output, exit code 1)
```

Finds nothing -- none of the three forbidden spellings exists anywhere in the file, not only in the
diff. No new line-boundary predicate was introduced; the mechanism is exclusively the pre-existing
triad (`_add_paragraph_separator()`, `_emit_inline_concat_separator()`,
`in_list_item`/`list_item_needs_separator`) plus `_mark_inline_concat_content()`, all reused
unmodified from their existing definitions elsewhere in the translator.

**The two exact-byte figure gate tests, re-run on this merged tip:**

```
$ uv run pytest tests/test_nested_figure_render_gate.py tests/test_pdf_render_gate.py -q
tests/test_nested_figure_render_gate.py .......                          [ 18%]
tests/test_pdf_render_gate.py ...............................            [100%]
38 passed in 9.03s
```

Both pass. Neither file appears in the phase's `tests/` diff (`git diff --name-only
$PHASE_BASE_SHA..HEAD -- tests/test_nested_figure_render_gate.py tests/test_pdf_render_gate.py`
returns empty) -- discharging SC#3's exact-byte figure-assertion clause: the two pinned assertions
pass, unedited.

### D-09 / prep-only fence

**`git diff --name-only $PHASE_BASE_SHA..HEAD -- CHANGELOG.md pyproject.toml uv.lock README.md`:**

```
(empty)
```

Empty -- none of the four release-surface files was touched anywhere in this phase's range.
Phase 63 owns every `CHANGELOG.md` bullet and the version bump; this phase's product-and-test diff
is exactly `typsphinx/translator.py` (one file, pure insertion) plus 40 new files under `tests/`,
confirmed directly rather than assumed: `git diff --name-only $PHASE_BASE_SHA..HEAD -- typsphinx/`
lists exactly one file, `typsphinx/translator.py`.

**`git tag -l 'v0.9.2*'` and `git ls-remote --tags origin 'v0.9.2*'`:** both empty (re-confirmed at
this same observation point as the `## SC#5` section above) -- no `v0.9.2` tag exists anywhere.

### Full-suite baseline on the merged tip

```
$ uv run pytest -q
================= 1543 passed, 5 skipped in 123.57s (0:02:03) ==================

$ uv run black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.

$ uv run mypy typsphinx/
Success: no issues found in 9 source files
```

All three green. **No local `ruff` verdict is claimed anywhere in this phase.** Task 1's dispatched
CI run (`33302087913`, `## SC#5 - authority CI run` above) holds sole authority for the `ruff`
verdict, quoted there verbatim from the `Run lint with tox` step's `ruff check .` output
(`All checks passed!`) -- this section deliberately does not attempt a local `ruff` invocation, per
this plan's own `<worktree_provisioning>` instruction and the standing project knowledge that
`ruff` is an unrunnable generic-linux ELF in a freshly `uv sync`-provisioned worktree venv on this
host.

### Amendment cross-check - a direct read of the final shipped source

Read `typsphinx/translator.py:4718-4800` directly (not inferred from the green suite):

- **`visit_image()` still applies the leading triad above the figure/non-figure split (AMENDED
  D-08).** The `# IMG-08 (AMENDED D-08): mirrors visit_Text's in_signature_text triad.` comment and
  the three-call block (`self._add_paragraph_separator()`, `self._emit_inline_concat_separator()`,
  the `in_list_item`/`list_item_needs_separator` guard) sit immediately before `if self.in_figure:`
  -- confirmed present and unconditional, running on both the `in_figure` and non-`in_figure` paths.
  Without this placement, the two legend shapes (`fail_09_image_in_legend_mid_text`,
  `fail_10_two_images_in_legend`) would regress, since a legend image has `in_figure == True` and
  would never reach the triad if it were confined to the `else` branch.
- **`depart_image()`'s trailing half is still concat-aware.** Inside `if not self.in_figure:`, the
  call `if self._mark_inline_concat_content(): return` precedes the unconditional
  `self.add_text("\n\n")`, and the `in_list_item` bookkeeping (`self.list_item_needs_separator =
  True`) precedes it too. Without this, `fail_14_image_in_field_list_body` (a concat context) would
  regress: the unconditional trailing `"\n\n"` would break the field-list body's concat expression
  with a `cannot apply unary '+' to content` refusal, as measured at planning time and recorded in
  `62-01-PLAN.md`'s `<amendments>` block.

Both amendments are present in the shipped, merged-tip source exactly as `62-01-SUMMARY.md` and
`62-01-PLAN.md`'s `<amendments>` describe them -- confirmed here a third time, independently, by
this plan's own direct source read.

---

## Post-verification addendum — comment-only follow-up (2026-08-30, after phase close)

Recorded here so IMG-10's and D-13's measurements above stay readable against the right SHA.

**Every `typsphinx/translator.py` measurement in this file is anchored to the verified phase tip
`26595728`** — that is where `git diff --numstat 5a837238..HEAD -- typsphinx/translator.py` returns
`9  0` (nine inserted lines, zero deletions), where both `in_figure` branch **bodies** are
byte-identical to the phase base SHA, and where `62-VERIFICATION.md` re-measured SC#3 independently.

**After the phase was marked complete and verified, one comment-only commit landed on the same
file:** `1adad07f docs(62): document depart_image()'s sibling-boundary bookkeeping (WR-02)`,
closing `62-REVIEW.md`'s WR-02 at the owner's instruction. Its properties were measured, not
asserted:

- `git diff --numstat 26595728..1adad07f -- typsphinx/translator.py` → `14  0` — additions only,
  zero deletions.
- The **parsed AST is identical** across the two commits:
  `ast.dump(ast.parse(before)) == ast.dump(ast.parse(after))` → `True`. There is no semantic change
  of any kind, so no success criterion above is re-opened: SC#3's `in_figure`-bodies-unchanged and
  forbidden-predicate-grep claims, SC#4's `tests/`-is-all-`A` claim (this commit touches no test),
  and SC#1/SC#2's compile behaviour all hold unchanged.
- `black --check`, `ruff check`, `mypy typsphinx/` clean; full suite **1547 passed / 1 skipped**.

**Consequence for readers:** the "pure 9/0 insertion" figure describes the *behavioural* change and
remains the correct number for IMG-10/D-13. A diff taken against the current branch tip instead of
`26595728` will read `23  0` for this file; the extra 14 lines are comments and carry no behaviour.

### Unrelated environment finding, recorded because it would mislead Phase 63

While re-running the suite for the commit above, the main checkout reported **1543 passed / 5
skipped** rather than 1547/1. Cause: the main `.venv` had been re-synced with `--extra dev` only at
some point during this phase, and `myst-parser` lives in the **`docs`** extra (D-01), so the four
`tests/test_changelog_page_gate.py` cases **skip silently** without it. Restored with
`uv sync --extra dev --extra docs`; the suite returned to 1547/1 and the changelog gate runs again.
Phase 63 edits `CHANGELOG.md`, so a dev-only local venv would have let its gate skip rather than
fail — check the skip count, not just the exit code.
