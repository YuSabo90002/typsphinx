"""
Tests guarding tox.ini's runner/package configuration and pyproject.toml dependency
invariants (QUA-04, Phase 45.2).

This module asserts four critical toolchain configuration constraints exposed during
Phase 45.2's migration from tox-uv to tox-uv-bare and the conversion of [testenv]
from non-editable to editable package installs:

**GAP G3 (45.2-02-D3):** Every tox.ini section declaring `runner = uv-venv-lock-runner`
must declare an `extras` key and must NOT declare a `deps` key. This invariant is
critical because `uv-venv-lock-runner` provisions each environment solely from `uv.lock`
via `uv sync` and NEVER consults a `deps` list in tox.ini. A `deps` key silently goes
unread (no error, no warning) — and before Phase 45.2, this gap was masked because
those environments' tools (pytest, black, ruff, mypy) resolved from the outer `.venv`
via the PATH-shadowing mechanism 45.2-CONTEXT.md D-04 diagnosed: CI invokes
`uv run tox -e lint`, and `uv run` prepends `.venv/bin` to PATH, so `black`/`ruff`
ran and passed on CI run 31287786840 even though that run's own `lint: freeze>` line
shows `.tox/lint` contained neither of them. Reverting to `deps`
would produce NO failure signal at runtime, leaving the defect undetected. Plan 02's
patterns-established block states: "New tox environments must declare their tooling via
extras ... never deps — uv-venv-lock-runner silently ignores deps and only the plan's
own manual verification catches the gap." This test provides automated detection.

**GAP G4 (45.2-05-D3):** [testenv] must declare `package = editable` and must NOT
declare a `wheel_build_env` key. The prior setting `package = wheel` built non-editable
typsphinx installs that silently dropped `typsphinx/templates/base.typ` under CI's
uv 0.12.3 (but NOT under this machine's uv 0.11.25), causing 23 pytest failures across
py312/py313/cov, all `FileNotFoundError: Default template not found`. CI runs
31444258982/31444883849 captured the failure; commit 2fb6c6f in Plan 05 fixed it by
switching to `package = editable`. This was never exercised in pre-45.2 environments
because pytest had always resolved against the outer editable `.venv` via the same
PATH-shadowing mechanism as G3. The failure is uv-version-dependent and unreproducible
locally — a static gate is the only defense.

**GAP G5 (45.2-02-D1, SC#2):** [project.optional-dependencies].dev MUST name
`tox-uv-bare` (by normalized distribution name) and MUST NOT name `tox-uv`. The
plain `tox-uv` meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot
exec on NixOS; uv.find_uv_bin() searches .venv/bin first and reads no environment
variable. A revert from `tox-uv-bare` to `tox-uv` reinstates the broken .venv/bin/uv,
re-breaks every local `tox` invocation and the 45 pytest failures that Step 3 of
45.2-TOOLCHAIN-EVIDENCE.md censused — confined to the 5 modules that invoke `uv` in a
subprocess argument list. 45.2-CONTEXT.md D-09 deliberately leaves those 5 modules on
`uv run` rather than normalizing them onto `sys.executable -m sphinx`, precisely because
they are this defect class's only runtime regression detector; this gate is the static
counterpart. Critically, CI would stay green — the defect
is NixOS-specific, so only the maintainer's machine shows it. That asymmetry (no CI
signal) is precisely why this static gate exists. See CLAUDE.md 'Conventions & gotchas':
"The -bare package is deliberate (QUA-04, Phase 45.2) ... Do not 'simplify' it back to
tox-uv."

**GAP G6 (45.2-05-D2, SC#7):** [project].dependencies MUST NOT name any of: uv, tox,
tox-uv, tox-uv-bare (by normalized distribution name). SC#7 establishes that Phase 45.2's
fix stayed entirely inside the `dev` extra and that typsphinx/ plus [project].dependencies
are unchanged. Leaking a toolchain package into [project].dependencies would ship dev
tooling to every typsphinx end-user. The @preview-count clause of SC#7 is guarded by
tests/test_preview_version_sync.py; this gate covers the dependency clause, which had
no automated guard before this audit.

Implementation: stdlib tomllib reads pyproject.toml; stdlib configparser reads tox.ini.
Vacuous-pass guards assert files exist, parse, and discovered tables/sections are
non-empty. All assertions carry consequence-focused messages (not "expected X, got Y")
matching test_readthedocs_config.py's assertive-guard idiom. Distribution name
comparison uses packaging.utils.canonicalize_name (already available transitively).
No subprocess, no network, no external tools beyond stdlib+packaging.
"""

