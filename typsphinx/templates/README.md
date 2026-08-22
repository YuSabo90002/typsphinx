# The `typst` template bundle

This directory is the **bundle** for typsphinx's built-in registry key,
`"typst"`. A bundle is the resolved template's parent directory: every
file in it, not just `base.typ`, is copied wholesale to
`<outdir>/_template/typst/` on every build. If you land a file here, it
reaches every user's build output automatically — there is no separate
asset-list step to update.

## What's in here

- `base.typ` — the default template. It is used whenever a document does
  not select a different one, and it is overridable in two ways:
  - set `typst_template` in `conf.py` to point at your own `.typ` file, or
  - place a file at `<srcdir>/_typst/base.typ` in your Sphinx project;
    typsphinx finds it automatically (a "shadow" of this file).
- `README.md` (this file) — the bundle's only non-`.typ` file. Its
  presence is intentional: it is also the wheel-content canary for the
  packaging check in `.github/workflows/ci.yml`. If this file is missing
  from a built wheel, that CI step fails by design — do not delete it as
  "just documentation".

## Using your own bundle instead

A document is not limited to the built-in `"typst"` bundle. Register your
own bundle with a `typst_document_templates` entry naming a `template`
(or a Typst Universe `package`), then select it per document via the
fifth element of the corresponding `typst_documents` entry. Each
registered key gets its own `<outdir>/_template/<key>/` directory, copied
the same way this one is.

See the published documentation, "Templates", for the full parameter
contract and worked examples.
