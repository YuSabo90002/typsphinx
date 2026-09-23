# Feature Research

**Domain:** PyPI publishing mechanics — Trusted Publishing (OIDC) + PEP 740 attestations, as delivered by `pypa/gh-action-pypi-publish@release/v1`
**Researched:** 2026-09-23
**Confidence:** HIGH for anything below marked "verified against source/live" — those are either the action's own committed source code (`oidc-exchange.py`, `twine-upload.sh`, `attestations.py`, `action.yml` at `release/v1`, fetched from `raw.githubusercontent.com` on 2026-09-23) or a live `curl` against `pypi.org` run during this research (against `sigstore` 4.5.0 as a known-attested control, and against typsphinx's own live 0.9.6 release as the "before" baseline). MEDIUM/LOW is called out inline per claim.

This file answers one question for the roadmapper/planner: **what, exactly, can be observed after `release.yml` runs, to prove ATT-01 is fixed — without trusting the workflow file itself.**

---

## Success Signals (what a token-free, attested publish looks like)

All of these are things a human or script can check *right after* `release.yml` finishes, ordered cheapest → most rigorous.

### S1. Absence of the ATT-01 warning annotation
**Check:** `gh run view <run-id> --log | grep -c "attestations input ignored"`
**Expect:** `0`
**Complexity:** trivial (gh CLI + grep, no auth beyond repo access)
**Confidence:** HIGH — verified against the action's own source (`twine-upload.sh`, see § "The v0.9.6 Annotation" below). This warning is emitted by the *action*, not PyPI, and fires purely from the local condition "a `password` was supplied." Its absence is a necessary but not sufficient success signal — it only proves the `password:` key is gone, not that PyPI accepted the OIDC exchange.

### S2. Presence of the attestation-generation notice
**Check:** `gh run view <run-id> --log | grep -c "Generating and uploading digital attestations"`
**Expect:** `≥ 1` (once, for the `publish-pypi` step; `publish-testpypi` is explicitly out of scope for v0.9.7 and keeps its token)
**Complexity:** trivial (gh CLI + grep)
**Confidence:** HIGH — verified against source. This is a `::notice::` annotation printed by `twine-upload.sh` immediately before it invokes `attestations.py`, and only when `TRUSTED_PUBLISHING=true` (no password) **and** `attestations` input is not `false` (it defaults to `true` and this milestone deliberately does not set it). Unlike GitHub's `::debug::` lines, `::notice::` annotations are visible in a normal run log without enabling debug logging.

### S3. Twine's own upload gains `--attestations`
**Check:** in the same log, near the `twine upload` invocation, the flags include `--attestations` (alongside `--disable-progress-bar --verbose`).
**Complexity:** trivial (log grep)
**Confidence:** HIGH — verified against source (`TWINE_EXTRA_ARGS="--attestations $TWINE_EXTRA_ARGS"` is only appended inside the same `if` block as S2).

### S4. PyPI Simple JSON API carries a non-null `provenance` field — THE primary machine-checkable oracle
**Check:**
```bash
curl -s "https://pypi.org/simple/typsphinx/" -H "Accept: application/vnd.pypi.simple.v1+json" \
  | jq '.files[] | select(.filename | test("0\\.9\\.7")) | {filename, provenance}'
```
**Expect:** both the wheel and sdist entries show a non-null `provenance` URL, e.g. `"https://pypi.org/integrity/typsphinx/0.9.7/typsphinx-0.9.7-py3-none-any.whl/provenance"`.
**Complexity:** single unauthenticated `curl`; `jq` optional (plain `curl | python3 -m json.tool` works too). No tool installation beyond what's already on any CI runner or dev machine.
**Confidence:** HIGH — verified live, twice, during this research:
  - Against `sigstore` 4.5.0 (known TP+attestation user): `"provenance": "https://pypi.org/integrity/sigstore/4.5.0/sigstore-4.5.0-py3-none-any.whl/provenance"`.
  - Against typsphinx's own **current, unfixed** 0.9.6 release, right now: `{"filename": "typsphinx-0.9.6-py3-none-any.whl", "provenance": None}` and the same for the sdist. This is the live "before" baseline that ATT-01 exists to flip.

