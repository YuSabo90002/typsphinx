# Feature Research

**Domain:** Sphinx extension (docutils→Typst builder/writer/translator) — forward-compatibility port to Sphinx 9 + typst 0.15+
**Researched:** 2026-07-09
**Confidence:** MEDIUM-HIGH (primary-source `typst.toml`/`CHANGELOG.md` pulls from `typst/packages` + upstream repos are HIGH; Sphinx/docutils changelog synthesis via WebSearch is MEDIUM — verify against `sphinx-doc.org/en/master/changes/9.0.html` at implementation time)

> Supersedes the previous (2026-07-04) version of this file, which researched the **v0.4.4 pin-backward** milestone. This version researches the **v0.5.0 forward-ecosystem** milestone (Sphinx 9 FWD-01 + typst 0.15+ FWD-02), which is the opposite direction: raising pins forward instead of pinning back.

This is a maintenance/compatibility milestone, not a product-feature milestone, so "features" below means **behavior-compatibility work items** required (or optional) to run correctly on Sphinx 9 + typst 0.15+. Categorized per the template: table stakes = must-fix-to-compile-and-pass-CI, differentiators = optional modernization while touching the same code, anti-features = scope creep to explicitly reject this cycle.

## Feature Landscape

### Table Stakes (Must-Fix to Compile/Build Green)

