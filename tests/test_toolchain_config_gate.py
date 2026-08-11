"""
Tests guarding tox.ini's runner and package configuration invariants (QUA-04, Phase 45.2).

This module asserts two critical toolchain configuration constraints exposed during
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

Implementation: stdlib configparser reads tox.ini; vacuous-pass guards assert the file
exists, parses, and discovered sections are non-empty; all assertions carry consequence-
focused messages (not just "expected X, got Y") matching test_readthedocs_config.py's
assertive-guard idiom. No subprocess, no network, no external tools.
"""

import configparser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOX_INI_PATH = REPO_ROOT / "tox.ini"


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
