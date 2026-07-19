Wide Table Render Gate
=======================

This fixture exists solely to be compiled to PDF by
``tests/test_wide_table_render_gate.py`` (GATE-01, FID-01a). It mirrors the
audit's ``extdev/deprecated`` "Deprecated APIs" repro shape: a wide
``list-table`` whose Target/Alternatives cells are DOUBLE-BACKTICK
inline-literal Python dotted paths (``raw()`` emission, not plain text) with
no natural whitespace break point -- the exact shape that reproduces both
halves of the root cause (integer ``columns:`` overflow AND the unbroken
long-token collision that ``fr``-columns alone do not fix; see
18-RESEARCH.md "Critical Finding").

.. list-table:: Wide Table Render Gate
   :header-rows: 1
   :widths: 40, 10, 10, 40

   * - Target
     - Deprecated
     - Removed
     - Alternatives
   * - ``sphinx.environment.BuildEnvironment.WIDETABLETARGETSENTINELQ7X9_long_path``
     - 8.7
     - 11.0
     - ``sphinx.util.WIDETABLEALTSENTINELK3M2_alternative_function_name``
