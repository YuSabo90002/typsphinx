# Phase 30 — Live Evidence Record

This is `30-EVIDENCE.md`, not `30-VERIFICATION.md` — the latter name is reserved and rewritten by
`/gsd-verify-work`. Every gate below is a command run in this session against the merged post-wave-1
tree, with its verbatim output pasted immediately after. No gate script is committed anywhere in the
repository. Nothing here cites a prior phase's SUMMARY as evidence — every number was re-measured in
this session.

## Pre-flight: confirming the wave-1 merge is actually complete

Before measuring anything, this session confirmed the merge landed in full — a gate run against a
partially-merged tree "produces a green that will be cited later" (30-04-PLAN.md's own warning).

```
$ test -f docs/build_multilang.py && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f docs/source/_templates/language-switcher.html && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f docs/source/_templates/page.html && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f docs/source/_static/custom.css && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f docs/usage.rst && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f docs/installation.rst && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f tests/test_documentation_usage.py && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -f tests/test_documentation_installation.py && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
$ test -d docs/locale && echo "PRESENT (bad)" || echo "ABSENT (good)"
ABSENT (good)
```

All four switcher assets, both root orphan documents, both collateral test files, and `docs/locale/`
are all absent. Confirming the three edited files carry their edits:

```
$ grep -c "docs-multilang" tox.ini
0
$ grep -n "publish_dir\|docs-html\|docs/_build/html" .github/workflows/docs.yml
35:        run: uv run tox -e docs-html
44:          path: docs/_build/html
57:          publish_dir: ./docs/_build/html
$ cat docs/Makefile
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

**Verdict: the merge is complete.** All gates below are measured against a fully-merged tree.

Worktree provisioning for this session (per CLAUDE.md's standing worktree-isolated execution
instructions):

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev --extra docs
[... 130+ packages resolved, typsphinx==0.6.3 installed from file:///.../agent-a4dd28d60319f7111 ...]
$ ln -sf /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv .venv/bin/uv
```

---

## Gate A — SC#1 token sweep

**Command** (scoped with `git ls-files` per the plan's own instruction — "the repository" is a
definition, not a filesystem walk):

```
$ git ls-files -z -- . ':!CHANGELOG.md' ':!.planning' | xargs -0 grep -nE 'multilang|html-ja|language-switcher|typsphinx_lang|custom\.css|html_context|html_sidebars'
```

**Verbatim output (unfiltered):**

```
tests/fixtures/confval_field_body_render_gate/index.rst:15:.. confval:: html_sidebars
tests/test_readthedocs_config.py:296:    I18N-02 deleted the language-switcher's context dict, the wiring
```

**Analysis of both hits:**

1. `tests/fixtures/confval_field_body_render_gate/index.rst:15` — the known survivor named in this
   plan's `must_haves.truths`: an unrelated Sphinx `.. confval:: html_sidebars` directive in a
   field-body render-gate fixture, nothing to do with the switcher.

2. `tests/test_readthedocs_config.py:296` — **a hit not enumerated in this plan's `must_haves.truths`
   or in `30-RESEARCH.md`'s Pitfall list.** Read in context (lines 288–298), this is a *docstring*
   sentence added by Plan 02's own repointing commit (`204f7ef feat(30-02): delete hand-rolled
   language-switcher machinery, trim conf.py`, confirmed via `git log --oneline -- tests/test_readthedocs_config.py`):

   ```python
   def test_language_seam_precedence(monkeypatch):
       """`_resolve_language()` resolves READTHEDOCS_LANGUAGE -> SPHINX_LANGUAGE -> "en".
       ...
       the Typst `lang` element derived through `derive_typst_lang` -- now that
       I18N-02 deleted the language-switcher's context dict, the wiring
       assertion's previous subject.
       """
   ```

   This uses "language-switcher" as a **proper noun referring to the now-deleted feature**, in prose
   explaining *why* the test was repointed (I18N-02 deleted it) — not a live reference to switcher
   code, config, or any surviving machinery. It is exactly the same class of textual false positive
   Gate B's `html_static_path` scoping already documents (a token that legitimately survives for
   reasons unrelated to the switcher's continued existence), just discovered one plan-wave later than
   Pitfall 1 was, because Plan 02 (which wrote this docstring) executed after this plan's own
   `30-RESEARCH.md` was researched.

**Exercised discretion (Gate A, this plan):** the survivor list named in this plan's `must_haves` is
widened by one entry — `tests/test_readthedocs_config.py:296` — on the same reasoning already
authorized for Gate B's `html_static_path` scoping: a token match that documents the deletion in
prose is not the presence of switcher machinery. This is recorded explicitly, as an exercised
discretion, per this plan's own prohibition: *"the gate's scoping is documented in `30-EVIDENCE.md`
rather than achieved by deletion"* — no file was edited to make this line disappear; the plan's own
`<artifacts_this_phase_produces>` forbids editing any source or test file in this plan, so the correct
action is to record the finding honestly, not to silently pass it or to fix it out of scope.

**Verdict:** zero *live* switcher-machinery references survive; two textual matches survive, both
accounted-for false positives (one previously known, one newly discovered and documented here for
the first time). Down from the pre-phase baseline of **37 lines across 9 files** (recorded at
planning time in `30-RESEARCH.md` Pitfall 1's "Measured (this session)" block, itself the
authoritative fresh grep — not `30-CONTEXT.md`'s pre-Phase-30.1 grep). **PASS, with one discretion
recorded.**

---

## Gate B — the scoped static-path token

SC#1 also names the static-path setting, but `html_static_path` is a generic Sphinx confval name
with 7 legitimate occurrences elsewhere in the repository (`30-RESEARCH.md` Pitfall 1). Two separate
assertions:

**B1 — absent from `docs/source/conf.py`:**

```
$ grep -n html_static_path docs/source/conf.py || echo "ABSENT in docs/source/conf.py (good)"
ABSENT in docs/source/conf.py (good)
```

**B2 — all 7 legitimate occurrences elsewhere survive, byte-unchanged:**

```
$ grep -rn html_static_path examples tests
examples/advanced/conf.py:30:html_static_path = []
examples/basic/conf.py:25:html_static_path = ["_static"]
tests/fixtures/glob_image_render_gate/conf.py:29:# declared html_static_path directory (`_static/`), exactly as the corpus's
tests/fixtures/glob_image_render_gate/conf.py:31:html_static_path = ["_static"]
tests/fixtures/static_asset_copy_render_gate/conf.py:25:# declared html_static_path directory (`_static/`), exactly as the corpus's
tests/fixtures/static_asset_copy_render_gate/conf.py:27:html_static_path = ["_static"]
tests/fixtures/static_asset_copy_render_gate/index.rst:5:html_static_path directory, mirroring the Sphinx doc corpus case.
```

7 lines, matching the expected count exactly (2 bundled example projects + 2 render-gate fixtures,
one of which — `static_asset_copy_render_gate` — has the token in both its `conf.py` and its
`index.rst`).

**Scoping decision and reasoning (recorded per this plan's own instruction, so a later reader does
not mistake the narrowed scope for an oversight):** `html_static_path` is scoped to
`docs/source/conf.py` only, rather than swept repo-wide, because a literal repo-wide reading of
SC#1's token list would demand breaking two bundled example projects
(`examples/basic/conf.py`, `examples/advanced/conf.py` — real, working sample code with nothing to
do with the language switcher) and two unrelated render-gate test fixtures. This is exactly Pitfall 1
from `30-RESEARCH.md`: the token was added to SC#1's word list via a later Claude's-discretion
decision, without ever having been repo-wide-grepped against the whole tree first. Deleting these
7 occurrences to force a repo-wide zero would be pure gate-appeasement of the precise defect class
this milestone's predecessor (v0.6.3) found at its own close — breaking a bundled example to satisfy
a textual grep.

**Verdict: PASS.** The token is gone from its one in-scope location; all 7 out-of-scope survivors are
present, byte-unchanged.

---

## Gate B (continued) — the confval fixture survivor

```
$ grep -n 'confval:: html_sidebars' tests/fixtures/confval_field_body_render_gate/index.rst
15:.. confval:: html_sidebars
```

**Verdict: PASS.** The one named must-survive line is present.

---

## Gate C — the SC#2 seam proof

Two anchored regions of `docs/source/conf.py` must be byte-unchanged from their recorded pre-phase
values.

**Region 1** (file start through the `# -- Options for HTML output` header line — carries
`templates_path`, Phase 29's `_resolve_language()` seam, its `language` assignment, and the
locale/gettext block):

