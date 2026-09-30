# Stack Research

**Domain:** Sphinx→Typst translator bugfix + PyPI release (v0.9.2, a narrow blocker-fix-and-ship milestone)
**Researched:** 2026-08-30
**Confidence:** HIGH

## Headline Verdict

**Add nothing.** No new runtime dependency, no new dev dependency, no new test framework, no
`@preview` package version bump. The one required "stack" action is invoking the test tooling
already in the repo (`typst-py`'s `typst.compile()`, driven through `sphinx-build -b typstpdf`, in
a new `tests/test_*_render_gate.py` + `tests/fixtures/*_gate/` pair) in the same shape as three
existing gates. Everything else in this milestone is bumping ONE version literal
(`pyproject.toml`'s `version = "0.9.0"`) and writing a CHANGELOG section — no library research
applies to that at all.

## 1. Test-side: the real-compile gate idiom to copy

The repo already has 100+ `test_*_render_gate.py` modules; three are close enough to the image
separator defect that a new gate should copy their structure directly rather than invent a new
shape.

### Closest precedent — copy this one

**`/home/yuta/Documents/typsphinx/tests/test_paragraph_concat_render_gate.py`** paired with
**`/home/yuta/Documents/typsphinx/tests/fixtures/paragraph_concat_render_gate/`**

This is the same defect *class* as the image-separator bug: a missing separator between two
juxtaposed Typst code-mode expressions inside the unified code-mode block, verified as a false
negative in `visit_paragraph`/`depart_paragraph`'s early-return branches, fixed by making the
right emitter call `add_text("\n")`/`parbreak()` under the same `list_item_needs_separator`
condition the image fix will reuse. Its idiom:

- `TYPST_AVAILABLE` try/except import guard (`import typst`) → `@pytest.mark.skipif(not
  TYPST_AVAILABLE, ...)` on the test class. No `pypdf` needed for a structural + magic-bytes gate.
- `_run_sphinx_build_typstpdf(source_dir, build_dir)` helper — a `subprocess.run([sys.executable,
  "-m", "sphinx", "-b", "typstpdf", ...])` call, invoked as `sys.executable -m sphinx` (never `uv
  run sphinx-build`, never a resolved binary on PATH) to dodge the NixOS PATH-shadowing hazard.
  **Every gate module carries its own copy of this helper — do not import a sibling module's.**
- Two fixtures: `..._render_gate_dir` (returns `Path(__file__).parent / "fixtures" /
  "paragraph_concat_render_gate"`) and `temp_build_dir(tmp_path)` (returns `tmp_path / "_build"`).
- Asserts, in order: `result.returncode == 0`; `"Typst compilation failed" not in result.stderr`
  (a fatal inside `TypstPDFBuilder.finish()` is *logged*, not raised, so returncode alone is not
  proof); a structural string assert on `index.typ` (here: `"parbreak()" in typ_text`, with an
  index-ordering check that the separator sits *between* the two paragraphs, not merely anywhere in
  the file); then `index.pdf`/`master.pdf` exists, is non-empty, and starts with the `%PDF` magic
  bytes.

### Second precedent — copy its multi-shape-in-one-fixture structure

**`/home/yuta/Documents/typsphinx/tests/test_abbr_pep_separator_render_gate.py`** paired with
**`/home/yuta/Documents/typsphinx/tests/fixtures/abbr_pep_separator_render_gate/`**

Use this one for the *fixture layout*, not the assertion content: it packs a suppressed-behavior
case and a must-still-work regression case into the SAME `index.rst`/`conf.py` fixture pair, so the
"fails pre-fix" and "must keep passing" shapes can never drift apart from each other. The image
gate needs exactly this: the todo's trigger matrix has **four failing shapes** (substitution image
mid-sentence, two images in a row, an image inside a list item, an image preceded by any sibling
content) and **two shapes that must keep passing** (image first in its paragraph, image inside
`.. figure::`) — one fixture document exercising all six, one compile, structural asserts per shape
plus one shared PDF-produced assert, mirrors this module's `abbr_pep_separator_render_gate/
index.rst` combining the auto-generated-separator case with a genuine `:abbr:` regression case.
Its `conf.py` also documents the fixture-naming convention worth reusing verbatim: `typst_documents
= [("index", "master.typ", "<Title>", "Test Author")]` — index must be a *master* document (not
merely included), because only a master gets the full template applied by `TypstWriter.translate()`
(`writer.py`); a bare `"index"` target would collide with the unconditional docname-derived content
file `index.typ`, so a de-collided target name like `master.typ` is the convention every existing
fixture in this suite already follows.

### Third precedent — cited in the question, correctly heavier than needed here

**`/home/yuta/Documents/typsphinx/tests/test_windows_image_uri_render_gate.py`** paired with
**`/home/yuta/Documents/typsphinx/tests/fixtures/windows_shaped_image_uri_gate/`**

Also a real image-related compile gate, and also builds a `_assert_..._escaped_and_separator_free`
shared helper reused by two test classes — but its second class needs a **measured runtime
filesystem probe** (`pytest.skip` if the OS cannot hold a backslash+quote basename) because ITS
defect is platform-shaped (Windows path escaping). The image-separator defect is not
platform-shaped — it reproduces identically on every OS the todo measured it on — so this module's
extra skip-probing machinery is not needed for the new gate. Name it as evidence the pattern exists
in-repo, but do not copy its runtime-probe skip logic.

### What is NOT missing

`typst-py` (already a runtime dependency, `pyproject.toml`: `typst>=0.15.0,<0.16`) is the same
package these three existing gates already import and call through `TypstPDFBuilder.finish()` (via
`sphinx-build -b typstpdf`) — no separate "call `typst.compile()` directly" pattern needs
introducing; all three precedent gates go through the builder, not a bare `typst.compile()` call,
and that is the right idiom to copy since it also exercises the code path the bug actually breaks
(`ExtensionError` raised by `TypstPDFBuilder.finish()`, not a raw compiler exception). `pypdf` is
only needed if a gate wants extracted-*text* assertions (as `test_abbr_pep_separator_render_gate.py`
does for its second test); the image-separator gate's needs (compile succeeds + PDF magic bytes +
structural `.typ` string checks) do not require it, so `pypdf` is optional for this gate, not
missing.

**Verdict: the existing tooling suffices. Add zero test dependencies, zero test frameworks.**

## 2. Version currency — verified against live sources 2026-08-30

| Dependency | Pinned in this repo | Resolved in `uv.lock` | Current released version (verified) | Verdict |
|---|---|---|---|---|
| `typst` (typst-py, PyPI) | `pyproject.toml:11` `typst>=0.15.0,<0.16` | `uv.lock:1533` `version = "0.15.0"` | **0.15.0** (PyPI JSON API, `pypi.org/pypi/typst/json`, `info.version`) | **IRRELEVANT** — pinned version already equals PyPI's current release; no newer 0.15.x/0.16 exists to bump to. |
| `sphinx` | `pyproject.toml:24` `sphinx>=9.1,<10` | `uv.lock:1266` `version = "9.1.0"` | **9.1.0** (PyPI JSON API, `pypi.org/pypi/sphinx/json`) | **IRRELEVANT** — already current. |
| `docutils` | `pyproject.toml:25` `docutils>=0.21,<0.23` | `uv.lock:407` `version = "0.22.4"` | **0.23** exists on PyPI (PyPI JSON API, `pypi.org/pypi/docutils/json`) but is excluded by this repo's own `<0.23` upper bound | **MERELY AVAILABLE, and out of scope.** Relaxing `<0.23` → `<0.24` (or similar) is a real option that exists, but it is an ecosystem-currency change unrelated to the image-separator blocker or the release mechanics, and `CLAUDE.md`'s pinned filterwarnings comment ("No third-party ignore:: entries needed as of ... docutils 0.22.4") documents that the current pin was verified deliberately — do not touch it in this milestone. |
| `@preview/codly` | `templates/base.typ:8`, `template_engine.py:706`, `writer.py:266` — all `1.3.0` | n/a (Typst package, not a Python dep) | **1.3.0** (typst.app/universe/package/codly, fetched live) | **IRRELEVANT** — already the latest published version. |
| `@preview/codly-languages` | same three files — all `0.1.10` | n/a | **0.1.10** (typst.app/universe/package/codly-languages, fetched live) | **IRRELEVANT** — already latest. |
| `@preview/mitex` | same three files — all `0.2.7` | n/a | **0.2.7** (typst.app/universe/package/mitex, fetched live) | **IRRELEVANT** — already latest. |
| `@preview/gentle-clues` | same three files — all `1.3.1` | n/a | **1.3.1** (typst.app/universe/package/gentle-clues, fetched live) | **IRRELEVANT** — already latest. |

**No REQUIRED bump exists anywhere in this table.** All four `@preview` packages are already at
their current Typst Universe release, `typst`/`sphinx` are already at their current PyPI release
within their pinned ranges, and `docutils`'s available-but-unpinned `0.23` is an unrelated,
out-of-scope ecosystem question. This confirms the milestone's own stated default ("do not bump")
is correct — nothing in the stack would break the release, and nothing in the stack needs touching
to make the release succeed.

Since all four `@preview` versions are unchanged, `tests/test_preview_version_sync.py`'s
three-way lockstep assertion (`writer.py` / `template_engine.py` / `templates/base.typ`) needs no
action this milestone — it is already green and stays green.

## 3. Release tooling — exact files, exact literals, exact lockstep

### Files carrying the version literal (must move in lockstep for 0.9.0 → 0.9.2)

| File | Line | Current literal | Action |
|---|---|---|---|
| `pyproject.toml` | `7` | `version = "0.9.0"` | Edit to `"0.9.2"` — this is the **sole hand-edited source of truth** per PROJECT.md's own D-08/carry-forward wording. |
| `uv.lock` | `1467` | `version = "0.9.0"` (under the `name = "typsphinx"`, `source = { editable = "." }` entry) | **Not hand-edited** — regenerate via `uv lock` (or `uv sync --extra dev`) after the `pyproject.toml` edit, so this stays a lockfile-managed derivative, not a second hand-maintained literal. |
| `README.md` | `347` | `**Status**: Stable (v0.9.0) - Production ready` | Edit to `v0.9.2`. This is the only literal version string in `README.md` — the PyPI/Python-version badges above it (lines 4–8) are dynamic shields.io badges with no literal to edit, and line 348 (`**Python**: 3.12+ \| **Sphinx**: 9.1+ \| **Typst**: 0.15+`) is a range statement unaffected by this bump. |
| `CHANGELOG.md` | new `## [0.9.2]` heading + tail reference-link block | see below | Curate content; no other file needs a version-string literal for this bump (there is no `__version__.py`, no `docs/conf.py` version pin found — Sphinx's own docs build reads `release`/`version` from the installed package, not a separate literal). |

