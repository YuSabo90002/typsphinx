---
phase: 33
slug: v0-6-4-release-prep
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-28
---

# Phase 33 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `uv lock` → package index resolution | Only network-reaching step that can alter installed code | dependency resolution metadata |
| repository → published wheel metadata | `version` string becomes the identity of a future PyPI artifact | package identity (public) |
| CHANGELOG entry → published GitHub Release body | Text is copied verbatim into a public release announcement | public release claims |
| CHANGELOG entry → downstream upgrade decisions | Presence/absence of breaking-change language drives user decisions | public disclosure |
| private milestone branch → public `main` | Merge makes the four translated planning docs publicly readable | project decision record (non-sensitive) |
| translator → project audit trail | A meaning-changing edit corrupts the decision record | decision-record semantics |
| plan-03 worktree → GSD handler writes to STATE.md | Concurrent framework writes to a file this phase edits | planning-state text |
| prepared tree → irreversible publish (tag, PyPI, Release, PR merge) | The boundary this prep-only phase must not cross | release artifacts |
| repository → live Read the Docs service | SC#3 fetch observes an external service no local test can assert | public URL observation |
| evidence record → future audits / milestone close | Downstream decisions rest on what 33-RELEASE-EVIDENCE.md claims | audit evidence |
| repository → `typsphinx-doc-translations` repository | REL-02's Japanese half resolves against a second repo's tags | cross-repo reference |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-33-01 | Tampering | `uv lock` regeneration of `uv.lock` | low | mitigate | Self-pin bump constrained to 1 insertion / 1 deletion (`git diff --numstat uv.lock`); no transitive line moved. `uv.lock:1379` carries `version = "0.6.4"`. | closed |
| T-33-02 | Spoofing | package version identity in `pyproject.toml` | low | mitigate | `pyproject.toml:7` is `version = "0.6.4"`; grep over `pyproject.toml`, `typsphinx/`, `uv.lock` finds zero remaining `0.6.3` literals. | closed |
| T-33-03 | Spoofing | `### Verified` section claims in CHANGELOG | medium | mitigate | Section restricted to three `git diff`-provable invariants (D-03); 33-RELEASE-EVIDENCE.md records the live diff output backing each. | closed |
| T-33-04 | Repudiation | omission of breaking-change disclosure | medium | mitigate | CHANGELOG 0.6.4 Removed section discloses github.io 404-without-redirect and loss of browser-language auto-redirection (CHANGELOG.md:46–48). | closed |
| T-33-05 | Tampering | historical CHANGELOG entries | low | mitigate | `git diff main...HEAD -- CHANGELOG.md` deletes only the `[Unreleased]` compare link (expected link-block rollover); zero 0.6.3-or-earlier lines modified. | closed |
| T-33-06 | Tampering | project decision record in four translated planning docs | medium | mitigate | 33-03-SUMMARY records byte-identical requirement-ID census, identical heading counts, identical table-row counts before/after translation; prohibitions forbade meaning-changing edits. Human UAT (33-UAT.md test 1) passed the meaning-preservation spot-check. | closed |
| T-33-07 | Information disclosure | Japanese-only project prose becoming broadly legible | low | accept | D-05's explicit intent, owner-decided. Files contain no credentials or private endpoints; granular phase archives stay untranslated. | closed |
| T-33-08 | Denial of service | concurrent handler writes to `.planning/STATE.md` | low | mitigate | Edit confined to the single CONF-06 Deferred-Items table cell; `git diff --numstat` = 1 insertion / 1 deletion; frontmatter and progress fields untouched (33-03-SUMMARY). | closed |
| T-33-09 | Elevation of privilege | irreversible publish actions inside a prep-only phase | high | mitigate | `git tag -l v0.6.4` and `git ls-remote --tags origin v0.6.4` both empty — re-verified live 2026-07-28 during this audit; publish actions forbidden by name in must_haves. | closed |
| T-33-10 | Spoofing | evidence claims in `33-RELEASE-EVIDENCE.md` | high | mitigate | Every assertion backed by verbatim command output; merge-base SHA `771ec56f` cross-checked against live `git merge-base` and 33-CONTEXT.md. | closed |
| T-33-11 | Repudiation | ambiguous empty-diff result | medium | mitigate | Non-empty positive control recorded alongside the empty `typsphinx/` diff, proving pathspec machinery works (33-RELEASE-EVIDENCE.md §Invariant 1). | closed |
| T-33-12 | Information disclosure | evidence file destroyed by name collision | medium | mitigate | Deliverable named `33-RELEASE-EVIDENCE.md`; distinct from verifier-owned `33-VERIFICATION.md` — both coexist in the phase dir. | closed |
| T-33-13 | Tampering | stale external observation presented as current | medium | mitigate | Fresh RTD fetch recorded with ISO-8601 timestamp `2026-07-27T21:15:32Z`; observation kept out of CHANGELOG per D-03 (no standing re-verification mechanism). | closed |
| T-33-SC | Tampering | package-manager installs (all four plans) | low | accept | No new package installed anywhere in the phase; 33-RESEARCH.md Package Legitimacy Audit records the gate not-applicable; `git diff main..HEAD -- uv.lock` empty at plan time apart from the self-pin bump. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-33-01 | T-33-07 | Translation to English is D-05's explicit purpose; the four files hold no credentials or private endpoints. | project owner (D-05) | 2026-07-28 |
| AR-33-02 | T-33-SC | Phase installs no new package; supply-chain gate recorded not-applicable in 33-RESEARCH.md across all four plans. | plan-time disposition | 2026-07-28 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-28 | 14 | 14 | 0 | gsd-secure-phase (L1 short-circuit; register authored at plan time) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-28
