# Phase 35: v0.6.5 Release Prep — Release Evidence

This file records SC#1 (freshness re-run), SC#2 (cited), SC#3, SC#4, and SC#5 of ROADMAP Phase 35,
with verbatim command output backing every claim. Every command below was re-run live during this
plan's execution (2026-07-29); no output is carried forward from `35-CONTEXT.md`, `35-RESEARCH.md`,
`35-PATTERNS.md`, or a prior phase's evidence file as evidence — those documents are inputs to be
re-verified, not evidence themselves.

**Filename note:** this file is deliberately not named `35-VERIFICATION.md` — that name is reserved
by the `/gsd-verify-work` verifier, which overwrites it wholesale when it runs. The surviving
precedent for this naming choice is `33-RELEASE-EVIDENCE.md` from the previous release-prep phase.

**Provisioning note:** all commands below were run inside this plan's isolated git worktree, after
`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev --extra docs` and symlinking a
working `uv`/`ruff` binary into `.venv/bin/` (the standing NixOS dynamic-linker shim this project's
`CLAUDE.md` documents), and every command was invoked through `uv run`.

---

## SC#1: version-sync guards re-run for freshness (carried primarily from plan 35-03)

**Claim:** `pyproject.toml` declares `0.6.5` as the sole version literal, `uv.lock` is in lockstep,
`typsphinx.__version__` reports `0.6.5`, and README's Status line agrees. Full evidence — including
the `uv.lock` numstat and the `uv sync --extra dev --locked` regeneration proof — is recorded in
`35-03-SUMMARY.md`; that plan's own transcript is not re-typed here. This section only re-runs the
two guard commands fresh, for evidence-freshness per this plan's own convention.

### Step 1 — `__version__` probe

Command:
```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
```
Verbatim output:
```
0.6.5
```

### Step 2 — the two version-sync guard tests

Command:
```
$ uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q
```
Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_readme_version_sync.py .                                      [ 25%]
tests/test_preview_version_sync.py ...                                   [100%]

