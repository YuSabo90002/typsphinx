# Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision - Context

**Gathered:** 2026-07-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up the **English parent** Read the Docs project for typsphinx and settle the PDF
delivery path, so that `/en/latest/` serves this repository's real documentation built from
the checked-out commit, the documentation root always lands on a version that exists, and
the milestone's one genuinely open empirical unknown (`@preview` package egress from RTD's
build sandbox) is resolved by reading a raw build log rather than inferred.

Repo-side deliverables: `.readthedocs.yaml` (new), and the `conf.py` language seam
(`READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"`). Everything else in this phase is
verification of an owner-performed RTD web-UI setup.

**Requirements:** RTD-01, RTD-02, RTD-03, RTD-04.

**Explicitly NOT this phase:** the Japanese project (Phase 30), the multilang-machinery and
orphan-doc deletions (Phase 30), README/`pyproject.toml` URL rewrites (Phase 31), the
GitHub Pages teardown (Phase 32), the version bump (Phase 33). No `typsphinx/` runtime code
change at all — if the phase appears to need one, that is a re-scope signal.

</domain>

<decisions>
## Implementation Decisions

### RTD project slug (owner-manual, irreversible)

- **D-01:** The English parent project slug is **`typsphinx`** — identical to the PyPI
  package name and the repository name, giving
  `https://typsphinx.readthedocs.io/en/latest/`. Measured 2026-07-25:
  `https://typsphinx.readthedocs.io/` returns **404**, so the slug appears unclaimed; RTD's
  import screen is the authoritative check.
- **D-02:** **If the slug is already taken at import time, stop and consult the owner.** Do
  not silently fall back to a second candidate. RTD slugs are not self-service changeable
  and Phase 31 burns this URL into `README.md`, `pyproject.toml`'s `Documentation`
  metadata, and the repository's About → Website field.
- **D-03:** The Japanese project's slug is **deliberately not decided here** — it belongs to
  Phase 30's discussion. Noted only as a measurement: `https://typsphinx-ja.readthedocs.io/`
  also returns 404 today.

### PDF output path (`build.jobs.build.pdf`)

- **D-04:** Build into a **temporary directory, then copy only `*.pdf`** into
  `$READTHEDOCS_OUTPUT/pdf/`. Do **not** point `sphinx-build -b typstpdf` directly at
  `$READTHEDOCS_OUTPUT/pdf/`.
  *Measured 2026-07-25* (`sphinx-build -b typstpdf docs/source <tmp>`): the builder writes
  **31 files** into its output directory — `typsphinx.pdf`, `_template.typ`, 14 further
  `.typ` files (including per-docname files under `api/`, `examples/`, `user_guide/`), and
  a `.doctrees/` tree of 16 files. Only the PDF belongs in RTD's published download area,
  and this also side-steps the "exactly one file in `$READTHEDOCS_OUTPUT/pdf/`" constraint
  that research flagged as unconfirmed against any RTD reference page.
- **D-05:** The PDF filename stays **`typsphinx.pdf`** (derived from `typst_documents`'
  target name in `docs/source/conf.py`). It matches the existing GitHub Release asset name,
  so the RTD download and the Release asset are the same filename.

### Probing the `@preview` egress unknown

- **D-06:** **Two-stage, HTML first.** Land a `.readthedocs.yaml` that builds **HTML only**
  (no `formats:`, no `build.jobs.build.pdf`), confirm the build is green and that
  `/en/latest/` plus the documentation root serve real content — discharging RTD-01 and
  RTD-04 first. **Then**, in a separate commit, add `formats: [pdf]` together with the
  `build.jobs.build.pdf` override and read *that* build's raw log.
  Rationale: if the PDF step fails, the failure is isolated to the PDF step in a log with
  nothing else in it, and `/en/latest/` is already established and serving — the phase never
  passes through a state where the English site is red and RTD-04 is violated. Cost: two RTD
  build cycles instead of one, accepted.
- **D-07:** The `@preview` verdict must be a **recorded log excerpt**, not an inference.
  Branch A requires the log to show the four Typst Universe packages resolving *and* zero
  `latexmk` / `pdflatex` / `.tex` lines anywhere. Branch B requires the log to show the
  registry fetch blocked or failed; that excerpt is the recorded trigger for the fallback.

