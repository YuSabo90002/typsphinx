# Feature Research: Per-Document Templates in Multi-Output Doc Toolchains

**Domain:** Documentation-toolchain output/template configuration (Sphinx builders, Pandoc, Quarto,
MkDocs, Asciidoctor, Hugo, Typst Universe)
**Researched:** 2026-08-15
**Confidence:** HIGH for Sphinx's own precedent (primary-source `.rst`/`.py` quotes from
`sphinx-doc/sphinx`, verified 2026-08-15 against the `master` branch, current 9.x); MEDIUM for
non-Sphinx systems (official docs quoted directly, cross-checked across ≥2 pages per claim, but not
verified against the tools' own source code the way Sphinx was).

## Answering the four research questions directly

### 1. Sphinx's own builders — per-output-document variation vs global-only

Quoted verbatim from `doc/usage/configuration.rst` on `sphinx-doc/sphinx` `master` (tracks current
9.x) and `sphinx/builders/latex/__init__.py`:

| Config | Tuple shape / type | Per-document? | Quote |
|---|---|---|---|
| `latex_documents` | `Sequence[tuple[str, str, str, str, str, bool]]` = `(startdocname, targetname, title, author, theme, toctree_only)` | **YES** — element [4] is a per-entry theme-name override | *"theme — LaTeX theme. See `latex_theme`."* Confirmed by source: `default_latex_documents()` builds the fallback tuple as `(root_doc, target, title, author, config.latex_theme)` — i.e. the per-entry slot's default **is** the global value, exactly the "reserved key defers to global" shape typsphinx is proposing. |
| `latex_theme` | `str`, default `'manual'` | Global only (but is the fallback value each per-entry `theme` slot resolves to when equal to it) | *"The 'theme' that the LaTeX output should use. It is a collection of settings for LaTeX output (e.g. document class, top level sectioning unit and so on). The bundled first-party LaTeX themes are manual and howto."* |
| `latex_theme_options` | `dict[str, Any]`, default `{}` | **Global only** — one dict applies to whichever theme is selected build-wide, not per-entry | *"A dictionary of options that influence the look and feel of the selected theme. These are theme-specific."* Validated at `config-inited` — `validate_latex_theme_options()` drops (and warns on) any key not in `Theme.UPDATABLE_KEYS`: `"Unknown theme option: latex_theme_options[%r], ignored."` — a **fail-loud-ish but not fail-hard** precedent (warn + drop, not abort). |
| `latex_theme_path` | `list[str]`, default `[]` | Global only — a directory-scan registry, not a dict | *"A list of paths that contain custom LaTeX themes as subdirectories."* Each subdirectory name becomes a usable theme name; the same convention as `html_theme_path`. |
| `latex_docclass` | `dict[str, str]`, default `{}` | Global only, and fixed-shape (exactly two keys) | *"A dictionary mapping `'howto'` and `'manual'` to names of real document classes that will be used as the base for the two Sphinx classes. Default is to use `'article'` for `'howto'` and `'report'` for `'manual'`."* This is NOT a general per-key registry — it only ever has two meaningful keys. |
| `man_pages` | `Sequence[tuple[str, str, str, str, str]]` = `(startdocname, name, description, authors, section)` | **NO per-document template element at all.** No `man_theme`, no styling hook per entry. | Full tuple quoted above; there is nothing analogous to `theme`. |
| `texinfo_documents` | `Sequence[tuple[str, str, str, str, str, str, str, bool]]` = `(startdocname, targetname, title, author, dir_entry, description, category, toctree_only)` | **NO** per-document template element | Full tuple quoted above; same absence as `man_pages`. |
| `epub_theme` | `str`, default `'epub'` | N/A — EPUB has no multi-master concept (`epub_documents` does not exist; one build = one `.epub`), so "per-document" doesn't apply | *"The HTML theme for the EPUB output... This defaults to `'epub'`."* |

**Historical precedent for widening a tuple slot's meaning (directly on point for this milestone):**
pre-3.0 Sphinx's `latex_documents` 5th element was literally called **`documentclass`**, and its
value was a raw string, mostly `'manual'`/`'howto'` but explicitly open-ended: *"documentclass:
Normally, one of `'manual'` or `'howto'` (provided by Sphinx). Other document classes can be given,
but they must include the 'sphinx' package..."* — i.e., historically the slot was **accepted almost
as free text**, much like typsphinx's current "usually `'typst'` — accepted and ignored." In Sphinx
3.0 this same tuple position was formalized into a **named registry key** resolved against
`latex_theme`/`latex_theme_options`/`latex_theme_path`, with a matching per-entry override. **This is
the closest one-to-one precedent for typsphinx's exact move**: an already-existing, loosely-defined
tuple slot gets promoted into a strict per-entry registry-key lookup, with the global config value
becoming the fallback default. Sphinx did this once and never walked it back.

**Verdict for Q1:** only the LaTeX builder supports true per-output-document template variation, and
it does so with exactly the shape typsphinx is proposing — a tuple element naming a registry key,
global config as the fallback/default value for that key. `man_pages` and `texinfo_documents` prove
the alternative (no per-document hook at all) is also a legitimate, shipped design when a format has
no real "theming" concept — relevant if typsphinx ever considers whether every builder needs this,
but typst output clearly does (it already has `typst_template`/`typst_package`, so removing per-doc
variation isn't on the table).

### 2. Non-Sphinx systems — shape of the mapping

| System | Mechanism | Shape | Quote / evidence |
|---|---|---|---|
| **Pandoc** | `--template=FILE`, or a `defaults` YAML file's `template:` key | **Per-invocation flag / per-defaults-file key**, not a registry inside one config. Convention-over-configuration fallback: dropping `templates/default.FORMAT` into the user data directory silently becomes the default for that writer with **no key at all**. | *"A custom template can be specified using the `--template` option... you can also override the system default templates for a given output format FORMAT by putting a file `templates/default.FORMAT` in the user data directory."* Different outputs from one source get different templates by running pandoc **multiple times** with different `--template`/defaults-file arguments — there is no single config expressing "doc A uses template X, doc B uses template Y" the way Sphinx's tuple does. |
| **Quarto** | `format:` key, nestable per-format under `_quarto.yml` (project), `_metadata.yml` (directory), or the document's own YAML frontmatter | **Named registry keyed by *format*, not by *document*** (`html:`, `pdf:`, `epub:`, each a themed sub-map), with **directory-level override files** (`_metadata.yml` per subfolder) as the closest thing to "this subset of documents gets this config." No first-class "document A vs document B, same format, different theme" key. | *"You can set defaults for more than one format in `_quarto.yml` by nesting them under `format`"*; and, matching typsphinx's own `params`-exclusivity decision almost exactly: *"The one exception to metadata merging is `format`. If the document-level YAML defines a format, it must define the complete list of formats to be rendered."* — Quarto independently arrived at "declaring the key at all replaces the whole set, no partial merge," the same rule typsphinx already applies to `params`. |
| **MkDocs** | `theme.name` / `theme.custom_dir` | **Single global theme per build, full stop.** Multiple templates for one content tree require **multiple separate top-level config files** and separate `mkdocs build -f siteN.yml` invocations — explicitly the maintainer's own answer to "can I have multiple themes for one docs/ tree," not a registry inside one config. | GitHub maintainer (`lovelydinosaur`) on a "Multiple Themes" feature discussion: *"You could have this kind of layout... `site1.yml site2.yml site3.yml docs/...` `mkdocs -f site1.yml` — Each config file could also point to a different custom theme directory."* This is the strongest **negative** precedent found: a mature, widely-used tool with real demand for this exact feature chose N-builds-of-one-config over a per-document/per-output registry inside one config. |
| **Asciidoctor PDF** | `-a pdf-theme=NAME` / `--theme NAME` document attribute, resolved against `pdf-themesdir` | **Per-CLI-invocation attribute**, resolvable per document because Asciidoctor is normally invoked once per source file already (unlike Sphinx/typsphinx's one-build-many-masters model). A theme file can also `extends:` another theme file for composition. | *"asciidoctor-pdf -a pdf-theme=basic -a pdf-themesdir=resources/themes doc.adoc"* — no in-repo multi-document registry exists because there's no multi-document build unit to register against. |
| **Hugo** | `layouts/<type>/<kind>.html` directory convention + front-matter `type:`/`layout:` override, searched via a fixed **lookup-order** algorithm | **Directory-convention registry**, not an explicit dict: the "key" is implicit in a content file's path/front matter (`type`, `layout`), and Hugo walks a fixed precedence list (`layouts/<type>/<kind>.html` → `layouts/_default/<kind>.html` → theme equivalents) until it finds a match. | *"You cannot change the lookup order to target a content page, but you can change a content page to target a template. Specify `type`, `layout`, or both in front matter."* This is the closest analog to "per-document key selects from a registry with a global fallback," but the registry is a filesystem convention (directory tree), not a `dict` in one config file. |
| **Typst Universe `template` packages** | `typst.toml`'s `[template]` table: `path` (dir copied into the user's new project) + `entrypoint` (the file inside it Typst opens) | **One template = one package = one directory, copied wholesale.** No per-document selection concept exists at the Typst-package level at all — that's exactly the layer typsphinx itself sits above and is building the missing per-document dispatch for. | *"`path`: The directory within the package that contains the files that should be copied into the user's new project directory. `entrypoint`: A path relative to the template's path that points to the file serving as the compilation target."* This directly validates typsphinx's **"resolved template's parent directory is copied wholesale"** output rule (D-in-milestone-brief) — it is exactly how Typst's own template convention already behaves at the single-package level; typsphinx is only adding the *selection* layer on top (which key's bundle to copy for which master), not inventing a new bundling convention. |

**Shape taxonomy answer:** three shapes were found in the wild —
1. **Inline per-invocation** (Pandoc `--template`, Asciidoctor `-a pdf-theme`) — works because the
   tool is normally invoked once per output anyway.
2. **Directory convention, positionally resolved** (Hugo lookup order, Typst package `path`) — no
   explicit registry dict; the "key" is a path/front-matter value walked against a fixed search order.
3. **Named registry inside one config, referenced by key** (Sphinx `latex_documents[4]` → `latex_theme`
   family; Quarto `format:` sub-maps) — the shape typsphinx is proposing.
Shape 3 is real and shipped (Sphinx), but it is the **least common** of the three — most tools that
build many-outputs-from-one-source (Pandoc, Asciidoctor) sidestep the "one config, many named
templates" problem entirely by re-invoking the tool per output instead. MkDocs explicitly rejected
folding it into one config for its one-output-per-build model.

### 3. Table stakes vs differentiators for a per-document-template feature

| Item | Category | Precedent |
|---|---|---|
| Fallback to a sane default when a document doesn't specify a template | **Table stakes** | Sphinx: `default_latex_documents()` always fills the per-entry `theme` slot with `config.latex_theme`; Hugo: lookup order always bottoms out at `layouts/_default/`. typsphinx's `"typst"` reserved key does exactly this. |
| Error (not silent fallback) on an unregistered/typo'd key | **Table stakes** | Sphinx: `validate_latex_theme_options()` warns+drops unknown *option* keys (not unknown *theme names* — an unknown `latex_theme` string is a harder LaTeX-level failure since it can't find the theme's `theme.conf`). typsphinx's own precedent (CONF-04's unknown-`typst_elements`-key `ExtensionError`) is a stricter bar than Sphinx's own warn-and-drop, and matches the milestone's "fail-loud" decision — reasonable to hold to a higher bar than upstream Sphinx here. |
| Per-document assets travelling with the chosen template | **Table stakes** | Typst's own `[template]` `path` convention makes this the default expectation at the package level already; typsphinx's "copy the bundle wholesale" rule matches it exactly. |
| Reusing one named template across several documents (many masters → one registry key) | **Table stakes**, not a differentiator | Quarto's `format:` sub-maps are shared across every document unless overridden per-document/per-directory; nothing in the precedent suggests 1:1 document-to-template cardinality is expected — N:1 is the norm. |
| Per-document page size / paper size | **Differentiator** | No system surveyed exposes this as *only* a per-document-template axis distinct from the template's own logic — Sphinx's `latex_elements`/`typst_elements` equivalent is global (this milestone explicitly keeps `elements` global too, matching precedent, not diverging). |
| Per-document language | **Differentiator**, and notably **absent from every precedent surveyed** — no tool's per-document/per-format registry carries a language override independent of the whole-project locale setting (Quarto: `lang` is global per `_quarto.yml`; Sphinx: `language` is a single project-wide config value with no per-`latex_documents`-entry override). This is out of scope for the current milestone and consistent with every precedent's own scope choice. | — |
| A distinct template-function-parameter set per registry entry (the `params` route) | **Differentiator** — none of Pandoc/Quarto/Hugo/Asciidoctor expose "this named template gets this literal argument dict," because none of them have Typst's typed-function-call template model. This is a typsphinx-specific capability inherited from the pre-existing `typst_template_function` mechanism, not something borrowed from precedent — call this out to the roadmapper as genuinely novel, not validated by outside prior art. | — |

### 4. Anti-features — what's been added and regretted or explicitly refused

- **MkDocs refused a within-one-config multi-theme registry outright.** The maintainer's answer to a
  real, repeatedly-requested feature ("branded doc sets from one content tree") was: don't add a
  per-page/per-output theme key to `mkdocs.yml` — run the builder N times with N separate top-level
  config files instead. Read as: **when a tool's output unit is fundamentally "one site," bolting a
  named-registry selector onto the single config is the wrong shape** — the config file itself should
  be the unit of "which template." typsphinx doesn't have this problem because its output unit is
  already N PDFs from one `conf.py` (established at v0.8.0), so the "config file = one theme" workaround
  doesn't apply — but this is the strongest evidence *against* assuming per-document template registries
  are the default expected shape; they're conditional on the tool already having a multi-output-per-build
  unit, which typsphinx does and MkDocs doesn't.
- **Sphinx's `latex_docclass` is a cautionary shape, not a template registry to imitate.** It looks
  like a registry (`dict[str, str]`) but is fixed at exactly two meaningful keys (`'howto'`, `'manual'`)
  — extending it to arbitrary user-defined keys was never done; instead Sphinx built the *separate*,
  properly-general `latex_theme`/`latex_theme_path` system for that. Lesson for typsphinx: don't grow
  `typst_document_templates` keys by special-casing a fixed enum later — the milestone's decision to
  make it a genuinely open `dict[str, ...]` from day one, with `"typst"` as the only reserved value,
  avoids repeating this Sphinx wrinkle.
- **Quarto's partial-merge trap on `format:`** — silently discarding formats not re-declared at a more
  specific level when a document-level `format:` key is present at all — is exactly the failure mode
  typsphinx's own docs already warn about for `params` (`configuration.rst`'s "silent trap" warning on
  partial migration). No new anti-feature to add here; this milestone's design already avoids repeating
  it for the *new* registry (declaring `template`/`package` xor, and `template_function` either absent
  or complete, mirrors the same all-or-nothing rule Quarto had to document as a gotcha rather than fix).
- **No evidence found of any surveyed tool having added and then removed a per-output template
  selector.** The closest thing to a "regretted" per-document knob is Sphinx's `latex_theme_options`
  warn-and-drop-unknown-key behavior, which is not a removal, just weaker validation than typsphinx's
  own `ExtensionError` bar — nothing suggests the *existence* of per-document template selection itself
  was ever walked back once shipped (LaTeX's `theme` slot has existed unchanged since 3.0, i.e. many
  years, through the current 9.x line).

## Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---|---|---|---|
| Reserved "use the global config" key with zero-edit backward compatibility | Sphinx's own `latex_documents` per-entry default falls back to `config.latex_theme`; every existing `conf.py` with a bare four-tuple keeps building | LOW — already the milestone's `"typst"` design | Directly matches `default_latex_documents()`'s fallback behavior |
| Fail-loud on unregistered registry key / typo | typsphinx's own CONF-04 precedent, stricter than Sphinx's warn-and-drop | LOW | Milestone already commits to `ExtensionError` |
| Per-entry bundle (assets travel with the chosen template) | Typst's own `[template]` package convention already does this at the single-package granularity | MEDIUM — the "copy parent directory wholesale, no exceptions" rule this milestone adopts | Validated directly against Typst Universe's own template-package shape |
| N documents sharing one named template | Quarto's format sub-maps and Sphinx's `latex_theme` are both N:1 by default | LOW | Registry-by-key naturally gives this; no extra work needed |

## Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| Literal `params` argument dict per registry entry | No precedent tool has typed Typst-style function-call templates, so this parameter-injection model is typsphinx-specific, inherited from the already-shipped `typst_template_function` | MEDIUM (already exists per-global; extending per-registry-entry is what's new) | Not validated by outside prior art — flag as own design risk, not precedent-backed |
| Per-document template selection inside a single build, without re-invoking the tool | Pandoc/Asciidoctor require a separate CLI invocation per template; MkDocs requires a separate config file per theme. typsphinx (like Sphinx's LaTeX builder) does it in one `sphinx-build` pass | MEDIUM — already largely built by the v0.8.0 wrapper/content split, which threads the specific `typst_documents` entry into `render_wrapper()` | This is genuinely rarer than the milestone brief's framing suggests; most peers punt to "just run the build twice" |

## Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| Per-document *language* override in the registry | Multi-language project docs feels natural to want per-master | No precedent tool exposes this at the per-output-document granularity (Quarto/Sphinx both keep language whole-project); adding it here would be inventing unvalidated design, not following precedent | Leave `lang` derivation from Sphinx's project-wide `language` as-is (unchanged this milestone); revisit only if demand appears, informed by nothing in this survey |
| Growing the registry into a fixed enum of "blessed" keys (mirroring `latex_docclass`'s `'howto'`/`'manual'` shape) | Feels safer/more guided than open string keys | Sphinx itself moved *away* from this shape (superseded by the general `latex_theme` system); repeating it would be adopting the deprecated-in-spirit half of Sphinx's own history, not the current one | Keep `typst_document_templates` a fully open `dict[str, ...]` with only `"typst"` reserved, as already decided |
| Silent partial-merge when a registry entry declares only some of `template`/`package`/`template_function` | Looks convenient ("just override the one thing you need") | Quarto's own docs had to add an explicit warning for exactly this shape on `format:`; typsphinx already learned this lesson the hard way with `params` exclusivity | Keep the existing all-or-nothing rules (xor on `template`/`package`; `params` presence is the complete-set signal) — already the milestone's design |

## Feature Dependencies

```
typst_document_templates registry (new)
    └──requires──> v0.8.0 wrapper/content split (entry already threaded into render_wrapper())
    └──requires──> existing resolve_template()/TemplateEngine per-key invocation (already per-master-capable post v0.8.0)

Reserved "typst" key defers to global config
    └──requires──> typst_document_templates registry existing at all
    └──enhances──> zero-edit backward compatibility (matches Sphinx latex_documents precedent)

Fail-loud unregistered-key / xor-violation errors
    └──requires──> registry existing
    └──enhances──> matches typsphinx's own CONF-04/BLD-02..04 precedent bar (stricter than Sphinx's own warn-and-drop)

Bundle-copy-wholesale per key ("_template/<key>/")
    └──requires──> registry existing (one bundle root per key, not one global _template.typ)
    └──conflicts──> typst_template_assets (this milestone removes it — no assets key needed once every bundle is copied whole)

Per-entry params (literal template-function arguments)
    └──requires──> existing typst_template_function dict-form / params-exclusivity machinery (TemplateEngine.__init__'s params_specified)
    └──conflicts──> per-entry title/author when params is declared (same exclusivity constraint that already exists globally, now scoped per registry entry)
```

### Dependency Notes

- **The registry requires the v0.8.0 wrapper/content split:** before v0.8.0, there was one shared
  `.typ` output and one shared `_write_template_file()` call per build; the per-master
  `render_wrapper()` call is what makes "which entry is this, so which registry key applies" a
  question with a well-defined answer at the exact point template resolution happens. This milestone
  is not buildable without v0.8.0's entry-aware wrapper.
- **Bundle-copy-wholesale conflicts with `typst_template_assets`:** once every registry key's bundle
  (including `"typst"`'s own) is copied in full with no selection mechanism, an asset-allowlist config
  value has nothing left to filter — this is a genuine conflict (not just redundancy), which is why
  the milestone brief removes `typst_template_assets` rather than keeping it inert.
- **Fail-loud errors enhance (don't require) the registry:** they could technically ship as a laxer
  warn-and-drop like Sphinx's own `latex_theme_options` validation, but the milestone's own precedent
  (CONF-04) sets a stricter bar already in the codebase, so it's an internal-consistency dependency,
  not a technical one.

## MVP Definition

### Launch With (v1 — this milestone, v0.9.0)

- [ ] `typst_document_templates` dict registry (`template` xor `package`, plus `template_function`) —
  essential: this is the entire feature
- [ ] `"typst"` reserved key deferring to existing global config — essential for zero-edit backward
  compatibility, matching the strongest precedent found (Sphinx `latex_documents` per-entry default)
- [ ] Wholesale bundle-copy-per-key output rule — essential to make template-relative assets
  (`#image("logo.png")`) actually work, which is a currently-documented-but-broken promise
  (`templates.rst:106-113`)
- [ ] Fail-loud errors on: unregistered key, `template`+`package` both set, user-defined `"typst"`
  key, `template` pointing directly under `srcdir` — essential given this project's own CONF-04/BLD-02..04
  precedent for config-time validation

### Add After Validation (v1.x)

- [ ] Nothing identified in this survey as a natural "add next" — no precedent tool exposes a
  materially different per-document axis (page size, language) that isn't already covered by the
  existing global `typst_elements`/`typst_template_function` machinery. If demand emerges, the closest
  analog is Quarto's directory-level `_metadata.yml` override (apply a registry key to "everything
  under this subtree" rather than naming it per-master) — not validated by this research, flag as
  speculative.

### Future Consideration (v2+)

- [ ] Directory-convention resolution (Hugo-style implicit lookup order) as an alternative/adjunct to
  the explicit dict registry — **not recommended**: it would add a second, weaker-precedent mechanism
  alongside the stronger, already-decided explicit-registry shape, for no demonstrated need.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| `typst_document_templates` registry + `"typst"` reserved key | HIGH | MEDIUM | P1 |
| Wholesale bundle-copy-per-key output rule | HIGH (fixes a documented-but-broken promise) | MEDIUM | P1 |
| Fail-loud config validation (unregistered key, xor violation, reserved-key collision, srcdir-root template) | MEDIUM | LOW | P1 |
| Deleting `typst_template_assets` / `_write_template_file()` / the three `.typ`-exclusion special cases | MEDIUM (reduces surface area, prevents inert config) | LOW (deletions, not additions per the milestone brief) | P1 |
| Per-document language / page-size axis | LOW (no precedent demand found) | MEDIUM–HIGH | P3 (explicitly deferred) |

## Competitor Feature Analysis

| Feature | Sphinx LaTeX builder | Quarto | MkDocs | typsphinx's plan |
|---|---|---|---|---|
| Per-output-document template key | YES — `latex_documents[4]` (`theme`) | Partial — `format:` keys by *format*, not by *document*; directory-level `_metadata.yml` is the closest per-subtree override | NO — one theme per build; multi-theme needs multi-config | YES — `typst_documents[4]` → `typst_document_templates` key |
| Reserved "use global" sentinel | YES — per-entry default *is* `config.latex_theme` | N/A (format-keyed, not document-keyed) | N/A | YES — `"typst"` |
| Fail-loud on typo'd key | Partial — warns+drops unknown *option* keys, not unknown theme names | Partial — documented gotcha (silent partial-merge on `format`), not an error | N/A | YES — `ExtensionError`, stricter than either precedent |
| Assets travel with the template automatically | Themes carry their own static files as part of the theme directory | N/A (Pandoc-format-specific, not Quarto's concern) | YES — theme dir is the whole theme | YES — wholesale bundle copy, matching Typst's own `[template]` `path` convention |

## Sources

- [Sphinx `latex_documents` / `latex_theme` / `latex_theme_options` / `latex_theme_path` / `latex_docclass` — `configuration.rst` on `sphinx-doc/sphinx` master](https://raw.githubusercontent.com/sphinx-doc/sphinx/master/doc/usage/configuration.rst) — HIGH, primary source, directly quoted
- [Sphinx `default_latex_documents()` / `validate_latex_theme_options()` — `sphinx/builders/latex/__init__.py`](https://raw.githubusercontent.com/sphinx-doc/sphinx/master/sphinx/builders/latex/__init__.py) — HIGH, primary source
- [Sphinx `man_pages` / `texinfo_documents` tuple shapes — Configuration docs](https://www.sphinx-doc.org/en/master/usage/configuration.html) — HIGH, primary source
- [Sphinx 1.2 historical `latex_documents` docs (`documentclass` element, pre-`latex_theme`)](https://sphinx-rtd-trial.readthedocs.io/en/latest/config.html) — MEDIUM, archived third-party mirror of period-accurate Sphinx docs
- [Pandoc User's Guide — `--template`, `--reference-doc`, `defaults` files, `templates/default.FORMAT` convention](https://pandoc.org/MANUAL.html) — HIGH, primary source
- [Quarto `_quarto.yml` project format-nesting and the format-key no-partial-merge rule](https://quarto.org/docs/projects/quarto-projects.html) and [Including Other Formats](https://quarto.org/docs/output-formats/html-multi-format.html) — HIGH, primary source
- [MkDocs `theme.custom_dir` docs](https://www.mkdocs.org/dev-guide/themes) — HIGH, primary source
- [MkDocs maintainer answer on multi-theme-per-site (GitHub Discussion #3645)](https://github.com/mkdocs/mkdocs/discussions/3645) — MEDIUM, maintainer statement not a docs page, but authoritative for project intent
- [Asciidoctor PDF theme application (`pdf-theme`/`pdf-themesdir` attributes)](https://docs.asciidoctor.org/pdf-converter/latest/theme/apply-theme) — HIGH, primary source
- [Hugo template lookup order](https://gohugo.io/templates/lookup-order) — HIGH, primary source
- [Typst package manifest — `[template]` table (`path`, `entrypoint`)](https://github.com/typst/packages/blob/main/docs/manifest.md) — HIGH, primary source
- typsphinx internal: `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` (v0.9.0 milestone brief) — HIGH, project's own decisions
- typsphinx internal: `/home/yuta/Documents/typsphinx/docs/source/user_guide/configuration.rst`, `/home/yuta/Documents/typsphinx/docs/source/user_guide/templates.rst` — HIGH, current documented behavior being changed by this milestone

---
*Feature research for: per-document template registries in documentation toolchains*
*Researched: 2026-08-15*
