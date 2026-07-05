"""
Tests for entry points configuration.
"""

from importlib.metadata import entry_points


def test_entry_point_registration():
    """Test that entry points are defined in pyproject.toml."""
    # Get entry points for sphinx.builders group
    eps = entry_points(group="sphinx.builders")

    # Convert to list of names
    ep_names = [ep.name for ep in eps]

    # Check that both 'typst' and 'typstpdf' entry points exist
    assert (
        "typst" in ep_names
    ), f"'typst' entry point not found in sphinx.builders. Found: {ep_names}"
    assert (
        "typstpdf" in ep_names
    ), f"'typstpdf' entry point not found in sphinx.builders. Found: {ep_names}"


def test_entry_point_value():
    """Test that the entry points point to the correct module."""
    # Get entry points for sphinx.builders group
    eps = entry_points(group="sphinx.builders")

    # Find the entry points
    typst_ep = None
    typstpdf_ep = None
    for ep in eps:
        if ep.name == "typst":
            typst_ep = ep
        elif ep.name == "typstpdf":
            typstpdf_ep = ep

    # Check typst entry point
    assert typst_ep is not None, "'typst' entry point not found"
    assert (
        typst_ep.value == "typsphinx"
    ), f"Entry point value should be 'typsphinx', got '{typst_ep.value}'"

    # Check typstpdf entry point
    assert typstpdf_ep is not None, "'typstpdf' entry point not found"
    assert (
        typstpdf_ep.value == "typsphinx"
    ), f"Entry point value should be 'typsphinx', got '{typstpdf_ep.value}'"
