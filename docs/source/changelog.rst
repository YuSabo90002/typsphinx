.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_

Migration Guides
----------------

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
     typst compile build/typst/index.typ output.pdf

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
