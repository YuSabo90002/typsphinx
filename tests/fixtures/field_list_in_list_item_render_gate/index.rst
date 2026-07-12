Field List In List Item Render Gate
====================================

This fixture reproduces the corpus fatal where a field list nested inside an
enumerated-list item, following a paragraph, is emitted with no leading
separator -- juxtaposing ``visit_field_name``'s ``strong(`` against the
preceding paragraph's closing ``)`` in the code-mode content block, aborting
the compile with "expected semicolon or line break". Mirrors
``usage/advanced/intl.rst`` lines 245-256 (Sphinx's own corpus).

#. Install the tool.

   You need the command line tool for uploading resources.

#. Create your account and create a new project and an organization
   for your document.

   For example:

   :Organization ID: ``sphinx-document``
   :Project ID: ``sphinx-document-test``
   :Project URL: ``https://example.com/projects/p/sphinx-document-test``

#. Create an API token to be used in the command-line.

   Go to the API token page and generate a token.

Top-level field list
---------------------

A field list at the top level (not nested in a list item) must stay
byte-unchanged by this fix.

:Author: Test Author
:Version: 1.0.0
