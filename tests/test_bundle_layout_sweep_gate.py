"""
Phase 56 Plan 05 -- D-10 / SC#4: a never-skipping, run-time, repo-wide presence
gate proving no page in the policed documentation set claims a root-level
shared template file (the ``_template.typ`` artifact Phase 54 deleted) or
names the deleted ``_write_template_file()`` builder method.

Policed scope (54.1 D-12, unchanged by this plan): exactly ``docs/source/``,
``README.md``, and ``examples/``. ``tests/`` is deliberately NOT policed --
every occurrence under ``tests/`` is either a regression assertion that the
reserved-basename artifact is GONE, or a fixture/docstring deliberately
exercising the reserved-basename edge case for a collision/reservation gate
(56-SWEEP-DISPOSITION.md's per-hit disposition table records this measurement
in full). Historical release notes (``docs/source/changelog.rst``,
``CHANGELOG.md``) are excluded WITH their reason recorded below, never
silently skipped -- they describe what was true at the version they document,
and rewriting them would falsify the record. ``CHANGELOG.md`` itself sits
outside the three policed roots entirely and is not walked by this module at
all, for the same reason.

D-10's failure mode this gate exists to prevent: a written floor (the hit
list recorded during context-gathering or planning) gets mistaken for the
search set. Discovery here is a run-time ``rglob()`` over the three policed
roots -- never a hardcoded file list -- so a page added to the policed scope
after this phase lands is automatically covered (milestone invariant #11),
and 56-05's own execution-time re-run already found one hit beyond the
floor (``examples/charged-ieee/approach1/conf.py``, see the disposition
record) that this gate would have caught mechanically had it existed
earlier.

This module reads every policed file as TEXT ONLY and matches it with
compiled ``re`` patterns. It never calls ``exec``, ``eval``,
``compile(..., "exec")``, ``importlib.import_module``, or ``__import__`` on
any swept file -- a swept ``examples/**/conf.py`` can therefore never
execute inside this test process (T-56-13). All three policed roots are
derived at run time from ``Path(__file__).resolve().parent.parent``; no
absolute path literal appears anywhere in this module, and every message
below names paths relative to the repository root (T-56-14).
"""

import re
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent

# 54.1 D-12: exactly these three roots are policed. Do not add "tests" here.
POLICED_ROOTS = [
    REPO_ROOT / "docs" / "source",
    REPO_ROOT / "README.md",
    REPO_ROOT / "examples",
]

# docs/source/ is policed for *.rst and *.md; README.md is the one file
# itself; examples/ is policed for *.md, *.rst, and *.py (conf.py files
# carry documentation-shaped comments this sweep must reach, per D-10's
# examples/charged-ieee/approach2/conf.py hit).
_DOCS_SOURCE_SUFFIXES = {".rst", ".md"}
_EXAMPLES_SUFFIXES = {".md", ".rst", ".py"}
_SKIP_PARTS = {"__pycache__", "_build"}

# Anchored: the character immediately before the match must be a
# start-of-line or a non-alphanumeric character. Without the anchor, a
# LONGER basename that merely ENDS in the same characters -- e.g.
# "custom_template.typ" -- would falsely fire, because plain substring
# matching cannot distinguish "the reserved basename itself" from "a
# different, legitimately-named file whose name happens to end the same
# way". `docs/source/conf.py`'s own `custom_template.typ` and
# `docs/source/changelog.rst`'s `custom_template.typ` mention are exactly
# this false-positive shape, measured during this plan's own discovery
# sweep (56-SWEEP-DISPOSITION.md, disposition rows #2 and #7).
RESERVED_TEMPLATE_BASENAME_RE = re.compile(r"(^|[^A-Za-z0-9])_template\.typ")

# The deleted builder.py method Phase 54 removed when it replaced the
# single-file template writer with the per-key bundle copy
# (_copy_used_template_bundles()). Word-bounded is sufficient here: unlike
# the reserved basename, no other real symbol in this codebase legitimately
# ends in these characters.
DELETED_WRITE_TEMPLATE_FILE_METHOD_RE = re.compile(r"\b_write_template_file\b")

