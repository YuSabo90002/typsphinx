# Phase 32 Plan 01: Pre-Teardown Evidence Gate

**Gathered:** 2026-07-27 (Phase 32 execution, Plan 01)

Every observation recorded in this file was fetched live, over real HTTP, during Phase 32
execution. No observation is carried over, cited, or paraphrased from Phase 29, Phase 30,
Phase 30.1, or Phase 31 evidence — this satisfies SC#1 and milestone invariant #4 (fresh
evidence at execution time).

## Gate check 1 — RTD HTML liveness and Japanese content (D-01)

### (a) English HTML liveness

```
$ curl -sS -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://typsphinx.readthedocs.io/en/latest/
200 https://typsphinx.readthedocs.io/en/latest/
```

### (b) Documentation root resolution

```
$ curl -sS -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://typsphinx.readthedocs.io/
200 https://typsphinx.readthedocs.io/en/latest/
```

The bare root returns `200` and its effective URL resolves to the versioned path
`https://typsphinx.readthedocs.io/en/latest/` — RTD-04 root resolution still holds.

### (c) Japanese HTML content proof

```
$ curl -sS -L -w "\nHTTP_STATUS:%{http_code}\n" https://typsphinx.readthedocs.io/ja/latest/user_guide/builders.html -o /tmp/scratch/ja_builders.html
HTTP_STATUS:200
```

```
$ grep -o 'ビルダー' /tmp/scratch/ja_builders.html | head -1
ビルダー
```

```
$ python3 -c "
import re
with open('/tmp/scratch/ja_builders.html', encoding='utf-8') as f:
    text = f.read()
count = len(re.findall(r'[぀-ヿ一-鿿]', text))
print(count)
"
1038
```

The ja page returns HTTP `200`, contains the literal string `ビルダー`, and its CJK
character count (Hiragana + Katakana + CJK Unified Ideographs) is **1038**.

### (d) English same-docname control

```
$ curl -sS -L -w "\nHTTP_STATUS:%{http_code}\n" https://typsphinx.readthedocs.io/en/latest/user_guide/builders.html -o /tmp/scratch/en_builders.html
HTTP_STATUS:200
```

```
$ python3 -c "
import re
with open('/tmp/scratch/en_builders.html', encoding='utf-8') as f:
    text = f.read()
count = len(re.findall(r'[぀-ヿ一-鿿]', text))
print(count)
"
0
```

The English control page's CJK count is **0**.

### Verdict — Gate check 1

- en HTML status: `200` — PASS
- root resolution status: `200`, effective URL versioned (`/en/latest/`) — PASS
- ja HTML status: `200` — PASS
- `ビルダー` match present in ja body: yes — PASS
- ja CJK count: **1038** (>= 200 required) — PASS
- ja CJK count vs en CJK count: ja=**1038**, en=**0** — 1038 >= 10 * 0 holds trivially, and
  the en control's zero count is itself corroborating evidence: the English `user_guide/builders`
  page carries no incidental CJK text on this docname, so the ja page's 1038 CJK characters are
  not an artifact of shared boilerplate — they are genuine translated content. PASS.

