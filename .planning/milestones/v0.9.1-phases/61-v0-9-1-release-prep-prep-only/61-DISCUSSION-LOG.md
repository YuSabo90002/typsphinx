# Phase 61: v0.9.1 Release Prep (prep-only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-29
**Phase:** 61-v0-9-1-release-prep-prep-only
**Areas discussed:** Handling of the unfixed inline-image blocker (the only area the owner selected)

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| 未修正 blocker の扱い | The 2026-08-29 owner-reported pending todo: an inline image mid-paragraph is emitted adjacent to the preceding code-mode expression, Typst answers `expected semicolon or line break`, and `-b typstpdf` produces no PDF for any master document. Measured as pre-existing (identical to the `v0.9.0` tag), not a v0.9.1 regression. | ✓ |
| [0.9.1] エントリの構成と事実主張 | `## [Unreleased]` holds zero real bullets so the entry is authored from scratch; section assignment for the three defect families; whether `typsphinx/pathfmt.py` and Phase 58 earn bullets; whether the lead may say "Windows-only". | |
| SC#3 の green の出所 | One CI dispatch or two; docs warning baselines; where lint authority sits. | |
| 61-HANDOFF.md の範囲 | SC#5's named items plus whether the unproven `release.yml` `create-release` step becomes a pre-publish check. | |

---

## 未修正 blocker の扱い

### Question 1 — How does the blocker relate to v0.9.1?

| Option | Description | Selected |
|--------|-------------|----------|
| 開示して出荷（推奨） | Ship as scoped, disclose as a known issue in the CHANGELOG. Fence intact; Phase 57 D-09/D-10 disclosure precedent. | ✓ (modified) |
| リリース前に直す | Insert a fix phase before v0.9.1 and ship the fix as part of it. Costs: work outside the milestone's theme; release slips. | |
| 開示せず出荷 | Say nothing; it first appears as `### Fixed` whenever it is fixed. | |
| v0.9.1 を先に出して v0.9.2 を即座に立てる | Ship as scoped, record the blocker as v0.9.2's first item. | |

**User's choice:** "開示して出荷するが、0.9.1 は complete-milestone でリリースしない" — a modified form of option 1: disclose, complete the prep, but do not publish.
**Notes:** This reframed the phase. It invalidated the premise of ROADMAP SC#1/SC#2, which assume a published 0.9.1, so the following questions were needed.

### Question 2 — What becomes of the deferred v0.9.1?

| Option | Description | Selected |
|--------|-------------|----------|
| prep 完了で凍結、publish は後日判断 | Complete SC#1–SC#5; `/gsd-complete-milestone` archives only; the handoff stays executable for whenever the owner decides. REL-09 carries forward. | |
| blocker 修正フェーズを v0.9.1 に追加してから publish | Add a fix phase to this milestone, then publish 0.9.1 with the fix. Disclosure becomes temporary. | |
| 0.9.1 は永久に未公開、次は 0.9.2 | No `v0.9.1` tag ever exists. The next milestone (carrying the blocker fix) publishes as 0.9.2. | ✓ |

**User's choice:** 0.9.1 は永久に未公開、次は 0.9.2.
**Notes:** Established that the version number is skipped outright, not held.

### Question 3 — How does Phase 61 handle the version?

Measured and presented before asking: `.github/workflows/links.yml` excludes `CHANGELOG.md` from the
repo-wide lychee scan, so a dead `[0.9.1]` link would **not** be caught by CI — but
`docs/source/changelog.rst:1` includes `CHANGELOG.md` wholesale, so it would be published on Read the
Docs as a 404, contradicting PROJECT.md's core value that a published URL must resolve.

| Option | Description | Selected |
|--------|-------------|----------|
| バンプしない。Unreleased に書く（推奨） | `pyproject.toml` stays 0.9.0; the three defect families go under `## [Unreleased]`; link block untouched. Phase shrinks to green proof plus handoff. | ✓ |
| 0.9.2 に直接バンプ | Bump now on the assumption the next release is 0.9.2. Costs: the CHANGELOG would pre-announce a fix not yet written; `[0.9.2]` link dead until tagged. | |
| 予定通り 0.9.1 にバンプ | Follow SC#1/SC#2 literally. Costs: README advertises an uninstallable version, `__version__` reports a version absent from PyPI, 404 link in published docs. | |

**User's choice:** バンプしない。Unreleased に書く.
**Notes:** This is what drops ROADMAP SC#1 and rewords SC#2 (CONTEXT D-01, D-03, D-04, D-11).

### Question 4 — Where is the blocker disclosed?

Measured and presented before asking: `### Known Limitations` appears in `CHANGELOG.md` exactly once
(inside the `0.1.0b1` section); the live public surface is `README.md:289`'s `## Known Limitations`,
currently holding two entries (Bibliography, Citations).

