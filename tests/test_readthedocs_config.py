"""
Tests guarding the RTD build manifest's shape and the `conf.py` language seam
(RTD-01 / D-06, Phase 29 Plan 01).

Read the Docs refuses every build without a `.readthedocs.yaml`, and RTD's
zero-config Sphinx build does not install the project package -- without
`python.install` the published docs would either fail to import `typsphinx`
or, worse, silently resolve a stale PyPI wheel instead of the checked-out
commit. This module asserts the commit-1 (HTML-only) shape of
`.readthedocs.yaml` and the two-layer `READTHEDOCS_LANGUAGE` ->
`SPHINX_LANGUAGE` -> `"en"` precedence chain in `docs/source/conf.py`.

PyYAML is available transitively via `sphinx` (confirmed under `uv run`,
per 29-PATTERNS.md) and is deliberately NOT added as a direct dependency --
this suite must be run under `uv run pytest`, per CLAUDE.md's standing
worktree-isolated execution mode. No test in this module performs a network
fetch; the suite stays hermetic.
"""

import importlib.util
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
READTHEDOCS_YAML_PATH = REPO_ROOT / ".readthedocs.yaml"
CONF_PY_PATH = REPO_ROOT / "docs" / "source" / "conf.py"
DOCS_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "docs.yml"

# Matches an `actions/setup-python`-style `python-version: "MAJOR.MINOR"` line.
_PYTHON_VERSION_RE = re.compile(r'python-version:\s*"(?P<version>\d+\.\d+)"')


def _load_readthedocs_yaml():
    """Parse `.readthedocs.yaml` via `yaml.safe_load`.

    Guards against a vacuous pass: asserts the file exists (named explicitly
    so a missing file fails loudly) and that the parsed document is a dict,
    so a scalar/None document cannot silently satisfy later key lookups.
    """
    assert (
        READTHEDOCS_YAML_PATH.exists()
    ), f"{READTHEDOCS_YAML_PATH} does not exist -- RTD refuses every build without it"
    data = yaml.safe_load(READTHEDOCS_YAML_PATH.read_text(encoding="utf-8"))
    assert isinstance(
        data, dict
    ), f"{READTHEDOCS_YAML_PATH} did not parse to a mapping (got {type(data)!r})"
    return data


def _extract_docs_workflow_python_version() -> str:
    """Parse the raw text of `docs.yml` for its `python-version:` line.

    Mirrors `_extract_readme_status_version`'s assertive-guard idiom: a
    reworded workflow fails loudly here rather than the comparison test
    silently comparing against nothing.
    """
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    match = _PYTHON_VERSION_RE.search(text)
    assert match, (
        f"Could not find a 'python-version: \"MAJOR.MINOR\"' line in "
        f"{DOCS_WORKFLOW_PATH} -- has the workflow's Python-setup step changed?"
    )
    return match.group("version")


