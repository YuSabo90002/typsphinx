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

## Milestone: v0.6.2 — rendering fidelity round 2

**Shipped:** 2026-07-23
**Phases:** 9 (19, 20, 21, 22, 22.1, 22.2, 22.3, 22.4, 23) | **Plans:** 30 | **Tasks:** 65 | **Sessions:** ~4 days (2026-07-20 → 2026-07-23)

### What Was Built
- The 13 medium/low silent mis-render findings the v0.6.1 audit left open, fixed as one coherent `translator.py` series grouped by root cause (clusters A–F): block separation (FID-02..FID-06, Phase 19), intra-signature token spacing (FID-07..FID-09, Phase 20), and the residual inline-literal overflow / paragraph reflow / codly-wrapper leak / external-link styling / PEP-separator hover-title findings (FID-10..FID-14, Phase 21) — each pinned by a fail-pre-fix real-`typst.compile()` GATE-01 fixture.
- Issue #117 target-name PDF fix (PDF-01, Phase 22): one guarded `TypstBuilder._resolve_output_stem()` governs all three `.typ`/`.pdf` output-path sites; and nested-master compile-root alignment (PDF-02, Phase 22.1) so `finish()` compiles each master's own on-disk `.typ` at its real docname-derived location — the compile basis finally matches the translator's emission basis.
- Dead-config sweep + `typst_package` end-to-end repair (CONF-01..CONF-03, Phase 22.2): a *class* of defect closed — a config value registered/documented but inert, kept green by registration-only tests — locked by a standing config→output regression gate.
- Builder-warning hardening (WR-01/WR-02, Phase 22.3): a missing/malformed master now joins the aggregate `ExtensionError` instead of a silent successful build, and the render gate stopped asserting on `typst-py`'s uncontracted error wording.
- Full-text README/CLAUDE.md accuracy pass (DOC-01..DOC-05, Phase 22.4): unverifiable numeric claims *removed rather than re-measured*; a `README`↔`pyproject` version-sync ratchet test added in Phase 23. Closed on the full ~684-page corpus regression gate (fatal-free, valid `%PDF`, `unknown_visit` catalogue empty).

### What Worked
- **Root-cause clustering beat ticket-per-finding.** The 13 audit findings were delivered as 3 root-cause-clustered translator phases (A / B / C-D-E-F) rather than 13 unrelated fixes — one `parbreak()`/`linebreak()`/`pass`-through edit typically resolved several findings in a cluster, and the CHANGELOG collapsed 25 ledger IDs into 12 coherent bullets.
- **The config→output gate closed a defect *class*, not a bug.** Phase 22.2 diagnosed that both dead config values shared one escape — tests asserting registration or doc-presence stay green while the feature is dead — and the fix was a fixture that asserts a config value *changes emitted output*, making the whole class un-shippable-broken going forward.
- **Real-compile revert-and-restore reproduction as verification.** Phase 22.3's verifier didn't trust SUMMARY transcripts — it reverted each fix in place and re-ran the gates to confirm the pre-fix defect reproduces (`IndexError`, silent `returncode==0`), then restored byte-identically. The strongest form of "this fixture has teeth."
- **Honest-verifier abstention over false-green.** The one truth that couldn't be exercised (pytest-xdist parallel safety, no such dependency) abstained to `human_needed` rather than being silently counted as passed — the milestone closed `override_closeout` with the single non-blocking item named explicitly, not papered over.
- **Discovery-driven insertions stayed disciplined.** Four decimal phases (22.1–22.4) were inserted as review warnings and doc-drift surfaced, each sequenced to land before the release phase so every user-visible change made the `[0.6.2]` CHANGELOG — insertion without scope drift.

### What Was Inefficient
- **README drift is a recurring, un-gated tax.** Phase 22.4 existed only because README numeric claims (test count 413→577→589 in days) and Status/methodology lines had silently rotted — the eventual fix was to *delete* the unverifiable claims and add a version-sync ratchet, but the discovery was manual full-text re-reading. The truly valuable automation (`sphinx-build -b linkcheck` CI) was itself deferred as a todo.
- **The requirements traceability status column went stale.** CONF-01..03 / WR-01/02 sat at "Not started" in `REQUIREMENTS.md` even after Phases 22.2/22.3 completed and verified — the status column isn't updated when an inserted phase closes, so milestone close had to reconcile it manually. Cosmetic (the work was done and verified), but a repeat of the "state file doesn't self-update" friction.
- **A code-review scope breach became a same-milestone follow-up.** Phase 22.1's necessary `writer.py` template-import fix (a deliberate CONTEXT fence breach) was then found by review to mis-resolve for a `_template`-named directory, forcing gap-closure plan 22.1-04 — correct outcome, but the breach-then-repair cost a wave that tighter up-front scoping might have avoided.

### Patterns Established
- **Root-cause clustering for audit-derived work:** group N findings by the shared code root cause and deliver one fix series per cluster, not one ticket per finding — collapses both the diff and the changelog.
- **Config→output regression gate:** for any config value, assert it *changes emitted output*, never merely that it is registered or documented — registration-only asserts are the escape that lets a feature ship dead.
- **Revert-and-restore verification:** to prove a regression fixture has teeth, revert the fix in place, confirm the gate goes red with the exact pre-fix symptom, then restore byte-identically (md5-checked) — don't trust the SUMMARY's transcript.
- **Honest-verifier abstention:** a `verification: backstop` truth that can't be exercised with direct evidence abstains to `human_needed` and is named at close as a known override — never silently counted as passed.

### Key Lessons
1. **Cluster audit findings by root cause before planning phases** — one translator edit often resolves several findings, and the milestone ships as a coherent series instead of 13 disconnected tickets.
2. **Gate config on output, not registration.** The dead-config class shipped because every test asserted the value was *registered* or *documented*, never that it *did* anything. A single config→output fixture makes the class impossible to reintroduce.
3. **Prove fixtures have teeth by reverting in place.** Revert-and-restore (byte-identical, md5-verified) is the cheapest way to confirm a regression test actually fails against pre-fix code — worth doing for any load-bearing gate.
4. **Prefer deleting an unverifiable claim to re-measuring it.** README test counts/coverage % with no `fail_under` gate drift constantly; removing them (and ratcheting only the machine-guardable ones like version) beats chasing the number.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~4 calendar days (2026-07-20 → 2026-07-23); worktree-isolated executor mode was the standing execution mode throughout.
- Notable: root-cause clustering kept a 25-requirement milestone to 9 phases / 30 plans, and four discovery-driven decimal insertions (22.1–22.4) landed without scope drift because each was sequenced before the release phase.

---

## Milestone: v0.6.3 — config & docs 実測整合 + captioned tables

**Shipped:** 2026-07-25
**Phases:** 6 (24, 25, 26, 27, 27.1, 28) | **Plans:** 12 | **Tasks:** 28 | **Sessions:** ~3 days (2026-07-23 → 2026-07-25)