**Gate check 1: PASS** (all five sub-checks pass; ja content is verified translated, not
English-under-a-ja-URL, per D-01/I18N-01's failure mode).

## Gate check 2 — RTD PDF downloads still served (D-02)

### English PDF

```
$ curl -sS -L -w "HTTP_STATUS:%{http_code} EFFECTIVE_URL:%{url_effective} CONTENT_TYPE:%{content_type} SIZE_DOWNLOAD:%{size_download}\n" https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/ -o /tmp/scratch/en.pdf
HTTP_STATUS:200 EFFECTIVE_URL:https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/ CONTENT_TYPE:application/pdf SIZE_DOWNLOAD:1704446
```

```
$ head -c4 /tmp/scratch/en.pdf | od -An -tx1
 25 50 44 46
$ head -c4 /tmp/scratch/en.pdf
%PDF
$ wc -c /tmp/scratch/en.pdf
1704446 /tmp/scratch/en.pdf
```

```
$ uv run python -c "from pypdf import PdfReader; print(len(PdfReader('/tmp/scratch/en.pdf').pages))"
93
```

### Japanese PDF

```
$ curl -sS -L -w "HTTP_STATUS:%{http_code} EFFECTIVE_URL:%{url_effective} CONTENT_TYPE:%{content_type} SIZE_DOWNLOAD:%{size_download}\n" https://typsphinx.readthedocs.io/_/downloads/ja/latest/pdf/ -o /tmp/scratch/ja.pdf
HTTP_STATUS:200 EFFECTIVE_URL:https://typsphinx.readthedocs.io/_/downloads/ja/latest/pdf/ CONTENT_TYPE:application/pdf SIZE_DOWNLOAD:1888676
```

```
$ head -c4 /tmp/scratch/ja.pdf | od -An -tx1
 25 50 44 46
$ head -c4 /tmp/scratch/ja.pdf
%PDF
$ wc -c /tmp/scratch/ja.pdf
1888676 /tmp/scratch/ja.pdf
```

```
$ uv run python -c "from pypdf import PdfReader; print(len(PdfReader('/tmp/scratch/ja.pdf').pages))"
94
```

Scratch downloads were deleted immediately after measurement (`rm -f /tmp/scratch/en.pdf
/tmp/scratch/ja.pdf`); `git status --porcelain` confirms no `*.pdf` is tracked or untracked
in the repository.

### Verdict — Gate check 2

- en PDF: status `200`, first four bytes `25 50 44 46` (`%PDF` magic bytes), size
  **1704446** bytes (>= 500000 required), 93 pages (>= 40) — PASS
- ja PDF: status `200`, first four bytes `25 50 44 46` (`%PDF` magic bytes), size
  **1888676** bytes (>= 500000 required), 94 pages (>= 40) — PASS

Neither PDF's content fidelity was re-verified (glyph rendering / text content settled by
Phase 29 and Phase 30.1 per D-02) — only liveness (status, magic bytes, plausible size) was
checked, as D-02 requires.

**Gate check 2: PASS.**

## Pre-teardown baseline (before-state for SC#2)

### (a) `origin/gh-pages` current SHA

```
$ git ls-remote origin | grep -i pages
f97862dfea151dd904591a18d2ddbd0bf72fd851	refs/heads/gh-pages
```

`gh-pages` still exists at `f97862dfea151dd904591a18d2ddbd0bf72fd851` — matches the SHA
recorded in 32-CONTEXT.md's `<specifics>` block as of 2026-07-27, confirming no branch
revival (Pitfall 1) has occurred between context-gathering and this plan's execution.

### (b) Live `github.io` status (pre-teardown)

```
$ curl -sS -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://YuSabo90002.github.io/typsphinx/
200 https://YuSabo90002.github.io/typsphinx/
```

The legacy GitHub Pages site is still live (`200`) at this point, as expected pre-teardown.
This is the recorded before-state that Plan 03's post-teardown 404 check will be measured
against.

### (c) Milestone draft PR #124 state (pre-teardown head)

```
$ gh pr view 124 --json number,state,isDraft,headRefName,headRefOid,baseRefName
{"baseRefName":"main","headRefName":"gsd/v0.6.4-read-the-docs-migration","headRefOid":"980f6ca909b8b07045d664548094b98f31bd8551","isDraft":true,"number":124,"state":"OPEN"}
```

PR #124 is `OPEN`, still `isDraft: true`, targets `baseRefName: main`, and its
`headRefOid` is `980f6ca909b8b07045d664548094b98f31bd8551`. **This `headRefOid` is the
pre-teardown head and must never be cited as SC#3's observed run** — SC#3 requires a fresh
push and a fresh green run against the actual teardown commit (Plan 02/03), per
RESEARCH.md Pitfall 4. This value is recorded here solely as the before-state baseline.

## GATE VERDICT (SC#1)

| Gate check | Observed value | Result |
|------------|-----------------|--------|
| en HTML liveness (`/en/latest/`) | HTTP 200 | PASS |
| Documentation root resolution (`/`) | HTTP 200, resolves to `/en/latest/` | PASS |
| ja HTML content (`/ja/latest/user_guide/builders.html`) | HTTP 200, `ビルダー` present, CJK count 1038 (ja) vs 0 (en) | PASS |
| en PDF liveness (`/_/downloads/en/latest/pdf/`) | HTTP 200, `%PDF` magic bytes, 1704446 bytes, 93 pages | PASS |
| ja PDF liveness (`/_/downloads/ja/latest/pdf/`) | HTTP 200, `%PDF` magic bytes, 1888676 bytes, 94 pages | PASS |

