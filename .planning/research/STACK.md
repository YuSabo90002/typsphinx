# Stack Research

**Domain:** Per-document Typst template registry for the `typsphinx` Sphinx extension (v0.9.0)
**Researched:** 2026-08-15
**Confidence:** HIGH (all four questions resolved against primary sources: PyPI's JSON API for
installed-version ground truth, official Sphinx `extdev/appapi.html`, official Typst
`reference/foundations/path/` docs, and this repository's own existing code)

## Verdict

**Add nothing.** No new runtime dependency, no new stdlib import that isn't already imported
elsewhere in this codebase, no Sphinx API this project isn't already using. Every piece this
milestone needs — dict-of-dicts config registration, directory-tree copy, and
nesting-depth-independent Typst imports — is either already present in `typsphinx/builder.py` or
is a one-line addition to an import list of a module already used elsewhere in the package. The
zero-new-runtime-dependency invariant holds with room to spare.

## Recommended Stack

### Core Technologies (already pinned, unchanged by this milestone)

| Technology | Version (verified via PyPI JSON API, 2026-08-15) | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Sphinx | 9.1.0 | Config registration (`add_config_value`), builder lifecycle | Already the pinned floor (`pyproject.toml:28` `sphinx>=9.1,<10`); latest PyPI release is 9.1.0/9.1.1 patch line — no version bump needed for this feature |
| typst (typst-py) | 0.15.0 | `typst.compile(path, root=...)` — the PDF compile step | Already the pinned floor (`pyproject.toml:30` `typst>=0.15.0,<0.16`); latest PyPI release is 0.15.0 — matches exactly |
| docutils | 0.22.x (pinned `>=0.21,<0.23`) | Doctree the translator walks | Unaffected by this milestone; noting only that PyPI's current docutils release (0.23) is *outside* today's pin — pre-existing, not something this feature should touch |

No version change is required in any of the three for this milestone.

### Supporting Libraries / stdlib (all already imported in this codebase)

| Module | Stdlib since | Purpose | When to Use (this milestone) |
|--------|---------|---------|-------------|
| `shutil` (`copytree(..., dirs_exist_ok=True)`) | 3.8 | Recursive directory copy that tolerates a pre-existing destination | The "copy the resolved template's parent directory wholesale to `<outdir>/_template/<key>/`" rule (PROJECT.md line 58-63) is exactly this call. **Already used this way in this file**: `builder.py:1381` — `shutil.copytree(src_path, dest_path, dirs_exist_ok=True)` inside `_copy_single_asset()`. Reuse that pattern (or lift it into a small shared helper) for every registry key's bundle copy instead of writing a second directory-copy routine. `dirs_exist_ok=True` matters here specifically because Sphinx incremental builds don't guarantee `outdir` is clean, and multiple `typst_documents` entries can share one registry key, so the destination directory legitimately gets written more than once per build. |
| `importlib.resources` (`files()`, `as_file()`) | 3.9 (`files()`), directory-`Traversable` support solidified in 3.12 | Get a real filesystem path for a directory bundled *inside* the installed package, safe under zipimport | Needed for exactly one case: the built-in `"typst"` key's bundle is `typsphinx/templates/` (`template_engine.py:274-278`, currently read via `Path(__file__).parent / "templates" / "base.typ"`). That line reads a single file's *text* today; this milestone needs to copy the *directory* it lives in. `Path(__file__).parent` works for the overwhelming majority of real installs (pip always unpacks wheels to real files on disk; this project ships no `zip_safe`/zipapp packaging), but `importlib.resources.files("typsphinx") / "templates"` + `importlib.resources.as_file(...)` is the textbook-correct, packaging-guide-endorsed way to turn package data into a real directory for `shutil.copytree`, and it degrades correctly (extracts to a cleaned-up temp dir) in the rare zipimport case `Path(__file__).parent` would silently mis-resolve. Zero cost: it's stdlib, and Python 3.12 is already this project's floor (`pyproject.toml:10`), which is also the exact version `files()`'s directory-`Traversable` walking matured in — no fallback shim needed for an older interpreter. |
| `re` (`re.fullmatch`) | stdlib | Charset-validate registry keys as path segments | PROJECT.md line 85 requires registry keys be "charset-validated at config-read time" because they become a path segment (`_template/<key>/`). This project already has a validate-and-`ExtensionError`-on-failure precedent using plain `re` (see `derive_typst_lang()`'s `re.fullmatch(r"[a-z]{2,3}", head)` in `template_engine.py:133`) — reuse that idiom, e.g. `re.fullmatch(r"[A-Za-z0-9_-]+", key)`, rejecting anything with `/`, `\`, `..`, or a leading `.` so a key can never escape `_template/` or collide with a dotfile. No path-sanitizing library is needed for this — the key space is small and fully under the user's/project's own control, unlike arbitrary untrusted input. |

### Development Tools

No change. `black`, `ruff`, `mypy`, `pytest` configurations in `pyproject.toml` need no new entries for this feature — no new third-party import is introduced that would need an ignore rule or type stub.

## Installation

```bash
# Nothing to install. All of the above are either already-pinned runtime
# dependencies or Python 3.12+ stdlib modules already imported elsewhere
# in typsphinx/builder.py (shutil, re) or importable with zero new
# dependency (importlib.resources).
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Hand-rolled validation of `typst_document_templates` inside `TypstBuilder.init()` / a `config-inited`-connected function, raising `sphinx.errors.ExtensionError` (existing pattern) | Sphinx's `ENUM` type validator (`sphinx.config.ENUM`) passed as the `types=` argument to `add_config_value` | `ENUM` validates that a single scalar config value is one of a fixed, enumerable set of literals (e.g. `ENUM("no", "footnote", "inline")` for `latex_show_urls`) — it has no concept of validating the *shape* of a dict-of-dicts (per-key `template` xor `package`, optional `template_function`) or of applying a regex to dict *keys*. It is the wrong tool for this schema regardless of Sphinx version; do not reach for it. |
| Validating in `TypstBuilder.init()` (this codebase's existing pattern — see the output-path-collision check at `builder.py:611`, which runs from inside builder methods, not a `config-inited` hook) | A new `app.connect("config-inited", ...)` handler registered in `__init__.py:setup()` | `config-inited` exists in Sphinx 9.x (`Callable[[Sphinx, Config], None]`, confirmed via `extdev/appapi.html`) and is a legitimate place to validate/convert config, but this project has **zero existing precedent** for it — every current `ExtensionError` this extension raises for bad config (unknown `typst_elements` key, output-path collisions, unusable `typst_documents` entries) is raised from inside a `Builder` method at build time, not from a `config-inited` callback at config-parse time. Introducing the first `config-inited` hook in this codebase to validate one new config value would add a second validation *mechanism* alongside the first for no behavioral gain — prefer following the established in-builder pattern (fail loud from `TypstBuilder.init()`, same place `_check_output_path_collisions`-style checks already live) unless a later need specifically requires pre-parse-time validation. |
| Root-relative Typst paths: emit `#import "/_template/<key>/custom.typ": project` from every wrapper, regardless of nesting depth | Depth-computed relative paths: emit `#import "../../_template/<key>/custom.typ": project`, computed via `os.path.relpath`/`posixpath.relpath` per wrapper's output location | Typst resolves a path starting with `/` "relative to the root of the project," and by default that root is "the parent directory of the main Typst file" *unless* overridden — which this codebase already does: `pdf.py:143` calls `typst.compile(typ_path, root=root_dir)`, and its sole call site (`builder.py:1545`) passes `root_dir=self.outdir`. Since every wrapper and content `.typ` file is written under `self.outdir`, and the milestone's own output rule places every bundle at `<outdir>/_template/<key>/`, a root-relative import from *any* wrapper file at *any* nesting depth resolves correctly with **one fixed string per key**, with no per-caller relative-path arithmetic and no possible off-by-one `../` count. Use depth-computed relative paths only if the project ever needs the emitted `.typ` files to also compile correctly via the bare `typst compile` CLI *without* an explicit `--root` flag pointed at `outdir` — not the case here, since this project always compiles through `typst-py`'s `root=` parameter (confirmed no existing CLI-only compile path in `pdf.py`). |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `sphinx.config.ENUM` for `typst_document_templates` schema validation | Validates one scalar against a fixed candidate list, not a dict-of-dicts shape; not applicable at all here (see Alternatives row above) | Manual validation with `ExtensionError`, following this project's existing `map_parameters()`/`_check_output_path_collisions`-style fail-loud pattern |
| A new `app.connect("config-inited", ...)` hook as this feature's validation entry point | No precedent in this codebase; every existing config-shape error in this extension is raised from a `Builder` method, and introducing a second validation *mechanism* for one new config value fragments where "typsphinx validates its own config" lives | Validate inside `TypstBuilder.init()` (or a helper it calls), matching `_check_output_path_collisions` (`builder.py:611`) |
| Any third-party path-safety / slugify library (e.g. `python-slugify`, `pathvalidate`) for registry-key charset validation | The zero-new-runtime-dependency invariant explicitly rules this out, and it is unnecessary: the key space is small, author-controlled `conf.py` config (not untrusted user input), and one `re.fullmatch()` call fully covers "safe path segment" | `re.fullmatch(r"[A-Za-z0-9_-]+", key)` (or similarly narrow), following the `derive_typst_lang()` precedent already in `template_engine.py:133` |
| Depth-computed `../../..` relative `#import` paths for the template bundle | Fragile: correctness depends on getting the wrapper's nesting depth exactly right at every call site, and multi-master composition (v0.8.0) already produces wrappers at varying output locations — a wrong `../` count is a silent-until-compile-time Typst "file not found" error | Typst's root-relative `/`-prefixed path, given `root=self.outdir` is already fixed at every compile call site (`pdf.py:143`, `builder.py:1545`) |
| Changing `get_default_template_path()`'s `Path(__file__).parent` pattern everywhere in `template_engine.py` | Out of scope creep — every OTHER read in this file (loading a single template's text) works today and isn't touched by this milestone; rewriting working, unrelated code isn't warranted | Scope the `importlib.resources.files()`/`as_file()` change to *only* the new operation this milestone introduces: producing a real directory to hand to `shutil.copytree` for the `"typst"` key's bundle |

## Stack Patterns by Variant

**If the registry key is `"typst"` (the reserved built-in key):**
- Its bundle source is `typsphinx/templates/` — data shipped *inside* the installed package.
- Use `importlib.resources.files("typsphinx") / "templates"` wrapped in `importlib.resources.as_file(...)` to get a real directory, then `shutil.copytree(that_dir, outdir/_template/typst, dirs_exist_ok=True)`.
- Because this is the one bundle source that might not be a plain file on disk (zipimport edge case) — every other bundle source is already guaranteed to be a real path.

**If the registry key names a local `template` (srcdir-relative `.typ` file):**
- Its bundle source is `Path(srcdir) / dirname(that .typ path)` — already a real directory on the user's filesystem, exactly like today's `_copy_template_directory()` (`builder.py:1263-1317`) and `_copy_single_asset()` (`builder.py:1356-1391`) inputs.
- Use plain `shutil.copytree(src_dir, outdir/_template/<key>, dirs_exist_ok=True)` directly — `importlib.resources` does not apply; there is no installed-package indirection to route around.

**If the registry key names a `package` only (no `template`):**
- No bundle exists to copy (PROJECT.md line 61: "A package-only key has no bundle and copies nothing").
- No filesystem or stdlib call is needed for that key's copy step at all — skip it, exactly as `copy_template_assets()`'s existing `typst_package` early-return already does for the global-config case (PROJECT.md line 69-70, being generalized to a per-key property this milestone).

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3.12 (project floor, `pyproject.toml:10`) | `importlib.resources.files()` returning a `Traversable` that correctly walks *subdirectories* | This directory-walking behavior for `files()` was solidified in 3.12 (earlier 3.9-3.11 versions had rougher edges around nested-directory `Traversable`s per the CPython docs) — this project's floor is exactly the version where the modern API is fully reliable, so no compatibility shim or `importlib_resources` backport package is ever needed. |
| typst-py 0.15.0 | Typst 0.15's root-relative `/`-path resolution | Root-relative (`/`-prefixed) path resolution against an explicit `root=` is long-standing Typst behavior (predates 0.15 by several major/minor releases); 0.15 additionally introduced a first-class *file path type* accepted throughout the language, but did not change how a leading `/` resolves. No version-sensitivity risk for this milestone on the currently-pinned typst-py floor. |
| `typst.compile(path, root=root_dir)` | `root_dir` must be an ancestor of (or equal to) every `.typ` file's own directory | Already satisfied today: `builder.py:1545` passes `root_dir=self.outdir`, and every wrapper/content `.typ` file this extension writes already lives under `self.outdir` (enforced by the existing output-path-collision machinery at `builder.py:524-613`). The new `_template/<key>/` bundles are specified to land at `<outdir>/_template/<key>/` — also under `self.outdir` — so this constraint continues to hold with no new code needed to enforce it. |

## Sources

- PyPI JSON API (`https://pypi.org/pypi/{sphinx,typst,docutils}/json`), queried directly 2026-08-15 — HIGH confidence, authoritative registry data: Sphinx 9.1.0, typst-py 0.15.0, docutils 0.23 (current pins: `sphinx>=9.1,<10`, `typst>=0.15.0,<0.16`, `docutils>=0.21,<0.23`, all confirmed in `pyproject.toml:28-30`)
- [Application API — Sphinx documentation](https://www.sphinx-doc.org/en/master/extdev/appapi.html) — HIGH confidence (direct fetch of official docs): `Sphinx.add_config_value(name, default, rebuild, types=(), description='')` signature; `ENUM` and `config-inited` both confirmed present in Sphinx 9.x
- [Typst reference — Path](https://typst.app/docs/reference/foundations/path/) — HIGH confidence (direct fetch of official docs, quoted verbatim): "`/`-prefixed paths resolve relative to the root of the project... the project root is the parent directory of the main Typst file" by default, overridable; relative paths (no leading `/`) "resolve in relation to the parent directory of the Typst file where the function is called" — applies uniformly to `#import`, `#include`, `image()`, `read()`
- [Typst 0.15.0 changelog](https://typst.app/docs/changelog/0.15.0/) — MEDIUM confidence (web-search-sourced, cross-checked against the official changelog page and GitHub release notes): confirms 0.15 added a first-class file path *type*, not a change to `/`-prefix resolution semantics
- This repository, read directly (HIGH confidence — ground truth):
  - `typsphinx/builder.py:1381` — existing `shutil.copytree(src_path, dest_path, dirs_exist_ok=True)` call, the pattern to reuse
  - `typsphinx/builder.py:611`, `builder.py:524-613` — existing in-builder `ExtensionError` validation pattern (no `config-inited` hook precedent anywhere in this codebase, confirmed via `grep -n "config-inited" typsphinx/*.py` returning nothing)
  - `typsphinx/pdf.py:110-153`, `builder.py:1545` — `typst.compile(typ_path, root=root_dir)` with `root_dir=self.outdir` at its only call site
  - `typsphinx/template_engine.py:133`, `derive_typst_lang()` — existing `re.fullmatch()` validate-and-warn/raise idiom to follow for registry-key charset validation
  - `typsphinx/template_engine.py:266-278`, `get_default_template_path()` — the `Path(__file__).parent / "templates" / "base.typ"` line this milestone's `"typst"`-key bundle copy needs to route around with `importlib.resources`
  - `pyproject.toml:10,27-31,72-73` — Python floor, dependency pins, `package-data` declaration for `typsphinx/templates/*.typ`

---
*Stack research for: per-document Typst template registry (typsphinx v0.9.0)*
*Researched: 2026-08-15*
