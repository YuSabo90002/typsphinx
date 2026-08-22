---
phase: 53
slug: template-registry-foundation
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-15
---

# Phase 53 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time** — all 10 of Phase 53's PLAN files carry a parseable
`<threat_model>` block, so this audit verifies declared mitigations rather than reconstructing a
register retroactively. ASVS level 1 (grep-depth verification), `security_block_on: high`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `conf.py` → `resolve_template_registry()` | Sphinx registers `typst_document_templates` as `[dict]`, which only *warns* on mismatch — the container, its keys and every definition field arrive with arbitrary Python types. The phase's only new input surface. | Author-controlled config: registry keys destined to become filesystem path segments in Phase 54; `template` path strings; `package` specs |
| declared `template` value → `os.path` arithmetic | A user-authored value reaches `join`/`abspath`/`dirname`/`normpath`/`commonpath`. CONF-17 decides from that arithmetic alone whether the value would make Phase 54 copy the source tree. | Path string / `os.PathLike` |
| this phase's validator → Phase 54's write sites | Deferred-harm boundary: the exploit sites (`mkdir()`, `copytree()`) do not exist yet. Validating here closes the door before they are built. | Registry key as directory name; template parent as copy source |
| `TypstBuilder.write()` → filesystem under `outdir` | Every `.typ` path the phase can cause to be written, or not written. The gap closed in 53-06 is entirely about which side of a validation failure this boundary is crossed on. | Generated `.typ` files |
| resolved registry → `render_wrapper()` | Crosses from build-wide resolution into per-document template construction; a wrong value silently changes every wrapper's typesetting rather than failing. | `TemplateRegistryEntry` |
| local repository → `origin` | A push publishes / advances the milestone branch. A pushed ref cannot be cleanly un-published. | Git history (public) |
| GitHub Actions run output → evidence artifacts | Run IDs, job names, head SHAs and conclusions are transcribed into artifacts the verifier, the milestone audit and the release record treat as ground truth. | Run metadata, public URLs, SHAs — no credentials |
| phase artifacts → `.planning/REQUIREMENTS.md` | A recorded requirement status is read downstream by the milestone audit and `/gsd-complete-milestone` as ground truth for what shipped. | Requirement completion status |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-53-01 | Tampering | registry key reaching a future `mkdir()`/`copytree()` | medium | mitigate | CONF-18 seven-case denylist at `template_registry.py:101-134`, attached at the single resolution point before any key-derived write site exists | closed |
| T-53-02 | Information Disclosure | `template` path whose parent is `srcdir` or an ancestor | medium | mitigate | `_violates_conf17()` (`template_registry.py:137-175`) — pure path arithmetic, single `commonpath` comparison covering both rejected shapes; wired at `:420` | closed |
| T-53-03 | Tampering | denylist drift toward an allowlist / an eighth case | low | mitigate | `_KEY_SHAPE_REJECTION_CASES` module constant + `tests/test_template_registry.py:422-425` asserting `len == 7` and `len(set(...)) == 7` | closed |
| T-53-04 | Tampering | `53-RED-EVIDENCE.md` recorded values | medium | mitigate | 37 SHA-256 lines present and countable; commit SHA produced by `git rev-parse HEAD`; live `typst.compile()` probe transcript recorded verbatim (§ "Environment note") | closed |
| T-53-05 | Repudiation | `typst.compile()` availability path | low | mitigate | Evidence path decided by a live probe recorded in the artifact (`53-RED-EVIDENCE.md:22-48`, re-verified at `:271`), not by a RESEARCH note | closed |
| T-53-06 | Tampering | `resolve_package_for_engine()` routing | low | mitigate | Defined once (`template_engine.py:159`); both consumers (`writer.py:366`, `builder.py:1281`) call it rather than re-deriving the template-wins-over-package rule — verified 1 definition, 2 call sites | closed |
| T-53-07 | Denial of Service | empty `_document_template_registry` on the direct-call write path | medium | mitigate | Lazy-derivation fallback at `builder.py:1180-1182` calls the same resolver, so a caller bypassing `write()` cannot observe an unresolved registry | closed |
| T-53-08 | Spoofing | user key impersonating the built-in `typst` key | low | mitigate | CONF-16 literal reserved-key rejection (`template_registry.py:338-343`); `Typst`/`TYPST` admitted by explicit decision D-04, collision scoped to Phase 54 and recorded in CONTEXT § Deferred Ideas | closed |
| T-53-09 | Tampering | a second, independent path lookup drifting from the priority walk | low | mitigate | `grep -c 'TemplateResolution('` = 3 (`template_engine.py:321,336,350`); no `resolve_template_path` definition exists anywhere in `typsphinx/` | closed |
| T-53-10 | Tampering | the `origin` branch namespace | medium | mitigate | Single named ref, no force flag; stale `gsd/v0.9.0-milestone` re-measured at `aed773c9` unchanged; `git reflog` shows no rebase/reset inside the phase window | closed |
| T-53-11 | Information Disclosure | evidence artifacts committed to the repository | low | mitigate | Credential-pattern sweep over every `53-*.md` returns zero hits; artifacts carry hashes, run IDs and public URLs only | closed |
| T-53-06-01 | Tampering | `TypstBuilder._validate_registry_key_references()` | medium | mitigate | Dict-lookup-only pass at `builder.py:630-694`, called from `write()` at `:813` before `prepare_writing()` — an unregistered key never reaches Phase 54's `_template/<key>/` write site | closed |
| T-53-06-02 | Denial of Service | partial `.typ` output surviving a failed build | medium | mitigate | Validation hoisted above `prepare_writing()`; pinned by `test_conf14_bad_key_sorting_{first,last}_writes_no_typ_files` in both master orders | closed |
| T-53-06-03 | Information disclosure | `resolve_registry_key()`'s `ExtensionError` message | low | accept | See Accepted Risks R-01 — message embeds only user-authored `conf.py` values via `repr()`; naming registered keys is required by CONF-14 | closed |
| T-53-07-01 | Denial of Service | `_violates_conf17()` cross-drive `ValueError` | medium | mitigate | Narrow `except ValueError: return False` guard (`template_registry.py:164-175`) mirroring `builder.py`'s `_track_image()`; POSIX-deterministic monkeypatch test | closed |
| T-53-07-02 | Denial of Service | `resolve_template_registry()` accumulate loop | medium | mitigate | Non-`str` key guard (`:331-333`), truthy non-`dict` definition guard (`:361-366`), and a total `sorted()` ordering key (`:321-324`) — all feeding the single accumulated raise | closed |
| T-53-07-03 | Information disclosure | new `ExtensionError` message text | low | accept | See Accepted Risks R-02 | closed |
| T-53-07-04 | Elevation of privilege | registry key reaching a directory path | medium | transfer | Transferred to Phase 54, where `mkdir`/`copytree` first exist. This phase ships the frozen seven-case single-segment denylist; the drive-qualified shape (`53-REVIEW.md` CR-01) is a known accepted gap locked as a Deferred Idea in `53-CONTEXT.md` | closed |
| T-53-08-01 | Denial of Service | `resolve_template_registry()` container read | medium | mitigate | Pre-accumulation `isinstance(declared, dict)` guard (`template_registry.py:302-306`) raising this module's own `ExtensionError`; pinned by `tests/test_registry_container_shape_gate.py` incl. falsy controls and a no-`.typ`-written assertion | closed |
| T-53-08-02 | Denial of Service | `resolve_template_registry()` definition half | medium | mitigate | Truthiness-gated `isinstance(template, (str, os.PathLike))` guard (`:408-412`) joining the accumulated raise as an `elif`-sibling of CONF-15, so both failures still report together | closed |
| T-53-08-03 | Information disclosure | new `ExtensionError` message text | low | accept | See Accepted Risks R-03 | closed |
| T-53-08-04 | Elevation of privilege | registry key / template path reaching a directory operation | medium | transfer | Transferred to Phase 54's bundle-write threat model (destination-collision OUT-07, symlink-escape BLD-06). This phase ships the seven-case denylist plus CONF-17 path arithmetic | closed |
| T-53-08-05 | Tampering | `53-08-RED-EVIDENCE.md` | medium | mitigate | `git rev-parse`-measured SHA at `:9`; verbatim `AttributeError` and `TypeError` traceback tails at `:37-44` and `:94-100` — both defects independently re-reproduced at HEAD before the plan was written | closed |
| T-53-09-01 | Tampering | `.planning/REQUIREMENTS.md` status cells | medium | mitigate | Commit `cdde40e7` numstat is exactly `6	6`; `REL-08` verified still `[ ]` / `Pending` — the recorded auto-flip hazard did not fire | closed |
| T-53-09-02 | Repudiation | requirement delivery record | medium | mitigate | Statuses transcribed from `53-03-SUMMARY.md`'s `requirements-completed` list and `53-VERIFICATION.md`'s Requirements Coverage rows, with a halt condition if either fails to name all three IDs | closed |
| T-53-09-03 | Tampering | surrounding prose (totals, coverage block) | low | mitigate | Numstat bound plus positive grep on the `**Per-phase totals:**` line; coverage arithmetic intact | closed |
| T-53-10-01 | Repudiation | `53-CI-EVIDENCE.md` currency | high | mitigate | Re-measured live in this audit: `git log 35ee8a0e..HEAD -- typsphinx/ tests/` is **empty**, `git ls-remote` shows `origin/gsd/v0.9.0-per-document-templates` at `35ee8a0e` = the certified `headSha`. The five commits since are `.planning/`-only. Invalidation rule published in the artifact itself | closed |
| T-53-10-02 | Tampering | `53-CI-EVIDENCE.md` recorded values | medium | mitigate | Verbatim `gh run view --json` blocks for runs `31875380355`, `31875707734` and `31884774067`; `git ls-remote` line present; SHA equality between pushed tip and run `headSha` re-confirmed in this audit | closed |
| T-53-10-03 | Tampering | the `origin` branch namespace | medium | mitigate | No force-push, rename, merge or delete; `gsd/v0.9.0-milestone` still resolves to `aed773c9807ab871468b1b2a7e1ec36b54e82907`; reflog carries no rebase/reset entry inside the phase window | closed |
| T-53-10-04 | Spoofing | CI run identification | medium | mitigate | Three-field match required on workflow name `CI`, event `workflow_dispatch` and `headSha` — the `Link Check` workflow every push fires cannot be mistaken for a test run | closed |
| T-53-10-05 | Information disclosure | evidence artifact committed to the repository | low | mitigate | Credential-pattern sweep clean; `gh auth status` used as a precondition only, output never pasted | closed |
| T-53-SC | Tampering | npm/pip/cargo installs (supply chain) | high | accept | See Accepted Risks R-04. Measured: zero changes to `pyproject.toml`, `uv.lock`, `tox.ini`, `requirements*.txt` or `.github/workflows/` across the whole phase — no install site exists to guard | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Register consolidates 32 unique threats across 10 PLAN files. The per-plan supply-chain rows
(`T-53-SC`, `T-53-06-SC`, `T-53-07-SC`, `T-53-08-SC`, `T-53-09-SC`, `T-53-10-SC`) are identical in
substance and are folded into the single `T-53-SC` row above; the highest severity any plan
assigned them (`high`, plans 53-06 and 53-07) is carried forward rather than the lowest.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-01 | T-53-06-01 → T-53-06-03 | `resolve_registry_key()`'s error message embeds the user's own registry keys and the offending value via `repr()`. CONF-14 *requires* the message to name the registered keys; the values are ones the user authored in their own `conf.py`. No build-machine path or environment value is added. | Phase 53 plan 53-06 | 2026-08-15 |
| R-02 | T-53-07-03 | Both new `ExtensionError` messages (non-`str` key, non-`dict` definition) embed the offending key/value via `repr()`. SC#3 requires "a message naming the specific reason". No filesystem path or environment value beyond what the user declared is added. | Phase 53 plan 53-07 | 2026-08-15 |
| R-03 | T-53-08-03 | Same class as R-02 for 53-08's two new messages (non-`dict` container, non-path `template`). User-authored values only. | Phase 53 plan 53-08 | 2026-08-15 |
| R-04 | T-53-SC | No package-manager install task exists anywhere in the phase. Zero new runtime dependencies is a standing v0.9.0 milestone invariant (STACK.md: "Add nothing"); only already-imported stdlib (`os`, `posixpath`, `pathlib`, `dataclasses`) is used. Verified by measurement, not by assertion: no dependency-manifest or workflow file changed in the phase's diff. A `## Package Legitimacy Audit` therefore has no install site to audit. | Phase 53 plans 53-01 … 53-10 | 2026-08-15 |
| R-05 | T-53-07-04, T-53-08-04 | Drive-qualified registry-key shape (`53-REVIEW.md` CR-01) is a **known accepted gap** for this phase. The exploit site (`mkdir`/`copytree` under `_template/<key>/`) does not exist until Phase 54; the destination-collision (OUT-07) and symlink-escape (BLD-06) checks belong alongside the write site rather than ahead of it. Locked as a Deferred Idea in `53-CONTEXT.md` and transferred to Phase 54's own bundle-write threat model. | Phase 53 plans 53-07, 53-08 | 2026-08-15 |

*Accepted risks do not resurface in future audit runs.*

**Phase 54 carry-in:** R-05's two transferred threats (T-53-07-04, T-53-08-04) are open obligations
on Phase 54, not on this phase. Phase 54's threat model must carry them — the deferral is only
valid because the write site does not yet exist.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-15 | 32 | 32 | 0 | /gsd-secure-phase (orchestrator, ASVS L1 grep-depth) |

Verification depth: ASVS level 1. Register was authored at plan time in all 10 PLAN files, so this
run verified declared mitigations rather than scanning for new threats. Mitigation evidence was
re-measured against the working tree and git — not transcribed from SUMMARY prose. No SUMMARY file
in this phase carries a `## Threat Flags` section, so no summary-level flags entered the register.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-15