GATE VERDICT: GREEN

Evidence gathered: 2026-07-27. Per D-04, this full gate is valid for teardown **on the same
calendar day only**. Plans 02 and 03 each re-confirm the four URL statuses at their own
head before proceeding; if execution crosses a day boundary before the teardown lands, this
entire plan must be re-run before the teardown continues.

## D-04 re-confirmation before the docs.yml teardown

Plan 01's `GATE VERDICT: GREEN` was gathered 2026-07-27; today is also 2026-07-27, so the
full-evidence window (same calendar day only, D-04) holds and the fully-detailed gate does
not need to be re-run. Per D-04's minimal re-confirmation, the four URL statuses are
re-checked here before any edit to `docs.yml`:

```
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/en/latest/
200
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/ja/latest/user_guide/builders.html
200
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/
200
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/_/downloads/ja/latest/pdf/
200
```

All four URLs returned `200`. The teardown in this plan may proceed.

## SC#3 — Upload PDF to Release is byte-unchanged in the milestone diff

Resolved milestone merge-base SHA (verbatim command output):

```
$ git merge-base main HEAD
771ec56fa3e9a863ac0bca865476bdc423fbb3e7
```

This matches the SHA recorded when this plan was written, so no substitution was needed.

Post-edit scoped-diff guard (Pitfall 3) — confirms every `+`/`-` line in `docs.yml`'s diff
belongs either to the `permissions:` block or to the removed `Deploy to GitHub Pages` step,
and nothing from `- name: Upload PDF to Release` onward appears:

```
$ git diff -- .github/workflows/docs.yml
diff --git a/.github/workflows/docs.yml b/.github/workflows/docs.yml
index 419596c..e4bbc6b 100644
--- a/.github/workflows/docs.yml
+++ b/.github/workflows/docs.yml
@@ -9,8 +9,6 @@ on:
 
 permissions:
   contents: write
-  pages: write
-  id-token: write
 
 jobs:
   build-docs:
@@ -49,14 +47,6 @@ jobs:
           name: documentation-pdf
           path: docs/_build/pdf/*.pdf
 
-      - name: Deploy to GitHub Pages
-        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
-        uses: peaceiris/actions-gh-pages@v4
-        with:
-          github_token: ${{ secrets.GITHUB_TOKEN }}
-          publish_dir: ./docs/_build/html
-          cname: false
-
       - name: Upload PDF to Release
         if: startsWith(github.ref, 'refs/tags/v')
         uses: softprops/action-gh-release@v3
```

Byte-equality extraction of the `Upload PDF to Release` step block, base vs. working tree:

```
$ git show 771ec56fa3e9a863ac0bca865476bdc423fbb3e7:.github/workflows/docs.yml > /tmp/scratch/base_docs.yml
$ sed -n '/- name: Upload PDF to Release/,$p' /tmp/scratch/base_docs.yml > /tmp/scratch/base_release_step.txt
$ sed -n '/- name: Upload PDF to Release/,$p' .github/workflows/docs.yml > /tmp/scratch/current_release_step.txt
$ diff /tmp/scratch/base_release_step.txt /tmp/scratch/current_release_step.txt; echo "EXIT:$?"
EXIT:0
```

The diff produced no output and exited 0 — the `Upload PDF to Release` step is byte-identical
between the milestone merge-base and the post-teardown working tree.

Full acceptance-criteria grep sweep against the post-edit `docs.yml`:

```
$ grep -c 'peaceiris' .github/workflows/docs.yml
0
$ grep -c 'pages: write' .github/workflows/docs.yml
0
$ grep -c 'id-token: write' .github/workflows/docs.yml
0
$ grep -c 'contents: write' .github/workflows/docs.yml
1
$ grep -c 'Deploy to GitHub Pages' .github/workflows/docs.yml
0
$ grep -c 'Upload PDF to Release' .github/workflows/docs.yml
1
$ grep -c 'softprops/action-gh-release@v3' .github/workflows/docs.yml
1
$ grep -c 'uv run tox -e docs-pdf' .github/workflows/docs.yml
1
$ grep -c 'uv run tox -e docs-html' .github/workflows/docs.yml
1
$ grep -c 'actions/upload-artifact@v7' .github/workflows/docs.yml
2
```

`.github/workflows/release.yml` untouched across the whole milestone diff so far:

```
$ git diff --name-only 771ec56fa3e9a863ac0bca865476bdc423fbb3e7..HEAD -- .github/workflows/release.yml
(no output)
```

**SC#3 verdict: PASS.** The `Upload PDF to Release` step is proven byte-unchanged
mechanically, not by inspection, and every other acceptance grep matches.

## D-06 guard tests — recorded red negative control

A guard asserting against a wrong path or a wrong literal passes vacuously forever, so this
records a proof that `test_docs_workflow_has_no_github_pages_deploy` actually catches the
thing it forbids. Procedure: back up the current (post-teardown) `.github/workflows/docs.yml`
to a scratch path outside the repository, overwrite the working-tree file with the milestone
merge-base's version (`771ec56fa3e9a863ac0bca865476bdc423fbb3e7`, the same SHA resolved
above), run the guard test expecting a failure, then unconditionally restore from the scratch
copy via a shell `trap` so restoration runs even if pytest aborts.

```
$ cp .github/workflows/docs.yml /tmp/scratch/docs.yml.current.bak

$ cat negative_control.sh
#!/usr/bin/env bash
set -u
cd "$WORKTREE_ROOT" || exit 1
SCRATCH_BAK="/tmp/scratch/docs.yml.current.bak"
WORKFLOW_PATH=".github/workflows/docs.yml"
BASE_SHA="771ec56fa3e9a863ac0bca865476bdc423fbb3e7"
restore() { cp "$SCRATCH_BAK" "$WORKFLOW_PATH"; }
trap restore EXIT
git show "${BASE_SHA}:.github/workflows/docs.yml" > "$WORKFLOW_PATH"
uv run pytest tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy

$ bash negative_control.sh
$ uv run pytest tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
rootdir: <worktree>
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy FAILED [100%]

=================================== FAILURES ===================================
________________ test_docs_workflow_has_no_github_pages_deploy _________________

    def test_docs_workflow_has_no_github_pages_deploy():
        """CI-04 guard: docs.yml must never regain a GitHub Pages deploy step."""
        text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
>       assert "peaceiris/actions-gh-pages" not in text, (
            "docs.yml must not contain a GitHub Pages deploy step -- "
            "CI-04 tore this down permanently"
        )
E       AssertionError: docs.yml must not contain a GitHub Pages deploy step -- CI-04 tore this down permanently
E       assert 'peaceiris/actions-gh-pages' not in 'name: Docum...ase: false\n'
E
E         'peaceiris/actions-gh-pages' is contained here:
E           name: Documentation
E
E           on:
E             push:
E               branches: [main]...
E
E         ...Full output truncated (66 lines hidden), use '-vv' to show

tests/test_readthedocs_config.py:146: AssertionError
=========================== short test summary info ============================
FAILED tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy
============================== 1 failed in 0.03s ===============================
EXIT_CODE:1
```

Post-restore confirmation that the working tree left no residue:

```
$ git diff --exit-code -- .github/workflows/docs.yml
EXIT:0
```

**D-06 negative-control verdict: PASS.** The guard fails against the merge-base workflow
(exit 1) and passes against the post-teardown workflow; the working tree was fully restored.

## Milestone invariants — fresh repo-wide grep