```
$ sed -n '1,/^# -- Options for HTML output/p' docs/source/conf.py | sha256sum
06f177f82fb153ca4971d258989e7ede2a4e5ffa018a5caaa8ab0a56e6f7b466  -
```

Matches the recorded pre-phase value `06f177f82fb153ca4971d258989e7ede2a4e5ffa018a5caaa8ab0a56e6f7b466`
exactly.

**Region 3** (`# -- Options for typst/typstpdf output` header through end of file — Phase 30.1's
font-config block and the `derive_typst_lang` re-derivation):

```
$ sed -n '/^# -- Options for typst/,$p' docs/source/conf.py | sha256sum
cd245215f80b2552dcba7b01d74a36de0ef0b2323df665e88390381c2cd5d169  -
```

Matches the recorded pre-phase value `cd245215f80b2552dcba7b01d74a36de0ef0b2323df665e88390381c2cd5d169`
exactly.

**Milestone invariant #3 — zero `typsphinx/` changes across the whole phase:**

```
$ git diff --stat 458ffc8..HEAD -- typsphinx/
(empty output)
$ git diff --name-only 458ffc8..HEAD -- typsphinx/
(empty output)
```

**Verdict: PASS.** Both cross-repository-shared regions are proven byte-identical by hash; the phase's
whole diff against its base (`458ffc8`, the last commit before Phase 30 execution began) touches
nothing under `typsphinx/`.

