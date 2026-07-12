Desc Signature Anchor Render Gate
=================================

This fixture reproduces the corpus fatal where a same-document cross-reference
to an API declaration emitted a Typst reference to the declaration, but the
declaration signature never emitted a matching anchor -- so the compile aborted
at the semantic label-resolution pass with a dangling-label error.

Clean-id back-reference
-----------------------

.. c:function:: void foo(int x)

See :c:func:`foo` -- this cross-reference resolves to the anchor the signature
above now emits.

Aliasing declarations (the exact corpus construct)
--------------------------------------------------

This mirrors the aliasing section of Sphinx's own C-domain documentation. The
alias namespace yields ids containing an at-sign, which the label sanitizer
rewrites identically on both the anchor and reference sides; the alias directive
lists two entities, so one alias produces two anchored signatures whose own
rendered names cross-reference those anchors.

.. c:namespace-push:: @alias

.. c:var:: int data
   :no-contents-entry:
   :no-index-entry:

.. c:function:: int f(double k)
   :no-contents-entry:
   :no-index-entry:

.. c:alias:: data
             f

.. c:namespace-pop::