import configparser
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

REPO_ROOT = Path(__file__).resolve().parents[1]
TOX_INI_PATH = REPO_ROOT / "tox.ini"
PYPROJECT_TOML_PATH = REPO_ROOT / "pyproject.toml"


def _load_tox_ini() -> configparser.ConfigParser:
    """Parse tox.ini via configparser.

    Guards against a vacuous pass: asserts the file exists (named explicitly
    so a missing file fails loudly) and that the parser successfully reads it,
    so a malformed file cannot silently satisfy later assertions.
    """
    assert (
        TOX_INI_PATH.exists()
    ), f"{TOX_INI_PATH} does not exist -- all tox configuration lives here"
    parser = configparser.ConfigParser()
    read_files = parser.read(TOX_INI_PATH, encoding="utf-8")
    assert (
        read_files
    ), f"{TOX_INI_PATH} could not be parsed -- configparser may have encountered a syntax error"
    return parser


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


def test_uv_venv_lock_runner_requires_extras_forbids_deps():
    """Every [testenv*] section with runner=uv-venv-lock-runner must declare extras, not deps.

    Dynamically discovers all tox.ini sections declaring `runner = uv-venv-lock-runner`
    and asserts each one:
    1. Declares an `extras` key (the mechanism uv-venv-lock-runner uses to install tooling)
    2. Does NOT declare a `deps` key (uv-venv-lock-runner ignores it silently)

    This gate catches silent configuration errors: before Phase 45.2, tox environments
    with `runner = uv-venv-lock-runner` and inert `deps` blocks appeared to work only
    because pytest/black/ruff/mypy resolved from the outer `.venv` via PATH-shadowing.
    The `deps` key is never read by the runner, so no CI failure signal would warn of
    the configuration drift until the outer `.venv` was no longer available or the tool
    moved into the environment.

    Scope: this gate covers all uv-venv-lock-runner sections discovered at test time,
    so future environments added to tox.ini are automatically covered — no hardcoded
    section-name list to maintain.
    """
    parser = _load_tox_ini()
    sections = parser.sections()

    # Guard against vacuous pass: ensure the file carries at least one
    # uv-venv-lock-runner section; if the runner key is removed or renamed
    # everywhere, this assertion will catch it.
    uv_venv_lock_sections = [
        section
        for section in sections
        if parser.has_option(section, "runner")
        and parser.get(section, "runner") == "uv-venv-lock-runner"
    ]
    assert uv_venv_lock_sections, (
        f"No sections found with `runner = uv-venv-lock-runner` in {TOX_INI_PATH} -- "
        "the vacuous-pass guard fired: either all runners have been removed/renamed "
        "(making this test meaningless), or the tox.ini structure has drifted "
        "significantly from the Phase 45.2-established pattern"
    )

    for section in uv_venv_lock_sections:
        # G3 requirement 1: the section MUST declare an `extras` key.
        assert parser.has_option(section, "extras"), (
            f"[{section}] declares `runner = uv-venv-lock-runner` but has no `extras` key -- "
            "uv-venv-lock-runner provisions tooling solely from uv.lock via `uv sync`, "
            "reading the `extras` specifier to determine what to install. Without this key, "
            "any tool this environment needs (pytest, black, ruff, mypy) will not be installed "
            "in the environment's own .tox subdirectory; it would have to exist in the outer "
            ".venv for PATH-shadowing to resolve it, creating a latent defect. See "
            "Phase 45.2 Plan 02 patterns-established entry and CLAUDE.md 'Conventions & gotchas' "
            "for the full explanation of the PATH-shadowing mechanism that masked this gap "
            "pre-45.2."
        )

        # G3 requirement 2: the section MUST NOT declare a `deps` key.
        assert not parser.has_option(section, "deps"), (
            f"[{section}] declares both `runner = uv-venv-lock-runner` and `deps` -- "
            "uv-venv-lock-runner does not read the `deps` key at all. The key is silently "
            "ignored with no warning or error, so reverting to this pattern produces no "
            "failure signal: tox runs, the environment provisioning completes (minus the "
            "uninstalled tools), and any test execution that happens to find tools in the "
            "outer `.venv` via PATH-shadowing appears to succeed. This is precisely the "
            "defect D-04 diagnosed for [testenv:lint] in Phase 45.2 Plan 02 -- removing the "
            "inert `deps` blocks was essential to making the environments self-contained. "
            "See 45.2-02-SUMMARY.md coverage entry D3 for the transcript of tox config "
            "output showing the deps key was successfully removed from all four environments."
        )


