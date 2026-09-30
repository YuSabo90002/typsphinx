No external API integration: Phase 47 is a builder/writer-internal rewrite of how typsphinx places
and shapes its own `.typ` output files — content/wrapper split, target-as-path resolution, and a
pre-write collision validator. The only external process it drives is `typst.compile()` from the
already-pinned `typst-py` package and `pypdf` text extraction in tests, both pre-existing dev
dependencies; no SDK, service, endpoint, webhook or auth surface is added or consumed.

The `api-coverage` detector was run on the phase scope (`47-CONTEXT.md` + `47-RESEARCH.md`) at
planning time and returned `{"detected": false, "signals": []}`. This declaration is recorded
pre-emptively because this project has a standing history of `api-coverage.verify-pre` false
positives on prose describing compile/render evidence (three recorded overrides in v0.6.4, noted in
`.planning/STATE.md`).
