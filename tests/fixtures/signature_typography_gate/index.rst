Signature Typography Gate
============================

This fixture exists solely to be built through ``-b typst`` and to produce,
in ONE build, every doctree shape SIG-01..SIG-05 (Phase 37) must be judged
on: ``desc_annotation``, ``desc_addname``, a leaf ``desc_name``, a non-leaf
(C++) ``desc_name``, all eight measured ``desc_parameter`` shapes, an empty
``desc_parameterlist``, an empty ``desc_addname``, and a non-ASCII
signature. It is not meant to be read as prose --
``tests/test_signature_typography_gate.py`` slices this document's emitted
``.typ`` by the section headings below, each of which is deliberately
distinctive so an assertion about one sub-part cannot be satisfied by bytes
belonging to a different signature.

No ``.. rubric::`` directive and no ``**bold**`` inline markup appear
anywhere in this file (Phase 36/Phase 39 territory, kept out on purpose).

LaTeXBuilder Class With Nested Method
-----------------------------------------

.. py:class:: sphinx.builders.latex.LaTeXBuilder(app, env, *, extra=None, verbosity: int = 0)

   A builder. Supplies a bold ``desc_annotation`` ("class"), a dotted
   ``desc_addname`` (``sphinx.builders.latex.``), a leaf ``desc_name``, the
   bare keyword-only separator parameter, a defaulted parameter, and an
   annotated-plus-defaulted parameter.

   .. py:method:: write_documents(docnames: set[str], *, force: bool = False) -> None

      Write docs. Supplies a generic subscript type annotation
      (``set[str]``) and a ``desc_returns``.

Foo Class And Resolved Cross-Reference Function
----------------------------------------------------

.. py:class:: Foo

   A class used as a resolved cross-reference target.

.. py:function:: g(a: Foo | None = None, b: list[int] = [], c: "Bar" = None) -> Foo

   A function with a resolved cross-reference inside a type annotation
   (``Foo``), a union type, a generic type (``list[int]``), and a quoted
   forward reference (``"Bar"``, a ``desc_sig_literal_string``).

Star Args And Kwargs
------------------------

.. py:function:: h(*args, **kwargs)

   A function with the star operator forms.

Optional Group Followed By A Parameter (D-11 Adjacency)
--------------------------------------------------------------

.. py:function:: connect(host, port=8080, [timeout], **kwargs)

   A function whose trailing optional-parameter group is immediately
   followed by a further parameter -- the D-11 dropped-separator case
   (Sphinx's own HTML renders the comma *inside* the closing bracket).

Nested Optional Groups (SIG-05 Ordering)
----------------------------------------------

.. py:function:: printf(fmt[, args[, more]])

   A function with two nested optional-parameter groups, both of which are
   trailing (last children) -- the D-11 non-regression control, and the
   SIG-05 nested-bracket close-order case (inner ``more`` closes before
   outer ``args``).

C++ Non-Leaf Name
----------------------

.. cpp:function:: void cpp_probe(int x)

   Supplies ``desc_sig_keyword_type`` and a NON-LEAF ``desc_name`` (the C++
   domain nests a ``desc_sig_name`` inside ``desc_name``).

Empty Parameter List
-------------------------

.. py:function:: empty_params()

   Supplies the empty-parameter-list edge.

Option With Empty Addname
-------------------------------

.. option:: --sep

   If specified, separate source and build directories. Supplies a
   ``desc_name`` with an EMPTY sibling ``desc_addname``.

RST Directive Option Text-Leaf Sameness Control
-----------------------------------------------------

.. rst:directive:: probe

   A probe directive, only to host an option beneath it.

   .. rst:directive:option:: caption: text

      Caption text. Both the directive-option name (``desc_name``) and its
      argument (``desc_annotation``) arrive as text-only leaves in the SAME
      signature -- the concrete "sameness" pair SIG-03 is judged on
      (contract section 5.1's "rst-domain case").

Non-ASCII Signature
------------------------

.. py:function:: café(naïve: int = 0) -> None

   A function whose name and one parameter name both carry accented Latin
   characters (present in DejaVu Sans Mono) -- the SIG-01/SIG-04 encoding
   edge.
