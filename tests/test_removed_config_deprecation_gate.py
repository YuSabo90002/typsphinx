"""
Phase 54 plan 06 (CONF-19): the removed-config detection gate.

This module exercises ``typsphinx/removed_config.py``'s ``config-inited``
handler through real ``sphinx-build`` subprocess builds (the
``_run_sphinx_build`` helper is copied near-verbatim per this repository's
own per-module convention, established by ``test_typst_lang_gate.py`` and
``test_collision_predicate_completeness_gate.py``) -- one per removed
value, the A-03 boundary case (a removed value explicitly set to ``None``
still warns), the negative case (a clean ``conf.py`` warns about nothing),
and a loud-failure test asserting the private Sphinx attribute the
detection mechanism depends on (``Config._raw_config``) still exists.

D-10, recorded here rather than left implicit: ``config-inited`` fires for
EVERY builder, not just the Typst ones, because ``app.builder`` does not
exist yet at this point in Sphinx's build lifecycle -- so this repository's
own ``docs/source/conf.py`` build (``-b html``) would emit these warnings
too, if it ever set one of these three names (it does not).
"""

import subprocess
import sys
from pathlib import Path

import pytest

REMOVED_NAMES = ["typst_template_assets", "typst_authors", "typst_toctree_defaults"]

# D-09's required content, one bespoke phrase per value -- deliberately NOT
# a single shared template, matching removed_config.py's own design.
REQUIRED_PHRASES = {
    "typst_template_assets": ["typst_template_assets", "copied wholesale", "MORE"],
    "typst_authors": [
        "typst_authors",
        "typst_template_function",
        "department, organization, and email",
    ],
    "typst_toctree_defaults": ["typst_toctree_defaults", "no replacement"],
}

MINIMAL_CONF_HEADER = (
    'project = "Test"\n'
    'author = "Test Author"\n'
    'release = "1.0.0"\n'
    'copyright = "2026, Test Author"\n'
    'extensions = ["typsphinx"]\n'
    'typst_documents = [("index", "manual.typ", "Test", "Test Author")]\n'
)