def test_testenv_package_is_editable_not_wheel():
    """[testenv] must declare package=editable and must not declare wheel_build_env.

    This gate prevents regression to non-editable typsphinx package installations in
    [testenv], which caused a critical, uv-version-dependent CI failure during Phase 45.2:

    **Symptom:** 23 pytest failures across py312/py313/cov, all with:
        FileNotFoundError: Default template not found ... Package installation may be corrupted.

    **Root cause:** [testenv]'s pre-existing `package = wheel` (present since the project's
    first commit) builds a non-editable install via setuptools. Under uv 0.12.3 (CI's version
    during the failure), this non-editable build silently omitted the package data file
    `typsphinx/templates/base.typ` from the installed package. The same `package = wheel`
    setting exists on this machine with uv 0.11.25 and does NOT exhibit the failure,
    indicating the root cause is uv-version-dependent and cannot be reproduced locally --
    making a static gate the only defense.

    **Why [testenv]'s pytest never caught it pre-45.2:** these environments declared
    their tooling via an inert `deps` block (the G3 defect above), so `.tox/py312`,
    `.tox/py313` and `.tox/cov` never installed a pytest of their own. Every run
    therefore resolved `pytest` from the OUTER editable `.venv` through the same
    PATH-shadowing mechanism 45.2-CONTEXT.md D-04 diagnosed for `lint`'s tools — and
    an editable install resolves `typsphinx` from the source tree, where
    `templates/base.typ` is simply present on disk. The wheel-mode packaging gap was
    only ever exercised once `extras = dev` made each environment self-contained,
    which is why a setting present since the project's first commit failed for the
    first time in Phase 45.2.

    **Fix (Phase 45.2 Plan 05, commit 2fb6c6f):** Switch to `package = editable`, which
    matches what an outer `uv sync --extra dev` already does successfully and removes the
    wheel-build step. Verified: local `tox -e py313` full suite → 984 passed/5 skipped;
    CI run 31445582363 (post-fix) shows the same test jobs green where runs 31444258982/
    31444883849 had FileNotFoundError failures.

    **CI evidence:**
    - Pre-fix failures: CI runs 31444258982 (all 23 failures) and 31444883849 (same)
    - Post-fix green: CI run 31445582363 (Code Coverage, Test Python jobs all pass)
    - Full transcript in Phase 45.2 Plan 05 45.2-TOOLCHAIN-EVIDENCE.md Step 8

    This test asserts the fix is preserved and the defect cannot regress undetected.
    """
    parser = _load_tox_ini()

    # Vacuous-pass guard: assert [testenv] exists (if it's removed, that's a
    # bigger structural change we want to catch explicitly, not silently pass).
    assert parser.has_section("testenv"), (
        f"[testenv] section not found in {TOX_INI_PATH} -- "
        "this is the primary test environment where pytest runs; removing it would "
        "be a major structural change that should fail this gate loudly rather than "
        "silently passing."
    )

    # G4 requirement 1: [testenv] MUST declare `package = editable`.
    assert parser.has_option("testenv", "package"), (
        "[testenv] does not declare a `package` key -- "
        "without this key, tox defaults to its own legacy behavior, which may not match "
        "the uv-venv-lock-runner's `package = editable` default. Explicit declaration "
        "is safer than relying on defaults."
    )

    package_value = parser.get("testenv", "package")
    assert package_value == "editable", (
        f"[testenv] declares `package = {package_value!r}`, not `package = editable` -- "
        "the prior setting `package = wheel` built non-editable installs that silently "
        "dropped `typsphinx/templates/base.typ` from the installed package under CI's "
        "uv 0.12.3, causing 23 pytest failures (FileNotFoundError: Default template not found). "
        "The failure is uv-version-dependent: uv 0.11.25 on this machine does NOT exhibit it, "
        "so it cannot be reproduced or tested locally. The only defense is this static gate. "
        "Switch to `package = editable`, which matches what `uv sync --extra dev` already does "
        "successfully and removes the wheel-build step. See Phase 45.2 Plan 05 commit 2fb6c6f "
        "and CI run 31445582363 (post-fix green) vs. pre-fix runs 31444258982/31444883849 "
        "(all 23 failures)."
    )

    # G4 requirement 2: [testenv] MUST NOT declare `wheel_build_env`.
    assert not parser.has_option("testenv", "wheel_build_env"), (
        "[testenv] declares `wheel_build_env` alongside (or instead of) `package = editable` -- "
        "wheel_build_env is only meaningful with `package = wheel` and should not coexist "
        "with `package = editable`. Its presence indicates a partial revert to wheel-mode "
        "packaging, which is the defect state this gate protects against. Remove the "
        "wheel_build_env key entirely."
    )


