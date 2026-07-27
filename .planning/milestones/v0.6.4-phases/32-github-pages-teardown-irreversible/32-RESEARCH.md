# Phase 32: GitHub Pages Teardown (IRREVERSIBLE) - Research

**Researched:** 2026-07-27
**Domain:** GitHub Actions CI/CD workflow editing, remote git branch deletion, GitHub Pages
deprovisioning, RTD live-evidence gating
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: ja HTML は内容照合まで踏む。** `/ja/latest/user_guide/builders.html`(65/65 全訳
  docname、Phase 30.1 実測)を curl し、既知の翻訳済み文字列の実在を grep で確認する。
  I18N-01 の故障モード「ビルドは緑なのに 100% 英語配信」(カタログ 24.3% 翻訳)は撤去後も
  存続するため、HTTP 200 + 言語マーカーでは不足。en HTML とルート URL の解決も同時に取る。
- **D-02: PDF は en+ja 両方を配信確認、忠実性の再検証はしない。** 両 PDF URL
  (en は `https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/`、ja は RTD ja
  プロジェクトのダウンロード URL)を curl し、HTTP 200 + PDF マジックバイト + 常識的
  サイズ/ページ数を確認。グリフ・内容一致は Phase 29(en)/ Phase 30.1(ja, D-03 ゲート)が
  検証済みで、`latest` は main 追従のため SHA 比較の基準も動く — ゲートが問うのは
  「今も配信されているか」のみ。
- **D-03: ゲートと撤去は別プランに分離する。** Plan 1 = ゲート(証拠取得・記録のみ、
  リポジトリ変更なし)、Plan 2 = 撤去(Plan 1 の緑を依存条件に)。ゲートが赤(RTD 配信停止を
  検出)なら Plan 2 に構造的に入らず、オーナーにエスカレーションする。
- **D-04: 証拠鮮度は「撤去と同日 + 直前再確認」。** ゲートプランの完全な証拠は同日内で
  有効。撤去プランの先頭で最小の再確認(4 URL の HTTP ステータスのみ)をもう一度取る。
  日をまたいだ場合はゲートプランの完全版を再実行する。
- 記録形式は既定の前例に従う: 逐語のコマンド + 出力転記(Phase 29 D-15 形式)。
- **D-05: デプロイステップ + 未使用権限も削除する。** `peaceiris/actions-gh-pages` ステップ
  に加え、`permissions:` から `pages: write` と `id-token: write` を落とす(実測: peaceiris
  方式は `contents: write` でブランチ push するため両権限は現状でも未使用 — 公式
  `actions/deploy-pages` 方式用)。**`contents: write` はタグ時 Release 添付(softprops)に
  必要なので残置。** SC#3 の byte-unchanged 制約は `Upload PDF to Release` ステップにのみ
  かかる。
- **D-06: 再発防止ガードテストを追加する。** docs.yml に gh-pages デプロイ(peaceiris /
  pages 権限)が不在であること + `Upload PDF to Release` ステップが存在することを断定する
  小テスト。`tests/test_readthedocs_config.py` の既存パターン
  (`test_build_python_matches_docs_workflow` が docs.yml を読んで形状断定)を踏襲。
- **D-07: HTML/PDF アーティファクト upload ステップは残置。** ROADMAP の「撤去対象は公開
  経路のみ」の対象外。`.planning/codebase/INTEGRATIONS.md` の差分更新(docs.yml 削減の
  反映)は Phase 31 D-18 の既決により本フェーズが持つ。
- **D-08: マイルストーン draft PR を main に向けて開き、その pull_request トリガーで
  docs.yml の観測実行を得る。** リポジトリ変更ゼロで Phase 30 UAT test 1(同一構造で
  blocked)と Phase 32 SC#3 の両方を解決する。workflow_dispatch 追加も backstop 繰り延べも
  採らない。正式な ready 化とマージは従来どおり `/gsd-complete-milestone` で。
- **D-09: draft PR は Phase 32 の前に開く。** 順序の循環(Phase 30 完了が Phase 32 の前提 ↔
  Phase 30 の最終 UAT 項目が PR 待ち)を解消するため、次のアクションとして先に draft PR を
  開き、`/gsd-verify-work 30` で Phase 30 UAT を完結させてから Phase 32 を計画/実行する。
  Phase 32 実行中は既存の開いた PR にコミットを積むだけで SC#3 の観測(撤去コミットを head
  とする緑の run の逐語転記)が取れる。
- オーナー手動: リポジトリ Settings → Pages で GitHub Pages サイトを無効化する。ブランチ削除
  だけでは Pages 機能がソース欠損のまま有効に残り得る。観測可能な結果は SC#2 の github.io
  404。
