---
id: SEED-001
status: dormant
planted: 2026-08-01
planted_during: v0.7.0 (API rendering design overhaul) — Phase 36 planning
trigger_when: when relevant
scope: unknown
---

# SEED-001: README の Quick Start に何も書いていないのに、`typst_documents` を設定していないと `.typ` ファイルが PDF にコンバートされない

**Captured verbatim (owner's words):**

> Readme の quickStart になにも書いてないのにも関わらず `typst_documents` を設定していないと typ
> ファイルが pdf にコンバートされない

## Why This Matters

_To be filled in. Run `/gsd-capture --seed --enrich SEED-001` to add context._

Provisional note: this is a first-run onboarding failure. A new user who follows the README's
Quick Start exactly gets a **silent-ish no-op** — the `typstpdf` build "succeeds" (exit 0) and
emits only a `WARNING`, but produces zero PDFs. The gap between "the documented happy path" and
"the config actually required for the documented happy path" is the defect.

## When to Surface

**Trigger:** when relevant

This seed will surface during `/gsd-new-milestone` when the milestone scope matches.

Candidate narrower triggers (pick one at enrich time): a docs/onboarding milestone; the planned
Read the Docs migration; any phase touching `TypstPDFBuilder.finish()` or first-run UX.

## Scope Estimate

**Unknown** — run `/gsd-capture --seed --enrich SEED-001` to estimate effort.

Note that the fix direction is not yet decided, and the options differ a lot in size:
1. **Docs-only** — document `typst_documents` in the Quick Start. Small.
2. **Better failure signal** — promote the warning so a `typstpdf` build that produces no PDF is
   loud (or non-zero). Small–medium; touches error-contract expectations and existing tests.
3. **Sensible default** — derive a master document from `root_doc`/`master_doc` when
   `typst_documents` is unset, so the documented Quick Start works as written. Medium; a real
   behavioural change with config-precedence and multi-master implications.

## Breadcrumbs

**Verified 2026-08-01 — the report reproduces from source inspection.**

- `README.md:63-88` — `## Quick Start`. The "Basic Configuration" `conf.py` block sets only
  `typst_use_mitex`, and explicitly frames adding `typsphinx` to `extensions` as optional. The
  "Build Typst Output" block then shows `sphinx-build -b typstpdf source build/pdf` as if it
  works with that config. `typst_documents` is never mentioned anywhere in the Quick Start.
- `typsphinx/builder.py:903-910` — `TypstPDFBuilder.finish()`:
  ```
  typst_documents = getattr(self.config, "typst_documents", [])
  if not typst_documents:
      logger.warning("No documents defined in typst_documents. Nothing to compile.")
      return
  ```
  So with the README's config, the PDF stage returns early. The `.typ` files are still written
  (`write_doc` is unaffected); only the PDF compile is skipped.
- `typsphinx/__init__.py:44` — `app.add_config_value("typst_documents", [], "html", [list])`.
  The default is the empty list, which is exactly the value that triggers the early return.
- `typsphinx/builder.py:882` — docstring: "Only master documents (defined in `typst_documents`)
  are compiled to PDF." The behaviour is intentional and documented *in the code*; the gap is
  that it is not documented in the *README*.

Related planning records:
- `.planning/todos/completed/2026-07-22-readme-overall-content-review-stale-claims.md` — a prior
  README accuracy sweep. Worth checking at enrich time whether this case was considered and
  deliberately left, or simply missed.
- `.planning/todos/pending/2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` — another
  open defect in the same `TypstPDFBuilder.finish()` method. If a phase picks up that todo, this
  seed is cheap to fold in alongside it.
- Project memory records a planned Read the Docs migration (~2026-07-30) during which interim
  README/docs link fixes were deliberately deferred. Check whether that migration is the natural
  home for the docs-only variant of this fix before opening a separate docs phase.

## Notes

_Captured via one-shot seed capture. Enrich with trigger, why, and scope at your convenience._

Not folded into Phase 36 — Phase 36 is a translator emission-seam refactor (ADM-06, MATH-02) with
a locked zero-byte-delta scope; this is unrelated onboarding/docs work and pulling it in would
break that phase's only acceptance criterion.