============================== 4 passed in 0.02s ===============================
```

### SC#1 verdict

**SC#1: MET.** `typsphinx.__version__` reports `0.6.5` and both version-sync guards are green,
consistent with `35-03-SUMMARY.md`'s full evidence (the `uv.lock` numstat of exactly 1 insertion / 1
deletion, and `uv sync --extra dev --locked` exiting 0).

---

## SC#2: curated CHANGELOG entry (carried from plan 35-04)

**Claim:** `CHANGELOG.md` carries a curated `## [0.6.5]` entry (lead paragraph + `### Fixed` +
`### Verified`) directly above `## [0.6.4]`, and the tail link block is rolled over (`[0.6.5]:`
release-tag line added, `[Unreleased]:` compare advanced to `v0.6.5...HEAD`). This is fully evidenced
in `35-04-SUMMARY.md` (whole-plan `CHANGELOG.md` diff: 25 insertions, exactly 1 deletion). No
re-transcription is needed here — this is a prose/structural artifact with no dedicated automated
guard in this repository (per `35-VALIDATION.md`'s own Requirements → Test Map: "manual / prose —
N/A"). The three `### Verified` bullets that CHANGELOG entry states are each given a matching
evidence section below (SC#3 and SC#4).

### SC#2 verdict

**SC#2: MET** (per `35-04-SUMMARY.md`'s verification; not re-run here as there is no mechanical
guard to re-run).

---

## SC#3: the post-bump tree is proven green end to end on a live run

**Claim:** the full pytest suite, `black`, `ruff`, `mypy`, the full-corpus `-b typstpdf` regression
gate, and (per D-12) the two docs dogfooding builds `tox -e docs-html` / `tox -e docs-pdf` are all
green on the post-bump tree.

### Step 1 — full pytest suite

Command:
```
$ uv run python -m pytest -q --tb=no -rf
```
Verbatim tail output:
```
======================= 649 passed, 1 skipped in 56.86s ========================
```
649 passed / 1 skipped / 0 failed — matches the `35-RESEARCH.md` baseline (`649 passed, 1 skipped`)
exactly, and matches `35-03-SUMMARY.md`'s post-bump re-run. Exit code 0.

### Step 2 — `black --check .`

Command:
```
$ uv run black --check .
```
Verbatim output:
```
All done! ✨ 🍰 ✨
173 files would be left unchanged.
```
Exit code 0.

### Step 3 — `ruff check .`

Command:
```
$ uv run ruff check .
```
Verbatim output:
```
All checks passed!
```
Exit code 0.

### Step 4 — `mypy typsphinx/`

Command:
```
$ uv run mypy typsphinx/
```
Verbatim output:
```
Success: no issues found in 6 source files
```
Exit code 0.

### Step 5 — full-corpus `-b typstpdf` regression gate, isolated confirmation

This isolated run exists purely as an **evidence-legibility step, not a coverage step**. A plain
full-suite run (Step 1 above) applies no `-m "not slow"` filter anywhere in this repository's
`pyproject.toml` `addopts`, its `tox.ini`, or `.github/workflows/ci.yml` — despite
`tests/test_corpus_gate.py`'s own module docstring claiming the slow-marked class is excluded from
the default suite. **That docstring claim is stale and does not match this repository's actual
configuration**: no marker filter is applied anywhere, so the plain `pytest -q` run in Step 1 already
executed the corpus gate and every other slow-marked test in the suite. The isolated run below is
recorded only because it is easier evidence-file prose to point at a 2-item run than at one line
inside a 650-item run; the next release-prep phase should not re-derive this correction from
scratch.

Command:
```
$ uv run pytest tests/test_corpus_gate.py -q -m slow
```
Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py .s                                             [100%]

================= 1 passed, 1 skipped, 3 deselected in 12.70s ==================
```
1 passed, 1 skipped (the pre-existing env-gated `test_empty_url_before_after`, unrelated to this
phase), 3 deselected (the non-`slow` tests in the same file, already covered by Step 1). Exit code 0.

### Step 6 — `tox -e docs-html` (D-12)

Command:
```
$ uv run tox -e docs-html
```
Verbatim tail output:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
...
build succeeded, 2 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.69=setup[0.49]+cmd[3.20] seconds)
  congratulations :) (3.72 seconds)
```
Exit code 0 (independently re-confirmed via a captured `$?` on a second invocation: `EXIT:0`). The
two warnings are a pre-existing docstring-formatting nit in `visit_toctree`'s own docstring
(unrelated to this milestone's translator change, which touched only the math visitors) — they do
not fail the build.

### Step 7 — `tox -e docs-pdf` (D-12)

Command:
```
$ uv run tox -e docs-pdf
```
Verbatim tail output:
```
preparing documents... Template written to /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/docs/_build/pdf/_template.typ
done
writing output... [api/index] done
writing output... [changelog] done
writing output... [contributing] done
writing output... [examples/advanced] done
writing output... [examples/basic] done
writing output... [examples/index] done
writing output... [index] done
writing output... [installation] done
writing output... [quickstart] done
writing output... [user_guide/builders] done
writing output... [user_guide/configuration] done
writing output... [user_guide/index] done
writing output... [user_guide/templates] done
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/docs/_build/pdf/typsphinx.pdf
build succeeded, 2 warnings.
  docs-pdf: OK (3.63=setup[0.51]+cmd[3.12] seconds)
  congratulations :) (3.65 seconds)
```
Exit code 0. The project's own documentation set builds through the `typstpdf` builder and produces
`docs/_build/pdf/typsphinx.pdf`. This is D-12's addition to the three runs SC#3 names — since this
milestone touched the translator (the two math visitors), rebuilding the project's own documentation
through `typstpdf` is worth doing rather than ceremonial: it is the closest thing this project has to
a live consumer of the fix.

### Step 8 — working-tree cleanliness after both docs builds

Command:
```
$ git status --porcelain -- docs/
```
Verbatim output:
```
(empty)
```
Both tox environments build out of `docs/` into `docs/_build/`, which is gitignored; the empty
output confirms neither build wrote anything unexpected outside that path. Nothing under `docs/` is
committed by this phase.

### SC#3 verdict

**SC#3: MET.** All seven live runs (full pytest suite, `black --check .`, `ruff check .`,
`mypy typsphinx/`, the isolated corpus-gate confirmation, `tox -e docs-html`, `tox -e docs-pdf`) exit
0 on the post-bump tree, and the docs builds leave the working tree clean under `docs/`.

---

## SC#4: milestone invariants asserted mechanically over the full diff

**Claim:** the three milestone invariants — zero new runtime dependencies, no `@preview` package
version bump across the four version-sync surfaces, and (per this milestone's scope note) the
`typsphinx/` change confined to exactly `typsphinx/translator.py` — hold over the full milestone
diff, anchored on the merge-base SHA, never on a written-down commit count.

### Diff-range re-measurement (source of truth for this section)

Command:
```
$ git merge-base main HEAD
```
Verbatim output:
```
eb696bb02d135227d880c679fc909513fe6f7d19
```
This matches the SHA prefix `eb696bb` recorded in `35-CONTEXT.md` and `35-RESEARCH.md`, and the same
SHA re-measured in Task 1's own SC#1 section.

Command:
```
$ git log --oneline eb696bb..HEAD | wc -l
```
Verbatim output:
```
63
```
This number is a moving target, not a fact to compare against any earlier planning document: every
`docs(35-...)` tracking commit this phase's own execution makes increments it further (it read 33 at
discussion time, 36 at research time, and had already reached 63 by this task's own execution —
purely from accumulating planning-doc and task commits, none of which touch `typsphinx/`, `tests/`,
or any dependency file — this task's own Task 1 commit alone accounted for one of the increments
since research). Only the merge-base SHA above is a stable anchor; the invariants below are asserted
against the SHA-anchored range, never against this count.

### Invariant 1 of 3 — zero new runtime dependencies

Command:
```
$ git diff --numstat eb696bb..HEAD -- pyproject.toml
```
Verbatim output:
```
1	1	pyproject.toml
```

Command:
```
$ git diff --numstat eb696bb..HEAD -- uv.lock
```
Verbatim output:
```
1	1	uv.lock
```

Full diffs, shown so a reader can see the changed lines are exactly the version keys:

Command:
```
$ git diff eb696bb..HEAD -- pyproject.toml
```
Verbatim full diff:
```diff
diff --git a/pyproject.toml b/pyproject.toml
index e101643..82b1efc 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"
 
 [project]
 name = "typsphinx"
-version = "0.6.4"
+version = "0.6.5"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
```
Exactly one hunk: the `version` bump (plan 35-03). No line inside `dependencies` or
`optional-dependencies` changed.

Command:
```
$ git diff eb696bb..HEAD -- uv.lock
```
Verbatim full diff:
```diff
diff --git a/uv.lock b/uv.lock
index b3e8a78..30d5a50 100644
--- a/uv.lock
+++ b/uv.lock
@@ -1376,7 +1376,7 @@ wheels = [
 
 [[package]]
 name = "typsphinx"
-version = "0.6.4"
+version = "0.6.5"
 source = { editable = "." }
 dependencies = [
     { name = "docutils" },
```
Exactly one hunk: the `typsphinx` self-entry's version field — no transitive dependency line moved,
matching `35-03-SUMMARY.md`'s recorded numstat exactly.

**Positive control** (proves the diff-range and pathspec machinery is actually working — an empty
result on a broken pathspec would look identical to a genuine pass without this control):

Command:
```
$ git diff --numstat eb696bb..HEAD -- typsphinx/translator.py
```
Verbatim output:
```
45	0	typsphinx/translator.py
```
Non-zero (45 insertions, 0 deletions) — matching the fact recorded in `35-CONTEXT.md`'s Specifics
table and re-verified independently in `35-04-SUMMARY.md`. This proves the numstat/diff machinery
over this exact range is a working comparison, so the empty/minimal results above are genuine, not a
silently-broken check.

**Invariant 1: PASS.** `pyproject.toml` and `uv.lock` each carry exactly one insertion and one
deletion — the version-literal bump — with no dependency array or transitive-dependency line touched
anywhere.

### Invariant 2 of 3 — no `@preview` package version bump

The four declaration surfaces are `typsphinx/writer.py`, `typsphinx/template_engine.py`,
`typsphinx/templates/base.typ`, and `examples/`.

Command:
```
$ git diff eb696bb..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/
```
Verbatim output:
```
(empty)
```
Empty — none of the four surfaces changed a single byte over the milestone range.

Command (mechanized corroboration):
```
$ uv run pytest tests/test_preview_version_sync.py -q
```
Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_preview_version_sync.py ...                                   [100%]

============================== 3 passed in 0.01s ===============================
```
This module (read in full during this task) asserts three things across the same four surfaces:
that the four `@preview` package versions (`codly`, `codly-languages`, `mitex`, `gentle-clues`)
agree identically across `writer.py`/`template_engine.py`/`base.typ`
(`test_preview_versions_identical_across_declaration_sites`), that all four are declared at every
site (`test_all_four_packages_declared`), and that every `.typ` file under `examples/` pins versions
matching the canonical `base.typ` values (`test_example_templates_match_canonical_versions`).

**Invariant 2: PASS.**

### Scope note — `typsphinx/` is not untouched this milestone

Unlike the previous milestone (v0.6.4), where `typsphinx/` was entirely untouched, this milestone's
fix (Phase 34) required a translator change. The assertion here is that the change is **confined**
to exactly one file, not that `typsphinx/` is unchanged overall.

Command:
```
$ git diff --name-only eb696bb..HEAD -- typsphinx/
```
Verbatim output:
```
typsphinx/translator.py
```
Exactly one path. Combined with Invariant 1's positive control above (45 insertions, 0 deletions in
that same file) and Invariant 2's empty diff on the three `typsphinx/`-internal `@preview` surfaces
(which are also under `typsphinx/` and are therefore included in this same one-path result), this
confirms the entire milestone's `typsphinx/`-tree change is the two math-visitor edits in
`translator.py` and nothing else.

### Cross-reference to the third CHANGELOG `### Verified` claim

The CHANGELOG's third `### Verified` bullet ("The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf`
re-run remains fatal-free") is evidenced by Task 1's SC#3 § Step 5 above (the isolated
`test_corpus_gate.py -m slow` run, 1 passed / 1 skipped / 3 deselected) plus SC#3 § Step 1 (the full
suite, which already executes the same test class). It is not re-run a third time here.

