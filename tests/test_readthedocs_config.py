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

It also guards the manifest's `build.apt_packages` provisioning seam: a
live column-0 `.. graphviz::` directive under `docs/source` requires the RTD
container to install the `graphviz` apt package, because
`sphinx.ext.graphviz` shells out to the `dot` binary rather than rendering
in Python. That gate is a pure static file-vs-file check -- see its own
docstring for the liveness approximation it uses and the boundary it does
not cover.

PyYAML is available transitively via `sphinx` (confirmed under `uv run`,
per 29-PATTERNS.md) and is deliberately NOT added as a direct dependency --
this suite must be run under `uv run pytest`, per CLAUDE.md's standing
worktree-isolated execution mode. No test in this module performs a network
fetch; the suite stays hermetic.
"""

import importlib.util
import re
import tomllib
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


def test_docs_workflow_has_no_github_pages_deploy():
    """CI-04 guard: docs.yml must never regain a GitHub Pages deploy step."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "peaceiris/actions-gh-pages" not in text, (
        "docs.yml must not contain a GitHub Pages deploy step -- "
        "CI-04 tore this down permanently"
    )
    assert "pages: write" not in text, (
        "docs.yml's permissions block must not request pages: write -- "
        "unused once the peaceiris deploy step is removed"
    )
    assert "id-token: write" not in text, (
        "docs.yml's permissions block must not request id-token: write -- "
        "release.yml declares its own separate copy for PyPI trusted "
        "publishing; this assertion is deliberately scoped to docs.yml "
        "alone rather than a repo-wide grep"
    )
    assert "contents: write" in text, (
        "docs.yml must retain permissions.contents: write -- required by "
        "the Upload PDF to Release step (softprops/action-gh-release)"
    )


