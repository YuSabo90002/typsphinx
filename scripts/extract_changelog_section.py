"""
Extract a single ``## [X.Y.Z]`` section body from ``CHANGELOG.md`` (REL-04).

Why this exists: ``.github/workflows/release.yml`` never opened
``CHANGELOG.md`` at all -- its ``create-release`` job built the GitHub
Release body from a raw ``git log $PREV_TAG..$TAG --pretty=format:"- %s
(%h)"`` dump, which for v0.6.4 was 296 dump lines inside a 308-line body.
This script replaces that dump: it extracts the curated, human-written
``## [X.Y.Z]`` section for a given released version and prints its body to
stdout, so the release notes are what a maintainer actually wrote in
``CHANGELOG.md``, not an auto-generated commit list.

D-06: this is the ONE committed, pytest-covered implementation of the
extraction. ``release.yml`` calls this exact script from both its
``validate`` job (existence-and-non-emptiness check, D-09 -- run BEFORE
``build``/``publish-pypi``/``create-release`` so a missing section fails
before the PyPI upload, not after it) and its ``create-release`` job (the
release-notes body itself). ``tests/test_changelog_extraction.py`` exercises
this exact script via ``subprocess.run``, never by importing it -- so there
is no second, independently-implemented copy of this logic anywhere that
could silently diverge from what CI actually runs.

The load-bearing gotcha (Pitfall 1, 41-RESEARCH.md): ``CHANGELOG.md`` carries
TWO ``## [Unreleased]`` headings -- one near the top (the standard Keep a
Changelog placeholder) and a second, unrelated one deep in the tail block
("Planned for Future Releases", a scratch area for ideas not yet scheduled).
Do NOT "fix" this by special-casing the string ``"Unreleased"`` anywhere in
this module. The extraction algorithm below is purely POSITIONAL: find the
first line whose ``## [...]`` heading names the requested version, then take
every line up to (but not including) the very next ``## [...]`` heading line,
or end of file. Because the algorithm never inspects heading *names* other
than the one it is searching for, the two identically-named ``[Unreleased]``
headings can never make a numeric version's extraction order-dependent or
leak the tail scratch area's content into an unrelated version's section.

Security note (ASVS V5, T-41-01): the ``version`` argument is used ONLY for
a string-equality comparison against text already parsed out of
``CHANGELOG.md``. It is never interpolated into a shell command, never
``eval``'d, and never used to build a filesystem path -- ``--changelog-path``
is the only path input, and it defaults to this repository's own
``CHANGELOG.md``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

#: One level up from `scripts/` is the repository root.
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"

#: Matches EVERY `## [...]` heading line, including both `## [Unreleased]`
#: headings -- this is deliberate. The extraction algorithm below is purely
#: positional (first match of the requested version, terminated by the next
#: match of this same pattern, whatever its name), never name-based. See the
#: module docstring's "load-bearing gotcha" paragraph.
_SECTION_HEADER_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")


def extract_section(changelog_text: str, version: str) -> str:
    """
    Extract the body of the ``## [<version>]`` section from ``changelog_text``.

    The body is every line after the matching heading line, up to (but not
    including) the next line matching ``_SECTION_HEADER_RE`` -- any heading,
    not only a version-shaped one -- or end of file, with leading and
    trailing blank lines stripped.

    Args:
        changelog_text: The full text of a CHANGELOG.md-shaped file.
        version: The version string to look for, e.g. ``"0.7.0"`` (no
            leading ``v`` and no surrounding brackets).

    Returns:
        The stripped section body. Never an empty string -- see the raises
        clause below.

    Raises:
        RuntimeError: if no ``## [<version>]`` heading is found, or if the
            matched section's body is empty after stripping. Both name the
            requested version explicitly, since two CI jobs (`release.yml`'s
            `validate` and `create-release`) consume this script's stderr as
            their sole diagnostic on failure.
    """
    lines = changelog_text.splitlines()

    start_index: int | None = None
    for index, line in enumerate(lines):
        match = _SECTION_HEADER_RE.match(line)
        if match and match.group("version") == version:
            start_index = index + 1
            break

    if start_index is None:
        raise RuntimeError(
            f"No '## [{version}]' section found in the CHANGELOG. "
            "Add a curated entry for this version before releasing."
        )

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        if _SECTION_HEADER_RE.match(lines[index]):
            end_index = index
            break

    body = "\n".join(lines[start_index:end_index]).strip("\n").strip()

    if not body:
        raise RuntimeError(
            f"The '## [{version}]' section in the CHANGELOG is empty. "
            "Write a release-notes body for this version before releasing."
        )

    return body


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Print the '## [<version>]' section body from CHANGELOG.md to "
            "stdout, for use as a GitHub Release's body (REL-04)."
        )
    )
    parser.add_argument(
        "version", type=str, help="Version to extract, e.g. '0.7.0' (no 'v' prefix)."
    )
    parser.add_argument(
        "--changelog-path",
        type=Path,
        default=DEFAULT_CHANGELOG_PATH,
        help=f"Path to the CHANGELOG file (default: {DEFAULT_CHANGELOG_PATH}).",
    )
    args = parser.parse_args()

    changelog_text = args.changelog_path.read_text(encoding="utf-8")

    try:
        section = extract_section(changelog_text, args.version)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(section)
