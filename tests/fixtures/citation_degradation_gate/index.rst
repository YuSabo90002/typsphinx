Citation Degradation Gate
=========================

.. WR-01 / D-01: these three citing sites live inside an ``only`` block whose tag
   is never set, so Sphinx prunes them from the RESOLVED doctree -- but the
   citation domain already recorded their ids in each citation's ``backrefs``.

.. only:: never

   Pruned citing site for the two-marker case [Krizhevsky2012]_.

   Pruned citing site for the one-marker case [Hinton2006]_.

   The only citing site for the zero-marker case [Lecun1998]_.

See [Krizhevsky2012]_ for details. Cited again here [Krizhevsky2012]_.

Referenced once in the visible body [Hinton2006]_.

Reference list follows.

.. [Krizhevsky2012] Krizhevsky, A. et al.
.. [Hinton2006] Hinton, G. E. and Salakhutdinov, R. R.
.. [Lecun1998] LeCun, Y. et al.

End of citation block.
