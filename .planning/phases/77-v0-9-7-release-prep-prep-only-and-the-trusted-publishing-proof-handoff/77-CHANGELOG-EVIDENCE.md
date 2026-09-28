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

Only this file, `77-CHANGELOG-EVIDENCE.md`, is staged and committed here, by explicit path.
`CHANGELOG.md` and `tests/test_changelog_page_gate.py` stay uncommitted for Task 3's single
five-file commit.
