.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_

Migration Guides
----------------

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

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.md``
3. Create git tag: ``v0.x.x``
4. Push to GitHub
5. GitHub Actions builds and publishes to PyPI
6. GitHub Release created with changelog

See Also
--------

- `GitHub Releases <https://github.com/YuSabo90002/typsphinx/releases>`_
- `PyPI Release History <https://pypi.org/project/typsphinx/#history>`_
- :doc:`contributing` for development guidelines
