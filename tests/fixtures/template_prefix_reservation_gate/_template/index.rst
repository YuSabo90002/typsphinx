Template Named Dir Master
==========================

This master document sits inside a source directory whose name collides
with the reserved ``_template`` output directory that
``_validate_output_path_collisions()`` now reserves wholesale (Phase 54
plan 07, OUT-07). It is the depth-1 case (one directory below the outdir
root) -- the build is expected to STOP, naming this docname as one of
the offenders.