def test_dev_extra_pins_tox_uv_bare_not_tox_uv():
    """[project.optional-dependencies].dev MUST name tox-uv-bare, MUST NOT name tox-uv.

    This gate prevents a critical NixOS-specific regression: the plain `tox-uv` meta
    package bundles a PyPI `uv` wheel (generic-linux ELF) that cannot execute on NixOS
    due to the stub-ld defect QUA-04 fixed. Reverting from `tox-uv-bare` to `tox-uv`
    would reinstate the broken .venv/bin/uv and re-break every local `tox` environment
    plus the 45 pytest failures censused in 45.2-TOOLCHAIN-EVIDENCE.md Step 3, which are
    confined to the 5 test modules that invoke `uv` in a subprocess argument list.
    45.2-CONTEXT.md D-09 keeps those 5 modules on `uv run` on purpose — they are this
    defect class's only runtime regression detector, and this gate is its static
    counterpart, catching the revert at the config level before a suite run is needed.

    **Why this defect stays undetected on CI:** CI runs on Linux runner images with
    glibc, not NixOS; the `tox-uv` wheel's generic-linux ELF executes there. Only the
    maintainer's machine (NixOS) exhibits the defect. That asymmetry (no CI signal) is
    exactly why SC#2 mandates a static gate rather than relying on CI to catch it.

    **The naming trap:** "tox-uv-bare" contains the substring "tox-uv". A naive
    substring-match test would either false-positive on the correct value or false-
    negative the bad one. This gate parses each requirement's distribution NAME
    (via packaging.requirements.Requirement) and compares the normalized name, not
    the raw requirement string.

    **Scope:** All package names are compared on their normalized distribution names
    (via packaging.utils.canonicalize_name), so future variations in spacing or case
    are covered automatically.

    See CLAUDE.md 'Conventions & gotchas' for the full explanation: "The -bare package
    is also deliberate (QUA-04, Phase 45.2): the plain `tox-uv` meta package bundles
    a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()`
    searches `.venv/bin` first and reads no environment variable. Do not 'simplify'
    it back to `tox-uv`."
    """
    pyproject = _load_pyproject()

    # Guard against vacuous pass: ensure [project.optional-dependencies] exists and
    # is non-empty; the dev extra must be present and non-empty.
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

    # Parse all requirements in the dev extra and collect normalized distribution names.
    dev_names = set()
    for req_string in dev_extra:
        try:
            req = Requirement(req_string)
            dev_names.add(canonicalize_name(req.name))
        except Exception as e:
            raise AssertionError(
                f"Could not parse requirement '{req_string}' in dev extra: {e}"
            ) from e

    # G5 requirement 1: dev extra MUST contain tox-uv-bare.
    assert canonicalize_name("tox-uv-bare") in dev_names, (
        "dev extra does not contain 'tox-uv-bare' (on normalized distribution name) -- "
        "Phase 45.2's migration from tox-uv to tox-uv-bare switched the dev environment "
        "to the -bare variant to work around the generic-linux-ELF NixOS defect (QUA-04). "
        "The plain tox-uv meta package bundles a PyPI uv wheel that cannot execute on NixOS; "
        "uv.find_uv_bin() searches .venv/bin FIRST and reads no environment variable. "
        "Without tox-uv-bare, every local `tox` invocation fails, and 45 pytest tests "
        "confined to the 5 modules that invoke uv in a subprocess argument list will fail. "
        "Critically, CI would stay GREEN (the defect is NixOS-specific), so only the "
        "maintainer's machine would show it. See CLAUDE.md 'Conventions & gotchas' and SC#2 "
        "for full context. Evidence: 45.2-TOOLCHAIN-EVIDENCE.md Step 3 (pre-fix, 45 failed) "
        "vs. Step 7 (post-fix, 0 failed), and CI run 31445582363 (post-fix green)."
    )

    # G5 requirement 2: dev extra MUST NOT contain tox-uv.
    assert canonicalize_name("tox-uv") not in dev_names, (
        "dev extra contains 'tox-uv' (on normalized distribution name) -- "
        "this is precisely the defect QUA-04 fixed. The plain tox-uv meta package bundles "
        "a PyPI uv wheel whose generic-linux ELF cannot execute on NixOS; uv.find_uv_bin() "
        "searches .venv/bin FIRST and reads no environment variable. A revert from tox-uv-bare "
        "to tox-uv reinstates the broken .venv/bin/uv and re-breaks every local `tox` command "
        "plus the 45 pytest tests confined to the 5 uv-invoking modules. The defect is "
        "NixOS-specific, so CI would stay GREEN — that asymmetry (no CI signal) is why SC#2 "
        "established this static gate. Switch to tox-uv-bare; do NOT 'simplify' this back to "
        "tox-uv (per CLAUDE.md). See 45.2-TOOLCHAIN-EVIDENCE.md Step 3 for the pre-fix "
        "45-failure census and Step 5 for the post-fix census proving .venv/bin/uv absent."
    )


