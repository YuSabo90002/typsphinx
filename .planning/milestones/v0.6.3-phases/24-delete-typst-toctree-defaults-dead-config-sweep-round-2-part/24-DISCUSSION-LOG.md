# Phase 24: Delete `typst_toctree_defaults` (dead-config sweep round 2, part B) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-23
**Phase:** 24-delete-typst-toctree-defaults-dead-config-sweep-round-2-part-b
**Areas discussed:** CHANGELOG handling, orphan docs handling

---

## CHANGELOG handling

| Option | Description | Selected |
|--------|-------------|----------|
| 履歴残す + P28 一任 | `CHANGELOG.md:553` の履歴行は不変履歴として残す（v0.6.2 CONF-01 で `typst_output_dir` 削除時も履歴行を残した前例、SC#1 の列挙面に CHANGELOG は含まれない）。Unreleased の `### Removed` 削除メモは Phase 28 release-prep に一任。 | ✓ |
| 履歴行も今消す | SC#1 の「whole repo grep-zero」を字面通り取り、line 553 の履歴行も削除しリポ全体 grep 0 ヒットにする（不変履歴を変更する形）。 | |
| 今 Unreleased にメモ | 履歴行は残すが、Unreleased の `### Removed` に今フェーズで削除メモを追加する（Phase 28 ではなく）。 | |

**User's choice:** 履歴残す + P28 一任（推奨）
**Notes:** Phase 24 は `CHANGELOG.md` を一切触らない。削除後も `CHANGELOG.md:553` は grep にマッチし続けるが意図通り。grep-zero バーは SC#1 の列挙サーフェスに適用され、リポ全体の履歴には適用しない。

---

## orphan docs handling

| Option | Description | Selected |
|--------|-------------|----------|
| 外科的削除 | `docs/configuration.rst` から `typst_toctree_defaults` の3節だけ削り、ファイル自体は残す。orphan 全体の削除は Phase 27 / DOC-06 の scope。 | ✓ |
| orphan ごと今削除 | orphan ファイル `docs/configuration.rst` を Phase 24 で丸ごと削除（Phase 27 の DOC-06 を前倒し）。 | |

**User's choice:** 外科的削除（推奨）
**Notes:** Phase 24 は先に走り grep-zero が要るため、Phase 27 が丸ごと削除予定でも今フェーズで該当節だけ外科的に除去する。Phase 27 の scope は侵さない。

---

## Claude's Discretion

- `docs/configuration.rst` と `examples/advanced/` の周辺空白・見出しをどこまでトリムして自然に読ませるかの line-editing 詳細。

## Deferred Ideas

- orphan `docs/configuration.rst` のファイルごと削除 → Phase 27 / DOC-06。
- CHANGELOG `[Unreleased] → ### Removed` の削除メモ追加 → Phase 28 release-prep（0.6.3 版バンプと同フェーズ）。