No other file in the repo carries a `0.9.0`-shaped literal that gates this release: `docs/`
version fields are computed from the installed package, not a checked-in literal (confirmed by
`README.md:176`'s `'release': 'version'` mapping comment referring to the *translator's*
document-metadata mapping, unrelated to the package's own version).

### What `scripts/extract_changelog_section.py` requires of the heading format

- The extraction is **purely positional**, matched by `_SECTION_HEADER_RE = re.compile(r"^## \[(?P<version>[^\]]+)\]")`:
  find the first line whose heading names the requested version string exactly (no `v` prefix,
  e.g. `"0.9.2"` not `"v0.9.2"` — `release.yml` already strips the `v` before calling the script),
  then take every line up to (but not including) the *next* `## [...]`-shaped heading of any name,
  or end of file.
- It does **not** special-case the string `"Unreleased"` — deliberately, per its own module
  docstring, because `CHANGELOG.md` already carries a second, unrelated `## [Unreleased]` heading
  deep in a "Planned for Future Releases" scratch block. Any two same-named headings are handled
  the same way: whichever occurs first wins, terminated by whichever `## [...]` line comes next.
- It raises `RuntimeError` (exit 1, message on stderr) if no heading matches, or if the matched
  body is empty after stripping — both cases `release.yml`'s `validate` job treats as a hard
  failure *before* `build`/`publish-pypi`/`create-release` run (the "Verify CHANGELOG has a section
  for this version" step), so an incomplete `## [0.9.2]` entry blocks the tag from publishing
  rather than publishing with an empty GitHub Release body.

### What "v0.9.1 was never released" implies for the extractor and the tail link block

Today `CHANGELOG.md`'s top has ONE `## [Unreleased]` heading holding the PATH-01, IMG-04..07, and
MSG-02..05 bullets (v0.9.1's completed-but-unreleased work), immediately followed by a `###
Planned for Future Releases` sub-block (an unrelated, persistent scratch list: BibTeX, Glossary,
Index generation, pre-commit hooks, template integration — none of these are release notes for any
version), then `## [0.9.0] - 2026-08-17`.

Per the milestone context, **no `## [0.9.1]` heading is ever created.** The correct edit is:

1. Rename the current `## [Unreleased]` heading to `## [0.9.2] - <release date>`, folding in this
   milestone's own image-separator fix as an additional `### Fixed` bullet alongside the carried
   PATH-01/IMG-04..07/MSG-02..05 bullets.
2. **Extract the `### Planned for Future Releases` sub-block out from under that heading first** —
   it must not become part of the `## [0.9.2]` section body, because
   `extract_section()`'s positional algorithm would otherwise include it verbatim in the GitHub
   Release body (it has no heading of its own to stop at until the next `## [...]` line, which
   today is `## [0.9.0]` — so as currently nested, the scratch block IS inside the "Unreleased"
   section and WOULD be captured if that heading were simply renamed in place without relocating
   the sub-block). The scratch content needs to persist somewhere (it is not versioned work); the
   simplest correct shape is a **fresh, empty `## [Unreleased]` heading placed above the new `##
   [0.9.2]` heading**, with the `### Planned for Future Releases` sub-block moved under that new
   empty `## [Unreleased]` heading instead of remaining under `## [0.9.2]`. This also restores the
   normal Keep-a-Changelog convention (an `## [Unreleased]` heading always exists at the top,
   ready to receive the next round's bullets) that the v0.9.1-was-never-released situation had
   temporarily broken.
3. At the tail reference-link block (currently ending
   `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD`), add a new line
   `[0.9.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.2` positioned above the
   existing `[0.9.0]: .../releases/tag/v0.9.0` line (newest-first, matching every existing entry's
   ordering), and advance the `[Unreleased]` compare link's base ref from `v0.9.0` to `v0.9.2`:
   `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD`. No `[0.9.1]`
   link is ever added, matching the "no `## [0.9.1]` heading" rule.

### `release.yml` mechanics that apply unchanged (no workflow edit needed)

`release.yml`'s `validate` job resolves `TAG_VERSION` from the pushed tag (`v0.9.2` → `0.9.2`),
compares it string-for-string against `pyproject.toml`'s `project.version` (so the `pyproject.toml`
edit above is what this check reads), then calls `extract_changelog_section.py "$VERSION"` to gate
on the `## [0.9.2]` section existing and being non-empty — all before `build`/`publish-pypi` run.
The `create-release` job later calls the same script to build the GitHub Release body. Per
PROJECT.md's own binding constraint #6, this job's `uv`-on-PATH step previously failed on the
v0.7.0 tag push (`uv: command not found`, since fixed) and has been green at v0.8.0/v0.9.0 — a real
tag push exercises it again, so a failure here is an in-scope release-prep problem, not a stack
question; no code or dependency change is indicated by this research.

## 4. What NOT to add — explicit out-of-scope list

| Tempting addition | Why it is out of scope for v0.9.2 | What to do instead |
|---|---|---|
| A new test framework, mocking library, or snapshot-testing tool for the regression gate | The existing `subprocess.run([sys.executable, "-m", "sphinx", ...])` + `typst-py`-via-builder idiom, already used by 100+ gates in this suite, fully covers "assert on a real compile" — introducing anything else (e.g. `pytest-subprocess`, a Typst-specific test harness) would be a second, divergent idiom for no capability gain. | Copy `test_paragraph_concat_render_gate.py` + `test_abbr_pep_separator_render_gate.py`'s structure exactly (Section 1 above). |
| Bumping `typst`, `sphinx`, or the four `@preview` packages | All five are already at their current released version (Section 2) — a bump literal would not change what gets installed, it would only be a no-op edit that risks a version-sync test false alarm. | Leave `pyproject.toml`, `writer.py`, `template_engine.py`, `templates/base.typ` byte-identical on these lines. |
| Relaxing the `docutils<0.23` upper bound to admit `docutils==0.23` | `docutils` 0.23 exists but this repo's own `filterwarnings` comment in `pyproject.toml` documents that the current `0.22.4`-resolving pin was deliberately verified against `error::DeprecationWarning`/`error::PendingDeprecationWarning`; admitting an unverified newer `docutils` is an ecosystem-currency change with its own research burden, unrelated to the image blocker or the release mechanics. | Leave the pin as `>=0.21,<0.23`; file it as a future-milestone research item if desired, not this one. |
| A new `numref`/per-master-divergence fix, a `templates_path` fix (WR-02), the tripled-warning fix (54.1 WR-01), a `linkcheck` CI job, the `UP006`/`UP035` typing modernization, or `ruff`-on-NixOS work | PROJECT.md's own "Not scoped into v0.9.2" list names every one of these explicitly as carried-forward-unchanged. None of them touch the image-separator defect or the publish path. | Leave untouched; they remain filed as pending todos for a future milestone. |
| Creating a `## [0.9.1]` CHANGELOG heading, or a `v0.9.1` git tag/PyPI release | v0.9.1 was never published — its work is absorbed into `## [0.9.2]` directly (Section 3). Creating a retroactive `0.9.1` artifact would misrepresent what was actually shipped and complicate the tail reference-link block for no reason. | Fold v0.9.1's bullets into the `## [0.9.2]` entry; add only a `[0.9.2]` link, never a `[0.9.1]` one. |
| A second, independent implementation of changelog-section extraction (e.g. a new script, or reading `CHANGELOG.md` a different way inside a new test) | `scripts/extract_changelog_section.py` is explicitly documented (D-06 in its own module docstring) as the ONE committed, pytest-covered implementation, consumed by both `release.yml` jobs via subprocess — a second implementation risks silent divergence from what CI actually runs. | Reuse the existing script as-is; if a test needs to check the new `## [0.9.2]` section, drive it the same way `tests/test_changelog_extraction.py` already does (subprocess, not import). |
| Auditing the other thirteen inline constructs the todo already swept (`:ref:`, inline literal, emphasis, `:abbr:`, `:kbd:`, `:manpage:`, citation reference, `:term:`, `:index:`, `:guilabel:`, external link, footnote reference, `:math:`, `:download:`) for the same class of bug | PROJECT.md's binding constraint #2 states this sweep was already measured and found exactly one unseparated site (the image); footnote, math, and download already emit a leading separator. Re-auditing them is scope creep on a "single site, not a class" fix. | Fix only `visit_image()`; do not touch the other fourteen visitor pairs. |

## Sources

- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` (`## Current Milestone: v0.9.2` section) — HIGH confidence, primary project record.
- `/home/yuta/Documents/typsphinx/.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` — HIGH confidence, measured reproduction with trigger matrix.
- `/home/yuta/Documents/typsphinx/pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`, `.github/workflows/release.yml`, `scripts/extract_changelog_section.py` — HIGH confidence, read directly from the working tree at HEAD, 2026-08-30.
- `/home/yuta/Documents/typsphinx/typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `typsphinx/translator.py` — HIGH confidence, read directly, line numbers verified by direct `grep -n`/`sed -n` against the working tree.
- `/home/yuta/Documents/typsphinx/tests/test_paragraph_concat_render_gate.py`, `test_abbr_pep_separator_render_gate.py`, `test_windows_image_uri_render_gate.py` and their `tests/fixtures/*` pairs — HIGH confidence, read directly.
- PyPI JSON API (`https://pypi.org/pypi/typst/json`, `.../sphinx/json`, `.../docutils/json`) — HIGH confidence, live official package-index source, fetched 2026-08-30.
- `https://typst.app/universe/package/codly`, `.../codly-languages`, `.../mitex`, `.../gentle-clues` — HIGH confidence, live official Typst Universe package pages, fetched 2026-08-30.

---
*Stack research for: typsphinx v0.9.2 (inline-image blocker fix + PyPI release)*
*Researched: 2026-08-30*
</content>
