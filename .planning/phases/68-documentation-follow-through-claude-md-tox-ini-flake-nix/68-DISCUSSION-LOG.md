# Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-12
**Phase:** 68-documentation-follow-through-claude-md-tox-ini-flake-nix
**Areas discussed:** SC#1 boundary, CLAUDE.md NixOS content, flake.nix note style, edit footprint

**Pre-discussion findings presented to the owner:** (1) SC#1's "unaffected and unassisted by
`flake.nix`" is contradicted by NIX-05's measurement; (2) `git log -S` finds no commit ever adding
`ln -sf`/`patchelf` to CLAUDE.md; (3) stale `tox-uv-bare` text survives in `CLAUDE.md:11/:77`,
`tox.ini:4-10`, two test files, and `flake.nix:93`.

---

## SC#1 boundary

| Option | Description | Selected |
|--------|-------------|----------|
| AMENDED で訂正 | AMENDED block on SC#1, original kept; CLAUDE.md states measured truth; verifier reports both readings | ✓ |
| 逃げ道条項で読む | Rely on SC#1's "if reachable, say so" clause; leave ROADMAP untouched | |

| Option | Description | Selected |
|--------|-------------|----------|
| 証拠記録＋否定の一文 | Record vacuous satisfaction; add one "no manual step; stub-ld means shim not on PATH" sentence | ✓ |
| 証拠記録だけ | Evidence only | |

| Option | Description | Selected |
|--------|-------------|----------|
| 前提＋command -v 確認 | State launch prerequisite; add shim check before the unchanged provisioning line | ✓ |
| 前提だけ書く | Prerequisite only | |

---

## CLAUDE.md NixOS content

| Option | Description | Selected |
|--------|-------------|----------|
| 新しい小節を Worktree 節の直前に | New subsection; worktree section keeps recipe plus boundary paragraph | ✓ |
| Worktree 節に統合 | One combined section | |

| Option | Description | Selected |
|--------|-------------|----------|
| 一文＋LC_ALL=C 事前確認 | Locale passes through (REPRODUCES); check warning-text tests under LC_ALL=C | ✓ |
| CLAUDE.md には書かない | flake.nix notes and evidence only | |

| Option | Description | Selected |
|--------|-------------|----------|
| 注意として一文書く | Compare pyvenv.cfg home/version_info before comparing counts | ✓ |
| 書かない | Leave in auto-memory | |

| Option | Description | Selected |
|--------|-------------|----------|
| 運用の事実だけ、理由は flake.nix へ | Operational facts in CLAUDE.md; rationale in flake.nix | ✓ |
| 理由も CLAUDE.md に書く | Full rationale in CLAUDE.md | |

---

## flake.nix note style

| Option | Description | Selected |
|--------|-------------|----------|
| 自己完結文＋末尾に出典パス | Self-contained prose; source paths at end of header block | ✓ |
| 自己完結文、引用は全削除 | No .planning references | |
| 現状の ID 引用スタイルを維持 | Keep D-NN citations | |

**Notes:** while writing CONTEXT, `.planning/phases/` paths were found to move at milestone
archival, so D-09 cites sources by milestone + phase + file name instead of a live path.

| Option | Description | Selected |
|--------|-------------|----------|
| 先頭概要＋各要素の横に短注 | Header overview plus per-element notes | ✓ |
| 全部各要素の横 | Inline only | |
| 全部先頭ブロック | Header only | |

| Option | Description | Selected |
|--------|-------------|----------|
| 必須内容＋「eval のみ確認済み」 | Mandatory content plus: only Linux-evaluator eval checked; darwin has plain uv; report via issue | ✓ |
| 必須内容だけ | Minimal SC#3 wording | |

| Option | Description | Selected |
|--------|-------------|----------|
| 役割で書き版番号は書かない | Legs by role; sole deliberate exception; no versions | ✓ |
| 計測時の版も併記 | Include 0.12.13 / 0.11.25 | |

---

## Edit footprint

| Option | Description | Selected |
|--------|-------------|----------|
| 文言だけ直す (config gate) | Rewrite the two "until Phase 68" strings; logic unchanged | ✓ |
| 触らない | Limit to the three named files | |

| Option | Description | Selected |
|--------|-------------|----------|
| 一文足して現状に合わせる (render gate) | Add sentence that `.venv/bin/uv` is back and runs via FHS | ✓ |
| 履歴記述として残す | Leave untouched | |

| Option | Description | Selected |
|--------|-------------|----------|
| .planning/ と uv.lock を除外し全行判定 | Classify every remaining hit; MET at zero "presented as current" | ✓ |
| .planning/ も含める | Include historical docs | |

| Option | Description | Selected |
|--------|-------------|----------|
| 経緯を1と2文で残す | Current pin + ~= constraint + brief tox-uv-bare history | ✓ |
| 現状のみ | No history | |

---

## Todos

5 keyword-matched todos reviewed (typing modernize, numref, root toctree, translator debug-log
delimiters, linkcheck CI job). Owner chose: fold none.

## Claude's Discretion

- CLAUDE.md wording, subsection name, sentence order; flake.nix note wording; whether the header
  lists the seven names; plan split and evidence file naming.

## Deferred Ideas

- Update of the maintainer's out-of-repo auto-memory `nixos-sandbox-test-env.md` (orchestrator, at
  discussion close).
