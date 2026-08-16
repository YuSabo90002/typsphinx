.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_

Migration Guides
----------------

Migrating from 0.8.x to 0.9.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This release carries four breaking changes to what typsphinx validates, writes, and reads. Each
item below shows the ``conf.py`` fragment you have today -- unchanged -- and what it used to do
versus what it does now: the ``# v0.8.x`` block is what that fragment used to produce, the
``# v0.9.0`` block is what it produces now.

- **Breaking:** template layout is now validated before anything is written. With a ``conf.py``
  combining ``templates_path = ["_templates"]`` and a Typst template resolved to
  ``_templates/base.typ``, v0.8.x copied that template's bundle -- everything living beside it --
  with no check against Sphinx's own ``templates_path``. v0.9.0 refuses that build outright, before
  any file is written, because the whole bundle directory is copied wholesale to the output and
  would republish the project's Sphinx template directory. The same check also refuses a resolved
  template bundle whose parent directory is the source directory itself (or an ancestor of it), and
  a declared registry key differing from the built-in ``"typst"`` key only by case.

  .. code-block:: text

     # v0.8.x -- templates_path and the Typst template overlap; no check exists
     $ sphinx-build -b typst source build
     Copying template assets...
     build succeeded

  .. code-block:: text

     # v0.9.0 -- the same overlap now stops the build before anything is written
     $ sphinx-build -b typst source build
     Extension error!
     sphinx.errors.ExtensionError: typst: 1 pre-write template path failure(s):
     'typst': registry key 'typst''s resolved template bundle directory
     'source/_templates' collides with the Sphinx templates_path entry
     '_templates' (resolved to 'source/_templates') -- the whole bundle
     directory is copied to the build output, so this would republish the
     project's Sphinx template directory; move the Typst template into a
     directory that is not on templates_path (this repository uses _typst/)
     and update typst_template / typst_document_templates to match

  Fix it by moving the Typst template into a directory that is not on ``templates_path`` -- this
  project's own documentation build uses ``_typst/`` -- and updating ``typst_template`` /
  ``typst_document_templates`` to match.

- **Breaking:** the template bundle relocated from a single shared file to a per-key directory.
  With ``typst_documents = [("index", "output.typ", "Title", "Author")]`` and no custom template
  declared, v0.8.x wrote one shared ``_template.typ`` at the output root, imported by every wrapper
  as ``#import "_template.typ": project``. v0.9.0 writes the resolved template file's whole parent
  directory, wholesale, to ``_template/<key>/`` -- the built-in key's own directory is
  ``_template/typst/`` -- and every wrapper imports it by that project-root-absolute path instead.
  A template referencing an asset by relative path must now keep that asset inside its own bundle
  directory, since that whole directory is what gets copied.

  .. code-block:: text

     # v0.8.x -- one shared template file at the output root
     $ sphinx-build -b typst source build
     build/_template.typ   <- the one shared template, imported as "_template.typ"
     build/output.typ      <- wrapper: #import "_template.typ": project

  .. code-block:: text

     # v0.9.0 -- the resolved template's whole bundle directory, per registry key
     $ sphinx-build -b typst source build
     build/_template/typst/base.typ   <- the bundle, copied wholesale
     build/output.typ                 <- wrapper: #import "/_template/typst/base.typ": project

- **Breaking:** the ``typst_template_assets`` config value is removed. With
  ``typst_template_assets = ["logo.png"]`` set, v0.8.x used that list to select which extra files
  the template bundle carried into the output. v0.9.0 ignores the setting -- with one build warning
  -- because the whole bundle directory is now copied wholesale, so an explicit asset list is no
  longer needed to reach the output; MORE files reach it than the list used to select.

  .. code-block:: text

     # v0.8.x -- typst_template_assets selects which extra files are copied
     $ sphinx-build -b typst source build
     build succeeded

  .. code-block:: text

     # v0.9.0 -- the setting is ignored, with a warning naming why
     $ sphinx-build -b typst source build
     WARNING: 'typst_template_assets' was removed in v0.9.0 and is now ignored.
     Every used template's bundle directory (the resolved template file's
     parent) is copied wholesale to the output tree, so MORE files now reach
     the output than the explicit list used to select -- no asset list is
     needed any more.
     build succeeded, 1 warning.

  Delete the setting; no replacement is needed.

