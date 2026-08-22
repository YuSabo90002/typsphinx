# Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-15
**Phase:** 54-one-bundle-rule-template-key-per-document-selection-four-deletions
**Areas discussed:** Bundle copy mechanics, CONF-19 detection and severity, BLD-05's non-`.typ` bundle file

**Areas offered but not selected:** `template_named_dir_master` fixture relocation and its three
regression intents (recorded under Claude's Discretion in CONTEXT.md rather than dropped, because
ROADMAP SC#5 requires the phase to record what carries the intent forward).

---

## Bundle copy mechanics

### Q1 — Existing destination bundle on re-build

| Option | Description | Selected |
|--------|-------------|----------|
| Delete destination, then copy | `rmtree` each used key's destination before copying; no stale files; best fit for the manifest-diff test. Cost: first `rmtree` under `outdir` in this extension. | |
| Overwrite only (leave stale) | `dirs_exist_ok`-equivalent; inherits `_copy_single_asset()`'s current behaviour; introduces no deletion. Stale files linger. | ✓ |
| Differential copy (mtime/size) | Copy only when the source is newer. Stale still lingers; bundles are a handful of files so no real I/O win. | |

**User's choice:** Overwrite only (stale を残す)
**Notes:** Measured for the options: `grep -n "rmtree\|os.remove\|unlink" typsphinx/*.py` returns only `pdf.py:204` (its own temp file), so this extension performs no deletion under `outdir` today.

### Q2 — Symlinks inside the bundle

The question was first framed as "how hard should the out-of-bundle symlink refusal be
(`ExtensionError` / warn-and-skip / `logger.error`)". The owner replied **"何が問題なん？"** and,
after the harm was spelled out, stated that there was no intent to build an inverted prohibition on
files outside the directory — only "the template directory gets copied wholesale". BLD-06's symlink
clause and ROADMAP SC#3's symlink sentence were therefore **retracted** and the question was
re-formulated as a purely mechanical one.

| Option | Description | Selected |
|--------|-------------|----------|
| `os.walk(followlinks=False)` + `copy2` (today's body) | File symlinks: content copied. Directory symlinks: not descended. Loops: structurally impossible. Introduces no new risk. | ✓ |
| `copytree(symlinks=False)` | Fullest reading of "wholesale"; descends directory symlinks. Measured: a self-referential `loop -> .` wrote ~40 nested copies before raising `shutil.Error`, so it needs a loop guard written by hand. | |
| `copytree(symlinks=True)` | Reproduces the bundle's shape; no loops. Output stops being self-contained — relative links point outside `outdir`, absolute links point at the build machine. | |

**User's choice:** 今の `os.walk` + `copy2` をそのまま使う
**Notes:** All three behaviours were measured in a scratch bundle containing an outward file symlink, an outward directory symlink, and `loop -> .` before the options were written.

### Q3 — Metadata exclusion set

| Option | Description | Selected |
|--------|-------------|----------|
| Exactly SC#3's four kinds | `.git` (directory), `.DS_Store`, `Thumbs.db`, editor backups. Does not exceed the roadmap text; keeps the manifest-diff test's expected set small. | ✓ |
| Wider VCS/tooling set | Adds `.svn`, `.hg`, `__pycache__`, `.idea`, `.vscode`. More realistic for a template directory sharing a working tree, but draws a boundary the roadmap did not. | |
| No exclusions at all | Literal "the whole directory is copied". Would also retract BLD-06's remaining half and publish a `.git` directory verbatim. | |

**User's choice:** SC#3 が名指しした4種だけ
**Notes:** Measured: `_copy_template_directory()` currently excludes only `.typ`; there is no metadata exclusion anywhere in the extension today.

### Q4 — Copy failure handling

| Option | Description | Selected |
|--------|-------------|----------|
| Template body raises, others warn | `ExtensionError` naming the key and both paths when the resolved `.typ` fails to copy; existing warn-and-continue for everything else. | ✓ |
| Any failure raises | Bundle copy is all-or-nothing. Turns previously-tolerated asset failures (permissions, name mismatches) into hard failures. | |
| Keep warning for everything | No behaviour change. `-b typst` would report success over an output whose `#import` target is absent. | |

**User's choice:** テンプレート本体だけ raise、他は warning
**Notes:** Measured: the per-file `except Exception → logger.warning("Failed to copy template asset …")` at builder.py:1425-1430. Today the template body never travels that path (`.typ`-excluded, written by `_write_template_file()`), which is why swallowing was safe until now.

---

## CONF-19 — removed-config detection

### Q1 — Detection mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Read `Config._raw_config` | The only route that covers all three names through one path. Private attribute; needs a defensive read and a test that fails loudly if it disappears. | ✓ |
| Keep a sentinel registration for `typst_template_assets` | Public API only, but cannot see the two already-unregistered names, so it degenerates into two coexisting mechanisms — and contradicts PROJECT.md's "no inert config left registered". | |

**User's choice:** `Config._raw_config` を読む
**Notes:** Measured on the installed Sphinx 9.1: `_raw_config` holds the `conf.py` namespace and is cleared only in `__setstate__` (unpickle), so it is live at `config-inited`.

### Q2 — Severity

| Option | Description | Selected |
|--------|-------------|----------|
| `logger.warning`, build continues | REQUIREMENTS.md's CONF-19 text as written. `-W` users get a hard failure for free. | ✓ |
| `ExtensionError`, build stops | Exceeds the requirement text and turns `conf.py` files that have built fine since v0.6.3 / v0.7.1 into hard failures at v0.9.0. | |

**User's choice:** warning（ビルドは続ける従来通り）

### Q3 — `suppress_warnings` subtype

| Option | Description | Selected |
|--------|-------------|----------|
| No subtype (match existing) | Measured: `grep -n "subtype" typsphinx/*.py` returns nothing — every warning here is a bare call. | ✓ |
| Tag it (e.g. `typsphinx.removed_config`) | Lets migrating users keep `-W` while silencing this one. Would be the extension's only tagged warning and forces a naming convention now. | |

**User's choice:** 付けない（既存と揃える）

### Q4 — Message text

| Option | Description | Selected |
|--------|-------------|----------|
| Bespoke text per value | Handles the asymmetry: `typst_template_assets` has a mechanism replacement, `typst_authors` has a config replacement, `typst_toctree_defaults` has none. | ✓ |
| Shared template with substitution | The common part collapses to "is ignored", so SC#5's observable-consequence requirement pushes the per-value sentences into a table anyway. | |

**User's choice:** 3値それぞれに専用文面
**Notes:** Recorded as a consequence, not a question: `config-inited` fires for every builder, so the warning appears in `-b html` builds too, including this repository's own `docs/source/conf.py`. `app.builder` does not exist at `config-inited`, so the handler cannot narrow itself — and the handler choice is locked by ROADMAP SC#5.

---

## BLD-05 — the `"typst"` bundle's non-`.typ` file

### Q1 — What file to add

The owner asked to clarify before answering; the premise (`typsphinx/templates/` contains only
`base.typ`, so BLD-05's assertion has no subject until a file is added) was restated and accepted.

| Option | Description | Selected |
|--------|-------------|----------|
| `README.md` describing the bundle | Explains what the directory is, that it lands in `<outdir>/_template/typst/` on every build, and how to register your own bundle. One file serving as both canary and explanation. | ✓ |
| Copy of `LICENSE` | `base.typ` can end up in a user's distributed output, so shipping MIT text alongside it has real meaning. Cost: duplicate of the root `LICENSE` needing a sync mechanism. | |
| Both | Two files of glob redundancy; two extra files in every user's output. | |

**User's choice:** README.md
**Notes:** Excluded before asking: adding a real path-relative asset to `base.typ`. It would break ROADMAP constraint #7's load-bearing measurement (all three real templates have zero path-relative references) while buying nothing, since SC#3 separately forbids the built-in template from standing as OUT-05 evidence.

### Q2 — package-data glob

| Option | Description | Selected |
|--------|-------------|----------|
| `templates/**/*` | Survives a future `templates/fonts/x.otf`. Matches the phase's "copy the directory wholesale" framing. | ✓ |
| `templates/*` | Minimal change covering today's two files; silently drops any subdirectory added later — exactly the failure BLD-05 exists to catch. | |

**User's choice:** `templates/**/*`（子ディレクトリも含む）
**Notes:** Measured: `pyproject.toml:73` is currently `"typsphinx" = ["templates/*.typ"]`.

### Q3 — Where the wheel-content check lives

| Option | Description | Selected |
|--------|-------------|----------|
| Step in the existing `build` job | `ci.yml:127-151` already runs `uv build` and `twine check`; adding an assertion step costs ~no build time. Not detectable locally. | ✓ |
| pytest test that builds a wheel | Detectable locally, sits with the other gates. No precedent for invoking a build tool from pytest here, and it would rebuild per OS × Python cell. | |
| Both | CI step plus a pytest assertion on the `pyproject.toml` glob declaration itself. | |

**User's choice:** 既存の `build` ジョブに step を追加

---

## Claude's Discretion

- `tests/fixtures/template_named_dir_master/`'s relocation and what carries each of its three
  regression intents forward (G-22.1-4/CR-01, BLD-02/OUT-01, CONF-09). Enumerated in CONTEXT.md so
  nothing is silently dropped; ROADMAP constraint #1 forecloses re-opening the reserved-directory-name
  choice, and `_templates/` is unavailable as a replacement name (Sphinx's own `templates_path` default).
- The concrete glob list for "editor backups".
- Exact wording of the three CONF-19 messages and of D-05's `ExtensionError`.
- Where the `config-inited` handler lives.
- How the write-time used-key accumulator is stored on the builder.
- Test file naming/placement and the composition of the OUT-05 user-template asset fixture.

## Deferred Ideas

- VCS/tooling metadata beyond SC#3's four exclusion kinds (`.svn`, `.hg`, `__pycache__`, `.idea`, `.vscode`).
- `suppress_warnings` subtypes for this extension's warnings as a set.
- Stale-bundle cleanup on incremental rebuilds (would introduce deletion under `outdir`).
- `writer.py:170-216` `_compute_template_import_path()` dead-code removal (carried forward from Phase 53).

## Requirement amendments produced by this discussion

- `.planning/REQUIREMENTS.md` BLD-06 — drop "and does not follow a symlink out of the bundle".
- `.planning/ROADMAP.md` Phase 54 SC#3 — drop "and refuses, with a named error, a symlink whose
  resolved path is not a descendant of the bundle".
