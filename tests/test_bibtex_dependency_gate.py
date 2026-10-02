"""
Tests guarding how sphinxcontrib-bibtex is declared in pyproject.toml (R012, M001/S01).

R012 (constraint) states that bibliography support must activate only when the user
installs and enables `sphinxcontrib-bibtex` themselves, and that users who write no
bibliographies must not carry pybtex and its dependency tree. MEM003 records the
decision that follows from it: **dev extra only** — add `sphinxcontrib-bibtex` to
`[project.optional-dependencies].dev`, keep it out of `[project].dependencies`, and do
not create a `[bibtex]` optional extra. Bibliography users install the package
themselves anyway, since they must list it in `conf.py`'s `extensions`, so a runtime
dependency would only impose pybtex on every typsphinx user for no benefit.

This module asserts the two halves of that declaration:

**The dev extra names it.** Without the declaration the package is not installed by
`uv sync --extra dev`, and every downstream bibliography test in this slice — the ones
that build a Sphinx project carrying `refs.bib`, a `:cite:p:` citation and a
`.. bibliography::` directive — fails at `conf.py` extension load rather than on the
behaviour it means to measure. A missing dev dependency is also invisible on a machine
where the package happens to be installed for some other reason; only CI's clean
provisioning would catch it, and only as a confusing collection-time error.

**The runtime dependency list does not.** This is the clause that actually enforces
R012. Nothing in `typsphinx/` imports `sphinxcontrib.bibtex` (per MEM002, typsphinx
registers no cite roles, no cite domain and no bibliography directives — that
registration stays entirely with sphinxcontrib-bibtex, and typsphinx only renders the
resolved docutils nodes it leaves behind), so the package working correctly in tests
gives no signal at all about whether it leaked into runtime dependencies. The leak
would be silent: the test suite stays green, and the cost lands on end users as an
inflated install. A static manifest gate is the only defense, which is the same
reasoning `test_toolchain_config_gate.py` applies to the toolchain packages.

Implementation notes: stdlib `tomllib` parses the manifest (never a regex over TOML),
and distribution names are compared on their PEP 503 normalized form via
`packaging.utils.canonicalize_name` after `packaging.requirements.Requirement` strips
the version specifier — so this gate keeps holding when the bound `>=2.7,<3` is later
moved, and is not fooled by `-`/`_`/`.` or case variation in the entry. Both tests carry
vacuous-pass guards so a missing or malformed file fails loudly instead of passing
trivially. This module deliberately does **not** import `sphinxcontrib.bibtex`: it reads
the manifest, so it must pass even where the package is not installed, and no
`pytest.skip` is appropriate here.
"""

import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_TOML_PATH = REPO_ROOT / "pyproject.toml"

BIBTEX_DISTRIBUTION = canonicalize_name("sphinxcontrib-bibtex")


def _load_pyproject() -> dict:
    """Parse pyproject.toml via tomllib.

    Guards against a vacuous pass: asserts the file exists (named explicitly
    so a missing file fails loudly) and that the parser successfully reads it,
    so a malformed file cannot silently satisfy later assertions.
    """
    assert (
        PYPROJECT_TOML_PATH.exists()
    ), f"{PYPROJECT_TOML_PATH} does not exist -- all project configuration lives here"
    with open(PYPROJECT_TOML_PATH, "rb") as f:
        try:
            data = tomllib.load(f)
        except Exception as e:
            raise AssertionError(
                f"{PYPROJECT_TOML_PATH} could not be parsed -- tomllib may have "
                f"encountered a syntax error: {e}"
            ) from e
    return data


def _normalized_names(requirement_strings: list[str], where: str) -> set[str]:
    """Map a PEP 508 requirement list to its set of normalized distribution names.

    Parsing each entry as a `Requirement` strips the version specifier, extras and
    environment markers, leaving only the distribution name, which
    `canonicalize_name` then folds per PEP 503 (lowercased, with `-`/`_`/`.` runs
    collapsed to a single `-`). Comparing on that form is what makes these gates
    survive a later bound change such as `>=2.7,<3` becoming `>=3,<4`, and keeps
    them from being fooled by a `sphinxcontrib_bibtex` or `SphinxContrib.BibTeX`
    spelling of the same distribution.

    An unparseable entry raises rather than being skipped, so a typo in the manifest
    cannot quietly shrink the set these assertions run against.
    """
    names = set()
    for req_string in requirement_strings:
        try:
            names.add(canonicalize_name(Requirement(req_string).name))
        except Exception as e:
            raise AssertionError(
                f"Could not parse requirement '{req_string}' in {where}: {e}"
            ) from e
    return names


