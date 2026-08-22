Installation
============

Requirements
------------

- Python 3.12 or later
- Sphinx 9.1 or later (below 10)

Installing from PyPI
--------------------

The easiest way to install typsphinx is using pip:

.. code-block:: bash

   pip install typsphinx

Or using uv (recommended for faster installation):

.. code-block:: bash

   uv pip install typsphinx

Installing from Source
----------------------

If you want to install from the latest source code:

.. code-block:: bash

   git clone https://github.com/YuSabo90002/typsphinx.git
   cd typsphinx
   pip install -e .

Or with uv:

.. code-block:: bash

   git clone https://github.com/YuSabo90002/typsphinx.git
   cd typsphinx
   uv pip install -e .

Development Installation
------------------------

For development with all dependencies:

.. code-block:: bash

   git clone https://github.com/YuSabo90002/typsphinx.git
   cd typsphinx
   uv sync --extra dev

This installs:

- All runtime dependencies
- Testing tools (pytest, pytest-cov)
- Code quality tools (black, ruff, mypy)
- Documentation tools

Verifying Installation
----------------------

To verify that typsphinx is installed correctly:

.. code-block:: bash

   python -c "import typsphinx; print(typsphinx.__version__)"

You should see the version number printed.

Next Steps
----------

Continue to :doc:`quickstart` to learn how to use typsphinx in your Sphinx project.
