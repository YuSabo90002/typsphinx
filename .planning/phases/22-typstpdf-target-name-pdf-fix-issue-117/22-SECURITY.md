---
phase: 22
slug: typstpdf-target-name-pdf-fix-issue-117
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-21
---

# Phase 22 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: `register_authored_at_plan_time: true` — all three PLAN files
(`22-01`, `22-02`, `22-03`) carried a parseable `<threat_model>` block. ASVS level 1,
block-on threshold `high`. No threat in this phase reaches `high`, so the L1 grep-depth
short-circuit applies (no auditor subagent required).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| user `conf.py` (`typst_documents[i][1]`) → builder filesystem write path | A user-authored string becomes a path component passed to `open(..., "w")` under `outdir`. Weak by construction: `conf.py` is arbitrary Python that Sphinx imports and executes, so anyone controlling it already has code execution. The guard is defense against accidental escape and a UX signal, not containment of a hostile author. | target-name string (operator-supplied, non-sensitive) |
| test fixture `conf.py` → spawned `sphinx-build` subprocess | The GATE-01 render gate executes `tests/roots/test-basic/conf.py` as Python in a subprocess. Repository-controlled test input, not user input. | test config (repo-controlled) |
| resolved output stem → filesystem write under `tmp_path` | The gate's build writes only into a pytest `tmp_path`-rooted `_build` directory; its absence assertions double as a containment check on the Plan 01 path guard. | build artifacts (ephemeral) |
| upstream Sphinx corpus clone → `wire_typsphinx_into_corpus_conf`'s appended `conf.py` text | The slow corpus gate clones an external repository at a resolved tag and executes its `conf.py`. Pre-dates this phase and is unchanged by it. | external repo content (pinned tag) |
| documentation prose → user's `conf.py` | Wrong prose leads users to configure a target name and look for the wrong artifact — a correctness/UX failure, not a security one. | documentation text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-22-01 | Tampering | `TypstBuilder._resolve_output_stem` feeding `path.join(self.outdir, ...)` at all three write sites | low | mitigate | D-06/D-07 path guard implemented at `typsphinx/builder.py:131` — detects `/`, `\`, `os.sep`, `os.altsep`, `..` segments, `path.isabs`, and drive-qualified prefixes BEFORE the join, warns, and reduces to `path.basename`. Verified present in source; asserted by the five `test_resolve_output_stem_guards_*` tests in `tests/test_builder_output_stem.py`. | closed |
| T-22-02 | Denial of Service | degenerate target name (`""`, `".typ"`, whitespace-only, non-str, short tuple) | low | mitigate | Degenerate guard falls back to the docname and warns; `write_doc` never raises `IndexError`/`AttributeError` and never opens an empty/bare-dotfile basename. `tests/test_builder_output_stem.py` collects 24 tests (plan floor: 18), including the `falls_back_on_*` set. | closed |
| T-22-03 | Information Disclosure | `logger.warning` text for a guarded target name | low | accept | The warning echoes the operator's own `conf.py` value into the build log — same disclosure class Sphinx already performs for every config error, and the value originates from the operator running the build. See Accepted Risks R-22-01. | closed |
| T-22-04 | Tampering | `_run_sphinx_build_typstpdf` subprocess invocation | low | mitigate | Invoked as `sys.executable -m sphinx` with an explicit argument list — verified at `tests/test_target_name_render_gate.py:70`; no `shell=True` and no string interpolation into a shell command anywhere in the file. Also the documented NixOS-sandbox requirement. | closed |
| T-22-05 | Spoofing | PDF artifact validity | low | mitigate | The gate asserts PDF magic bytes and non-emptiness rather than trusting `returncode == 0` — `tests/test_target_name_render_gate.py:146-148` (`st_size > 0`, `f.read(4) == b"%PDF"`). Necessary because `TypstPDFBuilder.finish()` logs compile failures as ERROR rather than raising. | closed |
| T-22-06 | Repudiation | `tests/test_corpus_gate.py` GATE-02 assertion | medium | mitigate | The assertion was realigned to the target-derived artifact and now asserts `pdf_path.exists()` and `pdf_path.stat().st_size > 0` (`tests/test_corpus_gate.py:336,341`), with the comment/docstring rewritten so the recorded contract matches builder behavior and carries no stale line-number citations. | closed |
| T-22-07 | Tampering | `tests/fixtures/cross_doc_label_namespace_render_gate/` label-namespacing assertions | medium | mitigate | The `pagea:shared-topic` namespacing assertions are intact and strengthened, not relaxed — present at `tests/test_cross_doc_label_namespace_render_gate.py:172,208` alongside the renamed-master cross-reference proof. | closed |
| T-22-08 | Information Disclosure | `.planning/ROADMAP.md` scoped edits | low | mitigate | Scoped replacement was used instead of a whole-file `Write`; the `### Phase ` heading count is 6, matching the pre-edit pin — no phase entry outside the diff window was deleted. | closed |
| T-22-SC | Tampering | npm/pip/cargo installs | low | accept | All three plans install zero packages; `typst-py` and `pytest` were already declared dev dependencies. `git diff main -- pyproject.toml` is empty, confirming no dependency edit. RESEARCH.md § "Package Legitimacy Audit" records the gate as not applicable. See Accepted Risks R-22-02. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-22-01 | T-22-03 | The guard warning echoes the operator's own `typst_documents` value into the build log. The value originates from the person running the build, and Sphinx already discloses config values in the same way for every config error. Suppressing it would remove the UX signal that makes the guard useful. | yuta | 2026-07-21 |
| R-22-02 | T-22-SC | Phase 22 installs zero packages and edits no dependency manifest (verified: empty `pyproject.toml` diff vs. `main`). The supply-chain legitimacy gate is not applicable; the milestone invariant of zero new runtime deps holds. | yuta | 2026-07-21 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-21 | 9 | 9 | 0 | /gsd-secure-phase (L1 short-circuit, orchestrator) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-21