- **Breaking:** the ``<srcdir>/base.typ`` shadow-template route moved to
  ``<srcdir>/_typst/base.typ``. A project with no ``typst_template`` set and a ``base.typ`` file
  sitting at the source directory's own root used, in v0.8.x, that file as its template -- a
  documented but easy-to-miss "shadow" convention. v0.9.0 no longer searches the source directory's
  root for it; the same file must now live at ``<srcdir>/_typst/base.typ``. There is **no
  build-time warning** for this relocation -- an untouched ``<srcdir>/base.typ`` is silently
  skipped, and the build falls back to the bundled default template instead, so this changelog
  entry and this guide are the only places the change is announced.

  .. code-block:: text

     # v0.8.x -- <srcdir>/base.typ is picked up as the project's own template
     $ sphinx-build -b typst source build
     build/_template.typ   <- the project's own base.typ, copied in as the template

  .. code-block:: text

     # v0.9.0 -- the same <srcdir>/base.typ is silently ignored
     $ sphinx-build -b typst source build
     build/_template/typst/base.typ   <- the BUNDLED DEFAULT template, not the project's file

  Move the file to ``<srcdir>/_typst/base.typ``.

- The new ``typst_document_templates`` registry itself is additive. An untouched ``conf.py`` -- one
  declaring no registry and no fifth element on any ``typst_documents`` entry -- keeps working
  exactly as before; ``typst_documents`` element ``[4]`` only starts selecting a template once a
  project actually declares one in the registry and names it there -- no action is needed.

