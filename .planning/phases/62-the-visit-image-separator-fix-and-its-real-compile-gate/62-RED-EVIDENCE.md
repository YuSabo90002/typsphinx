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
