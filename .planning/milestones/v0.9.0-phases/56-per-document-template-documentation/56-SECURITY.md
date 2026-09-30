---
phase: 56
slug: per-document-template-documentation
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-16
---

# Phase 56 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time** — all five PLAN files
(`56-01`…`56-05`) carried a parseable `<threat_model>` block, so this audit
verified the pre-declared mitigations rather than reconstructing a register
retroactively. No SUMMARY file declared a `## Threat Flags` section, so no
execution-time threat was added to the register.

Phase 56 is a documentation-and-test phase: it added no production code path
and no dependency. Every trust boundary below is a *test-time* boundary
(repository bytes entering a pytest process, or a pytest-authored `conf.py`
entering a `sphinx-build` subprocess), not a boundary the shipped extension
exposes to its users.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| repository file contents → test process | the four new/extended gate modules parse `typsphinx/*.py` and read `docs/source/**`, `README.md`, `examples/**` as text | source and documentation bytes, all repo-committed; no secrets |
| repository layout → assertion messages | discovered paths are interpolated into pytest failure output | repository-relative path strings |
| test-authored `conf.py` → `sphinx-build` subprocess | `test_hand_compile_root_gate.py` and `test_removed_config_deprecation_gate.py` write a `conf.py` under `tmp_path` and Sphinx executes it | test-authored Python literals, parameterized only by in-process constants |
| committed fixture files → `sphinx-build` / `typst.compile()` | `tests/fixtures/user_template_relative_asset_gate/_typst/{branded.typ,refs.bib}` are parsed by Sphinx and the Typst compiler | static, repo-committed template and BibTeX data |
| build output `.typ` → `typst.compile()` | the compiler reads the generated wrapper and follows its root-absolute import | generated Typst markup inside a `tmp_path` build tree |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-56-01 | Tampering | `tests/test_registry_documentation_gate.py` source scan | medium | mitigate | Verified: the module imports `ast`, `re`, `pathlib` only; scanned files are `read_text()` + `ast.parse()` (`:230-231`). Grep over the module found no `exec(`, `eval(`, `compile(..., "exec")`, `import_module`, `__import__` or `runpy` — the only `compile(` hit in the phase's modules is `re.compile` (`:266`). A scanned module's contents can never execute in the test process. | closed |
| T-56-02 | Information Disclosure | path constants and assertion messages in the registry gate | low | mitigate | Verified: `REPO_ROOT = Path(__file__).resolve().parent.parent` (`:53`); every other root derives from it. No host absolute-path literal in the module. | closed |
| T-56-03 | Denial of Service | run-time `glob`/`rglob` discovery in the registry gate | low | accept | Accepted (see Accepted Risks Log). Bounded by construction: `TYPSPHINX_PKG_DIR.glob("*.py")` is non-recursive (`:149`); `rglob` is confined to `DOCS_SOURCE_DIR` and `EXAMPLES_DIR` (`:373-377`). | closed |
| T-56-04 | Tampering | the `tmp_path` `conf.py` executed by `sphinx-build` in `TestMultipleRemovedValuesEachWarnSeparately` | medium | mitigate | Verified: the `conf.py` is `MINIMAL_CONF_HEADER` (a module literal) plus a body built only from `REMOVED_CONFIG_VALUES` keys — this repository's own already-imported production constant, never an environment variable, CLI argument or file read from disk. The subprocess argument list is the fixed `[sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)]` (`:69-79`); no user-controlled string reaches the command line. See the residual note below. | closed |
| T-56-05 | Information Disclosure | assertion messages quoting build output and file paths | low | mitigate | Verified: build roots are `tmp_path`-managed and test-authored; repository paths in both modules derive from `Path(__file__)` relatives, with no host absolute-path literal. | closed |
| T-56-06 | Tampering | importing `typsphinx.template_registry` / `typsphinx.removed_config` in a static gate | low | accept | Accepted (see Accepted Risks Log). Verified the imports are exactly those two first-party production modules (`test_registry_documentation_gate.py:50-51`), already imported across the existing suite. | closed |
| T-56-07 | Tampering | the runtime-generated `conf.py` executed by Sphinx in `test_hand_compile_root_gate.py` | medium | mitigate | Verified: `_build_source_tree()` writes a literal `conf.py` whose only interpolation is `{target!r}` — the target string the test itself supplies ("manual.typ" / "manuals/guide.typ"), `repr`-quoted. Nothing from the environment, the repository or an external source is interpolated. Subprocess argument list is the same fixed form (`:70-79`). | closed |
| T-56-08 | Tampering | `typst.compile(..., root=<outdir>)` in the nested-target test | low | mitigate | Verified: `root=str(build["build_dir"])` (`:230-232`), where `build_dir = tmp_path / "build"` under `tmp_path_factory.mktemp(...)`. No repository path and no path outside `tmp_path` is ever passed as a project root. | closed |
| T-56-09 | Information Disclosure | compiler error text asserted in the nested-target test | low | accept | Accepted (see Accepted Risks Log). The asserted value is the fragment `"base.typ"` out of the compiler's own file-not-found message over `tmp_path` paths. | closed |
| T-56-10 | Tampering | the new `refs.bib` fixture consumed by `typst.compile()` | low | mitigate | Verified by reading the file: a single static `@misc{proof2026, ...}` entry plus `%` comments. No `\input`, `@preamble`, include or shell-escape construct. Read as data inside a `tmp_path` build tree, never executed. | closed |
| T-56-11 | Tampering | `TestPublishedAssetGuidanceMatchesTheFixture` reading two documentation pages | low | mitigate | Verified: the class does `read_text()` + string containment only (`:220-272`); no `exec`, `eval` or import of a read file. `FIXTURE_TEMPLATE_PATH` / `TEMPLATES_RST_PATH` / `ADVANCED_RST_PATH` all derive from `Path(__file__)` relatives (`:44-53`). | closed |
| T-56-12 | Elevation of Privilege | `sphinx-build` executing the fixture's `conf.py` | low | accept | Accepted (see Accepted Risks Log). Phase 56 added a data file (`refs.bib`) and a `#bibliography(...)` call beside the existing template; the fixture's `conf.py` was already executed by four pre-existing tests in the module. | closed |
| T-56-13 | Tampering | `tests/test_bundle_layout_sweep_gate.py` reading `examples/**/*.py` | medium | mitigate | Verified: the module imports `re`, `pathlib`, `typing` only (`:40-42`). Every policed file is `read_text()` and matched with pre-compiled regexes (`:163-167`, `:223-241`). No `exec`, `eval`, `compile(..., "exec")`, `import_module` or `__import__` — an `examples/` `conf.py` can never execute inside the test process. | closed |
| T-56-14 | Information Disclosure | path constants and failure messages in the sweep gate | low | mitigate | Verified: `REPO_ROOT = Path(__file__).resolve().parent.parent` (`:44`) with all three `POLICED_ROOTS` derived from it (`:47-51`); failure output prints `path.relative_to(REPO_ROOT).as_posix()` (`:137`). No host absolute-path literal. | closed |
| T-56-15 | Denial of Service | repo-wide `rglob` over three roots | low | accept | Accepted (see Accepted Risks Log). Bounded: `rglob("*")` runs over exactly the three `POLICED_ROOTS` (`:123`), filtered by suffix allow-lists and `_SKIP_PARTS` (`__pycache__`, `_build`); both patterns are literal/word-bounded with no backtracking-prone construct. | closed |
| T-56-16 | Repudiation | a sweep result asserted rather than measured | medium | mitigate | Verified: `56-SWEEP-DISPOSITION.md` records the discovery commands with their complete output against named commits (`753ea458` for discovery, `0811ab69` for the phase-boundary evidence), a 56-row per-hit disposition table, and a requirement-to-evidence mapping — 34 fenced transcript blocks. The "the sweep is clean" claim is falsifiable by re-running the recorded commands. | closed |
| T-56-SC | Tampering | npm/pip/cargo installs (declared identically in all five plans) | low | accept | Accepted (see Accepted Risks Log). Measured, not asserted: `git diff f07e8cb8..HEAD -- pyproject.toml uv.lock package.json requirements*.txt --stat` is empty across the whole phase. The new modules import only `ast`, `re`, `subprocess`, `sys`, `pathlib`, `typing`, `pytest` and the two first-party `typsphinx` modules; `typst-py` was already a dev dependency used by four pre-existing gate modules. The Phase-56 bibliography route deliberately uses Typst's built-in `#bibliography()` rather than a Universe package, so it does not become a fourth `@preview` version-lockstep site. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (`high`) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Residual note on T-56-04.** The plan's mitigation text said the executed
`conf.py` body is "never derived from a repository file". As shipped, the
body's variable names come from `REMOVED_CONFIG_VALUES`, imported from
`typsphinx/removed_config.py` — a repository source, though an in-process
first-party constant rather than external or untrusted input. That import is
itself the subject of T-56-06 (disposition `accept`), and it is what makes the
declaration-order guarantee binding instead of transcribed. Substantively
mitigated; recorded here so the wording gap is visible rather than silently
absorbed.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-56-01 | T-56-03 | Discovery is bounded to `typsphinx/*.py` (non-recursive) plus the two policed documentation roots; the measured full-suite cost of the six existing gate modules of this shape is seconds. | yuta (plan-time disposition, 56-01-PLAN.md) | 2026-08-16 |
| AR-56-02 | T-56-06 | `typsphinx.template_registry` and `typsphinx.removed_config` are this repository's own production modules, already imported by the whole existing suite; importing them is not new attack surface, and it is what makes the enumeration binding real instead of transcribed. | yuta (plan-time disposition, 56-02-PLAN.md) | 2026-08-16 |
| AR-56-03 | T-56-09 | The asserted text is the Typst compiler's own file-not-found message over `tmp_path` paths, which pytest already prints for every failing test in this suite. | yuta (plan-time disposition, 56-03-PLAN.md) | 2026-08-16 |
| AR-56-04 | T-56-12 | The fixture and its `conf.py` are already executed by four pre-existing tests in the module; adding a static data file beside the template introduces no new execution surface. | yuta (plan-time disposition, 56-04-PLAN.md) | 2026-08-16 |
| AR-56-05 | T-56-15 | The three roots are bounded and already walked by two existing gate modules of the same shape at negligible cost; the gate reads text and runs compiled regexes with no backtracking-prone construct. | yuta (plan-time disposition, 56-05-PLAN.md) | 2026-08-16 |
| AR-56-06 | T-56-SC | The phase installs no package. Verified at audit time: the dependency manifests are byte-identical across the phase's full commit range. | yuta (plan-time disposition, all five PLAN files) | 2026-08-16 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-16 | 17 | 17 | 0 | /gsd-secure-phase 56 (orchestrator, ASVS L1 grep-depth; auditor not spawned — short-circuit: `threats_open: 0` + register authored at plan time + `asvs_level == 1`) |

### Security Audit 2026-08-16

| Metric | Count |
|--------|-------|
| Threats found | 17 |
| Closed | 17 |
| Open | 0 |
| Open at or above `high` (blocking) | 0 |

Register composition: 16 uniquely-numbered threats (T-56-01…T-56-16) plus the
supply-chain threat T-56-SC, declared identically in all five PLAN files and
consolidated into one row here. 11 dispositions were `mitigate` (all verified
present in the implementation); 6 were `accept` (all recorded in the Accepted
Risks Log above).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-16