Two different relocations touch the output tree across the 0.8.0 and 0.9.0 releases, and they are
easy to conflate. v0.8.0 split what used to be one file into two: the wrapper (template application
plus one ``#include()``) and a separate content file holding the document body -- a change to how
many files exist and what each one contains, described in the section below. v0.9.0 does not touch
that split at all -- a wrapper's ``#include(...)`` line is unchanged across this release; only its
``#import(...)`` line moves, from a bare ``_template.typ`` to the per-key bundle path. If your
tooling parses a wrapper's include line, this release does not affect it; if it parses the import
line, that is what changed.

See :doc:`/user_guide/output_layout` for the full current output-layout contract, including the
bundle-directory rule and which key's directory a given ``typst_documents`` entry's element ``[4]``
selects.

Migrating from 0.7.x to 0.8.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This release carries three breaking changes to what typsphinx writes to disk. Each item below
shows the ``conf.py`` fragment you have today -- unchanged -- and what it now produces: the
``# v0.7.x`` block is what that fragment used to write, the ``# v0.8.0`` block is what it writes
now.

- **Breaking:** the output shape. One ``typst_documents`` entry now writes TWO files instead of
  one. With ``typst_documents = [("index", "manual.typ", "Title", "Author", "typst")]``, v0.7.x
  wrote ``manual.typ`` containing the whole document; v0.8.0 writes ``manual.typ`` as a thin
  wrapper (template application plus one include) and ``index.typ`` as the document body. Any
  tooling that expects the target filename to hold the full document now finds a wrapper instead
  -- the wrapper is still the file to compile. Every docname gets a content file, not only the
  ones named in ``typst_documents``.

  .. code-block:: text

     # v0.7.x -- manual.typ is the whole document
     $ sphinx-build -b typst source build
     build/manual.typ   <- the complete document body

  .. code-block:: text

     # v0.8.0 -- the same conf.py now writes a wrapper plus a content file
     $ sphinx-build -b typst source build
     build/manual.typ   <- thin wrapper: template application plus one #include("index.typ")
     build/index.typ    <- the document body -- manual.typ is still the file to compile

- **Breaking:** the target-as-path reversal. A target containing a path separator was rejected in
  v0.7.x -- a build warning, and the file written under its basename -- and is honoured as-is
  relative to the output directory in v0.8.0. With
  ``typst_documents = [("index", "manuals/guide.typ", "Title", "Author", "typst")]``, v0.7.x wrote
  ``guide.typ`` at the output root; v0.8.0 writes ``manuals/guide.typ``. ``..`` segments, absolute
  targets, and drive-qualified targets are still refused with the same warning-and-basename-fallback
  behavior -- see the current refusal rules on the new output layout page, linked at the end of
  this section.

  .. code-block:: text

     # v0.7.x -- a path in the target is rejected and truncated to its basename
     $ sphinx-build -b typst source build
     build/guide.typ   <- WARNING: path rejected, written under its basename at the output root

  .. code-block:: text

     # v0.8.0 -- the same target is honoured as-is, relative to the output directory
     $ sphinx-build -b typst source build
     build/manuals/guide.typ   <- written exactly where the target says

- **Breaking:** the collision hard error. A configuration whose target resolves onto a path
  another claimant already owns now aborts the build. With
  ``typst_documents = [("index", "index.typ", "Title", "Author", "typst")]``, the wrapper target
  collides with ``index``'s own content file: this built successfully in v0.7.x and now raises an
  ``ExtensionError``. The check runs before anything is written, so no ``.typ`` file is left on
  disk. Fix it by giving the entry a target that is not any docname's own name. The claimants are
  the reserved ``_template.typ``, every docname's content file, and every entry's wrapper.

  .. code-block:: text

     # v0.7.x -- this configuration builds without error
     $ sphinx-build -b typst source build
     build succeeded

  .. code-block:: text

     # v0.8.0 -- the wrapper target collides with index's own content file
     $ sphinx-build -b typst source build
     ExtensionError: typst: 1 output path collision(s): 'index.typ': the content file
     for docname 'index' and typst_documents entry 0 (docname 'index', target
     'index.typ') both resolve to the same output path 'index.typ'

- A document reached from more than one master now renders in each of those masters' PDFs, at
  that master's own position and heading level, where v0.7.x placed it in only one of them. No
  action is needed -- it is the defect this release fixes.

Two different renames touch ``typst_documents`` targets across these releases, and they are easy
to confuse. v0.7.1 already renamed the DEFAULT-DERIVED target from the root docname to
``<project>.typ`` when ``typst_documents`` is unset -- a change to what the target is *called*.
v0.8.0 changes what the target file *contains* -- a change to the output shape, described above.
If your project saw its output renamed at the 0.7.1 upgrade, it is seeing a different change now.
See :doc:`/user_guide/output_layout` for the full current output-layout contract.

Migrating from 0.7.0 to 0.7.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This patch release carries three breaking configuration changes. Each item below shows the
rewrite: the ``conf.py``/template fragment you have today, and the corrected fragment to replace
it with.

- **Breaking:** the ``typst_authors`` config value is removed. It was pure sugar over the
  ``typst_template_function`` ``params`` route -- Phase 44.2 measured the two routes producing a
  byte-identical ``authors:`` value, differing only in the order of named arguments in the emitted
  call, which is semantically irrelevant in Typst -- and removing it brings the config surface to
  LaTeX parity, matching ``latex_documents``, which has no facility for supplying an author as a
  dictionary. A leftover ``typst_authors`` is now an unregistered ``conf.py`` variable, which
  Sphinx ignores without warning, so author information is lost silently rather than loudly.

  .. code-block:: python

     # Old way -- typst_authors is gone in 0.7.1
     typst_authors = {
         "John Doe": {
             "department": "Computer Science",
             "organization": "MIT",
             "email": "john@mit.edu",
         },
     }

  .. code-block:: python

     # New way -- the same dictionary through typst_template_function's params route
     typst_template_function = {
         "name": "project",
         "params": {
             "authors": (
                 {
                     "name": "John Doe",
                     "department": "Computer Science",
                     "organization": "MIT",
                     "email": "john@mit.edu",
                 },
             ),
             # every other parameter your template needs must also be named here --
             # see the next item.
         }
     }

- **Breaking:** a declared ``typst_template_function`` ``params`` dict is now the **complete**
  parameter set. Previously, auto-derived values (``title``/``authors``/``date``, the
  ``typst_elements`` allowlist merge, and the ``toctree_*`` merge) filled in whatever ``params``
  did not name. A project that declares ``params`` to add one key and relies on the auto-derived
  rest now renders with the template's own defaults (empty title, no author) instead of the
  previous merged result -- write all nine.

  .. code-block:: python

     # Old way -- the auto-derived title/authors/date/toctree_* filled in the rest
     typst_template_function = {
         "name": "project",
         "params": {
             "subtitle": "A Technical Report",
         }
     }

  .. code-block:: python

     # New way -- name every parameter the template needs, including the ones that
     # used to be auto-derived
     typst_template_function = {
         "name": "project",
         "params": {
             "title": "My Document",
             "authors": ({"name": "John Doe"},),
             "date": "2026-08-11",
             "papersize": "a4",
             "fontsize": 11,
             "lang": "en",
             "toctree_maxdepth": 2,
             "toctree_numbered": False,
             "toctree_caption": "Contents",
             "subtitle": "A Technical Report",
         }
     }

- **Breaking:** a custom template must now declare ``lang``. The auto-derived ``lang`` reaches
  every non-``typst_package`` template route -- an explicit ``typst_template`` and a
  ``<srcdir>/base.typ`` shadow now both receive it, same as the bundled default. A custom template
  that does not declare a ``lang`` parameter now fails the compile with
  ``unexpected argument: lang``.

  .. code-block:: typst

     // Old way -- no lang parameter, now fails with "unexpected argument: lang"
     #let project(
       title: "",
       authors: (),
       date: none,
       toctree_maxdepth: 2,
       toctree_numbered: false,
       toctree_caption: "Contents",
       papersize: "a4",
       fontsize: 11pt,
       body
     ) = {
       // ...
     }

  .. code-block:: typst

     // New way -- declare lang with a default, matching the shipped custom_template.typ
     #let project(
       title: "",
       authors: (),
       date: none,
       toctree_maxdepth: 2,
       toctree_numbered: false,
       toctree_caption: "Contents",
       papersize: "a4",
       fontsize: 11pt,
       lang: "en",
       body
     ) = {
       // ...
     }

