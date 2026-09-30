# Phase 44 Plan 03 — Gate Evidence 03 (CONF-08 / SC#4 measured before/after record)

This file discharges ROADMAP SC#4: the CONF-08 output-filename rename, plus D-05's second half (the
`.typ` content structure change — untemplated body vs. fully templated), measured on two real
`sphinx-build` runs against two named commits, each built from its own throwaway git worktree with
its own `uv sync`. It also hands the measured pair to Phase 46 as CHANGELOG source text for REL-06.

**Every figure in this file was produced by a command run in this task's own session.** None of it
was transcribed or recalled from a planning document. `44-CONTEXT.md`'s D-05 measurement (373 bytes /
8209 bytes) was taken against a DIFFERENT minimal project (`project = 'My Cool Project'`) than the
`default_typst_documents_gate` fixture this plan measures (`project = 'Quickstart Default Gate'`),
so its figures are expected to differ from this file's and are NOT copied in. Where a figure differs
from a planning document's, the number measured here wins, and the divergence is stated rather than
hidden — see the note at the end of § 3.

---

## 1. The two named commits

**PRE** — the RED commit plan 44-01 recorded in `44-GATE-EVIDENCE-01.md` § "2. RED commit": the
last commit on this phase's history that predates every production change in this phase.

**Command:** `git log -1 --oneline eeb930429c2608c5245f2769fc6b7edbbed206c5`

```
eeb9304 test(44-01): add RED gate for unset typst_documents (CONF-08)
```

**POST** — this worktree's current `git rev-parse HEAD` at the start of this plan's execution.

**Command:** `git log -1 --oneline b819c8bfaeb18745db44ee909ed2d12314b673b6`

```
b819c8b docs(phase-44): update tracking after wave 2
```

Both are real 40-hex SHAs:

```
eeb930429c2608c5245f2769fc6b7edbbed206c5
b819c8bfaeb18745db44ee909ed2d12314b673b6
```

**Command:** `git show --name-only eeb930429c2608c5245f2769fc6b7edbbed206c5`

```
commit eeb930429c2608c5245f2769fc6b7edbbed206c5
Author: yuta <yusabo90002@gmail.com>
Date:   Tue Aug 4 14:11:24 2026 +0900

    test(44-01): add RED gate for unset typst_documents (CONF-08)

.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-01.md
tests/fixtures/default_typst_documents_gate/conf.py
tests/fixtures/default_typst_documents_gate/index.rst
tests/test_default_typst_documents_gate.py
```

No path begins `typsphinx/` — confirmed also by `git show --name-only ... | grep -c '^typsphinx/'` →
`0`. The pre-change side really predates every production change in this phase.

**Command:** `git ls-tree -r --name-only eeb930429c2608c5245f2769fc6b7edbbed206c5 | grep default_typst_documents_gate`

```
tests/fixtures/default_typst_documents_gate/conf.py
tests/fixtures/default_typst_documents_gate/index.rst
tests/test_default_typst_documents_gate.py
```

The fixture's `conf.py`/`index.rst` exist at PRE — the same project is built twice, once per side.

**Command:** `grep -c 'def _default_typst_documents' typsphinx/builder.py` (in the current, POST tree)

```
1
```

**Command:** `grep -c 'isinstance(docname, str)' typsphinx/builder.py` (in the current, POST tree)

```
1
```

POST contains both waves' production changes (44-01's derivation function, 44-02's docname guard).

**Command:** `git diff --stat eeb930429c2608c5245f2769fc6b7edbbed206c5..b819c8bfaeb18745db44ee909ed2d12314b673b6 -- typsphinx/`

```
 typsphinx/__init__.py |  4 ++--
 typsphinx/builder.py  | 49 +++++++++++++++++++++++++++++++++++++++++++++++--
 2 files changed, 49 insertions(+), 4 deletions(-)
```

Only `typsphinx/__init__.py` and `typsphinx/builder.py` — nothing else under `typsphinx/` changed
between the two named commits.

**Command (unscoped, deliberately larger):** `git diff --stat eeb930429c2608c5245f2769fc6b7edbbed206c5..b819c8bfaeb18745db44ee909ed2d12314b673b6`

