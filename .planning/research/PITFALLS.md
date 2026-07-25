# Pitfalls Research

**Domain:** Migrating an existing multi-language Sphinx + custom-builder (Typst PDF) documentation site from GitHub Pages to Read the Docs (RTD) — v0.6.4 "Read the Docs migration" milestone
**Researched:** 2026-07-25
**Confidence:** MEDIUM-HIGH (RTD official docs are current and directly cited; the one true unknown — a real build inside RTD's actual container — is flagged UNVERIFIED, not guessed at. Supersedes the prior v0.6.3-era PITFALLS.md that lived at this path, which covered a different milestone's translator-fix pitfalls and is no longer the active scope.)

## Critical Pitfalls

### Pitfall 1: Declaring `formats: [pdf]` collides with the hand-built typstpdf PDF

**What goes wrong:**
RTD ships its own PDF pipeline (`sphinx-build -b latex` + `latexmk`) that activates the moment `formats: [pdf]` (or `formats: all`) is set in `.readthedocs.yaml`. If that key is added — even with the intent of "just enabling PDF downloads" — RTD tries to run its own LaTeX-based PDF build in addition to (or in place of) whatever the `typstpdf`-built PDF is doing, and it fails immediately since this project has no LaTeX toolchain and was never designed to compile via `-b latex`.

**Why it happens:**
The natural instinct when you want "a downloadable PDF" on RTD is to look for the PDF checkbox/format key, not realize that a custom-generated PDF placed in `$READTHEDOCS_OUTPUT/pdf/*.pdf` via `build.jobs`/`build.commands` is picked up automatically as a downloadable artifact with **no** `formats:` declaration needed — RTD's per-format opt-in only exists to trigger its *own* Sphinx `-b latex`/`-b epub` engines, which is exactly not wanted here (verified: PDF/ePub are opt-in and disabled by default in v2 config; per-format outputs are auto-discovered from well-known `$READTHEDOCS_OUTPUT/<format>/` directories regardless of which tool produced them — [RTD config-file v2 docs](https://docs.readthedocs.com/platform/stable/config-file/v2.html), [PR #10115 making PDF/ePub opt-in](https://github.com/readthedocs/readthedocs.org/pull/10115)).

**How to avoid:**
Do **not** add a `formats:` key to `.readthedocs.yaml` at all. Use `build.jobs` (e.g. a `post_build` or format-specific job hook) to run `sphinx-build -b typstpdf docs/source $READTHEDOCS_OUTPUT/pdf` directly, and let RTD's artifact auto-discovery pick up the file from that well-known directory. Confirm in the RTD build log that only one PDF-producing step runs, and that no `latexmk`/`pdflatex` invocation appears anywhere in the log.

**Warning signs:** A `latexmk`/`xelatex`/`.tex` line appears anywhere in the RTD build log; two different-sized PDFs both claim to be "the" download; the build fails with a LaTeX-package-not-found error despite typsphinx never touching LaTeX.

**Phase to address:** RTD build-establishment phase ("RTD ビルド確立" feature) — write and inspect the raw build log from a real RTD build before calling this feature done, not just a green checkmark.

---

### Pitfall 2: The self-referential extension is unimportable because RTD never installed the package

**What goes wrong:**
`conf.py`'s `extensions = [..., "typsphinx"]` requires the `typsphinx` package itself to be importable at Sphinx-build time. RTD does **not** install your project package by default — without an explicit `python.install` block in `.readthedocs.yaml`, RTD only provisions a Python environment but does not `pip install .` your own repo. First build fails with `ModuleNotFoundError: No module named 'typsphinx'` (or, worse, a *partial* success if some *stale* published wheel of `typsphinx` from PyPI gets pulled in transitively and shadows the in-repo working tree, so the RTD-rendered PDF/HTML reflects an old release, not the commit being built).

**Why it happens:**
This is invisible in local dev and in `docs.yml` CI because both explicitly run `uv sync --extra dev --extra docs --locked` + `uv pip install -e .` before any Sphinx invocation (confirmed in `.github/workflows/docs.yml:29-32`) — that install step has no RTD equivalent unless it is *deliberately re-declared* in `.readthedocs.yaml`'s `python.install`.

