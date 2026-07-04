"""
Typst builder for Sphinx.

This module implements the TypstBuilder class, which is responsible for
building Typst output from Sphinx documentation.
"""

import shutil
from collections.abc import Iterator
from os import path
from typing import Set

from docutils import nodes
from sphinx.builders import Builder
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

from typsphinx.pdf import compile_typst_to_pdf
from typsphinx.writer import TypstWriter

logger = logging.getLogger(__name__)


class TypstBuilder(Builder):
    """
    Builder class for Typst output format.

    This builder converts Sphinx documentation to Typst markup files (.typ),
    which can then be compiled to PDF using the Typst compiler.
    """

    name = "typst"
    format = "typst"
    out_suffix = ".typ"
    allow_parallel = True

    def init(self) -> None:
        """
        Initialize the builder.

        This method is called once at the beginning of the build process.
        """
        # Initialize images dictionary to track images used in documents
        # Key: image URI relative to source directory
        # Value: destination path (empty string for now, compatible with parent class)
        self.images: dict[str, str] = {}

    def get_outdated_docs(self) -> Iterator[str]:
        """
        Return an iterator of document names that need to be rebuilt.

        For now, we rebuild all documents on every build.

        Returns:
            Iterator of document names that are outdated
        """
        for docname in self.env.found_docs:
            yield docname

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        """
        Return the target URI for a document.

        Args:
            docname: Name of the document
            typ: Type of the target (not used for Typst builder)

        Returns:
            Target URI string
        """
        return docname + self.out_suffix

    def prepare_writing(self, docnames: Set[str]) -> None:
        """
        Prepare for writing the documents.

        This method is called before writing begins.
        Writes the template file to the output directory for master documents to import.

        Args:
            docnames: Set of document names to be written
        """
        # Create the writer instance
        self.writer = TypstWriter(self)

        # Write template file for master documents to import
        self._write_template_file()

    def write(
        self,
        build_docnames: Set[str] | None,
        updated_docnames: Set[str],
        method: str = "update",
    ) -> None:
        """
        Override write() to preserve toctree nodes.

        By default, Sphinx's Builder.write() calls env.get_and_resolve_doctree()
        which expands toctree nodes into compact_paragraph with links.
        For Typst, we need the original toctree nodes to generate #include() directives.

        This method uses env.get_doctree() instead to preserve toctree nodes.

        Args:
            build_docnames: Document names to build (None = all)
            updated_docnames: Document names that were updated
            method: Build method ('update' or 'all')
        """
        if build_docnames is None or build_docnames == ["__all__"]:
            # build_all
            build_docnames = self.env.found_docs
        if method == "update":
            # build updated and specified
            docnames = set(build_docnames) | set(updated_docnames)
        else:
            # build all
            docnames = set(build_docnames)

        logger.info("preparing documents... ", nonl=True)
        self.prepare_writing(docnames)
        logger.info("done")

        # Write individual documents
        warnings_count = 0
        for docname in sorted(docnames):
            # Use env.get_doctree() instead of env.get_and_resolve_doctree()
            # to preserve toctree nodes (Requirement 13.2)
            doctree = self.env.get_doctree(docname)
            self.env.apply_post_transforms(doctree, docname)

            # Log progress
            logger.info(f"writing output... [{docname}]", nonl=True)

            # Write the document
            self.write_doc(docname, doctree)

            logger.info(" done")

    def post_process_images(self, doctree: nodes.document) -> None:
        """
        Post-process images in the document tree.

        Collects all image nodes from the document tree and tracks them
        in self.images dictionary for later copying to the output directory.

        Args:
            doctree: Document tree to process
        """
        from docutils.nodes import image

        for node in doctree.findall(image):
            # Get image URI
            imguri = node.get("uri", "")
            if not imguri:
                continue

            # Track this image
            # Store empty string as value to be compatible with parent class type
            if imguri not in self.images:
                self.images[imguri] = ""

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """
        Write a document.

        This method is called for each document that needs to be written.

        Requirement 13.1: 各 reStructuredText ファイルに対応する独立した
        .typ ファイルを生成する

        Requirement 13.12: ソースディレクトリ構造を保持して出力する

        Args:
            docname: Name of the document
            doctree: Document tree to be written
        """
        # Get the output file path
        destination = path.join(self.outdir, docname + self.out_suffix)

        # Ensure the directory for this specific file exists
        # This handles nested paths like "chapter1/section"
        dest_dir = path.dirname(destination)
        ensuredir(dest_dir)

        # Set current docname for template application logic
        self.current_docname = docname

        # Post-process images to track them for copying
        self.post_process_images(doctree)

        # Set the document on the writer
        self.writer.document = doctree

        # Translate the document to Typst markup
        self.writer.translate()

        # Save the output to the file
        with open(destination, "w", encoding="utf-8") as f:
            f.write(self.writer.output)

    def _write_template_file(self) -> None:
        """
        Write the template file to the output directory.

        This writes a separate template.typ file that master documents can import.
        Only writes if a template is configured (not using Typst Universe packages).
        """
        from typsphinx.template_engine import TemplateEngine

        config = self.config

        # Get template configuration
        template_path = getattr(config, "typst_template", None)
        if template_path:
            # Resolve relative path from source directory
            import os

            template_path = os.path.join(self.srcdir, template_path)

        # Skip if using Typst Universe package (no separate template file needed)
        typst_package = getattr(config, "typst_package", None)
        if typst_package:
            return

        # Create template engine
        template_engine = TemplateEngine(
            template_path=template_path,
            search_paths=[self.srcdir],
            parameter_mapping=getattr(config, "typst_template_mapping", None),
            typst_package=typst_package,
            typst_template_function=getattr(config, "typst_template_function", None),
            typst_package_imports=getattr(config, "typst_package_imports", None),
            typst_authors=getattr(config, "typst_authors", None),
            typst_author_params=getattr(config, "typst_author_params", None),
        )

        # Get template content
        template_content = template_engine.get_template_content()

        # Write template file
        template_file_path = path.join(self.outdir, "_template.typ")
        with open(template_file_path, "w", encoding="utf-8") as f:
            f.write(template_content)

        logger.info(f"Template written to {template_file_path}")

    def copy_image_files(self) -> None:
        """
        Copy image files to the output directory.

        Iterates through all tracked images and copies them from the
        source directory to the output directory, preserving relative paths.
        """
        if not self.images:
            return

        logger.info(f"Copying {len(self.images)} image file(s)...")

        for imguri in self.images:
            # Resolve source path
            # Image URIs are relative to source directory
            src = path.join(self.srcdir, imguri)

            # Resolve destination path
            dest = path.join(self.outdir, imguri)

            # Check if source file exists
            if not path.exists(src):
                logger.warning(f"Image file not found: {src}")
                continue

            # Ensure destination directory exists
            dest_dir = path.dirname(dest)
            ensuredir(dest_dir)

            # Copy the file
            try:
                shutil.copy2(src, dest)
                logger.debug(f"Copied image: {imguri}")
            except Exception as e:
                logger.warning(f"Failed to copy image {imguri}: {e}")

    def copy_template_assets(self) -> None:
        """
        Copy template-associated assets to the output directory.

        When using custom Typst templates via typst_template configuration,
        this method copies assets (fonts, images, logos, etc.) referenced by
        the template to the output directory.

        Behavior:
        - If typst_template_assets is configured, copies only specified files/directories
        - If typst_template_assets is None (default), automatically copies entire template directory
        - If typst_template_assets is empty list, disables automatic copying
        - Skips .typ files to avoid duplicating template file (already handled by _write_template_file)

        This follows the same pattern as copy_image_files() from Issue #38.
        """

        # Early return if no custom template is configured
        template_path = getattr(self.config, "typst_template", None)
        if not template_path:
            return  # No custom template

        # Early return if using Typst Universe package (assets handled by Typst compiler)
        typst_package = getattr(self.config, "typst_package", None)
        if typst_package:
            return

        # Get template assets configuration
        template_assets = getattr(self.config, "typst_template_assets", None)

        # Check if explicitly disabled (empty list)
        if template_assets is not None and len(template_assets) == 0:
            logger.debug("Template asset copying disabled (empty list)")
            return

        logger.info("Copying template assets...")

        if template_assets:
            # Option 2: Explicit asset list
            self._copy_explicit_assets(template_assets)
        else:
            # Option 1: Automatic directory copy
            self._copy_template_directory(template_path)

    def _copy_template_directory(self, template_path: str) -> None:
        """
        Copy entire template directory to output (default behavior).

        Automatically copies all files in the template directory,
        excluding .typ files (which are handled separately).

        Args:
            template_path: Path to template file relative to source directory
        """
        import os

        # Get template directory path
        template_dir = path.dirname(template_path)
        if not template_dir:
            # Template is in root directory, no assets to copy
            return

        # Resolve absolute paths
        src_dir = path.join(self.srcdir, template_dir)
        dest_dir = path.join(self.outdir, template_dir)

        # Check if template directory exists
        if not path.exists(src_dir):
            logger.warning(f"Template directory not found: {src_dir}")
            return

        # Track copied files for logging
        copied_count = 0

        # Walk through directory and copy all files except .typ
        for root, _dirs, files in os.walk(src_dir):
            for file in files:
                # Skip .typ files (already handled by _write_template_file)
                if file.endswith(".typ"):
                    continue

                # Get source and destination paths
                src_file = path.join(root, file)
                rel_path = path.relpath(src_file, src_dir)
                dest_file = path.join(dest_dir, rel_path)

                # Ensure destination directory exists
                ensuredir(path.dirname(dest_file))

                # Copy the file
                try:
                    shutil.copy2(src_file, dest_file)
                    logger.debug(f"Copied template asset: {rel_path}")
                    copied_count += 1
                except Exception as e:
                    logger.warning(f"Failed to copy template asset {rel_path}: {e}")

        if copied_count > 0:
            logger.info(f"Copied {copied_count} template asset(s) from {template_dir}/")

    def _copy_explicit_assets(self, assets: list) -> None:
        """
        Copy explicitly specified assets.

        Supports individual files, directories, and glob patterns.

        Args:
            assets: List of asset paths (relative to source directory)
                   May include glob patterns like "*.png" or "fonts/*.otf"
        """
        import glob

        copied_count = 0

        for asset_pattern in assets:
            # Resolve absolute pattern path
            abs_pattern = path.join(self.srcdir, asset_pattern)

            # Check if pattern contains wildcards
            if "*" in asset_pattern or "?" in asset_pattern:
                # Expand glob pattern
                matches = glob.glob(abs_pattern, recursive=True)
                if not matches:
                    logger.warning(f"No files matched pattern: {asset_pattern}")
                    continue

                for match in matches:
                    if self._copy_single_asset(match, asset_pattern):
                        copied_count += 1
            else:
                # Single file or directory
                if self._copy_single_asset(abs_pattern, asset_pattern):
                    copied_count += 1

        if copied_count > 0:
            logger.info(f"Copied {copied_count} explicitly specified template asset(s)")

    def _copy_single_asset(self, src_path: str, original_pattern: str) -> bool:
        """
        Copy a single asset file or directory.

        Args:
            src_path: Absolute source path
            original_pattern: Original pattern from configuration (for error messages)

        Returns:
            True if successfully copied, False otherwise
        """

        # Check if source exists
        if not path.exists(src_path):
            logger.warning(f"Template asset not found: {original_pattern}")
            return False

        # Calculate relative path from source directory
        rel_path = path.relpath(src_path, self.srcdir)
        dest_path = path.join(self.outdir, rel_path)

        try:
            if path.isdir(src_path):
                # Copy directory recursively
                # Use copytree with dirs_exist_ok for Python 3.8+
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                logger.debug(f"Copied template asset directory: {rel_path}/")
            else:
                # Copy single file
                ensuredir(path.dirname(dest_path))
                shutil.copy2(src_path, dest_path)
                logger.debug(f"Copied template asset: {rel_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to copy template asset {rel_path}: {e}")
            return False

    def finish(self) -> None:
        """
        Finish the build process.

        This method is called once after all documents have been written.
        Copies image files and template assets to the output directory.
        """
        self.copy_image_files()
        self.copy_template_assets()


