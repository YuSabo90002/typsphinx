"""
WR-01 (Phase 54.1 plan 01): real-``sphinx-build`` subprocess gate proving
that a used ``typst_document_templates`` registry key whose resolved
template bundle directory collides with Sphinx's own ``templates_path``
(D-01) refuses the build with an ``ExtensionError`` instead of copying
that directory into build output.

Detection is a path-relationship test against the LIVE
``self.config.templates_path`` values, resolved against ``self.srcdir``
-- never a name match on the literal string ``_templates`` (D-02). The
refusal happens in a pre-write pass at the top of ``write()``, so a
refused build leaves ZERO ``.typ`` files anywhere under the build
directory (D-04) -- the same "no partial output" property
``tests/test_template_prefix_reservation_gate.py``'s
``test_no_typ_file_written_after_refusal`` already established for
OUT-07's reservation refusal.

Pre-fix RED transcript recorded verbatim in
``.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-01-RED-EVIDENCE.md``
(binding constraint #6) -- both tests below FAIL against the pre-fix
tree, because nothing in ``typsphinx/`` reads ``templates_path`` today.
"""

import re
import subprocess
import sys
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "templates_path_collision_gate"

# Phase 54.1 plan 04: the multi-relation fixture exercising all three of
# D-02's path relations (is / is-contained-by / contains) across three
# registry keys in ONE build, feeding D-03's accumulate-then-raise-once
# aggregation and sorted() ordering guarantee.
MULTI_FIXTURE_DIR = (
    Path(__file__).parent / "fixtures" / "templates_path_collision_multi_gate"
)

# Phase 54.1 plan 04, task 2: the three shapes D-02 says must NEVER
# refuse -- the adjacency false positive a naive prefix test would
# produce, and the two measured non-colliding shapes (D-02 bullets 1
# and 2).
ADJACENT_CONTROL_FIXTURE_DIR = (
    Path(__file__).parent / "fixtures" / "templates_path_adjacent_control_gate"
)
ABSENT_CONTROL_FIXTURE_DIR = (
    Path(__file__).parent / "fixtures" / "templates_path_absent_control_gate"
)
NO_TYPST_TEMPLATE_CONTROL_FIXTURE_DIR = (
    Path(__file__).parent / "fixtures" / "templates_path_no_typst_template_control_gate"
)

# Phase 54.1 plan 04, task 3: D-05's synthesized-entry gate -- an unset
# document-list config value still routes the built-in "typst" key
# through the checked key set via this extension's callable default.
DEFAULT_DOCUMENTS_FIXTURE_DIR = (
    Path(__file__).parent / "fixtures" / "templates_path_default_documents_gate"
)

# D-01: the exact sentence fragment the new ``ExtensionError`` message
# must contain, naming this specific failure kind -- asserted by both
# tests below and reused as the gate's own marker constant so a future
# wording change is caught in exactly one place.
TEMPLATES_PATH_COLLISION_MARKER = "collides with the Sphinx templates_path entry"

# D-03: the aggregate summary prefix ``_validate_used_template_paths()``
# raises with, capturing the failure count as group 1 and the semicolon-
# joined per-key summary as group 2. Failure-kind-neutral by design (this
# same prefix is shared with sibling plans' CONF-17 hoist and reserved-
# key case checks), so this regex matches on the literal text this plan
# owns rather than assuming it is the ONLY failure kind ever reported.
AGGREGATE_PREFIX_RE = re.compile(
    r"typst: (\d+) pre-write template path failure\(s\): (.*)"
)


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
    """The LIST of ``.typ`` files under ``build_dir`` -- returned (not
    just a bool) so a failing assertion can name the survivors."""
    if not build_dir.exists():
        return []
    return sorted(build_dir.rglob("*.typ"))