### Branch B fallback (registry blocked)

- **D-08:** If Branch B is taken, the documentation links to
  `https://github.com/YuSabo90002/typsphinx/releases/latest/download/typsphinx.pdf` from
  **both** `docs/source/index.rst` (Quick Links) **and** `README.md`.
  *Measured 2026-07-25:* that URL already returns **HTTP 200, 1,678,961 bytes** against the
  current `v0.6.3` release — the `releases/latest/download/` form needs no per-release
  editing, so RTD-03's "stays correct across releases without editing" clause is already
  empirically satisfied.
- **D-09:** Note for planning — the `README.md` edit in D-08 lands in the same file Phase 31
  rewrites. Keep it a small, additive block so the two phases do not fight over the same
  lines.

### CJK fonts — a new risk found by measurement

- **D-10:** Add **`build.apt_packages: [fonts-noto-cjk]`** to `.readthedocs.yaml` in the
  PDF-enabling commit, rather than waiting to see whether RTD's image happens to have CJK
  coverage.
  *Measured 2026-07-25:* the **English** documentation genuinely needs CJK glyphs —
  `docs/source/user_guide/configuration.rst:186` and `:240` contain 「表 1」「図 1」「图 1」
  「圖 1」 (the CONF-07 `lang` explanation added in v0.6.3 Phase 27.1). The locally built
  93-page PDF embeds **9 fonts**, of which `IPAexGothic`, `NotoSansCJKjp-Thin`,
  `DejaVuSansMono` and `Unifont` come from the *host*, not from typst-py. typst-py's
  embedded set (Libertinus Serif / New Computer Modern) has **no** CJK coverage, and Typst's
  font fallback is silent — so on an image without CJK fonts this renders as tofu in a build
  that reports success. This is exactly the RTD-02 SC#3 failure mode, now known to be likely
  rather than hypothetical.
- **D-11:** D-10 is **not** a reversal of the deferred I18N-03 ("no Japanese PDF"). I18N-03
  is about producing a full Japanese-language PDF; D-10 is about four CJK strings inside the
  English documentation. `build.apt_packages` is RTD build-environment configuration, not a
  Python runtime dependency, so the milestone's zero-new-runtime-dependencies invariant is
  untouched.

### RTD-02 content-comparison gate (Branch A)

- **D-12:** The comparison bar against the local `tox -e docs-pdf` baseline for the same
  commit is **three mechanical checks plus one human look**:
  1. page count matches,
  2. extracted text matches (`pypdf`, already a `dev` extra — no new dependency),
  3. the RTD-built PDF embeds at least one font with CJK coverage,
  4. the owner opens the two affected pages and confirms no tofu.
- **D-13:** **"Embedded font list must match exactly" is explicitly rejected as a bar.**
  Measured: the local baseline's 9-font list includes four host-provided fonts, so a
  perfectly healthy RTD build cannot be expected to produce an identical list. Only CJK
  *coverage* is asserted, not font identity.
- **D-14:** Text-extraction equality alone cannot detect glyph substitution — a tofu-rendered
  PDF still extracts the correct characters. That is why checks 3 and 4 exist; do not
  simplify the gate down to a text diff.
- **D-15:** The comparison is a **one-off**, run by hand with its exact commands and output
  pasted verbatim into `29-VERIFICATION.md`. No comparison script is committed to the
  repository: the RTD-built PDF is not reachable from CI, so a committed script would never
  run automatically and would only look like a gate that isn't one. The human-look half is
  recorded honestly (`human_needed` style), not asserted as machine-verified.

### Claude's Discretion

The owner explicitly delegated the remaining `.readthedocs.yaml` details. Planning may
decide these without asking again:

- `build.os` and `build.tools.python`. **Recommendation: `ubuntu-24.04` + Python `3.12`**,
  matching `.github/workflows/docs.yml`'s `actions/setup-python@v6` `python-version: "3.12"`
  so the RTD PDF and the `tox -e docs-pdf` baseline in D-12 are compared across the same
  Python minor. (Research says 3.12 or 3.13 are both fine; the tie-break is baseline parity.)