### What Was Built
- Dead-config sweep round 2: the registered-but-inert `typst_toctree_defaults` deleted from all seven surfaces (CONF-05, Phase 24), and `typst_elements` `papersize`/`fontsize` finally reaching the template's `project()` via a curated `ELEMENTS_ALLOWLIST` with per-key typing (`papersize` quoted string, `fontsize` an unquoted Typst length through a `RawTypst` marker) and a fail-loud `ExtensionError` on unknown keys (CONF-04, Phase 26).
- External PR#98 reimplemented against current `translator.py` (TBL-01/TBL-02, Phase 25): a captioned `.. table::`/`csv-table`/`list-table` emits `figure(table(...), caption:, kind: table)` with native "Table N" numbering, composed with the existing `:width:` block wrap, and carrying a single collision-free `<label>` so `:numref:`/`:ref:` resolve. Fixed the stale-`table_cell_content`-buffer bug at root, which had been silently eating the second-and-later table's caption.
- Docs 実測整合 (DOC-06/DOC-07, Phase 27): the unreachable orphan `docs/configuration.rst` deleted with its collateral test, five phantom config names purged, and the redundant drifted config table in `api/index.rst` removed so config is documented in exactly one canonical place.
- Typst's typesetting `lang` wired to Sphinx's own `language` conf (CONF-07, inserted Phase 27.1) — a two-line `base.typ` change plus a `derive_typst_lang()` conversion rule, gated to the bundled-default-template path with explicit `typst_elements["lang"]` structurally winning.
- Phase 28 (prep-only) bumped the version, curated the `## [0.6.3]` CHANGELOG entry, and closed on a live full-corpus regression gate.

### What Worked
- **Separating the two config risks into distinct phases paid off.** The captioned-table state-machine work (25) and the `typst_elements` type-mismatch work (26) were deliberately kept in different phases; each shipped its own GATE-01 fixture and neither had to debug the other's failure mode.
- **Ordering the docs phase strictly after the config phase.** Phase 27 could rewrite the phantom `typst_papersize`/`typst_fontsize` lines into *working* `typst_elements` examples because Phase 26 had already shipped the allowlist — the docs fix was a correction, not a deletion.
- **The GATE-01 bar kept catching real defects.** Phase 26's negative unknown-key fixture and Phase 27.1's three non-regression fixtures (custom template / `typst_package` / srcdir shadow each proving no injected kwarg) are what make the fail-loud allowlist and the gated derivation safe to ship rather than merely plausible.
- **Post-merge orchestrator review caught what worktree executors structurally could not.** Phase 27.1's three post-merge defects — a ruff I001/N811 CI break, a `typst_elements = None` TypeError regression, and five new docs-build warnings — were each invisible from inside the executor's own worktree. Re-running the gates on the main tree after merge is not ceremony.
- **A long-standing execution hazard was finally root-caused.** The "45 integration tests fail only in worktrees" problem recurring since Phase 22.1 turned out to be `uv run` resolving a generic-linux ELF `uv` wheel inside the worktree venv that NixOS cannot exec — not the sandbox, not the editable install. One symlink closes it.

### What Was Inefficient
- **The `examples/` directory was invisible to two consecutive phases, and shipped broken.** Phase 26 made unknown `typst_elements` keys fail loud without checking who set them; Phase 27's "anywhere under `docs/source/`" criterion was read as the files the requirement named. The bundled `examples/advanced` sample was therefore unbuildable — and it surfaced only at the milestone close, from a todo, not from any gate. Worse, it had *also* been failing on stale `@preview` pins since v0.5.0 — three milestones of silent drift, because the version-sync guard watched only the three extension-internal surfaces.
- **The same scoping miss happened twice in one milestone.** Phase 27 needed a post-verify gap-closure for phantom names in `docs/source/examples/*.rst` that the discuss/research/plan chain missed. The lesson had already been recorded after that gap-closure — and the `examples/` directory was still missed at the milestone level.
- **No milestone audit was produced.** The close proceeded on Phase 28's live gate re-run standing in. That was defensible for requirement coverage, but the one real defect found at close was found by reading open todos, not by any automated or structured check.

### Patterns Established
- **A curated allowlist that fails loud beats both silent-drop and pass-through** when the downstream contract (a `.typ` `project()` signature) can't be introspected — but it must be paired with a check that everything the repo ships still builds.
- **Precedence should be structural, not incidental:** pre-merge a derived default *under* the user's dict (right-hand-wins union) so "explicit wins" is a property of the data flow rather than of an if-branch that a later edit can invert.
- **Version-sync guards must cover every surface that ships,** not just the ones the extension itself reads. A stale pin in a bundled sample is not cosmetic — it makes the sample fail to compile.

### Key Lessons
1. **When you make something fail loud, grep the whole repo for who was relying on it silently succeeding.** CONF-04's fail-loud allowlist was the right call and immediately broke a shipped example — the cost was not the fix, it was that nothing noticed for two more phases.
2. **"Anywhere under X" in a success criterion means a repo-wide grep at discovery time.** Twice in one milestone, the criterion was checked against the files the requirement named. Naming the files is a hint, not the scope.
3. **Anything the project ships to users should be built by CI, including examples.** The `examples/**/*.typ` version-sync check added at close is a start; actually building `examples/*` would have caught both axes of this defect three milestones earlier.
4. **Verification gates prove the phases did what they said — they do not prove the repo is shippable.** Every phase was `verification_status: passed` and 7/7 requirements were checked off while a bundled sample could not build.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~3 calendar days (2026-07-23 → 2026-07-25); worktree-isolated executor mode throughout, with the `uv` shim hazard root-caused mid-milestone.
- Notable: 6 phases / 12 plans for 7 requirements — the smallest milestone since v0.6.0, and the first where the most valuable finding came from the close's todo audit rather than from a phase.

---

## Milestone: v0.6.4 — Read the Docs migration

**Shipped:** 2026-07-28
**Phases:** 6 (29, 30, 30.1, 31, 32, 33) | **Plans:** 33 | **Tasks:** 79 | **Sessions:** ~4 days (2026-07-25 → 2026-07-28)

### What Was Built
- Documentation hosting moved from GitHub Pages to Read the Docs end to end: English site from `.readthedocs.yaml` + the `READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"` seam (Phase 29), Japanese site from a separate `typsphinx-doc-translations` repository registered as an RTD translation project with an auto-advancing submodule pin (Phase 30.1).
- The RTD-served PDF is `typstpdf`'s own artifact: `formats: [pdf]` + a `build.jobs.build.pdf` override replaces RTD's LaTeX path; the milestone's one open unknown (`@preview` egress from RTD's build sandbox) resolved to Branch A by reading the raw build log, so the pre-agreed `releases/latest/download/` fallback was never needed.
- The Japanese PDF's 10-NUL-byte glyph defect was root-caused to Typst's own font-selection stage (not a missing font) and fixed via a custom template's explicit `("Libertinus Serif", "Noto Serif CJK JP")` — owner visual UAT confirmed, English parent re-measured unregressed.
- The deletion round (Phase 30): `build_multilang.py`, the language switcher, its `conf.py` wiring, six Makefile targets, the `docs-multilang` testenv, `docs/locale/ja/`, and the orphan doc pair with 20 collateral tests — net −6,218 lines of code/config left the repository.
- URL cutover behind a proven guard (Phase 31): advisory lychee `links.yml` recorded red on the unfixed tree first, then all retired-host URLs rewritten and locked by a hermetic regression test; all 35 published URLs fetched over real HTTP; About → Website set.
- The irreversible Pages teardown (Phase 32) ran only behind freshly re-taken same-day evidence that RTD was serving en HTML, ja HTML (content-verified at 1038 CJK chars), and both PDFs; `gh-pages` deleted with `ls-remote` proof, github.io 404 observed live.
- Release prep (Phase 33) with the publish fence proven held; publish executed at `/gsd-complete-milestone` behind a passed milestone audit.

