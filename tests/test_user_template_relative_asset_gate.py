"""
GATE-01 OUT-05 real-compile regression gate (Phase 54): proves a
USER-supplied template's own relative asset reference (``#image("logo.png",
...)``) survives the per-key bundle relocation this phase introduces.

ROADMAP constraint #7 measured that all three real templates already in
this repository (the bundled default ``typsphinx/templates/base.typ``,
``docs/source/_typst/custom_template.typ``, and
``tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ``) carry
font-family references only -- none of them proves a path-RELATIVE
reference survives relocation. SC#3 explicitly rejects the built-in
template as evidence for this gate, so this module's fixture
(``tests/fixtures/user_template_relative_asset_gate/``) is a genuinely new
real ``sphinx-build -b typstpdf`` -> ``typst.compile()`` proof, recorded
RED against the pre-relocation tree in ``54-01-RED-EVIDENCE.md``.

Scaffolding (subprocess-based ``sys.executable -m sphinx``,
``TYPST_AVAILABLE`` guard, class-scoped ``build`` fixture) is modelled on
``tests/test_typst_lang_gate.py``'s ``TestJapaneseSourceProof`` /
``TestGermanLinkageProof`` classes.

Made green by ``54-04`` (OUT-05): the per-key bundle relocation now copies
the user template's own directory wholesale to
``<outdir>/_template/<key>/``, so its same-directory ``logo.png`` sits
beside it, and the wrapper imports the template by its root-absolute
``/_template/<key>/<file>.typ`` path. RED recorded in
``54-01-RED-EVIDENCE.md``.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "user_template_relative_asset_gate"
FIXTURE_TEMPLATE_PATH = FIXTURE_DIR / "_typst" / "branded.typ"

# DOC-16 (Phase 56): paths for TestPublishedAssetGuidanceMatchesTheFixture,
# below. Same REPO_ROOT / DOCS_SOURCE_DIR derivation convention as
# tests/test_docs_contract_claims_gate.py.
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"
TEMPLATES_RST_PATH = DOCS_SOURCE_DIR / "user_guide" / "templates.rst"
ADVANCED_RST_PATH = DOCS_SOURCE_DIR / "examples" / "advanced.rst"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard -- copied near-verbatim from
    ``tests/test_typst_lang_gate.py::_run_sphinx_build``.
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


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the OUT-05 real-compile gate",
)
# Made green for real by 54-04 (OUT-05) -- the marker 54-01 recorded
# this module's RED under has been removed.
class TestUserTemplateRelativeAssetGate:
    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        # This fixture body performs no verification of its own -- every
        # test method below carries its own verification instead.
        build_dir = tmp_path_factory.mktemp("user_template_relative_asset_gate_build")
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typstpdf")
        wrapper_path = build_dir / "master.typ"
        wrapper_text = (
            wrapper_path.read_text(encoding="utf-8") if wrapper_path.exists() else ""
        )
        pdf_path = build_dir / "master.pdf"
        return {
            "result": result,
            "build_dir": build_dir,
            "wrapper_path": wrapper_path,
            "wrapper_text": wrapper_text,
            "pdf_path": pdf_path,
        }

    def test_build_succeeds(self, build):
        result = build["result"]
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_pdf_is_valid(self, build):
        pdf_path = build["pdf_path"]
        result = build["result"]
        assert pdf_path.exists(), (
            f"PDF was not produced at {pdf_path}:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        pdf_bytes = pdf_path.read_bytes()
        assert len(pdf_bytes) > 0, "PDF is empty"
        assert pdf_bytes[:4] == b"%PDF", f"Not a valid PDF: {pdf_bytes[:16]!r}"

    def test_asset_reached_the_bundle_destination(self, build):
        build_dir = build["build_dir"]
        assert (build_dir / "_template" / "typst" / "logo.png").exists(), (
            "logo.png did not reach the bundle destination "
            "<outdir>/_template/typst/logo.png"
        )
        assert (build_dir / "_template" / "typst" / "branded.typ").exists(), (
            "branded.typ did not reach the bundle destination "
            "<outdir>/_template/typst/branded.typ"
        )
        assert (build_dir / "_template" / "typst" / "refs.bib").exists(), (
            "refs.bib did not reach the bundle destination "
            "<outdir>/_template/typst/refs.bib"
        )

    def test_wrapper_imports_the_bundled_template(self, build):
        wrapper_text = build["wrapper_text"]
        assert "/_template/typst/branded.typ" in wrapper_text, (
            "wrapper does not import the bundled template at the expected "
            f"root-absolute path:\n{wrapper_text}"
        )


def _extract_bare_bibliography_reference(template_text: str) -> str:
    """Extract the quoted filename argument of the fixture template's
    ``#bibliography(...)`` call, e.g. ``#bibliography("refs.bib")`` ->
    ``"refs.bib"``.

    Deriving this from the fixture itself, rather than hardcoding
    ``"refs.bib"``, means correcting the fixture's reference form without
    correcting the published pages fails HERE instead of silently
    diverging (DOC-16's design note, 56-04-PLAN.md Task 3).
    """
    match = re.search(r'#bibliography\("([^"]+)"', template_text)
    assert match, (
        'could not find a #bibliography("...") call in the fixture '
        f"template to derive the reference form from:\n{template_text}"
    )
    return match.group(1)


def _subpath_form(bare_form: str) -> str:
    """The source-tree-shaped subpath form a page must NOT publish, e.g.
    ``refs.bib`` -> ``_typst/refs.bib``."""
    return f"_typst/{bare_form}"


def _page_names_bare_reference(page_text: str, bare_form: str) -> bool:
    return bare_form in page_text


def _page_names_subpath_reference(page_text: str, bare_form: str) -> bool:
    return _subpath_form(bare_form) in page_text


def _asset_section_restricts_to_custom_templates(templates_page_text: str) -> bool:
    return "only applies to custom local templates" in templates_page_text


def _asset_section_names_built_in_key_covered(templates_page_text: str) -> bool:
    return (
        "built-in" in templates_page_text
        and '"typst"' in templates_page_text
        and "same rule" in templates_page_text
    )


def _asset_section_states_per_key_directory_rule(templates_page_text: str) -> bool:
    return "its own directory named after that key" in templates_page_text


def _asset_section_states_empty_bundle_rule(templates_page_text: str) -> bool:
    return "copies just the template file itself" in templates_page_text


class TestPublishedAssetGuidanceMatchesTheFixture:
    """DOC-16 (Phase 56): binds ``templates.rst`` and ``advanced.rst`` to
    the reference form ``tests/fixtures/user_template_relative_asset_gate/``
    actually proves by real compile (``TestUserTemplateRelativeAssetGate``
    above).

    Deliberately defined OUTSIDE the ``TYPST_AVAILABLE`` skipif scope: this
    class reads text only and performs no compile, so it must never skip --
    the same never-skipping design ``tests/test_docs_contract_claims_gate.py``
    chose, for the same reason (a ``typst-py`` import guard tests
    importability, not compile capability, and would let this binding
    silently vanish in a sandbox without typst-py installed).
    """

    @staticmethod
    def _fixture_bare_reference_form() -> str:
        template_text = FIXTURE_TEMPLATE_PATH.read_text(encoding="utf-8")
        return _extract_bare_bibliography_reference(template_text)

    def test_advanced_rst_publishes_the_bare_reference_form(self):
        bare_form = self._fixture_bare_reference_form()
        advanced_text = ADVANCED_RST_PATH.read_text(encoding="utf-8")
        assert _page_names_bare_reference(advanced_text, bare_form), (
            "advanced.rst does not name the bare-filename reference form "
            f"{bare_form!r} the fixture proves by real compile"
        )

    def test_neither_page_publishes_the_subpath_form(self):
        bare_form = self._fixture_bare_reference_form()
        advanced_text = ADVANCED_RST_PATH.read_text(encoding="utf-8")
        templates_text = TEMPLATES_RST_PATH.read_text(encoding="utf-8")
        assert not _page_names_subpath_reference(advanced_text, bare_form), (
            "advanced.rst still publishes the source-tree-shaped subpath "
            f"form {_subpath_form(bare_form)!r}, which the bundle layout "
            "does not resolve"
        )
        assert not _page_names_subpath_reference(templates_text, bare_form), (
            "templates.rst still publishes the source-tree-shaped subpath "
            f"form {_subpath_form(bare_form)!r}, which the bundle layout "
            "does not resolve"
        )

    def test_templates_rst_does_not_restrict_bundle_copying_to_custom_templates(
        self,
    ):
        templates_text = TEMPLATES_RST_PATH.read_text(encoding="utf-8")
        assert not _asset_section_restricts_to_custom_templates(templates_text), (
            "templates.rst still restricts bundle copying to custom local "
            "templates, understating OUT-04's no-exceptions rule"
        )

    def test_templates_rst_names_the_built_in_key_as_covered_by_the_same_rule(
        self,
    ):
        templates_text = TEMPLATES_RST_PATH.read_text(encoding="utf-8")
        assert _asset_section_names_built_in_key_covered(templates_text), (
            'templates.rst does not state that the built-in "typst" key is '
            "copied by the same no-exceptions bundle rule as any custom key"
        )

    def test_templates_rst_states_the_per_key_directory_rule(self):
        templates_text = TEMPLATES_RST_PATH.read_text(encoding="utf-8")
        assert _asset_section_states_per_key_directory_rule(templates_text), (
            "templates.rst does not state that each used key's bundle is "
            "copied into its own directory named after that key"
        )

    def test_templates_rst_states_the_empty_bundle_rule(self):
        templates_text = TEMPLATES_RST_PATH.read_text(encoding="utf-8")
        assert _asset_section_states_empty_bundle_rule(templates_text), (
            "templates.rst does not state that a template with no other "
            "files beside it copies just the template file itself"
        )

    def test_teeth_subpath_detector_fires_on_a_synthetic_bad_page(self):
        bare_form = self._fixture_bare_reference_form()
        synthetic_bad_page = (
            f'Reference the copied asset as ``"_typst/{bare_form}"``, '
            "matching where the copy lands, not the bare filename."
        )
        assert _page_names_subpath_reference(synthetic_bad_page, bare_form), (
            "the subpath detector did not fire on a synthetic page known "
            "to carry the subpath form -- its pattern is wrong"
        )

    def test_teeth_restriction_detector_fires_on_a_synthetic_bad_page(self):
        synthetic_bad_page = (
            "Bundle copying only applies to custom local templates "
            "(``typst_template``)."
        )
        assert _asset_section_restricts_to_custom_templates(synthetic_bad_page), (
            "the restriction-phrase detector did not fire on a synthetic "
            "page known to carry the restricting phrase -- its pattern is "
            "wrong"
        )
