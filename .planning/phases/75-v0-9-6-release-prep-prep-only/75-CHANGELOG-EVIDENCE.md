# Phase 75 — CHANGELOG Evidence (SC2, SC3)

## Base census

Before editing, from `git show "$B:CHANGELOG.md"` where `B = BASE_75_03 =
526a21d352696cb65c570d07d75ef8c7e3aa96a1`:

```
$ git show 526a21d352696cb65c570d07d75ef8c7e3aa96a1:CHANGELOG.md | wc -l
1349
```

The base `## [Unreleased]` section body (from `^## \[Unreleased\]$` to the line before the next
`^## \[`) was extracted with:

```
awk '/^## \[/{if(f)exit} f; /^## \[Unreleased\]$/{f=1}' <base CHANGELOG.md>
```

giving 60 lines, holding `### Added` (1 bullet), `### Changed` (4 bullets), `### Fixed`
(1 bullet), and `### Planned for Future Releases` (5 items, no bold-lead bullet).

```
$ awk '...' | grep -cE '^- \*\*'
6
```

CARRIED_BULLETS_BASE = 6

BASE_SUBSECTIONS = `### Added|### Changed|### Fixed|### Planned for Future Releases|`

```
$ grep -cE '^## \[' <base CHANGELOG.md>
23

$ grep -cE '^\[[^]]+\]: https' <base CHANGELOG.md>
23
```

HEADINGS_BEFORE = 23
LINKREFS_BEFORE = 23

```
$ grep -c '^### Known Limitations' <base CHANGELOG.md>
1
```