**How to avoid:**
`.readthedocs.yaml` must include:
```yaml
python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
```
(RTD's own docs confirm `extra_requirements` under `method: pip` is the way to install optional-dependency groups; editable (`-e .`) installs are not documented as a first-class option, so plan for a normal, non-editable `pip install .` unless a spike proves editable works — [RTD config-file v2](https://docs.readthedocs.com/platform/stable/config-file/v2.html).) If `build.commands` (not `build.jobs`) is used instead, this install step is **entirely the author's responsibility** — `build.commands` bypasses every default RTD step, including the implicit environment/install machinery, per RTD's own documentation ("When `build.commands` is used, none of the pre-defined build jobs will be executed").

**Warning signs:** `ModuleNotFoundError: No module named 'typsphinx'` in the RTD build log; or (the silent variant) the RTD-rendered docs reflect an older PyPI release's behavior instead of the in-repo commit — check by grepping the RTD build log for `Installing collected packages: typsphinx` and confirming the install source is the local checkout path, not a PyPI index URL.

**Phase to address:** RTD build-establishment phase. Verification must include reading the actual install-step log lines, not just "build succeeded."

---

### Pitfall 3: `conf.py` keeps reading `SPHINX_LANGUAGE`, so the ja translation project silently serves English

**What goes wrong:**
`docs/source/conf.py:51` is `language = os.getenv("SPHINX_LANGUAGE", "en")`. RTD does not set `SPHINX_LANGUAGE` — it sets `READTHEDOCS_LANGUAGE` (confirmed: "The locale name...for the project being built," lowercase-dash values like `en`, `ja` — [RTD environment-variables reference](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html)). If `conf.py` is migrated to RTD unchanged, **every** RTD project — both the English parent and the Japanese translation project — resolves `language` to the `os.getenv` fallback `"en"`, because the env var it checks for is never set. The ja translation project would build, look successful, and silently render 100% English prose with zero visible error, because Sphinx's own i18n machinery keys off `config.language` — if it stays `"en"` the translation catalog is simply never applied even though `.mo` files and `locale_dirs` are all correctly in place. This is exactly the failure class the milestone context calls out ("Is there a known failure where the translation project silently serves English?") — and per the read `conf.py`, the answer is **yes, this WILL happen if the env-var name is not changed**, not a hypothetical.

**Why it happens:**
The hand-rolled `build_multilang.py` was the only thing ever setting `SPHINX_LANGUAGE` (`env["SPHINX_LANGUAGE"] = lang_code`, `docs/build_multilang.py:44`). Deleting that script per the milestone plan removes the only producer of that variable — RTD was never a consumer of it and has no reason to know about it.

**How to avoid:**
Change `conf.py:51` to read `READTHEDOCS_LANGUAGE` (falling back to `SPHINX_LANGUAGE` only if still needed for local dev, or dropping the local-dev path entirely and relying on Sphinx's own `-D language=` override for local builds). Concretely:
```python
language = os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))
```
Then verify per-project: on the **ja** RTD project, confirm the RTD admin "Language" dropdown is actually set to Japanese (this is what makes RTD emit `READTHEDOCS_LANGUAGE=ja` in the first place — the env var reflects the *project's own configured language*, it does not itself select which translation to build). A project whose RTD admin language is left at the default "English" will emit `READTHEDOCS_LANGUAGE=en` even if it is nominally "the ja project," reproducing the exact same silent-English failure one level up the stack.

**Warning signs:** Visiting `/ja/latest/` shows English body text; `.mo` catalogs look fine but the rendered HTML/PDF never differs between `/en/` and `/ja/`; the RTD build log for the ja project never prints a language other than `en` if you `echo $READTHEDOCS_LANGUAGE` in a diagnostic `build.jobs.pre_build` step.

**Phase to address:** The "ja を RTD 翻訳プロジェクトとしてリンク" feature phase. This is a two-part fix (code: `conf.py` env-var rename; RTD admin: set the child project's language dropdown) and both parts must be verified independently — a real compiled ja page with visibly-Japanese prose, not just "build succeeded."

---

### Pitfall 4: The `ja` translation project's versions are a separate, unsynced list that needs manual activation

**What goes wrong:**
Each RTD translation project is a fully independent RTD project with its own version list — activating `latest`/`stable` on the English parent does **not** automatically activate or build the same versions on the `ja` project. "Both projects build the same commit" is not a platform guarantee; it requires the ja project to separately have `latest` (tracking the same default branch) and a `stable` version (tracking the same tag) active, or the two sites will drift — e.g. `/ja/stable/` could still be pointing at an older or nonexistent build months after `/en/stable/` has moved on.

**Why it happens:**
RTD treats translation projects as regular projects linked only for navigation/URL-prefix purposes ("Each language must have its own project on Read the Docs" — [RTD localization guide](https://docs.readthedocs.com/platform/stable/localization.html)); version activation, tag-triggered stable promotion, and even the `.readthedocs.yaml` presence are each independently evaluated per project. Community reports confirm new versions are not always auto-activated and require going into that specific project's admin ("you'll need to log in to your Read the Docs account and manually do so" — community/issue discussion on RTD's automation/versions behavior).

**How to avoid:** After creating the ja project and linking it as a translation, explicitly configure its own Automation Rules (or manually activate `latest`/`stable`) to mirror the parent's version policy. Re-check this after the v0.6.4 tag is cut — confirm `/ja/stable/` exists and points at the same tag as `/en/stable/`, not just that the ja project "builds."

**Warning signs:** `/ja/stable/` 404s or serves an older version than `/en/stable/` after a release; the ja project's version list (in its own RTD admin) doesn't contain `stable` at all.

**Phase to address:** The "ja を RTD 翻訳プロジェクトとしてリンク" feature phase, re-verified at the final release phase once the `v0.6.4` tag actually exists (this is the same "`stable` doesn't exist until the tag is cut" timing constraint the milestone already tracks for the parent — it must be independently re-checked on the child).

---

### Pitfall 5: `linkcheck` passes cleanly while the actual broken links (README, badges, `pyproject.toml`) go unchecked

**What goes wrong:**
Issue #119 ("website seems down") and the 7 dead README deep-links exist **only** in `README.md` (badge line, header, and the 7 links at `:271-277`) and in `pyproject.toml`'s `Documentation` URL — a repo-wide grep confirms **zero** occurrences of `github.io` anywhere under `docs/source/`. `sphinx-build -b linkcheck` only scans the Sphinx document tree it is given (`docs/source/**/*.rst`); it has no knowledge of `README.md` or `pyproject.toml` at the repo root. A `linkcheck` CI job can therefore be added, run green every single time, and never once have caught the actual defect that motivated this milestone — because the URLs that broke were never inside its scan scope to begin with.

**Why it happens:**
"Add a linkcheck job" reads as "this closes the 404-link gap," but the gap that actually bit this project lived in a file class linkcheck structurally cannot see. This is an easy trap: a green linkcheck run creates false confidence that the exact failure mode from #119 is now covered.

**How to avoid:** Treat `sphinx-build -b linkcheck` as covering *only* cross-references and external links authored inside `docs/source/*.rst` — it is a good, cheap advisory net for future in-doc rot, but it is not a substitute for verifying the README/pyproject/`INTEGRATIONS.md` URL rewrites landed correctly. Verify those with a separate, explicit grep-and-curl (or a `lychee`/similar tool run against `README.md` directly) rather than relying on the Sphinx linkcheck job to have covered them. Document this scope boundary explicitly wherever the linkcheck job is introduced, so a future contributor doesn't assume "linkcheck is green" implies "README links are fine."

**Warning signs:** Grep for the pattern that caused #119 (`github.io` or the eventual RTD URL) across `README.md`/`pyproject.toml` and confirm it's *not* inside `docs/source/` — if it were, linkcheck actually would have caught it and this pitfall would not apply going forward for that specific pattern. Any future "linkcheck is green" claim about README/metadata links specifically is unverifiable by that job and should be treated as unverified.

**Phase to address:** The linkcheck CI-job feature phase — the SC for that phase should explicitly state what linkcheck does and does not cover, and the URL-rewrite phase should carry its own independent verification (real HTTP fetch of the rewritten URLs), not lean on linkcheck for that proof.

---

### Pitfall 6: Deleting `build_multilang.py`/the language-switcher while a test still hard-asserts on it (repeat of a pattern that already bit this project twice)

**What goes wrong:**
This project has already hit this exact failure class twice in the immediately preceding milestone: Phase 27 discovered `tests/test_documentation_configuration.py` hard-asserted the existence of the very orphan file (`docs/configuration.rst`) it was about to delete, and had to delete the test in the same commit to keep the suite green; and the "anywhere under docs/source" scoping gap (phantom config names surviving in `examples/advanced.rst`/`basic.rst`) required a post-verify gap-closure commit because a repo-wide grep was skipped in favor of grepping only the files a requirement named. **Both traps are pre-loaded for this milestone**, confirmed present right now:
- `tests/test_documentation_usage.py` (`assert usage_file.exists(), "docs/usage.rst should exist"`) and `tests/test_documentation_installation.py` (`"""Test that docs/installation.rst file exists."""`) hard-assert the existence of `docs/usage.rst`/`docs/installation.rst` — the exact orphan-doc pair this milestone is scoped to resolve. Deleting those two `.rst` files without also removing (or updating) these two test files will redden the suite immediately.
- A repo-wide grep (not scoped only to the files the milestone brief names) confirms the multilang-machinery references are, in fact, fully enumerated: `tox.ini:78,84` (`[testenv:docs-multilang]`), `docs/source/_templates/language-switcher.html`, `docs/source/conf.py:50-51,85` (`SPHINX_LANGUAGE` + the sidebar registration), and `docs/build_multilang.py:44` itself. No hidden fifth reference site was found in `README.md`, `CONTRIBUTING`, or elsewhere — but this should be re-confirmed with a fresh grep immediately before the deletion commit lands, not trusted from this research snapshot, since files change between research and execution.

**Why it happens:** Deletion-scoping is easy to under-scope to "the files the requirement names" rather than "everything that references them," and collateral tests asserting a soon-to-be-deleted artifact's existence are invisible until the suite actually runs post-deletion.

**How to avoid:** Before deleting `build_multilang.py`, the `docs-multilang` tox env, `language-switcher.html`, or `docs/usage.rst`/`docs/installation.rst`, run a repo-wide grep for each target's filename/env-name/identifier (not scoped to files named in the requirement) as the very last step before the deletion commit, and explicitly decide the fate of `tests/test_documentation_usage.py` and `tests/test_documentation_installation.py` (delete them alongside their subjects, per the Phase 27 precedent, or repoint them if the content is relocated rather than deleted).

**Warning signs:** `pytest` collection errors or new failures immediately after a deletion commit; `grep -rn "build_multilang\|docs-multilang\|language-switcher\|usage.rst\|installation.rst"` returning any hit outside the set already enumerated above.

**Phase to address:** The "ja を RTD 翻訳プロジェクトとしてリンク + 自前 multilang 廃止" phase (for `build_multilang.py`/tox env/language-switcher) and the "`docs/usage.rst`/`installation.rst` の孤児処理" phase (for the two test files) — both phases' plans should name the collateral test files explicitly as in-scope deletions/edits, not leave them for a post-verify gap-closure commit as happened last milestone.

---

### Pitfall 7: Irreversible or hard-to-undo steps executed without an explicit owner confirmation gate

**What goes wrong:** Several actions in this migration cannot be cleanly undone or are expensive to redo, and doing them prematurely (before the rest of the migration is verified) forecloses options:
- **RTD project slug**: chosen at project creation and is not self-service changeable afterward. RTD's own guidance: you can delete-and-recreate to get a new slug, but "you really shouldn't do this if you have existing inbound links, as it breaks the internet" — the only sanctioned path to rename an existing slug is emailing `support@readthedocs.org` ([RTD FAQ](https://docs.readthedocs.com/platform/stable/faq.html)). Since this project's inbound links are about to be *rewritten to point at RTD for the first time*, getting the slug wrong at creation (e.g. picking `typsphinx-docs` instead of `typsphinx`) bakes an ugly URL into every link this milestone is about to publish.
- **`gh-pages` branch + GitHub Pages site deletion**: the milestone's own locked decision is immediate deletion with no redirect stubs, an explicit accepted-consequence choice already made by the owner (2026-07-25) — but this research flags it again because it is the one step in this milestone with zero technical recovery path once done (a force-deleted branch's history is not gone from git reflog/local clones, but the *served* GitHub Pages site and any external cached copies are gone the moment Pages is disabled).
- **Custom domain / canonical URL**: RTD's canonical-domain setting affects what search engines index as canonical; setting a custom domain later (if ever desired) is a distinct, separate action from the base RTD subdomain and should not be assumed as an implicit part of this milestone unless explicitly scoped.
- **SEO/inbound-link cost of the no-redirect teardown**: every external link to `yusabo90002.github.io/typsphinx/...` (search results, blog posts, other projects' READMEs, cached search-engine index entries) 404s the instant Pages is torn down, with no 301 to carry authority to the new RTD URL. This is a real, if hard-to-quantify, SEO cost — search engines treat a 404 as a broken/removed page rather than a moved one, and any accumulated backlink equity to the old URLs does not transfer.

**Why it happens:** These are one-way doors executed as ordinary phase work; without an explicit stop-and-confirm step, a phase can execute them and move on before the rest of the migration (RTD build, translation project, URL rewrites) is proven to work end-to-end.

**How to avoid:** Sequence irreversible steps **last**, after the RTD build is proven green and the URL rewrites are proven live (RTD project first, verify it serves correctly, verify README/pyproject point at it and resolve — only then delete Pages/`gh-pages`). For the project-slug choice specifically, confirm the exact slug with the owner before RTD project creation (not after) since it becomes the permanent URL segment. This project's own "Key context" already names project creation, translation-linking, default-version setting, and About-Website setting as requiring manual owner action ("要ユーザー操作（自動化不可）") — the slug choice belongs in that same explicit-confirmation list and should be surfaced to the owner as its own line item, not implied by "RTD ビルド確立."

**Warning signs:** RTD project created with a placeholder/wrong slug before the owner explicitly confirmed the name; `gh-pages` branch deleted before an RTD build has been observed to actually serve HTML/PDF successfully at the target URL.

**Phase to address:** Sequencing concern spanning the whole milestone — the roadmap should order "prove RTD works" strictly before "delete GitHub Pages," and the RTD-project-creation step (which the owner must do manually anyway) should include an explicit slug-confirmation sub-step.

---

### Pitfall 8: The native-dependency risk is real but almost certainly smaller than assumed — plus font-availability is the actual residual unknown

**What goes wrong (or rather, what the milestone brief over-states):**
The milestone frames "does typst-py's wheel work on RTD" as the single biggest technical unknown. Verified against PyPI's own package metadata: `typst` 0.15.0 publishes `cp38-abi3` wheels for `manylinux_2_17_x86_64`/`manylinux2014_x86_64` (plus aarch64/i686/ppc64le/s390x/armv7l Linux, both macOS arches, and both Windows arches) — [PyPI JSON API for `typst`](https://pypi.org/pypi/typst/json). RTD's build images are Ubuntu 20.04/22.04/24.04 on x86_64 ([RTD build-images developer docs](https://dev.readthedocs.io/en/latest/design/build-images.html)), which is exactly the manylinux2014_x86_64 target. A plain `pip install typst` (or `uv pip install .`) should therefore resolve a prebuilt wheel with **zero** Rust/cargo compilation, identical to what already happens today in GitHub Actions' `ubuntu-latest` runner. This substantially de-risks the "compiled wheel fails to build" framing — the more likely failure modes, if any, are network/index-resolution issues, not an actual from-source compile.

The genuinely unverified risk that *is* real: **font availability for the Typst compiler inside RTD's container.** Typst's font-fallback behavior is silent by design — using a non-installed font falls back to a different font with no error and no warning by default ([typst/typst#2818](https://github.com/typst/typst/issues/2818), [typst/typst#4378](https://github.com/typst/typst/issues/4378)). If RTD's Ubuntu build image ships a different font package set than GitHub's `ubuntu-latest` runner (plausible — they are different maintained images, not the same base), the PDF could compile successfully on RTD while rendering with visibly different glyphs/kerning than the CI-validated PDF, with the build reporting full success either way.

**Why it happens:** Build success and font-correctness are orthogonal — `typst.compile()` doesn't error on a font substitution, so this class of defect is invisible to any "build succeeded" check and only surfaces on visual inspection of the actual RTD-rendered PDF.

**How to avoid:** This is exactly the kind of claim this project's culture flags as UNVERIFIED-until-measured rather than assumed. Concrete probe: after the first real RTD build produces a PDF, download it and diff/visually-compare it against the `docs-pdf` CI artifact from the same commit (or at minimum extract text via `pypdf` and confirm no `[MISSING CHARACTER]`/tofu-box indicators, and spot-check that Japanese content — if any renders through the PDF path — doesn't silently fall back to a different CJK font than intended, given Phase 27.1's own note that CJK font availability on the CI ubuntu runner was left unconfirmed). Do not rely on "RTD build succeeded" alone as evidence the native dependency or fonts are fine.

**Warning signs:** RTD build log shows a `.tar.gz` sdist being built/compiled for `typst` rather than a `.whl` being downloaded (would indicate no matching wheel was found and a source-compile with Rust toolchain requirements is being attempted — a real failure risk since the RTD build image may or may not have a Rust toolchain provisioned); or the downloaded PDF, once visually compared, shows different font rendering than the CI-produced one.

**Phase to address:** RTD build-establishment phase. The verification bar for this feature should explicitly include "downloaded the real RTD-built PDF and visually/textually compared it to the CI baseline," not just a green build status — this is the one item in this research that stays UNVERIFIED until a real RTD build is observed, per this project's stated preference for empirical gates over assertions.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Leave `conf.py`'s `SPHINX_LANGUAGE` env-var read in place "for now" alongside a new `READTHEDOCS_LANGUAGE` check | Less code churn in one commit | Silent-English translation bug (Pitfall 3) ships unnoticed since both env vars can coexist without erroring | Never for this migration — the whole point of the ja feature is a correctly-localized site |
| Add `formats: [pdf]` because it's the first thing that shows up in RTD docs/UI for "I want a PDF" | Fast, matches tutorial examples | Triggers RTD's own broken LaTeX pipeline (Pitfall 1) atop the intentional typstpdf output | Never — always route the PDF through `build.jobs`/`build.commands` output-directory convention instead |
| Grep only the files named in the requirement text before deleting orphan docs | Faster to scope, matches the literal ask | Misses collateral references (tests, tox envs, templates) — this project has hit this twice already (Pitfall 6) | Never — a repo-wide grep immediately before the deletion commit is cheap insurance already proven necessary twice |
| Treat a green `linkcheck` job as proof the README/pyproject URL rewrite is correct | One CI signal to point at | Linkcheck structurally cannot see README/pyproject (Pitfall 5) — false confidence | Never for this specific claim; fine as a *general* in-doc link-rot net |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| Read the Docs `python.install` | Assume RTD installs the project automatically like local `uv sync`/CI does | Explicitly declare `python.install: [{method: pip, path: ., extra_requirements: [docs]}]`, or do the install yourself inside `build.commands` if that path is chosen |
| Read the Docs `formats:` | Add `formats: [pdf]` to "turn on PDF downloads" | Omit `formats:` entirely; place the typstpdf output at `$READTHEDOCS_OUTPUT/pdf/*.pdf` via `build.jobs` and let RTD's artifact auto-discovery pick it up |
| Read the Docs translation projects | Assume the ja project inherits the parent's active-version list and language automatically | Separately configure the ja project's own version activation/Automation Rules, and separately confirm its Admin "Language" dropdown is set to Japanese (this is what actually sets `READTHEDOCS_LANGUAGE=ja` at build time) |
| `typst` (PyPI) native wheel on RTD's build image | Assume a Rust/PyO3 dependency needs a source-compile fallback plan on RTD | Verified: `typst` ships `cp38-abi3` wheels for `manylinux_2_17_x86_64`/`manylinux2014_x86_64` (and macOS/Windows/other Linux arches) — a plain `pip install typst` on RTD's x86_64 Ubuntu build image should resolve a prebuilt wheel with zero compilation, same as it does in the existing GitHub Actions `ubuntu-latest` CI. This is a real risk-reduction finding, not a guess — see Pitfall 8 for the residual unknown |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Running the full typstpdf compile (`tox -e docs-pdf`) inside every RTD PR-preview build | RTD PR builds become slow/expensive; RTD explicitly restricts non-HTML formats to post-merge builds by policy ("With builds from pull requests, only HTML formats are generated...other formats are built after merging") | Gate the PDF `build.jobs` step to non-PR builds (RTD's `READTHEDOCS_VERSION_TYPE` env var distinguishes `external` PR builds from `branch`/`tag`) if PR previews are ever enabled | Becomes a real cost the moment PR-preview builds are turned on for this repo (not yet in scope, but worth a guard now since RTD's own default policy already assumes this pattern) |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Treating RTD's `.readthedocs.yaml` as equivalent to a locked/pinned CI environment | RTD builds resolve dependencies at build time using whatever `pip`/`uv` resolves per the declared `python.install`; if `docs` extras aren't pinned the same way `docs.yml` CI pins them (`uv sync --locked`), an RTD build can silently pick up a different `sphinx`/`furo`/`sphinx-intl` version than CI validated against | Mirror the same lockfile-driven install RTD-side if possible (e.g. `uv export`/`pip install -r` a locked requirements file inside `build.commands`), or at minimum keep the same version ranges declared in `pyproject.toml`'s `docs` extra so RTD and CI resolve compatibly |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| Visiting the bare RTD project URL before `stable` has any real build | A visitor lands on a version selector or an empty/placeholder page instead of documentation, because the default version (`stable`) has nothing to serve until the `v0.6.4` tag exists (confirmed: RTD serves a 404/placeholder for a default version with no active build, and the fix is either to create the version or temporarily point default elsewhere — [RTD versions doc](https://docs.readthedocs.io/en/stable/versions.html)) | Either accept this as a known, temporary window (already the milestone's documented plan) and communicate it (e.g. in the release notes / About field), or default to `latest` until the tag lands and flip default to `stable` at the same commit as the release phase, minimizing the empty-`stable` window rather than opening it at RTD-project-creation time |
| `/ja/` visitor sees English text with no visual indicator anything is wrong | Confusing, silent failure — see Pitfall 3 | Fix the env-var read and verify visually (not just "build succeeded") before considering the ja feature done |

## "Looks Done But Isn't" Checklist

- [ ] **RTD build succeeds:** Often "succeeds" only because a step was skipped/no-op'd (e.g. `python.install` missing, so `typsphinx` import silently fell back to a stale PyPI wheel) — verify the install-step log lines show installing from the local checkout, not a PyPI index.
- [ ] **PDF is served from RTD:** Verify the *actual byte content* is the typstpdf-generated PDF (check page count/size against the known `docs-pdf` CI output), not a RTD-default LaTeX-built PDF that happened to also succeed.
- [ ] **ja translation "works":** Verify by reading rendered Japanese text on `/ja/latest/`, not just "build green" — a build can succeed while emitting 100% English content (Pitfall 3).
- [ ] **linkcheck job "covers" the #119 class of bug:** It does not, by construction (Pitfall 5) — verify the README/pyproject URL rewrites separately with a real HTTP check.
- [ ] **Orphan docs "resolved":** Verify the collateral test files (`test_documentation_usage.py`, `test_documentation_installation.py`) were also handled, not just the `.rst` files — a green `pytest` run after deletion is the actual proof, not the deletion commit itself.
- [ ] **`stable` "is the default version":** Verify `stable` actually resolves to real content, not a 404/empty-placeholder, at the moment this is declared done — this is only true after the `v0.6.4` tag exists.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|------------------|
| Wrong RTD project slug picked | MEDIUM | Email `support@readthedocs.org` to request a slug change (documented supported path), or accept the slug and never re-migrate; either way, don't compound it by publishing links to the wrong slug before confirming |
| `formats: [pdf]` added and RTD's LaTeX build breaks the pipeline | LOW | Remove the `formats:` key; re-verify the custom `build.jobs` PDF step alone still populates `$READTHEDOCS_OUTPUT/pdf/` |
| `SPHINX_LANGUAGE`→`READTHEDOCS_LANGUAGE` fix shipped after ja project already public | LOW | Fix `conf.py`, trigger a rebuild of the ja project; no data loss, just a stale-content window until the next build |
| `gh-pages`/Pages deleted before RTD proven working | HIGH (effectively irreversible per the accepted-consequence decision) | None — this is why Pitfall 7's sequencing matters; if it happens prematurely, the only mitigation is finishing the RTD migration as fast as possible to minimize the dead-docs window |
| Collateral test files left hard-asserting deleted orphan docs | LOW | Delete or repoint the test files in a follow-up commit (as Phase 27 did); cheap once noticed, but "noticed" requires actually running the suite post-deletion |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| 1. `formats: [pdf]` collides with typstpdf | RTD build-establishment phase | Raw RTD build log shows no `latexmk`/`pdflatex`; exactly one PDF artifact, byte-comparable to `docs-pdf` CI output |
| 2. Self-referential extension unimportable | RTD build-establishment phase | Build log shows `typsphinx` installed from the local checkout path; a deliberately-broken `python.install` block reproduces `ModuleNotFoundError` as a negative control |
| 3. ja project silently serves English | ja-translation-project phase | Real rendered `/ja/latest/` page visually confirmed Japanese; `conf.py` reads `READTHEDOCS_LANGUAGE`; RTD admin language dropdown set correctly for the ja project |
| 4. ja versions unsynced with parent | ja-translation-project phase, re-verified at release phase | `/ja/stable/` exists and matches the same tag as `/en/stable/` after the v0.6.4 tag is cut |
| 5. linkcheck doesn't cover README/pyproject | linkcheck CI-job phase + URL-rewrite phase | Explicit separate HTTP-check/grep proof for README/pyproject links; linkcheck job's scope documented as doc-tree-only |
| 6. Deletion-order collateral damage | multilang-removal phase + orphan-docs phase | Repo-wide grep for each deleted identifier returns zero hits; full `pytest` suite green post-deletion, not just the targeted test files |
| 7. Irreversible steps executed out of order | Whole-milestone sequencing (roadmap ordering) | Pages/`gh-pages` deletion phase ordered strictly after RTD-build-proven-green phase; slug confirmed with owner before RTD project creation |
| 8. Native-wheel build unknown / font-availability | RTD build-establishment phase | A real RTD build observed to `pip install typst` from a prebuilt wheel (log line shows `.whl` download, not a `cargo`/source build); downloaded PDF visually/textually compared to the CI baseline |

## Sources

- [RTD Configuration file reference (v2)](https://docs.readthedocs.com/platform/stable/config-file/v2.html) — HIGH confidence, official current docs
- [PR #10115 — PDF/ePub opt-in by default](https://github.com/readthedocs/readthedocs.org/pull/10115) — HIGH, official RTD repo
- [RTD environment-variables reference](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html) — HIGH, official, confirms `READTHEDOCS_LANGUAGE`/`READTHEDOCS_OUTPUT`/`READTHEDOCS_VERSION_TYPE` exact names
- [RTD localization / translation-project guide](https://docs.readthedocs.com/platform/stable/localization.html) — HIGH, official
- [RTD manage-translations-for-sphinx guide](https://docs.readthedocs.io/en/stable/guides/manage-translations-sphinx.html) — HIGH, official
- [RTD Versions reference](https://docs.readthedocs.io/en/stable/versions.html) / [readthedocs.org/docs/user/versions.rst](https://github.com/readthedocs/readthedocs.org/blob/main/docs/user/versions.rst) — HIGH, official, confirms stable-from-tags behavior and deactivated-version 404 behavior
- [RTD FAQ — project slug change process](https://docs.readthedocs.com/platform/stable/faq.html) — HIGH, official
- [RTD custom domains / canonical URLs](https://docs.readthedocs.com/platform/stable/canonical-urls.html) — HIGH, official
- [RTD build-images developer docs](https://dev.readthedocs.io/en/latest/design/build-images.html) — HIGH, official (RTD dev docs), confirms Ubuntu 20.04/22.04/24.04 x86_64 build images
- [PyPI JSON API — `typst` package files](https://pypi.org/pypi/typst/json) — HIGH, primary source, confirms manylinux2014_x86_64 `cp38-abi3` prebuilt wheel exists
- [typst/typst#2818 — silent font-fallback, no warning](https://github.com/typst/typst/issues/2818) — MEDIUM, upstream issue tracker, corroborated by related issues (#4378, #5663, #6010)
- [Sphinx linkcheck anchor false-positive issue #13620](https://github.com/sphinx-doc/sphinx/issues/13620) — MEDIUM, upstream issue tracker (general linkcheck fragility, relevant to advisory-first rollout rationale)
- Repo-internal verification (this research): `grep -rn "github.io" docs/source/` → zero hits (confirms Pitfall 5); `tests/test_documentation_usage.py`/`tests/test_documentation_installation.py` hard-assert `docs/usage.rst`/`docs/installation.rst` existence (confirms Pitfall 6); `docs/source/conf.py:51`, `docs/build_multilang.py:44`, `.github/workflows/docs.yml:29-32,34-43,57-63` (confirms Pitfalls 1-3, 6 code-level claims) — HIGH, direct repo inspection
- `.planning/PROJECT.md` (Current Milestone section + Key Decisions), `.planning/todos/pending/2026-07-25-docs-usage-installation-orphan-class.md`, `.planning/milestones/v0.6.3-phases/27-*` — HIGH, project's own prior-milestone precedent for the exact deletion-order trap class (Pitfall 6)

---
*Pitfalls research for: Read the Docs migration (v0.6.4 milestone), typsphinx*
*Researched: 2026-07-25*