Migrating from 0.6.x to 0.7.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No breaking config changes. Autodoc/API reference output changes visually: monospace
signatures, hanging-indented description bodies, and depth-indexed member nesting replace the
flat proportional-bold text used before — every ``.typ`` file and compiled PDF containing API
documentation looks different on your next build.

- Citations (``.. [Label]`` / ``[Label]_``) now compile. Previously a document containing a
  citation failed the Typst compile outright; citations now render as hanging-indent reference
  entries with working links and back-references.
- Admonition bucket changes are visual only: ``seealso`` now uses the ``hint``/``tip`` styling
  and ``attention`` uses the red family instead of the orange warning bucket.

Migrating from 0.5.x to 0.6.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several breaking config removals landed across this range, alongside a large set of
rendering-fidelity fixes that need no action.

- **Breaking:** a ``typst_elements`` key outside ``papersize``/``fontsize``/``lang`` now fails the
  build instead of being silently dropped. Remove the unsupported key, or pass it through a
  custom template's ``typst_template_function.params`` instead.
- **Breaking:** the inert ``typst_toctree_defaults`` config value was removed. Delete it from
  your ``conf.py`` if present — it never affected any build's output.
- **Breaking:** ``typst_output_dir`` and ``typst_author_params`` config values were removed.
  Neither ever affected output; delete them if present.
- ``sphinx-build -b typstpdf`` now names the output PDF after your configured
  ``typst_documents`` target rather than the source docname — e.g. ``mydoc.pdf`` instead of
  ``index.pdf``. Update any CI or release step that hardcodes the old filename.
- No action needed for the rendering-fidelity fixes across this range (pixel-unit figure/image
  widths, footnotes, glossaries, wide tables, and numerous spacing/separation fixes) — content
  that previously dropped silently or clipped now simply renders correctly.

Migrating from 0.2.x to 0.3.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No breaking changes. Documentation site is a new feature.

Migrating from 0.1.x to 0.2.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Breaking Changes**

None. Version 0.2.0 is backward compatible with 0.1.x.

**New Features**

- Use ``typstpdf`` builder for direct PDF generation:

  .. code-block:: bash

     # Old way (still works)
     sphinx-build -b typst source/ build/typst
     # Since 0.8.0, the file to compile is the wrapper -- for project = "My Project"
     # (typst_documents unset), that wrapper is myproject.typ.
     typst compile build/typst/myproject.typ output.pdf

     # New way (recommended)
     sphinx-build -b typstpdf source/ build/pdf

- Configure templates with dict format:

  .. code-block:: python

     # Old way (still works)
     typst_template_function = "project"

     # New way (more flexible)
     typst_template_function = {
         "name": "ieee",
         "params": {
             "abstract": "...",
             "index-terms": ["AI", "ML"],
         }
     }

Deprecation Policy
------------------

We follow semantic versioning:

- **Major versions** (x.0.0): May include breaking changes
- **Minor versions** (0.x.0): New features, backward compatible
- **Patch versions** (0.0.x): Bug fixes, backward compatible

Deprecated features are:

1. Announced in the release notes
2. Kept for at least one minor version
3. Removed in the next major version

Upcoming Features
-----------------

See our `GitHub Issues <https://github.com/YuSabo90002/typsphinx/issues>`_
for planned features.

Versioning
----------

typsphinx uses semantic versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backward compatible
- **PATCH**: Bug fixes, backward compatible

Release Process
---------------

The released version lives in ``pyproject.toml``'s ``[project].version``. A release runs through
``.github/workflows/release.yml``, triggered by pushing a matching ``vX.Y.Z`` tag:

1. Update ``pyproject.toml``'s version and add a curated ``## [X.Y.Z]`` section to
   ``CHANGELOG.md``, then push the ``vX.Y.Z`` tag (or trigger the workflow manually with the tag
   as input).
2. The ``validate`` job checks the tag against ``pyproject.toml``'s version and aborts on a
   mismatch, aborts if ``CHANGELOG.md`` has no matching non-empty ``## [X.Y.Z]`` section, then
   runs the test suite and linters.
3. The ``build`` job produces the wheel and sdist.
4. The ``publish-pypi`` job runs behind the protected ``pypi`` GitHub environment and requires a
   manual approval before it uploads the package to PyPI.
5. The ``create-release`` job extracts that same ``## [X.Y.Z]`` CHANGELOG section and publishes
   it as the body of a GitHub Release, with the built wheel and sdist attached.

See Also
--------

- `GitHub Releases <https://github.com/YuSabo90002/typsphinx/releases>`_
- `PyPI Release History <https://pypi.org/project/typsphinx/#history>`_
- :doc:`contributing` for development guidelines
