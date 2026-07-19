# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v0.4.4 — CI-repair + modernize

**Shipped:** 2026-07-05
**Phases:** 5 | **Plans:** 15 | **Sessions:** ~2 days (2026-07-04 → 2026-07-05)

### What Was Built
- Runtime dependency graph pinned back to a known-good, reproducible combination (`typst>=0.14.1,<0.15`, `sphinx<9`, `docutils<0.22`), with regenerated `uv.lock` and mirrored tox ceilings — the actual bug fix for the `kai` PDF-compile break.
- A fully green CI pipeline confirmed by observed Actions runs: 3-OS × Python 3.10–3.13 matrix (19 jobs), coverage, and `docs.yml` end-to-end incl. the multi-language PDF-copy step.
- Modernized Python floor (3.10–3.13) and conservatively refreshed dev tooling + node24 artifact actions.
- Durability guardrails: `uv sync --locked` (DUR-01), standalone `drift.yml` weekly/dispatch detector (DUR-02), scoped `sphinx-typst-stack` Dependabot group (DUR-03), README CI badge (DUR-04).
- An automated `@preview` version-sync guard test protecting the 3-way hardcoded-version hazard.

### What Worked
- **Land-the-fix-alone sequencing.** Phase 1 pinned deps *alone* before any modernization, so the first green CI run was an unambiguous attribution of the fix. Every later phase rode on a confirmed-green baseline.
- **Empirical pin confirmation over assumption.** The exact typst 0.14.x patch was confirmed in CI rather than guessed, and PIN-06 explicitly recorded whether the sphinx/docutils ceilings were load-bearing vs precautionary.
- **Push→observe terminal gates.** Each phase closed with a real PR + observed CI run (PRs #104/#105/#106) rather than a local "should be green" assertion.
- **Guardrails as a first-class phase.** Making anti-recurrence its own phase (5) meant the milestone shipped with the drift class *actively prevented*, not just fixed.

### What Was Inefficient
- **Branch/main drift at close.** The milestone-finalization docs commits lived on the phase branch, 4 ahead of `origin/main`, while local `main` sat 74 behind — extra reconciliation was needed at milestone close. Fetch + fast-forward `main` immediately after each PR merge would avoid this.
- **Version-label mismatch.** GSD's internal milestone counter (`v1.0`) diverged from the project's real semver (`v0.4.4`), requiring a reconciliation pass across STATE/PROJECT at close. Set the milestone label to the intended release number at milestone *start*.
- **tox env-name mismatch surfaced late.** The `py3.10` vs `py310` mapping bug failed 9/12 matrix jobs and needed a Phase 2 gap-closure wave; a cheap local matrix-name lint could have caught it in Phase 1.

### Patterns Established
- **Floor + ceiling on every dependency bump.** After the unbounded-resolution rot, all deps (runtime and dev) now carry explicit upper bounds, mirrored between `pyproject.toml` and `tox.ini`.
- **Automated sync guards for hardcoded duplication.** Where a value is intentionally duplicated (the 3-way `@preview` versions), a CI test asserts equality rather than relying on human memory.
- **Release tag = live PyPI publish.** A `v*` tag triggers `release.yml`, which validates the tag against `pyproject.toml` version before publishing — so version bumps must precede tags.

### Key Lessons
1. **Pin the whole graph, not just the culprit.** The break came from a *transitive* `@preview` package under a new compiler major; only bounding the direct trio (typst/sphinx/docutils) *and* committing the lockfile makes CI reproducible.
2. **Sequence risk so red/green is attributable.** Landing the fix alone before modernization made every subsequent failure trivially traceable to the change that caused it.
3. **Set the milestone version label to the real release number up front** to avoid a rename pass at close.
4. **Guardrails belong in the milestone that fixed the rot**, not a vague "later" — `drift.yml` + `--locked` + scoped Dependabot make this exact class of silent drift fail loudly next time.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~2 calendar days of focused work.
- Notable: heavy use of push→observe CI gates meant wall-clock was dominated by GitHub Actions runs, not local iteration.

---

## Milestone: v0.5.0 — forward-ecosystem

**Shipped:** 2026-07-11
**Phases:** 6 (6–10 + 8.1 inserted) | **Plans:** 13 | **Sessions:** ~6 days (2026-07-05 → 2026-07-11)

### What Was Built
- Runtime pins raised forward to the current ecosystem — `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16`, Python floor 3.12–3.13 — across all 21 declaration sites, with `uv.lock` regenerated.
- The four bundled `@preview` packages bumped in lockstep (mitex 0.2.7, gentle-clues 1.3.1, codly-languages 0.1.10, codly 1.3.0), empirically closing the `unknown variable: kai` compile break — root-caused to mitex 0.2.6+, not the originally-suspected gentle-clues/codly.
- Soft-deprecated docutils/Sphinx API modernized (`traverse()`→`findall()`, `OptionParser`→`get_default_settings`, `builder.app`→`_app`, `writer_name`→`writer=get_writer_class`) with a permanent `filterwarnings` guard escalating both `DeprecationWarning` and `PendingDeprecationWarning`.
- A long-latent admonition markup/code-mode render bug fixed (Phase 8.1, inserted) — `info[...]`→`info({...})` code-mode blocks + inline-markup-preserving titles + five previously-missing admonition types + a real `sphinx-build → typst.compile → pypdf` acceptance gate.
- A `typst compile` smoke gate exercising all four `@preview` packages via real calls (incl. `.. math::` through mitex), closing the coverage gap the historical `kai` regression slipped through — proven with a negative control.
- Version single-sourced via `importlib.metadata` (stale `0.4.3` retired, `pyproject.toml` sole literal), curated `CHANGELOG.md` `[0.5.0]` entry, released to PyPI + GitHub Release.

### What Worked
- **Atomic risk-grouping.** FWD-02 (typst re-pin) was deliberately grouped with the `@preview` bump in one phase/wave rather than the pin-raise — raising typst alone would have left CI red on `kai`. The `kai` gate closed on the *first* real `docs-pdf` compile, no bisect needed.
- **Empirical gates over changelog inference.** The `kai` root cause (mitex 0.2.6+) was confirmed by a real compile, not trusted from changelogs — and it overturned the v0.4.4-era gentle-clues/codly suspicion.
- **Insert-a-phase for an orthogonal bug.** The admonition render bug surfaced mid-milestone (only visible once `docs-pdf` first compiled post-`kai`-fix); making it Phase 8.1 with its own acceptance gate kept it from contaminating the pin-raise phases.
- **Prep/publish split at the release boundary.** Phase 10 did prep-only; the irreversible publish (merge → tag → PyPI) was gated to milestone close on the exact CI-green merge commit — mirroring v0.4.4 and giving a clean go/no-go.
- **Milestone audit before close.** A dedicated `/gsd-audit-milestone` pass (14/14 requirements, 5/5 integration seams, E2E release-flow readiness) caught nothing broken but confirmed cross-phase wiring before the irreversible publish.

### What Was Inefficient
- **Sandbox environment friction.** The NixOS dynamically-linked `uv` binary couldn't launch in subprocess tests, producing ~45 environment-caused failures that had to be independently traced and distinguished from real regressions in every phase — a recurring per-phase verification tax. A documented in-sandbox `uv` shim/patch earlier would have saved repeated re-analysis.
- **VALIDATION.md drafts left non-compliant.** Every phase carries a `nyquist_compliant: false` draft VALIDATION.md; the Nyquist step-hook was inactive so they never gated, but they add audit noise. Either activate the hook or stop emitting the drafts.

### Patterns Established
- **Group the compiler bump with its package bumps.** A compiler-major raise and its ecosystem-package bumps must land atomically — splitting them guarantees a red intermediate state.
- **Every render-layer fix needs a real-render acceptance gate.** Unit asserts on emitted markup missed the admonition bug for months; only a `compile → extract-text → no-leak` gate proves typeset output.
- **Audit-then-publish for irreversible releases.** Run the milestone audit and confirm E2E release-flow readiness *before* the merge/tag/publish that can't be undone.

### Key Lessons
1. **Confirm root cause by reproduction, not changelog.** The `kai` culprit was misattributed for a whole prior milestone; one real compile settled it.
2. **A green unit suite ≠ correct rendered output.** Latent render bugs hide behind markup-level asserts until something actually compiles the output end-to-end.
3. **Split reversible prep from irreversible publish.** Keeping the PyPI/tag/merge step at milestone close, on the confirmed-green commit, makes the point of no return an explicit, auditable gate.
4. **Escalate the full deprecation-warning family.** `PendingDeprecationWarning` (Sphinx's `RemovedInSphinxNN`) must be caught alongside `DeprecationWarning` to see forward-deprecation signals early.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~6 calendar days; wall-clock dominated by push→observe CI runs and repeated sandbox-failure triage.
- Notable: a mid-milestone inserted phase (8.1) absorbed an orthogonal bug without derailing the pin-raise sequence.

---

## Milestone: v0.6.0 — real-world robustness

**Shipped:** 2026-07-13
**Phases:** 5 (11–15) | **Plans:** 15 | **Sessions:** ~2 days (2026-07-12 → 2026-07-13)

### What Was Built
- Issue #114's two fatal figure/image bugs fixed: `_convert_length_to_typst()` (px→pt / CSS-length conversion) wired into `visit_image` (FIG-01), and a caption buffer-swap + `:target:` `refid` branch emitting valid `#figure(link(...)[#image(...)], caption: [...])` (FIG-02).
- The highest-frequency previously-dropped nodes now render correctly and compilably: version directives (VER-01), `refid` cross-references (XREF-01), autodoc `desc_*` signature sub-parts (DESC-01…04), transition/topic/line_block/glossary/tabular_col_spec/abbr (BLK-01…06), and footnotes via a document-order doctree pre-pass with Typst-native `footnote[...]` (FN-01, the one architecturally-new item).
- A graceful-degrade net for out-of-scope graphical nodes (`graphviz`/`inheritance_diagram`): a bordered placeholder + one warning + `SkipNode`, never leaking source or aborting (DEG-01/02).
- A standing real-`typst.compile()` acceptance gate (GATE-01) extended by every node-handler phase, plus the full-corpus gate (GATE-02): Sphinx's own `doc/` tree compiles end-to-end through `typstpdf` with no fatal error (~14.4 MiB PDF, 0 errors), with an `unknown_visit` frequency catalogue and an empty-URL before/after measurement.

### What Worked
- **Fatal-fixes-first sequencing.** Phase 11 landed the Issue #114 fatals *before* any other handler, because a single fatal node aborts the whole PDF — nothing downstream could be validated against a real compile until #114 was green. This mirrors v0.4.4's "land the fix alone" discipline.
- **The real-compile gate earned its keep.** GATE-01's `sphinx-build → typst.compile() → pypdf` methodology caught three *additional* latent fatals that no unit assert would have surfaced: labels attached to code-mode statements, a dangling `:term:` glossary anchor, and a footnote buffer-swap paragraph-state clobber. Each was a real "aborts the whole PDF" bug hiding behind green unit tests.
- **Corpus-as-the-gate.** Making Phase 15 a real build of Sphinx's own full `doc/` tree (not a synthetic fixture) is what turned "we think it's robust" into a measured 0-errors PDF — and it honestly surfaced the long-tail residual (`todo_node`/`manpage`) as backlog rather than pretending zero warnings.
- **Native-model over literal port.** FN-01 used Typst's native `footnote[]` numbering/placement instead of re-implementing docutils' HTML-style backref plumbing — less code, fewer failure modes.

### What Was Inefficient
- **Scope creep into a post-gate polish campaign.** After GATE-02 went green, a same-day "rendering polish" campaign opened 13 non-fatal debug sessions (deflist/desc concat, dangling labels, propagated-target anchors). Valuable work, but it blurred the milestone boundary — it had to be explicitly acknowledged/deferred at close rather than being cleanly scoped as the next milestone from the start.
- **Branch/main drift returned — worse.** The *entire* v0.6.0 milestone (173 commits) accumulated on local `main`, unpushed, while `origin/main` sat at the v0.5.0 merge. This is the exact v0.4.4 lesson ("fast-forward main after each merge") un-applied; a single release PR at close now carries the whole milestone's diff instead of incremental observed-green merges.
- **Sandbox friction, still.** The NixOS `uv`-in-subprocess failures (~45 environment-caused) continued to tax per-phase verification, exactly as in v0.5.0 — still undocumented as a reusable shim.
- **VALIDATION.md drafts still non-compliant.** Every phase again carries a `nyquist_compliant: false` draft; the hook is inactive so they don't gate, but the audit-noise lesson from v0.5.0 went un-actioned.

### Patterns Established
- **Compile-gate every render-layer node handler.** The empirical bar for a node handler is a real `typst.compile()` of a fixture exercising it — extended, not re-invented, per phase. String-agreement asserts never suffice for a tool where one bad node aborts the whole document.
- **Graceful-degrade net for out-of-scope nodes.** Rather than crash or leak source, unsupported graphical nodes emit a visible placeholder + one warning + `SkipNode` — keeps a full-corpus compile usable as a feedback tool.
- **Real-corpus milestone gate.** Validate robustness against a real large downstream project's docs, not a synthetic corpus, and catalogue the residual long tail as explicit next-milestone input.

### Key Lessons
1. **One fatal node aborts the entire PDF — so "does it compile" is the only real correctness signal.** A green unit suite proved nothing here; the compile gate caught every one of the three latent fatals.
2. **A real downstream corpus is the honest robustness test.** Sphinx's own `doc/` tree surfaced both the fixed fatals and the deferred long tail; a synthetic fixture would have flattered the result.
3. **Draw the milestone boundary before polishing.** The 13 post-gate debug sessions should have been scoped as the next milestone at the moment GATE-02 went green, not accumulated against a shipped one.
4. **Apply the fast-forward-main discipline every merge, not at close.** Letting 173 commits pile up unpushed re-created the v0.4.4 drift at 2× scale.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~2 calendar days; the milestone phases (11–15) completed 2026-07-12, with the corpus measurement + polish campaign on 2026-07-13.
- Notable: the standing real-compile gate paid for itself by catching 3 latent fatals that would each have been a whole-PDF abort in a real user's build.

---

## Milestone: v0.6.1 — rendering fidelity

**Shipped:** 2026-07-19
**Phases:** 3 (16–18) | **Plans:** 9 | **Sessions:** ~6 days (2026-07-13 → 2026-07-19)

### What Was Built
- The last two silently-dropped nodes render: `.. todo::` as a gentle-clues `task()` box gated on `todo_include_todos` via `nodes.SkipNode` (TODO-01), and `:manpage:` as italic literal page text via 100% delegation to `visit_emphasis`/`depart_emphasis` (MAN-01) — each proven by a real `sphinx-build → typst.compile() → pypdf` GATE-01 fixture.
- LEN-01: v0.6.0's `visit_image`-local px→pt fix generalized into one shared `_convert_length_to_typst` helper reused at every length-bearing figure/table site via the `block(width: ...)[...]` wrapper.
- AUD-01: a full 151/151-docname human-assisted visual audit of the compiled Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` authority baseline, yielding a severity-rated catalogue of 15 systemic silent mis-render findings (1 high / 12 medium / 2 low), human-confirmed at a central gate (14 accepted / 1 rejected).
- FID-01a/GATE-03: the sole high-severity finding (F12 wide-table glyph collision + right-margin clip) fixed via fr-weighted `columns: (Nfr, …)` from docutils colwidth + in-table U+200B break injection in `visit_literal`, proven by a `wide_table_render_gate` collision-absence fixture; then the full ~684-page corpus re-run fatal-free (689-page `index.pdf`), `unknown_visit` catalogue empty, SC#4 no-new-deps/no-`@preview`-bump invariant held.

### What Worked
- **This milestone *was* the properly-scoped polish campaign.** v0.6.0's lesson #7 ("draw the milestone boundary before polishing") was applied directly: the rendering-quality work that blurred v0.6.0's close was scoped as its own milestone from the start, with a clean discovery→fix→gate arc.
- **Machine-catalogue → single human confirmation gate.** For subjective visual findings, Claude ran the page-by-page pass biased toward false-positives (Phase 17-02), then one human gate (17-03) ruled accept/reject + final severity in a single pass. Clean separation of automated cataloguing from human judgment — the model never had to be the final arbiter of severity.
- **Severity-gated backlog kept DoD bounded.** Only the high-severity finding became a requirement (FID-01a); the 13 medium/low findings were recorded as a single Future-Requirements pointer, not enumerated as 13 requirements — so the milestone shipped without scope-ballooning yet lost nothing.
- **The real-compile gate again proved a fix half-wrong.** fr-weighted columns alone still overflowed on long unbroken dotted API paths; the `wide_table_render_gate` fixture forced the second half (ZWSP break injection), exactly the "compile is the only real signal" pattern from v0.6.0.
- **Discovery-sized Phase 18 honored.** Its plan count was deliberately left TBD until AUD-01 enumerated the fix list — the roadmap didn't pre-commit to a count it couldn't know.

### What Was Inefficient
- **Audit/docs phases don't fit the code-verifier model.** Phase 17 produces a catalogue, not code, so `init.manager` couldn't certify it — forcing an `override_closeout` at milestone close. Its real verification (human gate 17-03 + `17-VALIDATION.md` + downstream FID-01a proof) exists but lives outside the machine `VERIFICATION.md` the readiness check expects. A recurring structural mismatch, not a real coverage gap.
- **The 151-docname visual pass was a long serial human-in-the-loop slog.** Phase 17-02 spanned multiple sessions with explicit stop-discipline resume pointers (docname-by-docname), the single longest-wall-clock activity of the milestone — inherent to a human visual audit, but not parallelizable.
- **VALIDATION.md `nyquist_compliant: false` drafts persisted again.** The same audit-noise lesson carried forward un-actioned from v0.5.0/v0.6.0; the hook stays inactive so they don't gate, but the drafts remain misleading.

### Patterns Established
- **Machine-catalogue → single human confirmation gate** for subjective/visual findings: bias the automated pass toward false-positives, then let one human gate rule accept/reject + final severity. Don't ask the model to be the severity arbiter.
- **Severity-gated backlog:** only high-severity findings are promoted to requirements; medium/low are recorded as a pointer to the catalogue, not enumerated — bounds the definition of done.
- **Verification-by-proxy for audit/docs phases:** a phase whose output is a document (not code) is "verified" by its human confirmation gate + downstream real-compile consumption, closed as `override_closeout` with the proxy chain recorded explicitly.

### Key Lessons
1. **For subjective/visual correctness, separate machine cataloguing from human judgment.** Bias the model's pass toward false-positives and give a human a single accept/reject + severity gate — far more reliable than asking the model to self-certify severity.
2. **Gate the backlog by severity.** Fix high, record low, enumerate only what materially breaks the deliverable as requirements — otherwise polish findings balloon the milestone.
3. **Scope the polish campaign as its own milestone up front** — v0.6.1 validated v0.6.0's hardest-won lesson by doing exactly this.
4. **Audit/docs phases will trip `verified_closeout`** — expect an override and record the proxy verification (human gate + downstream proof) rather than treating the missing `VERIFICATION.md` as a gap.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~6 calendar days (2026-07-13 → 2026-07-19); the 151-docname visual audit (Phase 17-02) dominated wall-clock as a serial human-in-the-loop pass across multiple sessions.
- Notable: the severity-gated catalogue turned an open-ended "make it render better" into a bounded, shippable milestone — 1 high-severity fix + a recorded 13-item backlog, no scope creep.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.4.4 | ~2 days | 5 | First GSD-managed milestone; established push→observe terminal gates and floor+ceiling dependency discipline |
| v0.5.0 | ~6 days | 6 (incl. 1 inserted) | Forward-port to Sphinx 9.1/typst 0.15; added real-render acceptance gates + a mid-milestone inserted phase; audit-then-publish for the irreversible release |
| v0.6.0 | ~2 days | 5 | Translator robustness (Issue #114 + high-freq nodes); standing real-compile gate extended per phase; a real full-corpus (Sphinx `doc/`) build as the milestone gate |
| v0.6.1 | ~6 days | 3 | Rendering fidelity: machine-catalogue → single human confirmation gate for a 151-docname visual audit; severity-gated backlog; first `override_closeout` driven by an audit/docs phase's missing machine verification |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.4.4 | ~400 (existing suite) + `@preview` sync guard | uploaded to Codecov (green) | 0 new runtime deps |
| v0.5.0 | 413 (added smoke gate, PDF-render gate, version drift-guard, admonition structural asserts) | green (13/13 CI jobs on PR #112) | 0 new runtime deps (pypdf is dev-only) |
| v0.6.0 | 476 fast + 18 GATE-01 real-compile classes + corpus gate (`test_corpus_gate.py`) | fast suite green; GATE-02 full-corpus PDF fatal-free | 0 new runtime deps |
| v0.6.1 | + `wide_table_render_gate` real-compile class; todo/manpage/figwidth/table-width GATE-01 fixtures | fast suite green; GATE-03 full-corpus PDF fatal-free, `unknown_visit` catalogue empty | 0 new runtime deps |

### Top Lessons (Verified Across Milestones)

1. Pin the whole dependency graph and commit the lockfile — reproducibility is the anti-rot mechanism. *(v0.4.4)*
2. Sequence changes so a red/green CI result is unambiguously attributable to one change. *(v0.4.4, reaffirmed v0.5.0 — atomic compiler+package bump)*
3. Confirm dependency root causes by reproduction, not changelog inference. *(v0.5.0 — overturned the v0.4.4-era `kai` attribution)*
4. A green unit suite doesn't prove correct rendered output — render-layer fixes need a compile→extract→assert acceptance gate. *(v0.5.0)*
5. Split reversible prep from the irreversible publish; gate the point-of-no-return at milestone close on a confirmed-green commit. *(v0.4.4 precedent, formalized v0.5.0)*
6. For a tool where one bad node aborts the whole output, "does it compile" is the only real correctness signal — compile-gate every render-layer handler against a fixture, and validate the milestone against a real downstream corpus. *(v0.6.0)*
7. Draw the milestone boundary before polishing, and fast-forward `main` after every merge — v0.6.0 re-created v0.4.4's branch/main drift at 2× scale by deferring both. *(v0.4.4, re-learned v0.6.0; validated v0.6.1 — the polish was scoped as its own milestone up front)*
8. For subjective/visual correctness, separate machine cataloguing (biased toward false-positives) from human judgment (one accept/reject + severity gate), and gate the resulting backlog by severity — promote only high-severity findings to requirements. *(v0.6.1)*