- Exact `sphinx:` key wording (`configuration: docs/source/conf.py`), `python.install`
  block shape (`method: uv`, `command: sync`, `extras: [docs]` — already locked by prior
  decisions), the temp-directory name and `-d` doctrees placement in the `build.jobs`
  commands.
- Which specific log lines are captured as evidence, and how they are formatted in
  `29-VERIFICATION.md`.

### Folded Todos

- **`.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md`** —
  the milestone's originating todo (`resolves_phase: 32`). Its Phase-29-relevant portions
  (add `.readthedocs.yaml`, create the RTD project + GitHub connection, decide the PDF
  path) are covered by the decisions above. The todo stays open until Phase 32, since its
  own `resolves_phase` targets the Pages teardown.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints
- `.planning/ROADMAP.md` § "🚧 v0.6.4" and § "Phase 29" — the phase goal, the four success
  criteria, the owner-manual dependency list, and the Notes paragraph that settles
  `formats:` + `build.jobs.build.pdf` as **used together** (correcting PITFALLS.md).
- `.planning/REQUIREMENTS.md` — RTD-01..RTD-04 text; § "Milestone Invariants" (all seven,
  especially #3 no `typsphinx/` change, #4 repo-wide grep, #7 a green build proves nothing
  about content); § "Owner-Manual Steps" items 1 and 5; § "Out of Scope".
- `.planning/PROJECT.md` § "Current Milestone: v0.6.4" — the four post-research owner
  decisions of 2026-07-25 (egress fallback, lost language auto-redirect, no Japanese PDF,
  PR previews dropped) and the Default-Version sequencing note.
- `.planning/STATE.md` § "Accumulated Context" — standing verification culture (honest
  `human_needed` abstention over unevidenced assertion) and the `ui.plan-gate` false-positive
  note (use `--skip-ui` if it flags this phase).

### Research (read before planning; do not re-derive)
- `.planning/research/SUMMARY.md` — § "Un-Researchable Blocker" (the `@preview` egress
  unknown), § "Settled Technical Questions (do not re-open)" (wheel availability, font
  embedding, `formats:`+override), § "Gaps to Address" (the unconfirmed
  `$READTHEDOCS_OUTPUT/pdf/` one-file constraint, which D-04 makes moot).
- `.planning/research/STACK.md`, `.planning/research/ARCHITECTURE.md`,
  `.planning/research/PITFALLS.md` — note that PITFALLS.md's "omit `formats:`" reading is
  **superseded**; STACK.md's reading is the one to build against.

### Files this phase touches or measures
- `docs/source/conf.py:51` — the `language = os.getenv("SPHINX_LANGUAGE", "en")` line that
  gains the `READTHEDOCS_LANGUAGE` layer. Also `:93-95` (`typst_documents`, source of the
  `typsphinx.pdf` filename) and `:71-89` (`html_context` / `html_sidebars` language-switcher
  wiring — **Phase 30's** to delete, not this phase's).
- `docs/source/user_guide/configuration.rst:186,240` — the CJK strings behind D-10.
- `docs/source/index.rst` § "Quick Links" — where the Branch B fallback link lands (D-08).
- `pyproject.toml:48-52` — the `docs` optional-dependency extra that `python.install`
  installs.
- `tox.ini:53-84` — the `docs-html` / `docs-pdf` environments. RTD **bypasses tox entirely**;
  do not wrap `build.jobs` commands in `tox -e docs-*`.
- `.github/workflows/docs.yml` — the existing build/publish pipeline. **Untouched by this
  phase**; its multilang steps belong to Phase 30 and its Pages deploy step to Phase 32.

### Todos
- `.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md` —
  originating todo; see Folded Todos above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`pypdf>=6.14,<7`** is already declared in `pyproject.toml`'s `dev` extra. Verified
  2026-07-25 that it reads page count, extracts text, and enumerates embedded `/BaseFont`
  names from the built PDF — everything D-12 needs, with no new dependency.
- **`docs` extra** (`furo`, `sphinx-autodoc-typehints`, `sphinx-intl`) is exactly what
  RTD's `python.install: extras: [docs]` will install; `sphinx-autodoc-typehints` is
  required — a build without it aborts with `Could not import extension` (observed while
  measuring).
