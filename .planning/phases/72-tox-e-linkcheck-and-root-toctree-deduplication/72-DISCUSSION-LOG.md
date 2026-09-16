# Phase 72: `tox -e linkcheck` and Root Toctree Deduplication - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 72-tox-e-linkcheck-and-root-toctree-deduplication
**Areas discussed:** Linkcheck non-working results, DOC-24 line wording, 2026-07-22 linkcheck todo, UI-gate handling

The findings and all four questions were presented in a single plain-text message. Focus mode hides
text placed before an AskUserQuestion call, so AskUserQuestion was not used. The owner answered
"1a 2a 3a 4a", which picked the recommended option in each area.

The measurement shown with the questions was a clean `sphinx-build -b linkcheck` run: 95/95
`working`, exit 0, 41 anchored URIs, and 40 entries from `api/` autodoc docstrings. The questions
also cited Sphinx 9.1.0's `write_linkstat()`, which writes every status to `output.json`, so an
ignore-style key cannot satisfy SC#1's total-equals-`working`.

---

## Linkcheck non-working results at execution time

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Transient failures (timeout / 503 / rate-limited): re-run from clean and record every run. A recurring transient failure permits only `linkcheck_timeout` / `linkcheck_retries`, with a comment. A real broken link, or a need for `linkcheck_ignore`, stops the phase and goes to the owner. | ✓ |
| (b) | The executor may add a commented `linkcheck_ignore`, and SC#1 is re-read as "`working` + commented `ignored` = total", which needs an AMENDED block | |
| (c) | Any non-`working` result goes to the owner immediately, with no re-run | |

**User's choice:** (a)
**Notes:** Became D-01..D-04. CONTEXT fixes the run ceiling at three runs in total, and it adds
`linkcheck_rate_limit_timeout` to the timing keys, since it addresses the same transient class.

---

## DOC-24 line wording

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | The comment says the environment needs the network and is not run by plain `tox`, e.g. `# Check external links and anchors (needs network; not run by plain tox)` | ✓ |
| (b) | The comment states only the purpose, e.g. `# Check links in the documentation` | |

**User's choice:** (a)
**Notes:** The line goes last in each block: after `docs-pdf` in `CLAUDE.md`, and after `docs` in
`README.md` and `contributing.rst` (D-05). The existing "Run all tox environments" comment stays
true (D-06).

---

## 2026-07-22 linkcheck todo

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Keep it pending and append a note that the tox environment landed in Phase 72 and QUA-08 remains | ✓ |
| (b) | Leave it untouched | |
| (c) | Move it to completed and file a new QUA-08 todo | |

**User's choice:** (a)
**Notes:** D-07. The note is appended after QUA-13's environment has landed.

---

## UI-gate false positive (constraint 13)

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | `--skip-ui` at plan time, with no ROADMAP edit (the standing workaround) | ✓ |
| (b) | Add a `**UI hint**: no` line to Phase 72 in the ROADMAP (the v0.9.4 style) | |

**User's choice:** (a)
**Notes:** D-09.

---

## Claude's Discretion

- The exact DOC-24 comment text, within D-05.
- The `[testenv:linkcheck]` `description` text.
- The plan split, the evidence file names, how the base build is materialised, and how the sidebar
  count is taken from the markup.

## Deferred Ideas

None. Reviewed but not folded: the QUA-08 linkcheck todo (it stays pending, with a note), NUM-01,
MSG-06 and TRN-01. The last three are all `typsphinx/` edits, which constraint 2 forbids.
