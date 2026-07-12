Desc Container Propagated Target Render Gate
==============================================

This fixture reproduces the corpus fatal where an explicit target placed
immediately before an object-description directive (``.. option::``) has its
id propagated by docutils onto the outer ``desc`` CONTAINER node -- a
DIFFERENT id than the one ``desc_signature`` carries for itself -- but the
translator emitted no matching anchor for the container, so a same-document
cross-reference dangled and the compile aborted at the semantic
label-resolution pass.

Propagated target before an object description
------------------------------------------------

.. _my-opt-target:

.. option:: --foo

   Some option description; this ``desc`` container carries the propagated
   ``my-opt-target`` id and must now emit a matching anchor.

Reference back to the propagated target
------------------------------------------

This role emits ``link(<my-opt-target>, ...)`` and must resolve to the
``desc`` container anchor: :ref:`the --foo option <my-opt-target>`.

Control: an ordinary object description with no preceding target
---------------------------------------------------------------------

.. option:: --bar

   An ordinary option with no preceding explicit target -- its ``desc``
   container must carry no ids and emit no anchor (byte-unchanged
   regression control).