- **`releases/latest/download/`** — the existing tag-time `Upload PDF to Release` step in
  `docs.yml` already produces `typsphinx.pdf` as a Release asset, which is what makes D-08's
  edit-free fallback URL work today.

### Established patterns
- **Measured output shape of the `typstpdf` builder** (`typsphinx/builder.py`): `write_doc`
  writes one `.typ` per docname into `outdir`, `_write_template_file` writes `_template.typ`
  into `outdir`, images are copied into `outdir`, and `finish()` compiles and writes the
  `.pdf` into `outdir`. There is no "PDF-only output directory" mode — hence D-04.
- **Advisory-CI precedent (D-07 of Phase 5, `drift.yml`)** — relevant background for Phase
  31's link guard, not for this phase; noted so planning does not confuse the two.
- **Deletion guard** (`worktree.cleanup-wave`) blocks branches containing deletions. Phase 29
  is additive only, so it should **not** fire here; Phase 30 is where it is expected.

### Integration points
- `.readthedocs.yaml` (new, repository root) → RTD's build manifest. Sole new file in the
  phase.
- `docs/source/conf.py` `language` seam → read by both the en and (from Phase 30) the ja
  project from the same commit. Locally both env vars are unset, so the value stays `"en"` —
  a zero-behavior-change edit. `conf.py` is documentation, not runtime; the
  no-`typsphinx/`-change invariant holds.
- RTD web UI (owner-manual, unassertable by any test): project creation + GitHub connection,
  Admin Language = English, Default Version left at `latest`.

</code_context>

<specifics>
## Specific Ideas

Measurements taken during this discussion, to be used as the baseline rather than re-derived:

- `sphinx-build -b typstpdf docs/source <tmp>` → **31 files**: `typsphinx.pdf`,
  `_template.typ`, 14 `.typ` files, `.doctrees/` (16 files). Build succeeded with 2 warnings.
- The built PDF is **93 pages** and embeds **9 fonts**: `IPAexGothic`,
  `NotoSansCJKjp-Thin`, `DejaVuSansMono`, `DejaVuSansMono-Bold`, `Unifont`, and four
  Libertinus Serif variants (Regular / Bold / Semibold / Italic). The first five are
  host-provided.
- `https://typsphinx.readthedocs.io/` → **404**; `https://typsphinx-ja.readthedocs.io/` →
  **404** (2026-07-25).
- `https://github.com/YuSabo90002/typsphinx/releases/latest/download/typsphinx.pdf` →
  **200, 1,678,961 bytes** (2026-07-25), resolving against the `v0.6.3` release.
- CJK in the English doc tree is confined to
  `docs/source/user_guide/configuration.rst:186,240` — a repo-wide `.rst` grep found no
  other file under `docs/source/`.

</specifics>

<deferred>
## Deferred Ideas

- **Japanese project slug** — deliberately left to Phase 30 (D-03).
- **RTD Default Version `latest` → `stable` flip** — Phase 33's owner-manual handoff. This
  phase records it as an explicit precondition and leaves Default Version at `latest`.
- **PR preview builds (RTD-05)** — dropped from v1 by owner decision 2026-07-25; a single
  owner-side checkbox, enable any time without a code change.
- **Japanese PDF (I18N-03)** — Future. D-10's `fonts-noto-cjk` is scoped strictly to the four
  CJK strings inside the English documentation and is not a step toward a Japanese PDF.
- **Documentation for tags before `v0.6.4` (RTD-06)** — structurally impossible; no earlier
  tag contains `.readthedocs.yaml`.

### Reviewed Todos (not folded)

- **`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`** — belongs to Phase 31
  (DOC-09). Phase 29 does not rewrite any published URL.
- **`2026-07-25-docs-usage-installation-orphan-class.md`** — belongs to Phase 30 (DOC-08).
- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — stays open, deferred as Future LNK-01.
- **`2026-07-22-citation-node-support-untracked.md`**,
  **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`**,
  **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`**,
  **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** — all require `typsphinx/`
  runtime changes, which this milestone's invariant #3 forbids.

</deferred>

---

*Phase: 29-RTD Build Establishment (English Parent) + PDF Path Decision*
*Context gathered: 2026-07-25*
