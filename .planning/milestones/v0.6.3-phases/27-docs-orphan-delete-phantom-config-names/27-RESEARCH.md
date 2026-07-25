# Phase 27: Docs 実測整合 — Orphan Delete + Phantom Config Names - Research

**Researched:** 2026-07-24
**Domain:** Sphinx docs content fidelity, orphan-file deletion, sphinx-intl/.po follow mechanism
**Confidence:** HIGH

## Summary

This is a docs-content-and-test phase, not a code phase. CONTEXT.md already locked the five
concrete edits (D-01..D-13); this research validates the mechanics the planner needs to turn
those edits into safe, gate-passing tasks, and surfaces **one load-bearing gap CONTEXT.md did
not catch**: `tests/test_documentation_configuration.py` hard-asserts that
`docs/configuration.rst` exists and inspects its content across 11 test functions. Deleting the
orphan without deleting/repointing this test file drops the D-12(d) "full test suite green"
gate to broadly RED. This must be a task in the same wave as the `git rm`.

All other mechanics were verified by actually running the toolchain in this session (not by
reading about it): the `.pot`/`.po` regeneration path (`sphinx-build -b gettext` →
`sphinx-intl update`), the safe-deletion xref proof, a real content diff between the orphan and
the canonical doc, and a baseline `sphinx-build -b html` run to establish the pre-existing
warning count. Every `.po` msgstr in `api/index.po` for the deleted table is empty — no real
Japanese translation exists for that content, so deletion loses zero translator effort, not
"near-zero" — literally zero.

