---
quick_id: 260711-kr2
slug: mcp-json-main
description: プロジェクトトップレベルにいる .mcp.json は main ブランチに含まれないようにする
date: 2026-07-11
status: complete
commit: 50a2623
---

# Quick Task 260711-kr2 — 完了サマリ

## 実施内容

`.mcp.json`（GSD が書き込むマシン固有絶対パスを含む MCP サーバ設定）を git 追跡対象から
外し、`.gitignore` に登録した。

- `git rm --cached .mcp.json` — 追跡解除（ワーキングツリーのファイルは保持）。
- `.gitignore` の GSD セクションに `.mcp.json` を追記。
- アトミックコミット: `50a2623`（`release/v0.5.0` ブランチ上）。

## 検証結果

| チェック | 結果 |
|---|---|
| `git ls-files .mcp.json` が空 | ✅ 追跡されていない |
| `git check-ignore .mcp.json` | ✅ `.mcp.json` を返す |
| `.mcp.json` がディスク上に存在 | ✅ ローカルには残存 |

## 効果と残課題

- この `release/v0.5.0` が `main` へマージされた時点で、`.mcp.json` は main のツリーから
  外れる（`git rm --cached` の削除がマージで反映される）。以後 `.gitignore` により再追跡
  されない。
- **残課題（スコープ外）**: 過去履歴のブロブ（コミット `1dc3a77`、および `origin/main`）に
  `.mcp.json` は残る。ブランチの tip からは消えるが履歴からの完全消去は行っていない。
  完全に消すには `git filter-repo` 等での履歴書き換え + force push が必要で、共有履歴の
  書き換えとなりリスクが高いため別途明示依頼で対応する。