# D-10: a dict mapping a policed path (optionally ":LINENO" for a
# line-scoped exemption) to its written reason. A bare path key excludes
# the WHOLE file from both patterns; a "path:LINENO" key excludes only that
# one line, so a file with other lines worth policing stays policed
# everywhere else -- the same line-scoped-exemption shape
# tests/test_docs_template_layout_gate.py's `templates_path` rule already
# established for this codebase.
EXCLUDED_SWEEP_PATHS: Dict[str, str] = {
    "docs/source/changelog.rst": (
        "Historical release notes describing what was true at the version "
        "they document (the _template.typ-era output layout, at the "
        "versions that shipped it). Rewriting them would falsify the "
        "record; CHANGELOG curation is Phase 57's, not this phase's."
    ),
    "examples/charged-ieee/approach2/conf.py:28": (
        "The typst_template assignment line "
        '(typst_template = "_typst/_template.typ"). This user\'s own '
        "template file legitimately NAMES a basename that coincides with "
        "the former reserved output basename -- it is an INPUT path, not "
        "an output-artifact claim, and Task 1 of this plan explicitly does "
        "not change it (56-SWEEP-DISPOSITION.md disposition row #10)."
    ),
}


def _discover_policed_files() -> List[Path]:
    """Discover every policed file at run time -- never a hardcoded list.

    ``docs/source/`` is walked for ``*.rst``/``*.md``; ``README.md`` is
    yielded directly; ``examples/`` is walked for ``*.md``/``*.rst``/
    ``*.py``. Skips ``__pycache__`` and any ``_build`` output directory.
    """
    files: List[Path] = []
    for root in POLICED_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        if root.name == "source":
            suffixes = _DOCS_SOURCE_SUFFIXES
        else:
            suffixes = _EXAMPLES_SUFFIXES
        for candidate in root.rglob("*"):
            if not candidate.is_file():
                continue
            if candidate.suffix not in suffixes:
                continue
            if _SKIP_PARTS & set(candidate.parts):
                continue
            files.append(candidate)
    return sorted(files)


def _relpath(path: Path) -> str:
    """Repo-root-relative POSIX-style path string, for messages and
    EXCLUDED_SWEEP_PATHS keys -- never an absolute path (T-56-14)."""
    return path.relative_to(REPO_ROOT).as_posix()


def _excluded_lines_for(relpath: str) -> set:
    """The set of 1-indexed line numbers excluded for this file by a
    "path:LINENO" entry in EXCLUDED_SWEEP_PATHS."""
    prefix = f"{relpath}:"
    lines = set()
    for key in EXCLUDED_SWEEP_PATHS:
        if key.startswith(prefix):
            lineno_part = key[len(prefix) :]
            if lineno_part.isdigit():
                lines.add(int(lineno_part))
    return lines


def _find_offenses(pattern: re.Pattern) -> List[str]:
    """Every ``relpath:lineno: line text`` offense the given pattern finds
    across every policed file, honouring EXCLUDED_SWEEP_PATHS (both
    whole-file and line-scoped entries)."""
    offenses = []
    for path in _discover_policed_files():
        relpath = _relpath(path)
        if relpath in EXCLUDED_SWEEP_PATHS:
            continue
        excluded_lines = _excluded_lines_for(relpath)
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if lineno in excluded_lines:
                continue
            if pattern.search(line):
                offenses.append(f"{relpath}:{lineno}: {line.strip()}")
    return offenses