### SC#4 verdict

**SC#4: MET.** Both invariants hold over the SHA-anchored milestone range
(`eb696bb02d135227d880c679fc909513fe6f7d19..HEAD`, 63 commits at this measurement — a number that
will keep moving and is not the anchor): zero new runtime dependencies (`pyproject.toml` and
`uv.lock` each show exactly one insertion and one deletion — the version-literal bump — with a
working positive control proving the diff machinery itself functions), and no `@preview` version
bump on any of the four declaration surfaces (empty diff plus a green mechanized guard). The
`typsphinx/`-tree scope differs from the previous milestone by design — the change is confined to
exactly `typsphinx/translator.py`, which is the assertion this section proves, not zero change.

---

## SC#5: no irreversible action was taken

**Claim:** no `v0.6.5` tag exists locally or on `origin`, and nothing was published, merged, or
released by this phase. Run last, after every other command in this task.

Command:
```
$ git tag -l v0.6.5
```
Verbatim output:
```
(empty)
```

Command:
```
$ git ls-remote --tags origin v0.6.5
```
Verbatim output:
```
(empty)
```

Both are empty. The release workflow (`.github/workflows/release.yml`) fires only on a tag push, so
an absent tag on both the local repository and the remote is what makes "nothing was published" a
mechanical claim rather than an assurance — no other trigger in this repository's CI configuration
can publish a release.

**Optional `gh` CLI check:** `gh` is available and authenticated in this environment (`gh auth
status` confirmed a logged-in account with `repo` scope), so the additional query was run rather than
recorded as unrun:

Command:
```
$ gh release view v0.6.5 --repo YuSabo90002/typsphinx
```
Verbatim output:
```
release not found
```
(exit code 1). This confirms no `v0.6.5` GitHub Release exists, corroborating the two empty tag
checks above through an independent read path.

State explicitly, for the record: no pull request was opened or merged by this phase, no package was
uploaded to PyPI, no GitHub Release was created, and no Read the Docs setting was changed. This
task's own actions were limited to reading git/GitHub state and running the read-only/build-only
commands transcribed above; no tag was created "to check whether it works," nothing was pushed, and
no pull request was opened.

### SC#5 verdict

**SC#5: MET.** Both no-tag checks (local and remote) are empty, the optional `gh` release query
independently confirms no `v0.6.5` release exists, and no irreversible action of any kind was taken
during this phase's execution.
