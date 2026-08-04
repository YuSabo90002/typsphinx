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
<!-- gsd:write-continue -->
