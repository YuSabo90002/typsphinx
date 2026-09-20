# Phase 75: v0.9.6 Release Prep (prep-only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-20
**Phase:** 75-v0-9-6-release-prep-prep-only
**Areas discussed:** `[0.9.6]` section shape, Phase 74 CHANGELOG bullet wording, Phase 74
leftovers, REL-16 Known Limitations

**Gray areas presented:** four — REL-16 Known Limitations, `[0.9.6]` section shape, Phase 74 bullet
wording, Phase 74 leftovers. The owner selected the last three. REL-16 was raised anyway at the end
of the discussion, because ROADMAP SC3's decline branch requires the *owner* to decline and record
why — Claude's discretion cannot satisfy it.

---

## `[0.9.6]` section shape

### Q1 — Where does the Phase 74 doctest bullet go, and are the six carried bullets touched?

| Option | Description | Selected |
|--------|-------------|----------|
| Head of `### Fixed`, existing unchanged | New bullet first, sidebar bullet after; six carried bullets byte-identical in their current Added/Changed/Fixed assignment; matches house order | ✓ |
| Tail of `### Fixed`, existing unchanged | Chronological (v0.9.5 sidebar → v0.9.6 doctest); smallest diff | |
| Also revise existing wording | Compress the four ~40-line `### Changed` bullets; flagged as diverging from REL-15's "promoted" wording and from 69/71/73's D-05 | |

**User's choice:** Head of `### Fixed`, existing unchanged → **D-01**

### Q2 — Lead paragraph under the `## [0.9.6]` heading?

| Option | Description | Selected |
|--------|-------------|----------|
| Write it, doctest-fix framing | Rendering fix is the subject; contributor tooling gets one sentence | ✓ |
| Write it, maintenance-release framing | "Three milestones of accumulation" framing; 5 of 6 bullets say they have no user effect | |
| No lead paragraph | Flagged: every prior released section (`[0.9.2]` … `[0.6.5]`) has one | |

**User's choice:** Write it, doctest-fix framing → **D-02**

### Q3 — How far does the lead paragraph go on recommending the upgrade?

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit recommendation | `[0.9.2]`'s register ("0.9.0 users should upgrade"); reader's previous release is 0.9.2 since 0.9.3–0.9.5 are unclaimed | ✓ |
| State the affected condition only | Give the facts, let the reader judge; no "should upgrade" | |
| Do not mention it | `[0.9.0]` guides toward breaking changes but never says "upgrade"; only `[0.9.2]` has the recommendation | |

**User's choice:** Explicit recommendation → **D-03**

**Notes:** justified by the measured pre-fix compile abort (`expected semicolon or line break`),
not only by the rendering collapse.

### Q4 — Does `## [0.9.6]` carry a `### Verified` section?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, invariants stated precisely | Measured: `[0.9.2]`'s blanket "Zero new runtime or dev dependencies" is **false** for v0.9.6 — the `dev` extra changed (`tox-uv-bare`→`tox-uv`, `ruff` cap `<0.16`→`<0.17`) while runtime deps did not | ✓ |
| Yes, doctest evidence only | GATE-01 real-compile coverage plus the warning ledger; avoids the dependency claim entirely | |
| No `### Verified` | Would be the first released section without one | |

**User's choice:** Yes, invariants stated precisely → **D-04**

### Q5 — How is the `## [0.9.6] - YYYY-MM-DD` date decided?

| Option | Description | Selected |
|--------|-------------|----------|
| Fix at the prep authoring date | Measured precedent: `[0.9.2]` written 2026-08-30, merged 08-31 (1 day out); `[0.9.0]` written 2026-08-17, tagged 08-22 (5 days out) | ✓ |
| Reconcile before merge | Conditional handoff step to re-check the date against the actual tag date before the PR | |
| Omit the date | Would be the first heading without one | |

**User's choice:** Fix at the prep authoring date → **D-05**

**Notes:** recorded in `75-HANDOFF.md` as a fact, not a step — `/gsd-complete-milestone` does not
rewrite the heading.

---

## Phase 74 CHANGELOG bullet wording

### Q1 — Where is the doctest bullet's claim centred?

