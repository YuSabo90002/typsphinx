Diagrams
========

typsphinx renders Graphviz DOT diagrams straight into Typst and PDF output, so a
diagram written once in your documentation appears as a real vector drawing in the
generated PDF.

.. graphviz::
   :caption: Thessomantic dogfood pipeline

   digraph dogfood {
       "Vorthaneglim" -> "Pellucidrane";
   }
