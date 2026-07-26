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

<!-- gsd:write-continue -->
