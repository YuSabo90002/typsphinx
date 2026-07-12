"""
Minimal importable class hierarchy for the GATE-01 inheritance-diagram
fixture (``tests/fixtures/graphviz_degrade_render_gate/index.rst``).

Kept deliberately tiny and self-contained -- the fixture must resolve the
``.. inheritance-diagram::`` directive without importing anything from
typsphinx itself.
"""


class BaseWidget:
    """A minimal base class for the inheritance-diagram fixture."""


class DerivedWidget(BaseWidget):
    """A minimal derived class for the inheritance-diagram fixture."""