KNOWN_LIMITATIONS_BEFORE = 1. The base file's only anchored `^### Known Limitations` hit is the
`[0.1.0b1]` section (`:1205` in the base file's own numbering). The unanchored form,
`grep -c 'Known Limitations'`, would additionally count a prose mention elsewhere in the file
(the `[0.9.0]` section's discussion text), which is why every check in this evidence file uses
the anchored `^` form.

Per-subsection SHA-256 digests of the carried base bodies, blank lines dropped
(`awk -v h="### X" '$0==h{f=1;next} f&&/^### /{exit} f' | grep -v '^$' | sha256sum`):

CARRIED_ADDED_SHA = c630d24f43fddf5c82efd09f8d3675a75fab078a344e7fa4e1186a48c1b3492d
CARRIED_CHANGED_SHA = 6dac1ebd5e08cf5ef33d82673597cfb30d5dc59e217c04d82842fa2237abc7df
CARRIED_FIXED_SHA = ec38c5cbdfae8b4c32c95864e43f0cb658f06776f9f0f482f40143962c309f20

## Curation

`CHANGELOG.md` was edited to:

1. Insert a fresh `## [Unreleased]` heading holding only the existing `### Planned for Future
   Releases` block (5 items, unchanged, not promoted).
2. Insert `## [0.9.6] - 2026-09-20` (RELEASE_HEADING_DATE, `date -u +%F` at execution), with:
   - A lead paragraph naming the doctest rendering fix as the release's subject, the
     `expected semicolon or line break` compile abort as the pre-fix failure's severity, an
     explicit upgrade recommendation against 0.9.2, and the contributor tooling acknowledged in
     one side-note sentence.
   - The carried `### Added` (1 bullet) and `### Changed` (4 bullets) bodies, copied
     byte-identically from the base `## [Unreleased]` section — no re-wrap, re-word, re-order or
     re-assignment.
   - `### Fixed` with two new bullets first (the doctest bullet trailing `(TRN-01, TRN-02)`, then
     the QUA-14 bullet trailing `(QUA-14)`), followed by the carried `### Fixed` bullet as a
     byte-identical tail.
   - `### Known Limitations`, holding exactly one bold-lead entry naming NUM-01, adapted (not
     copied verbatim) from `75-RESEARCH.md` Pattern 4's draft shape and the NUM-01 todo's
     precondition, both symptoms and workaround.
   - `### Verified`, four bullets: no new runtime/dev dependency other than the `dev` extra's
     `tox-uv` return; the four `@preview` packages unchanged across the three declaration sites;
     the GATE-01 real-`typst.compile()` coverage behind the new `doctest_block` handler; and the
     QUA-14 clean-build warning reading (zero, down from a measured baseline of five).
3. Move the tail link block: `[0.9.6]: .../releases/tag/v0.9.6` inserted immediately above
   `[0.9.2]`, and `[Unreleased]`'s compare base re-pointed from `v0.9.2` to `v0.9.6`.

`tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple gained `"0.9.6"`, appended
immediately after the existing `"0.9.2"` entry, reordering nothing.

## New section census

```
$ awk '/^## \[/{if(f)exit} f; /^## \[0\.9\.6\]/{f=1}' CHANGELOG.md | grep -E '^### ' | tr '\n' '|'
### Added|### Changed|### Fixed|### Known Limitations|### Verified|
```

Per-subsection bullet counts (`grep -cE '^- \*\*'`): Added 1, Changed 4, Fixed 3.

```
$ grep -cE '^## \['CHANGELOG.md
24

$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
24
```

HEADINGS_AFTER = 24
LINKREFS_AFTER = 24

Each is the base count plus exactly one: `HEADINGS_AFTER` gains the new `## [0.9.6]` heading, and
`LINKREFS_AFTER` gains the new `[0.9.6]` tail link.

```
$ grep -n '^## \[0\.9\.6\]' CHANGELOG.md
17:## [0.9.6] - 2026-09-20

$ grep -n '^## \[Unreleased\]$' CHANGELOG.md
8:## [Unreleased]
```

The `## [0.9.6]` heading (line 17) sits below the `## [Unreleased]` heading (line 8).

RELEASE_HEADING_DATE = 2026-09-20

```
$ grep -n '^\[0\.9\.6\]:' CHANGELOG.md
1378:[0.9.6]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6

$ grep -n '^\[0\.9\.2\]:' CHANGELOG.md
1379:[0.9.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.2

$ grep -n '^\[Unreleased\]:' CHANGELOG.md
1401:[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD
```

The `[0.9.6]` tail link (1378) sits immediately above `[0.9.2]` (1379).

Recomputed carried digests, compared against the base ones recorded above — all three match:

| Subsection | Base digest | Recomputed digest |
|---|---|---|
| `### Added` | `c630d24f…` | `c630d24f…` (identical) |
| `### Changed` | `6dac1ebd…` | `6dac1ebd…` (identical) |
| `### Fixed` (carried tail) | `ec38c5cb…` | `ec38c5cb…` (identical) |

`### Known Limitations` anchored count:

```
$ grep -c '^### Known Limitations$' CHANGELOG.md
2
```

KNOWN_LIMITATIONS_AFTER = 2

That count is the pre-existing `[0.1.0b1]` heading plus the new one added this phase.

## REL-16: which branch was taken

The branch taken is the `### Known Limitations` section, not the declination — SC3 and D-10/D-11
require a genuine disclosure entry, not silence.

Its candidate set is **NUM-01 alone**. REL-16's literal text names three defects; two of them were
measured closed before this phase:

- **The converted-image rehome collision** closed in v0.8.0. `typsphinx/builder.py` carries a
  reserved image namespace constant closing this collision, and its tracking todo is in
  `.planning/todos/completed/` — measured, not assumed.
- **The `typst_documents` duplicate-target cluster** also closed in v0.8.0, via the pre-write
  output-path collision validator landed the same release.

Both closures are recorded in the same v0.8.0 milestone that also delivered the two-layer output
split; their todos are archived under `.planning/todos/completed/`, not `.planning/todos/pending/`.

WR-02 and WR-03 are genuinely open defects in this codebase, but REL-16's text does not name
either one, so neither is added to this section — adding them would exceed what this requirement
actually asks for.

D-12's anchored grep expects exactly two `### Known Limitations` headings after this phase (the
pre-existing `[0.1.0b1]` one plus this phase's new one), confirmed above: `KNOWN_LIMITATIONS_AFTER
= 2`.

REL16_BRANCH = known-limitations-section

## Zero-skip changelog page gate

```
$ uv run pytest tests/test_changelog_page_gate.py -q -rs -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a64ee11a04ac3c9ef
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests/test_changelog_page_gate.py ......                                 [100%]

============================== 6 passed in 4.21s ===============================
```

No `SKIPPED` lines were reported. The `docs` extra (installing `myst-parser`) is present in this
worktree's environment per this plan's `<worktree_provisioning>`, so the content-coverage classes
ran rather than skipped.

CHANGELOG_GATE_EXIT = 0
CHANGELOG_GATE_SKIPS = 0

## Commit discipline

`CHANGELOG.md` and `tests/test_changelog_page_gate.py` are left uncommitted per this plan's
worktree provisioning instructions. Only this evidence file (`75-CHANGELOG-EVIDENCE.md`) is
staged and committed for Task 2; the product edits wait for Task 3's single five-file commit.
