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
