"""
Phase 53 plan 08, Task 1: closes `53-REVIEW.md` WR-01 and the corresponding
⚠ WARNING row in `53-VERIFICATION.md`'s Anti-Patterns table for
`typsphinx/template_registry.py`. `declared = getattr(config,
"typst_document_templates", None) or {}` is followed immediately by
`declared.keys()`; Sphinx's `[dict]` config type only *warns* on a mismatch,
so a TRUTHY non-`dict` value -- a `list` is the plausible
copy-paste-from-`typst_documents` typo -- reaches that line and crashes with
a raw `AttributeError`, dumping an internal Sphinx traceback instead of this
module's `ExtensionError` contract. The pre-fix RED transcript (both the
unit-level `AttributeError` and the falsy-control `[]` resolving cleanly) is
recorded in
`.planning/phases/53-template-registry-foundation/53-08-RED-EVIDENCE.md`.

Mirrors `tests/test_registry_prewrite_validation_gate.py`'s two-class,
subprocess-plus-unit layout, carrying its OWN copy of `_run_sphinx_build()`
and `_typ_files()` rather than importing the sibling module's -- this
suite's convention is one copy per gate module.

Every assertion below is on a string typsphinx itself emits. Sphinx's own
config-type warning for a `[dict]`-declared value that receives a `list` is
gettext-translated and appears in the developer's own locale (see
`53-REVIEW.md` WR-01's transcript, which shows it in Japanese) -- asserting
on it would pass locally and fail on a differently-localized machine, a
defect class this project has already been bitten by. Both this module and
`tests/test_template_registry.py`'s new Task 2 tests are proven green under
`LC_ALL=C` and the ambient locale (see the RED-evidence artifact's post-fix
section).
"""

import subprocess
import sys
from pathlib import Path

import pytest
from sphinx.errors import ExtensionError

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONTAINER_SHAPE_FIXTURE_DIR = FIXTURES_DIR / "registry_container_shape_gate"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str = "typst"
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
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


def _typ_files(build_dir: Path) -> list:
    """Sorted list of every ``.typ`` file under ``build_dir``, or an empty
    list when the directory does not exist. Returns the LIST, not a bool,
    so a failure message can name the survivors."""
    if not build_dir.exists():
        return []
    return sorted(build_dir.rglob("*.typ"))


class TestTruthyNonDictContainerSubprocessGate:
    """WR-01, end to end: a typo'd `typst_document_templates` container
    value travels from `conf.py` through a real `sphinx-build` to this
    module's own `ExtensionError`, with zero `.typ` files written."""

    def test_truthy_non_dict_container_build_fails_with_extension_error_not_attributeerror(
        self, tmp_path
    ):
        """Pre-fix RED (53-08-RED-EVIDENCE.md): the combined output
        contains `AttributeError` and `has no attribute 'keys'`. Post-fix:
        it contains `typst_document_templates must be a dict` and no
        `AttributeError`."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(CONTAINER_SHAPE_FIXTURE_DIR, build_dir)

        assert result.returncode != 0, (
            f"Expected the build to fail on a truthy non-dict container:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert "typst_document_templates must be a dict" in combined_output, (
            f"Expected this module's own container-shape message:\n{combined_output}"
        )
        assert "AttributeError" not in combined_output, (
            f"Expected no raw AttributeError to escape:\n{combined_output}"
        )

    def test_truthy_non_dict_container_build_writes_no_typ_files(self, tmp_path):
        """CONF-17 concurrency edge, explicit half: `resolve_template_registry()`
        is called from `write()` before `prepare_writing()`, so the
        container guard inherits the same zero-output property
        `_validate_registry_key_references()` gave CONF-14."""
        build_dir = tmp_path / "build"
        _run_sphinx_build(CONTAINER_SHAPE_FIXTURE_DIR, build_dir)

        survivors = _typ_files(build_dir)
        assert survivors == [], (
            f"Expected NO .typ file written when the container is a truthy "
            f"non-dict, found: {survivors}"
        )


class TestTruthyNonDictContainerUnitGate:
    """In-process unit half: `resolve_template_registry()` directly, plus
    the falsy-container controls and the well-formed no-op control."""

    def test_truthy_non_dict_container_unit_raises_extension_error(
        self, temp_sphinx_app
    ):
        """Test C: `resolve_template_registry()` over
        `typst_document_templates = ["a", "b"]` raises `ExtensionError`
        whose message contains `must be a dict` and the `repr` of the
        offending value; no `AttributeError` escapes."""
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        app.config.typst_document_templates = ["a", "b"]

        with pytest.raises(ExtensionError) as excinfo:
            resolve_template_registry(app.config, str(app.srcdir))

        message = str(excinfo.value)
        assert "must be a dict" in message
        assert repr(["a", "b"]) in message

    @pytest.mark.parametrize(
        "falsy_container",
        [
            pytest.param({}, id="empty_dict"),
            pytest.param([], id="empty_list"),
            pytest.param(None, id="none"),
            pytest.param("", id="empty_string"),
            pytest.param(0, id="zero"),
        ],
    )
    def test_falsy_container_values_resolve_to_only_the_typst_key(
        self, temp_sphinx_app, falsy_container
    ):
        """Test D: every FALSY `typst_document_templates` value still
        resolves to a registry containing exactly the built-in `"typst"`
        key and raises nothing -- only a TRUTHY non-`dict` raises."""
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        app.config.typst_document_templates = falsy_container

        registry = resolve_template_registry(app.config, str(app.srcdir))

        assert sorted(registry.keys()) == ["typst"]

    def test_well_formed_container_still_resolves_unchanged(self, temp_sphinx_app):
        """Test E: a well-formed one-key registry still resolves and
        yields both the declared key and `typst`, proving the guard is a
        no-op for an ordinary config."""
        from typsphinx.template_registry import resolve_template_registry

        app = temp_sphinx_app
        app.config.typst_document_templates = {
            "good": {"package": "@preview/example:0.1.0"}
        }

        registry = resolve_template_registry(app.config, str(app.srcdir))

        assert sorted(registry.keys()) == ["good", "typst"]
