"""
Detection for removed ``typst_*`` configuration values.

Sphinx has no built-in mechanism for announcing that a `conf.py` sets a
configuration name the extension no longer registers: ``add_config_value()``
only ever adds names, and there is no reverse "this name used to be
registered" lookup. A `conf.py` that still sets one of these three values
therefore builds successfully today, with zero diagnostic, while doing
something materially different than it did before -- silently.

Two of the three names below (``typst_authors``, removed at v0.7.1;
``typst_toctree_defaults``, removed at v0.6.3) have already been
unregistered for two milestones, so a sentinel-default re-registration
(``app.add_config_value("typst_authors", None, ...)`` purely so Sphinx would
raise on an unknown name) cannot see either of them -- Sphinx only validates
names it currently owns. And re-registering ``typst_template_assets`` as an
inert sentinel, solely to make detection easier, would contradict this
project's own rule against leaving inert configuration registered (see
PROJECT.md). The only mechanism that reaches all three names through one
path is reading the raw, pre-lookup `conf.py` namespace directly.

This module exists to be that one path.
"""

from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

logger = logging.getLogger(__name__)

# D-09: each value gets its own bespoke message -- not one template with a
# substituted replacement -- because the replacement relationship is
# asymmetric and one value has no replacement at all.
REMOVED_CONFIG_VALUES: dict[str, str] = {
    "typst_template_assets": (
        "'typst_template_assets' was removed in v0.9.0 and is now ignored. "
        "Every used template's bundle directory (the resolved template "
        "file's parent) is copied wholesale to the output tree, so MORE "
        "files now reach the output than the explicit list used to select "
        "-- no asset list is needed any more."
    ),
    "typst_authors": (
        "'typst_authors' was removed in v0.7.1 and is now ignored. Rich "
        "author structure (department, organization, location, email) is "
        "expressed through 'typst_template_function's 'params' route "
        "instead, so author department, organization, and email do not "
        "reach the output unless supplied that way."
    ),
    "typst_toctree_defaults": (
        "'typst_toctree_defaults' was removed in v0.6.3 and has no "
        "replacement. It was registered but never read even when it "
        "existed, so deleting it changes no build output."
    ),
}


def check_config_at_init(app: Sphinx, config: Config) -> None:
    """
    Warn, by name, about any removed configuration value still present in
    the raw `conf.py` namespace.

    D-06: reads ``config._raw_config`` -- the pre-lookup `conf.py`
    namespace -- defensively via ``getattr(..., {})``, so a future Sphinx
    dropping this private attribute degrades to no-detection at runtime
    rather than raising. The loud failure for that disappearance is a
    test's job (``tests/test_removed_config_deprecation_gate.py``), not a
    runtime crash here.

    A-03: presence of the name in the raw namespace is the trigger,
    regardless of the value assigned to it -- a `conf.py` setting a removed
    value to ``None`` or an empty list still means the author wrote the
    line and still holds a wrong belief about what it does.

    D-07/D-08: severity is a bare ``logger.warning`` call carrying no
    keyword arguments at all -- the build continues, matching every other
    warning this extension emits (none of them is individually
    suppressible via ``suppress_warnings``, and this one does not become
    the exception). A user running ``sphinx-build -W`` gets a hard failure
    for free.

    D-10: this handler is connected to the ``config-inited`` event, which
    fires for every builder -- including ``-b html`` -- because
    ``app.builder`` does not exist yet at this point in the build
    lifecycle and the handler cannot narrow itself to the Typst builders.
    This is recorded behaviour, not a defect.
    """
    raw: dict[str, Any] = getattr(config, "_raw_config", {})
    for name, message in REMOVED_CONFIG_VALUES.items():
        if name in raw:
            logger.warning(message)
