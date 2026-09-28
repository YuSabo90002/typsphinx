# Phase 77 — CHANGELOG Evidence (SC#2)

## Base census

From `git show "$B:CHANGELOG.md"` where `B` is `BASE_77_02`
(`3984b231e30fbb76ba156d2f9b2abe475231bccf`):

```
## [Unreleased] body (base):

### Planned for Future Releases
- BibTeX/bibliography support
- Glossary generation
- Index generation
- Pre-commit hooks
- Additional Typst Universe template integration
```

CARRIED_BULLETS_BASE = 0
(count of `^- \*\*` lines in the base `## [Unreleased]` body — zero, so Discretion B's section
shape, settled on the measured zero, holds. No `## HALT` needed.)

BASE_UNRELEASED_SUBSECTIONS = ### Planned for Future Releases

```
grep -cE '^## \[' (base CHANGELOG.md)   -> 24
grep -cE '^\[[^]]+\]: https' (base)     -> 24
```

HEADINGS_BEFORE = 24
LINKREFS_BEFORE = 24

```
grep -c '^### Known Limitations$' (base)   -> 2
```

KNOWN_LIMITATIONS_BEFORE = 2

The `[0.9.6]` section's `### Known Limitations` body (blank lines dropped), SHA-256:

V096_KNOWN_LIMITATIONS_SHA256 = a82c3bb9eaac5744563fe32922d9b9625d01ebf980de626fb2b91df7b4c434ee

## Measurements behind the new section

Quoted from `77-BUMP-EVIDENCE.md`:

PYPROJECT_DEP_TABLES_UNCHANGED = yes
UV_LOCK_PACKAGE_SET_UNCHANGED = yes

```
git diff --name-only v0.9.6 HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
```
prints nothing.

PREVIEW_SITES_UNCHANGED_SINCE_V096 = yes

The four `@preview/<name>:<version>` strings from `typsphinx/templates/base.typ`:

```
@preview/codly-languages:0.1.10
@preview/codly:1.3.0
@preview/gentle-clues:1.3.1
@preview/mitex:0.2.7
```

```
LC_ALL=C uv run pytest tests/test_translator_path_quoting_gate.py -q -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_translator_path_quoting_gate.py ....                          [100%]

============================== 4 passed in 0.03s ===============================
```

MSG06_GATE_EXIT = 0

Quoted from `76-MSG06-EVIDENCE.md`:

MSG06_RED_FAILED = 2
MSG06_RED_TEST_COMMIT = 68065948277abd93488f9686e6d656cf183fe209
(the pre-fix RED reading and the commit it was recorded against — the "recorded RED" claim the
`### Verified` bullet points at.)

`git diff v0.9.6 HEAD -- typsphinx/translator.py`, transcribed:

```diff
diff --git a/typsphinx/translator.py b/typsphinx/translator.py
index 944d5f39..590c21c3 100644
--- a/typsphinx/translator.py
+++ b/typsphinx/translator.py
@@ -15,6 +15,8 @@ from sphinx.locale import admonitionlabels
 from sphinx.util import logging
 from sphinx.util.docutils import SphinxTranslator
 
+from typsphinx.pathfmt import quote_path
+
 logger = logging.getLogger(__name__)
 
 # Units docutils may normalize into `:width:`/`:height:` (via
@@ -5118,7 +5120,7 @@ class TypstTranslator(SphinxTranslator):
 
             logger.debug(
                 f"Cross-directory path calculation: up_count={up_count}, "
-                f"up_path='{up_path}', down_path='{down_path}', "
+                f"up_path={quote_path(up_path)}, down_path={quote_path(down_path)}, "
                 f"result: {relative_path}"
             )
 
@@ -5223,7 +5225,7 @@ class TypstTranslator(SphinxTranslator):
 
             logger.debug(
                 f"Cross-directory path calculation: up_count={up_count}, "
-                f"up_path='{up_path}', down_path='{down_path}', "
+                f"up_path={quote_path(up_path)}, down_path={quote_path(down_path)}, "
                 f"result: {relative_path}"
             )
```

The change is the `quote_path` import plus the two DEBUG-message lines in each of two functions —
the basis for the `### Fixed` bullet's "only DEBUG-level log text is affected" sentence.

## Provenance pointer measurement

Measured live this session (Discretion C — never recalled):

```
curl -s -o "$S/p7702_pip_int.json" -w '%{http_code}' https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance
200
```

POINTER_CONTROL_HTTP = 200

```
jq '.attestation_bundles | length' "$S/p7702_pip_int.json"
1
jq -r '.attestation_bundles[0].publisher.kind' "$S/p7702_pip_int.json"
GitHub
```

POINTER_CONTROL_BUNDLES = 1
POINTER_CONTROL_PUBLISHER_KIND = GitHub

```
curl -s -o "$S/p7702_typsphinx_int.json" -w '%{http_code}' https://pypi.org/integrity/typsphinx/0.9.6/typsphinx-0.9.6-py3-none-any.whl/provenance
404
```

