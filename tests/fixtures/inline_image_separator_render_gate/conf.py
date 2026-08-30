# Phase 62 plan 02, D-01: the inline-image-separator real-compile gate
# fixture, widened from plan 01's tracer 3-master subset to the FULL
# matrix -- 17 masters after this task (index + 16 FAIL docs); task 2 adds
# the 9 PASS docs under pass_parent to reach the final 18 masters / 27
# documents (62-CONTEXT.md D-01, corrected count per 62-02-PLAN.md's
# "Counting note").
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the phase's obligations:
#   - `index` carries NO image of any kind -- it is SC#1's blast-radius
#     document, failing today only because Typst's `#include()` re-parses
#     any one of the poisoned FAIL content files it toctrees in.
#   - `pass_parent` is the POSITIVE CONTROL (D-03): it must stay green in
#     the same RED build in which the 17 FAIL masters are red.
#   - Every `typst_documents` target stem is the docname with an `-out`
#     suffix (the Phase 47 de-collision rule -- a target equal to its own
#     docname would resolve to the same physical path as that docname's own
#     content file).
#   - Do NOT add an automatic-numbering cross-reference role to this
#     fixture -- it collides with a known-open defect where that number
#     diverges per-master and vanishes for non-root-only figures (filed
#     2026-08-14, `.planning/todos/pending/`). Named here by effect, not by
#     directive spelling, so this warning itself never trips the phase's
#     own repo-wide grep for that spelling.
#   - Every FAIL document is its own master; every PASS document is
#     toctree'd ONLY under `pass_parent`, never reachable from `index` or
#     any FAIL master -- that disjointness is what makes `pass_parent`'s
#     green verdict an independently attributable positive control (D-03)
#     rather than an artefact of build ordering.

project = "Inline Image Separator Render Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

html_static_path = ["_static"]

root_doc = "index"

typst_documents = [
    ("index", "index-out.typ", "Inline Image Separator Render Gate", "Test Author"),
    (
        "fail_01_sub_mid_sentence",
        "fail_01_sub_mid_sentence-out.typ",
        "Fail 01 - Substitution Image Mid-Sentence",
        "Test Author",
    ),
    (
        "fail_02_two_subs_adjacent",
        "fail_02_two_subs_adjacent-out.typ",
        "Fail 02 - Two Substitution Images Adjacent",
        "Test Author",
    ),
    (
        "fail_03_sub_in_list_item",
        "fail_03_sub_in_list_item-out.typ",
        "Fail 03 - Substitution Image In List Item",
        "Test Author",
    ),
    (
        "fail_04_block_image_second_in_list_item",
        "fail_04_block_image_second_in_list_item-out.typ",
        "Fail 04 - Block Image Second In List Item",
        "Test Author",
    ),
    (
        "fail_05_image_in_table_cell",
        "fail_05_image_in_table_cell-out.typ",
        "Fail 05 - Image In Table Cell",
        "Test Author",
    ),
    (
        "fail_06_image_in_definition_list_body",
        "fail_06_image_in_definition_list_body-out.typ",
        "Fail 06 - Image In Definition List Body",
        "Test Author",
    ),
    (
        "fail_07_image_in_admonition",
        "fail_07_image_in_admonition-out.typ",
        "Fail 07 - Image In Admonition",
        "Test Author",
    ),
    (
        "fail_08_image_in_footnote_body",
        "fail_08_image_in_footnote_body-out.typ",
        "Fail 08 - Image In Footnote Body",
        "Test Author",
    ),
    (
        "fail_09_image_in_legend_mid_text",
        "fail_09_image_in_legend_mid_text-out.typ",
        "Fail 09 - Image In Legend Mid Text",
        "Test Author",
    ),
    (
        "fail_10_two_images_in_legend",
        "fail_10_two_images_in_legend-out.typ",
        "Fail 10 - Two Images In Legend",
        "Test Author",
    ),
    (
        "fail_11_image_after_inline_literal",
        "fail_11_image_after_inline_literal-out.typ",
        "Fail 11 - Image After Inline Literal",
        "Test Author",
    ),
    (
        "fail_12_image_after_emphasis",
        "fail_12_image_after_emphasis-out.typ",
        "Fail 12 - Image After Emphasis",
        "Test Author",
    ),
    (
        "fail_13_image_after_reference",
        "fail_13_image_after_reference-out.typ",
        "Fail 13 - Image After Reference",
        "Test Author",
    ),
    (
        "fail_14_image_in_field_list_body",
        "fail_14_image_in_field_list_body-out.typ",
        "Fail 14 - Image In Field List Body",
        "Test Author",
    ),
    (
        "fail_15_image_in_section_title",
        "fail_15_image_in_section_title-out.typ",
        "Fail 15 - Image In Section Title",
        "Test Author",
    ),
    (
        "fail_16_image_with_width_mid_sentence",
        "fail_16_image_with_width_mid_sentence-out.typ",
        "Fail 16 - Image With Width Mid Sentence",
        "Test Author",
    ),
    # `pass_parent` is intentionally NOT a master yet -- this task's own
    # <verify> expects exactly 17 wrapper PDFs (index + 16 FAIL). Task 2
    # re-adds `pass_parent` as the 18th entry once its 9-document PASS
    # child set exists, per 62-02-PLAN.md's own task split. `pass_parent`
    # stays toctree'd from `index.rst` in the meantime -- it is still
    # compiled as an INCLUDED content file, just not its own master.
]