```
 .planning/REQUIREMENTS.md                          |   4 +-
 .planning/ROADMAP.md                               |   9 +-
 .planning/STATE.md                                 |  14 +-
 .../44-01-SUMMARY.md                               | 184 ++++++++++++
 .../44-02-SUMMARY.md                               | 167 +++++++++++
 .../44-GATE-EVIDENCE-01.md                         | 312 ++++++++++++++++++++-
 .../44-GATE-EVIDENCE-02.md                         | 195 +++++++++++++
 .../empty_typst_documents_optout_gate/conf.py      |  22 ++
 .../empty_typst_documents_optout_gate/index.rst    |   4 +
 .../explicit_typst_documents_wins_gate/conf.py     |  23 ++
 .../explicit_typst_documents_wins_gate/index.rst   |   4 +
 tests/fixtures/non_str_docname_gate/conf.py        |  41 +++
 tests/fixtures/non_str_docname_gate/index.rst      |   4 +
 tests/test_builder.py                              |  16 +-
 tests/test_builder_requirement13.py                |  18 +-
 tests/test_default_typst_documents_derivation.py   | 155 ++++++++++
 tests/test_default_typst_documents_gate.py         |  55 ++++
 tests/test_empty_typst_documents_optout_gate.py    | 150 ++++++++++
 tests/test_non_str_docname_gate.py                 | 152 ++++++++++
 typsphinx/__init__.py                              |   4 +-
 typsphinx/builder.py                                |  49 +-
 21 files changed, 1553 insertions(+), 29 deletions(-)
```

**Why the unscoped diff is larger (one sentence):** the difference is entirely this phase's own new
test fixtures, new test modules, evidence files, and planning-tracking updates from plans 44-01 and
44-02 landing between the two named commits — none of it is production code outside `typsphinx/`.

---

## 2. Pre-change worktree isolation proof

**Why this section exists:** an unprovisioned worktree resolves `import typsphinx` to the MAIN
checkout via the PEP-660 editable finder baked into the main `.venv`, so the "pre-change" build
would silently run POST-change code and the whole record would be vacuous. This section records
that the pre-change side really ran its own copy of `typsphinx`.

**Worktree creation:**
```
git worktree add --detach <scratch>/pre-wt eeb930429c2608c5245f2769fc6b7edbbed206c5
```
Output:
```
Preparing worktree (detached HEAD eeb9304)
HEAD is now at eeb9304 test(44-01): add RED gate for unset typst_documents (CONF-08)
```

**Provisioning:**
```
(cd <scratch>/pre-wt && env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev)
```
Exited `0`; the resolved package set included:
```
typsphinx==0.7.0 (from file:///tmp/claude-1000/-home-yuta-Documents-typsphinx/d723f150-0645-48be-bfff-30b5818e11fb/scratchpad/measure-44-03/pre-wt)
```
`uv` itself resolved the editable install to THIS worktree's own path, not the main checkout's.

**Shim (NixOS-sandbox hazard, documented runbook):**
```
ln -sf /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv <scratch>/pre-wt/.venv/bin/uv
readlink -f <scratch>/pre-wt/.venv/bin/uv
```
```
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
```
**Acceptance test:** `<scratch>/pre-wt/.venv/bin/uv --version`
```
uv 0.11.25 (x86_64-unknown-linux-gnu)
```

**Isolation proof:**
```
(cd <scratch>/pre-wt && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())")
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/d723f150-0645-48be-bfff-30b5818e11fb/scratchpad/measure-44-03/pre-wt/typsphinx/__init__.py
```

