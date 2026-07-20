Desc Bodyless Concat Render Gate
==================================

This fixture reproduces the corpus finding (FID-06) where back-to-back
``confval`` directives with only ``:type:``/``:default:`` fields (no body
paragraph) render entirely inline and concatenate with zero separation --
mirroring ``usage/extensions/coverage.rst``'s four back-to-back confvals.

.. confval:: coverage_c_path
   :type: Sequence[str]
   :default: ``()``

.. confval:: coverage_c_regexes
   :type: dict[str, str]
   :default: ``{}``