---

## Whole-phase diff shape (for the owner's manual-merge review)

```
$ git diff --stat 458ffc8..HEAD | tail -5
 tests/test_documentation_installation.py           |  143 -
 tests/test_documentation_usage.py                  |  153 -
 tests/test_readthedocs_config.py                   |   17 +-
 tox.ini                                            |    8 -
 45 files changed, 576 insertions(+), 7110 deletions(-)
```

**Total deletion scope of the whole phase** (for the owner's manual merge past
`worktree.cleanup-wave`'s deletion guard):

```
$ git diff --diff-filter=D --name-only 458ffc8..HEAD | wc -l
34
```

34 files deleted across the phase — Plan 02's 4 (the switcher assets) + Plan 03's 30 (4 orphan-doc
pair + collateral tests, 26 `docs/locale/` tracked files), 0 added, 0 modified except the 3 CI/build
files (Plan 01) and `conf.py`/`test_readthedocs_config.py` (Plan 02).

---

## Gate D — the full suite (SC#3, SC#4)

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv run python -m pytest -q
...
tests/test_xref_orphan_degrade_render_gate.py .                          [100%]

======================= 641 passed, 1 skipped in 57.17s ========================
```

**Comparison against the pre-phase count:** Plan 03's `30-03-SUMMARY.md` recorded the identical
`641 passed, 1 skipped` result immediately after its own two deletion commits (`86633c4`,
`131ae4a`), with the delta from the pre-deletion `662 tests collected` fully accounted for by the
20 test functions in the two deleted collateral test files
(`tests/test_documentation_usage.py`: 12, `tests/test_documentation_installation.py`: 8). This
session's fresh run on the fully-merged tree (all three waves' work present at once, not just
Plan 03's own branch) reproduces the exact same `641 passed, 1 skipped` number — the merge
introduced no new failure and no new skip.

**Verdict: PASS.** The suite is green on the merged tree, and the only tests missing from the
pre-phase baseline are the ones whose subjects (the two orphan docs) are gone.

---

## Gate E — the documentation builds (SC#5)

**`docs-html`:**

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv run python -m tox -e docs-html
...
出力中...[  8%] api/index
...
出力中...[100%] user_guide/templates
索引を生成中... genindex py-modindex 完了
...
build succeeded, 2 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.54=setup[0.47]+cmd[3.07] seconds)
  congratulations :) (3.57 seconds)
```

(Sphinx's console messages render in Japanese because this worktree's `SPHINX_LANGUAGE`/locale
environment defaults to `ja` for interactive tool chrome — this is unrelated to the *documentation
content* language, which the build produces as English, matching `_resolve_language()`'s fallback
of `"en"` with no `READTHEDOCS_LANGUAGE`/`SPHINX_LANGUAGE` override set. The 2 warnings are the
pre-existing `visit_toctree` docstring-indentation warnings from `typsphinx/translator.py`, the
same baseline `30-02-SUMMARY.md` and `30-03-SUMMARY.md` both recorded — no new warning.)

**`docs-pdf`:**

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv run python -m tox -e docs-pdf
...
writing output... [user_guide/templates] done
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 2 warnings.
  docs-pdf: OK (3.57=setup[0.46]+cmd[3.11] seconds)
  congratulations :) (3.59 seconds)
