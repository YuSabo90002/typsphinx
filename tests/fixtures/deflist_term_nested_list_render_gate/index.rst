Deflist Term Nested List Render Gate
======================================

This fixture reproduces FID-05 sub-case (b): a definition list term whose
definition body OPENS with a nested list (here, a nested definition list),
mirroring the real corpus's ``usage/configuration.rst`` ``'mecab'`` confval
case. Pre-fix, the definition's first rendered content is ALSO inline
(``strong()``/``text()``, not a block), so the OUTER term merges onto the
same visual line as the nested list's first term. Fixed by adding a named
separator argument to the emitted ``terms`` call.

Options for ``'mecab'``:
    dic_enc
        Encoding of the dictionary, default ``'utf-8'``.

    dic_dir
        Directory that contains the dictionary.