This path lies INSIDE the pre-change throwaway worktree (`.../measure-44-03/pre-wt/...`), not
inside the main checkout (`/home/yuta/Documents/typsphinx`) and not inside this plan's own agent
worktree (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9f98e59c06aeda5d`).

`ruff` was not present in this NixOS sandbox's Nix store (matching `42-GATE-EVIDENCE-05.md` § 2's
own recorded limitation) — but neither Task 1 nor Task 2 of this plan invokes `ruff` in either
throwaway worktree, only `uv run python -m sphinx` builds, so this does not weaken the isolation
proof, which rests entirely on the `typsphinx.__file__` path and the `uv` shim above (both present).

---

## 3. Pre-change builds

Both builds run from inside `<scratch>/pre-wt` against the SAME fixture,
`tests/fixtures/default_typst_documents_gate` (present at PRE, confirmed § 1).

### `sphinx-build -b typstpdf`

**Command:**
```
uv run python -m sphinx -b typstpdf -E tests/fixtures/default_typst_documents_gate <scratch>/pre-pdf
```

**Output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <scratch>/pre-pdf/_template.typ
done
writing output... [index] done
WARNING: No documents defined in typst_documents. Nothing to compile.
build succeeded, 1 warning.
```

**Exit status: 0.** Complete typsphinx warning text (verbatim, exactly one): `WARNING: No documents
defined in typst_documents. Nothing to compile.`

**`ls -la <scratch>/pre-pdf/`:**
```
total 8
drwxr-xr-x 1 yuta users   62  8月  4 14:48 .
drwxr-xr-x 1 yuta users   40  8月  4 14:48 ..
drwxr-xr-x 1 yuta users   62  8月  4 14:48 .doctrees
-rw-r--r-- 1 yuta users 2438  8月  4 14:48 _template.typ
-rw-r--r-- 1 yuta users  412  8月  4 14:48 index.typ
```

**PDF count** (`find <scratch>/pre-pdf -name '*.pdf' | wc -l`): **`0`**

**`index.typ` byte size** (`wc -c <scratch>/pre-pdf/index.typ`): **`412`**

**First 20 lines of `index.typ` (verbatim — the file has 17 lines total, all shown):**
```
1	// Essential imports for included document
2	#import "@preview/codly:1.3.0": *
3	#import "@preview/codly-languages:0.1.10": *
4	#import "@preview/mitex:0.2.7": mi, mitex
5	#import "@preview/gentle-clues:1.3.1": *
6	
7	// Initialize codly
8	#show: codly-init.with()
9	#codly(languages: codly-languages)
10	
11	#{
12	[#heading(level: 1, {text("Quickstart Default Gate")}) <index:quickstart-default-gate>]
13	
14	par({text("QSDEFAULTBODY")})
15	
16	
17	}
```

Only `@preview` imports and the body — **no template import, no template function call**. This is
D-05's content half, pre-change: `root_doc` ("index") is NOT treated as a master document because
`typst_documents` resolves to `[]` unset.

### `sphinx-build -b typst`

**Command:**
```
uv run python -m sphinx -b typst -E tests/fixtures/default_typst_documents_gate <scratch>/pre-typ
```

**Output (tail):**
```
preparing documents... Template written to <scratch>/pre-typ/_template.typ
done
writing output... [index] done
build succeeded.
```

**Exit status: 0.**

**Note on figure divergence from `44-CONTEXT.md`:** D-05's own measurement (373-byte `index.typ`,
8209-byte compiled PDF) was taken against a DIFFERENT minimal project (`project = 'My Cool
Project'`, no fixture-file body content beyond the auto-generated Sphinx quickstart skeleton). This
plan's fixture (`tests/fixtures/default_typst_documents_gate`, `project = 'Quickstart Default
Gate'`, containing the literal body text `QSDEFAULTBODY`) is a different, purpose-built project, so
its 412-byte `index.typ` is EXPECTED to differ from D-05's 373-byte figure — both are correct for
their own project; neither transcribes the other. This file's own figures (412 bytes pre-change,
recorded above; the post-change figure appears in § 5 below) are what this record certifies as
measured in THIS session, and they match plan 44-01's own `44-GATE-EVIDENCE-01.md` § 1 RED
measurement exactly (same fixture, same commit lineage), which is the correct cross-check — not
`44-CONTEXT.md`'s figures, which were never claimed to apply to this fixture.
---

## 4. Post-change worktree isolation proof

**Worktree creation:**
```
git worktree add --detach <scratch>/post-wt b819c8bfaeb18745db44ee909ed2d12314b673b6
```
Output:
```
Preparing worktree (detached HEAD b819c8b)
HEAD is now at b819c8b docs(phase-44): update tracking after wave 2
```

**Provisioning:**
```
(cd <scratch>/post-wt && env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev)
```
Exited `0`; the resolved package set included:
```
typsphinx==0.7.0 (from file:///tmp/claude-1000/-home-yuta-Documents-typsphinx/d723f150-0645-48be-bfff-30b5818e11fb/scratchpad/measure-44-03/post-wt)
```

**Shim:**
```
ln -sf /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv <scratch>/post-wt/.venv/bin/uv
readlink -f <scratch>/post-wt/.venv/bin/uv
```
```
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
```
**Acceptance test:** `<scratch>/post-wt/.venv/bin/uv --version`
```
uv 0.11.25 (x86_64-unknown-linux-gnu)
```

