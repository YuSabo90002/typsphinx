# Pitfalls Research

**Domain:** Adding a per-document template registry (`typst_document_templates`) to an existing, mature Sphinx→Typst extension — directory-copy output layout, registry-key-as-path-segment, deletion of a live config value, relocation of an existing output artifact
**Researched:** 2026-08-15
**Confidence:** MEDIUM (general findings cross-checked across multiple independent web sources); HIGH where grounded directly in this repository's own code (`builder.py`'s existing escape/collision guards, `pyproject.toml` packaging config)

## Critical Pitfalls

### Pitfall 1: Registry key validation that stops at the wrong layer (string-shape only, or filesystem-probe only)

**What goes wrong:**
The v0.8.0 `_escapes_outdir()`/`_is_drive_qualified()` pair already solved "is this user string safe to become a path segment" for `typst_documents` target stems — but only for the **traversal/absolute/drive-qualified** shape. A registry key has a *stricter* contract than a target stem: a target stem is a whole relative path (`"manuals/guide"` is legal), but a registry key becomes exactly one path segment (`<outdir>/_template/<key>/`), so anything that makes it *multi-segment*, *empty*, *reserved*, or *colliding-after-folding* is newly in scope and the existing guard does not cover it. Concretely: a key containing `/` or `\` silently creates (or escapes into) a subdirectory instead of raising; a key that is empty, all-dot (`"."`, `".."`), or whitespace resolves to a nonsensical or dangerous segment; a key that differs from another only by case (`"Paper"`/`"paper"`) writes to the same path on Windows/macOS's default filesystems while looking like two independent bundles on Linux CI; a key matching a Windows reserved device name (`CON`, `NUL`, `AUX`, `COM1`...) makes directory creation fail outright on Windows, case-insensitively, with or without a trailing extension; and a key with trailing dots/spaces (`"paper. "`) is silently stripped by the Win32 API, so `"paper."` and `"paper"` collide there without colliding anywhere else.

**Why it happens:**
The temptation is to reuse `_escapes_outdir()` verbatim because "it already handles bad target stems" — but that function's contract (per its own docstring) is "may contain a `/`", which is the opposite of what a single path segment needs. Reviewers who don't re-read the docstring's stated contract will approve reuse that quietly widens the escape surface.

**How to avoid:**
Write a **new, narrower** predicate for registry keys — reject on: contains `/` or `\`; empty or whitespace-only; equals `.` or `..`; strips to a different string after removing trailing `.`/space characters (Windows-shape, but checked on every platform per this project's own D-05 platform-independence precedent — see `_is_drive_qualified()`'s docstring, which validates Windows-shaped input identically on POSIX CI); casefolds to a Windows reserved device name (`CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`, `CLOCK$`) with or without a trailing extension. Then, separately, extend `TypstBuilder._collision_key()`'s existing casefold-and-normalize comparison (already NFC/NFD-deliberately-non-normalizing, already cross-platform by design per its own docstring) to also index `_template/<key>/` bundle destinations, so two registry keys that differ only by case are caught by the *same* collision map the wrapper/content files already go through — not a second, independently-written check that can drift from the first. **Validation is theatre if it only rejects at string-shape and never re-checks after `casefold()`** — the case-collision hazard is invisible to a shape-only test.
Length limits are lower priority: a registry key is one path segment appended to `<outdir>/_template/`, and Windows' historical 260-char `MAX_PATH` is rarely reached by a plausible key name — flag but do not gate on this unless a plan explicitly targets long-path Windows support.

**Warning signs:**
A code review that reuses `_escapes_outdir()` for the new key validator without a written justification for why its "path is now legal" (OUT-01) reversal is safe for a single-segment context. A guard test suite that only exercises `../`, `/abs`, `C:` shapes (copy-pasted from the existing target-stem tests) and never exercises `""`, `"."`, `"CON"`, `"Paper"` vs `"paper"`, or `"paper. "`.

**Phase to address:**
The phase that introduces `typst_document_templates` config parsing/validation (the "fail-loud configuration errors" phase named in PROJECT.md) — this is where `ExtensionError` on an unregistered/malformed key already needs to be raised, so the stricter key-shape check belongs in the same validation pass, before any directory copy runs.

---

### Pitfall 2: `copytree`'s symlink default silently changes what gets published, in either direction

**What goes wrong:**
`shutil.copytree(src, dst, symlinks=False, ...)` — the default — **dereferences** every symlink in the source tree, copying the *contents* of whatever the symlink points to, including something outside the template's own directory (a symlink to a shared fonts folder, a build artifact, or accidentally `/etc/passwd` in a malicious/careless template repo). Explicitly passing `symlinks=True` instead **preserves** the symlink as a symlink in the copied output — which means an absolute-target symlink inside a user's template directory now appears verbatim inside `<outdir>/_template/<key>/`, and following it from the published output directory can escape entirely outside the project's intended publish tree. Neither default is safe on its own for a **user-designated, arbitrary directory being copied into a project's build output** (this is a materially different trust boundary than copying a hand-authored template file with a known-safe origin, which is what this project has copied to date via `_write_template_file()`).

**Why it happens:**
`copytree` is reached for because it's the one-line stdlib answer to "copy this whole directory," and the `symlinks=` decision is easy to skip because both defaults *look* reasonable in isolation and the difference has zero visible effect on an ordinary local dev machine where no template directory contains a symlink.

**How to avoid:**
Decide the symlink policy explicitly and encode it as a comment next to the call, not as an implicit stdlib default: either (a) `symlinks=False` (dereference) plus a size/type guard that refuses to copy a target outside `src`'s own tree (rejecting a symlink whose resolved real path is not a descendant of the template directory), or (b) reject symlinks outright via an `ignore=` callable that flags any `os.path.islink()` entry and raises/warns rather than silently copying or silently dropping it. Given this project's existing posture (fail-loud `ExtensionError` on malformed config, per PROJECT.md), rejecting an escaping symlink with a named error is the more consistent choice than silently resolving or silently preserving it.
Separately, exclude publish-inappropriate files unconditionally — `.git`, `.DS_Store`, `Thumbs.db`, editor backup suffixes (`~`, `.swp`), and anything matching common secret-file shapes — via an `ignore=` callable, the same mechanism `shutil.copytree` already exposes for this purpose. Do not rely on the template author to keep their template directory clean; a user pointing `template` at an existing docs `_templates/` subdirectory that also happens to be their whole git-tracked assets folder is a realistic case for this project given `docs/source/_typst/custom_template.typ` and `examples/*/  _templates/` already exist as real precedent directories in this repo.
Also decide the re-run behavior explicitly: `dirs_exist_ok=True` merges into an existing destination without pruning files the source directory no longer has — an incremental build that copies over a stale `_template/<key>/` will leave orphaned files from a prior template revision. Either `shutil.rmtree()` the destination bundle before each copy, or accept staleness as a known, documented limitation (do not leave it undecided).

**Warning signs:**
A guard test that only checks "the file I expect is present" and never checks "no file I didn't expect is present" (i.e., an allowlist-by-omission test rather than a manifest-diff test). A template fixture directory in the test suite that never contains a symlink, so the whole symlink branch is untested by construction.

**Phase to address:**
The phase that implements the directory-copy mechanism itself (the "one output rule, no exceptions" bullet in PROJECT.md, replacing `_copy_template_directory`/`copy_template_assets`). The `ignore=` callable and the symlink-escape guard are the SAME function's responsibility — do not defer the symlink decision to a later hardening phase, since it is cheap to decide correctly the first time and expensive to retrofit onto call sites that have already shipped without it.

---

### Pitfall 3: The bundled `"typst"` template's own directory is not safely copyable via `Path(__file__).parent`, and `pyproject.toml`'s package-data glob already only covers `.typ`

**What goes wrong:**
This project already has a concrete, present-tense instance of the general "copying a directory out of an installed package" hazard: `pyproject.toml:73` declares `[tool.setuptools.package-data] "typsphinx" = ["templates/*.typ"]` — a glob scoped to `.typ` files only. Today that is harmless because `typsphinx/templates/` contains exactly one file, `base.typ`. The moment the "typst" built-in key's bundle directory needs a companion non-`.typ` asset (an example font, a logo used in a demo, a `.bib` fixture), the *wheel a user actually `pip install`s* silently omits it — the file exists in the git checkout and in an editable/dev install (`pip install -e .`), so local testing and even CI running against the source tree never notices, but a real PyPI install's copied bundle is missing the file. This is the exact "works everywhere except the one environment nobody develops in" shape this project has already been bitten by once (the `tox-uv-bare` ELF hazard, the case-insensitive-filesystem hazard from v0.8.0).
Separately, whatever code resolves "the parent directory of the resolved template" for the `"typst"` built-in key must not assume `Path(__file__).parent` names a real, walkable directory on disk — that assumption breaks under zipimport, a PEP 302 non-filesystem loader, or (less likely for this project's own packaging, but a real distribution-side risk) a `--only-binary`/vendored/frozen install path. `importlib.resources.files()`/`as_file()` is the loader-agnostic answer; walking a `Path(__file__).parent`-derived directory with `os.walk()`/`copytree()` is not guaranteed to work identically to how it works in the dev checkout.

**Why it happens:**
The dev/CI loop for this project runs almost exclusively against an editable install of the source tree (per this project's own worktree-isolation `uv sync --extra dev` convention) or a sdist-adjacent checkout, where `Path(__file__).parent` and the package-data glob are both irrelevant — the files are just *there*, on disk, unconditionally. The gap between "installed from a wheel" and "running from source" is invisible to every test that never actually builds and installs the wheel.

**How to avoid:**
Two independent fixes, not one: (a) widen the `pyproject.toml` package-data glob for `typsphinx/templates/` to `**/*` (or itemize every file kind the bundle will ever need) the moment a second file kind enters that directory — treat "add a non-.typ file under templates/" as requiring a `pyproject.toml` diff in the same commit, and add a CI check that builds the wheel and asserts the expected files are present inside it (`python -m build && unzip -l dist/*.whl | grep templates/`) rather than trusting the glob by inspection. (b) Resolve the `"typst"` built-in key's bundle directory through `importlib.resources.files("typsphinx") / "templates"`, and when a real on-disk directory is needed for `copytree()`, do so inside an `importlib.resources.as_file()` context manager rather than constructing the path via `Path(__file__).parent`. This is strictly more portable and costs one extra import.

**Warning signs:**
Grepping the diff for `Path(__file__).parent` (or `os.path.dirname(__file__)`) anywhere near the new template-bundle-resolution code. A `pyproject.toml` package-data glob whose extension list doesn't match the actual file extensions present in `typsphinx/templates/` after the change (a one-line `find typsphinx/templates -type f` vs. the glob is enough to catch drift). No CI job that builds and installs the actual wheel/sdist and runs even a smoke test against it.

**Phase to address:**
The phase that implements "the resolved template's parent directory is copied wholesale" for the built-in `"typst"` key specifically — this is the one registry entry whose bundle lives inside the installed package rather than under `srcdir`, so it is the one call site that needs the `importlib.resources` treatment; every other registry key's bundle is already a real on-disk directory under `srcdir` and doesn't have this hazard. Add the wheel-build CI smoke test in the same phase, since a later phase has no organic reason to add it once this one ships without noticing the gap.

---

### Pitfall 4: Relocating `_template.typ` from outdir root to `_template/typst/` changes relative-path resolution inside every EXISTING custom template — and the failure mode is not uniformly loud

**What goes wrong:**
Today `_write_template_file()` writes `_template.typ` at the outdir root, and any relative path a custom template's own Typst code contains (`#image("logo.png")`, `#bibliography("refs.bib")`, `read("data.csv")`) resolves relative to that root. Moving the same logical file to `_template/typst/_template.typ` (one directory deeper) means every such relative reference now needs to walk up one extra level, or — since this milestone's whole point is that the template's bundle directory is copied alongside it — the reference should resolve correctly again *if and only if* the referenced asset lived in the same source directory as the template file and got swept into the wholesale copy. The failure mode splits three ways, not one:
1. **Loud (best case):** `#image("logo.png")` where `logo.png` was never adjacent to the template file (e.g. it lived at the outdir root via the old `advanced.rst:129-138`-documented `"_templates/refs.bib"` convention) — Typst's compiler raises a file-not-found compile fatal. This is the easy case; it aborts the build and points roughly at the cause.
2. **Silent wrong content, not silent failure:** a font referenced by **family name** (as all three real custom templates in this repository already do, per PROJECT.md's own measurement) is unaffected by this relocation at all — Typst resolves font families from the compiler's font search path, not from the `.typ` file's own directory, so this case is a non-issue for this project's *current* real templates but remains a live hazard for any future or third-party template that references a font by file path instead.
3. **Silent wrong render (worst case, no error at all):** if a same-named asset happens to exist at *both* the old outdir-root location and the new bundle-relative location (e.g. a stale `_templates/refs.bib` left over at outdir root from a prior build, per Pitfall 2's "re-run over existing destination" staleness risk, alongside a *different* `refs.bib` now correctly copied into the bundle) — the compile succeeds, but resolves to the wrong file, and nothing in the build output indicates this happened.

**Why it happens:**
Typst's `#image()`/`#bibliography()`/`read()` all resolve relative paths relative to the **file doing the referencing**, not relative to the compile root or the outdir — this is exactly the same "no import inheritance across `#include()`" semantics `writer.py`'s own docstring (per CLAUDE.md's architecture section) already documents as the reason included documents need their own `@preview` imports. The same file-relative resolution rule that motivated the multi-file include design in v0.8.0 is what makes relocating `_template.typ` a resolution-changing move, not a cosmetic one — this is entirely internally consistent with decisions this project has already made, which is exactly why it is easy to overlook as "just a file move."

**How to avoid:**
PROJECT.md's own decision log (D-block "`\"typst\"` gets no exception in the output layout") already measured this against the three real templates in this repository and found zero `#image()`/`#bibliography()`/`read()` path references — so the *known* blast radius for this codebase's own templates is genuinely zero. What is NOT yet covered: (a) a regression fixture that pins this measured-safe finding as a real-compile test (a template with a `#image("logo.png")` reference alongside `logo.png` in the same directory, asserting the compile succeeds *after* the relocation to `_template/<key>/`) — turning "we measured no template in this repo uses path-relative assets" into "we assert path-relative assets keep working going forward," since the whole point of moving the template into its own bundle is that `#image()` "starts working" per PROJECT.md's own stated goal; (b) `templates.rst`'s asset-reference documentation and `advanced.rst:129-138`'s `"_templates/refs.bib"` outdir-root-relative guidance must be corrected in the SAME phase that ships the relocation, not left stale — a stale doc describing the old resolution path is worse than no doc, since it actively teaches users to break their own template; (c) explicitly do NOT special-case a leftover stale asset at the old outdir-root location — if Pitfall 2's staleness concern is resolved by `rmtree`-before-copy, a stale same-named file at the old flat location has no home to hide in and case 3 above cannot occur silently.

**Warning signs:**
A real-`typst.compile()` regression fixture that only tests the bundled `"typst"` built-in template (which this project's own measurement shows has no path-relative assets) and never tests a *user-supplied* template with a `#image()` reference — the built-in template passing tells you nothing about the relocation's effect on the case that actually matters. `advanced.rst` still showing `"_templates/refs.bib"` after the phase ships.

**Phase to address:**
The phase that deletes `_write_template_file()` and routes the `"typst"` key through the same wholesale-directory-copy rule as every other key (the "four mechanisms are deleted, not extended" bullet in PROJECT.md) is where the relocation itself happens, and must ship the new real-compile regression fixture in the same phase, not deferred. The documentation phase named in PROJECT.md (`templates.rst`, `advanced.rst`) must land in the same milestone, ideally the same phase or the immediately adjacent one, given how actively misleading stale asset-path guidance would be.

---

### Pitfall 5: Deleting `typst_template_assets` from `add_config_value()` turns it into permanently-silent dead config, with no user-visible signal at all

**What goes wrong:**
Sphinx's config system only recognizes a name once an extension calls `app.add_config_value()` for it; there is no reverse mechanism ("this name used to be registered, now warn if still set"). A `conf.py` that still sets `typst_template_assets = [...]` after this milestone ships continues to load and build successfully — Sphinx accepts arbitrary names into the `conf.py` module namespace and simply never looks at ones no extension registered. The user gets **zero warning, zero error, and a completely successful build** that silently does something different from what their `typst_template_assets` setting used to select (the whole bundle directory is now copied wholesale regardless of what that list said). This is the single named user-visible breaking change PROJECT.md calls out, and it is also the one this project's own architecture makes structurally impossible to detect automatically at the point of removal.

**Why it happens:**
`add_config_value()`'s absence is not an error condition from Sphinx's point of view — an unregistered name in `conf.py` is indistinguishable, to Sphinx, from a user's own unrelated helper variable (`conf.py` is an executed Python module, and Sphinx only reads back the names it explicitly asked for). This is exactly the same shape CLAUDE.md's own history already names for `typst_toctree_defaults` (v0.6.3's CONF-05) — this project has removed a live config value at least once before and the removal itself carries no built-in detection.

**How to avoid:**
Sphinx has no built-in "deprecated config key" mechanism as of the versions this project targets, so the only lever available is a **manual, explicit deprecation check inside `setup(app)`** (or a `config-inited` event handler): read `config._raw_config` (or equivalent) for the literal string `"typst_template_assets"` at config-init time, and if present, emit a `logger.warning()` naming it as removed and pointing at the CHANGELOG/migration note. This is strictly better than silence and costs a handful of lines; it is the same category of fix as this project's own `_is_usable_typst_documents_entry()` philosophy of "one predicate, checked explicitly, rather than trusting a framework default to catch it." Also: the CHANGELOG entry and any migration doc must state plainly that the setting is now silently ignored if left in place — not merely that it "was removed" — so a user grep-searching their own `conf.py` after an upgrade knows *why* their template assets look different (the whole directory now copies unconditionally) without needing to read the extension's source.

**Warning signs:**
No `config-inited` (or equivalent) handler anywhere in `__init__.py`/`builder.py` after the `add_config_value()` call for `typst_template_assets` is deleted. A migration/CHANGELOG entry that says only "removed `typst_template_assets`" without stating the observable behavioral consequence for a `conf.py` that still sets it.

**Phase to address:**
The same phase that deletes the `add_config_value()` registration (paired with the `copy_template_assets()`-deletion phase in PROJECT.md) should add the explicit deprecated-key warning in the identical commit — this is cheap to do at removal time and essentially impossible to retrofit usefully later (there is no way to detect, after the fact, whether a given historical build silently ignored the setting).

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|-----------------|
| Reusing `_escapes_outdir()` unmodified for registry-key validation | Zero new code, "proven" guard | Misses empty/reserved/case-collision/multi-segment shapes a single path segment needs rejected that a whole relative path does not (Pitfall 1) | Never — write the narrower predicate |
| `copytree(..., symlinks=False)` with no `ignore=` callable | One-line implementation | Silently follows symlinks outside the template dir, or copies `.git`/secrets/editor backups into a published output tree (Pitfall 2) | Only if the template source is verified first-party (never for `srcdir`-relative user templates) |
| Trusting the existing `.typ`-only `package-data` glob unchanged | No `pyproject.toml` diff needed today | Silently drops any future non-`.typ` asset from the built wheel, invisible in editable/dev installs (Pitfall 3) | Only as long as `typsphinx/templates/` truly contains nothing but `.typ` files — revisit the moment that changes |
| Shipping the `_template.typ` relocation with only the built-in-template regression fixture | Reuses existing test infra | The built-in template has zero path-relative assets by design — the fixture proves nothing about the case that actually breaks (Pitfall 4) | Never as the *sole* fixture; add a user-template-shaped fixture in the same phase |
| Relying on Sphinx to warn about the removed `typst_template_assets` config key | No extra code | Sphinx has no such mechanism — silence is permanent without an explicit handler (Pitfall 5) | Never |

## Integration Gotchas

Common mistakes when connecting to external services/components.

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| `shutil.copytree()` (stdlib) | Leaving `symlinks=` at its implicit default without a written rationale | Decide and comment the symlink policy explicitly; add an `ignore=` callable for `.git`/`.DS_Store`/backup-suffix exclusion |
| `importlib.resources` vs. `Path(__file__).parent` | Assuming the installed package always lives as loose files on disk | Resolve the built-in `"typst"` bundle through `importlib.resources.files()`/`as_file()`, not `__file__`-relative path math |
| `setuptools` `package-data` glob | Assuming `templates/*.typ` covers "the templates directory" | Widen the glob (or itemize) the moment a non-`.typ` file is added; verify with a built-wheel content check in CI, not by inspection |
| Sphinx `add_config_value()` deletion | Assuming Sphinx will surface a stale `conf.py` setting for a value nobody registers anymore | Add an explicit `config-inited`-time check that warns by name when the removed key is still set |
| Typst's own relative-path resolution (`#image()`, `#bibliography()`, `read()`) | Assuming a file move at the Python/Sphinx layer has no effect because "it's the same logical template" | Typst resolves these relative to the referencing `.typ` file's own on-disk location, not the compile root — any relocation of `_template.typ` is a resolution-changing move for path-relative (not family-name) asset references |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Wholesale `copytree()` of a user's `template`-adjacent directory with no size/file-count bound | Build time balloons; disk usage doubles per registry key | Document that the bundle directory should contain only template-relevant files (not a whole shared `_static/` assets folder); consider a warning above some file-count threshold (e.g. hundreds of files) rather than a hard limit | A template author points `template` at a large pre-existing `_templates/` directory shared with other tooling (this repository's own `examples/*/_templates/` are exactly this shape today, currently small) |
| Re-running an incremental build over an existing `_template/<key>/` destination without pruning | Stale files accumulate silently across template revisions; disk usage grows unbounded across many local builds | `rmtree()` the destination bundle before each copy rather than relying on `dirs_exist_ok=True`'s merge-only semantics | Any project doing frequent local incremental rebuilds over months without a clean `outdir` |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Copying a symlink verbatim (`symlinks=True`) from a `srcdir`-relative template directory with no target-containment check | An absolute-target symlink inside a template bundle surfaces inside the published `<outdir>/_template/<key>/`, potentially exposing or aliasing a file outside the intended publish tree when the outdir itself is later published (e.g. to a static host or RTD artifact) | Reject any symlink whose resolved real path is not a descendant of the template's own source directory; fail loud (`ExtensionError`) rather than silently dropping or silently following |
| No `.git`/dotfile/backup-file exclusion in the wholesale copy | A template author's `.git` directory, `.DS_Store`, editor swap files, or an accidentally-committed credentials file (`.env`, an API key checked in next to a template for local testing) gets copied verbatim into build output that may be published | An `ignore=` callable excluding dotfiles-by-default (with an explicit opt-in escape hatch only if a real use case demands it) rather than an allowlist the template author must remember to maintain |
| Registry key used directly as a path segment without charset validation | A key containing shell-metacharacter-adjacent or control characters (even though PROJECT.md already commits to charset-validating keys at config-read time) reaching a raw `path.join()` before validation runs | Validate BEFORE any `path.join()`/`mkdir()` call touches the key — validation-then-use, never use-then-catch |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| A rejected registry key (reserved name, case collision, empty) reported with a generic "invalid key" message | User has to guess which of several possible reasons (Windows-reserved? case-collides with another key? empty?) caused the rejection | Name the SPECIFIC reason in the `ExtensionError` message, following this project's own established pattern (`_resolve_target_stem()`'s warnings each name the specific escape shape detected) |
| Silently-ignored `typst_template_assets` after removal (Pitfall 5) produces a successful build with different-looking output and no diagnostic | User spends time debugging "why did my template assets change" with no lead at all | Explicit deprecated-key warning naming the setting and the CHANGELOG/migration doc |
| `#image()` path that resolved before the `_template.typ` relocation now fails after an otherwise-unrelated version bump | User's previously-working custom template breaks on upgrade with a Typst compile fatal that gives no hint the CAUSE was a Sphinx-extension-side file relocation | CHANGELOG entry naming the relocation explicitly as a breaking change with a "if your template references an asset by relative path, it must now live inside the template's own directory" migration note |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Registry key validation:** Often only tests `../`/absolute/drive-qualified shapes copy-pasted from the existing target-stem guard — verify a dedicated test exercises empty, `.`/`..`, Windows-reserved-device-name, trailing-dot/space, and case-collision (`"Paper"` vs `"paper"`) shapes, and that the case-collision check runs through the SAME casefold-comparison route as the existing `_collision_key()` mechanism.
- [ ] **Directory copy security:** Often copies everything in the source directory unconditionally — verify an `ignore=` callable excludes `.git`, `.DS_Store`, editor backups, and that the symlink policy (follow vs. preserve vs. reject-if-escaping) is a deliberate, commented choice rather than the unexamined stdlib default.
- [ ] **Built-in `"typst"` bundle packaging:** Often verified only against an editable/dev install — verify a CI step builds the actual wheel/sdist and confirms every file the `"typst"` bundle needs is present inside it, and that the bundle-resolution code path uses `importlib.resources`, not `Path(__file__).parent`.
- [ ] **`_template.typ` relocation regression coverage:** Often tested only against the built-in template (which this project has already measured has zero path-relative asset references) — verify a real-compile fixture exists for a USER-supplied template with a `#image()`/`#bibliography()` reference to a same-directory asset, proving the relocation doesn't break the case PROJECT.md's own "start working" goal depends on.
- [ ] **Removed `typst_template_assets` deprecation signal:** Often assumed covered by "Sphinx will handle it" — verify an explicit `config-inited`-time (or equivalent) warning fires when a `conf.py` still sets the removed key, and that the CHANGELOG states the observable behavior change, not just the removal.
- [ ] **Cross-platform invisibility:** Often "verified" by running the full test suite on the Linux CI runner alone — verify which of the above are asserted as pure string-shape/logic tests (runnable identically on every platform, per this project's own D-05 precedent) versus which genuinely require a Windows or macOS filesystem to observe (see the Cross-Platform section below) and that the latter have either a Windows/macOS CI lane or an explicitly-filed follow-up, not silent omission.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|-----------------|
| Registry key validation gap ships and a case/reserved-name collision reaches a user | LOW | Ship a point release tightening the validator; the failure mode is a clear build-time error or an obviously-wrong output directory layout, not silent data loss |
| Symlink escape or unwanted-file leak into published output | MEDIUM | Audit and `rmtree` the affected `_template/<key>/` bundle from any already-published output (e.g. RTD-hosted artifacts), tighten the `ignore=` callable, document the incident in CHANGELOG if user-facing assets were exposed |
| Wheel-packaging glob omission (Pitfall 3) discovered post-release | LOW | Widen the `package-data` glob, cut a patch release; affected users re-`pip install --upgrade` |
| `_template.typ` relocation silently breaks a real user's path-relative asset reference | MEDIUM | The failure is a loud Typst compile fatal (case 1 in Pitfall 4) for the common sub-case, which is self-diagnosing from the error message; the silent-wrong-render sub-case (case 3) requires a user bug report to surface — respond by adding the exact fixture shape they hit as a permanent regression test |
| Removed config value's silent-ignore surprises a user post-upgrade | LOW | Cannot retroactively detect past silent builds; forward-fix by adding the deprecated-key warning in the very next patch release |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| Registry key becomes an unsafe/colliding path segment | Config-parsing/validation phase (`typst_document_templates` registry + `ExtensionError` fail-loud phase) | New string-shape unit tests for empty/`.`/`..`/reserved-name/trailing-dot-space/case-fold shapes, runnable on Linux CI (no real filesystem needed — pure predicate tests, per this project's D-05 precedent) |
| Wholesale `copytree` follows escaping symlinks or leaks unwanted files | Directory-copy-mechanism phase (replacing `_copy_template_directory`/`copy_template_assets`) | A filesystem-backed integration test with a fixture directory containing a symlink (in-tree and escaping), a `.git`-shaped subdirectory, and a dotfile — asserting the copy excludes/rejects each; this ONE test genuinely needs a real filesystem, not a string-shape test |
| Built-in `"typst"` bundle mis-packaged or mis-resolved under a non-filesystem loader | Same directory-copy-mechanism phase, for the `"typst"` key's specific resolution code path | A CI step building the actual wheel and asserting file presence inside it; a unit test mocking/using `importlib.resources` rather than `Path(__file__)` |
| `_template.typ` relocation breaks a path-relative asset reference | Same directory-copy-mechanism phase (where `_write_template_file()` is deleted) | A real-`typst.compile()` regression fixture using a USER-shaped template with a same-directory `#image()` reference, plus the corresponding `templates.rst`/`advanced.rst` doc corrections in the same phase |
| `typst_template_assets` removal is invisible to a user who kept it set | Same config-deletion phase (pairs with the `add_config_value()` removal) | A test asserting a `logger.warning` fires when `typst_template_assets` is present in `conf.py`'s raw config after the value is unregistered |
| Cross-platform hazards invisible on Linux-only local/CI runs | Any phase touching path validation or directory copy — flag explicitly rather than deferring silently | See the Cross-Platform section below for the split between string-shape-testable (Linux-safe) and genuinely filesystem-dependent (needs Windows/macOS CI or an explicit owner-accepted gap) |