def test_dev_extra_declares_sphinxcontrib_bibtex():
    """[project.optional-dependencies].dev MUST name sphinxcontrib-bibtex (R012).

    R012 requires bibliography support to activate only when the user installs and
    enables `sphinxcontrib-bibtex` themselves. MEM003 resolves that into a dev-extra
    declaration: the package is a *test* dependency of typsphinx, because this slice's
    bibliography tests must build a Sphinx project whose `conf.py` lists
    `sphinxcontrib.bibtex` in `extensions` and whose source carries a `:cite:p:`
    citation and a `.. bibliography::` directive.

    Without this entry, `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
    --extra dev` does not install the package, and those tests fail during Sphinx app
    setup -- an extension-load error that says nothing about the citation rendering
    they were written to measure. The gap is also environment-dependent and so easy to
    miss locally: on a machine where `sphinxcontrib-bibtex` is already installed for an
    unrelated reason the suite passes, and only a clean CI provisioning surfaces it.

    Asserted on the normalized distribution name with the version specifier stripped,
    so moving the `>=2.7,<3` bound does not break this gate.
    """
    pyproject = _load_pyproject()

    # Vacuous-pass guards: the tables this assertion reads must exist and be non-empty,
    # so a restructured or truncated manifest fails loudly rather than passing trivially.
    assert (
        "project" in pyproject
    ), "[project] table not found in pyproject.toml -- all package configuration lives here"

    assert (
        "optional-dependencies" in pyproject["project"]
    ), "[project.optional-dependencies] table not found in pyproject.toml"

    assert (
        "dev" in pyproject["project"]["optional-dependencies"]
    ), "[project.optional-dependencies].dev not found in pyproject.toml"

    dev_extra = pyproject["project"]["optional-dependencies"]["dev"]
    assert (
        dev_extra
    ), "[project.optional-dependencies].dev is empty -- the vacuous-pass guard fired"

    dev_names = _normalized_names(dev_extra, "the dev extra")

    assert BIBTEX_DISTRIBUTION in dev_names, (
        "dev extra does not name 'sphinxcontrib-bibtex' (on normalized distribution "
        "name) -- R012 makes this package a dev/test dependency of typsphinx: the "
        "bibliography tests in this slice build a Sphinx project whose conf.py lists "
        "sphinxcontrib.bibtex in `extensions`, and they cannot run at all unless "
        "`uv sync --extra dev` installs it. Without the entry those tests fail during "
        "Sphinx app setup with an extension-load error rather than on the citation "
        "behaviour they measure, and the breakage is invisible on any machine where "
        "the package happens to already be installed -- only a clean CI provisioning "
        "catches it. Add it to [project.optional-dependencies].dev with a bounded "
        "specifier in the style of the neighbouring entries, e.g. "
        "'sphinxcontrib-bibtex>=2.7,<3'. Per MEM003 it belongs ONLY there: do not move "
        "it into [project].dependencies (see the companion test in this module) and do "
        "not create a [bibtex] optional extra."
    )


def test_runtime_dependencies_do_not_declare_sphinxcontrib_bibtex():
    """[project].dependencies MUST NOT name sphinxcontrib-bibtex (R012).

    This is the clause that actually enforces R012's user-facing promise: a typsphinx
    user who writes no bibliographies must not carry `sphinxcontrib-bibtex`, and
    through it pybtex and its dependency tree. Users who *do* want bibliographies
    install the package themselves regardless, because they must name it in `conf.py`'s
    `extensions` for any of its roles and directives to exist -- so a runtime
    dependency buys those users nothing while taxing everyone else. MEM003 records this
    as decided, and also rules out a `[bibtex]` optional extra as the alternative
    packaging route.

    **Why no behavioural test can substitute for this gate.** Per MEM002, typsphinx
    registers nothing from the bibliography surface: the `:cite:*` roles, the `cite`
    domain and the `.. bibliography::` / `.. footbibliography::` directives all stay
    with sphinxcontrib-bibtex, and typsphinx's contribution is to translate the
    resolved `reference` / `citation` nodes that package leaves in the doctree. No
    module under `typsphinx/` imports `sphinxcontrib.bibtex`. A leak into
    [project].dependencies therefore changes nothing any test observes -- the suite
    stays green, the bibliography features keep working, and the only consequence is
    an inflated install for end users. Exactly as `test_toolchain_config_gate.py`
    argues for the toolchain packages, a static manifest assertion is the only defense
    against a silent regression of this shape.

    The failure message names the offending entry so a leak is immediately actionable.
    """
    pyproject = _load_pyproject()

    # Vacuous-pass guards: the table this assertion reads must exist and be non-empty.
    assert (
        "project" in pyproject
    ), "[project] table not found in pyproject.toml -- all package configuration lives here"

    assert (
        "dependencies" in pyproject["project"]
    ), "[project].dependencies not found in pyproject.toml"

    dependencies = pyproject["project"]["dependencies"]
    assert (
        dependencies
    ), "[project].dependencies is empty -- the vacuous-pass guard fired"

    # Name the offending raw entry (not just the normalized name) so a leak reported by
    # this gate points at the exact line to delete from pyproject.toml.
    offenders = [
        req_string
        for req_string in dependencies
        if canonicalize_name(Requirement(req_string).name) == BIBTEX_DISTRIBUTION
    ]

    assert not offenders, (
        f"[project].dependencies names sphinxcontrib-bibtex: {offenders!r} -- "
        "this package belongs in the `dev` extra only. R012 requires bibliography "
        "support to activate solely when the user installs and enables "
        "sphinxcontrib-bibtex themselves, so that users who write no bibliographies "
        "never carry pybtex and its dependency tree; users who do want bibliographies "
        "already install it themselves, since they must list it in conf.py's "
        "`extensions` for its roles and directives to exist at all. Nothing under "
        "typsphinx/ imports sphinxcontrib.bibtex (MEM002: role, domain and directive "
        "registration stays entirely with that package; typsphinx only renders the "
        "resolved doctree nodes), so this leak is silent -- the test suite stays green "
        "and the whole cost lands on end users' installs. Remove the entry from "
        "[project].dependencies; the declaration in "
        "[project.optional-dependencies].dev is the correct and only home for it "
        "(MEM003, which also rules out a [bibtex] optional extra)."
    )
