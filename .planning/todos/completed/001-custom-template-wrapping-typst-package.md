---
title: "manualのCustom Template Wrappingでtypst_Packageの設定で\"@preview/charged-ieee:0.1.4\"を指定してるんだけど、_templates/custom_ieee.typ内でこのパッケージ指定済だからtypst_package指定する必要無くない？記述合ってる？"
status: pending
priority: P2
source: "promoted from /gsd-note"
created: 2026-07-21
theme: general
---

## Goal

manualのCustom Template Wrappingでtypst_Packageの設定で"@preview/charged-ieee:0.1.4"を指定してるんだけど、_templates/custom_ieee.typ内でこのパッケージ指定済だからtypst_package指定する必要無くない？記述合ってる？

## Context

Promoted from quick note captured on 2026-07-21 20:28.

## Acceptance Criteria

- [ ] ドキュメント（manual の Custom Template Wrapping 節）の `typst_package = "@preview/charged-ieee:0.1.4"` 記述が、`_templates/custom_ieee.typ` 内で既に `#import` 済みの場合に本当に必要かを検証し、不要なら記述を修正する