## Cross-Platform: What Is Structurally Invisible on Linux-Only Local Runs

This project's own history already contains three confirmed instances of exactly this class of gap (per the milestone context: the path-separator `file not found` defect, the case-insensitive-filesystem collision hazard flagged but not caught locally in v0.8.0 research, and the CPython 3.13 `ntpath.isabs()` narrowing that silently disabled a Windows branch, caught only by Windows CI). The same split applies here:

**Testable as a pure string-shape assertion, on ANY platform (Linux CI is sufficient) — per this project's own D-05 "platform-independence" precedent already applied to `_is_drive_qualified()`/`_escapes_outdir()`:**
- Registry key contains `/` or `\`, is empty, is `.`/`..`, casefolds to a Windows reserved device name, or differs from another registered key only by case after `casefold()`.
- Trailing-dot/trailing-space stripping: this is a Windows API behavior, but the *check* ("does this key differ from its Windows-stripped form?") is a pure string operation testable identically on Linux — do not wait for Windows CI to write this test, following the exact reasoning `_is_drive_qualified()`'s own docstring already documents for why Windows-shaped input must be validated on POSIX too.
- The `_collision_key()`-style comparison extension for `_template/<key>/` bundle paths.

**Genuinely requires a real filesystem with the relevant semantics — needs Windows or macOS CI, or must be explicitly flagged as an accepted gap rather than silently skipped:**
- Case-insensitive collision on an ACTUAL filesystem (two registry keys `"Paper"`/`"paper"` producing genuinely conflicting `mkdir()` calls) — a Linux ext4 test tree cannot observe this; it can only observe the string-comparison-level detection described above. The v0.8.0 research already named this exact gap for the wrapper/content file layer; it now recurs identically at the registry-key layer and needs the same disposition (documented-and-accepted, or a Windows CI lane).
- Windows reserved-device-name `mkdir()` failure — the actual OS-level rejection can only be observed on Windows; Linux can only pre-empt it via the string check above.
- NFC/NFD Unicode-normalization mismatches on macOS (APFS does not normalize; a Finder-created vs. shell-created directory of visually-identical names can differ at the byte level) — this project's own `_collision_key()` already deliberately does NOT apply Unicode normalization (a documented, measured decision, not an oversight) for the WRITTEN filename; whether the same non-normalizing choice is correct for registry-key COMPARISON needs the same explicit measurement this project already applied to output-path collision keys, not a silent assumption that it transfers unchanged.
- Symlink-following/escape behavior differs across platforms in subtle ways (Windows symlinks require elevated privileges or Developer Mode to create at all, so a Windows CI symlink test may need to be skipped or specially provisioned rather than assumed to run identically to POSIX).
- The wheel-packaging/`importlib.resources` gap (Pitfall 3) is NOT a cross-platform issue in the OS sense — it is invisible specifically to an **editable/dev install**, which is this project's own standard local AND CI dev loop (per CLAUDE.md's worktree `uv sync --extra dev` convention). The mitigation is a wheel-build-and-inspect CI step, not a different-OS CI lane.

## Sources

- This repository, `typsphinx/builder.py` (`_escapes_outdir()`, `_is_drive_qualified()`, `_collision_key()`, `_validate_output_path_collisions()`, `_write_template_file()`, `copy_template_assets()`/`_copy_template_directory()`/`_copy_explicit_assets()`) — HIGH confidence, first-party source, read directly for this research.
- This repository, `.planning/PROJECT.md` lines 1-140 (v0.9.0 milestone brief, decisions D-block) — HIGH confidence, first-party source.
- This repository, `pyproject.toml` (`[tool.setuptools.package-data]`) — HIGH confidence, first-party source.
- Python official docs, `shutil.copytree()` reference (symlinks/dirs_exist_ok/ignore= semantics) — MEDIUM confidence (web, cross-checked across multiple independent mirrors/versions of the same official documentation).
- Python official docs, `importlib.resources` reference and multiple independent explainer sources on `Path(__file__)` vs. `importlib.resources.as_file()` under zipimport — MEDIUM confidence (web, cross-checked).
- Sphinx official `extdev/appapi` documentation, `Sphinx.add_config_value()` — MEDIUM confidence (web, cross-checked; the "unregistered config value is silently ignored, not an error" behavior is corroborated by Sphinx's own documented `conf.py`-is-an-executed-namespace design, not merely inferred).
- Multiple independent sources on Windows reserved device filenames (`CON`/`PRN`/`AUX`/`NUL`/`COM1`-`9`/`LPT1`-`9`/`CLOCK$`), including Microsoft's own documented list as quoted across secondary sources — MEDIUM confidence (web, cross-checked across independent citations of the same underlying Microsoft documentation).
- Multiple independent sources on macOS HFS+/APFS Unicode normalization behavior (including a JDK bug tracker discussion and an in-depth explainer) — MEDIUM confidence (web, cross-checked across independent technical sources describing consistent behavior).

---
*Pitfalls research for: adding a per-document template registry to typsphinx (v0.9.0)*
*Researched: 2026-08-15*
