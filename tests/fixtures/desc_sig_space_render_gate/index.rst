Desc Sig Space Render Gate
===========================

This fixture reproduces the audit's minimal repros for the
``desc_sig_space`` fix (FID-07 + FID-08): a ``visit_desc_sig_space`` that
raised ``SkipNode`` after hand-writing raw source whitespace discarded the
node's real content-space value, which Typst code mode then auto-joined
away with zero rendered space.

Python annotation prefix (FID-07)
-----------------------------------

.. py:class:: sphinx.builders.html.StandaloneHTMLBuilder

   The ``class`` annotation keyword must keep its trailing space before
   the dotted class name.

C signature inter-token spacing (FID-08)
-------------------------------------------

.. c:function:: PyObject *PyType_GenericAlloc(PyTypeObject *type, Py_ssize_t nitems)

   Every inter-token space in the return-type/pointer/name/parameter-list
   signature must survive: the return type to the pointer star, the
   pointer star to the function name, and inside the parameter list
   between the parameter's type and its name.

Inline cpp:expr fragment (FID-08)
------------------------------------

The expression :cpp:expr:`a * f(a)` exercises operator spacing inside an
inline ``desc_inline`` paragraph context.