### What Worked
- **Irreversibility-ordering as the roadmap's spine.** Every reversible action preceded the single no-undo one, and the teardown phase carried its own standing gate demanding *freshly re-taken* evidence rather than citations of earlier phases. The URL cutover proved the new links against RTD while both hosts were still live.
- **Content-level criteria caught what status-level criteria structurally cannot.** Both predicted present-as-success failure modes were real: the ja probe had to target 100%-coverage docnames (24.3% overall coverage would have made a healthy site look broken — or a broken site look healthy), and the glyph gate found 10 literal NUL bytes in a PDF that built green.
- **Negative controls everywhere.** The link guard was recorded red before the rewrite; the docs.yml guard tests got a recorded red run; the `--dump-inputs` diagnostic proved pyproject.toml in-scan. A guard first seen green proves nothing.
- **Pre-agreeing the fallback for the one empirical unknown.** Phase 29 could not deadlock on the `@preview` egress question because both branches were expressible in its success criteria and the owner had decided the fallback in advance.
- **The milestone audit returned — and the close was the first verified_closeout since v0.4.4.** v0.6.3's lesson (its one real defect was found by a side question, not a gate) was applied: a 3-source requirements cross-reference + integration checker ran before the publish.

### What Was Inefficient
- **Phase 30.1 consumed 11 of the milestone's 33 plans**, including a five-plan gap-closure round (07–11) after its first verification scored 3/5: the pin-bump workflow had a missing branch-fetch root cause, and the glyph defect needed a forensic diagnosis round plus an owner decision before the fix. Real defects, but the phase was scoped as if the happy path would hold.
- **The milestone's repository model was replaced mid-flight.** The original brief re-imported the same repository twice; the `sphinx-doc-translations` separate-repo model was adopted on 2026-07-26, forcing the 30.1 insertion, an I18N requirement split, and three owed post-merge flips (two RTD Default-branch settings + `.gitmodules`). Measuring RTD's actual translation model (15/15 sphinx translations are separate repos) *before* scoping would have avoided the churn.
- **The `api-coverage.verify-pre` gate false-positived three times** (Phases 30, 30.1, 31) on prose *describing* RTD API reads as evidence, each requiring a recorded override. The detector matches disclaimer text that exists precisely to say "this is not an API integration."
- **A handful of SUMMARY one-liner frontmatter fields were broken or empty** ("the owner created the empty"), which polluted the auto-generated MILESTONES entry and had to be curated away at close.

### Patterns Established
- **Two-repository release set:** every release now tags the parent *and* `typsphinx-doc-translations` — `/ja/stable/` resolves against the translations repo's own tags. Omitting it leaves ja stuck/404 while en works: exactly the partial-success failure mode the milestone's invariants exist to catch.
- **The no-undo action gets its own phase with a standing, freshly-re-taken gate** — never folded into a neighbour, never satisfied by citing earlier evidence.
- **Owner-manual web-UI steps carry no pretend-automatable criteria**: phases verify outcomes via real fetches, and the human half is recorded as owner-observed or handed off explicitly.

### Key Lessons
1. **When a failure mode presents as a successful build, pick probe targets for sensitivity.** A translated-content probe against a 0%-coverage docname, or a PDF byte-size check without text extraction, would have passed on broken output. Both real defects this milestone were only visible to content-level checks aimed at known-sensitive targets.
2. **Measure the platform's actual model before scoping a migration onto it.** The re-import-twice plan died on contact with RTD's measured translation model; the replacement was visible in the platform's public API the whole time.
3. **Cross-repository coupling needs an observed end-to-end run, not a plausible workflow file.** The pin-bump automation failed on its first real trigger (missing branch fetch under `--depth=1`); only the observed run surfaced it.
4. **Run the milestone audit.** It cost one session and produced the first fully-verified close in five milestones; the alternative (v0.6.3) shipped an unbuildable sample.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~4 calendar days (2026-07-25 → 2026-07-28), 290 branch commits; worktree-isolated executor mode throughout.
- Notable: 6 phases / 33 plans / 79 tasks for 13 requirements — plan count dominated by 30.1's gap-closure round; the code delta is net-negative (−6.2k lines), the first milestone whose main deliverable is infrastructure that lives mostly *outside* this repository.

---

## Milestone: v0.6.5 — inline-math separator hotfix

**Shipped:** 2026-07-29
**Phases:** 2 (34, 35) | **Plans:** 8 | **Tasks:** 27 | **Sessions:** ~2 days (2026-07-28 → 2026-07-29)

### What Was Built
- One defect fixed and released. A paragraph mixing prose and math emitted Typst with no valid separator before the `mi(...)` / `$...$` call, so `typst.compile()` aborted — the build died on a document a user can legitimately write.
- Phase 34 root-caused it **by measurement**: the backlog note blamed "`translator.py` math/Text visit ordering," but `visit_math` already called `_add_paragraph_separator()`. The real cause was a *scope gap* — that helper is deliberately a no-op inside list items (`visit_paragraph` never sets `in_paragraph` there) and inside the five code-mode concat contexts, so math after a sibling juxtaposed with zero separator characters. The fatal therefore surfaced in list items, definition-list terms, and collapsed confval field bodies, never in a plain paragraph.
- Fixed by applying the already-tested `visit_literal` pattern to the one visitor pair never retrofitted: `visit_math` now participates in all three separator protocols, `visit_math_block` in the list-item half only (D-01 — a block node is never a concat-context sibling). Zero new helpers; the mitex/native branch, the `_convert_latex_to_typst` call, and label-anchor emission are byte-unchanged.
- Pinned by a real `typst.compile()` GATE-01 fixture covering five constructs on both the mitex default and `-D typst_use_mitex=0` native paths, recorded RED against the unfixed translator with the verbatim `TypstError: expected semicolon or line break` captured — then independently re-reproduced RED at verification time by restoring the pre-fix translator.
- Phase 35 was prep-only: version bump in lockstep, a curated `## [0.6.5]` CHANGELOG entry with the tail link-block rollover, Phase 34's three test-side review Warnings closed, and the milestone invariants asserted mechanically over the SHA-anchored full diff. It took no irreversible action — proven by empty `git tag -l` / `git ls-remote --tags` observed at two separate moments.