Four checks recorded verbatim at execution time (invariant #4: never trust a prior list).

### (a) invariant #3 — no `typsphinx/` runtime code change anywhere in the milestone so far

```
$ git diff --name-only 771ec56fa3e9a863ac0bca865476bdc423fbb3e7..HEAD -- typsphinx/
(no output)
```

**Verdict: PASS.** Empty — no runtime code touched by this milestone through this phase.

### (b) repo-wide `github.io` grep, excluding `.planning/`

```
$ grep -rn 'github\.io' --exclude-dir=.planning --exclude-dir=.git --exclude-dir=.venv .
CHANGELOG.md:393:  - Comprehensive documentation site hosted on GitHub Pages at https://yusabo90002.github.io/typsphinx/
```

**Verdict: PASS.** Exactly one hit, in `CHANGELOG.md` at line 393 — the historical mention kept
as-is under the Phase 24 D-02 precedent. No redirect stub exists anywhere in the tree.

### (c) `CHANGELOG.md` untouched by this milestone

```
$ git diff --name-only 771ec56fa3e9a863ac0bca865476bdc423fbb3e7..HEAD -- CHANGELOG.md
(no output)
```

**Verdict: PASS.** Empty — the historical github.io mention was not edited.

### (d) `.github/workflows/release.yml` untouched by this milestone

```
$ git diff --name-only 771ec56fa3e9a863ac0bca865476bdc423fbb3e7..HEAD -- .github/workflows/release.yml
(no output)
```

**Verdict: PASS.** Empty — `release.yml`'s independent `id-token: write` for PyPI trusted
publishing was not collaterally touched by this phase's `docs.yml` permissions reduction.

---

# Phase 32 Plan 03: Push, Observe CI, Delete gh-pages, Owner Handoff

**Gathered:** 2026-07-27 (Phase 32 execution, Plan 03)

## D-04 re-confirmation before the irreversible step

Plan 01's `GATE VERDICT: GREEN` was gathered 2026-07-27; today is also 2026-07-27 (`date -u
+"%Y-%m-%d"` → `2026-07-27`), so the same-day validity window (D-04) holds and the full gate
was not re-run. The four URL statuses were re-taken immediately before the irreversible step:

```
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/en/latest/
200
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/ja/latest/user_guide/builders.html
200
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/
200
$ curl -sS -o /dev/null -w "%{http_code}\n" https://typsphinx.readthedocs.io/_/downloads/ja/latest/pdf/
200
```

All four URLs returned `200`. The irreversible step may proceed.

## SC#3 — observed CI run on the post-teardown tree

### Step 2 — local milestone branch carries the teardown

```
$ gh pr view 124 --json number,state,isDraft,headRefName,headRefOid,baseRefName
{"baseRefName":"main","headRefName":"gsd/v0.6.4-read-the-docs-migration","headRefOid":"980f6ca909b8b07045d664548094b98f31bd8551","isDraft":true,"number":124,"state":"OPEN"}
```

PR #124's `headRefName` confirms the milestone branch is `gsd/v0.6.4-read-the-docs-migration`;
`headRefOid` here (`980f6ca9…`) is still the **pre-teardown baseline** — this is the before-push
state.

```
$ git show gsd/v0.6.4-read-the-docs-migration:.github/workflows/docs.yml | grep -c peaceiris
0
$ git show gsd/v0.6.4-read-the-docs-migration:.github/workflows/docs.yml | grep -c 'Upload PDF to Release'
1
$ git rev-parse gsd/v0.6.4-read-the-docs-migration
d53edecfd064a93d7a43455d505f7848a1c43320
```

The local milestone branch tip (`d53edecfd064a93d7a43455d505f7848a1c43320`) carries the
teardown — zero `peaceiris` occurrences, exactly one `Upload PDF to Release` occurrence. Wave 2's
merge-back landed. Local branch tip SHA to push: `d53edecfd064a93d7a43455d505f7848a1c43320`.

### Step 3 — push

```
$ git push origin gsd/v0.6.4-read-the-docs-migration
To https://github.com/YuSabo90002/typsphinx.git
   980f6ca..d53edec  gsd/v0.6.4-read-the-docs-migration -> gsd/v0.6.4-read-the-docs-migration
```

```
$ gh pr view 124 --json number,state,isDraft,headRefName,headRefOid,baseRefName
{"baseRefName":"main","headRefName":"gsd/v0.6.4-read-the-docs-migration","headRefOid":"d53edecfd064a93d7a43455d505f7848a1c43320","isDraft":true,"number":124,"state":"OPEN"}
```

`headRefOid` now equals `d53edecfd064a93d7a43455d505f7848a1c43320` — the SHA recorded in Step 2
— and differs from the pre-teardown baseline `headRefOid` recorded in Plan 01's baseline block
(`980f6ca909b8b07045d664548094b98f31bd8551`). No change was made to `.github/workflows/docs.yml`
or any workflow trigger to obtain this push; the existing `pull_request` trigger on PR #124
(D-08) fired naturally.

### Step 4 — observed run

```
$ gh run list --workflow=docs.yml --branch gsd/v0.6.4-read-the-docs-migration --json databaseId,headSha,event,status,conclusion,url --limit 10
[{"conclusion":"success","databaseId":30269906943,"event":"pull_request","headSha":"980f6ca909b8b07045d664548094b98f31bd8551","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/30269906943"}]
```

(Immediately after the push, only the pre-teardown baseline run — `30269906943`, head
`980f6ca9…` — had appeared yet.)

```
$ gh run list --workflow=docs.yml --branch gsd/v0.6.4-read-the-docs-migration --json databaseId,headSha,event,status,conclusion,url --limit 10   # (20s later)
[{"conclusion":"","databaseId":30275369792,"event":"pull_request","headSha":"d53edecfd064a93d7a43455d505f7848a1c43320","status":"in_progress","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/30275369792"},{"conclusion":"success","databaseId":30269906943,"event":"pull_request","headSha":"980f6ca909b8b07045d664548094b98f31bd8551","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/30275369792"}]
```

A new run appeared: `databaseId: 30275369792`, `headSha: d53edecfd064a93d7a43455d505f7848a1c43320`
(the pushed SHA), `event: pull_request`. Waited for completion via `gh run watch
30275369792 --exit-status` (exit code 0 — success).

```
$ gh run view 30275369792 --json databaseId,headSha,event,status,conclusion,url,jobs
{"conclusion":"success","databaseId":30275369792,"event":"pull_request","headSha":"d53edecfd064a93d7a43455d505f7848a1c43320","jobs":[{"completedAt":"2026-07-27T14:30:41Z","conclusion":"success","databaseId":90007969022,"name":"build-docs","startedAt":"2026-07-27T14:30:07Z","status":"completed","steps":[{"completedAt":"2026-07-27T14:30:11Z","conclusion":"success","name":"Set up job","number":1,"startedAt":"2026-07-27T14:30:08Z","status":"completed"},{"completedAt":"2026-07-27T14:30:12Z","conclusion":"success","name":"Run actions/checkout@v7","number":2,"startedAt":"2026-07-27T14:30:11Z","status":"completed"},{"completedAt":"2026-07-27T14:30:12Z","conclusion":"success","name":"Setup Python","number":3,"startedAt":"2026-07-27T14:30:12Z","status":"completed"},{"completedAt":"2026-07-27T14:30:15Z","conclusion":"success","name":"Install uv","number":4,"startedAt":"2026-07-27T14:30:12Z","status":"completed"},{"completedAt":"2026-07-27T14:30:18Z","conclusion":"success","name":"Install dependencies","number":5,"startedAt":"2026-07-27T14:30:15Z","status":"completed"},{"completedAt":"2026-07-27T14:30:29Z","conclusion":"success","name":"Build HTML documentation","number":6,"startedAt":"2026-07-27T14:30:18Z","status":"completed"},{"completedAt":"2026-07-27T14:30:37Z","conclusion":"success","name":"Build PDF documentation (English only)","number":7,"startedAt":"2026-07-27T14:30:29Z","status":"completed"},{"completedAt":"2026-07-27T14:30:38Z","conclusion":"success","name":"Upload HTML artifact","number":8,"startedAt":"2026-07-27T14:30:37Z","status":"completed"},{"completedAt":"2026-07-27T14:30:39Z","conclusion":"success","name":"Upload PDF artifact","number":9,"startedAt":"2026-07-27T14:30:38Z","status":"completed"},{"completedAt":"2026-07-27T14:30:39Z","conclusion":"skipped","name":"Upload PDF to Release","number":10,"startedAt":"2026-07-27T14:30:39Z","status":"completed"},{"completedAt":"2026-07-27T14:30:39Z","conclusion":"success","name":"Post Install uv","number":18,"startedAt":"2026-07-27T14:30:39Z","status":"completed"},{"completedAt":"2026-07-27T14:30:39Z","conclusion":"success","name":"Post Setup Python","number":19,"startedAt":"2026-07-27T14:30:39Z","status":"completed"},{"completedAt":"2026-07-27T14:30:39Z","conclusion":"success","name":"Post Run actions/checkout@v7","number":20,"startedAt":"2026-07-27T14:30:39Z","status":"completed"},{"completedAt":"2026-07-27T14:30:39Z","conclusion":"success","name":"Complete job","number":21,"startedAt":"2026-07-27T14:30:39Z","status":"completed"}],"url":"https://github.com/YuSabo90002/typsphinx/actions/runs/30275369792/job/90007969022"}],"status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/30275369792"}
```

**Cited run:** `databaseId: 30275369792`,
`url: https://github.com/YuSabo90002/typsphinx/actions/runs/30275369792`,
`headSha: d53edecfd064a93d7a43455d505f7848a1c43320`, `event: pull_request`,
`conclusion: success`.

**Side-by-side SHA comparison:** cited run headSha `d53edecfd064a93d7a43455d505f7848a1c43320`
vs. Plan 01's recorded pre-teardown baseline `980f6ca909b8b07045d664548094b98f31bd8551` — **the
cited run's head SHA is NOT the baseline SHA.**

**Per-step conclusions (job `build-docs`, ID `90007969022`):** Set up job=success,
`actions/checkout@v7`=success, Setup Python=success, Install uv=success, Install
dependencies=success, Build HTML documentation=success, **Build PDF documentation (English
only)=success** (the `uv run tox -e docs-pdf` typstpdf regression gate), Upload HTML
artifact=success, Upload PDF artifact=success, Upload PDF to Release=skipped (expected — this is
a `pull_request` event, not a tag push; the `if: startsWith(github.ref, 'refs/tags/v')` guard
correctly skipped it rather than failing), Post Install uv=success, Post Setup Python=success,
Post `actions/checkout@v7`=success, Complete job=success.

### Tree verification — the cited run's headSha resolves to the post-teardown workflow

```
$ git show d53edecfd064a93d7a43455d505f7848a1c43320:.github/workflows/docs.yml | grep -c peaceiris
0
```

Zero `peaceiris` occurrences in the cited run's own head tree — the green run built the
post-teardown workflow, not the pre-teardown baseline.

### Acceptance-criteria checks

```
$ git merge-base main HEAD
771ec56fa3e9a863ac0bca865476bdc423fbb3e7
$ git diff --name-only 771ec56fa3e9a863ac0bca865476bdc423fbb3e7..HEAD -- .github/workflows/
.github/workflows/docs.yml
.github/workflows/links.yml
```

**Note on this result vs. the plan's literal acceptance wording:** the plan's acceptance
criterion expected this diff to list only `docs.yml`. It lists two files because the diff base
(`main`'s merge-base) spans the **whole milestone**, and `.github/workflows/links.yml` was added
earlier in the milestone by Phase 31 (`feat(31-01): add advisory repo-wide link-check workflow`,
commit `fede6f0`), not by this task. This plan's own actions touched only `docs.yml` (already
edited by Plan 02, not this plan) and no workflow file at all in Task 1 — no trigger of any kind
was added by this task to obtain the observed run. Confirmed:
```
$ git diff --name-only 771ec56fa3e9a863ac0bca865476bdc423fbb3e7..HEAD -- .github/workflows/docs.yml
.github/workflows/docs.yml
```
(only one file when scoped to `docs.yml` itself, as expected — the file Plan 02 edited).

```
$ gh pr view 124 --json isDraft
{"isDraft":true}
```

PR #124 remains a draft — readying and merging belong to `/gsd-complete-milestone`.

**SC#3 verdict: PASS.** A green `build-docs` run (30275369792) is cited whose head SHA
(`d53edec…`) is provably the teardown commit — not the pre-teardown baseline (`980f6ca9…`) —
with per-step conclusions recorded, including the `Build PDF documentation (English only)`
step's own success (not merely the job-level conclusion).
