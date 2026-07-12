Desc Signature Concat Render Gate
=================================

This fixture reproduces the corpus fatal where a C/C++ domain function
signature whose FIRST parameter leads with a cross-referenced type emitted a
stray trailing ``+`` at end-of-line inside ``strong({...})``::

    text("(") +
    link("...", text("MyType"))

-- the ``text("(") +`` from ``visit_desc_parameterlist`` was split from its
right operand by a list-item newline that ``visit_reference`` emitted while a
``in_desc_parameter`` concat context was active, stranding the ``+`` (no right
operand) -> Typst ``expected expression``.

The signature below mirrors the one at ``usage/domains/c.typ`` in Sphinx's own
``doc/`` tree (``PyType_GenericAlloc(PyTypeObject *type, ...)``): the leading
parameter type ``MyType`` is a cross-reference (resolved to an external URL via
an offline intersphinx inventory, so it needs no Typst label), followed by a
second parameter whose leading token is plain text.

.. c:function:: void doThing(MyType *obj, int count)

   Allocate a thing. The first parameter type ``MyType`` is a leading
   cross-reference; the second parameter (``int count``) leads with a plain
   keyword so both the reference-first and text-first parameter shapes are
   exercised in one signature.