def test_collision_refuses_build(tmp_path):
    """D-01: a used key's resolved bundle directory that collides with
    ``templates_path`` refuses the build, naming the offending registry
    key, the resolved bundle directory, and the colliding
    ``templates_path`` entry."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected the build to FAIL on a templates_path collision:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert TEMPLATES_PATH_COLLISION_MARKER in combined_output, (
        f"Expected the collision marker {TEMPLATES_PATH_COLLISION_MARKER!r} "
        f"in the build output:\n{combined_output}"
    )
    assert (
        "paper" in combined_output
    ), f"Expected the offending registry key 'paper' named:\n{combined_output}"
    assert "_templates" in combined_output, (
        f"Expected the resolved bundle directory (containing "
        f"'_templates') named:\n{combined_output}"
    )
    assert "_typst" in combined_output, (
        f"Expected the non-colliding remedy directory '_typst' named:\n"
        f"{combined_output}"
    )


def test_no_typ_file_written_after_refusal(tmp_path):
    """D-04: the refusal happens in a pre-write pass at the top of
    ``write()``, so a refused build leaves NO ``.typ`` file anywhere
    under the build directory."""
    build_dir = tmp_path / "build"
    _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    survivors = _typ_files(build_dir)
    assert not survivors, (
        f"Expected NO .typ file written when the templates_path "
        f"collision refuses the build, found: {survivors}"
    )


def _extract_aggregate_message(combined_output: str) -> str:
    """Locate the aggregate ``ExtensionError`` sentence -- the substring
    beginning ``"typst: N pre-write template path failure(s): ..."`` --
    in ``combined_output`` and return it verbatim, so every multi-
    relation assertion below reads one canonical string. Modelled on
    ``tests/test_registry_prewrite_validation_gate.py``'s
    ``_extract_registry_key_message()``, but matches on
    ``AGGREGATE_PREFIX_RE`` (a regex, not a fixed marker substring)
    because the count digit varies per build."""
    match = AGGREGATE_PREFIX_RE.search(combined_output)
    return match.group(0) if match else ""


class TestMultiRelationAggregationGate:
    """D-02/D-03: one build of ``templates_path_collision_multi_gate``
    exercises all three of D-02's path relations (is / is-contained-by /
    contains) across three registry keys (``alpha``/``beta``/``gamma``)
    and refuses with ONE aggregated ``ExtensionError`` naming all three
    keys, in ``sorted()`` order, with a correct failure count -- never a
    first-offender raise."""

    def test_multi_relation_build_refuses(self, tmp_path):
        """All three of D-02's relations (is / is-contained-by /
        contains) refuse the build, not just the equality case plan
        54.1-01's own fixture already pins."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(MULTI_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode != 0, (
            f"Expected the multi-relation fixture to refuse the build:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_multi_relation_aggregate_names_all_three_keys_in_sorted_order(
        self, tmp_path
    ):
        """D-03: multiple colliding keys are named in ONE message, in
        ``sorted()`` key order -- located by INDEX (not merely asserted
        present), so an ordering regression is actually caught."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(MULTI_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr
        message = _extract_aggregate_message(combined_output)
        assert message, (
            f"Expected an aggregate 'typst: N pre-write template path "
            f"failure(s):' sentence in the build output:\n{combined_output}"
        )

        index_alpha = message.find("'alpha'")
        index_beta = message.find("'beta'")
        index_gamma = message.find("'gamma'")
        assert -1 not in (index_alpha, index_beta, index_gamma), (
            f"Expected all three offending keys named in the aggregate "
            f"message:\n{message}"
        )
        assert index_alpha < index_beta < index_gamma, (
            f"Expected 'alpha', 'beta', 'gamma' to appear in that "
            f"sorted() order in the aggregate message, got positions "
            f"{index_alpha}, {index_beta}, {index_gamma}:\n{message}"
        )

    def test_multi_relation_aggregate_failure_count_is_three(self, tmp_path):
        """The aggregate's failure count matches the number of offending
        keys -- read out of the aggregate prefix's captured digit, not
        by counting substrings (three keys could produce more than three
        failures if a key collided with more than one templates_path
        entry; this fixture's keys each collide with exactly one)."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(MULTI_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr
        match = AGGREGATE_PREFIX_RE.search(combined_output)
        assert match, (
            f"Expected an aggregate 'typst: N pre-write template path "
            f"failure(s):' sentence in the build output:\n{combined_output}"
        )
        assert match.group(1) == "3", (
            f"Expected a failure count of 3, got {match.group(1)!r} in:\n"
            f"{combined_output}"
        )

    def test_multi_relation_each_key_names_own_bundle_dir_and_own_entry(self, tmp_path):
        """Each key's own sentence names its own resolved bundle
        directory and its own colliding ``templates_path`` entry -- not
        a shared or first-offender summary. ``alpha`` collides by
        equality against the ``_templates`` entry, ``beta`` by its
        bundle dir being contained by ``_templates``, ``gamma`` by its
        bundle dir containing the ``_typst/inner`` entry."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(MULTI_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr
        message = _extract_aggregate_message(combined_output)
        assert message, (
            f"Expected an aggregate 'typst: N pre-write template path "
            f"failure(s):' sentence in the build output:\n{combined_output}"
        )

        assert "'_templates'" in message, (
            f"Expected alpha/beta's colliding templates_path entry "
            f"'_templates' named:\n{message}"
        )
        assert "_templates/nested" in message, (
            f"Expected beta's resolved bundle directory (containing "
            f"'_templates/nested') named:\n{message}"
        )
        assert "_typst/inner" in message, (
            f"Expected gamma's colliding templates_path entry "
            f"'_typst/inner' named:\n{message}"
        )

    def test_no_typ_file_written_after_multi_relation_refusal(self, tmp_path):
        """D-04, carried into the multi-relation case: the refusal still
        leaves ZERO ``.typ`` files anywhere under the build directory."""
        build_dir = tmp_path / "build"
        _run_sphinx_build(MULTI_FIXTURE_DIR, build_dir, "typst")
        survivors = _typ_files(build_dir)
        assert not survivors, (
            f"Expected NO .typ file written when the multi-relation "
            f"collision refuses the build, found: {survivors}"
        )


class TestNonCollidingShapesControlGate:
    """D-02's three shapes that must NEVER refuse: the adjacency false
    positive a naive ``str.startswith()`` prefix test would produce, and
    the two measured non-colliding shapes (bullet 1: no
    ``templates_path`` set at all; bullet 2: ``templates_path`` set but
    no Typst template configured). Each control asserts BOTH exit code 0
    AND the produced ``.typ`` file set -- an exit-0-only assertion would
    pass for a build that silently produced nothing -- and asserts the
    collision marker is ABSENT from the build output. No RED transcript
    exists for any of these three: they pass both before and after the
    fix by design."""

    def test_adjacent_sibling_directory_does_not_refuse(self, tmp_path):
        """A directory whose name merely shares a prefix with a
        ``templates_path`` entry, but is neither the entry nor under it,
        must NOT be reported as a collision."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(ADJACENT_CONTROL_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"Expected the adjacency control build to succeed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert TEMPLATES_PATH_COLLISION_MARKER not in combined_output, (
            f"Expected NO collision marker in the adjacency control's "
            f"output:\n{combined_output}"
        )
        survivors = sorted(p.name for p in _typ_files(build_dir))
        expected = sorted(["custom.typ", "index.typ", "index_out.typ"])
        assert survivors == expected, f"Expected exactly {expected}, found {survivors}"

    def test_absent_templates_path_does_not_refuse(self, tmp_path):
        """D-02 bullet 1: no Sphinx Jinja override directory is set at
        all, even though the Typst template lives inside a directory
        spelled exactly like that config value's own default -- there is
        nothing to relate the template's directory against."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(ABSENT_CONTROL_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"Expected the absent-templates_path control build to "
            f"succeed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert TEMPLATES_PATH_COLLISION_MARKER not in combined_output, (
            f"Expected NO collision marker in the absent-templates_path "
            f"control's output:\n{combined_output}"
        )
        survivors = sorted(p.name for p in _typ_files(build_dir))
        expected = sorted(["custom.typ", "index.typ", "index_out.typ"])
        assert survivors == expected, f"Expected exactly {expected}, found {survivors}"

    def test_no_typst_template_configured_does_not_refuse(self, tmp_path):
        """D-02 bullet 2: ``templates_path`` is set, but no Typst
        template is configured at all, so the built-in registry key
        falls through to the packaged default -- never subjected to the
        containment test."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            NO_TYPST_TEMPLATE_CONTROL_FIXTURE_DIR, build_dir, "typst"
        )
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"Expected the no-typst-template control build to succeed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert TEMPLATES_PATH_COLLISION_MARKER not in combined_output, (
            f"Expected NO collision marker in the no-typst-template "
            f"control's output:\n{combined_output}"
        )
        survivors = sorted(p.name for p in _typ_files(build_dir))
        expected = sorted(["base.typ", "index.typ", "index_out.typ"])
        assert survivors == expected, f"Expected exactly {expected}, found {survivors}"