POINTER_NEGATIVE_HTTP = 404
(nothing has been attested for typsphinx yet — the typsphinx 0.9.6 wheel carries no
provenance record, confirming the CHANGELOG's provenance sentence describes 0.9.7's own
publishing mechanism, not a state already observed for a prior release.)

```
curl -s https://pypi.org/project/pip/ -o "$S/p7702_pip_page.html"
wc -c < "$S/p7702_pip_page.html"   -> 3038
grep -io '<title>[^<]*</title>' "$S/p7702_pip_page.html"   -> <title>Client Challenge</title>
grep -c 'Provenance' "$S/p7702_pip_page.html"   -> 0
```

POINTER_PAGE_BYTES = 3038
POINTER_PAGE_IS_CHALLENGE = yes
POINTER_PAGE_HAS_PROVENANCE = no
(the automated `curl` fetch of the pip project page returned PyPI's bot-mitigation
"Client Challenge" interstitial, not the real file page, so the file page's own
"Provenance" wording cannot be measured from this session and is not quoted.)

PROVENANCE_POINTER_BASIS = integrity-api
(the CHANGELOG's one pointer sentence names only PyPI's Integrity API path shape — the
measured, working control reading above — and adds no claim about the file page's UI text,
since that page's wording could not be measured this session.)

## Curate CHANGELOG.md

`## [Unreleased]` left holding only the existing `### Planned for Future Releases` block with its
five items, unchanged (byte-identical to the base body, blank lines aside).

`## [0.9.7] - 2026-09-28` inserted between `## [Unreleased]` and `## [0.9.6]`, carrying, in order:
a short modest-register lead paragraph, `### Changed` (one bold-lead ATT-01/ATT-02 bullet),
`### Fixed` (one bold-lead MSG-06 bullet), `### Known Limitations` (the `[0.9.6]` NUM-01 entry
carried byte-identical) and `### Verified` (three measured invariance bullets).

Tail link block: `[0.9.7]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.7`
inserted immediately above `[0.9.6]`; `[Unreleased]`'s compare re-pointed from `v0.9.6...HEAD` to
`v0.9.7...HEAD`.

## RELEASE_VERSIONS

`"0.9.7",` appended after `"0.9.6",` in `tests/test_changelog_page_gate.py`, same plain-string
style, no reordering. Comment restated as
`# The 18 releases the published page was frozen without (0.4.1 through 0.9.7,`.

Read back with `ast`:

```
uv run --no-sync python -c "
import ast
m = ast.parse(open('tests/test_changelog_page_gate.py').read())
v = [n for n in m.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'RELEASE_VERSIONS'][0]
t = ast.literal_eval(v.value)
print(len(t), t[0], t[-1])
"
18 0.4.1 0.9.7
```

RELEASE_VERSIONS_LEN = 18
RELEASE_VERSIONS_FIRST = 0.4.1
RELEASE_VERSIONS_LAST = 0.9.7
COMMENT_MATCHES_TUPLE = yes
(the comment's count — 18 — and range — 0.4.1 through 0.9.7 — agree with the tuple.)

## New section census

```
NEW_SECTION_SUBSECTIONS (the `^### ` headings inside `## [0.9.7]`, joined):
### Changed|### Fixed|### Known Limitations|### Verified|
```

Bold-lead bullet count per subsection: `### Changed` 1, `### Fixed` 1, `### Known Limitations` 1
(the carried NUM-01 entry); `### Verified` 3 plain `- ` bullets.

```
grep -cE '^## \[' CHANGELOG.md          -> 25
grep -cE '^\[[^]]+\]: https' CHANGELOG.md -> 25
grep -c '^### Known Limitations$' CHANGELOG.md -> 3
```

HEADINGS_AFTER = 25
LINKREFS_AFTER = 25
KNOWN_LIMITATIONS_AFTER = 3

The new `### Known Limitations` body (blank lines dropped) hashes to the same digest as
`V096_KNOWN_LIMITATIONS_SHA256` above (`a82c3bb9…`) — byte-identical to `[0.9.6]`'s.

KNOWN_LIMITATIONS_CARRIED = yes

```
printf '%s\n' "$NEW" | grep -c 'http'   -> 0
```

NEW_SECTION_URL_COUNT = 0
(the section contains no URL at all — the one pointer sentence names PyPI's Integrity API path
shape in inline code with `<project>`/`<version>`/`<filename>` placeholders and no scheme, so it
carries no literal `http` substring.)

Heading line numbers, ascending:

```
## [Unreleased]        -> line 8
## [0.9.7] - 2026-09-28 -> line 17
## [0.9.6] - 2026-09-20 -> line 70
```

RELEASE_HEADING_DATE = 2026-09-28

Moved tail-link lines:

```
[0.9.7]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.7  -> line 1431
[0.9.6]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6  -> line 1432
```

## Zero-skip changelog page gate

```
LC_ALL=C uv run pytest tests/test_changelog_page_gate.py -q -rs -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests/test_changelog_page_gate.py ......                                 [100%]

============================== 6 passed in 4.58s ===============================
```

No `SKIPPED` lines printed.

CHANGELOG_GATE_EXIT = 0
CHANGELOG_GATE_SKIPS = 0

## Commit

Only this file, `77-CHANGELOG-EVIDENCE.md`, was staged and committed here, by explicit path.
`CHANGELOG.md` and `tests/test_changelog_page_gate.py` stayed uncommitted for Task 3's single
five-file commit (landed as `BUMP_COMMIT_SHA` in `77-BUMP-EVIDENCE.md`).

## Extractor transcript

```
uv run python scripts/extract_changelog_section.py 0.9.7 > "$S/p7702_release_notes.md" 2>"$S/p7702_extract.err"; echo "exit:$?"
exit:0
```

EXTRACT_EXIT = 0

```
wc -c < "$S/p7702_release_notes.md"   -> 3132
wc -l < "$S/p7702_release_notes.md"   -> 50
sha256sum < "$S/p7702_release_notes.md"
82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6  -
```

EXTRACT_BYTES = 3132
EXTRACT_LINES = 50
EXTRACT_SHA256 = 82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6

The stdout, verbatim — this is the text that becomes the start of the GitHub Release body:

```
0.9.7 corrects a DEBUG-log quoting defect and changes how this release is published: the
release workflow now uses PyPI Trusted Publishing, which records provenance attestations
for the uploaded files. Neither change alters typsphinx's installed behaviour.

### Changed

- **The release workflow now publishes to PyPI through Trusted Publishing, and the
  publish action attaches PEP 740 attestations to the uploaded wheel and sdist
  (ATT-01, ATT-02).** The publish step now authenticates with a short-lived OIDC token
  instead of a long-lived API token, and each attestation records the GitHub Actions
  workflow that built and published the file. These attestations are audit provenance,
  not an install-time gate: neither `pip` nor `uv` verifies them when installing today,
  so installing typsphinx behaves exactly as before. A reader can inspect a file's
  attestation through PyPI's Integrity API, at the path shape
  `pypi.org/integrity/<project>/<version>/<filename>/provenance`.

### Fixed

- **A path containing a literal single quote no longer closes the quote early in two
  DEBUG-only diagnostic messages (MSG-06).** When typsphinx computes a cross-directory
  relative path for an included document or an image, the two DEBUG log messages that
  record the computed `up_path`/`down_path` values now quote each path with the same
  delimiter-aware quoting used by its other path diagnostics. Only DEBUG-level log text
  is affected; no compiled output changes.

### Known Limitations

- **A multi-master `typst_documents` configuration can produce a diverging or missing `:numref:`
  reference number (NUM-01).** A single-master project is entirely unaffected. When the same
  figure is reachable from two masters, Sphinx bakes one project-wide number into the `:numref:`
  reference text, but each compiled Typst wrapper counts its own captions independently — so the
  reference reads correctly in one master's PDF and points at the wrong number in the other, with
  no diagnostic reporting the mismatch. When a figure is reachable only from a non-root master, it
  never enters Sphinx's root-document figure-numbering scan, so its `:numref:` reference falls
  back to the raw label text instead of a number; Sphinx does emit one warning naming the label,
  so the build log carries a diagnostic even though the compiled PDF gives the reader none.
  **Workaround:** use a single-master `typst_documents` configuration, or replace `:numref:` with
  `:ref:` for the affected figures.

### Verified

- No new runtime dependency and no new dev dependency were added across this milestone's
  diff (`v0.9.6..HEAD`); `pyproject.toml` differs from the `v0.9.6` tag by exactly its
  version line, and `uv.lock`'s package-name set is identical to the tag's.
- The four bundled `@preview` package version strings are unchanged across all three
  declaration sites (`typsphinx/writer.py`, `typsphinx/template_engine.py`,
  `typsphinx/templates/base.typ`).
- MSG-06's fix is bound by a real regression gate
  (`tests/test_translator_path_quoting_gate.py`), recorded failing against the unfixed
  tree before the fix landed.
```

```
grep -c '^### Planned for Future Releases' "$S/p7702_release_notes.md"   -> 0
grep -cE '^## \[' "$S/p7702_release_notes.md"                           -> 0
```

EXTRACT_PLANNED_BLOCK = 0
EXTRACT_VERSION_HEADINGS = 0

The saved stdout, normalised with one trailing newline, hashes identically to the `## [0.9.7]`
section body read straight out of `CHANGELOG.md` with leading and trailing blank lines stripped:

```
SEC digest: 82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6
X   digest: 82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6
```

EXTRACT_MATCHES_SECTION = yes

```
LC_ALL=C uv run pytest tests/test_changelog_extraction.py -q -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests/test_changelog_extraction.py ......                                [100%]

============================== 6 passed in 0.27s ===============================
```

EXTRACTION_TESTS_EXIT = 0
