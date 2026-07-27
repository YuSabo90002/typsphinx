---
phase: 31-published-url-cutover-repo-wide-link-guard
reviewed: 2026-07-27T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - .github/workflows/links.yml
  - README.md
  - docs/source/changelog.rst
  - examples/advanced/README.md
  - examples/basic/README.md
  - examples/basic/index.rst
  - pyproject.toml
  - tests/test_no_stale_github_io_links.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 31: Code Review Report

**Reviewed:** 2026-07-27T00:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the retired-GitHub-Pages -> Read the Docs URL cutover, the new
repo-wide `lychee` link-check workflow, and the new pytest regression guard.
Content correctness was spot-checked over real HTTP: all nine rewritten URLs
in `README.md` (7 deep links + badge + Japanese doc link) return `200`, as
does the `app.readthedocs.org` badge endpoint and the `claude.com` link —
the actual link rewrites are factually correct. No critical/security issues
were found; this is a docs+CI-only change with no user input handling.

The findings below are all about the *guard rails* this phase built, not the
links themselves: the new pytest regression test has a case-sensitivity
blind spot that lets the exact mistake it was built to prevent slip back in
under a very plausible re-introduction path, the new CI workflow's
`--exclude-path` regex arguments are unanchored/unescaped in a way lychee's
own documentation calls out as a common footgun, and the hermetic pytest
guard's coverage is narrower than the "repo-wide" framing of this phase
would suggest (it only locks down `README.md` + `pyproject.toml`, not the
other four files this same phase edited).

## Warnings

### WR-01: Retired-host regression guard is case-sensitive, but the plausible re-introduction path is mixed-case

