---
phase: "74"
slug: "the-doctest-block-handler-its-real-compile-gate-and-the-docs"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-20"
---

# Phase 74 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time** — all seven of this phase's PLAN.md files
carry a parseable `<threat_model>` block. This audit verifies that each planned
mitigation is present in the delivered tree; it does not scan for new threats.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Sphinx console text → evidence counts | a localised, quieted or incremental build could fake a zero or a base count | build warning/error lines, counts |
| third-party autodoc extension → console | `sphinx-autodoc-typehints` prints unattributed docutils lines a naive grep would miscount | unattributed docutils message lines |
| reST / docstring text → Typst source | doctest content is emitted raw inside a code fence and compiled by typst-py | author-authored reST / docstring text |
| translator change → every document's output | a change on the shared literal-block path would alter every code block | emitted `.typ` markup |
| doctree node → later transforms / writers | a mutated node attribute would leak beyond this handler | docutils node attributes |
| test assertions → evidence | a gate first observed green, or asserting on observed output, proves nothing | expected-vs-observed values |
| worktree working tree ↔ base checkout window | the base rebuild temporarily replaces `typsphinx/` with base files | source files under `typsphinx/` |
| local gates → push decision | a tip pushed without local proof defers every signal to CI | commits, test verdicts |
| local refs → origin | a push publishes refs; a decoy, a force, another ref or a tag would publish what this phase must not | git refs (branch, tags) |
| gh CLI → GitHub Actions | a dispatch starts remote work; the wrong workflow could begin a publish pipeline | workflow_dispatch events |
| CI log → committed evidence | quoted job-log lines enter the repository | public CI log excerpts |
| worktree → GitHub API (read-only) | `gh api` / `gh run view` reads; no write crosses this boundary in 74-01 | run metadata |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-74-01 | Repudiation | base counts from a localised or incremental build | high | mitigate | `rm -rf` of the output dir before each build, `LANG=C LC_ALL=C`, English `build succeeded` in the same log, non-zero positive controls — verified in `74-BASE-EVIDENCE.md` (`rm -rf "$S/base-typst"`, `LANG=C LC_ALL=C … -b typst`, `BASE_WARNING_COUNT = 5`) | closed |
| T-74-02 | Tampering | a QUA-14 census narrowed to the named docstrings | high | mitigate | whole-log raw count plus the attributed filter; every unattributed line matched by the docstring probe — `BASE_ATTRIBUTED_COUNT (3) + BASE_UNATTRIBUTED_COUNT (7) = 10` raw, `BASE_UNATTRIBUTED_UNMATCHED = 0` | closed |
| T-74-03 | Information Disclosure | absolute worktree paths in transcribed console lines | low | accept | see ACC-74-01 | closed |
| T-74-04 | Tampering | `uv sync` supply chain | low | accept | see ACC-74-02 | closed |
| T-74-05 | Repudiation | RED reconstructed, or observed on a tree carrying a handler | high | mitigate | `RED_TREE_SHA = 215e9715` independently confirmed to carry an unmodified `typsphinx/` against `6cc44f22` (`git diff --stat` empty, 0 `doctest` mentions); verbatim RED transcript; `RED_PYTEST_EXIT = 1`, `RED_FAILED_COUNT = 10` | closed |
| T-74-06 | Tampering | a gate that asserts on observed output instead of the source | medium | mitigate | `_source_doctest_block()` reads the fixture reST (`tests/test_doctest_block_render_gate.py:123`) and supplies every expected value; no observed value appears in an assertion | closed |
| T-74-07 | Denial of Service | a Windows runner failing to decode non-ASCII subprocess output | low | mitigate | `encoding="utf-8", errors="replace"` on the subprocess (gate module lines 92–93) and UTF-8 text-mode reads of every `.typ` (lines 120, 134); Windows CI lanes green | closed |
| T-74-08 | Tampering | Typst code injection through doctest content | low | accept | see ACC-74-03 | closed |
| T-74-09 | Tampering | the shared literal-block emission path changing for `literal_block` nodes | high | mitigate | the `"python"` fallback is keyed on `isinstance(node, nodes.doctest_block)` (`typsphinx/translator.py:2578-2580`) and applies only when `node.get("language", "")` is empty; `test_literal_block_without_language_keeps_bare_fence` (`tests/test_translator.py:3961`); 74-05's whole-tree diff (`D05_UNEXPLAINED_HUNKS = 0`, `D05_REMOVED_FENCE_LINES = 0`) | closed |
| T-74-10 | Repudiation | a GREEN claim on a modified gate | high | mitigate | `GATE_UNCHANGED_SINCE_RED = yes` — `git diff --quiet 215e9715 255d1648` over the gate module and fixtures exits 0 | closed |
| T-74-11 | Tampering | doctree mutation leaking into later transforms or writers | medium | mitigate | no assignment to the node's `language` attribute exists anywhere in `typsphinx/translator.py` (grep: 0 hits); `test_doctest_block_defaults_to_python_fence` (`tests/test_translator.py:3925`) asserts the attribute stays absent | closed |
| T-74-12 | Repudiation | the QUA-14 message class suppressed instead of fixed | high | mitigate | `git diff 6cc44f22..HEAD -- docs/` empty (live re-check); only blank lines added under `typsphinx/`; English summary line and the base census serve as positive controls (`FIX_ATTRIBUTED_COUNT = 0` vs. base 3) | closed |
| T-74-13 | Tampering | documented meaning changed by the repair | medium | mitigate | blank-line-only diff enforced — live re-check: added non-blank lines in `typsphinx/pathfmt.py` = **0**; `HTML_VISIT_TOCTREE_WORDS_EQUAL = yes`, `TYP_VISIT_TOCTREE_WORDS_EQUAL = yes` | closed |
| T-74-14 | Tampering | scope creep into other `typsphinx/` code while the file is open | medium | mitigate | region-scoped hunk checks — `TRANSLATOR_HUNKS_OUTSIDE_SCOPE = 0`; live `git diff --name-only 6cc44f22..HEAD -- typsphinx/` lists exactly `pathfmt.py` and `translator.py` | closed |
| T-74-15 | Tampering | base files left in, or committed from, the worktree after the rebuild | high | mitigate | `RESTORE_CLEAN = yes`; live `git status --porcelain -- typsphinx` is empty; evidence staged by name, never `commit -a` | closed |
| T-74-16 | Repudiation | an unexplained output difference waved through as noise | high | mitigate | per-hunk table counted against `diff -u`: `D05_HUNK_COUNT = 6` = `D05_TRN01_HUNKS (2) + D05_QUA14_HUNKS (2) + D05_FINDING_HUNKS (2)`, `D05_UNEXPLAINED_HUNKS = 0` | closed |
| T-74-17 | Repudiation | a tip zero believed without a same-environment positive control | medium | mitigate | the base rebuild in the same venv reproduced 74-01's non-zero counts — `REBUILT_BASE_MATCHES_74_01 = yes` (5 / 2 / 10 / 3) | closed |
| T-74-18 | Tampering | scope creep into workflows, `flake.nix`, `pyproject.toml` or `uv.lock` | high | mitigate | `WORKFLOWS_FLAKE_UNTOUCHED = yes`, `PYPROJECT_UV_LOCK_INIT_UNTOUCHED = yes`; live `git diff --name-only 6cc44f22..HEAD -- .github/ flake.nix pyproject.toml uv.lock typsphinx/__init__.py` is empty | closed |
| T-74-19 | Denial of Service | a locale-dependent test that fails only in CI | medium | mitigate | the full suite also ran under `LC_ALL=C`: `FULL_PYTEST_C_EXIT = 0`, `FULL_PYTEST_C_PASSED = 1562`, `FULL_PYTEST_C_FAILED = 0`; 12/12 CI jobs green across ubuntu/macos/windows | closed |
| T-74-20 | Repudiation | a gate turned green by editing tests | high | mitigate | `PREEXISTING_TEST_DELETIONS = 0`, `MODIFIED_TEST_FILES = tests/test_translator.py`; live `git diff --numstat 6cc44f22..HEAD -- tests/test_translator.py` → `72 0` (zero deletions) | closed |
| T-74-21 | Tampering | pushing a decoy, force-pushing, another ref, or a tag riding along | high | mitigate | `DECOY_ACTION = none-present`, `ORIGIN_BEFORE = none`, `--no-follow-tags -u` of the canonical ref only; live `git ls-remote --heads origin` shows one v0.9.6 ref at `e54d47d0` and no decoy; live `git ls-remote --tags origin` has no `v0.9.3`–`v0.9.6` tag and no tag at the tip | closed |
| T-74-22 | Elevation of Privilege | triggering `release.yml` or `update-pin.yml` | high | mitigate | only `gh workflow run CI` was issued; `RELEASE_RUNS_AT_PUSHED = 0` | closed |
| T-74-23 | Repudiation | citing an older run as this phase's green, or masking a red run with a second dispatch | high | mitigate | `RUN_HEAD_SHA = PUSHED_SHA = e54d47d0…`; `createdAt` 2026-09-19T23:24:33Z follows `PUSH_AT` 23:24:15Z; `DISPATCH_COUNT = 1`; `RUN_CONCLUSION = success`, `NON_SUCCESS_JOBS = 0` of `JOB_COUNT = 12` | closed |
| T-74-24 | Tampering | required status checks changing mid-phase | medium | mitigate | head and close reads compared — `REQUIRED_CHECKS_UNCHANGED = yes`, `REQUIRED_STRICT_CLOSE = true`, six-context list unchanged | closed |
| T-74-25 | Denial of Service | a stale `uv.lock` failing every lane | medium | mitigate | `uv sync --extra dev --python 3.13.13 --locked` exited 0 before the push; the lock was never regenerated (`uv.lock` unchanged in the scope fence) | closed |
| T-74-26 | Information Disclosure | CI log excerpts in evidence | low | accept | see ACC-74-04 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| ACC-74-01 | T-74-03 | Transcribed console lines carry absolute worktree paths only. The repository is public, the paths are local development paths, and they carry no credentials or secrets. | 74-01 plan author (project owner) | 2026-09-19 |
| ACC-74-02 | T-74-04 | No new dependency is added by this phase. `uv sync` installs only what `uv.lock` already pins, and the lock is unchanged in the scope fence (`PYPROJECT_UV_LOCK_INIT_UNTOUCHED = yes`). | 74-01 plan author (project owner) | 2026-09-19 |
| ACC-74-03 | T-74-08 | Doctest content is emitted only inside a raw ```` ```python ```` fence through `visit_Text`'s `in_literal_block` branch — the same trust model `literal_block` has carried since v0.6.0. The source is the author's own reST, never runtime input. A triple-backtick run inside a doctest would end the fence early; that is a pre-existing `literal_block` limitation outside this phase's scope. | 74-03 plan author (project owner) | 2026-09-19 |
| ACC-74-04 | T-74-26 | Only tool-output lines from a public repository's public CI logs are quoted into evidence. No secrets, tokens or private data appear in the quoted excerpts. | 74-07 plan author (project owner) | 2026-09-19 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-20 | 26 | 26 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 grep-depth) |

### Security Audit 2026-09-20

| Metric | Count |
|--------|-------|
| Threats found | 26 |
| Closed | 26 |
| Open | 0 |

Method: State B (no prior SECURITY.md). Register built from the `<threat_model>` blocks of
`74-01`…`74-07-PLAN.md` (26 threats; no SUMMARY carried a `## Threat Flags` section).
`register_authored_at_plan_time: true` and `asvs_level: 1`, so classification ran at L1
grep depth against the phase's evidence files and the delivered tree, with the scope-fence,
diff-shape, test-deletion, working-tree and origin-ref controls **re-measured live** in this
session rather than read from evidence alone. No threat required the deeper auditor pass.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-20
