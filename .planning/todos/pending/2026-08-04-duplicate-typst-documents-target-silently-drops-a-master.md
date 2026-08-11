---
created: 2026-08-04T17:30:00+09:00
title: 同一ターゲット名を持つ typst_documents 2エントリが、片方のマスターを無言で消す
area: builder, tests
resolves_phase: TBD
source: .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-REVIEW.md (CR-02)
severity: high
files:
  - typsphinx/builder.py (`_resolve_output_stem` — 44-05 が入れた found_docs 衝突ガードの直後)
  - tests/ (新規ゲート: master-vs-master ターゲット衝突)
---

# 症状

`typst_documents` の2エントリが**互いに**同じターゲット名を指すと、片方のマスターの
出力が無言で失われる。`-b typst` は exit 0、衝突 WARNING なし。

Phase 44 の code review (CR-02) が発見し、オーケストレーターが現ツリーで独立再現した:

```python
# conf.py
typst_documents = [
    ("index", "manual.typ", project, author),
    ("other", "manual.typ", project, author),
]
```

`index.rst` / `other.rst` の両方が実在する状態で `uv run python -m sphinx -b typst`:

```
exit=0
出力: _template.typ, manual.typ のみ
grep -c INDEX-MASTER-MARKER-AAA manual.typ  → 0   ← index マスターの本文が消滅
grep -c OTHER-MASTER-MARKER-BBB manual.typ  → 1
衝突 WARNING: なし（出たのは無関係な toc.not_included のみ）
```

`-b typstpdf` ではさらに、生き残った1ファイルに対して "Generated PDF" が2回ログされる。

# なぜ既存ガードで防げないか

44-05 が `_resolve_output_stem` に入れた CR-01 衝突ガードは、解決後の実効パスを
`self.env.found_docs`（実在 docname の集合）と予約名 `_template` にのみ照合する。
master-vs-master 衝突では**どちらのターゲットも docname ではない**ため、
メンバシップ検査が原理的に発火しない。CR-01 と同じ「無言のドキュメント消失」クラスだが
機構が異なる。

# 経緯・スコープ判断

- Phase 44 が作り込んだ退行では**ない**。派生デフォルト以前から存在し、明示的に重複させた
  `typst_documents` を要する（Quick Start 経路からは到達しない）。
- 44-05 のプランは把握した上で範囲外にした（`<planning_measurements>` 項目8、
  `44-GATE-EVIDENCE-05.md` § 7 に繰り越し観察として明記）。
- 44-VERIFICATION.md（status: passed, 6/6）も CR-02 を Phase 44 のスコープ外と判定し、
  後続フェーズかバックログへのルーティングを推奨している。

# 修正の方向（未確定）

`_resolve_output_stem` の内部だけでは解けない可能性がある — 単一エントリを解決する時点では
「他のエントリが同じターゲットを取ったか」を知らないため。`write()` / `finish()` 側で
解決済みターゲットの集合を一度作って重複を検出するか、`_resolve_output_stem` に
解決済みターゲットのレジストリを渡すかの設計判断が要る。

CR-01 の fallback 規約（合成名を作らず docname にフォールバック + WARNING）を踏襲すること。
`must_haves.prohibitions` の「ユーザーが書いていないファイル名を発明しない」は CR-02 の
修正にもそのまま効く。

関連: [[.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-REVIEW.md]] CR-02, WR-02

## Re-measurement (2026-08-11, Phase 46 plan 46-06 Task 3)

**Still reachable — Phase 44 plan 44-05's collision guard does not close this.** Re-derived from
`44-05-SUMMARY.md`'s own scope statement: "Added a collision guard to
`TypstBuilder._resolve_output_stem` ... a resolved target whose directory-qualified effective path
equals a real docname in `self.env.found_docs`, or the reserved `_template` basename, now emits a
`logger.warning` and falls back to the docname itself." Confirmed by reading the current
`typsphinx/builder.py:189-196`: the comparison set is exactly `self.env.found_docs ∪ {"_template"}`
— never a registry of already-resolved `typst_documents` targets from *other* entries in the same
build, which is what this record's own two-entry `manual.typ`/`manual.typ` collision needs.

Reproduced live in this plan's own worktree (`uv run python -m sphinx -b typst`, a two-master
fixture identical in shape to this record's own repro): exit 0, no collision warning (the only
warning emitted is the unrelated `toc.not_included`), `_build/manual.typ` written once, and
`grep -c INDEX-MASTER-MARKER-AAA` on it returns `0` while `grep -c OTHER-MASTER-MARKER-BBB` returns
`1` — the first master's body is silently dropped, exactly as this record describes. Left pending;
named in `46-HANDOFF.md` § "Deferred by decision, not oversight".