**Isolation proof:**
```
(cd <scratch>/post-wt && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())")
```
```
/tmp/claude-1000/-home-yuta-Documents-typsphinx/d723f150-0645-48be-bfff-30b5818e11fb/scratchpad/measure-44-03/post-wt/typsphinx/__init__.py
```

**Both recorded `typsphinx.__file__` paths, side by side:**

| Side | Path |
|------|------|
| pre-change | `.../measure-44-03/pre-wt/typsphinx/__init__.py` |
| post-change | `.../measure-44-03/post-wt/typsphinx/__init__.py` |

The two paths differ (`pre-wt` vs. `post-wt`), and neither is the main checkout
(`/home/yuta/Documents/typsphinx`) nor this plan's own agent worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9f98e59c06aeda5d`) — direct, positive
evidence the two builds in §§ 3 and 5 ran against genuinely different copies of `typsphinx`, which
is what makes the pairing in § 6 meaningful rather than vacuous.

---

## 5. Post-change builds

Both builds run from inside `<scratch>/post-wt` against the SAME fixture,
`tests/fixtures/default_typst_documents_gate`, used in § 3.

### `sphinx-build -b typstpdf`

**Command:**
```
uv run python -m sphinx -b typstpdf -E tests/fixtures/default_typst_documents_gate <scratch>/post-pdf
```

