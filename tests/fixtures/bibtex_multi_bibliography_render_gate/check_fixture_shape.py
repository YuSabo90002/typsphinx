"""Standalone self-check for the bibtex multi-bibliography fixture (M001/S04, T01).

Run it with ``python``, NOT pytest::

    env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run python \
        tests/fixtures/bibtex_multi_bibliography_render_gate/check_fixture_shape.py

It exists so T01 has a pipe-free, substitution-free verification command.
T02's real pytest gate supersedes it as the durable signal; this file stays as
the fixture's own self-check.

What it proves, and why each assertion is here rather than a bare exit-code
check (a sub-second rc=0 is normal for this fixture but is also exactly what a
no-op looks like, so the exit code alone proves nothing):

* build rc 0 under ``-b typst -W`` -- ``-W`` is what catches the measured
  ``:filter:`` syntax trap, where the wrong form still "succeeds" while every
  citing site degrades to ``bibtex.key_not_found``;
* ``index.typ`` holds ``grid(`` exactly TWICE -- the two independent grids
  that are this fixture's whole reason to exist;
* each chapter's own title string appears exactly ONCE, so neither grid
  leaked the other's entry;
* the uncited third entry's title appears ZERO times, per MEM006.

The temp build tree is created and removed by this script.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent


def fail(message: str) -> None:
    """Report a mismatch and exit non-zero."""
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    build = Path(tempfile.mkdtemp(prefix="multi_bib_gate_"))
    try:
        # sys.executable -m sphinx keeps the interpreter the same one that is
        # running this script, so `uv run` resolves typsphinx to the worktree's
        # editable copy rather than any other checkout.
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "typst",
                "-W",
                str(FIXTURE),
                str(build),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(proc.stdout, file=sys.stderr)
            print(proc.stderr, file=sys.stderr)
            fail(f"sphinx-build exited {proc.returncode}, expected 0")

        content = build / "index.typ"
        if not content.is_file():
            fail(f"expected emitted content file {content} to exist")
        typ = content.read_text(encoding="utf-8")

        checks = [
            ("grid(", 2),
            ("A study of things", 1),
            ("Another work entirely", 1),
            ("An intentionally uncited", 0),
        ]
        problems = []
        for needle, expected in checks:
            actual = typ.count(needle)
            if actual != expected:
                problems.append(f"{needle!r}: expected {expected}, got {actual}")
        if problems:
            fail("index.typ shape mismatch -- " + "; ".join(problems))

        # Belt and braces for the filter trap: -W should already have failed
        # the build, but assert the degrade marker is absent from the log too.
        log = proc.stdout + proc.stderr
        if re.search(r"could not find bibtex key", log):
            print(log, file=sys.stderr)
            fail("build log contains a bibtex.key_not_found degrade")

        print(
            "OK: index.typ has 2 grids, 'A study of things' x1, "
            "'Another work entirely' x1, 'An intentionally uncited' x0; "
            "sphinx-build -b typst -W rc=0 with no key_not_found degrade"
        )
    finally:
        shutil.rmtree(build, ignore_errors=True)


if __name__ == "__main__":
    main()
