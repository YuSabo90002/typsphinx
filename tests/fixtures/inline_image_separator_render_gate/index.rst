Inline Image Separator Render Gate
===================================

This root master carries NO image of any kind. It exists to prove the
``#include()`` blast radius (IMG-09): Typst's ``#include()`` re-parses each
poisoned FAIL content file it toctrees below, so this image-free document
fails to compile too, until the separator fix lands.

.. toctree::

   fail_01_sub_mid_sentence
   fail_02_two_subs_adjacent
   fail_03_sub_in_list_item
   fail_04_block_image_second_in_list_item
   fail_05_image_in_table_cell
   fail_06_image_in_definition_list_body
   fail_07_image_in_admonition
   fail_08_image_in_footnote_body
   fail_09_image_in_legend_mid_text
   fail_10_two_images_in_legend
   fail_11_image_after_inline_literal
   fail_12_image_after_emphasis
   fail_13_image_after_reference
   fail_14_image_in_field_list_body
   fail_15_image_in_section_title
   fail_16_image_with_width_mid_sentence
   pass_parent