**File:** `tests/test_no_stale_github_io_links.py:35-37, 87-91`
**Issue:** `_RETIRED_HOST = "yusabo90002.github.io"` and the assertion
`assert _RETIRED_HOST not in text` (line 87) both use a case-sensitive
Python substring check. GitHub Pages hostnames are case-insensitive at the
DNS/HTTP level, and this exact file repeatedly spells the GitHub org name
with its canonical mixed-case capitalization, `YuSabo90002`, in adjacent
`github.com` links (e.g. `README.md:53`, `:279`, `:303`). A future
contributor who copy-pastes one of those `github.com/YuSabo90002/...`
references to reconstruct a GitHub Pages link (the exact regression this
test exists to prevent, per Issue #119) would very plausibly write
`https://YuSabo90002.github.io/typsphinx/` — which still resolves (Pages
hosts are case-insensitive) but silently passes this test because
`"yusabo90002.github.io" not in text` is true for text containing only the
capitalized form. The guard's one job is to catch this exact class of
mistake, and it has a hole sized exactly to the org's own capitalization
convention used elsewhere in the same file.
**Fix:**
```python
assert _RETIRED_HOST not in text.lower(), (
    f"README.md still references the retired documentation host "
    f"({_RETIRED_HOST}) -- Phase 31 rewrote every link to Read the "
    "Docs; see 31-03-SUMMARY.md."
)
```

### WR-02: `--exclude-path` arguments in the link-check workflow are unanchored regex, contrary to lychee's own documented guidance

**File:** `.github/workflows/links.yml:42-44`
**Issue:** lychee's own docs (`https://lychee.cli.rs/recipes/excluding-paths/`)
state `--exclude-path` values "are treated as regular expressions" and give
the worked example that a naive `--exclude-path 'test.md'` "would also
exclude files like `docs/test-md/intro.txt` and `testamd.html`" —
recommending `(^|/)test\.md$` instead to anchor the match to a real path
boundary. This workflow's three exclude-path arguments repeat that exact
pattern class: `.planning` has an unescaped `.` (a regex metacharacter,
matches any character, not just the literal dot that starts the directory
name) and no anchor, and `tests/fixtures` has no anchor either — a bare
substring match anywhere in the (possibly absolute) scanned path. None of
this misfires today given the current repo layout, but it is exactly the
footgun lychee's own docs warn about, and a future file whose name happens
to overlap the unanchored pattern (e.g. anything containing `Xplanning`,
or a nested `vendor/.../tests/fixtures/...` path someone didn't intend to
exclude) would be silently skipped from the link check with no signal that
it happened.
**Fix:**
```yaml
--exclude-path '(^|/)\.planning(/|$)'
--exclude-path '(^|/)CHANGELOG\.md$'
--exclude-path '(^|/)tests/fixtures(/|$)'
```

### WR-03: Hermetic pytest guard covers only 2 of the 6 files this phase rewrote — the rest rely solely on the non-blocking advisory workflow

**File:** `tests/test_no_stale_github_io_links.py:1-18`
**Issue:** The module's own docstring frames its purpose as locking "the
rewrite" behind "hermetic invariants so a future edit... fails a `pytest`
run immediately instead of silently regressing a second time" — but its
scope (by design, per the docstring) is only `README.md` and
`pyproject.toml`. This same phase also rewrote broken `your-repo` GitHub
placeholder links in `examples/basic/README.md`, `examples/advanced/README.md`,
and `examples/basic/index.rst`, and removed a dead GitHub Projects link
from `docs/source/changelog.rst`. None of those four files have a pytest
guard. A regression in any of them (e.g. someone reverts
`YuSabo90002` back to the `your-repo` placeholder while editing an example)
would only be caught by the repo-wide `lychee` workflow added in this same
phase — which is explicitly advisory/non-required (per `links.yml`'s own
header comment, "a red or cancelled run never blocks a merge"), so it can
be ignored or go unnoticed indefinitely. Given the phase name is
"published-url-cutover-**repo-wide**-link-guard," the hermetic (blocking)
half of that guard covers a narrower surface than the phase's own framing
implies.
**Fix:** Either extend `test_no_stale_github_io_links.py` (or add a
sibling test) to assert the retired host is absent from
`examples/**/README.md`, `examples/basic/index.rst`, and
`docs/source/changelog.rst` too, or narrow the phase/test docstring's
claims to explicitly note that only README.md/pyproject.toml are
hermetically guarded and the example files rely on the advisory workflow
by design.

## Info

### IN-01: README's Japanese documentation link is untested by any of the four regression tests

**File:** `README.md:269`, `tests/test_no_stale_github_io_links.py:94-139`
**Issue:** `https://typsphinx.readthedocs.io/ja/latest/` matches
`_READTHEDOCS_URL_RE` (so it is implicitly covered by the "no retired host"
assertion) but is excluded from both `test_readme_deep_links_carry_language_version_prefix`
(which only matches `/en/latest/...`) and
`test_readme_top_level_links_carry_no_version_segment` (which excludes any
URL containing a language segment, and `/ja/` is a language segment). No
test asserts this specific URL's path shape, so a future edit that
mis-spells or mis-paths the Japanese link (e.g. drops `/latest/`, or typos
the language code) would pass all four existing tests.
**Fix:** Add a targeted assertion, e.g.
`assert "https://typsphinx.readthedocs.io/ja/latest/" in text`, or fold it
into the deep-link test as a second expected-URL set.

### IN-02: Deep-link regression test matches the whole README, not just the "## Documentation" section it's meant to guard

**File:** `tests/test_no_stale_github_io_links.py:94-110`
**Issue:** `test_readme_deep_links_carry_language_version_prefix` calls
`_DEEP_LINK_RE.findall(text)` against the full file text rather than
scoping to the "## Documentation" section the test's own docstring
describes ("README.md must have exactly 7 `/en/latest/` deep links, in
order"). It currently works because no other part of `README.md` happens
to contain an `/en/latest/...` URL, but that's an implicit, unenforced
assumption rather than something the test structurally guarantees — a
future edit that adds an unrelated `/en/latest/...` link elsewhere in the
file (e.g. in a changelog blurb or acknowledgments entry) would silently
shift the count/order assertion's target list without anyone intending to
touch the Documentation section's quick links.
**Fix:** Slice `text` to the `## Documentation` section (e.g. split on the
heading and take everything up to the next `## `) before running
`_DEEP_LINK_RE.findall` against it.

---

_Reviewed: 2026-07-27T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
