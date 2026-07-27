# Feature Research

**Domain:** Documentation-hosting-platform migration (GitHub Pages → Read the Docs) for typsphinx v0.6.4
**Researched:** 2026-07-25
**Confidence:** HIGH for RTD platform mechanics (verified against official `docs.readthedocs.com` / `about.readthedocs.com` pages); MEDIUM/LOW flagged inline where only secondary sources were found; anything not directly confirmed is marked **UNVERIFIED**.

> Supersedes the previous (2026-07-23) version of this file, which researched the **v0.6.3 config & docs 実測整合 + captioned tables** milestone (`typst_elements` pass-through, PR#98 captioned tables, docs orphan cleanup). That milestone shipped and is now archived; this version researches the **v0.6.4 Read the Docs migration** milestone.

## How to read this file

Unlike a typical greenfield feature landscape, this migration is *replacing* a hand-rolled system with a vendor platform. So "table stakes" here means "capabilities a reader/maintainer will now expect from *any* RTD-hosted project, and would notice as broken/regressed if missing" — largely a checklist of what RTD gives for free versus what the repo must still wire up. "Differentiators" are real wins over the current GitHub Pages setup. "Anti-features" are RTD offerings this project should explicitly decline.

Every RTD-side item is tagged **[REPO]** (lives in git, automatable, testable) or **[OWNER-MANUAL]** (a web-UI click by the project owner, not expressible in a file, not assertable by CI).

## Feature Landscape

### Table Stakes (Users/Maintainers Expect These From an RTD-Hosted Project)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Flyout menu (version + language switcher, downloads, search) | Every RTD-hosted project has this; a reader landing from a search engine expects to jump versions/languages from any page | LOW | **[REPO]** none needed — RTD's Addons system is enabled by default on all new/imported projects (has been since 2024-10-07, per the `readthedocs/readthedocs.org#11474` deprecation of the old auto-injected `html_context`). It is a client-side JS include RTD serves alongside the docs; typsphinx's `conf.py` needs **zero** flyout-specific code. Confirmed theme-independent — works regardless of `html_theme` (Furo included) |
| Version switcher inside the flyout (`latest`/`stable`) | Readers on old bookmarked URLs need a way to jump to current docs | LOW | **[REPO]** automatic once `latest`+`stable` versions exist and are both "active" (Active/Hidden toggle is dashboard-side, **[OWNER-MANUAL]** one-time, defaults to reasonable). No `html_context` languages/versions list needed — replaces `conf.py:71-89` entirely |
| Language switcher inside the flyout | Same expectation, for translated docs | LOW | **[REPO + OWNER-MANUAL]** — automatic **only after** the ja child project is linked as a Translation of the en parent in RTD's UI (see Q2 below); until linked, there is no language switcher at all, RTD has nothing to switch to |
| Server-side search across the current version | Readers expect a working search box; Sphinx's built-in static-JSON search is what typsphinx ships today via Furo | LOW | **[REPO]** automatic — RTD's Addons "Search as you type" replaces Sphinx's local search index with a server-side (Elasticsearch-backed) search once the project is on RTD; no config needed. Confirmed it explicitly does **not** index PR-preview builds |
| Downloadable PDF from the docs UI | GitHub Pages already copies the typstpdf PDF into `en/`; readers currently expect a PDF link | LOW–MEDIUM | **[REPO]** — RTD's flyout "downloads" section auto-lists whatever exists in `$READTHEDOCS_OUTPUT/pdf/` after the build. Getting typsphinx's own `typstpdf` output there (rather than RTD's default LaTeX-based Sphinx PDF) is `build.jobs.build.pdf` work — see Differentiators, this is the milestone's own stated single technical unknown (does `typst-py`'s wheel run in RTD's build container) |
| `.readthedocs.yaml` present and valid | Mandatory since 2023-09-25; RTD refuses to build without it | LOW | **[REPO]** one-time file; this is scoped work already, not new information |
| Working root URL / correct default version | A docs site whose root 404s or lands on a stale/empty version reads as broken | LOW | **[OWNER-MANUAL]** — Default Version is a per-project dashboard setting (Admin > Advanced Settings or Versions page), decided here as `stable`. See Q4 below for the pre-v0.6.4-tag gap this creates |
| "Edit on GitHub" / view-source link | Standard expectation on any docs-as-code site; typsphinx's Furo theme has no built-in equivalent today | LOW | **[REPO, mostly automatic]** RTD's Addons flyout includes "view and edit on GitHub" per the `readthedocs/addons` feature list. This is populated from the VCS provider info RTD already has once the project is connected via the GitHub integration (repo URL + branch) — **no extra `conf.py` wiring is required** for a standard GitHub-connected project on current RTD (the older `sphinx-rtd-theme`-era pattern of setting `html_context["display_github"]`/`github_repo` is a *pre-Addons* mechanism, superseded). Not independently reproduced in a live RTD project during this research — flagged **UNVERIFIED** for typsphinx's exact Furo+Addons combination, but is the documented default behavior for GitHub-connected projects |

### Differentiators (Real Wins Over the Current GitHub Pages Setup)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| PR preview builds | Currently `docs.yml` only builds docs on a PR as a pass/fail CI gate with no way to *look at* the rendered output before merge — a reviewer has to trust the diff. RTD PR previews render the actual HTML output at a shareable per-PR URL and post it as a PR comment | LOW (config) | **[OWNER-MANUAL]** one checkbox: Settings → "Pull request builds" → "Build pull requests for this project" (requires the GitHub connection already established for step 1). Once enabled it needs **no repo-side workflow file** — this is entirely RTD-side and runs *in addition to*, not instead of, the existing `docs.yml` gate (see Q3 below for exact relationship) |
| Visual diff / docdiff on PRs | Highlights exactly what changed in the rendered HTML between the PR and the current published docs, inline on the preview page | LOW | **[OWNER-MANUAL]**, bundled free with PR previews being enabled — no separate switch |
| Server-side search with analytics | Sphinx's static search (what GitHub Pages serves today) has no query analytics and can't search across translations/versions; RTD's does both | LOW | **[REPO]** automatic once on RTD; analytics dashboard is **[OWNER-MANUAL]** to view (not required for launch) |
| One canonical published PDF surfaced two ways (RTD downloads + GitHub Release) | Today the PDF is *only* on the GitHub Release page (per-tag) and copied manually into the GH-Pages tree; RTD adds a persistent latest-and-stable-version download without extra CI steps once `build.jobs.build.pdf` is wired | MEDIUM | **[REPO]** — this is the milestone's stated single open technical risk: whether `typst-py`'s compiled wheel installs/runs inside RTD's Ubuntu build container (glibc/manylinux compatibility unverified — **UNVERIFIED**, must be proven empirically in Phase work, not assumable from this research) |
| No more hand-rolled multilang machinery to maintain | `docs/build_multilang.py` (180 lines), the `tox -e docs-multilang` env, and `language-switcher.html` + its `html_context`/`html_sidebars` wiring in `conf.py:71-89` are 100% replaced by RTD's own translation-project + Addons flyout | Removal is LOW; the RTD-side translation setup that replaces it is OWNER-MANUAL, see Q2 | Net maintenance burden goes down — no custom script to keep working across Sphinx/Furo upgrades |
| `llms.txt` / Markdown-via-content-negotiation for AI agents | RTD now serves `llms.txt`/`llms-full.txt` and lets any page be fetched as clean Markdown | Automatic | Not requested by this milestone's scope, but a free side effect of migrating — worth a one-line mention in the milestone close notes, not a requirement |

### Anti-Features (RTD Capabilities This Project Should NOT Enable)

| Feature | Why it looks tempting | Why it's wrong here | Alternative |
|---------|---------------------|----------------------|-------------|
| RTD's default Sphinx PDF build (`formats: [pdf]` with no `build.jobs.build.pdf` override) | It's the zero-config way to get a PDF download on RTD | It invokes Sphinx's own LaTeX-based `latexpdf` builder — a completely different, un-dogfooded rendering pipeline. typsphinx's entire value proposition is its own `typstpdf` builder; shipping the *other* builder's PDF on the project's own docs would be a visible self-contradiction (and the LaTeX pipeline needs a heavy TeX toolchain RTD may not have preinstalled for this project) | `build.jobs.build.pdf` overriding the PDF step specifically to run `sphinx-build -b typstpdf` and copy into `$READTHEDOCS_OUTPUT/pdf/` — already the locked scoping decision |
| `sphinx-rtd-theme` | It's RTD's own theme, "obviously" the natural fit for an RTD-hosted project | The docs already use Furo (`conf.py:61`), and RTD's Addons flyout is theme-independent — switching themes buys nothing and is a pure regression (loses Furo's current look, forces a rebuild of any Furo-specific customization). Confirmed via the PyData-theme and sphinx-rtd-theme docs that RTD does not require any specific theme | Keep Furo; do not touch `html_theme` |
| RTD's built-in flyout position/version-sort customization deep-dive | Available in Settings → Addons → Flyout Menu, could theoretically be tuned | Out of scope noise for a hosting migration; the defaults (SemVer sort, default position) match this project's exact `latest`+`stable` model with zero customization needed | Leave all Addons settings at their defaults except the two the milestone explicitly requires (PR builds on, and eventually Default Version → stable) |
| Full ad removal via RTD Business ($50+/mo paid plan) | Would give a fully ad-free, extra-build-resource experience | typsphinx is a free/open-source project with no budget line for this, and EthicalAds on RTD Community is privacy-respecting (no tracking/no data sale) rather than the surveillance-advertising a user might reasonably want to avoid | Stay on RTD Community (free); optionally opt out of *paid* ads only (Admin → Advertising) if the owner wants a slightly plainer page — community ads (promoting other OSS projects, run at RTD's own cost) persist regardless and are not a per-project switch large enough to warrant a requirement here |
| RTD's `readthedocs-sphinx-search` extension for extra in-page "search as you type" UI | Tempting to bolt on for a nicer search UX | Redundant — the equivalent "Search as you type" ships as part of the Addons flyout automatically since the 2024-10-07 default-on migration; adding the older separate extension duplicates functionality that's already free | Do nothing; rely on the built-in Addons search |
| Subprojects feature (RTD's mechanism for combining multiple *unrelated* doc sets under one domain) | Superficially similar-sounding to "Translations" | This is a different RTD feature (for combining separate projects, e.g. plugin docs, under a shared root) — not what typsphinx needs; the correct mechanism for `en`+`ja` is specifically **Translations**, not Subprojects | Use Translations (Settings → Translations on the en parent project), not Subprojects |

## Feature Dependencies

```
.readthedocs.yaml in repo [REPO]
    └──requires──> RTD project exists for "en" (owner creates + connects GitHub) [OWNER-MANUAL]
                       └──requires──> Flyout menu / search / downloads all "just work" [REPO, automatic]
                       └──enables───> PR preview builds (owner flips one checkbox) [OWNER-MANUAL]
                       └──requires──> Default Version = stable (owner sets, after a qualifying tag exists) [OWNER-MANUAL]

RTD project exists for "ja" (owner creates, sets Language=ja) [OWNER-MANUAL]
    └──requires──> linked as Translation of the "en" parent (owner clicks, on en's Settings > Translations) [OWNER-MANUAL]
                       └──enables───> Language switcher appears in flyout for BOTH projects [REPO, automatic once linked]
    └──requires──> docs/locale/ja/ .mo files committed/buildable — already true (13 .po catalogs via sphinx-intl) [existing]

READTHEDOCS_LANGUAGE env var wiring in conf.py [REPO]
    └──replaces──> SPHINX_LANGUAGE env var (build_multilang.py's mechanism) [DELETED]

build.jobs.build.pdf: sphinx-build -b typstpdf → $READTHEDOCS_OUTPUT/pdf/ [REPO]
    └──requires──> typst-py wheel installs/runs in RTD's build container [UNVERIFIED — the milestone's stated technical unknown]
    └──replaces──> docs.yml's "Copy PDF to multi-language build" step [DELETED, GH-Pages-specific]
    └──does NOT replace──> tox -e docs-pdf CI regression gate (kept per locked scoping) or Release-tag PDF attachment (kept)

Deletion of build_multilang.py / language-switcher.html / html_context languages / html_sidebars wiring [REPO]
    └──requires──> RTD translation projects (en+ja) already reachable, else the language switcher disappears entirely with nothing replacing it
```

### Dependency Notes

- **`.readthedocs.yaml` requires an RTD project to exist first** — the file alone does nothing; someone must import the GitHub repo into RTD's dashboard before any build happens. This is the very first owner-manual step and blocks everything else.
- **The ja translation project's language switcher depends on being linked, not just created.** Creating a second RTD project with `Language: Japanese` produces an *independent*, unlinked docs site at its own default RTD subdomain — it does **not** automatically appear in the en parent's flyout, and does **not** get the `/ja/` path relationship, until the owner explicitly adds it as a Translation on the parent's Settings → Translations page. Getting only halfway through this (project created, not linked) is a real "stranded migration" failure mode the owner was warned about in milestone scoping — worth calling out explicitly as a requirement checkpoint, not just a checkbox.
- **PDF-on-RTD enhances but does not require the flyout** — the flyout downloads section will simply show fewer formats if the PDF build.jobs override fails; it degrades gracefully (HTML-only downloads), it does not block the HTML build. This means the milestone's "single technical unknown" (`typst-py` in RTD's container) is a de-risked bet: worst case, ship HTML-only on RTD initially and keep iterating on the PDF job separately, rather than the whole migration hinging on it.
- **PR preview builds conflict with nothing** — they are additive to the existing `docs.yml` PR gate (see Q3 answer below), not a replacement, so there's no ordering dependency with the GitHub Pages removal work.
- **Deleting the hand-rolled multilang machinery is safe only after both RTD projects are live and linked** — doing the deletion first (as a pure cleanup PR) with no functioning RTD translation projects yet would leave the ja documentation completely unreachable by any switcher, a real regression versus today's (clunky but functional) JS-redirect + sidebar switcher.

## Detailed Answers to the Research Questions

### 1. RTD platform features that replace hand-rolled machinery — what a reader actually sees

| Hand-rolled piece today | RTD replacement | Automatic or config? | Lost behavior? |
|---|---|---|---|
| `build_multilang.py`'s language-detection JS redirect at the site root | RTD's own root-URL → Default Version redirect (no language auto-detection — it redirects to a *version*, not a *language*; each RTD project/language has its own separately-served root) | **[OWNER-MANUAL]** for Default Version; automatic otherwise | **Yes, one piece of behavior is lost and should be called out to the owner explicitly**: the current script's `navigator.language`-based auto-redirect (send a Japanese-browser visitor straight to `/ja/`) has **no RTD equivalent**. RTD's flyout lets a reader *manually* switch language once they land, but does not auto-detect browser language at the root. A `ja`-language visitor landing on the `en` parent's root will see English first and must click through the flyout. This is a real, if minor, UX regression versus today — worth one line in the roadmap/requirements doc rather than silently dropped |
| `language-switcher.html` + `html_context`/`html_sidebars` (`conf.py:71-89`) | RTD Addons flyout's translation switcher | Automatic, once translation projects are linked | No loss — RTD's version is arguably richer (also switches versions, not just language, from the same UI) |
| `.nojekyll` (GitHub Pages Jekyll-bypass marker) | N/A — RTD doesn't run Jekyll, the file is meaningless there | N/A | No loss, pure dead weight once GH Pages is removed |
| `peaceiris/actions-gh-pages` deploy step | RTD's own build+publish pipeline (triggered by its GitHub webhook on push, not by `docs.yml`) | **[OWNER-MANUAL]** initial connection; automatic thereafter | No loss — this is a straight swap of "who deploys" |
| Furo's language switcher styling (`custom.css`) | Addons flyout has its own styling, independent of Furo | N/A, becomes dead CSS | Check `docs/source/_static/custom.css` for language-switcher-specific rules that become orphaned — not read as part of this research's required files, flag for the phase that deletes the switcher template to also grep this file |
| "Edit on GitHub" — **currently absent** from typsphinx's Furo docs (Furo core has no such link, GH Pages had no such feature) | RTD Addons flyout's "view and edit on GitHub" | Automatic once GitHub-connected, per RTD's Addons feature list | **New capability, not a replacement** — call this out as a genuine feature the migration adds "for free," worth listing in requirements as a nice-to-have observed effect, not a thing to build |
| Search (Sphinx static local search via Furo) | RTD server-side search (Addons "Search as you type") | Automatic | No loss; net improvement — cross-version/cross-translation search, RTD notes this is impossible with pure static Sphinx search |
| PR-time build as pass/fail-only gate (`docs.yml`) | Stays as-is; RTD PR previews are additive (see Q3) | N/A | No loss — nothing is removed here per the locked scope |

### 2. Translation-project setup — the exact step list, repo vs. owner-manual

**Repo-side (automatable, testable):**
1. `.readthedocs.yaml` in the repo root, targeting the `en` build, with `build.jobs` overriding the PDF step per Differentiators above.
2. `conf.py:51` changed from reading `SPHINX_LANGUAGE` to reading `READTHEDOCS_LANGUAGE` (RTD's own build-time env var, confirmed present in RTD's build environment: `READTHEDOCS_LANGUAGE` — "The RTD language slug of the project which is being built," e.g. `en`) — falling back to a literal default (e.g. `"en"`) for local/non-RTD builds so `sphinx-build` still works outside RTD.
3. This is the **entire** repo-side footprint for translations — RTD's translation-linking model has **no `.readthedocs.yaml` key** for declaring a parent/child relationship; that relationship lives purely in RTD's database, set via its web UI. There is nothing to "get right" in a config file here beyond each project independently building for its own language.

**Owner-manual (RTD web UI, cannot be scripted or asserted by CI) — in dependency order:**
1. **Create the `en` project on RTD** — Import a Project → connect the GitHub repo (first-time GitHub OAuth connection to RTD if not already done) → confirm project name/repo URL/default branch. This creates the parent project and, on a GitHub-connected import, auto-configures the webhook (no manual webhook setup needed for GitHub specifically — confirmed automatic for GitHub/GitLab/Bitbucket connected imports; manual webhook config is a fallback path only needed for unsupported/disconnected providers, not applicable here).
2. **Create a second, separate RTD project for `ja`** — Import the *same* GitHub repository a second time as its own project (RTD explicitly supports re-importing the same repo under a different project slug/name for this purpose — confirmed by the community walkthrough pattern of appending a language suffix to the project name, e.g. `typsphinx-ja`). On this second project's Admin/import settings, set **Language: Japanese**.
3. **Link them** — On the `en` (parent) project's **Settings → Translations** page, click "Add translation," choose the `ja` project from the dropdown, save. This is the step that actually produces the `/ja/latest/` URL relationship and populates the flyout's translation switcher on both projects. **This is the step most likely to be missed or done in the wrong order** (owner scoping doc already flags this) — doing steps 1–2 without step 3 leaves two working-but-unlinked docs sites with no switcher between them.
4. **Set the Default Version to `stable`** on the `en` parent project — Settings → (Versions page or Advanced Settings, terminology varies by RTD dashboard version) → Default Version → `stable`. Per Q4, this should be deferred/sequenced against when a real `stable` version actually exists (see below) — flipping it too early produces a broken/empty root landing page.
5. **Enable PR builds** on the `en` project (see Q3) — a fifth, independent one-time checkbox, not dependent on 1–4 but naturally done in the same setup session.
6. **Set the repository's GitHub "About" Website field** to the new RTD URL (separate from RTD itself — this is a GitHub repo-settings field, not an RTD dashboard field, but equally owner-manual and equally a one-time click, called out in the milestone's own scope for closing Issue #119).

None of steps 1, 2, 3, 4, or 6 above can be verified by any test in this repo — they are asserted only by an owner screenshot/confirmation or by the requirement-definition phase writing them as explicit manual checklist items with no automated acceptance criterion, exactly as the milestone context already anticipated.

### 3. PR preview builds — enable, URL, relationship to `docs.yml`

- **Enable:** one dashboard checkbox — Settings → Pull request builds → "Build pull requests for this project" (`[OWNER-MANUAL]`, confirmed requires the GitHub connection from step 2/1 above; GitHub and GitLab supported, Bitbucket is not).
- **URL:** preview builds are served from a **separate domain** than production docs — `org.readthedocs.build` (Community) / `com.readthedocs.build` (Business) — specifically so that "anyone who can open a PR" (i.e., in an open-source project, effectively anyone) triggering a build can't accidentally serve content under the project's real production domain. RTD posts the exact preview link as an automatic PR comment plus a GitHub commit-status/check.
- **Relationship to the existing `docs.yml` PR gate:** **complementary, not a replacement.** `docs.yml`'s PR-time job continues to serve as the pass/fail CI gate (build must not error) — that's a repo-controlled, required-status-check assertion. RTD's PR preview build is a *separate*, RTD-triggered build (via its own webhook, independent of GitHub Actions) that a reviewer can click through to see the actual rendered HTML before merging; it is not wired into GitHub's required-checks mechanism as a blocking gate by default (it does post a status, but treating it as a merge-blocking requirement is a separate, additional GitHub branch-protection decision this milestone doesn't need to make). Two explicitly-confirmed constraints worth carrying into requirements: **PDF is not built on PR previews** (HTML only, to keep build times down) — so the PR preview will never demonstrate the typstpdf-on-RTD path, only `docs.yml`'s `tox -e docs-pdf` job does that — and **search is not indexed** on PR-preview builds.

### 4. Version handling — what a reader sees before v0.6.4 is tagged, and the stable-empty window

- Per the milestone's own already-measured constraint, RTD refuses builds without `.readthedocs.yaml`, so **no tag before v0.6.4 can ever be built as a version on RTD** — this isn't a temporary gap, it's permanent for those historical tags.
- Mechanically: **`latest` will build and populate immediately** (it tracks the default branch, `main`, which will have `.readthedocs.yaml` as soon as this milestone merges) — a reader visiting `/en/latest/` gets working docs right away, before any v0.6.4 tag exists.
- **`stable` will not exist as an active version at all until the v0.6.4 tag is pushed** — RTD's stable-version logic requires *some* qualifying semver/PEP440 tag to exist in the repo; with none buildable, there is no `stable` version to activate, not merely an "empty" one.
- Confirmed from RTD's own versions doc: **the root-URL redirect always goes to whatever the Default Version setting says**, even if that version doesn't exist/isn't active yet — meaning if the owner sets Default Version → `stable` *before* the v0.6.4 tag lands, root-URL visitors get a broken/404-like experience (redirecting to a non-existent version) for the entire window between "RTD project created" and "v0.6.4 tagged."
- **Conventional way to handle this** (synthesized from the mechanics above, since RTD's docs don't give an explicit "how to sequence a fresh migration" playbook): keep **Default Version = `latest`** through the RTD project setup and through however much of the milestone happens before the release phase, and only flip Default Version → `stable` **after** the v0.6.4 tag is pushed and RTD has built it successfully (confirmable by checking the Versions page shows `stable` as Active). This is a **sequencing note for the requirements/roadmap**, not a new capability — it should land as an explicit last-phase step ("flip Default Version to stable, verify root URL resolves") rather than a same-day owner action alongside project creation, to avoid a self-inflicted dead-root-URL window that would look worse than what GitHub Pages had.

### 5. Categorization

See the three tables above (Table Stakes / Differentiators / Anti-Features). Summary of the sharpest calls:
- **Anti-feature, explicitly locked by scoping already:** RTD's own LaTeX-based default Sphinx PDF builder — never enable plain `formats: [pdf]` without the `build.jobs.build.pdf` override, or the published PDF stops being typsphinx's own dogfooded output.
- **Anti-feature:** `sphinx-rtd-theme` — no reason to switch off Furo; RTD doesn't need or reward it.
- **Anti-feature (soft):** chasing full ad removal via a paid RTD Business plan — not proportionate for this project; RTD Community's EthicalAds model is already privacy-respecting and free community ads aren't switchable off per-project regardless.
- **Table stakes with a real gap:** the flyout's automatic version/language switching and search are the free wins that justify most of the deletion work, but the browser-language auto-redirect behavior of `build_multilang.py`'s root page has no RTD equivalent and is a genuine (minor) UX regression to note rather than silently accept.

### 6. Dependencies on the existing setup that constrain or complicate each capability

- **`conf.py:51`'s `SPHINX_LANGUAGE` env-var read** is the single existing hook every language-related RTD capability depends on being correctly repointed at `READTHEDOCS_LANGUAGE` — get this wrong and both the `en` and `ja` RTD projects would build with the wrong (or a hardcoded) language, silently breaking the very translation-switcher capability the migration is going for.
- **The `html_context`/`html_sidebars` wiring (`conf.py:71-89`) and `language-switcher.html`** are pure liabilities from RTD's perspective — they don't interoperate with or enhance the Addons flyout, they're simply dead code to delete, but they must not be deleted *before* the RTD translation projects are live and linked (see Dependency Notes) or the `ja` docs become unreachable in the interim.
- **The dogfooded `tox -e docs-pdf` / `typstpdf` regression gate** is exactly what makes the `build.jobs.build.pdf` RTD override low-risk to attempt — it's already a proven, CI-tested command (`sphinx-build -b typstpdf`), so the RTD-side risk is narrowly about the *build environment* (does `typst-py`'s compiled wheel run under RTD's container), not about the command's correctness.
- **The `docs/locale/ja/` `.po`/`.mo` catalogs (13 files, via sphinx-intl)** are exactly what RTD's per-project `Language` setting needs already in place — no new i18n infrastructure is required by the RTD migration itself, only the delivery mechanism (RTD translation project vs. hand-rolled second `sphinx-build` invocation) changes.
- **`docs.yml`'s existing structure** (build-multilang → docs-pdf → gh-pages-deploy → release-upload) needs the `docs-multilang` job replaced with a plain `docs-html` build per the locked scoping decision — this is a prerequisite for RTD's own webhook-triggered build becoming the actual production pipeline; `docs.yml` after this milestone becomes a CI-only regression gate (matching what RTD independently rebuilds), not the deploy mechanism.

## Sources

- https://docs.readthedocs.com/platform/latest/flyout-menu.html — HIGH (official RTD user docs)
- https://docs.readthedocs.com/platform/latest/addons.html — HIGH (official)
- https://github.com/readthedocs/addons — HIGH (official RTD GitHub org, Addons feature list incl. "view and edit on GitHub")
- https://docs.readthedocs.com/platform/latest/pull-requests.html — HIGH (official)
- https://docs.readthedocs.com/platform/stable/guides/pull-requests.html — HIGH (official how-to guide)
- https://docs.readthedocs.com/platform/stable/localization.html — HIGH (official)
- https://docs.readthedocs.com/platform/latest/guides/manage-translations-sphinx.html — HIGH (official)
- https://docs.readthedocs.com/platform/latest/versions.html — HIGH (official)
- https://docs.readthedocs.com/platform/stable/build-customization.html — HIGH (official)
- https://docs.readthedocs.com/platform/latest/downloadable-documentation.html — HIGH (official)
- https://docs.readthedocs.com/platform/stable/config-file/v2.html — HIGH (official config reference)
- https://about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs — HIGH (official RTD blog, confirms `build.pdf` override with a worked rinohtype-style example directly analogous to typsphinx's typstpdf case)
- https://docs.readthedocs.com/platform/stable/advertising/ethical-advertising.html — HIGH (official)
- https://docs.readthedocs.com/platform/stable/about/index.html — HIGH (official, Community vs. Business revenue model)
- https://www.ethicalads.io/publishers/readthedocs — MEDIUM (vendor case-study page, corroborating but not the primary source)
- https://docs.readthedocs.com/platform/latest/tutorial/index.html — HIGH (official, import/webhook flow)
- https://docs.readthedocs.com/platform/stable/guides/setup/git-repo-manual.html — HIGH (official, confirms automatic webhook for GitHub-connected imports vs. manual fallback)
- https://github.com/readthedocs/readthedocs.org/issues/11474 — HIGH (official RTD repo issue, confirms Addons-enabled-by-default since 2024-10-07 and the retirement of the old `html_context` auto-injection / theme-forcing behavior)
- https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/readthedocs.html — MEDIUM (third-party theme docs, corroborates flyout is independent of/can conflict with a theme's own switcher — used to confirm Furo compatibility reasoning, not itself about Furo)
- https://kattni.com/mkdocs-po-i18n-mkdocs-translations-with-po-files-and-read-the-docs — LOW (community blog walkthrough; used only to corroborate the practical "re-import same repo as second project" mechanic for translations, which the official docs describe more abstractly)
- Stack Overflow threads on `github_url`/`display_github` — LOW (community answers; cited only to establish that the *pre-Addons* "Edit on GitHub" mechanism existed historically and to distinguish it from the current Addons-based automatic behavior)

**Explicitly UNVERIFIED (not confirmed by any source read during this research, flagged per the quality gate rather than glossed over):**
- Whether `typst-py`'s compiled wheel actually installs and runs inside RTD's standard `ubuntu-22.04`/`ubuntu-24.04` build image (glibc version, manylinux tag compatibility) — this is the milestone's own named "single technical unknown" and nothing in RTD's public docs confirms or denies it; it can only be resolved by an actual `build.jobs` attempt in the target milestone phase.
- Whether the Addons "view and edit on GitHub" flyout link requires any `.readthedocs.yaml`/`conf.py` field beyond a standard GitHub-connected project (i.e., whether it needs the repo's branch/path auto-detected vs. needing an explicit VCS config block) — documented as automatic in RTD's feature list, but not independently reproduced against a live Furo+typsphinx project during this research.
- Exact current dashboard label/location for "Default Version" (Admin > Advanced Settings vs. a dedicated Versions page) — RTD's UI has been reorganized across versions of its own docs; the *existence and effect* of the setting is confirmed, the precise click-path label is not pinned to today's exact UI and should be confirmed by the owner during the actual manual step, not assumed from this research.

---
*Feature research for: typsphinx v0.6.4 — Read the Docs migration*
*Researched: 2026-07-25*
