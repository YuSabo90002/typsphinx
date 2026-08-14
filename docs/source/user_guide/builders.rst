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
- Each ``typst_documents`` entry writes a **wrapper** file at that entry's
  own target path, plus a **content** file named after the entry's source
  document
- Every document in the project gets a content file, whether or not it is
  named in ``typst_documents``
- See :doc:`output_layout` for the full wrapper/content contract and which
  file to compile

When to Use
~~~~~~~~~~~

- You want to edit the generated Typst markup
- You have a specific Typst CLI version
- You need fine control over compilation
- You want to learn Typst syntax

Manual Compilation
~~~~~~~~~~~~~~~~~~

After generating ``.typ`` files, compile with Typst CLI. Compile the
**wrapper**, not the docname-named content file -- see :doc:`output_layout`
for the full wrapper/content contract.

.. code-block:: bash

   # Install Typst CLI if needed
   # https://github.com/typst/typst

   # Compile to PDF -- with typst_documents unset, project = "My Project"
   # produces the wrapper myproject.typ
   typst compile build/typst/myproject.typ output.pdf

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

The second tuple element names the **wrapper** file for that entry, and
only the wrapper -- it does not govern the entry's content file. With the
configuration shown above, the builders emit four ``.typ`` files: wrappers
``main.typ`` and ``api-ref.typ``, plus content files ``index.typ`` and
``api.typ``, named after the two source documents shown above. Under the
``typstpdf`` builder only the wrappers become PDFs: ``main.pdf`` and
``api-ref.pdf``, and no others. See :doc:`output_layout` for the full
wrapper/content contract.

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
   # With typst_documents unset, project = "My Project" produces the
   # wrapper's PDF as myproject.pdf
   open build/pdf/myproject.pdf

Production
~~~~~~~~~~

For production, you can use either builder:

.. code-block:: bash

   # Option 1: Direct PDF (recommended)
   sphinx-build -b typstpdf source/ build/pdf

   # Option 2: Typst + manual compilation
   sphinx-build -b typst source/ build/typst
   # With typst_documents unset, project = "My Project" produces the
   # wrapper myproject.typ
   typst compile build/typst/myproject.typ output.pdf

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

- :doc:`output_layout` - The wrapper/content output contract
- :doc:`configuration` - Configuration options
- :doc:`templates` - Customizing templates
- :doc:`/examples/basic` - Basic usage examples