def test_runtime_dependencies_carry_no_toolchain_package():
    """[project].dependencies MUST NOT name any of: uv, tox, tox-uv, tox-uv-bare.

    This gate establishes that Phase 45.2's fix stayed entirely inside the `dev` extra
    and that [project].dependencies remain unchanged. Leaking a toolchain package into
    [project].dependencies would ship dev tooling to every typsphinx end-user,
    inflating their install size, adding unnecessary transitive dependencies, and
    blurring the boundary between dev and runtime concerns.

    **SC#7 context:** Phase 45.2 established a fence between build/dev tooling (which
    moved into the `dev` extra) and runtime dependencies (which must carry only what
    users need). SC#7 reads: "No runtime surface moves. `[project] dependencies` is
    untouched, `typsphinx/` is untouched, the `@preview` count stays at four, and the only
    `pyproject.toml` change is inside the `dev` extra — asserted mechanically over this
    phase's own diff, because Phase 46's SC#3 measures the tree this phase hands it."

    Its `@preview`-count clause is already guarded by tests/test_preview_version_sync.py.
    This gate covers the `[project] dependencies` clause, which had no automated guard
    before this audit. The `typsphinx/`-untouched clause remains a diff-time assertion,
    not a testable invariant, and is not claimed here.

    **Scope:** All package names are compared on their normalized distribution names
    (via packaging.utils.canonicalize_name), so future variations in spacing or case
    are covered automatically. The forbidden list (uv, tox, tox-uv, tox-uv-bare) covers
    all possible toolchain packages that should never land in runtime dependencies.

    See Phase 45.2 Plan 05 45.2-TOOLCHAIN-EVIDENCE.md Step 9 for the mechanical assertion
    of SC#7: tomllib comparison (not text-grep) proves [project].dependencies byte-identical
    as parsed data between the pre-phase base and HEAD.
    """
    pyproject = _load_pyproject()

    # Guard against vacuous pass: ensure [project] exists and [project].dependencies
    # exists and is non-empty.
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

    # Guard vacuity further: at least sphinx should be present (the most critical runtime dep).
    dep_names = set()
    for req_string in dependencies:
        try:
            req = Requirement(req_string)
            dep_names.add(canonicalize_name(req.name))
        except Exception as e:
            raise AssertionError(
                f"Could not parse requirement '{req_string}' in dependencies: {e}"
            ) from e

    assert canonicalize_name("sphinx") in dep_names, (
        "Sphinx not found in [project].dependencies -- this would be a critical break "
        "since Sphinx is the core runtime dependency of typsphinx. Either the file was "
        "corrupted or the test environment has drifted."
    )

    # G6 requirement: [project].dependencies MUST NOT contain any toolchain packages.
    forbidden_packages = {"uv", "tox", "tox-uv", "tox-uv-bare"}
    forbidden_normalized = {canonicalize_name(name) for name in forbidden_packages}

    bad_packages = forbidden_normalized & dep_names
    assert not bad_packages, (
        f"[project].dependencies contains one or more toolchain packages: {sorted(bad_packages)} -- "
        "these belong in the `dev` extra only, not in runtime dependencies. Phase 45.2's fix moved "
        "all toolchain packages (tox, tox-uv-bare, pytest, black, ruff, mypy) into [project.optional-dependencies].dev, "
        "establishing a fence between dev tooling and runtime concerns. SC#7 mandates that [project].dependencies "
        "remain unchanged (compare: Phase 45.2 pre-phase base vs. HEAD via `git diff`) and carry no toolchain "
        "packages. Leaking a toolchain package here would ship dev tooling to every typsphinx end-user, "
        "inflating their environment, adding unnecessary transitive dependencies, and breaking the "
        "dev/runtime boundary. If a genuine runtime need for one of these packages emerges, that's a "
        "distinct feature request (Phase 46+), not a carry-over from this phase's fix. See Phase 45.2 "
        "Plan 05 45.2-TOOLCHAIN-EVIDENCE.md Step 9 for the full mechanical assertion of SC#7."
    )