class TestNoStaleBundleLayoutClaimSurvives:
    """The real assertions: discovery is non-empty, every non-excluded
    policed file is clean under both patterns, and every exclusion still
    matches something it claims to exempt (the staleness check)."""

    def test_discovery_is_non_empty(self):
        discovered = _discover_policed_files()
        # A broken root (typo'd path, moved directory) must not make this
        # gate vacuously pass by discovering zero files -- at least twenty
        # is comfortably below this repository's real policed-file count
        # and comfortably above "discovery silently found nothing".
        assert len(discovered) >= 20, (
            f"only discovered {len(discovered)} policed files -- expected "
            "at least 20. A broken POLICED_ROOTS entry would make this "
            "gate pass vacuously; investigate before trusting a green run."
        )

    def test_no_reserved_template_basename_claim_survives(self):
        offenses = _find_offenses(RESERVED_TEMPLATE_BASENAME_RE)
        assert not offenses, (
            "found a claim naming the reserved root-level `_template.typ` "
            "output artifact, which Phase 54 replaced with the per-key "
            "`_template/<key>/` bundle directory -- rewrite to describe "
            "the bundle layout, or add a reasoned exclusion to "
            "EXCLUDED_SWEEP_PATHS if this is a legitimate input path or "
            "historical record:\n" + "\n".join(offenses)
        )

    def test_no_deleted_write_template_file_method_survives(self):
        offenses = _find_offenses(DELETED_WRITE_TEMPLATE_FILE_METHOD_RE)
        assert not offenses, (
            "found a reference to `_write_template_file`, the single-file "
            "template writer Phase 54 deleted -- describe the shipped "
            "`_copy_used_template_bundles()` bundle-copy path instead:\n"
            + "\n".join(offenses)
        )

    def test_every_exclusion_still_matches_something(self):
        """The staleness check: if a correction removes the text an
        exclusion was written to exempt, the exclusion becomes stale and
        must be removed from EXCLUDED_SWEEP_PATHS rather than left as dead
        weight silently exempting nothing."""
        stale = []
        for key in EXCLUDED_SWEEP_PATHS:
            if ":" in key and key.rsplit(":", 1)[1].isdigit():
                relpath, lineno_str = key.rsplit(":", 1)
                lineno = int(lineno_str)
                path = REPO_ROOT / relpath
                if not path.exists():
                    stale.append(f"{key} (file does not exist)")
                    continue
                lines = path.read_text(encoding="utf-8").splitlines()
                if lineno < 1 or lineno > len(lines):
                    stale.append(f"{key} (line does not exist)")
                    continue
                line = lines[lineno - 1]
                if not (
                    RESERVED_TEMPLATE_BASENAME_RE.search(line)
                    or DELETED_WRITE_TEMPLATE_FILE_METHOD_RE.search(line)
                ):
                    stale.append(f"{key} (line no longer matches either pattern)")
            else:
                path = REPO_ROOT / key
                if not path.exists():
                    stale.append(f"{key} (file does not exist)")
                    continue
                text = path.read_text(encoding="utf-8")
                if not (
                    RESERVED_TEMPLATE_BASENAME_RE.search(text)
                    or DELETED_WRITE_TEMPLATE_FILE_METHOD_RE.search(text)
                ):
                    stale.append(f"{key} (file no longer matches either pattern)")

        assert not stale, (
            "EXCLUDED_SWEEP_PATHS entries that no longer exempt anything -- "
            "a stale exclusion. Remove them:\n" + "\n".join(stale)
        )


class TestSweepPatternsHaveTeeth:
    """Control / fail-first tests: both patterns are proven to fire on a
    synthetic known-bad string and NOT fire on a synthetic known-clean
    string, using inline strings only -- never a repository file -- so this
    class stays green both before and after any documentation change and
    can never pass vacuously."""

    def test_reserved_basename_pattern_fires_on_a_direct_claim(self):
        assert RESERVED_TEMPLATE_BASENAME_RE.search(
            "the wrapper imports `_template.typ`"
        )
        assert RESERVED_TEMPLATE_BASENAME_RE.search(
            "written to `_build/typst/_template.typ`"
        )

    def test_reserved_basename_pattern_does_not_fire_on_a_longer_basename(self):
        # The exact false positive the anchor exists to prevent: a longer
        # basename that merely ENDS in the same characters is a different
        # filename, not a hit. Measured against this repository's own
        # docs/source/conf.py (custom_template.typ).
        assert not RESERVED_TEMPLATE_BASENAME_RE.search(
            'typst_template = "_typst/custom_template.typ"'
        )
        assert not RESERVED_TEMPLATE_BASENAME_RE.search(
            "See docs/source/_typst/custom_template.typ for the font list"
        )

    def test_reserved_basename_pattern_fires_at_start_of_line(self):
        # The anchor's "start-of-line" branch: a match at column 0 has no
        # preceding character at all, and must still fire.
        assert RESERVED_TEMPLATE_BASENAME_RE.search("_template.typ")

    def test_deleted_method_pattern_fires_on_a_direct_reference(self):
        assert DELETED_WRITE_TEMPLATE_FILE_METHOD_RE.search(
            "It also writes a shared `_template.typ` file (`_write_template_file`)."
        )

    def test_deleted_method_pattern_does_not_fire_on_the_shipped_method(self):
        assert not DELETED_WRITE_TEMPLATE_FILE_METHOD_RE.search(
            "In `finish()` it calls `_copy_used_template_bundles()`."
        )