| Option | Description | Selected |
|--------|-------------|----------|
| README の Known Limitations | Add one entry with the measured trigger condition and workaround; also reaches the PyPI project page. | |
| CHANGELOG の Unreleased 配下 | `### Known Limitations` under `## [Unreleased]`; reaches RTD `latest` via the include. | |
| docs のユーザーガイド | A note in the image-related docs pages. | |
| 公開面には書かない | Keep it to the todo record and the internal handoff; it first appears publicly as a `### Fixed` bullet in 0.9.2. | ✓ |

**User's choice:** 公開面には書かない.
**Notes:** Consistent with question 2 — no version carrying the defect will be newly published. The
trade-off explicitly stated in the option text and accepted: users already on the published 0.9.0 hit
this defect today and get no notice until 0.9.2 ships. Recorded in CONTEXT D-05.

### Question 5 — What happens to REL-09?

| Option | Description | Selected |
|--------|-------------|----------|
| 未達のまま繰り越す（推奨） | Stays `[ ]` with its wording untouched, including the literal `v0.9.1`; moves to the v0.9.2 milestone. | ✓ |
| 文言を v0.9.2 に改めて繰り越す | Rewrite the requirement text. Costs: editing a completed milestone's requirement after the fact. | |
| superseded として閉じる | Close it with a supersession note. Costs: a requirement could read `[x]` when nothing shipped. | |

**User's choice:** 未達のまま繰り越す.
**Notes:** CONTEXT D-08. Raises the stakes on the known `phase.complete` auto-flip guard (D-10), since
REL-09's wording no longer matches what the phase did.

### Question 6 — Where does the blocker fix live?

| Option | Description | Selected |
|--------|-------------|----------|
| 次マイルストーン v0.9.2 で（推奨） | Close this milestone at Phase 61; `/gsd-new-milestone` picks the todo up during requirements gathering. | ✓ |
| このマイルストーンに修正フェーズを追加 | Add a Phase 62 on this branch, then release as 0.9.2. Cheaper environment-wise; breaks the milestone's theme and phase ordering. | |
| Phase 61 の前に割り込む | Insert as Phase 60.5. Costs: a backwards roadmap insertion with STATE already on 61. | |

**User's choice:** 次マイルストーン v0.9.2 で.
**Notes:** CONTEXT D-07. `61-HANDOFF.md` names the todo so v0.9.2 does not rediscover it.

### Question 7 — Confirmation of the reshaped phase

The five-point reshaped phase (no bump; content under `## [Unreleased]`; SC#3 green proof retained
and re-anchored; SC#4 fence proof retained; handoff re-aimed at v0.9.2) was restated and confirmed.

| Option | Description | Selected |
|--------|-------------|----------|
| これで CONTEXT を書く | Lock the five points; record the ROADMAP conflict inside CONTEXT.md for downstream agents. | ✓ |
| ROADMAP も今書き換える | Rewrite ROADMAP.md's Phase 61 Goal and SC#1–SC#5 first so downstream gates see no mismatch. | |
| もう少し詰めたい | Continue into CI dispatch count, bullet granularity, and the handoff's scope. | |

**User's choice:** これで CONTEXT を書く.
**Notes:** Produced CONTEXT D-11, which maps each ROADMAP criterion to DROPPED / REWORDED / RETAINED
and names the planner, plan-checker, and verifier as its readers.

---

## Claude's Discretion

Recorded in CONTEXT.md's `### Claude's Discretion`: CHANGELOG bullet wording, section assignment and
granularity (including whether `typsphinx/pathfmt.py` and Phase 58's test-side work earn bullets);
placement relative to `### Planned for Future Releases`; whether a `### Verified` subsection is
written now or left to v0.9.2; plan decomposition; how docs warning baselines are established; the
mechanical form of the `REQUIREMENTS.md` checksum guard; the structure of `61-HANDOFF.md` and evidence
file naming (subject to the `61-VERIFICATION.md` reserved-name constraint); and whether a
`v0.9.0`-anchored milestone-diff sweep is worth running.

## Deferred Ideas

- Rewriting ROADMAP.md's Phase 61 entry to match CONTEXT.md — offered and declined; revisit only if a
  downstream gate proves too noisy about the mismatch.
- Publishing v0.9.1 after all — foreclosed by D-02 for this milestone.
- Disclosing the inline-image blocker on a public surface — foreclosed by D-05; the natural place to
  revisit is the v0.9.2 release-prep phase, where it becomes a `### Fixed` bullet.
- Three unfolded todos worth re-offering later: the `translator.py` hardcoded-delimiter debug logs and
  the inline-image blocker (both natural companions in v0.9.2), and the unproven `release.yml`
  `create-release` step (belongs in the v0.9.2 handoff's pre-publish checks).
