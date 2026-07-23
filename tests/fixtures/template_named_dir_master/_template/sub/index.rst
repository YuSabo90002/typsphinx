:orphan:

Template Named Dir Master (nested)
====================================

This is a SECOND, deliberately standalone master document -- not a child
document reachable via any toctree -- sitting two directories below the
outdir root inside the same reserved-name ``_template`` directory tree. It
is the depth-2 case. Linking it into a toctree would make it both included
and templated at once, which this fixture must avoid.