| Feature / Fix | Why Required | Complexity | Notes |
|---------|--------------|------------|-------|
| Bump bundled `mitex` from `0.2.4` → `0.2.7` (3-way sync: `writer.py` line 96, `template_engine.py` line 315, `templates/base.typ` line 14) | **Root-cause fix for the `kai` CI failure.** Confirmed via `mitex`'s own `CHANGELOG.md`: v0.2.6 = `"Fix: fix 'kai is deprecated' warning for Typst v0.14.0" (#201)`. typsphinx pins `0.2.4`, which predates that fix and still emits the deprecated `kai` symbol. Typst 0.15's changelog states deprecated stdlib symbols were *removed outright* ("Various previously deprecated symbols have been removed"), turning mitex 0.2.4's warning into a hard `typst.TypstError: unknown variable: kai`. This directly corrects PROJECT.md's speculation that `gentle-clues:1.2.0` or `codly` was the culprit — it is `mitex:0.2.4`. | LOW | No breaking `mi()`/`mitex()` signature change 0.2.4→0.2.7 (confirmed against `mitex-rs/mitex` source); pure version-string swap in the 3 sync points + `tests/test_preview_version_sync.py` assertion update |
| Bump bundled `gentle-clues` from `1.2.0` → `1.3.1` (same 3-way sync) | Compiler floor rises to a version whose `typst.toml` explicitly declares `compiler = "0.13.0"` — safely below 0.15, but 1.2.0 predates ~2 years of upstream fixes and is the most plausible *secondary* suspect if `kai` isn't fully resolved by the mitex bump alone. Changelog 1.2.0→1.3.1 = translation additions (Czech/Danish/Japanese) + a `quotation` quoting fix only — **no breaking change** to `info`/`warning`/`tip`/`danger`/`error`/`success`/`question` clue functions (all remain `#let x(..args) = _predefined-clue("x", ..args)` per `lib/predefined.typ`). | LOW | `translator.py`'s `_visit_admonition()` calls (`info(title: "...")[...]`, `warning[...]`, `tip[...]`) remain valid unchanged |
| Bump bundled `codly-languages` from `0.1.1` → `0.1.10` (same 3-way sync) | Multiple years of upstream language/icon-set additions; confirmed via `lib.typ` diff that the sole export (`codly-languages` dict) is unchanged — bump is a same-shape drop-in, only internal icon-rendering tweaked (`image(..., height: 130%, fit: "contain")` replacing the old `height: 0.9em, baseline: 0.05em`) | LOW | Safe; translator/template code never references internals, only the dict via `codly(languages: codly-languages)` |
| Confirm `codly` stays pinned at `1.3.0` (no bump available on Universe) | `typst/packages` (the actual Universe source-of-truth, queried via GitHub API directory listing) shows codly's latest **published** version is still `1.3.0` — identical to what typsphinx already pins. Upstream `Dherse/codly` git repo already has a `v1.3.1` tag/`typst.toml` not yet submitted to `typst/packages`, so nothing newer is consumable via `@preview` today. `compiler = "0.12.0"` floor is well below 0.15 but that's a floor, not a compatibility guarantee. | LOW (no code change) / MEDIUM (verification risk) | Must be verified empirically by an actual `docs-pdf` build under typst 0.15 in this milestone's phase work — no changelog confirms or denies 0.15 compatibility for codly 1.3.0. If it breaks, there is no simple "bump the pin" fallback (would need a fork/patch or waiting on upstream to publish 1.3.1) — should not be needed based on current evidence, but flag for phase-specific verification |
| Update `tests/test_preview_version_sync.py` expected versions | The 3-way sync test asserts `writer.py`/`template_engine.py`/`templates/base.typ` agree on `@preview` versions — it will fail the moment any of the three files above are bumped unless the test's expected-version constants are updated in the same change | LOW | Single test file, mechanical update |
| Audit `translator.py` for docutils 0.22 structural node changes: multi-`<term>` `definition_list_item`, `<figure>` whose first child is now a `<reference>` wrapping a "clickable" `<image>` | docutils 0.22 release notes explicitly flag both as changes "third-party writers may need adaption" for. **Spot-checked and found low-risk**: `visit_figure`/`visit_image`/`visit_reference` (translator.py lines ~1124, 1462, 1891) are all independent visitor methods driven by docutils' generic `walkabout()` traversal (not positional child-indexing), so a `<reference>`-wrapped image inside `<figure>` is walked into naturally — no code change expected. `visit_term`/`visit_definition_list_item` (lines 1027-1082) buffer via a single `self.current_term_buffer`, which assumes exactly one `<term>` per item — needs a positive integration-test check (multi-term definition lists: `term1 : term2\n   definition`) | LOW-MEDIUM | Add a targeted test with a multi-term definition list to confirm `visit_term`'s single-buffer assumption doesn't silently drop the 2nd+ term. Flag for deeper phase-specific research if the audit surfaces breakage |
| Verify `sphinx.util.logging`, `SphinxTranslator`, `Builder.get_outdated_docs()/write()/write_doc()`, `app.add_config_value()`, `app.add_builder()`, and the `[project.entry-points."sphinx.builders"]` discovery mechanism against Sphinx 9 | Sphinx 9.0's own changelog was reviewed end-to-end (Incompatible Changes + Deprecated sections) — **none of these specific APIs are listed as changed, deprecated, or removed** in 9.0. The only deprecations that touch extension code at all are: public `.app` attributes (`builder.app`, `env.app`, `events.app`, `SphinxTransform.app` — typsphinx's builder/writer/translator never reference `self.app`), `Parser.set_application()`/`.config`/`.env` (typsphinx has no custom `Parser`), and non-UTF-8 source encoding support (irrelevant — typsphinx reads/writes UTF-8 explicitly throughout `builder.py`). Entry-point discovery via `[project.entry-points."sphinx.builders"]` remains Sphinx's documented, unchanged mechanism. | LOW (verification only, expected no-op) | This is good news: the builder/writer/translator/config-registration layer (`builder.py`, `writer.py`, `__init__.py`) needs **no structural changes** for Sphinx 9 itself — the Sphinx-9 half of this milestone is expected to be mostly a version-ceiling change plus a `black`/`ruff`/CI-matrix pass, not an API port. Should still be confirmed empirically against the actual resolved `sphinx==9.0.x` in CI, since WebSearch-derived changelog summaries are MEDIUM confidence |
| `black --check` reformat under `sphinx>=9`/`docutils>=0.22` resolution (already observed in PROJECT.md's failure evidence: `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`) | Already reproduced once in CI (2026-07-04 run); trivial lint-formatting delta, unrelated to any Sphinx/docutils/typst API, but blocks the same green-CI gate | LOW | Just re-run `black .` and commit; not a translator/API concern |

### Differentiators (Nice-to-Have While Touching This Code, Not Required)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Replace `template_engine.py`'s `doctree.traverse(addnodes.toctree)` (line 239) with `doctree.findall(addnodes.toctree)` | `traverse()` is docutils' pre-0.18 back-compat shim ("returns a list again to restore backwards compatibility"); `findall()` is the modern iterator-based API and is already used elsewhere in the codebase (`builder.py`'s `post_process_images` uses `doctree.findall(image)`). Using `findall()` everywhere removes the one remaining inconsistency and de-risks a hypothetical future docutils major that drops `traverse()` entirely (not currently scheduled, but the pattern-drift is the kind of thing the milestone's durability guardrails exist to prevent) | LOW | One-line change (`list(doctree.findall(...))` still works — `findall()` also returns an iterator that `list()` consumes identically); purely a modernization, not required for 0.15/Sphinx 9 green CI |
| Refresh hardcoded `@preview` version strings shown in `docs/`/`README.md` user-facing examples to match the new pins | Once the 3-way sync bumps versions, any docs (README examples, `docs/` `.rst` source showing `#import "@preview/codly:1.3.0"` etc.) that hardcode the old version strings should be refreshed so copy-pasted user snippets don't silently regress to stale/incompatible pins | LOW | Search-and-verify pass across `docs/` and `README.md`; not required for CI green but avoids user-facing drift right after the bump |
| Add a regression test compiling a doc that exercises the `mitex` construct that previously triggered `kai` | Since the actual trigger construct inside mitex 0.2.4 that emitted `kai` isn't publicly documented in detail (only "fix kai is deprecated warning" in the changelog, no repro snippet), a targeted math/mitex integration test compiled under the new typst pin would give durable regression coverage instead of relying solely on "the version number is high enough" | MEDIUM | Would need to trace `mitex-rs/mitex` PR #201's diff for the exact trigger construct if deeper certainty is wanted; otherwise a broad LaTeX-math smoke test compiled end-to-end under typst 0.15 is a reasonable proxy |

### Anti-Features (Explicitly Out of Scope This Cycle)

| Feature | Why It Might Seem Appealing | Why Problematic Here | Alternative |
|---------|---------------|------------------|-------------|
| Making `@preview` package versions user-configurable (FWD-03) | Natural adjacent improvement while already touching the 3-way sync code for the version bumps | Explicitly out of scope per PROJECT.md/milestone decision (FWD-03 tracked separately); expands surface area of this ecosystem-forward cycle into a design/back-compat feature with its own testing burden | Deferred to its own future milestone (tracked as FWD-03 tech debt) |
| Supporting both Sphinx 8/typst 0.14 AND Sphinx 9/typst 0.15+ simultaneously (a compat range/shim layer, e.g. conditional imports or version-branching in `translator.py`) | Reduces blast radius / lets users upgrade gradually | Explicitly rejected — "latest-only" is a locked scope decision; a compat range roughly doubles the CI matrix and the mental model of every future translator change ("does this work on both `kai`-era and post-`kai` mitex?") | Raise the floor cleanly; no dual-version branching in source |
| New reST→Typst translation features or new node coverage (e.g. new admonition types, new directive support) discovered incidentally while auditing `translator.py` | Auditing ~140 visitor methods for docutils 0.22 compat naturally surfaces "hey, we could also support X" ideas | This is a maintenance/compatibility cycle per PROJECT.md ("New translation features / new reST constructs" is explicitly Out of Scope) | File as backlog ideas for a future feature milestone, do not implement now |
| Rewriting `pdf.py`'s `compile_typst_to_pdf()` around new `typst.compile()` kwargs (`sys_inputs`, `pdf_standards`, `package_path`, `timestamp`) just because they're now available | typst-py's `compile()` signature has grown several optional kwargs over its lifetime; tempting to "modernize" the call site while touching the compile path | No evidence any of these are required for correctness on 0.15 — the existing `typst.compile(temp_file, root=root_dir)` call remains valid per the stable typst-py binding surface; adding unused kwargs is speculative scope creep with no test coverage driving it | Leave `pdf.py` untouched unless a specific 0.15 compile failure demands one of these parameters |
| Fixing docutils 0.22's `nodes.Text.__init__` `rawsource`-argument deprecation now | It's a listed 0.22-era deprecation, so it's tempting to preempt it | Confirmed removal target is docutils **2.0**, not 0.22 itself; a `grep` across `translator.py` shows typsphinx never constructs `nodes.Text()` directly (it only consumes `Text` nodes docutils itself creates during parsing) — there is no call site to fix | No action needed; note as a non-issue, don't manufacture work |

## Feature Dependencies

```
[Bump mitex 0.2.4→0.2.7]
    └──resolves──> [kai CI failure / typst.TypstError: unknown variable: kai]

[Bump mitex/gentle-clues/codly-languages versions]
    └──requires──> [Update tests/test_preview_version_sync.py expected constants]
                       └──gates──> [Every CI job green]

[Raise typst pin to >=0.15]
    └──requires──> [All 4 bundled @preview packages compile under 0.15]
                       └──requires──> [mitex >=0.2.6 (root-cause fix), gentle-clues (any recent),
                                        codly-languages (any recent), codly 1.3.0-as-is (verify empirically)]

[Raise sphinx pin to >=9]
    └──independent-of──> [typst 0.15 @preview package work]
    (Sphinx 9 changelog audit found no builder/writer/translator/config-registration API breaks;
     the two halves of this milestone (FWD-01, FWD-02) do not block each other)

[docutils 0.22 structural node audit: multi-term definition lists, reference-wrapped figures]
    └──rides-along-with──> [Sphinx 9 support, since docutils>=0.22 is Sphinx 9's transitive floor]
```

### Dependency Notes

- **The `kai` fix requires the mitex bump specifically, not gentle-clues or codly:** this corrects PROJECT.md's speculative attribution ("likely `gentle-clues:1.2.0` or `codly`"). Any phase plan should target `mitex` first/primarily and treat the gentle-clues/codly-languages bumps as hygiene, not root-cause fixes.
- **The version-sync test gates CI green:** bumping the 3 pinned versions without updating `tests/test_preview_version_sync.py` in the same commit will itself fail CI — this is a hard sequencing dependency within a single phase, not across phases.
- **Sphinx 9 and typst 0.15 work are independent:** based on the changelog audit, nothing in the Sphinx-9 migration touches the `@preview` package layer, and nothing in the typst-0.15/`@preview` migration touches the builder/writer Sphinx-API layer. They can be planned/executed as two largely-parallel-safe phases (FWD-01, FWD-02) rather than a strict sequence, though both must land before "every CI job green" per the milestone's Active requirement.
- **`codly` has no available upgrade lever — this is a verification risk, not a code-change task:** unlike the other three packages, there's no version bump to reach for if `codly` 1.3.0 turns out incompatible with typst 0.15. If empirical testing in phase work surfaces a break, escalate immediately — the only fallback would be a fork/patch or waiting on upstream `Dherse/codly` to publish its already-tagged `v1.3.1` to `typst/packages`.

## MVP Definition

### Launch With (v0.5.0)

Minimum to close FWD-01 + FWD-02 and get every CI job green:

- [ ] Bump `mitex` 0.2.4→0.2.7 across all 3 sync points — resolves the `kai` error (root cause, HIGH confidence)
- [ ] Bump `gentle-clues` 1.2.0→1.3.1 across all 3 sync points — no API break, safe hygiene bump
- [ ] Bump `codly-languages` 0.1.1→0.1.10 across all 3 sync points — no API break, safe hygiene bump
- [ ] Leave `codly` at `1.3.0` (nothing newer published) — but empirically verify it compiles clean under typst>=0.15 as part of this milestone's CI-green gate
- [ ] Update `tests/test_preview_version_sync.py` expected version constants to match
- [ ] Drop `sphinx<9` and `typst<0.15` ceilings in `pyproject.toml`; regenerate `uv.lock`
- [ ] Run `black .` / `ruff check .` fixes for the already-observed reformatting drift under the new resolved deps
- [ ] Spot-audit `translator.py`'s definition-list-item (multi-`<term>`) handling against docutils 0.22's structural note; add a targeted test if it's found to silently drop terms
- [ ] Full 3-OS × Python 3.10–3.13 matrix green, `docs.yml` (incl. PDF build) green

### Add After Validation (not blocking v0.5.0, but cheap to fold in if time allows)

- [ ] Swap `template_engine.py`'s `doctree.traverse()` → `doctree.findall()` for API consistency with the rest of the codebase
- [ ] Refresh any hardcoded `@preview` version strings in `docs/`/`README.md` examples to match the new pins
- [ ] Add a regression test specifically exercising the mitex construct that used to emit `kai`, for durable coverage beyond "the version number is high enough"

### Future Consideration (explicitly deferred)

- [ ] FWD-03: configurable `@preview` package versions (already tracked as its own tech-debt item)
- [ ] Sphinx 8/typst 0.14 ⇄ Sphinx 9/typst 0.15 compatibility range (explicitly rejected — latest-only)
- [ ] New reST construct / translation feature coverage surfaced incidentally during the docutils 0.22 audit

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| mitex 0.2.4→0.2.7 bump | HIGH (unblocks all PDF-integration tests + docs-pdf) | LOW | P1 |
| gentle-clues 1.2.0→1.3.1 bump | MEDIUM (hygiene, unlikely to be the sole CI blocker) | LOW | P1 |
| codly-languages 0.1.1→0.1.10 bump | MEDIUM (hygiene) | LOW | P1 |
| codly 1.3.0 empirical 0.15 verification | HIGH (no fallback lever if it breaks) | LOW (verification) / unknown if it fails | P1 |
| version-sync test update | HIGH (gates CI) | LOW | P1 |
| Sphinx 9 API audit (builder/writer/translator/config) | HIGH (confirms the "no-op" expectation) | LOW (audit) | P1 |
| docutils 0.22 multi-`<term>` / figure-reference audit | MEDIUM (edge-case correctness) | LOW-MEDIUM | P1/P2 |
| `traverse()`→`findall()` swap | LOW | LOW | P3 |
| docs/README version-string refresh | LOW | LOW | P3 |
| mitex `kai` regression test | MEDIUM (durability) | MEDIUM | P2 |

**Priority key:**
- P1: Must have for v0.5.0 green CI
- P2: Should have, add when possible without expanding scope
- P3: Nice to have, purely optional polish

## Competitor Feature Analysis

Not applicable in the traditional sense — this is a compatibility/maintenance milestone for a single tool's dependency graph, not a competitive feature build. The closest analog is "how do other Sphinx→X builders handle bundled third-party package pinning," which is out of scope for a forward-compat feature landscape; pinning-strategy pitfalls belong in PITFALLS.md, not this file.

## Sources

- [Sphinx 9.0 changelog](https://www.sphinx-doc.org/en/master/changes/9.0.html) — incompatible changes + deprecations (MEDIUM confidence, WebSearch-synthesized; re-verify directly at implementation time)
- [Sphinx Deprecated APIs reference](https://www.sphinx-doc.org/en/master/extdev/deprecated.html)
- [Sphinx 8.0/8.1/8.2 changelogs](https://www.sphinx-doc.org/en/master/changes/8.0.html) — pre-9.0 deprecation lead-time context
- [Docutils Release Notes](https://docutils.sourceforge.io/RELEASE-NOTES.html) — 0.22/0.21/0.18.1 entries (MEDIUM confidence, WebSearch-synthesized)
- [Typst 0.15.0 changelog](https://typst.app/docs/changelog/0.15.0/) — breaking changes, deprecated-symbol removal (MEDIUM confidence)
- [Typst 0.15 blog post "Typst 0.15 contains multitudes"](https://typst.app/blog/2026/typst-0.15/)
- [typst/typst v0.15.0 GitHub release](https://github.com/typst/typst/releases/tag/v0.15.0)
- [typst-py PyPI page](https://pypi.org/project/typst/) and [messense/typst-py GitHub](https://github.com/messense/typst-py)
- [mitex-rs/mitex CHANGELOG.md](https://raw.githubusercontent.com/mitex-rs/mitex/main/CHANGELOG.md) — **HIGH confidence, primary source**: confirms the 0.2.6 `kai` deprecation-warning fix
- [typst/packages GitHub repo](https://github.com/typst/packages) (queried via GitHub API for `packages/preview/{mitex,gentle-clues,codly,codly-languages}` directory listings) — **HIGH confidence, primary source**: ground-truth latest-published-version data, superseding Typst Universe web-page summaries which showed some date inconsistencies
- [gentle-clues CHANGELOG.md](https://raw.githubusercontent.com/jomaway/typst-gentle-clues/main/CHANGELOG.md) and [lib/predefined.typ](https://raw.githubusercontent.com/jomaway/typst-gentle-clues/main/lib/predefined.typ) — **HIGH confidence, primary source**
- codly-languages `lib.typ` diff (0.1.1 vs 0.1.10), fetched via `raw.githubusercontent.com/typst/packages/main/packages/preview/codly-languages/` — **HIGH confidence, primary source**
- Dherse/codly `typst.toml` (main branch, unpublished v1.3.1), fetched via `raw.githubusercontent.com/Dherse/codly/main/typst.toml` — **HIGH confidence, primary source**
- typsphinx source: `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `typsphinx/translator.py`, `typsphinx/builder.py`, `typsphinx/__init__.py`, `typsphinx/pdf.py`, `.planning/PROJECT.md` — direct codebase inspection

---
*Feature research for: typsphinx v0.5.0 forward-ecosystem milestone (Sphinx 9 + typst 0.15+)*
*Researched: 2026-07-09*