class TypstPDFBuilder(TypstBuilder):
    """
    Builder class for generating PDF output directly from Typst.

    This builder extends TypstBuilder to compile generated .typ files
    to PDF using the typst-py package.

    Requirement 9.3: TypstPDFBuilder extends TypstBuilder
    Requirement 9.4: Generate PDF from Typst markup
    """

    name = "typstpdf"
    format = "pdf"
    out_suffix = ".pdf"

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """
        Write a document as both .typ and .pdf.

        Override to generate .typ file (not .pdf) during the write phase.
        The .pdf will be generated in finish() by compiling the .typ file.

        Args:
            docname: Name of the document
            doctree: Document tree to be written
        """
        # Generate .typ file (not .pdf)
        typ_destination = path.join(self.outdir, docname + ".typ")

        # Ensure the directory exists
        dest_dir = path.dirname(typ_destination)
        ensuredir(dest_dir)

        # Set current docname for template application logic
        self.current_docname = docname

        # Set the document on the writer
        self.writer.document = doctree

        # Translate the document to Typst markup
        self.writer.translate()

        # Save the .typ file
        with open(typ_destination, "w", encoding="utf-8") as f:
            f.write(self.writer.output)

    def finish(self) -> None:
        """
        Finish the build process by compiling Typst files to PDF.

        After the parent TypstBuilder has generated .typ files,
        this method compiles them to PDF using typst-py.

        Only master documents (defined in typst_documents) are compiled to PDF.
        Included documents are not compiled individually.

        Requirement 9.2: Execute Typst compilation within Python
        Requirement 9.4: Generate PDF from Typst markup
        """
        # First, call parent finish() to copy image files
        # This ensures images are available before PDF compilation
        super().finish()

        # Get master documents from typst_documents config
        typst_documents = getattr(self.config, "typst_documents", [])

        if not typst_documents:
            logger.warning(
                "No documents defined in typst_documents. Nothing to compile."
            )
            return

        logger.info(f"Compiling {len(typst_documents)} master document(s) to PDF...")

        for doc_tuple in typst_documents:
            # doc_tuple format: (sourcename, targetname, title, author)
            docname = doc_tuple[0]
            typ_file = path.join(self.outdir, docname + ".typ")

            if not path.exists(typ_file):
                logger.warning(f"Master document not found: {typ_file}")
                continue

            try:
                # Read Typst content
                with open(typ_file, encoding="utf-8") as f:
                    typst_content = f.read()

                # Compile to PDF
                pdf_bytes = compile_typst_to_pdf(typst_content, root_dir=self.outdir)

                # Write PDF file
                pdf_file = path.join(self.outdir, docname + ".pdf")
                with open(pdf_file, "wb") as f:
                    f.write(pdf_bytes)

                logger.info(f"Generated PDF: {pdf_file}")

            except Exception as e:
                logger.error(f"Failed to compile {typ_file}: {e}")