- 議論外のハザード(planner/オーナー判断 — 対処は未決): gh-pages 復活ハザード。`main` 側の
  docs.yml はマイルストーンマージまで旧デプロイステップを保持する。マージ前に main へ push が
  起きると main 上の docs.yml が発火し peaceiris が `gh-pages` を再作成し得る(実測: dependabot
  PR #123 がオープン中)。対処は planner の提案とオーナー判断に委ねる。少なくとも
  `/gsd-complete-milestone` での ls-remote 再検証を推奨として記録する。

### Claude's Discretion

- ゲートで grep する具体的な翻訳済み文字列の選定(D-01)と PDF の「常識的サイズ/ページ数」
  のしきい値(D-02)。
- ガードテストの関数名・断定の厳密さ(D-06)。
- draft PR のタイトル・本文(英語・簡潔 — 外向き成果物の既定に従う)。
- 404 確認のリトライ姿勢(Pages 無効化直後の CDN キャッシュ猶予)。
- INTEGRATIONS.md 差分更新の記述粒度(D-07)。

### Deferred Ideas (OUT OF SCOPE)

- gh-pages 復活ハザードの恒久対処(議論スキップ、planner/オーナー判断)。
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — Future LNK-01 として据え置き(オーナー決定
  2026-07-25)。本フェーズと無関係。
- `2026-07-22-citation-node-support-untracked.md` / `2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`
  / `2026-07-25-derive-typst-lang-duplicated-warning-block.md` /
  `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — いずれも `typsphinx/`
  ランタイム変更を要し、マイルストーン不変量 #3 で本フェーズ対象外。
- Redirect stubs for the old `github.io` URL — owner decision 2026-07-25, permanently no.
- `CHANGELOG.md:393`'s historical `github.io` mention — kept as-is (Phase 24 D-02 precedent).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CI-04 | GitHub Pages no longer hosts or publishes typsphinx documentation, while the `typstpdf` regression gate and the tag-time PDF Release attachment keep working. | Confirmed exact `docs.yml` diff shape (Standard Stack / Code Examples), confirmed live RTD evidence sources for the pre-teardown gate (D-01/D-02), confirmed `git ls-remote` as the branch-existence proof mechanism, confirmed the guard-test file/pattern for D-06, confirmed draft PR #124 already exists and is the SC#3 observation vehicle. |

</phase_requirements>

## Summary

This phase is almost entirely CI/CD-configuration and remote-git-state work — there is no application
code, no new package, and no test-framework gap to fill. `CONTEXT.md` already locks nearly every
implementation decision (D-01 through D-09); this research's job is to confirm the concrete artifacts
those decisions operate on are exactly as described, and to surface the mechanics the planner needs to
turn "delete `peaceiris/actions-gh-pages` and the `gh-pages` branch" into verifiable task steps.

Live verification during this research session confirms every piece of the pre-teardown gate is
currently green: `https://typsphinx.readthedocs.io/en/latest/` → 200, `/ja/latest/user_guide/builders.html`
→ 200 and contains the Japanese string `ビルダー` (title `ビルダー - typsphinx 0.6.3`), the English PDF
download URL → 200 with `content-type: application/pdf`, the documentation root → 200, and the legacy
`https://YuSabo90002.github.io/typsphinx/` still → 200 (Pages has not been torn down yet, as expected).
`origin/gh-pages` still exists at `f97862dfea151dd904591a18d2ddbd0bf72fd851` per `git ls-remote`. The
milestone draft PR #124 (D-08/D-09) is already open, targets `main`, and its most recent `build-docs`
run (30269906943, head `980f6ca9`) is green — this is the pre-teardown baseline; Plan 2 must push a new
commit to this same PR and observe a **fresh** green run against the post-teardown tree to satisfy SC#3,
since the existing green run predates the teardown diff.

`docs.yml`'s current shape (7 steps) is fully read and quoted below. The guard-test file named in D-06
(`tests/test_readthedocs_config.py`) exists, uses a `_load_readthedocs_yaml()`-style helper plus a
compiled regex over the raw workflow text — the same idiom the new guard test should follow, reading
`docs.yml` as raw text (not YAML-parsed) because `permissions:` keys and step `uses:` values are simplest
to assert against as substrings/regex, matching the file's existing `_extract_docs_workflow_python_version()`
pattern. `release.yml` independently declares its own `id-token: write` for PyPI trusted publishing —
confirmed textually distinct from `docs.yml`'s `id-token: write`, so removing the latter cannot affect
the former.

**Primary recommendation:** Follow CONTEXT.md's decisions verbatim (they are already fully specified);
this research's value-add is the exact current-state snapshot (docs.yml text, live URL evidence, branch
SHA, guard-test pattern, draft-PR state) so the planner does not need to re-derive it.

## Architectural Responsibility Map