| Option | Description | Selected |
|--------|-------------|----------|
| Both rendering and compile | Rendering fix leads; the compile abort in the trailing-content shape is recorded second | ✓ |
| Rendering collapse only | Compile failure's conditions are narrow and heavy for release notes | |
| Compile failure as the subject | `[0.9.2]`'s framing; noted that this project's own docs build succeeded — the failure reproduced in the fixture | |

**User's choice:** Both rendering and compile → **D-06**

### Q2 — Disclose the `python`-fence trade-off?

| Option | Description | Selected |
|--------|-------------|----------|
| One sentence | Output lines are coloured as Python source; measured, `'index.typ'` comes out green as a string literal; `pycon` would give neither highlighting nor a language label | ✓ |
| Do not disclose | Cosmetic detail, and clearly better than the pre-fix running prose; rationale already lives in 74-CONTEXT D-01 | |
| Disclose plus the honour path | Also mention that an existing non-empty `language` wins; noted that standard Sphinx never sets one on a `doctest_block` | |

**User's choice:** One sentence → **D-07**

### Q3 — What does the bullet's single evidence sentence say?

| Option | Description | Selected |
|--------|-------------|----------|
| Reflection into the published documentation | typsphinx's own API reference is the worked example and reaches the published docs with this release; **inverts** 73 D-04, which barred `stable` claims because v0.9.5 published nothing | ✓ |
| The real-compile gate | Would duplicate `### Verified`, already decided in D-04 | |
| No evidence sentence | Concentrate evidence in `### Verified` | |

**User's choice:** Reflection into the published documentation → **D-08**

### Q4 — Does QUA-14 appear in the CHANGELOG?

| Option | Description | Selected |
|--------|-------------|----------|
| Its own bullet | Second in `### Fixed`; measured base 3 attributed / 10 raw docutils messages → zero on the tip | ✓ |
| Folded into the doctest bullet | One "the API reference now renders correctly" story; both measured on the same warning ledger | |
| Not written | Effect is limited to autodoc'ing typsphinx, effectively this project's own docs | |

**User's choice:** Its own bullet → **D-09**

---

## Phase 74 leftovers

### Q1 — The five untracked `probe_*.typ` files at the repo root

| Option | Description | Selected |
|--------|-------------|----------|
| Delete in Phase 75 | Untracked, so no commit and no effect on SC5's `git diff`; cleans `git status` at the milestone close; named by the milestone audit | ✓ |
| Leave them | Outside every scope fence; prep-only phases do not touch the working tree | |
| Delete and add to `.gitignore` | Prevents recurrence but adds a product-tree commit beyond REL-15's file set | |

**User's choice:** Delete in Phase 75 → **D-13**

### Q2 — IN-01 (`Args:` text not widened with the signatures)

| Option | Description | Selected |
|--------|-------------|----------|
| Leave it, file a todo | Holds the prep-only fence; precedent v0.7.1 D-03/D-27; touching `typsphinx/` would force SC4's whole green proof to be retaken | ✓ |
| Fix it in Phase 75 | One docstring line, near-zero risk | |
| Promote to a next-milestone requirement | Carry it explicitly in `75-HANDOFF.md` and the backlog instead of a todo | |

**User's choice:** Leave it, file a todo → **D-14**

### Q3 — push and CI dispatch operation

**First attempt was returned for clarification.** The owner's clarification: *"本来設定でMile Stone
毎にPRするわけだが必要ならば随時Pushしよう"* — the PR stays per-milestone (opened at
`/gsd-complete-milestone`); pushing in between is fine as needed. That settled the push half, and
the question was reformulated to cover only the explicit dispatch count.

| Option | Description | Selected |
|--------|-------------|----------|
| One dispatch, after the bump | Matches SC4's "One fresh CI run … on the bumped tip"; covers `tests/test_docstring_rest_census_guard.py`, which run `35476044079` on `e54d47d0` does not | ✓ |
| Also one before the bump | Catches Windows/macOS-only defects earlier, but makes two dispatches and complicates SC4's evidence | |
| Extra only on failure | Same as the first in practice; pre-agrees the failure procedure | |

**User's choice:** One dispatch, after the bump → **D-15**