### What Worked
- **Treating the backlog note as a hypothesis, not a finding.** The note's premise was checkable and false, and the check was cheap. Fixing the named suspect would have changed nothing; the real cause is not reachable from the guess. The roadmap made this explicit up front ("the root cause is NOT yet known — Phase 34 must measure it before fixing it"), which is why the phase's first plan was a reproduction rather than a fix.
- **Pattern reuse over new abstraction.** The fix is +45 lines with no new helper, because the separator protocols already had a worked example in `visit_literal`. Non-regression came out clean on a set-comparison against the pre-fix baseline (NEW-failures empty).
- **The prep/publish fence, proven rather than asserted.** Phase 35 could state exactly what it had *not* done and back it with two independent empty-tag observations, so the close inherited an unambiguous starting state and nothing needed unwinding.
- **Deliberate deferrals filed as records.** Both things consciously not done (WR-01's cosmetic blank line, the `release.yml` release-notes rework) became todo files during the phase that decided them, so the close had nothing to reconstruct from memory.
- **Scope held absolutely.** Two requirements in, two requirements out, in two days — the fastest milestone to date and the first with zero scope drift of any kind.

### What Was Inefficient
- **The release phase was larger than the fix: 5 of 8 plans.** Three of those five (35-01 closing WR-02/03/04, 35-02 filing todos) were Phase 34 cleanup that landed in Phase 35 because Phase 34's code review ran after its verification. Fixture coverage gaps found by review are Phase 34's work; they arrived one phase late and inflated the release phase.
- **A second consecutive audit-less close in three milestones.** The decision was defensible here (2 phases, 2 requirements, seven live runs already recorded), but v0.6.3 is the standing counter-example, and "the milestone is small" is exactly the reasoning that preceded it.
- **RESEARCH.md carried a wrong caution.** It warned that WR-04's candidate assertion string needed a spacing fix; measurement showed `visit_math_block`'s native branch intentionally emits `$ E = m c^2 $` with interior spaces — a different code path from inline math's space-free form. Second time this milestone that a prior text's claim about the code was overturned by reading the code.
- **`phase.complete` auto-flipped REL-03's checkbox** against the phase's own explicit decision (D-10: prep completion is not a publish), and had to be reverted before commit — a known tool behavior that costs a diff review at every release phase.

### Patterns Established
- **A backlog item's stated cause is an unverified claim.** Promote the *symptom* into the requirement and make the first plan a reproduction that captures the emitted artifact and the verbatim error. The requirement text here said so explicitly, and it paid.
- **When a bug appears in some containers and not others, suspect protocol participation, not ordering.** Three separator protocols existed; a visitor participating in one of them looks correct in the common case and fails only inside the containers the other two govern.
- **The release phase's evidence document names what it did not do, with a mechanical proof.** `35-HANDOFF.md`'s "Not done in this phase, by design" list plus the empty-tag observations is now the standard shape.

### Key Lessons
1. **Root-cause by measurement even when a plausible cause is written down.** Two independent prior texts (the backlog note and RESEARCH.md) each made a specific, checkable, wrong claim about the code. Both were cheap to check and expensive to trust.
2. **Run the code review before the phase's verification closes, not after.** Every warning it raises that needs work becomes a plan in the *next* phase otherwise — here, 3 of the release phase's 5 plans.
3. **A no-op guard is not a safe default.** `_add_paragraph_separator()` returning silently inside list items is why this bug was invisible for so long: the call site looked correct and the failure only appeared in containers nobody tested.
4. **Small milestones are where audit discipline actually erodes.** The reasoning that skips the audit scales with how obviously fine the milestone looks.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~2 calendar days (2026-07-28 → 2026-07-29), 72 branch commits; worktree-isolated executor mode throughout.
- Notable: the smallest milestone to date by every measure — 2 phases, 8 plans, 8 files changed, +560/−4 lines, of which the runtime change is 45 lines in one file. The proportion is the story: a 45-line fix carried 515 lines of fixture, evidence, and release scaffolding.

---

## Milestone: v0.7.0 — API rendering design overhaul

**Shipped:** 2026-08-04
**Phases:** 8 (36, 37, 38, 39, 40, 40.1, 41, 42) | **Plans:** 57 | **Tasks:** 158 | **Sessions:** ~7 days (2026-07-29 → 2026-08-04)

### What Was Built
- API reference pages became readable. Signatures moved from `strong({text("class") text(" ") …})` — proportional bold, never monospace — to a composed `block(sticky: true, par(hanging-indent: 2.5em, …))` with every text run routed through Typst's `raw(...)` primitive, ZWSP break opportunities injected so long identifiers wrap instead of overflowing the 453.54pt production column, italic-proportional parameters distinct from the name, and a real `→` glyph (SIG-01..SIG-09).
- Structure became visible. `visit_desc_content`/`depart_desc_content` were **both `pass`** before this milestone; they now emit a real `pad(left: SHARED_INDENT_STEP)` wrapper, with `field_list` nesting its own pad inside it, one named constant driving both, and no depth counter (the trap the fix deliberately avoids). A nested member's signature aligns with its parent's body rather than taking a further step (IND-01..05, FLD-01..03).
- Admonitions were re-bucketed and centralized: ten types onto `sphinx.locale.admonitionlabels` through the single escaping helper, `seealso` and `attention` the two that moved, generic `.. admonition::` rendering as a styled titled box, and a rubric inheriting its container's indent (ADM-01..06).
- Citations went from **zero handlers and a guaranteed compile abort** to a full round trip: a run of consecutive definitions renders as one `grid(columns: (auto, 1fr))`, `[Label]_` links resolve, back-references follow docutils' own `backrefs` order and same-document scope, and `examples/charged-ieee/` got its citation syntax back (CIT-01..06). Phase 40.1 then hardened the degradation paths that `40-REVIEW.md` found.
- Two compile fatals closed: MATH-02 (block math in a list item armed a separator flag the handler already satisfied) and TBL-03 (a captioned table's propagated-target anchor was written into a buffer that got `del`eted).
- The release surface changed shape: `release.yml` now builds the GitHub Release body from the curated `## [0.7.0]` CHANGELOG section via a stdlib-only positional extractor, replacing a ~296-line `git log` dump — the first release in this project's history whose notes a maintainer actually wrote (REL-04, REL-05).

### What Worked
- **The redefined RED held under pressure instead of being laundered.** Every prior GATE-01 fixture in this project proved a compile fatal, but every design defect here *compiled fine today*, so milestone invariant #4 required a structural / regex / `pypdf`-text assertion written before any code. The test came in Phase 40: four of nine gate selectors stayed RED after the handlers landed, and all four turned out to be defects in the gate module itself (a stale Sphinx API keyword, a line-vs-marker column confusion, a bracket-intolerant concat check, an anchor helper recognising only one of two emitted forms). Because "edit the test until it passes" is indistinguishable from laundering the gate, the corrected module was restored over the pre-fix translator and re-proved 9/9 RED **three independent times** — by the fixing plan, the orchestrator, and the verifier.
- **A locked decision was reversed on evidence rather than defended.** Phase 39 had closed 5/5 verified when conversational UAT put a live A/B/C render in front of the owner, who overturned D-03 and split the collapsed red admonition bucket into three distinct clue functions. The closed-phase gate was overridden deliberately; plans 39-09..39-13 closed it with a fresh RED, a re-taken ADM-04 sign-off against post-reversal code, and a re-run corpus gate.
- **Byte-identity as an acceptance criterion.** Phase 36's decoupling had no observable behaviour to assert, so its criterion was an empty diff between two real `sphinx-build` runs at named commits — with the golden captured *before* any decoupling edit existed (`git log --follow` proves one commit on that path, predating the change), so the proof is not circular.
- **Measurement inverted the phase's own premise, and the phase adapted instead of pretending.** SIG-07 assumed real signatures overflow. The corpus (1,445 real `desc_signature` nodes) has a 311-char worst case and a 143pt widest unbreakable token against a 453.54pt column read from Typst's own `layout()`/`measure()` — nothing overflows. The RED fixture became synthetic and the corpus worst case became a non-regression control.
- **A known tooling hazard was converted into a falsifiable check.** `phase.complete` auto-flipping REL-04/REL-05 against a CONTEXT decision was caught and reverted in Phase 41; Phase 42 then wrote `42-CLOSEOUT-GUARD.md` recording the four at-risk lines verbatim with a file checksum, so the post-close diff compares against a baseline instead of someone's memory. It did not recur.

### What Was Inefficient
- **Gap-closure rounds became normal rather than exceptional.** Phases 37, 38, 39, and 40 each needed one: 37-09/37-10 (a `0pt` block override that produced the overlap defect its own re-measurement then disproved), 38-09 (FLD-02 held at top level but regressed inside list items because `visit_paragraph` tested `in_list_item` first), 39-09..39-13 (the D-03 reversal), 40-05 (the four gate-module defects). 57 plans for 33 requirements is close to 2:1, and most of the excess is re-work found *after* a phase's verification passed.
- **Code review kept landing after verification.** The same ordering problem v0.6.5 named is still here: Phase 42's review findings (WR-01's stale docstring, IN-02's nested-table state clobber) arrived after the SC#4/SC#6 evidence had been recorded, so fixing WR-01 in-phase would have moved the change outside the SHA range that evidence measured. Both became todos instead of fixes.
- **A third consecutive `override_closeout` with no milestone audit.** The reasoning was stronger this time (8/8 phases verified, 31/33 requirements already Complete before the close began), but v0.6.3 remains the standing counter-example where the close's own todo audit — not any gate — found the milestone's one real defect.
- **A requirement was added to an already-complete milestone.** TBL-03 was promoted out of backlog 999.2 on 2026-08-03 after Phase 41 had closed, which forced Phase 42 to carry reconciliation debt Phase 41 would otherwise have owned: the curated CHANGELOG entry gained no TBL-03 line on its own, and SC#4's invariant sweep had been measured over a SHA range ending before Phase 42. It worked, but only because Phase 42's SC#6 was written to own exactly that.
- **The CHANGELOG's release date went stale for a day** because it was written in Phase 41 and the milestone did not ship until Phase 42 landed — surfaced as an open owner question by 42-06 and corrected at the close.
- **The milestone branch was never pushed until the release PR, and both defects found at the close were invisible until it was.** The Windows lanes went RED immediately on PR #129 — three Phase 37 signature render-gate modules read `.typ` with a bare `Path.read_text()`, and Windows' cp1252 default cannot decode UTF-8 (820 passed / 1 failed; Linux and macOS fully green). Then the real tag push failed at `create-release` with `uv: command not found`: REL-04 had wired `uv run python scripts/extract_changelog_section.py` into the one release job with no `astral-sh/setup-uv` step. PyPI published; the GitHub Release did not. Eight phases of green local runs, and neither Windows CI nor a tag push had touched the branch once.

### Patterns Established
- **When the defect compiles, define RED before writing code and never regenerate expected strings from the new code's output.** Derive GREEN strings by hand from the recorded RED strings.
- **A gate that goes green after you edit the gate must be re-proved able to fail.** Restore it over the pre-fix code and re-observe RED, ideally by more than one party.
- **A design phase's success criteria split by `[M]`/`[V]`.** Mechanically checkable structural properties (emitted through `raw(...)`; a nested member's left edge strictly greater than its parent's, via `pypdf` bounding boxes) versus explicit owner sign-off for aesthetic judgement — and the sign-off is recorded verbatim, with its caveats, not summarized.
- **Evidence for an absence needs two probes separated in time.** The prep/publish fence was proven by empty `git tag -l` / `git ls-remote --tags` observed 2m44s apart, at two separately-recorded moments.
- **Record a known tooling hazard as a baseline, not a warning.** `42-CLOSEOUT-GUARD.md`'s verbatim lines + checksum is the shape.

### Key Lessons
1. **Redefining what "red" means is a design decision that has to be made up front, per milestone.** "Does it compile" carried every prior milestone; it carries nothing when the defect is that correct-compiling output looks wrong.
2. **A test that turns green after you edited the test is not evidence until it is re-proved able to fail.** Four of nine selectors in Phase 40 were gate defects, not translator defects — indistinguishable from laundering without the restore-and-re-observe step.
3. **Re-open a verified phase when a live render overturns a locked decision.** The cost of 5 extra plans was lower than shipping a taxonomy the owner had just rejected on sight.
4. **Run the code review before verification closes.** Third milestone in a row where review findings became next-phase work or todos because they arrived after the evidence was sealed.
5. **Promoting work into a milestone after its release phase has closed creates reconciliation debt.** It is payable — but only if the inserted phase's own criteria explicitly own the prep artifacts that were measured before it existed.
6. **Push the milestone branch early even without opening a PR.** A branch that only meets CI at the release PR has had zero cross-platform coverage for the whole milestone; the cp1252 failure was eight phases old when it was found.
7. **A workflow change is not delivered until a real trigger has run it.** REL-04's extractor was hand-run, pytest-covered, and statically read — and still failed on the one thing static reading cannot check: whether the *job* that calls it has the tool on PATH. Deliverables whose only real exercise is an irreversible event need either a rehearsal trigger or an explicitly-open requirement until that event happens.
8. **At a close that performs a publish, flip publish-gated requirements after the run is green, not before it starts.** Phase 41 was right that prep completion is not a publish; the close then flipped both REL rows before the release run and had to flip REL-04 back.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~7 calendar days (2026-07-29 → 2026-08-04), 477 branch commits; worktree-isolated executor mode throughout.
- Notable: the largest milestone to date by every measure — 8 phases, 57 plans, 158 tasks, 80 files and +14,619/−339 lines outside `.planning/`. The ratio inverted from v0.6.5: where that milestone was 45 runtime lines carrying 515 lines of scaffolding, this one is a genuine redesign, and the scaffolding (gate modules, fixtures, evidence files) is roughly proportional to it rather than dominating it.
- Release-day cost not visible in the phase counts: two defects surfaced only once the branch met real CI (one Windows encoding bug, one broken release job), one hand-repaired GitHub Release, and one requirement carried to v0.7.1.

---

## Milestone: v0.7.1 — bug-fix round

**Shipped:** 2026-08-11
**Phases:** 8 (43, 44, 44.1, 44.2, 45, 45.1, 45.2, 46) | **Plans:** 43 | **Tasks:** 122 | **Sessions:** ~8 days (2026-08-04 → 2026-08-11)

### What Was Built

- `typst_documents` gained a default derived from `root_doc`/`project`/`author`, mirroring `sphinx.builders.latex.default_latex_documents`, so following the Quick Start produces a real PDF instead of exiting 0 with a warning and zero output. A target name that slugifies onto an existing docname now falls back with a WARNING instead of silently destroying content (CONF-08, DOC-11).
- An explicit `typst_documents` entry's `[2]` title and `[3]` author reach the compiled PDF's metadata, overriding `project`/`author` as LaTeX does, backed by a 27-test precedence matrix including the multi-master no-leak property (CONF-09).
- `translator.py`'s table and figure state moved from flat scalars to snapshot save/restore stacks, plus a new `legend` handler: a table nested in a `list-table` cell no longer replaces the outer table's body, and a figure nested in a figure's legend no longer aborts the compile or drops the outer caption. `depart_table`'s captioned check split into independently-gated RENDERING and ANCHORING decisions so an empty-titled caption still anchors its ids. `visit_title` emits relative depth so toctree'd headings nest (TBL-04, TBL-05, FIG-01, TOC-01).
- The published custom-template parameter contract was rewritten onto the nine parameters typsphinx actually passes and locked with a RED-proved gate; a declared `typst_template_function` `params` dict became the complete parameter set; the auto-derived `lang` reached every non-package template route; `typst_authors` was removed outright (DOC-13, CONF-10, CONF-11, CONF-12).
- `docs/source/changelog.rst` now renders live from repo-root `CHANGELOG.md` via myst-parser, closing at its source the drift channel that had left the page frozen at 0.4.0 for two years (DOC-12).
- `tox` ran on the maintainer's machine for the first time: renaming `tox-uv` to `tox-uv-bare` dropped the bundled generic-linux `uv` wheel NixOS cannot exec (QUA-04).
- Issue #130 / PR #131 (@christianwehe) merged — the project's first external contribution — fixing absolute image URIs from Sphinx's image converter and downloader.

### What Worked

- **Milestone invariant #5 paid on its first outing.** v0.7.0's post-mortem identified one shared cause for both of its release-day defects: the branch was never pushed until the release PR. v0.7.1 made "push from Phase 43" a success criterion, and Phase 46 caught a Windows-only path-separator defect on a dispatched CI run instead of at the release PR.
- **Fixing the root cause dissolved five carried items instead of deferring them again.** The Phase 45.1 deferred items were five test modules failing under the `uv run` invocation `CLAUDE.md` mandates. QUA-04 renamed one dependency and the full suite went from 45 failures to zero — so the close re-measured them and found nothing to defer.
- **Prep-only Release phases keep proving their worth, and the guard around them keeps firing.** Phase 46 held REL-04/REL-06 at `[ ]` through every plan; `phase.complete` auto-flipped REL-06 and auto-closed the REL-04 todo at close-out anyway, and the diff-before-trusting guard caught both. Three-for-three on release-prep phases now.
- **A requirement that could only be proved by the publish was, in fact, only proved by the publish.** REL-04's close is release run `31462027486`'s `create-release` job, plus a `diff` showing the published body byte-identical to the extractor's output. Nothing about the workflow file's correctness was accepted as evidence.
- **Small inserted phases beat widening an existing one.** Four of eight phases were insertions (44.1, 44.2, 45.1, 45.2), each carrying exactly one coherent defect family, and each closed on its own gates rather than diluting a neighbour's.

### What Was Inefficient

- **CONF-09 needed four verification rounds, and the last three failed on published prose rather than on code.** The implementation was right early; what kept failing was `configuration.rst`'s description of the precedence rule — first stated as a package-route condition, then as a `map_parameters()`-scoped rule, before the frame widened to the whole pipeline. A documentation claim about behaviour is as verifiable as the behaviour and should have been derived from the code the first time.
- **Phase 45.1 grew from one requirement to four at its own discussion.** The contract correction (DOC-13) turned out to be unfixable without three behaviour changes (CONF-10/11/12). Better discovery at roadmap time would have scoped it that way from the start rather than amending mid-milestone.
- **Two plans independently wrote an unsatisfiable acceptance command.** `git diff origin/main..HEAD -- typsphinx/` cannot be empty under `branching_strategy: milestone` — the merge-base predates the milestone. Both plans hit it, and both had to correct the anchor at execution time.
- **CONTEXT.md's "13 test modules" and "unfixable NixOS false positives" were both wrong**, and a whole phase's framing rested on them until plan 45.2-03 ran an actual grep (5 modules) and measured the actual cause (fixable).

### Patterns Established

- **A defect that ships unfixed gets its counter-case argued in writing before it is declined.** D-27's two `_track_image` defects were declined only after the full case for fixing them — regression in failure mode, reachability, the `CHANGELOG.md:817` `### Known Limitations` precedent, an empty public issue tracker — was written out and answered.
- **Every pending todo is dispositioned in the release-prep phase, in writing.** `46-HANDOFF.md` § "Deferred by decision, not oversight" names all nine with a reason each, and re-measures the ones whose status might have changed — one was reproduced live as still-reachable, two were found already delivered and filed to `completed/`.
- **When CI dispatch surfaces an unrelated pre-existing failure that blocks the task's own zero-failure bar, fix it in a separate clearly-scoped commit and re-dispatch** — never absorb it into the task's primary commit.
- **Documentation claims get their own cross-page gate.** `tests/test_docs_contract_claims_gate.py` closed the single-page-enumeration hole that let a stale claim survive a correction pass, and its `.as_posix()` normalization made the comparison platform-independent.

### Key Lessons

1. When a milestone's own post-mortem names a structural cause, encode it as a success criterion in the next roadmap rather than as a note — v0.7.1 turned "the branch was never pushed" into Phase 43's SC#5, and it caught a real defect.
2. Prefer the root-cause fix that dissolves a class of deferred items over the local workaround that repairs one symptom — `tox-uv-bare` versus `TOX_UV_PATH` was one dependency name against a NixOS-local patch, and it retired five carried items.
3. A requirement whose evidence is generated by an irreversible action must not be flipped before that action succeeds — and the tooling will try to flip it for you, so diff before committing the close.
4. Published prose describing behaviour is a claim about code and needs to be derived from the code, not written alongside it — CONF-09 passed its implementation gates on round 1 and its documentation gates on round 4.
5. Re-measure carried "deferred items" at close rather than transcribing them forward; five of this milestone's twelve open artifacts had already been resolved by a later phase.

### Cost Observations

- Model mix: adaptive profile (`model_profile: adaptive`) — opus for discussion/planning/verification, sonnet for execution.
- Sessions: ~8 calendar days (2026-08-04 → 2026-08-11), 421 branch commits; worktree-isolated executor mode throughout.
- Notable: 125 files and +10,760/−935 lines outside `.planning/`, but the balance is inverted from v0.7.0 — five of the eight largest changed files are new gate modules (`test_params_exclusivity_gate.py` 751 lines, `test_authors_pipeline_stage_gate.py` 614, `test_nested_table_render_gate.py` 577, `test_entry_metadata_precedence.py` 540, `test_docs_contract_claims_gate.py` 477) against 611 lines of `translator.py` change. A bug-fix milestone over already-diagnosed defects spends most of its budget proving the fixes stay fixed.
- Release-day cost: **zero defects surfaced at the publish**, against v0.7.0's two — the first close in this project's history where the release ran clean end to end on the first attempt.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.4.4 | ~2 days | 5 | First GSD-managed milestone; established push→observe terminal gates and floor+ceiling dependency discipline |
| v0.5.0 | ~6 days | 6 (incl. 1 inserted) | Forward-port to Sphinx 9.1/typst 0.15; added real-render acceptance gates + a mid-milestone inserted phase; audit-then-publish for the irreversible release |
| v0.6.0 | ~2 days | 5 | Translator robustness (Issue #114 + high-freq nodes); standing real-compile gate extended per phase; a real full-corpus (Sphinx `doc/`) build as the milestone gate |
| v0.6.1 | ~6 days | 3 | Rendering fidelity: machine-catalogue → single human confirmation gate for a 151-docname visual audit; severity-gated backlog; first `override_closeout` driven by an audit/docs phase's missing machine verification |
| v0.6.2 | ~4 days | 9 (incl. 4 inserted) | Rendering fidelity round 2: audit findings clustered by root cause into 3 translator phases; config→output regression gate closed a dead-config *class*; revert-and-restore fixture verification; `override_closeout` driven by an honest-verifier backstop abstention |
| v0.6.3 | ~3 days | 6 (incl. 1 inserted) | Config & docs 実測整合: fail-loud curated allowlist replaced silent config drops; risks split across phases by failure mode rather than by feature; the worktree `uv` exec hazard root-caused; `override_closeout` with no milestone audit — and the milestone's one real defect (an unbuildable bundled example) found by the close's todo audit, not by any gate |
| v0.6.4 | ~4 days | 6 (incl. 1 inserted) | Read the Docs migration: first hosting/infra milestone with a zero-`typsphinx/`-change invariant (held); irreversibility-ordered roadmap with the no-undo action isolated behind a freshly-re-taken gate; content-level criteria for present-as-success failure modes; milestone audit returned → first verified_closeout since v0.4.4 |
| v0.6.5 | ~2 days | 2 | First single-defect hotfix milestone: the requirement text itself mandated measuring the root cause before fixing it, and the backlog's stated cause was overturned; smallest milestone to date (8 plans, 45 runtime lines) with zero scope drift; `override_closeout` with no audit, the second in three milestones |
| v0.7.0 | ~7 days | 8 (incl. 1 inserted + 1 promoted from backlog after the release phase closed) | First typography/design milestone: GATE-01's RED redefined per-milestone (structural/`pypdf` assertions before any code, since the defects compile fine) and proved un-launderable by restore-and-re-observe; a locked decision reversed on a live render, re-opening an already-verified phase; a recurring tooling hazard converted into a checksummed baseline; largest milestone to date (57 plans) with a ~2:1 plan-to-requirement ratio driven by gap-closure rounds; third `override_closeout` in four milestones; **first milestone to ship with a known gap** (REL-04) — the release automation it built failed on its own first real tag push |
| v0.7.1 | ~8 days | 8 (incl. 4 inserted) | First maintenance milestone scoped entirely from already-diagnosed defects, each carrying a file/line-level todo or a measured basis: half the phases were insertions, each one coherent defect family. The prior milestone's post-mortem cause became a success criterion (invariant #5, push from Phase 43) and caught a Windows-only defect in-milestone. A root-cause toolchain fix dissolved five carried deferred items instead of deferring them again. Fourth consecutive `override_closeout`; **first milestone to close with zero known gaps and zero release-day defects** — REL-04, carried unmet from v0.7.0, closed on evidence the publish itself generated |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.4.4 | ~400 (existing suite) + `@preview` sync guard | uploaded to Codecov (green) | 0 new runtime deps |
| v0.5.0 | 413 (added smoke gate, PDF-render gate, version drift-guard, admonition structural asserts) | green (13/13 CI jobs on PR #112) | 0 new runtime deps (pypdf is dev-only) |
| v0.6.0 | 476 fast + 18 GATE-01 real-compile classes + corpus gate (`test_corpus_gate.py`) | fast suite green; GATE-02 full-corpus PDF fatal-free | 0 new runtime deps |
| v0.6.1 | + `wide_table_render_gate` real-compile class; todo/manpage/figwidth/table-width GATE-01 fixtures | fast suite green; GATE-03 full-corpus PDF fatal-free, `unknown_visit` catalogue empty | 0 new runtime deps |
| v0.6.2 | 567 passed; + cluster A–F translator GATE-01 fixtures, target-name / nested-master / package-only / missing-malformed-master gates, config→output regression gate, `README`↔`pyproject` version-sync ratchet | fast suite green; full-corpus PDF fatal-free, `unknown_visit` empty | 0 new runtime deps |
| v0.6.3 | 657 passed / 1 skipped; + captioned-table GATE-01 fixtures (2+-table, caption+width, `:numref:`), four `typst_elements` config→output fixtures incl. a negative unknown-key and a copyright-non-leak, `test_typst_lang_gate.py` (18 tests / 7 real-compile fixtures incl. 3 non-regression template paths), and a fourth-surface `@preview` sync check over `examples/**/*.typ` | full suite green; full-corpus PDF fatal-free, `unknown_visit` empty; `sphinx-build -b typstpdf examples/advanced` builds | 0 new runtime deps |
| v0.6.4 | 647 passed / 1 skipped (net down: 20 collateral tests deleted with their orphan subjects); + `.readthedocs.yaml` structural tests, `_resolve_language()` seam tests, stale-URL regression guard (`test_no_stale_github_io_links.py`), two docs.yml guard tests with recorded red negative controls, advisory lychee `links.yml` | full suite green; live RTD verified serving en+ja HTML and both `typstpdf` PDFs | 0 new runtime deps |
| v0.6.5 | 649 passed / 1 skipped; + `inline_math_after_text_render_gate` (5 constructs × both emission paths, recorded RED pre-fix and re-reproduced RED at verification) and four exact-string assertions derived from real `sphinx-build -b typstpdf` output | full suite green; full-corpus PDF fatal-free; 93-page docs dogfooding PDF; both `tox -e docs-html` / `docs-pdf` green on the post-bump tree | 0 new runtime deps |
| v0.7.0 | 821 passed / 1 skipped (up from 649); + per-sub-part signature gates (14 SIG-01..05 structural REDs + a determinism control), two Typst-probe geometric render gates (SIG-07 overflow, SIG-09 page boundary), a 13-assertion `pypdf` layout-mode desc-content indent gate, a 20-test field-body typography gate, region-scoped `.typ`+compiled-PDF admonition gates, an ADM-04 greyscale render pipeline (pillow, dev-only), a 9-selector citation render gate re-proved 9/9 RED against the pre-fix translator, the frozen `examples/charged-ieee` sample gate, a 9-test TBL-03 captioned-table gate plus a 7-method figure-side non-regression gate, and pytest coverage for the CHANGELOG-section extractor | full suite green; full-corpus `-b typstpdf` gate executed and PASSED (not skipped) at every phase close; both docs dogfooding builds green incl. the `ja` CJK glyph bar | 0 new runtime deps (pillow is dev-only) |
| v0.7.1 | 976 passed / 0 failed (up from 821); + `test_nested_table_render_gate.py` (7 nesting shapes, classic-`TypstError` RED), a figure-legend gate incl. the legend-in-legend leak its own code review found, `test_entry_metadata_precedence.py` (27 tests — full title/author precedence matrix + multi-master no-leak), `test_params_exclusivity_gate.py` and `test_authors_pipeline_stage_gate.py` (CONF-11's exclusivity rule proved by real build on all three template routes, RED recorded from a detached worktree at the true pre-fix commit), `test_documented_params_contract_gate.py` (the nine-parameter contract locked, RED-proved), `test_docs_contract_claims_gate.py` (cross-page claim guard, platform-independent via `.as_posix()`), `test_toolchain_config_gate.py`, a changelog-page gate proving all 12 previously-missing releases render clean on both builders, and a quickstart-default no-skip gate binding CONF-08 to a real `-b typstpdf` build | full suite green; full-corpus `-b typstpdf` gate executed and PASSED; both docs dogfooding builds green incl. a `SPHINX_LANGUAGE=ja` build proving `lang: "ja"` reaches the emitted template; 12/12 CI jobs green on the post-bump commit, 15/15 checks green on the release PR | 0 new runtime deps (the only dependency change is `dev`-only: `tox-uv` → `tox-uv-bare`) |

### Top Lessons (Verified Across Milestones)

1. Pin the whole dependency graph and commit the lockfile — reproducibility is the anti-rot mechanism. *(v0.4.4)*
2. Sequence changes so a red/green CI result is unambiguously attributable to one change. *(v0.4.4, reaffirmed v0.5.0 — atomic compiler+package bump)*
3. Confirm dependency root causes by reproduction, not changelog inference. *(v0.5.0 — overturned the v0.4.4-era `kai` attribution)*
4. A green unit suite doesn't prove correct rendered output — render-layer fixes need a compile→extract→assert acceptance gate. *(v0.5.0)*
5. Split reversible prep from the irreversible publish; gate the point-of-no-return at milestone close on a confirmed-green commit. *(v0.4.4 precedent, formalized v0.5.0)*
6. For a tool where one bad node aborts the whole output, "does it compile" is the only real correctness signal — compile-gate every render-layer handler against a fixture, and validate the milestone against a real downstream corpus. *(v0.6.0)*
7. Draw the milestone boundary before polishing, and fast-forward `main` after every merge — v0.6.0 re-created v0.4.4's branch/main drift at 2× scale by deferring both. *(v0.4.4, re-learned v0.6.0; validated v0.6.1 — the polish was scoped as its own milestone up front)*
8. For subjective/visual correctness, separate machine cataloguing (biased toward false-positives) from human judgment (one accept/reject + severity gate), and gate the resulting backlog by severity — promote only high-severity findings to requirements. *(v0.6.1)*
9. Cluster audit-derived findings by shared code root cause and gate config on *output* not registration; prove a fixture has teeth by reverting the fix in place (byte-identical restore), and let an unexercisable truth abstain to human rather than counting it green. *(v0.6.2)*
10. When you make a previously-silent failure loud, sweep the whole repo — including `examples/` — for who depended on the silence; and remember that per-phase verification proves the phases did what they said, not that the repo is shippable. *(v0.6.3 — a bundled sample shipped unbuildable through 6 green phases)*
11. Order a migration by irreversibility — every reversible action before the one with no undo, which gets its own phase and a freshly re-taken gate — and verify failure modes that present as success with content-level probes aimed at known-sensitive targets. *(v0.6.4 — the glyph defect and the coverage-blind ja probe were both invisible to build status)*
12. A written root cause — in a backlog note, a research doc, or an issue — is an unverified claim about code that is sitting right there. Reproduce and measure before fixing; make the first plan of a bugfix phase capture the emitted artifact and the verbatim error. *(v0.6.5 — two independent prior texts each made a specific, checkable, wrong claim)*
13. When the defect *compiles*, "does it compile" stops being a correctness signal — redefine RED for the milestone, write the assertion before the code, derive GREEN by hand from the recorded RED, and re-prove any gate you had to edit by restoring it over the pre-fix code. A test that went green after you edited the test is not evidence. *(v0.7.0 — four of nine citation gate selectors were gate defects, not translator defects)*
14. Reverse a locked decision when a live artifact overturns it, even if the phase already verified. Aesthetic and visual criteria need the owner's eyes on real output, and a sign-off is recorded verbatim with its caveats — not summarized. *(v0.7.0 — D-03-R re-opened a 5/5-verified Phase 39; ADM-04's "title-band luminance carries no signal" caveat is a recorded property, not latent work)*
15. When a milestone's post-mortem names a structural cause, encode it in the next roadmap as a success criterion rather than as a note. *(v0.7.1 — "the branch was never pushed until the release PR" became Phase 43's SC#5 and caught a Windows-only defect five phases before the release PR would have)*
16. Prefer the root-cause fix that dissolves a class of deferred items over the local workaround that repairs one symptom, and re-measure carried "deferred items" at close rather than transcribing them forward. *(v0.7.1 — one dependency rename took the suite from 45 failures to 0 and retired five Phase 45.1 deferrals; five of twelve open artifacts at close had already been resolved)*
17. A requirement whose acceptance evidence is generated by an irreversible action must not be flipped before that action succeeds — and the tooling will try to flip it for you, so diff the requirements file before committing the close. *(v0.7.1 — REL-04 closed on release run `31462027486` plus a `diff` of the published body against the extractor's output; `phase.complete`'s auto-flip is now three-for-three on release-prep phases and was caught each time)*
18. Published prose describing behaviour is a claim about code, and needs to be derived from the code with its own gate — not written alongside it. *(v0.7.1 — CONF-09 passed its implementation gates on round 1 and its documentation gates on round 4, the last three failures all in `configuration.rst`'s precedence description; `test_docs_contract_claims_gate.py` closed the single-page-enumeration hole afterwards)*