**Output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <scratch>/post-pdf/_template.typ
done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Generated PDF: <scratch>/post-pdf/quickstartdefaultgate.pdf
build succeeded.
```

**Exit status: 0.** **Typsphinx warnings emitted: none.** In particular, no
`WARNING: No documents defined in typst_documents. Nothing to compile.` — that warning is gone
because `typst_documents` now resolves to a derived non-empty list.

**`ls -la <scratch>/post-pdf/`:**
```
total 28
drwxr-xr-x 1 yuta users   144  8月  4 14:49 .
drwxr-xr-x 1 yuta users    86  8月  4 14:49 ..
drwxr-xr-x 1 yuta users    62  8月  4 14:49 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:49 _template.typ
-rw-r--r-- 1 yuta users 17308  8月  4 14:49 quickstartdefaultgate.pdf
-rw-r--r-- 1 yuta users   532  8月  4 14:49 quickstartdefaultgate.typ
```

**PDF count** (`find <scratch>/post-pdf -name '*.pdf' | wc -l`): **`1`**

**`quickstartdefaultgate.typ` byte size** (`wc -c <scratch>/post-pdf/quickstartdefaultgate.typ`):
**`532`**

**First 20 lines of `quickstartdefaultgate.typ` (verbatim — the file has 25 lines total, all shown):**
```
1	// Essential package imports
2	#import "@preview/codly:1.3.0": *
3	#import "@preview/codly-languages:0.1.10": *
4	#import "@preview/mitex:0.2.7": mi, mitex
5	#import "@preview/gentle-clues:1.3.1": *
6	
7	#show: codly-init.with()
8	#codly(languages: codly-languages)
9	
10	#import "_template.typ": project
11	
12	#show: project.with(
13	  title: "Quickstart Default Gate",
14	  authors: ("Test Author",),
15	  date: "1.0.0",
16	  lang: "en",
17	)
18	
19	#{
20	[#heading(level: 1, {text("Quickstart Default Gate")}) <index:quickstart-default-gate>]
```

Lines 10 (`#import "_template.typ": project`) and 12-17 (`#show: project.with(...)`) are the
template import and template function call — present here, absent in § 3's pre-change head. This is
D-05's content half, post-change: `root_doc` ("index") is now treated as a master document.

**First four bytes of `quickstartdefaultgate.pdf`** (`head -c 4 <scratch>/post-pdf/quickstartdefaultgate.pdf | od -c`):
```
%   P   D   F
```
A real PDF (the `%PDF` magic header).

### `sphinx-build -b typst`

**Command:**
```
uv run python -m sphinx -b typst -E tests/fixtures/default_typst_documents_gate <scratch>/post-typ
```

**Output (tail):**
```
preparing documents... Template written to <scratch>/post-typ/_template.typ
done
writing output... [index] done
build succeeded.
```

**Exit status: 0.**

---

## 6. The measured before/after pair

| Cell | Pre-change (§ 3, PRE `eeb9304`) | Post-change (§ 5, POST `b819c8b`) |
|------|----------------------------------|-------------------------------------|
| Emitted `.typ` filename | `index.typ` | `quickstartdefaultgate.typ` |
| Emitted `.typ` byte size | 412 bytes | 532 bytes |
| Template applied (yes/no) | No — `@preview` imports + body only | Yes — `_template.typ` import + `#show: project.with(...)` call |
| Number of `.pdf` files written | 0 | 1 |
| Emitted `.pdf` filename | (none) | `quickstartdefaultgate.pdf` |
| Typsphinx warnings emitted | 1 (`No documents defined in typst_documents. Nothing to compile.`) | 0 |

Every cell above is a figure recorded in § 3 or § 5 of this same file.

**What a user who never set `typst_documents` experiences on upgrade (two sentences):** the emitted
Typst artifact for their root document is renamed from `index.typ` to a project-derived name
(`<make_filename_from_project(project)>.typ`, e.g. `quickstartdefaultgate.typ` for this fixture),
and it is no longer a bare `@preview`-imports-plus-body fragment but a fully templated document —
which matters specifically to anyone who previously wrote `#include("index.typ")` from their own
Typst source, since that include path and the included file's internal structure both change.

---

## 7. CHANGELOG source text for Phase 46 (REL-06)

Phase 46 should quote or adapt the block below directly rather than re-derive it; the underlying
figures live in §§ 3, 5 and 6 of this file.

```markdown
### Changed

- With `typst_documents` unset, `sphinx-build -b typst`/`-b typstpdf` now emits the root document's
  Typst output under a project-derived filename (e.g. `index.typ` → `quickstartdefaultgate.typ` for
  a project named "Quickstart Default Gate") instead of the previous literal `index.typ`. If you
  `#include()` the old file from your own Typst source, update the include path.
- The same unset-config output is now a fully templated Typst document (the shared template's
  `#show: project.with(...)` wrapper applied) rather than a bare fragment of `@preview` imports plus
  body content — and, as a consequence, `sphinx-build -b typstpdf` with `typst_documents` unset now
  produces a real PDF where it previously produced none.
```

---

## 8. Cleanup

**Command:** `git worktree remove --force <scratch>/pre-wt`

**Command:** `git worktree remove --force <scratch>/post-wt`

**Command:** `git worktree list` (after both removals)

```
/home/yuta/Documents/typsphinx                                           b819c8b [gsd/v0.7.1-bug-fix-round]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7ea89f4fa3d64727 b819c8b [worktree-agent-a7ea89f4fa3d64727] locked
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9f98e59c06aeda5d 5f2ce54 [worktree-agent-a9f98e59c06aeda5d] locked
```

Neither `pre-wt` nor `post-wt` appears in the listing above. The main checkout and this plan's own
agent worktree (`agent-a9f98e59c06aeda5d`) are expected to appear; `agent-a7ea89f4fa3d64727` is the
concurrently-running sibling executor's worktree (plan 44-04) — its presence here is expected and is
NOT a leak of this plan's throwaway worktrees, which were named `pre-wt`/`post-wt` and lived entirely
under `/tmp`, outside `.claude/worktrees/`.

**Command:** `git status --porcelain typsphinx/ tests/`

```
(no output)
```

Empty — this plan changed no production code and no test.

---

## 9. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| ROADMAP SC#4 — the output-filename rename is measured, not assumed, on two real builds of the same project across two named commits, covering both D-05 halves (rename + content structure change) | § 1 (two named commits, pathspec-scoped production diff), § 2 & § 4 (per-side `typsphinx.__file__` isolation proofs, proven distinct), § 3 & § 5 (four real builds, exit codes, warnings, byte sizes, verbatim heads, PDF counts), § 6 (the paired table), § 7 (Phase 46 CHANGELOG source text) | **MET** |

**Not owned by this file:**
- SC#1/SC#2 (the derivation itself, the explicit-setting-wins guarantee) — plan 44-01,
  `44-GATE-EVIDENCE-01.md`.
- SC#3 (BLD-01's non-`str` docname hardening) — plan 44-02, `44-GATE-EVIDENCE-02.md`.
- SC#5 (the repo-wide existing-test audit) — plan 44-04, `44-GATE-EVIDENCE-04.md`.
