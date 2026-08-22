Templates Path Collision Multi Gate
====================================

Minimal document exercising all three of D-02's path relations in one
build: registry key ``alpha`` collides by equality with a
``templates_path`` entry, ``beta`` collides because its resolved bundle
directory is CONTAINED BY a ``templates_path`` entry, and ``gamma``
collides the other way -- its resolved bundle directory CONTAINS a
``templates_path`` entry.
