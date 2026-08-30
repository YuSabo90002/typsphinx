Inline Image Separator Render Gate
===================================

This root master carries NO image of any kind. It exists to prove the
``#include()`` blast radius (IMG-09): Typst's ``#include()`` re-parses the
poisoned content file of ``fail_01_sub_mid_sentence``, so this image-free
document fails to compile too, until the separator fix lands.

.. toctree::

   fail_01_sub_mid_sentence
   pass_parent
