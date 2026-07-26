Changelog
=========

All notable changes to typsphinx are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

For the complete changelog, see `CHANGELOG.md <https://github.com/YuSabo90002/typsphinx/blob/main/CHANGELOG.md>`_ in the repository.

Version 0.4.0 (Current)
-----------------------

**Fixed**

- Document wrapper (``#{...}``) preservation in nested structures (#61)
- Nested lists generating invalid Typst syntax (#62)
- Unified code mode syntax compliance

**Changed**

- Implemented stream-based rendering architecture
- Changed ``strong()`` and ``emph()`` to use content blocks: ``strong({...})``, ``emph({...})``
- Updated ``link()`` format from ``link(url)[content]`` to ``link(url, content)``
- List items now use content blocks with newline separators
- API signatures properly formatted with ``+`` operator concatenation

Version 0.3.0
-------------

**Added**

- Documentation site with GitHub Pages deployment
- Comprehensive user guide and examples
- API reference documentation

Version 0.2.2
-------------

**Added**

- Typst Universe template support (#13)
- Dictionary format for ``typst_template_function``
- Detailed author information with ``typst_authors``
- charged-ieee template examples

**Changed**

- Template parameter merging system
- Improved template documentation

Version 0.2.1
-------------

**Fixed**

- Image file copying in builds
- Path handling for multi-document projects

Version 0.2.0
-------------

**Added**

- ``typstpdf`` builder for direct PDF generation
- Self-contained PDF generation with typst-py
- Code highlighting with codly package
- Math rendering with mitex
- Template system with customization support

**Changed**

- Improved Sphinx integration
- Better error messages
- Enhanced type hints

Version 0.1.0
-------------

**Added**

- Initial release
- ``typst`` builder for Typst markup generation
- Basic Sphinx to Typst conversion
- reStructuredText support
- Table of contents generation
- Cross-reference support

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

Development Status
------------------

- **v0.3.x**: Current stable release
- **v0.2.x**: Maintenance mode
- **v0.1.x**: No longer supported

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