def _load_conf_module():
    """Load `docs/source/conf.py` fresh as a standalone module.

    `conf.py` is not importable via plain `import` from the pytest path --
    nothing under `tests/` does so today (confirmed by repo grep); the two
    existing consumption mechanisms are `sphinx.testing.fixtures`' throwaway
    `conf.py` under `tests/roots/`, and raw-text regex parsing. Loading it
    fresh via `importlib.util` on every call re-evaluates the module-level
    `language` assignment against the current environment, which a cached
    `sys.modules` entry would not do.

    Executing this file has two pre-existing side effects, unchanged by this
    phase: a CWD-relative `sys.path.insert(0, "../..")` and a `tomllib` read
    of `pyproject.toml` to resolve `release`. Deliberately not registered in
    `sys.modules` so repeated calls stay independent.
    """
    spec = importlib.util.spec_from_file_location("_p29_conf_probe", CONF_PY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_readthedocs_yaml_shape():
    """`.readthedocs.yaml` carries the D-06 commit-1 (HTML-only) shape."""
    data = _load_readthedocs_yaml()

    assert data["version"] == 2, "`.readthedocs.yaml` must declare version: 2"

    assert isinstance(
        data["build"], dict
    ), "`.readthedocs.yaml` build: must be a mapping"
    assert data["build"]["os"] and isinstance(
        data["build"]["os"], str
    ), "`.readthedocs.yaml` build.os must be a non-empty string"
    assert isinstance(
        data["build"]["tools"]["python"], str
    ), "`.readthedocs.yaml` build.tools.python must be a string"

    assert (
        data["sphinx"]["configuration"] == "docs/source/conf.py"
    ), "`.readthedocs.yaml` sphinx.configuration must point at docs/source/conf.py"

    install = data["python"]["install"]
    assert (
        isinstance(install, list) and install
    ), "`.readthedocs.yaml` python.install must be a non-empty list"
    entry = install[0]
    assert entry.get("method") == "uv", "python.install[0].method must be 'uv'"
    assert entry.get("command") == "sync", "python.install[0].command must be 'sync'"
    assert "docs" in entry.get(
        "extras", []
    ), "python.install[0].extras must include 'docs'"


def test_build_python_matches_docs_workflow():
    """RTD's Python minor must match `.github/workflows/docs.yml`'s pin.

    D-12's PDF baseline comparison is only same-Python-minor if RTD and
    `.github/workflows/docs.yml` provision the same interpreter minor.
    Compares the two parsed values against each other -- never against a
    hardcoded expected version string -- so this stays correct across a
    future joint Python bump.
    """
    data = _load_readthedocs_yaml()
    rtd_python = data["build"]["tools"]["python"]
    workflow_python = _extract_docs_workflow_python_version()

    assert rtd_python == workflow_python, (
        f"`.readthedocs.yaml` build.tools.python={rtd_python!r} but "
        f"{DOCS_WORKFLOW_PATH} pins python-version={workflow_python!r} -- "
        "these must match so D-12's PDF baseline comparison runs on the "
        "same Python minor on both sides"
    )


def test_language_seam_precedence(monkeypatch):
    """`_resolve_language()` resolves READTHEDOCS_LANGUAGE -> SPHINX_LANGUAGE -> "en".

    Covers all four combinations of the two env vars, asserting on both the
    freshly-loaded module's `language` attribute and a direct call to
    `_resolve_language()`. A final wiring assertion checks that
    `html_context["language"]` reads the same resolved value -- this is what
    catches a helper that exists but is never called by the `language`
    assignment.
    """
    # (a) both unset -> "en"
    monkeypatch.delenv("READTHEDOCS_LANGUAGE", raising=False)
    monkeypatch.delenv("SPHINX_LANGUAGE", raising=False)
    module = _load_conf_module()
    assert module.language == "en"
    assert module._resolve_language() == "en"
    assert module.html_context["language"] == module.language

    # (b) only SPHINX_LANGUAGE set -> that value (existing override keeps working)
    monkeypatch.setenv("SPHINX_LANGUAGE", "ja")
    monkeypatch.delenv("READTHEDOCS_LANGUAGE", raising=False)
    module = _load_conf_module()
    assert module.language == "ja"
    assert module._resolve_language() == "ja"
    assert module.html_context["language"] == module.language

    # (c) only READTHEDOCS_LANGUAGE set -> that value (RTD's setting is honored)
    monkeypatch.delenv("SPHINX_LANGUAGE", raising=False)
    monkeypatch.setenv("READTHEDOCS_LANGUAGE", "ja")
    module = _load_conf_module()
    assert module.language == "ja"
    assert module._resolve_language() == "ja"
    assert module.html_context["language"] == module.language

    # (d) both set -> READTHEDOCS_LANGUAGE wins
    monkeypatch.setenv("READTHEDOCS_LANGUAGE", "ja")
    monkeypatch.setenv("SPHINX_LANGUAGE", "fr")
    module = _load_conf_module()
    assert module.language == "ja"
    assert module._resolve_language() == "ja"
    assert module.html_context["language"] == module.language