This phase has no application-tier work; the "architecture" here is CI/CD pipeline + remote git state +
external hosting platform. Mapped onto the closest equivalent tiers for planner sanity-checking:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Pre-teardown live evidence gate (SC#1) | External Hosting Platform (Read the Docs, live HTTP) | — | Evidence must be freshly fetched from the actually-serving platform, never derived from repo state or prior phases' records |
| `docs.yml` deploy-step + permissions removal (SC#2) | CI/CD Pipeline (GitHub Actions workflow file) | — | Pure YAML edit in-repo; no runtime code touched (milestone invariant #3) |
| `origin/gh-pages` branch deletion (SC#2) | Remote Git State (GitHub ref, not local working tree) | — | Must be proven via `git ls-remote` against `origin`, not a local `git branch` listing, per SC#2's explicit wording |
| GitHub Pages feature disable (owner-manual) | External Platform Settings (GitHub repo Settings UI) | — | No API/CLI surface reachable from this repo's automation; only the *effect* (github.io 404) is observable |
| Guard test for the removed deploy step (D-06) | CI/CD Pipeline (pytest over workflow YAML) | Test Infrastructure | Extends the existing `tests/test_readthedocs_config.py` pattern; hermetic, no network |
| Observed post-teardown CI run (SC#3) | CI/CD Pipeline (GitHub Actions, `pull_request` trigger on draft PR #124) | — | Must be a **new** run against the post-teardown commit, not the pre-teardown baseline run already observed |
| `Upload PDF to Release` byte-unchanged proof (SC#3) | CI/CD Pipeline (diff/git show) | — | Verified via `git diff`/`git show` on the milestone branch, not by executing a tag build (impossible pre-tag) |

## Standard Stack

No new libraries, packages, or dependencies are introduced or required by this phase. It is a deletion
of one third-party GitHub Action (`peaceiris/actions-gh-pages@v4`) and two `permissions:` entries from
an existing workflow file, plus a small pytest addition using already-present dependencies (`yaml`,
already a transitive dependency per `test_readthedocs_config.py`'s own docstring; `re`, stdlib).

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| (none — no new dependency) | — | — | This phase only removes a third-party Action and edits YAML/pytest already present in the repo |

### Package Legitimacy Audit

**Not applicable.** This phase installs no new packages in any ecosystem. It *removes* the third-party
GitHub Action `peaceiris/actions-gh-pages@v4`, which requires no legitimacy check (removal, not
addition). `pyyaml` (import name `yaml`) is already an established transitive dependency exercised by
the existing `tests/test_readthedocs_config.py` suite — no new install needed for the D-06 guard test.

**Packages removed due to [SLOP] verdict:** none — no packages were checked because none are being added.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
                     ┌─────────────────────────────────────────┐
                     │   Pre-teardown gate (Plan 1, SC#1)       │
                     │   curl -> typsphinx.readthedocs.io       │
                     │     /en/latest/          -> 200          │
                     │     /ja/latest/.../builders.html          │
                     │        -> 200 + grep known ja string      │
                     │     /_/downloads/en/latest/pdf/ -> 200    │
                     │        + PDF magic bytes                  │
                     │     /_/downloads/ja/.../pdf/... -> 200    │
                     │     root https://typsphinx.readthedocs.io/│
                     │        -> 200                             │
                     └───────────────┬───────────────────────────┘
                                      │ gate green -> unlock Plan 2
                                      ▼
                     ┌─────────────────────────────────────────┐
                     │   Teardown (Plan 2, SC#2 + SC#3)         │
                     │                                            │
                     │  1. Re-confirm 4 URLs (status only, D-04) │
                     │  2. Edit .github/workflows/docs.yml:      │
                     │     - remove "Deploy to GitHub Pages" step│
                     │     - remove permissions.pages: write     │
                     │     - remove permissions.id-token: write  │
                     │     - keep permissions.contents: write    │
                     │     - keep "Upload PDF to Release" step   │
                     │       byte-unchanged                      │
                     │  3. Add guard test in                     │
                     │     tests/test_readthedocs_config.py      │
                     │     (D-06)                                │
                     │  4. git push origin --delete gh-pages     │
                     │     (or gh api -X DELETE                  │
                     │      git/refs/heads/gh-pages)              │
                     │  5. git ls-remote origin -> confirm        │
                     │     gh-pages absent                        │
                     │  6. Push commit(s) to existing draft PR    │
                     │     #124 (D-08) -> observe fresh green     │
                     │     build-docs run on the post-teardown    │
                     │     head (SC#3)                            │
                     │  7. Owner-manual: Settings -> Pages         │
                     │     disable (out of repo automation)        │
                     │  8. Poll https://<user>.github.io/typsphinx/│
                     │     -> expect 404 (D-03/CDN-lag retry,      │
                     │      Claude's discretion)                   │
                     └─────────────────────────────────────────┘
```

### Recommended Plan Structure (per D-03)

```
32-github-pages-teardown-irreversible/
├── Plan 1: Pre-teardown evidence gate
│   └── zero repo changes; produces a verbatim command+output evidence log
│       (Phase 29 D-15 format) as the plan's SUMMARY/evidence artifact
└── Plan 2: Teardown (depends on Plan 1 green)
    ├── docs.yml edit (deploy step + 2 permissions removed)
    ├── D-06 guard test added
    ├── remote gh-pages branch deletion
    ├── git ls-remote proof
    ├── push to draft PR #124, observe fresh green run
    └── INTEGRATIONS.md diff update (D-07)
```

### Pattern 1: Workflow-shape guard test via raw-text regex (D-06)

**What:** `tests/test_readthedocs_config.py` already asserts facts about `docs.yml` without a full YAML
parse of that file — it reads `docs.yml`'s raw text with `Path.read_text()` and a compiled regex
(`_PYTHON_VERSION_RE`), rather than `yaml.safe_load`. `.readthedocs.yaml` (a different file) *is*
YAML-parsed via `_load_readthedocs_yaml()`. Follow the same split for the new guard test: assert over
`docs.yml`'s raw text for step/permission absence-or-presence, since GitHub Actions YAML has
duplicate/ordering-sensitive semantics (`permissions:` keys, `uses:` step identity) that are simplest
to assert as substring/regex checks rather than reconstructing full step-object equality.

**When to use:** Any new guard test targeting `docs.yml`'s shape.

**Example:**
```python
# Source: tests/test_readthedocs_config.py (existing pattern, lines 52-65, 122-141)
DOCS_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "docs.yml"

def test_docs_workflow_has_no_github_pages_deploy():
    """CI-04 guard: docs.yml must never regain a GitHub Pages deploy step."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "peaceiris/actions-gh-pages" not in text, (
        "docs.yml must not contain a GitHub Pages deploy step -- "
        "CI-04 tore this down permanently"
    )
    assert "pages: write" not in text, (
        "docs.yml's permissions block must not request pages: write -- "
        "unused once the peaceiris deploy step is removed"
    )
    # id-token: write also appears in release.yml for a different purpose
    # (PyPI trusted publishing) -- scope this assertion to docs.yml's own
    # permissions block only, not a repo-wide grep.


def test_docs_workflow_still_uploads_pdf_to_release():
    """CI-04 guard: the tag-time Release attachment step must survive."""
    text = DOCS_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "softprops/action-gh-release" in text
    assert "Upload PDF to Release" in text
```

### Pattern 2: Verbatim command + output evidence log (Phase 29 D-15 format)

**What:** The pre-teardown gate (SC#1) and the SC#3 CI-run observation are not encoded as pytest — they
are point-in-time HTTP/CI observations. The established project convention (Phase 29 D-15, reused by
Phase 30.1 D-03 and Phase 31 D-09) is to record the **exact command run** and its **exact output**
inline in the plan's evidence artifact, not a paraphrase or a "checked, looks good."

**When to use:** SC#1's four URL checks, SC#2's `git ls-remote` proof, SC#3's CI-run citation.

**Example (already exercised live in this research session — reusable verbatim for Plan 1):**
```bash
$ curl -s -o /dev/null -w "en html: %{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/
en html: 200

$ curl -s -L https://typsphinx.readthedocs.io/ja/latest/user_guide/builders.html | grep -o 'ビルダー' | head -1
ビルダー

$ curl -s -o /dev/null -w "en pdf: %{http_code} %{content_type}\n" -L \
    https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/
en pdf: 200 application/pdf

$ git ls-remote origin | grep -i pages
f97862dfea151dd904591a18d2ddbd0bf72fd851	refs/heads/gh-pages
```

### Pattern 3: Remote branch deletion + proof (SC#2)

**What:** `origin/gh-pages` must be deleted at the remote (not just untracked locally), and the *proof*
must be `git ls-remote`, not a local branch listing (SC#2's explicit wording — a local `git branch -a`
can go stale relative to the remote).

**Example:**
```bash
# Delete the remote branch (either form works; gh CLI form shown as an
# alternative since it doesn't require the local repo to have gh-pages checked out)
git push origin --delete gh-pages
# or:
gh api -X DELETE repos/YuSabo90002/typsphinx/git/refs/heads/gh-pages

# Proof required by SC#2: git ls-remote, not `git branch -a`
git ls-remote origin | grep -i pages
# (expect: no output)
```

**Current auth confirmed sufficient:** `gh auth status` shows the active token has `repo` scope, which
covers ref deletion via either the `git push --delete` (HTTPS credential helper) or `gh api -X DELETE`
path — no additional owner action needed to execute the deletion itself (only the Settings → Pages
toggle is owner-manual).

### Anti-Patterns to Avoid

- **Editing `permissions:` with a full YAML round-trip (parse + dump).** `docs.yml` is a hand-authored,
  hand-commented workflow file; a `yaml.safe_load` → mutate → `yaml.dump` round-trip will reformat
  comments/quoting/ordering and produce a noisy diff unrelated to CI-04's actual change. Edit the two
  `permissions:` lines and the deploy step as a targeted text edit instead (this is exactly what the
  `Edit` tool's old_string/new_string mechanism is for).
- **Removing `id-token: write` from `docs.yml` under the assumption it's shared with `release.yml`.**
  Confirmed by grep: `release.yml` declares its own separate `id-token: write` for PyPI trusted
  publishing (line 15, commented `# Required for PyPI trusted publishing`). These are two different
  workflow files' independent `permissions:` blocks — GitHub Actions permissions are scoped per
  workflow file, not shared. Removing `docs.yml`'s copy cannot affect `release.yml`.
- **Treating the existing green `build-docs` run on PR #124 (run 30269906943, head `980f6ca9`) as
  satisfying SC#3.** That run predates this phase's diff — it proves Phase 30's post-deletion tree was
  green, not that the *post-CI-04-teardown* tree is green. SC#3 requires a **new** push to the same PR
  and a **new** observed run against the teardown commit.
- **Citing Phase 29/30.1's PDF-fidelity verification as satisfying D-02's PDF check.** D-02 is explicit
  that content/glyph fidelity is *not* re-verified here — only "is it still being served" (HTTP 200 +
  magic bytes + plausible size). Re-doing full fidelity checks would be scope creep beyond the locked
  decision.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Proving a PDF response is really a PDF | Custom byte-signature parsing | `curl ... \| head -c4` and check for the `%PDF` magic bytes (already the established RTD-evidence idiom in Phases 29/30.1) | Four bytes is sufficient and matches the project's existing verification depth; a full PDF parser is unwarranted for a liveness check |
| Verifying `docs.yml`'s "Upload PDF to Release" step is untouched | Manual line-by-line human comparison | `git diff <base>..HEAD -- .github/workflows/docs.yml` scoped to the step's line range, or a byte-equality check via `git show <base>:.github/workflows/docs.yml \| sed -n '<range>'` vs the current file | `git diff` is the direct tool for "byte-unchanged in the milestone diff" — SC#3's own wording |
| Confirming remote branch deletion | Trusting `git branch -a` (reads local remote-tracking refs, can be stale) | `git ls-remote origin` (live query against GitHub) | SC#2 explicitly requires the `git ls-remote` proof, not a local listing — this is also just objectively the correct check for remote state |

**Key insight:** Every verification instrument this phase needs (curl, git ls-remote, git diff, gh api)
is already a standard CLI tool available in the environment — there is no library gap here, only
sequencing and evidence-recording discipline (which CONTEXT.md's D-01–D-09 already fully specify).

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, no user records, no CMS content this phase touches | None |
| Live service config | **GitHub Pages feature setting** in the repository's Settings → Pages UI, not represented in git. Deleting `gh-pages` (the source) does not itself disable the *feature* — RTD's/GitHub's own docs confirm Pages can remain "enabled" pointing at a now-missing branch until explicitly turned off in Settings. This is the owner-manual step; the observable proxy (not a substitute) is the github.io URL returning 404 | Owner-manual: Settings → Pages → disable. Repo automation can only observe the resulting 404, never perform the toggle |
| OS-registered state | None found — no Task Scheduler/pm2/launchd/systemd entries reference `gh-pages` or `github.io` | None — verified by repo-wide grep (see Specific Ideas confirmation below); no OS-level registration mechanism is in play for a GitHub Actions-only CI/CD setup |
| Secrets/env vars | None removed. `secrets.GITHUB_TOKEN` (used by the peaceiris step) is GitHub's own auto-issued per-run token, not a repo-configured secret — its consumer (the deploy step) is deleted, but no secret name/rotation is affected. `CODECOV_TOKEN`, `PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN` are unrelated and untouched | None |
| Build artifacts | The `documentation-html` / `documentation-pdf` upload-artifact steps are explicitly kept per D-07 (they feed CI artifact downloads, unrelated to the Pages publish path); no stale build artifact needs regeneration | None — D-07 already covers this explicitly |

**Nothing found in category:** "Stored data" and "OS-registered state" — confirmed via repo-wide grep
(`grep -rn "peaceiris|gh-pages|github.io|pages: write|id-token: write"` across `*.yml`/`*.yaml`/`*.md`/
`*.py`/`*.toml`, excluding `.planning/`) returning only: `CHANGELOG.md:393` (historical, explicitly
out-of-scope per CONTEXT.md), `docs.yml`'s own three lines (the subject of this phase's edit), and
`release.yml`'s unrelated `id-token: write`. No other file in the tree references Pages/gh-pages state.

## Common Pitfalls

### Pitfall 1: gh-pages branch revival between this phase and merge

**What goes wrong:** `main`'s `docs.yml` still has the `peaceiris` deploy step until the milestone PR
merges. If any push lands on `main` before the milestone merge (e.g. dependabot PR #123, currently open,
auto-merging), `main`'s unmodified `docs.yml` runs and peaceiris recreates `gh-pages` — silently
invalidating this phase's `git ls-remote` proof after the fact.

**Why it happens:** `docs.yml`'s Pages deploy step only exists in the *removal commit itself* — until
that commit reaches `main`, `main`'s copy of the workflow is unmodified and will fire on any `main` push.

**How to avoid:** CONTEXT.md records this as an explicitly-deferred hazard (planner/owner judgment, not
resolved by a locked decision) — the plan should at minimum record a recommendation to re-run
`git ls-remote` at `/gsd-complete-milestone` time, and flag (not necessarily block on) the open
dependabot PR #123 as a live instance of this exact hazard.

**Warning signs:** `git ls-remote origin | grep -i pages` returning a *new* SHA (different from
`f97862dfea151dd904591a18d2ddbd0bf72fd851`) after this phase's deletion but before the milestone merges.

### Pitfall 2: CDN/edge cache lag on the 404 check

**What goes wrong:** Disabling GitHub Pages in Settings may not be instantaneous at GitHub's edge —
`github.io` can continue serving a cached 200 for some window after the feature is disabled, making an
immediate check look like teardown failed.

**Why it happens:** GitHub Pages is served through a CDN layer; propagation of a "site disabled" state is
not guaranteed synchronous with the Settings UI action.

**How to avoid:** Retry the 404 check with a short backoff rather than treating a single immediate 200 as
failure. CONTEXT.md explicitly leaves this retry posture to Claude's discretion — a small number of
retries (e.g. 3 attempts, few-minute spacing) is a reasonable default; do not loop indefinitely.

**Warning signs:** A 200 or 301/302 (rather than 404) immediately after the owner reports disabling
Pages — re-check after a short wait before escalating.

### Pitfall 3: Confusing "step removed" with "step never ran historically"

**What goes wrong:** Assuming `git diff` will show the "Upload PDF to Release" step as unchanged just
because it wasn't *intentionally* edited — an accidental reflow (e.g. an editor auto-reindenting the
YAML file, or a merge conflict resolution touching adjacent lines) could silently alter that step while
only the deploy step and permissions were meant to change.

**Why it happens:** The deploy step, the two permissions lines, and the Release step all live in the same
59-line file; a careless multi-line edit tool invocation can touch more than intended.

**How to avoid:** After editing, run `git diff -- .github/workflows/docs.yml` and manually confirm the
diff hunk touches *only* the `permissions:` block and the "Deploy to GitHub Pages" step — the
"Upload PDF to Release" step (lines 60-66 in the current file) should not appear in the diff at all.

**Warning signs:** A diff hunk that includes any line from `- name: Upload PDF to Release` onward.

### Pitfall 4: Treating a pre-teardown-tree CI run as satisfying SC#3

**What goes wrong:** The milestone draft PR #124 already has a green `build-docs` run (30269906943,
head `980f6ca9`) from Phase 30's landing. It is tempting to cite this as SC#3's "observed CI run on the
post-teardown tree" — but that run's head commit predates this phase's `docs.yml` edit entirely.

**Why it happens:** The draft PR being pre-opened (D-08/D-09) means a green run already exists in the PR
history by the time this phase starts, and it is easy to conflate "a green run exists on this PR" with
"a green run exists for this phase's commit."

**How to avoid:** After pushing this phase's teardown commit(s) to the existing draft-PR branch, wait for
and cite the **new** run's ID/URL/head SHA — verify the head SHA in the cited run matches the actual
teardown commit, not the pre-existing baseline commit.

**Warning signs:** The cited run's head SHA equals `980f6ca9` (the pre-teardown baseline) rather than a
new SHA introduced by this phase's commits.

## Code Examples

### Current `docs.yml` (baseline this phase edits — full text, verified 2026-07-27)

```yaml
# Source: .github/workflows/docs.yml (this repo, current HEAD)
name: Documentation

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs --locked
          uv pip install -e .

      - name: Build HTML documentation
        run: uv run tox -e docs-html

      - name: Build PDF documentation (English only)
        run: uv run tox -e docs-pdf

      - name: Upload HTML artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-html
          path: docs/_build/html

      - name: Upload PDF artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-pdf
          path: docs/_build/pdf/*.pdf

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
          cname: false

      - name: Upload PDF to Release
        if: startsWith(github.ref, 'refs/tags/v')
        uses: softprops/action-gh-release@v3
        with:
          files: docs/_build/pdf/*.pdf
          draft: false
          prerelease: false
```

### Target shape after this phase's edit (delta only)

```diff
 permissions:
   contents: write
-  pages: write
-  id-token: write
```
```diff
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

Everything else in the file (checkout, Python setup, uv install, `docs-html`/`docs-pdf` tox builds, both
artifact uploads, the Release step) stays byte-unchanged.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| GitHub Pages via `peaceiris/actions-gh-pages` deploy step | Read the Docs, self-building from `.readthedocs.yaml` | Phases 29-31 of this milestone (2026-07-25 onward) | This phase (32) removes the now-redundant publish path; RTD has been the actual served source of truth since Phase 31's URL cutover |

**Deprecated/outdated:**
- `peaceiris/actions-gh-pages@v4` step in `docs.yml`: superseded by RTD's own git-integration build,
  which needs no push-based deploy step at all — RTD polls/webhooks the repo directly.
- `pages: write` / `id-token: write` permissions in `docs.yml`: were unused even before this phase
  (confirmed — `peaceiris` authenticates via `secrets.GITHUB_TOKEN` and a `contents: write` branch push,
  not via the OIDC/Pages-API path those two permissions exist for; they were dead weight for the
  official `actions/deploy-pages` action pattern that was never adopted here).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The GitHub Pages "feature enabled but source missing" behavior (branch deletion alone doesn't disable Pages) is standard GitHub product behavior | Runtime State Inventory | Low — this is asserted directly by both ROADMAP.md and CONTEXT.md as the reason the owner-manual step exists; not independently re-verified against GitHub's current docs in this session, but it is a pre-existing project decision, not new research output |
| A2 | 404 propagation after Pages is disabled may lag due to CDN caching | Common Pitfalls, Pitfall 2 | Low — general web-infra knowledge; if wrong (propagation is instant), the retry logic is merely unnecessary, not harmful |

**All other claims in this research were verified via direct tool use in this session** (live `curl`
against RTD and github.io, `git ls-remote`, `gh pr list`/`gh pr checks`, `gh auth status`, repo-wide
`grep`, and direct file reads of `docs.yml` / `tests/test_readthedocs_config.py` / `INTEGRATIONS.md`) or
are copied verbatim from the already-locked `32-CONTEXT.md`.

## Open Questions

1. **Exact form of the guard test's assertions (function names, strictness) for D-06**
   - What we know: the pattern to follow (`tests/test_readthedocs_config.py`'s raw-text-regex idiom) and
     the two facts it must assert (no peaceiris/pages-permissions; Release step present).
   - What's unclear: exact function naming and whether to also assert `contents: write` is retained (a
     stronger, arguably more useful guard than the two facts CONTEXT.md names).
   - Recommendation: CONTEXT.md marks this as Claude's Discretion — the planner should propose specific
     test function signatures; suggest also asserting `contents: write` survives, since that's the one
     permission this phase must *not* remove and a regression there would silently break the Release
     step.

2. **How the plan should record/mitigate the gh-pages-revival hazard (Pitfall 1)**
   - What we know: CONTEXT.md explicitly defers this to "planner/owner judgment" and recommends at least
     a `git ls-remote` re-check at `/gsd-complete-milestone`.
   - What's unclear: whether Plan 2 should also proactively flag/comment on dependabot PR #123, or simply
     rely on the milestone-close re-check.
   - Recommendation: keep it lightweight — record the recommendation in the plan's Handoffs section for
     `/gsd-complete-milestone`, per CONTEXT.md's own suggested minimum; do not block this phase on
     dependabot PR #123's disposition (it is out of this phase's control and CONTEXT.md explicitly
     skipped discussing a permanent fix).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `curl` | SC#1 gate evidence, D-04 re-confirmation | ✓ | (system) | — |
| `git` (with `origin` push access) | SC#2 branch deletion + `git ls-remote` proof | ✓ | (system); `origin` is `https://github.com/YuSabo90002/typsphinx.git` | — |
| `gh` CLI, authenticated | Alternative branch-deletion path (`gh api -X DELETE`), PR/CI observation | ✓ | logged in as `YuSabo90002`, token scopes include `repo` | `git push origin --delete gh-pages` works without `gh` if preferred |
| Open draft PR targeting `main` | SC#3 observed CI run vehicle (D-08) | ✓ | PR #124, currently DRAFT, head `980f6ca9` as of this research session | — |
| RTD live site (`typsphinx.readthedocs.io`) | SC#1 gate | ✓ | Confirmed serving en HTML, ja HTML, en PDF, root — all 200 as of 2026-07-27 | — (this dependency IS the gate; a red result here structurally blocks Plan 2 per D-03) |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** none — everything needed is present.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), run via `uv run pytest` per CLAUDE.md's worktree-isolation mandate |
| Config file | `pyproject.toml` (existing); no new config needed |
| Quick run command | `uv run pytest tests/test_readthedocs_config.py -x` |
| Full suite command | `uv run pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CI-04 (SC#1) | RTD currently serves en HTML, ja HTML (content-verified), PDF (en+ja), root URL | manual/scripted evidence log (not pytest — live external HTTP state, per Phase 29 D-15 precedent) | `curl` commands, verbatim-recorded (see Code Examples/Pattern 2) | N/A — not a repo test file, an evidence artifact in the plan |
| CI-04 (SC#2, docs.yml shape) | `docs.yml` contains no `peaceiris`/Pages permissions | unit | `uv run pytest tests/test_readthedocs_config.py::test_docs_workflow_has_no_github_pages_deploy -x` | ❌ Wave 0 — new test to add per D-06 |
| CI-04 (SC#2, Release step present) | `docs.yml` still has the `Upload PDF to Release` step | unit | `uv run pytest tests/test_readthedocs_config.py::test_docs_workflow_still_uploads_pdf_to_release -x` | ❌ Wave 0 — new test to add per D-06 |
| CI-04 (SC#2, branch gone) | `origin/gh-pages` no longer exists | scripted evidence (not pytest — remote git state, not testable hermetically) | `git ls-remote origin \| grep -i pages` (expect empty) | N/A — evidence artifact, not a repo test |
| CI-04 (SC#2, 404) | `github.io` URL returns 404, no redirect | scripted evidence (not pytest — live external HTTP, and depends on an owner-manual action) | `curl -s -o /dev/null -w "%{http_code}" -L https://YuSabo90002.github.io/typsphinx/` (expect 404) | N/A — evidence artifact; blocked on owner-manual Settings step |
| CI-04 (SC#3, CI green) | Post-teardown `build-docs` run on PR #124 stays green | manual/scripted evidence (GitHub Actions run citation, not a local pytest run) | `gh pr checks 124` after pushing the teardown commit; cite the new run URL + head SHA | N/A — CI observation, not a repo test |
| CI-04 (SC#3, byte-unchanged Release step) | `Upload PDF to Release` step unchanged in the milestone diff | scripted evidence | `git diff <milestone-base>..HEAD -- .github/workflows/docs.yml` (confirm no hunk touches that step) | N/A — diff evidence, not a repo test |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_readthedocs_config.py -x` (fast, hermetic, no network)
- **Per wave merge:** `uv run pytest` (full suite — this phase touches a shared CI-config test file, so
  confirm nothing else regresses)
- **Phase gate:** Full suite green before `/gsd-verify-work`, plus all the non-pytest evidence artifacts
  (SC#1 gate log, SC#2 ls-remote + 404 proof, SC#3 CI-run citation + diff proof) recorded per the
  verbatim-command-and-output convention.

### Wave 0 Gaps
- [ ] `tests/test_readthedocs_config.py` — add the two D-06 guard-test functions (no new file needed;
  extends the existing module).
- [ ] No new fixtures or framework install needed — `pyyaml`/`re`/`pathlib` already exercised by this
  file.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No authentication surface touched — this phase edits CI workflow permissions, not app auth |
| V3 Session Management | no | N/A |
| V4 Access Control | yes | GitHub Actions `permissions:` block — principle of least privilege. Removing unused `pages: write` / `id-token: write` from `docs.yml` while retaining `contents: write` (needed for the Release attachment) is itself a least-privilege improvement over the current state, not merely a cleanup |
| V5 Input Validation | no | No user input processed by this phase's changes |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack (GitHub Actions CI/CD)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Over-broad workflow `permissions:` (a compromised/malicious dependency step could abuse `pages: write`/`id-token: write` even though the legitimate step doesn't need them once peaceiris is removed) | Elevation of Privilege | This phase's own change: drop the two now-unused permissions, keeping only `contents: write` scoped to what the Release step actually needs |
| Third-party Action supply-chain risk (`peaceiris/actions-gh-pages@v4` runs with repo write access) | Tampering | Removing the Action entirely (this phase's SC#2) eliminates that specific third-party trust surface from `docs.yml`; `softprops/action-gh-release@v3` (retained) is a separate, narrower-scoped dependency already accepted by the project |
| Stale/orphaned publish surface left reachable after a migration (a forgotten `gh-pages` branch/Pages site continuing to serve outdated or unmaintained content indefinitely) | Information Disclosure / Tampering | This phase's entire purpose — SC#1 gates on RTD being the live source of truth first, then SC#2 removes both the deploy mechanism and the branch, and the owner-manual step disables the hosting feature itself |
| Branch-recreation race (a workflow on `main` recreating `gh-pages` after this phase's deletion, before the milestone merges — see Common Pitfalls Pitfall 1) | Tampering (of the verified "gone" state) | No locked mitigation (CONTEXT.md defers this); recommended minimum is a `git ls-remote` re-check at `/gsd-complete-milestone`, which the planner should carry forward as a Handoff |

## Sources

### Primary (HIGH confidence)
- Live `curl` fetches against `typsphinx.readthedocs.io` (en HTML, ja HTML with content-string grep, en
  PDF headers, root) and `YuSabo90002.github.io/typsphinx` — run directly in this research session,
  2026-07-27.
- `git ls-remote origin` — run directly, confirms `origin/gh-pages` at `f97862dfea151dd904591a18d2ddbd0bf72fd851`.
- `gh pr list` / `gh pr checks 124` / `gh pr view 124` / `gh auth status` — run directly, confirms draft
  PR #124's state, its green `build-docs` run, and available auth scope for branch deletion.
- Direct file reads: `.github/workflows/docs.yml`, `tests/test_readthedocs_config.py`,
  `.github/workflows/release.yml` (grep only), `CHANGELOG.md:393` (grep only), `.planning/config.json`.
- `.planning/phases/32-github-pages-teardown-irreversible/32-CONTEXT.md` — locked decisions D-01 through
  D-09, canonical refs, specifics.
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/ROADMAP.md` (Phase 32 section) — project
  requirements, history, and roadmap text, read directly.

### Secondary (MEDIUM confidence)
- `.planning/codebase/INTEGRATIONS.md` — read directly; describes current docs.yml/RTD integration shape
  and explicitly notes Phase 32 as the pending removal work, consistent with live verification above.

### Tertiary (LOW confidence)
- GitHub Pages' "feature stays enabled with a missing source until disabled in Settings" behavior (A1 in
  Assumptions Log) — not independently re-verified against current GitHub product docs in this session;
  carried forward from the project's own prior research/decisions (ROADMAP.md, CONTEXT.md) rather than
  freshly checked here, since it describes an owner-manual step outside this repo's automation surface.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; verified no-op by direct grep and read
- Architecture: HIGH — every artifact (docs.yml, test file, branch state, PR state, live URLs) directly
  read/fetched in this session, not inferred
- Pitfalls: HIGH for Pitfalls 1, 3, 4 (directly observed conditions: open dependabot PR #123, exact file
  line structure, exact PR/run state); MEDIUM for Pitfall 2 (CDN-lag behavior is general web-infra
  knowledge, not verified against this specific GitHub Pages instance since Pages hasn't been disabled
  yet)

**Research date:** 2026-07-27
**Valid until:** Time-sensitive on two fronts — (1) the live RTD/github.io evidence is a same-day snapshot
per D-04 and must be re-taken at execution time regardless of this document's age; (2) `docs.yml`'s exact
line numbers/text and PR #124's head SHA will drift the moment any other commit lands — re-read the live
file and re-run `gh pr view 124` at planning/execution time rather than trusting this document's quoted
line numbers verbatim.
