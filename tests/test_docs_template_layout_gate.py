"""
Executable repo-wide-grep assertion for WR-01/SC#2: no page under ``docs/source/``,
no line of ``README.md``, and no file under ``examples/`` may recommend putting a
Typst template inside Sphinx's own Jinja ``templates_path`` directory
(``_templates/``).

This is a *presence* check, not a cross-site *agreement* check like
``test_preview_version_sync.py`` (which asserts multiple declaration sites agree
with each other). This module instead asks: does ANY file in the policed scope
recommend the discouraged ``_templates/`` layout for a Typst template?

Policed scope (D-12): exactly ``docs/source/``, ``README.md``, and ``examples/``.
``tests/`` and ``tests/fixtures/`` are deliberately NOT policed -- a repo-wide scan
measured that zero files under ``tests/`` set both a Sphinx ``templates_path``
value and a Typst ``typst_template`` value, so none of them trips the runtime
``templates_path`` collision refusal this phase's sibling plans add, and D-12
records that measurement as the basis for the exclusion.

Discovery is a run-time ``rglob()`` over the three policed roots, never a
hardcoded file list, so a page added to the policed scope after this phase lands
is automatically covered (milestone invariant #11).

Line-scoped exemption rule (Test 2): a surviving mention of the bare
``_templates`` token is legitimate ONLY when the same line also names Sphinx's
own ``templates_path`` config value -- i.e. it is explaining Sphinx's own
directory, not recommending a Typst template location. This forces any page that
keeps ``_templates`` in a tree diagram or explanatory sentence to say what it is
for.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# D-12: exactly these three roots are policed. Do not add "tests" here.
POLICED_ROOTS = [
    REPO_ROOT / "docs" / "source",
    REPO_ROOT / "README.md",
    REPO_ROOT / "examples",
]

_POLICED_SUFFIXES = {".rst", ".md", ".py", ".typ", ".txt"}
_SKIP_PARTS = {"__pycache__", "_build"}

# Matches a Typst-template configuration assignment (the config name, optional
# whitespace, "=", optional whitespace, an opening quote) immediately followed
# by the Sphinx Jinja directory name and a forward slash -- i.e. a config value
# that points a Typst template INSIDE `_templates/`.
TYPST_TEMPLATE_IN_JINJA_DIR_RE = re.compile(r"typst_template\s*=\s*['\"]_templates/")

# Matches the bare Sphinx Jinja directory token, word-bounded, anywhere in a
# line.
UNEXPLAINED_JINJA_DIR_RE = re.compile(r"\b_templates\b")

# Matches Sphinx's own `templates_path` config name -- the ONLY thing that
# makes a surviving `_templates` mention legitimate (Test 2's line-scoped
# rule).
LEGITIMATE_SPHINX_CONFIG_RE = re.compile(r"templates_path")


def _discover_policed_files():
    """Discover every policed file at run time -- never a hardcoded list.

    Iterates POLICED_ROOTS; a root that is itself a file (``README.md``) is
    yielded directly if it matches the suffix filter, a root that is a
    directory is walked with ``rglob("*")``.
    """
    files = []
    for root in POLICED_ROOTS:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else root.rglob("*")
        for path in candidates:
            if not path.is_file():
                continue
            if path.suffix not in _POLICED_SUFFIXES:
                continue
            if _SKIP_PARTS & set(path.parts):
                continue
            files.append(path)
    return sorted(files)


def test_no_typst_template_assignment_inside_jinja_dir():
    """Test 1 (narrow, assignment-shaped): no policed file assigns a Typst
    template configuration value that begins with the Sphinx Jinja directory
    name followed by a path separator."""
    offenders = []
    for path in _discover_policed_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if TYPST_TEMPLATE_IN_JINJA_DIR_RE.search(line):
                offenders.append(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}"
                )

    assert not offenders, (
        "found a Typst-template configuration assignment pointing inside "
        "Sphinx's own templates_path directory (`_templates/`) -- move the "
        "template to a Typst-owned directory (`_typst/`) instead:\n"
        + "\n".join(offenders)
    )


def test_every_surviving_jinja_dir_mention_names_templates_path():
    """Test 2 (broad, line-scoped): every surviving occurrence of the Sphinx
    Jinja directory token in the policed scope sits on a line that ALSO names
    Sphinx's own `templates_path` config value -- i.e. it is explaining
    Sphinx's directory, not recommending a Typst template location."""
    offenders = []
    for path in _discover_policed_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if UNEXPLAINED_JINJA_DIR_RE.search(
                line
            ) and not LEGITIMATE_SPHINX_CONFIG_RE.search(line):
                offenders.append(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}"
                )

    assert not offenders, (
        "found a mention of Sphinx's Jinja directory (`_templates`) that does "
        "not identify itself as Sphinx's own templates_path config value on "
        "the same line -- either annotate the line with `templates_path`, or "
        "if it is recommending a Typst template location, move it to "
        "`_typst/`:\n" + "\n".join(offenders)
    )


def test_patterns_have_teeth():
    """Test 3 (control / fail-first): both patterns are asserted to match a
    synthetic known-violating string and NOT match a synthetic known-clean
    string, so this gate can never silently become vacuous. Exercises inline
    synthetic strings only -- never reads a repository file -- so it stays
    green both before and after the documentation change."""
    violating_assignment = 'typst_template = "_templates/custom.typ"'
    clean_assignment = 'typst_template = "_typst/custom.typ"'
    assert TYPST_TEMPLATE_IN_JINJA_DIR_RE.search(violating_assignment)
    assert not TYPST_TEMPLATE_IN_JINJA_DIR_RE.search(clean_assignment)

    violating_bare_mention = "    |-- _templates/             # some directory"
    clean_bare_mention = "    |-- _typst/                  # some directory"
    assert UNEXPLAINED_JINJA_DIR_RE.search(violating_bare_mention)
    assert not UNEXPLAINED_JINJA_DIR_RE.search(clean_bare_mention)

    annotated_mention = (
        'templates_path = ["_templates"]  # Sphinx Jinja override directory'
    )
    assert UNEXPLAINED_JINJA_DIR_RE.search(annotated_mention)
    assert LEGITIMATE_SPHINX_CONFIG_RE.search(annotated_mention)
