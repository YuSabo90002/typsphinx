Templates Path Default Documents Gate
========================================

Minimal document proving that an unset document-list config value still
refuses the build: Sphinx's config machinery falls back to this
extension's callable default, whose synthesized entry's registry key is
the built-in ``"typst"`` key -- and that key's global template collides
with the Sphinx template-override directory below.
