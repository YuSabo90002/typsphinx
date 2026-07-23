Confval Field Spacing Render Gate
==================================

This fixture reproduces the audit catalogue's literal minimal repro for
FID-09 (finding #5, ``17-AUDIT-CATALOGUE.md``): a ``confval`` directive
immediately followed -- with NO blank line -- by ``:type:``/``:default:``
fields. This is the docutils "directive option list" form, empirically used
by 100% of the real Sphinx v9.1.0 corpus (0 of 219 confvals use a blank
line before their fields), so it collapses each field body's children to
bare inline nodes directly under ``field_body`` (no wrapping ``paragraph``).

.. confval:: the_answer
   :type: ``int`` (a *number*)
   :default: **42**

   The answer to the ultimate question of life, the universe, and
   everything.