MINIMAL_INDEX_RST = "Test\n====\n\nContent.\n"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str = "typst"
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard -- copied near-verbatim from this repository's
    other gate modules (each carries its own copy rather than importing a
    sibling module's).
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _write_project(tmp_path: Path, name: str, conf_body: str) -> Path:
    """Write a minimal Sphinx source directory and return its path."""
    src_dir = tmp_path / name
    src_dir.mkdir()
    (src_dir / "conf.py").write_text(MINIMAL_CONF_HEADER + conf_body, encoding="utf-8")
    (src_dir / "index.rst").write_text(MINIMAL_INDEX_RST, encoding="utf-8")
    return src_dir


class TestEachRemovedValueWarnsByName:
    """
    One test per removed value: a ``conf.py`` setting it produces a
    warning containing the value's own name, its replacement (or, for
    ``typst_toctree_defaults``, an explicit statement that there is none),
    and the observable-consequence phrase from D-09's message.
    """

    @pytest.mark.parametrize("name", REMOVED_NAMES)
    def test_removed_value_warns_with_required_content(self, tmp_path, name):
        conf_body = f"{name} = ['some_value']\n"
        src_dir = _write_project(tmp_path, f"proj_{name}", conf_body)
        build_dir = tmp_path / f"build_{name}"

        result = _run_sphinx_build(src_dir, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"A removed config value must warn, not fail, the build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        for phrase in REQUIRED_PHRASES[name]:
            assert phrase in combined_output, (
                f"Expected the warning for {name!r} to contain {phrase!r}:\n"
                f"{combined_output}"
            )


class TestA03NoneValueStillWarns:
    """
    The A-03 flagged-assumption boundary: a ``conf.py`` setting a removed
    value to ``None`` (or an empty list) still warns, because the author
    wrote the line and still holds a wrong belief about what it does --
    presence in the raw namespace is the trigger, not the assigned value.
    """

    def test_none_value_still_warns(self, tmp_path):
        conf_body = "typst_template_assets = None\n"
        src_dir = _write_project(tmp_path, "proj_none_value", conf_body)
        build_dir = tmp_path / "build_none_value"

        result = _run_sphinx_build(src_dir, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert "typst_template_assets" in combined_output, (
            f"Expected a warning even though the value is None -- presence "
            f"in the raw conf.py namespace is the trigger, not the "
            f"assigned value (A-03):\n{combined_output}"
        )

    def test_empty_list_value_still_warns(self, tmp_path):
        conf_body = "typst_authors = []\n"
        src_dir = _write_project(tmp_path, "proj_empty_list_value", conf_body)
        build_dir = tmp_path / "build_empty_list_value"

        result = _run_sphinx_build(src_dir, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert "typst_authors" in combined_output, (
            f"Expected a warning even though the value is an empty list -- "
            f"presence in the raw conf.py namespace is the trigger, not "
            f"the assigned value (A-03):\n{combined_output}"
        )


class TestCleanConfigEmitsNoWarnings:
    """
    Without this negative case, every other test in this module would pass
    against a handler that warns unconditionally regardless of what the
    conf.py actually sets.
    """

    def test_clean_conf_emits_none_of_the_three_warnings(self, tmp_path):
        src_dir = _write_project(tmp_path, "proj_clean", "")
        build_dir = tmp_path / "build_clean"

        result = _run_sphinx_build(src_dir, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"A clean conf.py must build successfully:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        for name in REMOVED_NAMES:
            assert name not in combined_output, (
                f"A conf.py that never sets {name!r} must not trigger its "
                f"warning:\n{combined_output}"
            )


class TestDetectionMechanismFailsLoudlyIfItDisappears:
    """
    D-06's loud-failure requirement: ``check_config_at_init()`` reads
    ``config._raw_config`` defensively via ``getattr(..., {})`` at
    runtime, so a future Sphinx dropping the attribute degrades to
    no-detection rather than crashing a user's build. That graceful
    runtime degradation must be paired with a test that does NOT degrade
    gracefully -- if the attribute the mechanism depends on ever
    disappears, THIS test must fail loudly and point at the module to
    repair, rather than the feature silently going quiet forever.
    """

    def test_raw_config_attribute_still_exists_on_sphinx_config(self):
        from sphinx.config import Config

        config = Config()
        assert hasattr(config, "_raw_config"), (
            "sphinx.config.Config no longer exposes '_raw_config' on a "
            "constructed instance -- the removed-config detection "
            "mechanism in typsphinx/removed_config.py has SILENTLY GONE "
            "QUIET as a result, since check_config_at_init() reads this "
            "attribute defensively (via getattr(..., {})) and therefore "
            "raises nothing at runtime when it disappears. Repair "
            "typsphinx/removed_config.py: find a new way to read the raw, "
            "pre-lookup conf.py namespace before you trust this gate's "
            "other tests again."
        )


class TestRemovedValueGenuinelyUnregistered:
    """
    A future accidental re-registration of ``typst_template_assets`` (for
    example, as an inert sentinel to make detection "easier") would
    contradict this project's own rule against leaving inert configuration
    registered. This test catches that regression directly.
    """

    def test_typst_template_assets_absent_from_config_registry(self, temp_sphinx_app):
        assert "typst_template_assets" not in temp_sphinx_app.config.values, (
            "typst_template_assets must stay genuinely UNREGISTERED -- "
            "re-registering it (even as an inert sentinel) would "
            "contradict this project's standing rule against leaving "
            "inert configuration registered."
        )


class TestNoWarningSubtype:
    """
    D-08: every warning this extension emits is a bare ``logger.warning``
    call with no keyword arguments -- tagging only this one would make it
    the extension's sole individually-suppressible warning. Enforced at
    the source level so the uniformity decision cannot silently drift.
    """

    def test_removed_config_module_carries_no_warning_keyword_arguments(self):
        import inspect

        import typsphinx.removed_config as removed_config

        src = inspect.getsource(removed_config)
        assert "subtype" not in src, (
            "typsphinx/removed_config.py must not tag its warning with a "
            "subtype -- see D-08."
        )
        assert "type=" not in src, (
            "typsphinx/removed_config.py must not pass a keyword argument "
            "to logger.warning() -- see D-08."
        )