**Hazard for whoever writes the AC:** the field only appears on the **Simple Index JSON API** (`/simple/<project>/`, `Accept: application/vnd.pypi.simple.v1+json`, PEP 691), *not* on the older, differently-shaped **legacy JSON API** (`/pypi/<project>/<version>/json`). Verified live against `docs.pypi.org/api/json/`'s own documented example response: that endpoint's `urls[]` file objects carry `digests`, `has_sig` (permanently `false`, a PGP-era artifact), `core-metadata`, etc. — **no `provenance` key at all**. A check written against the legacy JSON API will silently pass-as-absent forever regardless of whether the fix works, because that endpoint never carries this field for any package.

### S5. PyPI Integrity API — names the publishing workflow itself
**Check:**
```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  "https://pypi.org/integrity/typsphinx/0.9.7/typsphinx-0.9.7-py3-none-any.whl/provenance" \
  -H "Accept: application/vnd.pypi.integrity.v1+json"
# then, on 200:
curl -s "https://pypi.org/integrity/typsphinx/0.9.7/typsphinx-0.9.7-py3-none-any.whl/provenance" \
  -H "Accept: application/vnd.pypi.integrity.v1+json" | jq '.attestation_bundles[0].publisher'
```
**Expect:** `200`, then `{"kind": "GitHub", "repository": "YuSabo90002/typsphinx", "workflow": "release.yml", "environment": "pypi"}` (or `environment: null` if PyPI doesn't echo environment for this predicate type — verified live against `sigstore` that `environment` can legitimately be `null` even on a successful attestation).
**Expect on the *unfixed* baseline:** `404` — verified live, right now, against typsphinx's actual 0.9.6 wheel: `HTTP/2 404`. This is the exact negative control the phase planner can cite before the fix ships.
**Complexity:** single unauthenticated `curl`. Slightly more work than S4 but this is the check that closes the loop back to "produced by *this* workflow" rather than just "has *some* attestation" — asserting `publisher.repository` and `publisher.workflow` match is what actually proves the fix, not just that attestations exist.
**Confidence:** HIGH — endpoint URL pattern (`GET /integrity/<project>/<version>/<filename>/provenance`), header, status codes, and field names (`attestation_bundles[].publisher.{kind,repository,workflow,environment}`, `attestation_bundles[].attestations[].{envelope,verification_material}`) all verified against `docs.pypi.org/api/integrity/` AND independently reproduced live against `sigstore` 4.5.0 and typsphinx 0.9.6 in this session.

### S6. `pypi-attestations` CLI — the only check that cryptographically verifies, not just checks presence
**Check:** `pip install pypi-attestations` then `pypi-attestations verify pypi --repository https://github.com/YuSabo90002/typsphinx <wheel-url-or-local-path>`.
**Expect:** exits 0, prints that the Trusted Publisher identity in the provenance matches `--repository` and the Sigstore signature verifies against the file's digest.
**Complexity:** needs a tool installed (one `pip install`); heavier than S4/S5 but the only check in this list that actually walks the Sigstore certificate chain rather than checking for the field's presence.
**Confidence:** HIGH — command form verified against `docs.pypi.org/attestations/consuming-attestations/` and `docs.pypi.org/attestations/producing-attestations/`.

### S7. PyPI web UI (project/file page)
**Claim:** PyPI's project page shows a "Provenance" indicator per file, linking to the Sigstore transparency-log (Rekor) entry that names the git ref/workflow that produced it.
**Complexity:** web UI glance — but **cannot be scripted/curled**. Verified empirically in this session that `https://pypi.org/project/<name>/<version>/` is a client-side-rendered single-page app (curl returns an 88-line shell with a `#loading-error` div and no server-rendered file list, hashes, or attestation text) — a script cannot grep this page for confirmation; a human must open it in a real browser, or the check must go through S4/S5 instead.
**Confidence:** MEDIUM — the *capability* is confirmed by two independent sources (PyPI's own 2024-11-14 announcement blog: "a new page on PyPI's web UI, displaying details for individual files, including the presence of any attestations"; Simon Willison's 2024-11-14 post, which describes seeing "provenance information" on a file page linking to "this Sigstore log entry... including the Git hash that was used to build the package") but the *exact current wording/placement* could not be re-verified against primary-source HTML in this session because the page requires JS execution. Treat as a supplementary, human-only confirmation — not the acceptance oracle.

---

## Failure Signals (verified against `oidc-exchange.py` source, `release/v1`)

All four failure modes below share one important trait the planner should encode directly into the AC: **(a), (b), and (d) are indistinguishable from the top-line GitHub error text alone.** Only (c) fails differently (client-side, before any PyPI network call).

### F1 — No Trusted Publisher registered
**Symptom:** GitHub successfully mints an OIDC token (so `id-token: write` and no third-party-fork issue), but PyPI's `mint-token` endpoint rejects it. The action's `die()` prints, verbatim from source:
```
Token request failed: the server refused the request for the following reasons:

* `invalid-pending-publisher`: <description>
```
or `invalid-publisher` — per `docs.pypi.org/trusted-publishers/troubleshooting/`: "the OIDC token itself is well-formed... but doesn't match any known (pending) OIDC publisher."
In GitHub's log this becomes `::error::Trusted publishing exchange failure: Token request failed: the server refused the request...` and the step exits 1; a matching multi-line block is also appended to the run's **Job Summary** (`GITHUB_STEP_SUMMARY`), including the full rendered OIDC claim set: `sub`, `repository`, `repository_owner`, `repository_owner_id`, `workflow_ref`, `job_workflow_ref`, `ref`, `environment` (any claim GitHub didn't send back is rendered as literal `MISSING`).
**Confidence:** HIGH — exact strings from source; error-code taxonomy (`not-enabled`, `invalid-payload`, `invalid-token`, `invalid-pending-publisher`, `invalid-publisher`) cross-checked against `docs.pypi.org/trusted-publishers/troubleshooting/`.

### F2 — Environment name mismatch (`environment: pypi` in the workflow vs. what's registered on PyPI)
**Symptom:** identical top-line error to F1 (`invalid-publisher`/`invalid-pending-publisher`) — the `environment` claim is just one more field PyPI matches. Diagnosis requires opening the Job Summary or full log and comparing the rendered `environment:` claim against PyPI's Publishing settings for the project.
**Confidence:** HIGH (docs explicitly call this distinction out: "check if the workflow is using the same environment as configured when the publisher was configured on PyPI").

### F3 — Missing `id-token: write`
**Symptom:** fails *before any PyPI network call*, inside `_detect_credential()` — GitHub itself refuses to mint the token, raising `id.IdentityError`. Verbatim message:
```
OpenID Connect token retrieval failed: <identity_error>

This generally indicates a workflow configuration error, such as insufficient
permissions. Make sure that your workflow has `id-token: write` configured
at the job level...
```
→ `::error::Trusted publishing exchange failure: OpenID Connect token retrieval failed: ...`.
**Not currently exercisable against typsphinx's own workflow** — `id-token: write` is already declared at top level (`release.yml:13-15`, confirmed present). Listed here so the planner recognizes this failure shape (client-side, pre-network) is categorically different from F1/F2/F4 (server-refused) if it ever needs debugging.
**Confidence:** HIGH — verbatim from source.

### F4 — Workflow filename mismatch (e.g. repo renamed, or publisher registered against a different filename than `release.yml`)
**Symptom:** identical `invalid-publisher` server-refusal path as F1/F2. Docs single this out as a common regression: "Renaming the GitHub repository, transferring it to a new owner, or renaming the workflow file breaks trusted publishing... check that the `repository_owner`, `repository` and workflow filename values are the same on both sides."
**Recovery UI:** the Trusted Publisher registration/edit page is `https://pypi.org/manage/project/<name>/settings/publishing/` — this exact path is also what the action itself links to in its own "Create a Trusted Publisher" nudge (`twine-upload.sh`'s `MAGIC_LINK_MESSAGE`, built as `${INDEX_URL}/manage/project/${PACKAGE_NAME}/settings/publishing/?provider=github&owner=...&repository=...&workflow_filename=...`), confirmed against source.
**Confidence:** HIGH.

**Planner note:** because F1/F2/F4 all produce the same top-line text, an AC like "the run fails with an OIDC error" is not actionable on its own — write it as "the run's Job Summary contains the rendered claim block, and the `environment`/`repository`/`workflow_ref` values in it are checked by hand against the Trusted Publisher's settings page" if this milestone ever needs to specify failure-path behavior (it currently only needs to specify the success path — see PROJECT.md's rollback note).

---

## The v0.9.6 Annotation, Confirmed at Source

> "The workflow was run with the 'attestations: true' input, but an explicit password was also set, disabling Trusted Publishing. As a result, the attestations input is ignored."

**Emitter:** the `pypa/gh-action-pypi-publish` action's own `twine-upload.sh` script (runs inside the action's Docker container) — **not PyPI, and not twine**. Confirmed by reading the literal string constant in source, `release/v1`:

```bash
ATTESTATIONS_WITHOUT_TP_WARNING="::warning title=attestations input ignored::\
The workflow was run with the 'attestations: true' input, but an explicit \
password was also set, disabling Trusted Publishing. As a result, the \
attestations input is ignored."

[[ "${INPUT_USER}" == "__token__" && -z "${INPUT_PASSWORD}" ]] \
    && TRUSTED_PUBLISHING=true || TRUSTED_PUBLISHING=false
...
if [[ "${INPUT_ATTESTATIONS}" != "false" ]] ; then
    if ! "${TRUSTED_PUBLISHING}" ; then
        echo "${ATTESTATIONS_WITHOUT_TP_WARNING}"
        INPUT_ATTESTATIONS="false"
    fi
```

It fires from one purely **local** condition — "a `password` was supplied" — evaluated before any network call to PyPI. It has nothing to do with whether PyPI would even recognize the trusted publisher; it is the action self-detecting a contradictory input combination.

**Exact converse when it succeeds:** this whole `if` branch is skipped. No warning is printed, `INPUT_ATTESTATIONS` stays `'true'`, and execution falls straight through to generating attestations (S2/S3 above). There is **no explicit "trusted publishing enabled" success message** at this point in the script — success is proven by absence of the warning plus presence of the `::notice::Generating and uploading digital attestations` line (S1+S2), not by any dedicated "OK" line. This matters for writing the AC: don't look for positive confirmation text that doesn't exist; look for the specific notice annotation plus absence of the specific warning.

---

## What Attestations Do NOT Give You

### Table stakes (what TP + default attestations actually deliver)
| Capability | What it proves | Complexity to observe |
|---|---|---|
| Provenance record | A specific GitHub Actions workflow (`owner/repo` + `workflow filename` [+ `environment`]) uploaded this exact file, cryptographically bound to its SHA-256 digest, signed via a short-lived Sigstore (Fulcio) certificate, logged in the public Rekor transparency log | S4/S5 above (curl) |
| No long-lived secret in GitHub | The `PYPI_API_TOKEN` repo secret becomes unnecessary once OIDC works (this is a **Trusted Publishing** property, separate from attestations — see next row) | absence of the secret after retirement; not directly observable per-run |

### Differentiators / nuance the roadmap should not oversell
- **Trusted Publishing and attestations are two separate PyPI features that share one prerequisite.** TP removes the stored token; PEP 740 attestations add provenance. This milestone bundles both because they share the same `id-token: write` + no-`password:` gate, but they are independently toggleable (`attestations: false` would keep TP without attestations). Worth stating plainly so ATT-01's scope isn't misread as "just attestations."
- **The default attestation is the "PyPI Publish" predicate, not "SLSA Provenance."** Per `docs.pypi.org/attestations/` and corroborated by a secondary source (pydevtools): PyPI currently accepts two predicate types, `SLSA Provenance` (describes *how* the file was built) and `PyPI Publish` (asserts *only* that a trusted publisher uploaded the file — its `predicate` field is empty; the identity is what carries the claim). `gh-action-pypi-publish`'s default `attestations: true` generates the **PyPI Publish** predicate only. It does **not**, by itself, cryptographically assert "built from commit X via these exact build steps" — that stronger claim is the separate SLSA Provenance predicate, which is not what this milestone's default configuration produces.

### Anti-features — what NOT to claim in release notes / what NOT to build
| Claim/build temptation | Why it's wrong or premature | What's actually true instead |
|---|---|---|
| "pip now verifies our package is authentic" | **False.** Confirmed by two independent secondary sources (Trail of Bits' own PEP 740 blog: "downstream verification... is notably missing... [PEP 740] doesn't mandate a verification flow for installing clients like pip and uv"; pydevtools: "pip and uv do not yet reject unsigned packages by default; attestations today are evidence a consumer can record and audit rather than an install-time gate") | `pip install typsphinx` behaves identically whether or not the file has an attestation. Verification is opt-in, via S6 (`pypi-attestations` CLI) or third-party plugins (e.g. `trailofbits/pip-plugin-pep740`, an early example plugin, not pip core) |
| Building custom install-time attestation enforcement for typsphinx's own consumers | Out of scope for a publishing-pipeline fix; also duplicates work the ecosystem (pip/uv maintainers, per the `discuss.python.org` PEP 751 lockfile thread) is actively discussing upstream | Nothing to build here — this milestone's job is producing the attestation, not consuming it |
| Treating the disappearance of the ATT-01 warning as sufficient proof | It only proves the `password:` key is gone; a misconfigured Trusted Publisher (F1/F2/F4 above) would *also* make the warning disappear from the log **if the job failed before reaching that line** — actually no: the warning line is evaluated unconditionally as part of computing `TRUSTED_PUBLISHING`, before the OIDC exchange happens, so it fires/doesn't-fire purely on `password:` presence regardless of OIDC outcome. So S1's absence is necessary-but-not-sufficient for a different reason: a *successful* run could still theoretically be one where the publisher registration is subtly wrong in a way PyPI didn't catch (extremely unlikely given PyPI validates on every mint-token call) — but the real gap is that S1 alone doesn't independently confirm PyPI actually served provenance. Always pair S1/S2 (log-based) with S4 or S5 (PyPI-served-state-based) before declaring the fix proven | Use S1+S2 (log) **and** S4 or S5 (PyPI's own served state) together, not either alone |

---

## Idempotency / Retry (drives the rollback plan)

- **PyPI filenames are permanently immutable.** Confirmed via `pypi/warehouse#10541`: "PyPI does not allow for a filename to be reused, even once a project has been deleted and recreated." A failed publish that nonetheless got a file onto PyPI cannot be retried under the same version — the standard failure is `400 Bad Request: File already exists` (consistent phrasing across multiple independent reports: Stack Overflow, GitLab forum, python-poetry discussions).
- **`gh-action-pypi-publish`'s `skip-existing` input defaults to `'false'`**, confirmed against `action.yml` (`skip-existing: … default: 'false'`, and its deprecated alias `skip_existing` likewise `'false'`). typsphinx's `publish-pypi` step (`release.yml:141-144` at HEAD) does **not** set `skip-existing`, so it inherits `false`. Practical consequence: a re-run of the same tag after a partial success will hit `400 File already exists` on any file it already placed, rather than silently completing — twine does not upsert.
- **This confirms — does not merely repeat — the todo's own stated rollback plan** ("if the OIDC exchange fails, restore `password:` and re-tag as 0.9.8, leaving 0.9.7 unclaimed on PyPI"): the recovery unit is a new version number, never a same-version retry, and that is a direct, verified consequence of PyPI's immutable-filename rule plus this action's non-`skip-existing` default, not just caution.
- **Where in the pipeline a failure lands matters for whether *anything* reached PyPI at all.** `publish-pypi`'s single "Publish to PyPI" step, per action source, runs in this order: (1) OIDC exchange (F1–F4 failure modes, no PyPI upload has been attempted yet at this point — nothing is claimed), (2) `twine check` on the dists, (3) attestation generation (`attestations.py` — a Sigstore signing failure here, e.g. a transient OIDC hiccup, also happens *before* any `twine upload` call), (4) the actual `twine upload`. So: **any OIDC or attestation-generation failure (F1–F4, or a Sigstore signing error) leaves PyPI completely untouched** — no filename is claimed, and a same-version retry (not a version bump) is actually safe in that specific case. A version bump is only strictly required if the failure happens *during or after* the `twine upload` call itself (e.g., one of the two files uploads and the process is killed before the second). Worth confirming which sub-step failed before assuming 0.9.8 is needed, rather than bumping reflexively.
- **DAG consequence:** `create-release` `needs: [build, publish-pypi]`, so any `publish-pypi` failure (including all of F1–F4) stops the pipeline before the GitHub Release is created — there's no risk of a GitHub Release existing for a version that never reached PyPI.

---

## Feature Dependencies

```
[id-token: write present]           (already true, release.yml:13-15)
    └──requires for OIDC to be attempted at all──> [no `password:` set on publish-pypi step]  (ATT-01's actual code change)
                                                        └──requires for PyPI to accept it──> [Trusted Publisher registered on PyPI]  (owner action, PyPI-side, before the tag push)
                                                                                                 └──unlocks──> [attestations: true default takes effect] ──produces──> [provenance in Simple JSON API + Integrity API]
```

### Dependency Notes
- **Deleting `password:` requires the PyPI-side Trusted Publisher to already exist**, or the very first tag push after the code change fails outright (F1) — this is why PROJECT.md correctly orders PyPI-side registration *before* the tag, not after.
- **The `attestations: true` default requires Trusted Publishing to have succeeded**, not merely been attempted — per `action.yml`'s own description: "Only works with PyPI and TestPyPI via Trusted Publishing." If OIDC fails, attestation generation never runs (see Idempotency section above) — the two are sequential, not parallel, inside the single action invocation.
- **The proof (S4/S5) requires the fix to have gone all the way through a real tag push** — nothing here is observable from a `workflow_dispatch` dry run against non-`pypi.org` state, and nothing is observable from re-reading the YAML. This is the exact shape PROJECT.md already calls out from the REL-04/v0.7.0 precedent.

---

## MVP Definition (for the AC the planner writes)

### Must be checked at v0.9.7's real tag push (P1 — non-negotiable for proving ATT-01)
- [ ] **S1** — run log contains zero occurrences of `"attestations input ignored"`
- [ ] **S2** — run log contains at least one occurrence of `"Generating and uploading digital attestations"`
- [ ] **S4** — `pypi.org/simple/typsphinx/` (Simple JSON API, **not** the legacy `/pypi/.../json` endpoint) shows non-null `provenance` for both the 0.9.7 wheel and sdist
- [ ] **S5** — Integrity API returns `200` for both files, with `publisher.repository == "YuSabo90002/typsphinx"` and `publisher.workflow == "release.yml"`

### Should be checked, adds rigor (P2)
- [ ] **S6** — `pypi-attestations verify pypi` exits 0 against the published wheel
- [ ] **S7** — human glance at the PyPI project page shows a Provenance/attestation indicator (supplementary only — cannot be scripted)

### Deliberately not in scope for this milestone (P3 / future)
- [ ] Any pip/uv-side install-time attestation enforcement (upstream ecosystem work, not this project's to build — see Anti-features)
- [ ] SLSA Provenance predicate (stronger than the default "PyPI Publish" predicate; not produced by the current default configuration and not requested by ATT-01)
- [ ] `publish-testpypi`'s equivalent switch (explicitly out of scope per PROJECT.md; keeps `TEST_PYPI_API_TOKEN`)

## Feature Prioritization Matrix

| Check | Value (proves the fix) | Cost | Priority |
|---|---|---|---|
| S1/S2 (log grep) | MEDIUM (necessary, not sufficient alone) | LOW | P1 |
| S4 (Simple JSON API) | HIGH (primary oracle) | LOW | P1 |
| S5 (Integrity API) | HIGH (names the workflow, not just "has attestation") | LOW | P1 |
| S6 (`pypi-attestations` CLI) | HIGH (only cryptographic check) | MEDIUM (tool install) | P2 |
| S7 (web UI glance) | LOW (supplementary, human-only, unscriptable) | LOW (if a human is looking anyway) | P2 |

---

## Sources

**Primary / source-code (HIGH confidence, fetched directly in this session):**
- `pypa/gh-action-pypi-publish` at `release/v1`: `oidc-exchange.py`, `twine-upload.sh`, `attestations.py`, `action.yml` — https://github.com/pypa/gh-action-pypi-publish (raw files via raw.githubusercontent.com)
- PyPI docs — Trusted Publishers: https://docs.pypi.org/trusted-publishers/using-a-publisher/ , https://docs.pypi.org/trusted-publishers/troubleshooting/
- PyPI docs — Attestations: https://docs.pypi.org/attestations/ , https://docs.pypi.org/attestations/producing-attestations/ , https://docs.pypi.org/attestations/consuming-attestations/ , https://docs.pypi.org/attestations/security-model/
- PyPI docs — APIs: https://docs.pypi.org/api/integrity/ , https://docs.pypi.org/api/json/ , https://docs.pypi.org/api/index-api/
- PEP 740 (historical/canonical spec pointer): https://peps.python.org/pep-0740/
- `pypi/warehouse` issue #10541 (filename immutability, even after project deletion): https://github.com/pypi/warehouse/issues/10541
- Live `curl` reproductions against `pypi.org` (this session, 2026-09-23): Simple JSON API + Integrity API for `sigstore` 4.5.0 (known-attested control) and for typsphinx's own live 0.9.6 wheel/sdist (unfixed baseline — `provenance: null`, Integrity API `404`)

**Secondary (MEDIUM confidence, used for wording/UI description and cross-checks, not code-of-record):**
- PyPI blog, "PyPI now supports digital attestations" (2024-11-14): https://blog.pypi.org/posts/2024-11-14-pypi-now-supports-digital-attestations
- Trail of Bits blog, "Attestations: A new generation of signatures on PyPI" (2024-11-14): https://blog.trailofbits.com/2024/11/14/attestations-a-new-generation-of-signatures-on-pypi
- Simon Willison, "PyPI now supports digital attestations" (2024-11-14, describes the web UI's rendered provenance view): https://simonwillison.net/2024/Nov/14/pypi-digital-attestations
- pydevtools, "What is PEP 740?": https://pydevtools.com/handbook/explanation/what-is-pep-740
- pydevtools, "How to Publish to PyPI with Trusted Publishing" (verify-the-upload / troubleshooting phrasing): https://pydevtools.com/handbook/how-to/how-to-publish-to-pypi-with-trusted-publishing
- Are we PEP 740 yet? tracker: https://trailofbits.github.io/are-we-pep740-yet
- `trailofbits/pip-plugin-pep740` (example of the *absence* of install-time enforcement in pip core): https://github.com/trailofbits/pip-plugin-pep740

**Project-internal (read as required reading for this task):**
- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` (Current Milestone v0.9.7 section)
- `/home/yuta/Documents/typsphinx/.planning/todos/pending/2026-09-22-release-yml-uses-a-pypi-api-token-so-trusted-publishing-and.md` (ATT-01)
- `/home/yuta/Documents/typsphinx/.github/workflows/release.yml` (current state at HEAD `c4eec213`, confirmed `password:` still present in both `publish-pypi` and `publish-testpypi`)

---
*Feature research for: PyPI Trusted Publishing / PEP 740 attestation observability*
*Researched: 2026-09-23*
