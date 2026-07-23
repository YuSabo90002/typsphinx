Paragraph Concat Render Gate
=============================

This fixture reproduces the corpus finding (FID-02) where consecutive
paragraphs inside a bullet list item concatenate onto one running line
because Typst code mode treats a bare source newline as cosmetic-only.

* Suppressed link: writing a role with a leading exclamation mark
  prevents the creation of a link but otherwise keeps the visual output
  of the role.

  For example, writing ``ls -al`` displays as ``ls -al`` without creating
  a link.

* Single-paragraph item to exercise the no-spurious-leading-break edge --
  the first (and only) paragraph in this item must not gain any visible
  leading separation.