**Notes:** measured basis — `ci.yml`'s triggers are scoped to `main`/`develop`, so pushing the
milestone branch runs no CI. Push cost is zero and push timing carries no evidence weight.

---

## REL-16 Known Limitations

**Not selected in the area picker, raised anyway.** ROADMAP SC3 allows two branches — write the
section, or have the *owner* decline it and record why. The decline branch cannot be taken by
Claude's discretion, so the question had to reach the owner.

**Premise correction delivered before the question.** The candidate set REL-16, ROADMAP SC3 and
`PROJECT.md:88-90` all name — NUM-01, the converted-image rehome collision, the `typst_documents`
duplicate-target cluster — was measured and found **two-thirds stale**:

| Candidate | Where its todo lives | Verdict |
|---|---|---|
| NUM-01 (per-master `numref` divergence) | `.planning/todos/pending/` | open |
| converted-image rehome collision | `.planning/todos/completed/` | closed in v0.8.0 (IMG-01/IMG-02; `builder.py:40 RESERVED_IMAGE_NAMESPACE`) |
| `typst_documents` duplicate-target cluster | `.planning/todos/completed/` (all three records) | closed in v0.8.0 Phase 47 (`builder.py:1068 _validate_output_path_collisions()`) |

`.planning/todos/pending/` holds exactly three records: QUA-08, NUM-01 and MSG-06.

### Q1 — Does `## [0.9.6]` carry a `### Known Limitations` section?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, NUM-01 only | One entry, in v0.9.0's `### Known limitations shipped` register; the two closed defects are not written | ✓ |
| Yes, NUM-01 plus WR-02/WR-03 | Adds the two genuinely-open `templates_path` defects; WR-02's CHANGELOG carve-out was the reviewer's own recommended minimum, declined three releases running | |
| Decline | v0.7.1 D-27's precedent; record the decline and the reason in the decision record and handoff | |

**User's choice:** Yes, NUM-01 only → **D-10**

**Notes:** writing the two closed defects would be the mirror image of the over-broad
true-sounding claim this project criticised itself for at the v0.9.0 close
(`MILESTONES.md:626-630`).

### Q2 — How deep does the NUM-01 entry go?

| Option | Description | Selected |
|--------|-------------|----------|
| Precondition + both symptoms + workaround | Follows the existing `### Known Limitations` shape at `CHANGELOG.md:1205` (bold lead, sub-bullets, a `Workaround:` line) | ✓ |
| Precondition + both symptoms | Same content without a `Workaround:` line; the available workarounds both give up functionality | |
| One-sentence summary | Detail left to the todo | |

**User's choice:** Precondition + both symptoms + workaround → **D-11**

---

## Claude's Discretion

The owner did not discuss these; they are fixed by ROADMAP SC 1–5 or carried from Phases 69 / 71 /
73, and are recorded in CONTEXT.md § Claude's Discretion:

- the `75-CLOSEOUT-GUARD.md` SHA-256 fence and its post-`phase.complete` re-verification;
- the non-committing trial merge (`git merge-tree --write-tree`, `uv lock --check`, `ruff check .`);
- the bump mechanics (`pyproject.toml:7` the sole literal, `uv lock` regenerating `uv.lock`,
  `README.md`'s Status line, `RELEASE_VERSIONS` gaining `"0.9.6"`, all in one commit);
- the fresh `## [Unreleased]` retaining only `### Planned for Future Releases`;
- the tail link block move and the `scripts/extract_changelog_section.py 0.9.6` run;
- requirement-ID style, and omitting the "no effect on installing or using typsphinx" sentence from
  the two new bullets;
- `75-HANDOFF.md`'s contents;
- decoy-branch handling and the two tag-absence probe rounds.

## Deferred Ideas

- Fixing NUM-01 — disclosure only this milestone.
- Disclosing WR-02 / WR-03 in the CHANGELOG — open, but not named by REL-16.
- Fixing IN-01 — filed as a pending todo (D-14).
- Adding `probe_*.typ` to `.gitignore` — rejected as outside REL-15's file set (D-13).
- Reviewed but not folded: QUA-08 (`2026-07-22-add-sphinx-linkcheck-ci-job.md`, needs a side PR to
  `main`) and MSG-06
  (`2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`,
  touches `typsphinx/translator.py`).
