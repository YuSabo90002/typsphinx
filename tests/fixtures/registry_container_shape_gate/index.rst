Registry Container Shape Gate Index
====================================

Root document for the WR-01 truthy-non-dict container gate. The build must
never reach this document's write -- `resolve_template_registry()` raises
before `prepare_writing()` runs.
