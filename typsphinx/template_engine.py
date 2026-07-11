"""
Template engine for Typst document generation.

This module implements template loading, parameter mapping, and rendering
for Typst documents (Requirement 8).
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Manages Typst templates for document generation.

    Responsibilities:
    - Load default or custom Typst templates
    - Search templates in multiple directories with priority
    - Provide fallback to default template when custom template not found
    - Map Sphinx metadata to template parameters
    - Render final Typst document with template and content

    Requirement 8.1: Default Typst template included in package
    Requirement 8.2: Support custom template specification
    Requirement 8.7: Priority search in user project directory
    Requirement 8.9: Fallback to default template with warning
    """

    # Standard mapping from Sphinx metadata to template parameters
    # Requirement 8.3: Sphinx metadata passed to template
    # Requirement 8.5: Standard metadata name transformation
    DEFAULT_PARAMETER_MAPPING = {
        "project": "title",
        "author": "authors",
        "release": "date",
    }

    def __init__(
        self,
        template_path: str | None = None,
        template_name: str | None = None,
        search_paths: List[str] | None = None,
        parameter_mapping: Dict[str, str] | None = None,
        typst_package: str | None = None,
        typst_template_function: Any | None = None,
        typst_package_imports: List[str] | None = None,
        typst_authors: Dict[str, Dict[str, Any]] | None = None,
        typst_author_params: Dict[str, Dict[str, Any]] | None = None,
    ):
        """
        Initialize TemplateEngine.

        Args:
            template_path: Absolute path to template file (highest priority)
            template_name: Template filename to search in search_paths
            search_paths: List of directories to search for templates (priority order)
            parameter_mapping: Custom mapping from Sphinx metadata to template parameters
                             (Requirement 8.4: different parameter names)
            typst_package: Typst Universe package specification (e.g., "@preview/charged-ieee:0.1.0")
                          (Requirement 8.6: external template packages)
            typst_template_function: Template function name (str) or dict with {"name": str, "params": dict}
            typst_package_imports: Specific items to import from package
            typst_authors: Author details as dict with author name as key (recommended)
            typst_author_params: Legacy author params (for backward compatibility)
        """
        self.template_path = template_path
        self.template_name = template_name or "base.typ"
        self.search_paths = search_paths or []
        self.parameter_mapping = (
            parameter_mapping or self.DEFAULT_PARAMETER_MAPPING.copy()
        )
        self.typst_package = typst_package
        self.typst_package_imports = typst_package_imports or []
        self.typst_authors = typst_authors or {}
        self.typst_author_params = typst_author_params or {}

        # Parse typst_template_function: support both string and dict formats
        if isinstance(typst_template_function, dict):
            self.typst_template_function_name = typst_template_function.get(
                "name", "project"
            )
            self.typst_template_params = typst_template_function.get("params", {})
        elif isinstance(typst_template_function, str):
            self.typst_template_function_name = typst_template_function
            self.typst_template_params = {}
        else:
            self.typst_template_function_name = None
            self.typst_template_params = {}

    def get_default_template_path(self) -> str:
        """
        Get the path to the default template bundled with the package.

        Returns:
            Absolute path to default template file
        """
        # Template is located in sphinxcontrib/typst/templates/base.typ
        package_dir = Path(__file__).parent
        template_dir = package_dir / "templates"
        default_template = template_dir / "base.typ"

        return str(default_template)

    def load_template(self) -> str:
        """
        Load Typst template with priority order:
        1. Explicit template_path if provided
        2. Search for template_name in search_paths (first match wins)
        3. Default template bundled with package

        Returns:
            Template content as string

        Requirement 8.1: Load default template
        Requirement 8.2: Load custom template
        Requirement 8.7: Search in user project directory
        Requirement 8.9: Fallback to default with warning
        """
        template_content = None

        # Priority 1: Explicit template path
        if self.template_path:
            template_content = self._try_load_file(self.template_path)
            if template_content is None:
                logger.warning(
                    f"Custom template not found: {self.template_path}. "
                    f"Falling back to default template."
                )

        # Priority 2: Search in search_paths
        if template_content is None and self.search_paths:
            for search_dir in self.search_paths:
                candidate_path = Path(search_dir) / self.template_name
                template_content = self._try_load_file(str(candidate_path))
                if template_content is not None:
                    logger.debug(f"Loaded template from: {candidate_path}")
                    break

        # Priority 3: Default template
        if template_content is None:
            default_path = self.get_default_template_path()
            template_content = self._try_load_file(default_path)

            if template_content is None:
                # This should never happen if package is properly installed
                raise FileNotFoundError(
                    f"Default template not found at: {default_path}. "
                    f"Package installation may be corrupted."
                )

        return template_content

    def map_parameters(self, sphinx_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Sphinx metadata to template parameters.

        Args:
            sphinx_metadata: Dictionary of Sphinx configuration metadata
                           (project, author, release, etc.)

        Returns:
            Dictionary of template parameters ready to pass to template

        Requirement 8.3: Pass Sphinx metadata to template
        Requirement 8.4: Support different parameter names
        Requirement 8.5: Standard metadata name transformation
        Requirement 8.8: Convert to arrays and complex structures
        """
        params = {}

        # Apply mapping
        for sphinx_key, template_key in self.parameter_mapping.items():
            if sphinx_key in sphinx_metadata:
                value = sphinx_metadata[sphinx_key]

                # Special handling for authors (both standard "authors" and custom names)
                if sphinx_key == "author" or template_key in ("authors", "doc_authors"):
                    value = self._convert_to_authors_tuple(value)

                params[template_key] = value

        # Provide default values for missing required parameters
        if "title" not in params:
            params["title"] = ""
        if "authors" not in params:
            params["authors"] = ()
        if "date" not in params:
            params["date"] = None

        return params

    def generate_package_import(self) -> str:
        """
        Generate Typst package import statement.

        Returns:
            Import statement string, or empty string if no package specified

        Requirement 8.6: Typst Universe external template packages
        """
        if not self.typst_package:
            return ""

        # Generate import statement
        if self.typst_package_imports:
            # Import specific items: #import "@package:version": item1, item2
            items = ", ".join(self.typst_package_imports)
            return f'#import "{self.typst_package}": {items}'
        elif self.typst_template_function_name:
            # Import template function: #import "@package:version": template_func
            return (
                f'#import "{self.typst_package}": {self.typst_template_function_name}'
            )
        else:
            # Import entire module: #import "@package:version"
            return f'#import "{self.typst_package}"'

    def extract_toctree_options(self, doctree: Any) -> Dict[str, Any]:
        """
        Extract toctree options from doctree for template parameters.

        Args:
            doctree: Docutils document tree

        Returns:
            Dictionary of toctree options for template

        Requirement 8.12: toctree options passed as template parameters
        Requirement 8.13: template reflects toctree options in #outline()
        Requirement 13.8: #outline() managed at template level
        Requirement 13.9: toctree options mapped to template parameters
        """
        from sphinx import addnodes

        # Try to find toctree node in doctree
        toctree_nodes = list(doctree.findall(addnodes.toctree))

        if not toctree_nodes:
            # No toctree found - return empty dict
            return {}

        # Use first toctree node found
        toctree = toctree_nodes[0]

        # Extract options with defaults
        # Note: Sphinx toctree numbered can be False, True, or int
        # Convert to bool for Typst (0 means False, positive means True)
        numbered_value = toctree.get("numbered", False)
        if isinstance(numbered_value, int):
            numbered_value = numbered_value > 0

        # Note: Sphinx toctree maxdepth can be -1 (unlimited)
        # Typst outline() requires positive depth or none
        # Convert -1 to none for unlimited depth
        maxdepth_value = toctree.get("maxdepth", 2)
        if maxdepth_value == -1:
            maxdepth_value = None

        return {
            "toctree_maxdepth": maxdepth_value,
            "toctree_numbered": numbered_value,
            "toctree_caption": toctree.get("caption", ""),
        }

    def get_template_content(self) -> str:
        """
        Get the template content for writing to a separate file.

        Returns:
            Template content as string

        This is used when templates are written as separate files
        instead of being inlined in the main document.
        """
        template = self.load_template()
        return template

    def render(
        self, params: Dict[str, Any], body: str, template_file: str = None
    ) -> str:
        """
        Render final Typst document with template and body.

        Args:
            params: Template parameters (title, authors, etc.)
            body: Document body content (Typst markup)
            template_file: Path to template file for import (relative to output dir).
                          If None, template is inlined (old behavior).
                          If specified, template is imported from file.

        Returns:
            Complete Typst document string

        Requirement 8.2: Use custom template
        Requirement 8.10: Pass document settings to template
        Requirement 8.14: #outline() in template, not body
        """
        # Build output parts
        output_parts = []

        # Add package import if using Typst Universe package
        package_import = self.generate_package_import()
        if package_import:
            output_parts.append(package_import)
            output_parts.append("")  # Blank line

        if template_file:
            # Import essential packages (needed for content, not just template)
            output_parts.append("// Essential package imports")
            output_parts.append('#import "@preview/codly:1.3.0": *')
            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
            output_parts.append("")  # Blank line

            # Import template from separate file
            template_func = self.typst_template_function_name or "project"
            output_parts.append(f'#import "{template_file}": {template_func}')
            output_parts.append("")  # Blank line
        else:
            # Load template inline (old behavior)
            # For external packages, we skip loading the template
            if not self.typst_package:
                template = self.load_template()
                output_parts.append(template)
                output_parts.append("")  # Blank line

        # Generate #show statement with template function call
        template_func = self.typst_template_function_name or "project"
        output_parts.append(f"#show: {template_func}.with(")

        # Merge template-specific params with standard params
        all_params = {}
        all_params.update(self.typst_template_params)  # Template-specific params first
        all_params.update(params)  # Standard params (can override if needed)

        # Format parameters
        for key, value in all_params.items():
            formatted_value = self._format_typst_value(value)
            output_parts.append(f"  {key}: {formatted_value},")

        output_parts.append(")")
        output_parts.append("")  # Blank line

        # Add body content
        output_parts.append(body)

        return "\n".join(output_parts)

    def _format_typst_value(self, value: Any) -> str:
        """
        Format Python value as Typst value.

        Args:
            value: Python value (str, int, bool, tuple, etc.)

        Returns:
            Typst-formatted value string
        """
        if value is None:
            return "none"
        elif isinstance(value, bool):
            # Typst uses lowercase true/false
            return "true" if value else "false"
        elif isinstance(value, str):
            # Escape quotes and backslashes
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            # Format as Typst array/tuple
            formatted_items = [self._format_typst_value(item) for item in value]
            return f'({", ".join(formatted_items)},)' if formatted_items else "()"
        elif isinstance(value, dict):
            # Format as Typst dictionary (not commonly used in templates)
            items = [f"{k}: {self._format_typst_value(v)}" for k, v in value.items()]
            return f'({", ".join(items)})'
        else:
            # Default: convert to string and quote
            return f'"{str(value)}"'

    def _convert_to_authors_tuple(self, author_value: Any) -> tuple:
        """
        Convert author metadata to tuple of authors.

        Args:
            author_value: Author metadata (string or list)

        Returns:
            Tuple of author names

        Requirement 8.8: Convert to arrays and complex structures
        """
        if isinstance(author_value, (list, tuple)):
            return tuple(author_value)
        elif isinstance(author_value, str):
            # Split comma-separated authors
            authors = [a.strip() for a in author_value.split(",")]
            return tuple(authors)
        else:
            return (str(author_value),)

    def _try_load_file(self, file_path: str) -> str | None:
        """
        Try to load content from file.

        Args:
            file_path: Path to file

        Returns:
            File content as string, or None if file doesn't exist or can't be read
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, OSError):
            return None

    def _format_authors_with_details(self, authors: tuple | None = None) -> str:
        """
        Format authors with detailed information as Typst dict tuple.

        Args:
            authors: Optional tuple of author names (for backward compatibility with typst_author_params)

        Returns:
            Typst-formatted author dict tuple string

        Priority:
        1. typst_authors (recommended) - author name as key, details as dict value
        2. typst_author_params (legacy) - requires authors parameter
        """
        author_dicts = []

        # Use typst_authors if available (recommended approach)
        if self.typst_authors:
            for author_name, details in self.typst_authors.items():
                author_dict = {"name": author_name}
                author_dict.update(details)
                author_dicts.append(author_dict)
        # Fall back to typst_author_params (legacy support)
        elif self.typst_author_params and authors:
            for author_name in authors:
                author_dict = {"name": author_name}
                if author_name in self.typst_author_params:
                    author_dict.update(self.typst_author_params[author_name])
                author_dicts.append(author_dict)
        else:
            # No detailed author information available
            return ""

        # Format as Typst dict tuple
        result_parts = ["("]
        for author_dict in author_dicts:
            result_parts.append("  (")
            for key, value in author_dict.items():
                formatted_value = self._format_typst_value(value)
                result_parts.append(f"    {key}: {formatted_value},")
            result_parts.append("  ),")
        result_parts.append(")")

        return "\n".join(result_parts)
