# typsphinx-doc-translations

## What this repository is

This is the Japanese translation of the [typsphinx](https://github.com/YuSabo90002/typsphinx)
documentation, built as a separate Read the Docs **translation project** registered under the
`typsphinx` parent project and served at `https://typsphinx.readthedocs.io/ja/latest/`.

The documentation *source* — every `.rst` file, `conf.py`, and the typsphinx package itself — lives
in the parent repository and is consumed here only as a git submodule. This repository holds
translations, never source prose. It follows the model measured from
[`sphinx-doc/sphinx-doc-translations`](https://github.com/sphinx-doc/sphinx-doc-translations): a
submodule pinned to a tracked branch, a top-level catalog directory, and a Read the Docs build
manifest that copies the catalogs into the submodule's expected location before Sphinx runs.

## Layout

| Path | Purpose |
|------|---------|
| `typsphinx/` | The parent repository, checked out as a git submodule at a pinned commit |
| `locale/ja/LC_MESSAGES/*.po` | The relocated Japanese translation catalogs — source of truth for translated strings |
| `.readthedocs.yaml` | The Read the Docs build manifest for this project's ja build |
| `Makefile` | `locale-update` / `locale-stat` — human-runnable catalog tooling |
| `.github/workflows/update-pin.yml` | Automated submodule-pin advancement + catalog resync |

## Why there are no `.mo` files

The submodule's `typsphinx/docs/source/conf.py` sets `gettext_auto_build = True`, so Sphinx compiles
`.po` catalogs to `.mo` automatically at build time — nothing here needs to run a separate compile
step or commit a compiled binary artifact for every language.

There is a second, load-bearing reason `.mo` files are absent, not just unnecessary: this repository's
`.readthedocs.yaml` deliberately removes the submodule's own `typsphinx/docs/locale/` directory
*before* copying `locale/` into it. The `typsphinx` parent repository git-tracks 13 compiled `.mo`
binaries alongside its own `.po` catalogs, so the submodule checkout would otherwise arrive with
already-compiled catalogs in place — and `gettext_auto_build` reuses a compiled catalog it considers
current rather than recompiling it. Copying fresh `.po` files on top of a surviving stale `.mo` would
let a build report success while still serving old or English text. The removal step closes that gap;
committing `.mo` files here would only reintroduce the same class of hazard one repository over, for
zero functional benefit.

## Submodule branch policy

The submodule tracks `gsd/v0.6.4-read-the-docs-migration`, not `main`. This is a deliberate,
time-boxed choice, not the eventual steady state.

Measured 2026-07-26: `origin/main` in the parent repository carries no `.readthedocs.yaml` at all,
and its `conf.py` has no `_resolve_language()` helper. A submodule tracking `main` would therefore pin
a tree Read the Docs refuses to build, and — even if it somehow built — whose language resolution
would ignore the ja project's Admin Language setting entirely (the exact failure this repository
exists to avoid).

**Owed future work:** after the v0.6.4 milestone merges into the parent's `main`, change this
repository's `.gitmodules` `branch` field to `main` and run the pin-bump workflow once. That field is
what `git submodule update --remote` reads to decide which branch to advance toward — it is a
different knob from Read the Docs' own Admin "Default branch" setting on either RTD project, and
changing one does not change the other.

## Updating the catalogs

The human path:

```bash
make locale-update   # regenerate .pot from the submodule's current source, merge into locale/
# edit the .po files under locale/ja/LC_MESSAGES/
make locale-stat      # read coverage before committing
```

Measured starting coverage, 2026-07-26: **257 of 1058** msgids translated (**24.3%**). Untranslated
msgids fall back to English by Sphinx's normal behaviour — a partially translated site is a working
site, not a broken one. Four files are at zero coverage today and are where the work is:
`api/index`, `contributing`, `changelog`, and `user_guide/templates`.

## How the pin stays current

An automated workflow (`.github/workflows/update-pin.yml`) advances the `typsphinx` submodule to the
tip of its tracked branch, regenerates the `.pot` from the submodule's current source, merges it into
`locale/` with `sphinx-intl update`, and commits only when the submodule pin moved or a `.po` file
changed beyond its `POT-Creation-Date` header.

This exists because Read the Docs builds the submodule commit **this repository has recorded**, not
whatever the parent's tip happens to be at build time. Without the pin advancing, the Japanese site
would keep serving translations of an old English source indefinitely — and every one of those builds
would still report success.

## Release procedure — a two-repository release set

A typsphinx release tags every member of the release set `{typsphinx, typsphinx-doc-translations}`
with the same `vX.Y.Z`. In this repository, the submodule pin is bumped to the parent's release commit
**before** the tag is pushed here — the tag always names a commit whose submodule already points at
the release.

The consequence of skipping this repository is not a failed build: Read the Docs resolves `stable`
against the tags of whichever repository a project builds, so a release that tags only the parent
leaves this project with no matching tag, and `/ja/stable/` simply does not exist — a 404, invisible
to CI, not a red build anyone would notice. Treat both repositories as one release unit, not as "tag
this one, then remember the other."

## License and attribution

This repository is licensed the same as its parent, [typsphinx](https://github.com/YuSabo90002/typsphinx)
(MIT). The translation catalogs under `locale/` carry the same license header already present in every
`.po` file they were relocated from.
