Contributing
============

Thank you for your interest in contributing to typsphinx!

This guide will help you get started with development.

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.9 or later
- uv (recommended) or pip
- Git

Clone and Install
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/YuSabo90002/typsphinx.git
   cd typsphinx

   # Install with development dependencies
   uv sync --extra dev

   # Or with pip
   pip install -e ".[dev]"

Running Tests
-------------

We use pytest for testing:

.. code-block:: bash

   # Run all tests
   uv run pytest

   # Run with coverage
   uv run pytest --cov

   # Run specific test file
   uv run pytest tests/test_builder.py

   # Run with verbose output
   uv run pytest -v

Test Coverage
~~~~~~~~~~~~~

We maintain 90%+ test coverage. When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Check coverage doesn't decrease

Code Quality
------------

We use multiple tools to ensure code quality:

Black (Code Formatting)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Format all code
   uv run black .

   # Check without modifying
   uv run black --check .

Ruff (Linting)
~~~~~~~~~~~~~~

.. code-block:: bash

   # Lint all code
   uv run ruff check .

   # Auto-fix issues
   uv run ruff check --fix .

Mypy (Type Checking)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Type check
   uv run mypy typsphinx/

All Checks
~~~~~~~~~~

Run all quality checks:

.. code-block:: bash

   uv run black .
   uv run ruff check .
   uv run mypy typsphinx/
   uv run pytest --cov

Using Tox
~~~~~~~~~

We use tox for running tests across multiple Python versions and environments.
Tox provides the same commands used in CI, making it easy to reproduce issues locally:

.. code-block:: bash

   # Run all tox environments (tests, lint, type check, docs)
   uv run tox

   # Run specific environments
   uv run tox -e lint          # Black + Ruff
   uv run tox -e type          # Mypy type checking
   uv run tox -e py311         # Tests on Python 3.11
   uv run tox -e docs-html     # Build HTML documentation
   uv run tox -e docs-pdf      # Build PDF documentation
   uv run tox -e docs          # Build both HTML and PDF

   # Run tests on specific Python versions
   uv run tox -e py39,py310,py311,py312

The tox configuration is defined in ``tox.ini`` and provides:

- Consistent test execution across local and CI environments
- Isolated virtual environments for each test run
- Same commands work locally and in GitHub Actions

Development Workflow
--------------------

1. Create a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git checkout -b feature/your-feature-name

2. Make Changes
~~~~~~~~~~~~~~~

- Write code following the project style
- Add tests for new functionality
- Update documentation as needed

3. Run Tests and Checks
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv run pytest --cov
   uv run black .
   uv run ruff check .
   uv run mypy typsphinx/

4. Commit Changes
~~~~~~~~~~~~~~~~~

Use conventional commit messages:

.. code-block:: bash

   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in translator"
   git commit -m "docs: update configuration guide"

Commit types:

- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation changes
- ``style``: Code style changes (formatting)
- ``refactor``: Code refactoring
- ``test``: Adding tests
- ``chore``: Maintenance tasks

5. Push and Create Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git push origin feature/your-feature-name

Then create a pull request on GitHub.

Coding Guidelines
-----------------

Style
~~~~~

- Follow PEP 8 (enforced by Black and Ruff)
- Line length: 88 characters (Black default)
- Use type hints for public APIs
- Write docstrings for public functions/classes

Documentation
~~~~~~~~~~~~~

Use Google-style docstrings:

.. code-block:: python

   def convert_node(node: nodes.Node) -> str:
       """Convert a docutils node to Typst markup.

       Args:
           node: The docutils node to convert

       Returns:
           Typst markup string

       Raises:
           ValueError: If node type is unsupported

       Example:
           >>> node = nodes.paragraph()
           >>> convert_node(node)
           '#par[...]'
       """
       pass

Architecture
~~~~~~~~~~~~

- **Builder**: Manages build process, file I/O
- **Writer**: Orchestrates document conversion
- **Translator**: Converts individual node types (Visitor pattern)
- **TemplateEngine**: Handles template processing

Testing
~~~~~~~

- Write unit tests for individual functions
- Write integration tests for complete builds
- Use fixtures for test data
- Test edge cases and error conditions

Project Structure
-----------------

.. code-block:: text

   typsphinx/
   ├── typsphinx/              # Main package
   │   ├── __init__.py         # Extension entry point
   │   ├── builder.py          # TypstBuilder
   │   ├── pdf.py              # TypstPDFBuilder
   │   ├── writer.py           # TypstWriter
   │   ├── translator.py       # TypstTranslator
   │   ├── template_engine.py  # Template processing
   │   └── templates/          # Default templates
   ├── tests/                  # Test suite
   ├── docs/                   # Documentation
   ├── examples/               # Example projects
   └── pyproject.toml          # Project configuration

Reporting Issues
----------------

When reporting bugs:

1. Check if the issue already exists
2. Provide a minimal reproducible example
3. Include your environment details:

   - Python version
   - Sphinx version
   - typsphinx version
   - Operating system

4. Describe expected vs actual behavior

Use our issue templates on GitHub.

Feature Requests
----------------

For feature requests:

1. Describe the use case
2. Explain why it's needed
3. Suggest implementation approach (optional)
4. Consider creating an OpenSpec proposal for major features

Translations
------------

Japanese translation catalogs are maintained in a separate repository.
The repository, ``typsphinx-doc-translations``, consumes this repository as a git
submodule and is built by a Read the Docs translation project served at
https://typsphinx.readthedocs.io/ja/latest/.

To work on the translation:

.. code-block:: bash

   # Clone the translations repository
   git clone --recurse-submodules https://github.com/YuSabo90002/typsphinx-doc-translations.git
   cd typsphinx-doc-translations

   # Refresh the catalogs against the current English source
   make locale-update

   # Edit the .po files under locale/ja/LC_MESSAGES/, then check coverage
   make locale-stat

If you already cloned without ``--recurse-submodules``, run
``git submodule update --init`` before ``make locale-update``.

Open a pull request in the translations repository with your changes.

Coverage is partial by design: untranslated strings fall back to English, so a
partial translation is a working site rather than a broken one.

Community
---------

- **GitHub**: https://github.com/YuSabo90002/typsphinx
- **Issues**: https://github.com/YuSabo90002/typsphinx/issues
- **Discussions**: Use GitHub Discussions for questions

Code of Conduct
---------------

We follow the Contributor Covenant Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect differing viewpoints

License
-------

By contributing, you agree that your contributions will be licensed
under the MIT License.

Thank you for contributing to typsphinx!
