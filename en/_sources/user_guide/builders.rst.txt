Builders
========

typsphinx provides two builders for different use cases.

Overview
--------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Builder
     - Output
     - Use Case
   * - ``typst``
     - ``.typ`` files
     - Edit Typst markup manually, use external Typst CLI
   * - ``typstpdf``
     - ``.pdf`` files
     - Direct PDF generation, CI/CD pipelines

typst Builder
-------------

The ``typst`` builder generates Typst markup files (``.typ``).

Usage
~~~~~

.. code-block:: bash

   sphinx-build -b typst source/ build/typst

Output
~~~~~~

- Generates ``.typ`` files in the output directory
- One file per document defined in ``typst_documents``
- Include files for multi-document projects

When to Use
~~~~~~~~~~~

- You want to edit the generated Typst markup
- You have a specific Typst CLI version
- You need fine control over compilation
- You want to learn Typst syntax

Manual Compilation
~~~~~~~~~~~~~~~~~~

After generating ``.typ`` files, compile with Typst CLI:

.. code-block:: bash

   # Install Typst CLI if needed
   # https://github.com/typst/typst

   # Compile to PDF
   typst compile build/typst/index.typ output.pdf

typstpdf Builder
----------------

The ``typstpdf`` builder generates PDF files directly using typst-py.

Usage
~~~~~

.. code-block:: bash

   sphinx-build -b typstpdf source/ build/pdf

Output
~~~~~~

- Generates ``.pdf`` files directly
- No external tools required
- Uses typst-py Python bindings

When to Use
~~~~~~~~~~~

- You want PDF output immediately
- You're running in CI/CD without Typst CLI
- You want self-contained builds
- You don't need to edit Typst markup

Advantages
~~~~~~~~~~

- **No external dependencies**: Everything runs in Python
- **Faster setup**: No need to install Typst CLI
- **Reproducible builds**: Same output across environments
- **CI/CD friendly**: Works in restricted environments

Configuration
-------------

Both builders share the same configuration options in ``conf.py``.

Document Definitions
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   typst_documents = [
       # (source, output, title, author, class)
       ("index", "main", "My Document", "Author", "typst"),
       ("api", "api-ref", "API Reference", "Author", "typst"),
   ]

The second tuple element is the output filename stem, and it governs both
the emitted ``.typ`` file and the compiled ``.pdf`` (under the ``typstpdf``
builder). With the configuration shown above, the builders therefore emit
``main.typ`` / ``main.pdf`` and ``api-ref.typ`` / ``api-ref.pdf`` -- not
``index.typ`` / ``index.pdf`` or ``api.typ`` / ``api.pdf``. The CLI
walkthroughs elsewhere on this page assume the default identity
configuration, where the source name and the target name agree, so their
docname-named artifacts are correct for that configuration.

Builder-Specific Options
~~~~~~~~~~~~~~~~~~~~~~~~

There are no builder-specific options currently. All ``typst_*`` configuration
options apply to both builders.

Choosing a Builder
------------------

Use ``typst`` if:

- You want to customize the generated Typst code
- You need specific Typst CLI features
- You're learning Typst and want to see the markup

Use ``typstpdf`` if:

- You just want PDF output
- You're building in CI/CD
- You want the simplest workflow
- You don't need to edit Typst code

Common Workflow
---------------

Development
~~~~~~~~~~~

During development, use ``typstpdf`` for quick feedback:

.. code-block:: bash

   sphinx-build -b typstpdf source/ build/pdf
   open build/pdf/index.pdf

Production
~~~~~~~~~~

For production, you can use either builder:

.. code-block:: bash

   # Option 1: Direct PDF (recommended)
   sphinx-build -b typstpdf source/ build/pdf

   # Option 2: Typst + manual compilation
   sphinx-build -b typst source/ build/typst
   typst compile build/typst/index.typ output.pdf

CI/CD
~~~~~

In CI/CD, ``typstpdf`` is recommended for simplicity:

.. code-block:: yaml

   - name: Build Documentation PDF
     run: |
       pip install typsphinx
       sphinx-build -b typstpdf docs/source docs/build/pdf

See Also
--------

- :doc:`configuration` - Configuration options
- :doc:`templates` - Customizing templates
- :doc:`/examples/basic` - Basic usage examples