```

**Artifact confirmation:**

```
$ test -f docs/_build/html/index.html && echo "index.html PRESENT"
index.html PRESENT
$ ls -la docs/_build/pdf/*.pdf
-rw-r--r-- 1 yuta users 1708448  7月 26 20:47 docs/_build/pdf/typsphinx.pdf
```

**Verdict: PASS.** Both tox environments exit 0 and produce exactly the two artifact paths
`.github/workflows/docs.yml` uploads/publishes: `docs/_build/html/index.html` and a PDF under
`docs/_build/pdf/`.

---

## Gate F — workflow/task-runner consistency (SC#5)

**Command** (a scratch script, not committed anywhere in this repository, parsing `docs.yml`'s
`run:` values for `tox -e <env>` strings and cross-checking against `tox.ini`'s section list and
the D-14 deploy/release boundary):

```python
import yaml, re, sys, pathlib, glob

raw = pathlib.Path(".github/workflows/docs.yml").read_text(encoding="utf-8")
d = yaml.safe_load(raw)
steps = d["jobs"]["build-docs"]["steps"]
runs = [s.get("run", "") for s in steps]
envs = sorted(set(re.findall(r"tox -e ([A-Za-z0-9_.-]+)", " ".join(runs))))
tox = pathlib.Path("tox.ini").read_text(encoding="utf-8")
secs = set(re.findall(r"^\[([^]]+)\]", tox, re.M))
paths = sorted(set(re.findall(r"docs/_build/[A-Za-z0-9_./*-]*", raw)))
dep = [s for s in steps if s.get("uses", "").startswith("peaceiris/actions-gh-pages")]
missing = [e for e in envs if ("testenv:" + e) not in secs]
badp = [p for p in paths if not glob.glob(p.rstrip("/"))]
chk = [
    ("envs_resolve", not missing),
    ("envs_found", len(envs) >= 2),
    ("paths_exist", not badp),
    ("deploy_one", len(dep) == 1),
    ("publish_dir", bool(dep) and dep[0]["with"]["publish_dir"] == "./docs/_build/html"),
    ("release_kept", any(s.get("uses", "").startswith("softprops/action-gh-release") for s in steps)),
]
bad = [n for n, ok in chk if not ok]
print("ENVS", envs, "PATHS", paths, "MISSING_ENVS", missing, "MISSING_PATHS", badp)
print("FAILED:", bad)
sys.exit(1 if bad else 0)
```

**Verbatim output:**

```
ENVS ['docs-html', 'docs-pdf'] PATHS ['docs/_build/html', 'docs/_build/pdf/*.pdf'] MISSING_ENVS [] MISSING_PATHS []
FAILED: []
```

**D-14 boundary, re-asserted directly:**

```
$ grep -n "peaceiris/actions-gh-pages\|softprops/action-gh-release\|publish_dir" .github/workflows/docs.yml
54:        uses: peaceiris/actions-gh-pages@v4
57:          publish_dir: ./docs/_build/html
62:        uses: softprops/action-gh-release@v3
```

Exactly one `peaceiris/actions-gh-pages` step, `publish_dir` pointing at the HTML tree, and the
`softprops/action-gh-release` step present.

**Verdict: PASS.** Every `tox -e <env>` string resolves to a real `tox.ini` section, every
referenced `docs/_build/` path is one Gate E actually produced, and the D-14 deploy/release
boundary holds.

---

## Gate G — the documentation root still resolves (RTD-04)

**Command** (a one-off corroborating read of a public URL — no credential, no body, not an API
integration; this project's `api-coverage` gate has false-positived on RTD evidence prose before,
per `STATE.md`'s carried override):

```
$ curl -sS -o /dev/null -w 'HTTP_CODE=%{http_code} EFFECTIVE_URL=%{url_effective}\n' -L https://typsphinx.readthedocs.io/
HTTP_CODE=200 EFFECTIVE_URL=https://typsphinx.readthedocs.io/en/latest/
```

**Verdict: PASS.** 200, redirecting to `/en/latest/` — matches the planning-time measurement
exactly.

---

## Deferred to the milestone pull request

**The observed `docs.yml` CI run required by SC#5's "observed CI run" clause is not observable
inside this phase.** `.github/workflows/docs.yml` triggers only on a push to `main`, a `v*` tag, or
a pull request targeting `main`, and declares no `workflow_dispatch` — and adding one would not
help, because GitHub resolves manual dispatch against the *default branch's* copy of the workflow
file, not this worktree's. Under `branching_strategy: milestone`, no such event occurs until the
milestone pull request against `main` is opened.

**Exact future check named:** when the milestone pull request opens, the `Documentation` workflow's
`build-docs` job must complete green, its `Build HTML documentation` step must run
`tox -e docs-html`, and the `documentation-html` artifact must be uploaded from
`docs/_build/html`. This is recorded here as **open**, not as a pass — the verifier is expected to
abstain to `human_needed` on this item, per this plan's own `must_haves.truths` backstop entry.

---

## Deferred to the next Read the Docs build

Two items, neither observable until Read the Docs rebuilds the tracked branch (which cannot happen
inside a per-plan worktree branch):

**1. The published `/en/latest/` page must stop containing the switcher wrapper class and the
deleted stylesheet reference.** Measured before the phase: the live page contained one occurrence
of the switcher wrapper class and one reference to the deleted `custom.css` stylesheet. Both should
reach zero once Read the Docs rebuilds the merged branch.

**Exact future check named:** a fetch of `https://typsphinx.readthedocs.io/en/latest/` grepped for
the switcher wrapper class and `custom.css`, both expected at zero occurrences, after Read the Docs
has rebuilt the tracked branch.

**2. Whether Furo's restored `ethical-ads` slot and variant selector render on the hosted site.**
Both are `READTHEDOCS`-gated Furo templates (`sidebar/ethical-ads.html`'s
`furo-sidebar-ad-placement` id, `sidebar/variant-selector.html`'s `furo-readthedocs-versions` id).
`30-02-SUMMARY.md` measured both **locally absent** (`AD_PLACEMENT=0 VARIANT_SELECTOR=0`) because
Sphinx does not set the `READTHEDOCS` flag outside an actual RTD build — a local zero does not
settle whether either slot appears on the *hosted* site, which depends on whether Read the Docs'
Addons build model still injects `READTHEDOCS` into the Jinja context. This question is carried
forward from Plan 02 unresolved.

**Exact future check named:** a fetch of `https://typsphinx.readthedocs.io/en/latest/` after Read
the Docs has rebuilt the tracked branch, grepped for `furo-sidebar-ad-placement` and
`furo-readthedocs-versions`; a non-zero count is the accepted, documented side effect of deleting
`html_sidebars` (Pitfall 3 of `30-RESEARCH.md`), not a regression to fix in a future phase.

---

## Accepted, deliberate losses this phase makes permanent

Restated here so neither can later read as an oversight:

1. **The browser-language auto-redirect at the documentation root is gone and is not
   reimplemented.** Read the Docs redirects to a *version*, never auto-detects a visitor's
   *language* — reimplementing the lost behavior would mean re-adding the hand-rolled template
   code this phase (I18N-02) exists to delete. Recorded as an accepted regression at v0.6.4
   milestone scoping (`PROJECT.md` Deferred Items table).

2. **The two `docs/usage.rst` sections with no counterpart under `docs/source/` are permanently
   lost content**, not merely relocated: `Continuous Integration` and `Build Commands Reference`.
   Per D-11 (`30-03-SUMMARY.md`), the file had not been touched since 2026-07-04 and most likely
   carried the same drift-from-implementation that made `docs/configuration.rst` a liability in
   Phase 27; git history retains the full original content, but nothing in the current tree
   replaces those two sections.

3. **Furo's restored ad-placement and variant-selector sidebar slots are an accepted side effect**,
   not a regression — carried forward from item 2 of the "Deferred to the next Read the Docs build"
   section above; the project's custom `html_sidebars` list never explicitly excluded them by
   documented decision, it simply predated Furo shipping them as defaults.