def test_docs_workflow_still_uploads_pdf_to_release():
    """CI-04 guard: the tag-time Release attachment step must survive the teardown."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "softprops/action-gh-release" in text
    assert "Upload PDF to Release" in text


def test_readthedocs_yaml_pdf_override():
    """`.readthedocs.yaml` carries D-06's commit-2 (PDF-enabled) shape.

    `formats: [pdf]` and `build.jobs.build.pdf` must land together: RTD's
    override *replaces* the default LaTeX step for that format, so
    `formats: [pdf]` alone would silently activate RTD's own LaTeX pipeline
    instead of typsphinx's `typstpdf` builder (Common Pitfall 1). The
    override itself must build into a temporary directory and copy only
    `*.pdf` into `$READTHEDOCS_OUTPUT/pdf/`, creating that subdirectory
    first, because RTD does not pre-create it (Common Pitfall 3, D-04).
    """
    data = _load_readthedocs_yaml()
    build = data["build"]

    # 1. formats + build.jobs.build.pdf must land together.
    assert (
        isinstance(data.get("formats"), list) and "pdf" in data["formats"]
    ), "top-level formats must be a list containing 'pdf'"
    assert (
        "jobs" in build and "build" in build["jobs"] and "pdf" in build["jobs"]["build"]
    ), (
        "build.jobs.build.pdf must exist alongside formats: [pdf] -- "
        "formats alone activates RTD's own LaTeX pipeline instead of "
        "typsphinx's typstpdf builder (Common Pitfall 1)"
    )

    # 2. build.apt_packages must include fonts-noto-cjk (D-10).
    assert (
        isinstance(build.get("apt_packages"), list)
        and "fonts-noto-cjk" in build["apt_packages"]
    ), (
        "build.apt_packages must include 'fonts-noto-cjk' (D-10) -- "
        "the English docs contain CJK strings, typst-py's embedded fonts "
        "have no CJK coverage, and Typst's font fallback is silent, so "
        "without this package the PDF renders substituted glyphs in a "
        "build that reports success"
    )

    pdf_commands = build["jobs"]["build"]["pdf"]

    # 3. non-empty list of strings.
    assert (
        isinstance(pdf_commands, list) and pdf_commands
    ), "build.jobs.build.pdf must be a non-empty list of shell commands"
    assert all(
        isinstance(cmd, str) for cmd in pdf_commands
    ), "every build.jobs.build.pdf entry must be a string shell command"

    # 4. exactly one sphinx-build -b typstpdf invocation.
    typstpdf_indices = [
        i for i, cmd in enumerate(pdf_commands) if "sphinx-build -b typstpdf" in cmd
    ]
    assert len(typstpdf_indices) == 1, (
        "exactly one command in build.jobs.build.pdf must contain "
        f"'sphinx-build -b typstpdf', found {len(typstpdf_indices)}"
    )
    typstpdf_index = typstpdf_indices[0]

    # 5. that command must NOT reference $READTHEDOCS_OUTPUT.
    assert "READTHEDOCS_OUTPUT" not in pdf_commands[typstpdf_index], (
        "the sphinx-build -b typstpdf command must not reference "
        "READTHEDOCS_OUTPUT -- the builder writes many non-PDF files "
        "(a .typ per doc, every used key's _template/<key>/ bundle, a "
        "doctrees tree) into its output directory, so it must target a "
        "temporary directory instead (D-04)"
    )

    # 6. an explicit mkdir of $READTHEDOCS_OUTPUT/.../pdf/ (RTD does not
    #    pre-create the format subdirectory).
    mkdir_indices = [
        i
        for i, cmd in enumerate(pdf_commands)
        if "mkdir" in cmd and "READTHEDOCS_OUTPUT" in cmd and "pdf" in cmd
    ]
    assert mkdir_indices, (
        "at least one command must mkdir a 'pdf' path segment under "
        "$READTHEDOCS_OUTPUT -- RTD's post-build ingestion creates the "
        "format subdirectory, not the job itself, before this job runs "
        "(Common Pitfall 3)"
    )
    mkdir_index = mkdir_indices[0]

    # 7. a copy of only *.pdf into $READTHEDOCS_OUTPUT, via a *.pdf glob
    #    rather than a recursive or whole-directory copy.
    copy_indices = [
        i
        for i, cmd in enumerate(pdf_commands)
        if cmd.strip().startswith("cp ")
        and "*.pdf" in cmd
        and "READTHEDOCS_OUTPUT" in cmd
    ]
    assert copy_indices, (
        "at least one command must copy a '*.pdf' glob into "
        "$READTHEDOCS_OUTPUT -- only the PDF may cross into RTD's public "
        "download area"
    )
    copy_index = copy_indices[0]
    copy_cmd = pdf_commands[copy_index]
    assert "-r" not in copy_cmd.split() and "-R" not in copy_cmd.split(), (
        "the copy command must use a '*.pdf' glob, not a recursive copy "
        f"(no -r/-R flag): {copy_cmd!r}"
    )

    # 8. ordering: mkdir before copy.
    assert mkdir_index < copy_index, (
        "the mkdir command must appear before the copy command in "
        "build.jobs.build.pdf -- a copy before the mkdir fails with a "
        "'cannot create regular file' error because the pdf/ subdirectory "
        "does not yet exist"
    )

    # 9. no command delegates to this repository's tox runner.
    assert not any("tox" in cmd for cmd in pdf_commands), (
        "no command in build.jobs.build.pdf may reference this "
        "repository's tox runner -- RTD provisions its own environment "
        "through python.install, and nesting tox creates a redundant "
        "second venv with no working locked-sync wiring"
    )

    # 10. exactly one sphinx-build invocation total, with no locale/language
    #     flag -- this manifest's PDF build is English; the Japanese PDF is
    #     produced by a separate manifest in the typsphinx-doc-translations
    #     repository, whose language is supplied by that project's own Read
    #     the Docs Admin Language setting through READTHEDOCS_LANGUAGE, never
    #     by a flag on this manifest's sphinx-build (Phase 30.1 D-04/D-05).
    sphinx_build_indices = [
        i for i, cmd in enumerate(pdf_commands) if "sphinx-build" in cmd
    ]
    assert len(sphinx_build_indices) == 1, (
        "exactly one sphinx-build invocation must exist in "
        f"build.jobs.build.pdf, found {len(sphinx_build_indices)}"
    )
    sole_command = pdf_commands[sphinx_build_indices[0]]
    assert (
        "-D language" not in sole_command
        and " -l " not in sole_command
        and "--language" not in sole_command
    ), (
        "the sole sphinx-build invocation must carry no locale or language "
        "flag -- fonts-noto-cjk is scoped strictly to the four CJK strings "
        "inside the English documentation; the Japanese PDF ships from a "
        "different manifest in the typsphinx-doc-translations repository "
        f"(Phase 30.1 D-04/D-05): {sole_command!r}"
    )


def test_readthedocs_yaml_provisions_graphviz_for_live_directive():
    """A live column-0 `.. graphviz::` binds `build.apt_packages` to `graphviz`.

    `sphinx.ext.graphviz` draws nothing itself -- it shells out to Graphviz's
    `dot` binary, which is an apt package and not a Python one. This gate is
    deliberately a pure static file-vs-file check: it reads the `.rst` files
    under `docs/source`, `.readthedocs.yaml`, and `pyproject.toml` off disk,
    and runs no subprocess, no network fetch, and no Sphinx build -- so its
    verdict is identical on Read the Docs, on CI, and on the maintainer's
    NixOS machine. Build-based detection is rejected on purpose:
    build-dependence is precisely the property that let the original defect
    ship (a build reporting success while the page was broken), and Sphinx
    localises warning bodies to the host `LANG`, so a warning-text assertion
    would diverge between a local run and CI.

    Documented boundary. Liveness is approximated here by column-0
    anchoring, which isolates today's single live directive from the prose
    mentions and the `.. code-block:: rst` sample that merely talk *about*
    the directive. Indentation is NOT a general liveness rule in this tree
    -- live indented directives of other types exist here -- so a genuinely
    live `.. graphviz::` nested inside, say, a `.. only::` or `.. figure::`
    block would be MISSED by this pattern. The pinned count below is the
    tripwire for exactly that: any change to the number of live column-0
    directives fails this gate and forces a human to re-measure and re-pin,
    rather than letting the approximation drift silently.
    """
    live_directive_re = re.compile(r"^\.\. graphviz::", re.MULTILINE)
    live_directive_sites = []
    for rst_path in sorted((REPO_ROOT / "docs" / "source").rglob("*.rst")):
        text = rst_path.read_text(encoding="utf-8")
        for match in live_directive_re.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            live_directive_sites.append(
                f"{rst_path.relative_to(REPO_ROOT)}:{line_number}"
            )

    # Asserted FIRST, before anything about the manifest: a tree with zero
    # live directives must not be able to satisfy this gate silently. This
    # project has a measured precedent for that blind spot -- a gate that
    # derived both sides of its comparison from a single helper stayed green
    # under a mutation that collapsed both sides at once.
    assert len(live_directive_sites) == 1, (
        "expected exactly 1 live column-0 `.. graphviz::` directive under "
        "docs/source -- today's sole site is "
        "docs/source/user_guide/diagrams.rst:8 -- but found "
        f"{len(live_directive_sites)}: {live_directive_sites}. This count is "
        "pinned deliberately: any change to the number of live column-0 "
        "directives requires a human to re-measure and re-pin it here, "
        "because both this gate and the apt_packages entry it guards are "
        "justified only by that measurement."
    )

    data = _load_readthedocs_yaml()
    build = data.get("build")
    assert isinstance(build, dict), (
        f"`build` did not parse to a mapping in {READTHEDOCS_YAML_PATH} "
        f"(got {type(build)!r})"
    )
    apt_packages = build.get("apt_packages")
    why_dot_is_required = (
        "`sphinx.ext.graphviz` shells out to the `dot` binary, and upstream "
        "`render_dot()` catches the resulting `OSError` and returns "
        "`(None, None)` without raising -- so when `dot` is absent the page "
        "silently ships the escaped DOT source as literal text inside a "
        "build that reports success. Nothing fails; the page is just wrong."
    )
    assert isinstance(apt_packages, list), (
        "`build.apt_packages` must be a list naming `graphviz` while a live "
        f"`.. graphviz::` directive exists at {live_directive_sites[0]} "
        f"(got {apt_packages!r}). {why_dot_is_required}"
    )
    assert "graphviz" in apt_packages, (
        "`build.apt_packages` must contain `graphviz` while a live "
        f"`.. graphviz::` directive exists at {live_directive_sites[0]}; "
        f"the manifest currently installs {apt_packages!r}. "
        f"{why_dot_is_required}"
    )

    # The fix belongs in the container's apt layer, never in a Python extra.
    # `graphviz` is also the name of a PyPI package (a Python binding that
    # still requires the system binary), so adding anything graphviz-shaped
    # to the `docs` extra looks like a fix while leaving the RTD container
    # just as `dot`-less as before -- that is the exact non-fix this
    # constraint exists to block.
    pyproject = tomllib.loads(
        (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    docs_extra = pyproject["project"]["optional-dependencies"]["docs"]
    assert isinstance(
        docs_extra, list
    ), f"`project.optional-dependencies.docs` must be a list (got {docs_extra!r})"
    graphviz_shaped = [req for req in docs_extra if "graphviz" in req.lower()]
    assert graphviz_shaped == [], (
        "`graphviz` must appear nowhere in pyproject.toml's `docs` extra, "
        f"but found {graphviz_shaped}. Graphviz is a system binary (`dot`), "
        "not a Python dependency: installing a graphviz-shaped Python "
        "requirement looks like a fix while leaving the Read the Docs "
        "container still without `dot`. The provisioning seam is "
        "`.readthedocs.yaml`'s `build.apt_packages`, asserted above."
    )


def test_language_seam_precedence(monkeypatch):
    """`_resolve_language()` resolves READTHEDOCS_LANGUAGE -> SPHINX_LANGUAGE -> "en".

    Covers all four combinations of the two env vars, asserting on both the
    freshly-loaded module's `language` attribute and a direct call to
    `_resolve_language()`. A final wiring assertion checks that the resolved
    language would reach the compiled PDF's Typst `lang` element -- via
    `derive_typst_lang()`, the SAME conversion helper `typsphinx/writer.py`'s
    `auto_lang` block calls internally.

    CONF-12/D-I (45.1 Plan 03) removed `conf.py`'s own hand-rolled
    `typst_elements["lang"]` reconstruction: the extension itself now
    auto-derives `lang` on this file's explicit `typst_template` route
    (`TemplateEngine.uses_bundled_default_template()` was narrowed to its
    `typst_package` guard alone), so `conf.py` no longer carries a `lang`
    attribute to assert against directly. This wiring assertion is
    re-derived to call `derive_typst_lang()` itself against the resolved
    `module.language` -- proving the seam still holds end-to-end even
    though the conversion now happens inside the extension rather than in
    `conf.py`.
    """
    from typsphinx.template_engine import derive_typst_lang

    # (a) both unset -> "en"
    monkeypatch.delenv("READTHEDOCS_LANGUAGE", raising=False)
    monkeypatch.delenv("SPHINX_LANGUAGE", raising=False)
    module = _load_conf_module()
    assert module.language == "en"
    assert module._resolve_language() == "en"
    assert derive_typst_lang(module.language) == module.language

    # (b) only SPHINX_LANGUAGE set -> that value (existing override keeps working)
    monkeypatch.setenv("SPHINX_LANGUAGE", "ja")
    monkeypatch.delenv("READTHEDOCS_LANGUAGE", raising=False)
    module = _load_conf_module()
    assert module.language == "ja"
    assert module._resolve_language() == "ja"
    assert derive_typst_lang(module.language) == module.language

    # (c) only READTHEDOCS_LANGUAGE set -> that value (RTD's setting is honored)
    monkeypatch.delenv("SPHINX_LANGUAGE", raising=False)
    monkeypatch.setenv("READTHEDOCS_LANGUAGE", "ja")
    module = _load_conf_module()
    assert module.language == "ja"
    assert module._resolve_language() == "ja"
    assert derive_typst_lang(module.language) == module.language

    # (d) both set -> READTHEDOCS_LANGUAGE wins
    monkeypatch.setenv("READTHEDOCS_LANGUAGE", "ja")
    monkeypatch.setenv("SPHINX_LANGUAGE", "fr")
    module = _load_conf_module()
    assert module.language == "ja"
    assert module._resolve_language() == "ja"
    assert derive_typst_lang(module.language) == module.language