def test_default_documents_collision_refuses_build(tmp_path):
    """D-05: an unset document-list config value still routes through
    ``_default_typst_documents()``'s single synthesized entry, whose
    fifth element (the built-in registry key ``"typst"``) is what
    supplies the checked key -- proving the synthesized entry reaches
    the checked key set, not just explicitly-declared entries."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(DEFAULT_DOCUMENTS_FIXTURE_DIR, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected the default-documents fixture to refuse the build:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert TEMPLATES_PATH_COLLISION_MARKER in combined_output, (
        f"Expected the collision marker "
        f"{TEMPLATES_PATH_COLLISION_MARKER!r} in the build output:\n"
        f"{combined_output}"
    )
    assert "'typst'" in combined_output, (
        f"Expected the synthesized built-in registry key 'typst' "
        f"named:\n{combined_output}"
    )


def test_no_typ_file_written_after_default_documents_refusal(tmp_path):
    """D-04, carried into the synthesized-entry case: the refusal still
    leaves ZERO ``.typ`` files anywhere under the build directory."""
    build_dir = tmp_path / "build"
    _run_sphinx_build(DEFAULT_DOCUMENTS_FIXTURE_DIR, build_dir, "typst")
    survivors = _typ_files(build_dir)
    assert not survivors, (
        f"Expected NO .typ file written when the default-documents "
        f"collision refuses the build, found: {survivors}"
    )