**Primary recommendation:** Scope the `.po` regeneration to only the two affected docs via
`sphinx-build -b gettext source _build/gettext source/api/index.rst
source/user_guide/configuration.rst` (verified this restricts `.pot` output to 4 files:
`api/index`, `index`, `user_guide/configuration`, `user_guide/index` — never touching the other
9 unrelated `.po` files, which carry *pre-existing, unrelated* drift that must not be
silently swept into this phase's diff). Then `sphinx-intl update -p _build/gettext -d locale -l
ja` and commit only `api/index.po` + `user_guide/configuration.po`. Delete
`tests/test_documentation_configuration.py` alongside `docs/configuration.rst` in the same wave.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Config name truth-alignment (DOC-07) | Docs / Static content | — | Pure `.rst` prose edits; no code, no builder/translator involvement |
| Orphan file removal (DOC-06) | Docs / Static content | Test suite | The `.rst` deletion is docs-tier; the test-file break it causes is test-tier (see Pitfall 1) |
| `.po`/`.mo` translation catalog sync | Build tooling (sphinx-intl/Babel) | Docs / Static content | Catalog regeneration is a build-time transform over doc source, not application logic |
| Docs build verification (SC#5) | CI / Build pipeline | — | `tox -e docs-html` / `docs-multilang` / `docs-pdf`, matching `.github/workflows/docs.yml` |

No Browser/Frontend-Server/API/Database tiers apply — this is a static-site-generator content
phase with a Python-compiled-PDF side output. GATE-01 (config→output regression) does not apply
per ROADMAP (docs-only, confirmed — no `typsphinx/*.py` files touched).

## Standard Stack

No new dependencies. All tooling already present:

| Tool | Version (verified this session) | Purpose | Source |
|------|-----------------------------------|---------|--------|
| Sphinx | 9.1.0 | Doc build / gettext extraction | `uv run sphinx-build --version` [VERIFIED: local run] |
| sphinx-intl | ≥2.0 (pyproject `docs` extra) | `.po`↔`.pot` merge (Babel-backed, pure Python — no GNU `msgmerge`/`msgattrib` binary in this sandbox) | `pyproject.toml:51`, confirmed via `sphinx-intl update` run [VERIFIED: local run] |
| furo | ≥2024.0 (pyproject `docs` extra) | HTML theme | `pyproject.toml:49` |
| tox / tox-uv | pinned per `tox.ini` | Task runner for `docs-html`/`docs-pdf`/`docs-multilang` envs | `tox.ini` |

**Package Legitimacy Audit:** Not applicable — this phase installs zero new packages (pure
content edit + one test-file deletion). No `npm view`/`pip index` verification needed.

## Architecture Patterns

### Docs build/i18n data flow (as it exists today)

```
docs/source/*.rst  ──sphinx-build -b html──►  docs/_build/html (en)      ─┐
        │                                                                  ├─► docs/_build/multilang/{en,ja}
        │   (SPHINX_LANGUAGE=ja via build_multilang.py)                   │      (tox -e docs-multilang, GitHub Pages)
        └──sphinx-build -b html -D language=ja──► docs/_build/multilang/ja┘

docs/source/*.rst  ──sphinx-build -b gettext──►  docs/_build/gettext/*.pot  (NOT committed;
                                                                              gitignored via
                                                                              docs/_build/)
docs/_build/gettext/*.pot ──sphinx-intl update -p ... -d docs/locale -l ja──►
        docs/locale/ja/LC_MESSAGES/*.po   (committed; msgstr="" = untranslated fallback to English)

docs/source/*.rst  ──sphinx-build -b typstpdf──►  docs/_build/pdf/*.pdf  (tox -e docs-pdf,
                                                                            dogfoods this extension)
```

Key fact: `conf.py`'s `gettext_auto_build = True` only controls automatic `.po`→`.mo` **binary**
compilation at HTML-build time — it does **not** regenerate `.pot` files or run `sphinx-intl
update`. There is no existing automation that keeps `.po` msgids in sync with `.rst` source;
this is a fully manual step today (confirmed: no script, no CI job, no CONTRIBUTING.md section
invokes `sphinx-intl` or `sphinx-build -b gettext` anywhere in this repo
`[VERIFIED: grep -rn "sphinx-intl\|-b gettext" over *.py *.md *.ini *.yml]`).

### Recommended task shape (not prescriptive Python — this phase touches no `.py` source)

```
docs/configuration.rst                              # DELETE (git rm)
tests/test_documentation_configuration.py            # DELETE (git rm — see Pitfall 1)
docs/source/user_guide/configuration.rst              # EDIT (D-06..D-09)
docs/source/api/index.rst                              # EDIT (D-10, delete lines 44-84)
docs/locale/ja/LC_MESSAGES/api/index.po                # REGEN (follows api/index.rst edit)
docs/locale/ja/LC_MESSAGES/user_guide/configuration.po  # REGEN (follows configuration.rst edit — NOT
                                                          # listed in CONTEXT.md's file list; see
                                                          # "Additional Finding" below)
```

### Anti-Patterns to Avoid

- **Full-corpus `.pot` regeneration without scoping:** running bare `sphinx-build -b gettext
  source docs/_build/gettext` (no filename args) regenerates all 13 `.pot` files and, when fed
  to `sphinx-intl update`, touches 4 `.po` files even on a *no-op* baseline run — 2 of which
  (`user_guide/builders.po`, `examples/advanced.po`) carry **pre-existing, unrelated** content
  drift (stale docstrings/renumbered lines from earlier phases that were never resynced). This
  is real, verified drift already in the repo (see Pitfall 3), not a hypothetical. Committing it
  under a docs-fidelity phase silently expands scope beyond DOC-06/DOC-07. Use the scoped
  invocation (two explicit filenames) instead — see Code Examples.
- **Relying on `msgattrib --no-obsolete` to clean up `.po` output:** GNU gettext's `msgattrib`/
  `msgmerge`/`msgfmt` binaries are **not present on PATH in this NixOS sandbox**
  `[VERIFIED: which msgattrib msgmerge msgfmt → all "not found"]`. `sphinx-intl` here runs
  entirely on the pure-Python Babel backend. Do not plan a task around GNU gettext CLI tools
  being available to the executor — they may not be.
- **Migrating orphan content wholesale into the canonical doc:** the orphan's `typst_elements`
  example (`docs/configuration.rst:195-200`) itself lists `mainfont`/`monofont` keys that the
  real CONF-04 allowlist (`template_engine.py:55-56`, papersize/fontsize only) would **reject
  with a loud failure**. The orphan is not just wrong on package name — its "good-looking"
  sections are *also* phantom post-Phase-26. This reinforces D-05's default of salvaging
  nothing.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| `.po` msgid sync after `.rst` edits | Manual find/replace of msgid blocks in the `.po` file | `sphinx-build -b gettext` + `sphinx-intl update` (scoped invocation, see Code Examples) | Hand-editing risks msgid/`.pot` drift (exactly what D-11 warns against); the automated path guarantees the `.po`'s `#:` location comments and msgid text stay byte-consistent with the source `.rst` |
| Verifying "no broken `:doc:`/`:ref:`" | Grepping `.rst` source for `:doc:`/`:ref:` tokens by hand | Run the real `sphinx-build` and grep its `WARNING:` output (see Validation Architecture) | Sphinx build does NOT use `-W`/nitpicky in this project (`[VERIFIED: grep -n "\-W\b\|nitpicky" tox.ini docs/source/conf.py docs/build_multilang.py` → no hits`]`) — broken xrefs are non-fatal WARNINGs, not build failures, so only the build log (not exit code) proves the SC |

**Key insight:** every mechanic in this phase (gettext extraction, `.po` merge, broken-xref
detection) already has a first-party tool; the risk in this phase is entirely about **scope
creep** (touching unrelated `.po` files, migrating orphan content) and **collateral test
breakage** (Pitfall 1), not about missing tooling.

## Runtime State Inventory

This phase deletes a tracked file (`docs/configuration.rst`) and removes content (api
list-table + its `.po` msgids) — the Runtime State Inventory protocol applies.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — this project has no database/datastore that references `docs/configuration.rst` by name. | None. |
| Live service config | None — GitHub Pages deploy (`docs.yml`) publishes `docs/_build/multilang` (a build artifact), never the `docs/` root tree directly. Deleting `docs/configuration.rst` has zero effect on the deployed site (it was never built into it — no `conf.py` in root `docs/`). | None. |
| OS-registered state | None applicable (docs-only phase, no CLI/service registration). | None. |
| Secrets/env vars | None — no secret or env var references `docs/configuration.rst` by name or path. | None. |
| Build artifacts / installed packages / **test suite** | **`tests/test_documentation_configuration.py`** (11 test functions) hard-codes `Path(__file__).parent.parent / "docs" / "configuration.rst"` and calls `.read_text()` on it in every test. This file becomes 100% failing/erroring the instant `docs/configuration.rst` is deleted. See Pitfall 1. | **Code edit (test deletion), same wave as the `git rm`.** |

**Also checked, confirmed clean:**
- `tests/test_documentation_usage.py::test_usage_links_to_configuration` only substring-checks
  `docs/usage.rst`'s own content for the word "configuration" — it has **no** hard dependency on
  `docs/configuration.rst` existing. Safe, unaffected. `[VERIFIED: Read of test file]`
- `tests/test_confval_field_spacing_render_gate.py` and two `deflist_term_*` fixture files
  mention `usage/configuration.rst` in comments — this refers to an **unrelated external
  reference corpus** (a real-world Sphinx docs file used to mirror edge-case RST structures for
  regression fixtures), not this repo's `docs/configuration.rst`. No interaction.
  `[VERIFIED: grep + Read]`
- No test references `docs/source/api/index.rst`'s "Available Configuration Values" table
  content specifically — the api-table deletion (D-10) has no test-suite collateral.
  `[VERIFIED: grep -rln over tests/]`
- `tests/test_documentation_installation.py` exists and follows the identical
  hard-existence-check pattern for `docs/installation.rst` — **not touched this phase**
  (installation.rst is out of DOC-06's scope per CONTEXT.md's Deferred section), but this
  confirms the "test hardcodes root docs/*.rst file" pattern will recur when that deferred
  dead-tree sweep eventually happens. Informational only, no action here.

## Common Pitfalls

### Pitfall 1: Deleting the orphan without deleting its dedicated test file drops D-12(d) to RED
**What goes wrong:** `git rm docs/configuration.rst` alone makes every one of the 11 test
functions in `tests/test_documentation_configuration.py` fail (most with
`FileNotFoundError`/`OSError` from `.read_text()` on a non-existent path, since each test
independently re-reads the file). `pytest` goes from fully green to 11 new failures.
**Why it happens:** The test file was written when `docs/configuration.rst` was still the
active docs source (pre-`docs/source/` migration); it was never updated when the docs tree
moved, and nothing else in the repo currently exercises it as "dead."
**How to avoid:** Delete `tests/test_documentation_configuration.py` in the **same task/wave**
as `git rm docs/configuration.rst`. Do not attempt to repoint its assertions at the canonical
doc — several assertions (`test_configuration_has_troubleshooting`,
`test_configuration_documents_template_options` requiring `typst_template_mapping`) would not
even pass against the canonical file's current content, and adapting them would itself be scope
creep (documenting `typst_template_mapping` is not part of DOC-06/DOC-07).
**Warning signs:** `pytest` failures whose tracebacks point at
`tests/test_documentation_configuration.py` after the orphan deletion, all sharing the same
root file-not-found cause.

### Pitfall 2: `sphinx-intl update` leaves obsolete msgids as `#~`-commented, not deleted
**What goes wrong:** Running `sphinx-intl update` after the api-table content is removed from
`.pot` does not physically remove the corresponding `.po` entries — it comments them out with a
`#~` prefix (verified: e.g. `#~ msgid "modern-cv Template"` / `#~ msgstr "..."` pattern observed
in a live regen of an unrelated file this session). A naive `grep 'typst_papersize'
docs/locale/ja/LC_MESSAGES/api/index.po` would still return a hit (the `#~`-commented line) even
after a correct regeneration.
**Why it happens:** This is standard gettext/Babel merge semantics — obsolete entries are kept
as inert comments so a translator can recover lost translations if the string reappears later.
**How to avoid:** `#~`-commented entries are never compiled into `.mo` and are functionally
inert — they do not constitute a "live orphaned msgid." Scope the grep-zero check to exclude
comment lines: `grep 'typst_papersize\|typst_fontsize\|typst_use_codly\|typst_code_line_numbers'
docs/locale/ja/LC_MESSAGES/api/index.po | grep -v '#~'` → expect zero. Do not add a task to
strip `#~` lines with `msgattrib` (see Anti-Patterns — the binary isn't available in-sandbox).
**Warning signs:** A grep-zero check written without the `#~` exclusion will falsely fail even
after a correct regeneration; don't let that block the phase.

### Pitfall 3: Unscoped `.pot` regeneration sweeps in pre-existing, unrelated `.po` drift
**What goes wrong:** A bare `sphinx-build -b gettext source _build/gettext` (no filename args)
regenerates all 13 source `.pot` files. Feeding that to `sphinx-intl update -p ... -l ja`
updates **4** `.po` files even before this phase's content edits land: `api/index.po` (expected,
in scope), `user_guide/configuration.po` (expected, in scope once D-06..D-09 land), plus
`user_guide/builders.po` (+1/-0) and `examples/advanced.po` (+2/-2) — **both already stale
relative to current `.rst` source, unrelated to this phase** (verified: their diffs show
`.rst` line-number renumbering and one already-changed msgid pair from prior phases' edits that
was never resynced to `.po`).
**Why it happens:** `.po` sync is fully manual in this repo (see Architecture Patterns) — drift
accumulates silently across phases whenever a `.rst` file is edited without a matching
`sphinx-intl update`.
**How to avoid:** Use the scoped gettext invocation (two explicit filenames — see Code Examples)
which only touches `api/index`, `index`, `user_guide/configuration`, `user_guide/index`
`.pot`/`.po` pairs, and `.pot` build empirically confirmed to leave the other 9 `.po` files
untouched. If `index.po` / `user_guide/index.po` show as "Not Changed" after the scoped run
(expected, since their toctree content doesn't change), don't `git add` them — only stage
`api/index.po` and `user_guide/configuration.po`.
**Warning signs:** `git status` showing changes in `docs/locale/ja/LC_MESSAGES/user_guide/
builders.po` or `docs/locale/ja/LC_MESSAGES/examples/advanced.po` after running the `.po`
regeneration step — that means the unscoped (bare) invocation was used by mistake.

### Pitfall 4: Assuming a broken `:doc:`/`:ref:` fails the build
**What goes wrong:** Sphinx does not use `-W` (warn-as-error) or `nitpicky` anywhere in this
project's build commands (`tox.ini`, `docs/build_multilang.py`, `docs/source/conf.py` all
checked — no hits). A dangling `:doc:` or `:ref:` produced by the api-table deletion (e.g. an
accidentally-broken `See :doc:.../user_guide/configuration` pointer) would print a `WARNING:`
line and the build would still **exit 0**.
**Why it happens:** No warn-as-error gate is configured; this is a deliberate-or-unnoticed
project convention, not a phase-27 concern to fix.
**How to avoid:** SC#5's "no broken `:doc:`/`:ref:`" must be proven by grepping the captured
build output for `WARNING:`, not by trusting the exit code. Baseline established this session:
a clean `sphinx-build -b html` currently emits **exactly one** pre-existing WARNING (a docutils
block-quote spacing issue in `typsphinx/translator.py`'s docstring — unrelated to docs content,
untouched by this phase). Compare against this baseline: any *new* WARNING mentioning
"nonexisting document", "undefined label", or "unknown document" after this phase's edits is a
real regression; the pre-existing translator.py one is expected and must not be treated as a
failure.
**Warning signs:** A verification step that only checks `sphinx-build`'s exit code will pass
even with a broken cross-reference — don't rely on it alone.

## Code Examples

### Scoped `.pot` extraction + `.po` regeneration (verified this session)

```bash
# From the docs/ directory (matches tox's changedir=docs convention)
cd docs

# Restrict gettext extraction to exactly the two edited docs. Verified output:
# _build/gettext/api/index.pot, _build/gettext/index.pot,
# _build/gettext/user_guide/configuration.pot, _build/gettext/user_guide/index.pot
# (the parent toctree pages "index" and "user_guide/index" are pulled in automatically;
# no other doc's .pot is touched)
uv run sphinx-build -b gettext source _build/gettext \
    source/api/index.rst source/user_guide/configuration.rst

# Merge into the ja catalogs. sphinx-intl reads locale_dirs from conf.py (../locale/,
# relative to docs/source/conf.py) when -d is given explicitly as below.
uv run --extra docs sphinx-intl update -p _build/gettext -d locale -l ja

# Only these two should show as "Update:" — if others appear, scope leaked (Pitfall 3)
git status --short locale/

# Stage only the in-scope catalogs
git add locale/ja/LC_MESSAGES/api/index.po locale/ja/LC_MESSAGES/user_guide/configuration.po
```

### Grep-zero verification for the deleted phantom names (D-12a, `.po`-aware per Pitfall 2)

```bash
# .rst surfaces — must be truly zero (D-12a)
grep -n 'typst_use_codly\|typst_code_line_numbers\|typst_papersize\|typst_fontsize' \
    docs/source/user_guide/configuration.rst docs/source/api/index.rst
# expect: no output

# typst_author (tuple form) must not survive either — distinguish from typst_authors (real)
grep -n 'typst_author\b' docs/source/user_guide/configuration.rst
# expect: no output (only `typst_authors` should remain, checked separately below)

# .po surface — exclude inert #~-commented obsolete entries (Pitfall 2)
grep 'typst_papersize\|typst_fontsize\|typst_use_codly\|typst_code_line_numbers' \
    docs/locale/ja/LC_MESSAGES/api/index.po | grep -v '#~'
# expect: no output
```

### Grep cross-check: every surviving `typst_*` is registered (D-12b, SC#4)

```bash
# The D-01 registered set (11 names, typsphinx/__init__.py:44-60)
cat > /tmp/registered_confvals.txt <<'EOF'
typst_documents
typst_template
typst_template_mapping
typst_use_mitex
typst_elements
typst_package
typst_package_imports
typst_template_function
typst_authors
typst_debug
typst_template_assets
EOF

# Every typst_* token appearing in the two surfaces must be in the registered set.
grep -ohE '\btypst_[a-z_]+\b' docs/source/user_guide/configuration.rst docs/source/api/index.rst \
    | sort -u > /tmp/surviving_confvals.txt

comm -23 /tmp/surviving_confvals.txt /tmp/registered_confvals.txt
# expect: no output (comm -23 = lines only in surviving, i.e. unregistered survivors)
```

### Safe-deletion proof: no live inbound reference to the orphan (D-12, SC#1)

```bash
# Only the LIVE Sphinx tree (docs/source/) matters — docs/ root has no conf.py and is never built
grep -rn ':doc:`configuration`\|:doc:`/configuration`\|:ref:`configuration`' docs/source/
# expect: no output — confirmed this session; the only `:doc:`configuration`` hits under
# docs/source/ resolve relatively to user_guide/configuration.rst (the canonical doc), never
# to the orphan (user_guide/index.rst:27, templates.rst:360, builders.rst:187 — all safe)

# Dead-tree sibling refs to the orphan are EXPECTED to remain and are harmless (docs/ has no
# conf.py, never built) — do not "fix" these, they're the deferred cluster:
grep -n ':doc:`configuration`' docs/usage.rst docs/installation.rst
# expect: docs/usage.rst:554,582,601 and docs/installation.rst:213 — leave as-is
```

### Build-green proof mirroring real CI (SC#5)

```bash
# Mirrors .github/workflows/docs.yml's actual gate exactly
uv run tox -e docs-multilang 2>&1 | tee /tmp/docs-multilang.log
uv run tox -e docs-pdf 2>&1 | tee /tmp/docs-pdf.log

# Baseline established this session: exactly 1 pre-existing WARNING (translator.py docstring
# spacing, unrelated). Any NEW warning naming "nonexisting document" / "undefined label" /
# "unknown document" is a real regression from this phase's edits.
grep -n 'WARNING:' /tmp/docs-multilang.log /tmp/docs-pdf.log
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| `docs/configuration.rst` (root, no `conf.py`) as the docs source | `docs/source/` tree with `docs/source/conf.py`, toctree-driven | Some earlier, unrecorded migration (pre-dates this milestone) | The root `docs/*.rst` cluster (`configuration.rst`, `usage.rst`, `installation.rst`) is entirely dead weight — this phase removes the first of the three; `usage.rst`/`installation.rst` are explicitly deferred |
| `typst_papersize`/`typst_fontsize` top-level config (documented, never implemented) | `typst_elements = {"papersize": ..., "fontsize": ...}` (CONF-04, Phase 26) | Phase 26 (this milestone) | This phase's D-08 rewrite is what makes the paper-size docs finally *true* |

**Deprecated/outdated:**
- `typst_use_codly` / `typst_code_line_numbers`: never implemented; codly usage is currently
  unconditional/internal to the translator (per D-06, no config knob exists — removing the
  phantom examples is correct; do not invent a replacement note unless it can be stated without
  documenting unverified internal behavior).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | Codly application is fully internal/automatic with no user-facing toggle (D-06's basis for "just delete, don't replace with a note") | Common Pitfalls / State of the Art | Low — if a real config knob is later added, docs would need a follow-up addition, not a correction; this phase's deletion is safe either way since `typst_use_codly`/`typst_code_line_numbers` are unregistered today regardless |

No other claims in this research are assumed — every mechanic (`.po` merge behavior, `-W`
absence, test-file breakage, orphan content comparison, build warning baseline) was directly
verified by executing the real tooling against this repository in this session.

## Open Questions

1. **Should `typst_template_mapping`, `typst_package_imports`, and `typst_debug` get added to
   the canonical `user_guide/configuration.rst` in a future phase?**
   - What we know: the orphan documented all three (with the wrong package name); the canonical
     doc currently documents neither. These are real, registered config values (D-01) that are
     simply undocumented anywhere live today.
   - What's unclear: whether this is in scope for a future docs-coverage pass or stays
     permanently minimal.
   - Recommendation: out of DOC-06/DOC-07's scope (which is phantom-removal + rename, not
     coverage-completion). File a follow-up todo rather than expanding this phase; do not let
     the executor "helpfully" add these mid-phase (re-drift risk, matches D-05's caution).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| Sphinx | docs build gates | ✓ | 9.1.0 | — |
| sphinx-intl (Babel backend) | `.po` regeneration | ✓ | ≥2.0 (docs extra) | — |
| GNU gettext (`msgmerge`/`msgattrib`/`msgfmt` binaries) | Not required by this plan | ✗ | — | Not needed — `sphinx-intl` uses its pure-Python Babel backend in this sandbox; do not plan a task around these binaries |
| tox / tox-uv | `docs-html`/`docs-pdf`/`docs-multilang` envs | ✓ | pinned per `tox.ini` | — |

**Missing dependencies with no fallback:** none — GNU gettext absence has a working fallback
(pure-Python sphinx-intl path), already the verified default in this environment.

## Validation Architecture

Docs-only phase; `nyquist_validation: true` in `.planning/config.json` → included per policy.
No unit-test framework applies to `.rst` prose content itself — validation here is
grep-assertion + build-green, exactly as CONTEXT.md's D-12 already specifies. This section maps
each Success Criterion to its concrete, automated proof.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing suite) for the one collateral test-file deletion; grep/`comm` assertions + `tox` build gates for the docs content itself |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`), `tox.ini` |
| Quick run command | `uv run pytest tests/test_documentation_usage.py tests/test_documentation_installation.py -q` (confirm the two *sibling* doc-existence test files stay green — they are NOT touched by this phase) |
| Full suite command | `uv run pytest` (must be fully green post-deletion of `test_documentation_configuration.py`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| DOC-06 | Orphan deleted, no live xref, test collateral removed | grep + pytest | `grep -rn ':doc:\`configuration\`' docs/source/` (zero) + `uv run pytest` (green) | ✅ existing suite; ❌ no dedicated new test needed — deletion is self-verifying via grep-zero + suite-green |
| DOC-07 surface A | Phantom names gone from `user_guide/configuration.rst`, working `typst_elements` example present | grep + build | Code Examples block above (grep-zero + cross-check) + `tox -e docs-html` | ❌ Wave 0 gap: none — grep/build are sufficient, no unit test warranted for prose content |
| DOC-07 surface B | list-table deleted from `api/index.rst`, `.po` follows | grep + build | Code Examples block above + `tox -e docs-multilang` | ❌ Wave 0 gap: none |

### Sampling Rate
- **Per task commit:** grep-zero checks (near-instant) after each `.rst` edit
- **Per wave merge:** `uv run tox -e docs-html` (fast single-lang sanity)
- **Phase gate:** `uv run tox -e docs-multilang` + `uv run tox -e docs-pdf` (mirrors real CI
  exactly) + `uv run pytest` (full suite) before `/gsd-verify-work`

### Wave 0 Gaps
None — existing test infrastructure (pytest suite, tox docs envs) covers all phase
requirements once `tests/test_documentation_configuration.py` is deleted alongside the orphan.
No new test files are needed; this is a content-fidelity phase, not a behavior phase.

## Security Domain

`security_enforcement: true` in config — included per policy, but this phase has no attack
surface: no user input processing, no auth/session/crypto code paths, no network calls, no new
dependencies. It edits static `.rst` prose and deletes a dead file + a dead test file.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|-----------------|---------|---------------------|
| V2 Authentication | no | N/A — no auth surface in this phase |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | no | N/A — no user-supplied input is processed; `.rst` content is repo-authored, not runtime input |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack

None applicable — no code paths introduced or modified, only documentation content and one
dead test file removed.

## Sources

### Primary (HIGH confidence — verified via direct execution against this repository this session)
- `typsphinx/__init__.py:44-60` — the 11 registered `add_config_value` calls (D-01 source of truth, re-confirmed)
- `typsphinx/template_engine.py:44-56` — CONF-04 `typst_elements` allowlist (papersize/fontsize only), used to disprove the orphan's `mainfont`/`monofont` example
- `docs/source/conf.py` — `locale_dirs`, `gettext_compact`, `gettext_auto_build` settings read directly
- `tox.ini` — `docs-html`/`docs-pdf`/`docs-multilang` env definitions (no `-W` flag anywhere)
- `.github/workflows/docs.yml` — real CI build gate (`tox -e docs-multilang` + `tox -e docs-pdf`), used as the SC#5 command basis
- `docs/build_multilang.py` — confirms `docs-multilang` runs `sphinx-build -b html -D language={en,ja}` per language, no `-W`
- `docs/locale/ja/LC_MESSAGES/api/index.po` — read in full; confirmed exact line-number mapping to `api/index.rst` and that every relevant msgstr is empty
- Live `sphinx-build -b gettext` / `sphinx-intl update` runs performed this session against scratch copies of `docs/locale` — confirmed scoped-filename behavior, obsolete-entry (`#~`) handling, and pre-existing unrelated `.po` drift in `user_guide/builders.po` / `examples/advanced.po`
- Live `sphinx-build -b html` baseline run — confirmed exactly one pre-existing WARNING, unrelated to this phase
- `tests/test_documentation_configuration.py`, `tests/test_documentation_usage.py`, `tests/test_confval_field_spacing_render_gate.py` — read in full to establish Pitfall 1 and rule out other collateral

### Secondary (MEDIUM confidence)
- None used — all findings for this phase were directly verifiable against the local repository and its actual tool behavior; no external ecosystem/library documentation lookup was needed (docs-only, code-archaeology phase).

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new dependencies; existing tool versions confirmed via direct invocation
- Architecture: HIGH - data flow and file scope confirmed by reading every touched file plus live build/gettext runs
- Pitfalls: HIGH - all four pitfalls (test-file breakage, `#~` obsolete entries, unscoped regen drift, non-fatal broken xrefs) were reproduced/confirmed via actual command execution, not inferred

**Research date:** 2026-07-24
**Valid until:** 2026-07-31 (7 days — repo state, especially the `.po`/`.rst` drift baseline noted in Pitfall 3, will shift as soon as any other phase touches these files; re-verify grep baselines if planning is delayed)
