# Pitfalls Research

**Domain:** Migrating an existing, published PyPI package's release workflow from a long-lived API token to PyPI Trusted Publishing (OIDC), in a GitHub Actions workflow that publishes on every `v*` tag push with no `if:` gate.
**Researched:** 2026-09-23
**Confidence:** MEDIUM-HIGH (primary claims verified against official PyPI docs and `pypa/gh-action-pypi-publish`'s own README/issue tracker; community-report claims cross-checked across 2+ independent sources; a few claims are single-source and labelled LOW)

**Scope note:** typsphinx's `release.yml` (`:126-144`) already has almost every prerequisite in place — `id-token: write` at the top level, an `environment: pypi` with a manual-approval gate, and a `publish-testpypi` job kept deliberately out of scope. The only planned diff is deleting one `password:` line, done *after* registering a Trusted Publisher on PyPI. That narrowness is exactly why the pitfalls below matter: almost everything that can go wrong is a **registration/sequencing** mistake or a **false-positive verification** mistake, not a code mistake.

---

## Critical Pitfalls

### Pitfall 1: Workflow filename or environment name mismatch on the PyPI Trusted Publisher registration

**What goes wrong:**
PyPI's GitHub Trusted Publisher is identified by four fields: repository owner, repository name, **workflow filename** (exact, including `.yml`/`.yaml` extension — the registration form does not accept a path, just the bare filename), and an optional **environment name**. If any of these differs from what the OIDC token's claims actually say, the publish step fails outright with `invalid-publisher` (unregistered token) or `invalid-pending-publisher` (registered as a pending publisher but claims still don't match).

**Why it happens:**
- Typing `release.yaml` instead of `release.yml` (typsphinx's actual file, confirmed at `.github/workflows/release.yml`).
- Registering with no environment name when the workflow *does* specify `environment: pypi` (or vice versa — registering `pypi` when the workflow's job has no `environment:` block, or a differently-named one). PyPI's troubleshooting docs explicitly call out "check if the workflow is using the same environment as configured when the publisher was configured on PyPI" as the #1 cause of `invalid-pending-publisher`/`invalid-publisher`.
- Copy-pasting a registration example from a tutorial that uses a different filename convention (`publish.yml`, `ci.yml`, `sdk_publish.yaml` all appear in real-world examples).

**How to avoid:**
Register using the exact strings read directly from `release.yml`, not from memory or a template: repository owner = the GitHub org/user that owns `typsphinx`, repository = `typsphinx`, workflow filename = `release.yml` (bare filename, no `.github/workflows/` prefix), environment = `pypi` (matches `:131-132`). Do this by having the person registering open the actual file (or `git show HEAD:.github/workflows/release.yml`) side by side with the PyPI registration form, not by typing from recollection.

**Warning signs:**
The very first tag-push run after `password:` is deleted fails at the `Publish to PyPI` step with `invalid-publisher` / `The workflow 'release.yml' is not registered as a trusted publisher` / `OpenID Connect token could not be verified`. This is a hard failure, not silent — but it happens on the **real tag**, which is why registering correctly *before* the tag is pushed is the only real prevention (see Pitfall 4).

**Phase to address:**
PyPI-side registration step, which must run strictly before the `password:`-removal commit is tagged. This is a pre-tag, owner-performed, manual action — it cannot be automated or verified by CI in advance (see Pitfall 4).

---

### Pitfall 2: Registering the wrong account type, or a registration that silently targets the wrong PyPI project

**What goes wrong:**
Two distinct sub-failures reported in PyPI's own troubleshooting docs and on GitHub/Reddit:
1. A **"pending" publisher** (used to let Trusted Publishing create a *new* PyPI project on first upload) requires typing the PyPI project name yourself. If that typed name doesn't match what the build actually produces (e.g. `typsphinx` vs `Typsphinx` vs `type-sphinx`), the first upload creates the *wrong* project, or fails with "This project already exists, create an ordinary Trusted Publisher instead."
2. Because typsphinx already exists on PyPI (0.9.6 is live), the **pending-publisher flow does not apply at all** — the registration must go through "Adding a Trusted Publisher to an Existing PyPI Project" (a project-scoped registration reached via Manage → Publishing on the existing `typsphinx` project page), not the account-level "pending publisher" page. Using the wrong page is an easy mistake because most tutorials (pyOpenSci, blog posts) demonstrate the pending/new-project flow since it's the more commonly documented one for greenfield projects.

**Why it happens:** Most public tutorials optimize for the "I'm setting this up from scratch" case, not the "I already have a published project" case — exactly the asymmetry this milestone's context flags. The two PyPI UI flows (account-level pending publisher vs. project-level publisher) look similar but are reached from different places and behave differently on first use.

**How to avoid:** Register via the **existing `typsphinx` project's own "Publishing" management page** (`https://pypi.org/manage/project/typsphinx/settings/publishing/` — reached via "Manage" on the project, not the account-level pending-publisher page). This project already exists, so there is no version-name ambiguity to get wrong — confirm this is the flow used, not the account-level "add a pending publisher" flow meant for projects that don't exist yet.

**Warning signs:** If the registration form asks for a "PyPI project name" field that you have to type freehand, you are on the *pending*-publisher (new-project) flow, which is not what an existing project needs — stop and navigate to the project's own settings page instead.

**Phase to address:** Same pre-tag PyPI-side registration step as Pitfall 1.

---

### Pitfall 3: Repository rename or fork leaves a stale publisher registration that looks fine until the token doesn't verify

**What goes wrong:** PyPI's own troubleshooting doc names this as a specific, previously-seen case: "`invalid-publisher` for a previously-working project: this usually indicates a typo or that something has changed on either side. One example we've seen is when a source repository is renamed, and the configuration on PyPI continues to use the old repository name." A fork behaves the same way — a fork's OIDC claims carry the fork's own owner/repo, not the upstream's, so a publisher registered against the upstream repo will never authenticate from a fork's Actions run (this is by design, not a bug, but it surprises people who assume "the workflow file is identical").

**Why it happens:** GitHub repository renames are routine (org moves, username changes) and don't require touching `release.yml`, so nothing in the codebase signals that PyPI's registration has gone stale. This is a *dormant* mismatch — it doesn't fail until the next Trusted-Publishing-authenticated run.

**Why this doesn't currently apply, but is worth recording:** typsphinx's repository has not been renamed and this migration is not happening from a fork — but if a rename or ownership transfer ever happens *after* this migration lands, the very next tag push will fail with no advance warning, because nothing in CI checks the PyPI-side registration against the current repo identity.

**How to avoid:** No code-side prevention exists (PyPI does not expose the registration via API for CI to check). The only mitigation is process: if the repository is ever renamed or transferred after this milestone, re-verify the Trusted Publisher registration on PyPI as part of that rename's own checklist, before the next tag.

**Warning signs:** A tag push that used to publish fine now fails at `invalid-publisher` with no `release.yml` changes in the diff — check whether the repo was renamed/transferred since the last successful publish.

**Phase to address:** Not this milestone's own phases (no rename is planned) — but worth one line in the workflow file's own comments or in `CLAUDE.md`'s release-process notes, so a future rename doesn't rediscover this from a failed production tag.

---

### Pitfall 4: The "looks correct but was never exercised" trap — this project's own recurring failure shape (REL-04, and now ATT-01)

**What goes wrong:** A workflow-file change that is textually correct, reviewed, and merged to `main` sits unexercised because the only thing that exercises `publish-pypi` is a real `v*` tag push — and this project does not tag on every merge. The file "looking right" gets mistaken for "proven right." This is not hypothetical for typsphinx: REL-04 (the `create-release` job) was wrong for an entire milestone (v0.7.0) before a real tag push surfaced `uv: command not found`, and ATT-01 itself — the exact defect this milestone fixes — was only discovered because a *previous*, unrelated tag push (v0.9.6) happened to carry an annotation about it. The workflow file had looked correct (permissions present, environment present) for at least three prior milestones (v0.6.x onward) while silently never using Trusted Publishing.

**Why it happens:** GitHub Actions workflow files cannot be meaningfully dry-run for tag-triggered, environment-gated, secret-touching jobs — `act` and similar local runners cannot simulate OIDC exchange with PyPI, environment approval, or PyPI's server-side validation. `workflow_dispatch` on this same workflow *can* technically trigger `publish-pypi` (it has no `if:` gate — see the project's own **Key context** note), but running it manually still publishes to **production PyPI** with whatever `pyproject.toml` version is checked out, so it is not a safe rehearsal path either; it just moves the real-tag risk earlier without changing its nature.

**What evidence actually proves Trusted Publishing is on** (per this project's own todo and PyPI's own semantics):
1. **The absence of the specific GitHub Actions annotation**: `The workflow was run with the 'attestations: true' input, but an explicit password was also set, disabling Trusted Publishing.` No such annotation on the `publish-pypi` job's run = the `password:` path was not taken.
2. **The PyPI project page showing a Provenance/attestation badge** for the specific uploaded files of that release (wheel and sdist each individually attested — PEP 740). This is visible on `https://pypi.org/project/typsphinx/<version>/#history` or the file details page after upload.
3. **The run log's own `pypa/gh-action-pypi-publish` step output** showing the OIDC exchange happening (no `password set by command options` / `username: __token__` lines — those specifically indicate the token path was used, confirmed in a real `--verbose` log excerpt from `pypa/gh-action-pypi-publish#263`).

**What evidence FALSELY looks like proof (do not accept these alone):**
- **"The upload succeeded."** A successful upload is not evidence of Trusted Publishing — v0.9.6 uploaded successfully via a plain API token, with attestations silently dropped. Success only proves *some* valid credential was used.
- **"`id-token: write` and `environment: pypi` are present in the file."** These are necessary but not sufficient — v0.9.6's run had both, and still went down the token path, because `password:` overrides them. The presence of the permission is not evidence the permission was *used*.
- **"The diff removes `password:` and nothing else broke in review."** Code review of a workflow YAML file cannot observe PyPI-side registration state — a correct diff against an unregistered PyPI Trusted Publisher still fails, and a correct diff against a *registered* one still needs to be seen executing, not just read.
- **"CI is green."** `publish-pypi`'s only failure mode from a registration mismatch is the step itself failing loudly — but a *different* misconfiguration (Pitfall 5's silently-dropped-attestations family) produces a **green, successful run with no attestation**, which is indistinguishable from success in the Actions UI. Green CI proves the upload happened; it does not prove attestations were attached.

**Prevention:** Treat "proof" as the two things a human must go look at *after* the real 0.9.7 tag run completes — the annotation absence and the PyPI attestation badge — not as something inferable from the diff or from CI's pass/fail status. This is already correctly captured as the milestone's own explicit acceptance criterion ("Proof at a real tag push"); the risk is treating any earlier signal (file review, `workflow_dispatch` test run against production, green CI) as a substitute.

**Phase to address:** This is the framing for the entire milestone's verification step, not one phase — but concretely, whichever phase performs "push the v0.9.7 tag" must include, as an explicit gate before calling the milestone done, both (a) fetching the run's annotations/log for the absence of the disabling-message, and (b) visiting the PyPI project page for the attestation badge. Neither should be inferred from "the release completed" or "no errors were reported."

---

### Pitfall 5: Attestations silently absent — every way the upload can succeed while PEP 740 attestations are NOT attached

This project's own defect (ATT-01) is exactly this class, so treat this enumeration as load-bearing for the verification step in Pitfall 4.

| # | Cause | Why it's silent | Applies to typsphinx? |
|---|-------|------------------|------------------------|
| 1 | **`password:` (or `user:`) explicitly set**, even with a Trusted Publisher registered | The action treats an explicit credential as an unambiguous choice, disables Trusted Publishing entirely, and — per this project's own measured annotation — silently *ignores* the (default-on) `attestations: true` input rather than erroring. This is exactly ATT-01. | **Yes — this is the exact defect being fixed.** Also present verbatim in `publish-testpypi` (`:241-245`), out of scope for this milestone by design. |
| 2 | **Trusted Publishing used from within a reusable/called workflow** | `pypa/gh-action-pypi-publish`'s own README states this is "the only case that is explicitly unsupported at the moment" and asks users not to report bugs about it — attestation generation fails outright in this shape (`gh-action-pypi-publish#283`, `langchain-ai/langchain#27765`, worked around there with `attestations: false`). | No — `release.yml`'s `publish-pypi` job is a top-level job in a non-reusable workflow, not called via `workflow_call`. Worth a one-line guard if the workflow is ever refactored into a reusable one later. |
| 3 | **Action pinned to a version older than v1.11.0** | Attestation generation/upload was off-by-default before v1.11.0 and became on-by-default starting there. A pin to an old SHA/tag would silently produce no attestations even with Trusted Publishing correctly configured. | Low risk — `release.yml:142` uses the floating `@release/v1` tag, which tracks current releases, not a pinned old SHA. Confirm at execution time that `@release/v1` currently resolves to ≥ v1.11.0 (it does as of the current release line, per the README's own note). |
| 4 | **Files in `dist/` are not "actually files"** (symlinks, or a build step that leaves a directory named like a distribution) | `pypa/gh-action-pypi-publish#256`: `Attestation generation failure: The following paths look like distributions but are not actually files.` The upload can still proceed for plain-token flows, but attestation generation specifically refuses non-regular files. | Unlikely — `build:` (`:108-124`) runs `uv build` directly into `dist/` and uploads via `actions/upload-artifact`, and `publish-pypi` downloads that same artifact fresh via `actions/download-artifact@v8` — a normal, non-symlinked file set. |
| 5 | **Build artifact not produced in the same run / stale `dist/` reused** | Attestations sign the exact bytes uploaded, and are requested against whatever is physically present in `dist/` at the time the action runs — a `dist/` populated by an earlier, different build (e.g., manually re-running just the publish job against cached artifacts, or a race between concurrent runs) attests the wrong bytes or an already-consumed artifact fails PyPI-side verification (`Could not verify the uploaded artifact using the included attestation: Verification failed: 0 of 2 policies succeeded`, `gh-action-pypi-publish#283`). | Low risk as structured — `publish-pypi` (`needs: build`) always downloads the `dist-packages` artifact produced by *that same run's* `build` job (`:129, 135-139`), not a cached or externally-supplied `dist/`. |
| 6 | **PyPI-side eligibility**: attestation upload requires the Trusted Publishing OIDC identity and the uploaded metadata to match (Core Metadata version support, etc.) | `malloryai/malloryapi#9`: an action version too old to emit Core Metadata 2.5 got its upload rejected outright (`Invalid distribution metadata: '2.5' is not a valid metadata version`) once Hatchling started emitting it — not an attestation-specific bug, but the same "silently-stale pinned action" shape applies to attestation support too. | Low risk — same floating `@release/v1` tag as items 2–3, and `build:` already runs `twine check dist/*` (`:113-114`) as an independent metadata sanity check before upload. |
| 7 | **Non-standard `packages-dir`/glob picking up non-distribution files** | Attestation generation walks whatever `packages-dir` resolves to; stray files there (e.g. a checksum file, a `.tar.gz.asc`) can trip the "not actually files" or "not a distribution" checks. | Low risk — `publish-pypi` uses the action's default `dist/` with nothing else downloaded into that directory in the job. |

**Prevention (all rows):** Verified directly (Pitfall 4's evidence, item 2 — the PyPI attestation badge) rather than assumed from any single row's absence — since more than one of these can independently suppress attestations, ruling out row 1 (deleting `password:`) does not, by itself, prove attestations are now present.

**Phase to address:** Row 1 is the literal ATT-01 fix (the workflow-edit phase). Rows 2–7 are pre-existing structural properties of `release.yml` that already avoid the failure mode — no code change needed for them, but the verification step (Pitfall 4) should not stop at "the `password:` line is gone"; it should look at the actual attestation badge, which is the only signal that rules out all seven rows at once.

---

### Pitfall 6: Environment approval, OIDC token minting, and short token expiry — what actually interacts and what doesn't

**What goes wrong (real interaction):** PyPI's own Trusted Publishing security-model docs state the minted PyPI API token is short-lived — **expires no more than 15 minutes after the OIDC exchange**. The `pypa/gh-action-pypi-publish` step requests GitHub's OIDC token and immediately exchanges it for PyPI's short-lived token *during that step's execution* — which happens **after** the job has cleared the environment's required-reviewer approval gate (GitHub does not start running a job's steps, including OIDC token requests, until the environment protection rule is satisfied). So the 15-minute PyPI token window opens only once a human has already approved the run; a slow approval does not, by itself, cause the PyPI token to expire before use. This is the interaction people expect to be dangerous and, per the documented mechanics, is not.

**What actually does go wrong around approval, per real-world reports:**
- **A required-reviewer gate with no branch restriction is a weaker control than it looks.** `docs.bswen.com`'s migration checklist and `snarky.ca`'s guide both emphasize required reviewers as the main protection *because* OIDC removes the "stolen secret" attack vector but not the "malicious or accidental workflow trigger" vector — the approval gate is what stops an attacker (or an accidental `workflow_dispatch`) from publishing without a human clicking approve, not something that interacts badly with OIDC.
- **A newly-created environment with no protection rules configured yet auto-permits the first run against it.** Not applicable here — `pypi` already exists and has been used with its manual-approval gate across multiple prior published releases (v0.6.x–v0.9.6), so this risk is already closed for typsphinx specifically. Flagging only because it is the one way "environment approval" can be silently absent despite the YAML declaring `environment: pypi`.
- **Concurrent/matrix jobs against the same environment can each independently require approval**, multiplying manual-approval friction — not applicable here, `publish-pypi` is a single job, not a matrix.
- **`workflow_dispatch` reruns of a failed approval-gated run require a fresh approval**, which is expected behavior, not a defect, but worth knowing operationally: a rollback re-tag (Pitfall 7) will need the approval clicked again, it does not carry over from a prior failed attempt.

**Prevention:** No code change is needed for the approval/OIDC-expiry interaction itself — the mechanics already work in typsphinx's favor (token requested after approval, well inside its 15-minute window for a normal-length job). The one operational thing to plan for is that **the person who removes `password:` and pushes the tag should be available to click Approve promptly** — not because of token expiry, but because a stale, un-approved run sitting for hours/days is itself worth treating as a "did this actually happen the way I expect" check before finally approving it (i.e., re-confirm the run is against the expected commit/tag before approving, since approval is also the last human checkpoint before a production PyPI upload with no `if:` gate).

**Phase to address:** No dedicated phase — this is an operational note for whichever phase performs the real tag push (the same phase as Pitfall 4's proof-gathering), not a code or registration change.

---

### Pitfall 7: Secret retirement mistakes — sequencing `PYPI_API_TOKEN` deletion and revocation

**What goes wrong:**
1. **Deleting the GitHub secret before a Trusted-Publishing upload has actually succeeded** removes the rollback path. If the OIDC exchange fails on the real tag (registration mismatch, PyPI-side outage, etc.), the only fast recovery is restoring `password: ${{ secrets.PYPI_API_TOKEN }}` — which requires either the secret still existing in GitHub, or re-creating and re-adding a fresh token under time pressure during a stuck release. The project's own todo already gets this ordering right ("Retire `PYPI_API_TOKEN` from repository secrets only after a publish has succeeded without it") — the risk is not following that stated order under the pressure of "the tag is already pushed, let's clean up now."
2. **Deleting the GitHub *secret* is not the same as revoking the token on PyPI's side.** `docs.bswen.com`'s migration checklist treats these as two separate line items for a reason: deleting the GitHub Actions secret only removes *this workflow's* access to the token string — the token itself remains valid on PyPI's account/project page until explicitly revoked there, and could still be used by anyone who captured it earlier (leaked in a log, a compromised fork of the workflow before the edit, a local `.env`, etc.). Retiring only the GitHub secret leaves a live, unrevoked credential sitting in PyPI's token list indefinitely.
3. **`PYPI_API_TOKEN` and `TEST_PYPI_API_TOKEN` are two different secrets** (`:144` and `:244`) — this milestone's own scope explicitly retires only the former; deleting or revoking the latter would break `publish-testpypi`, which stays token-based on purpose. A retirement step that globs "all PYPI-looking secrets" would take out `publish-testpypi` by accident.

**How to avoid:** Sequence strictly: (a) confirm the v0.9.7 tag push succeeded via Trusted Publishing (Pitfall 4's two evidence items), (b) only then delete `PYPI_API_TOKEN` from GitHub repository secrets, (c) separately, log into PyPI and **revoke** the same token from the account/project's API-token management page — not just let it sit unused. Do not touch `TEST_PYPI_API_TOKEN`.

**Warning signs:** If the retirement step is written as "remove the token" without naming *both* the GitHub secret deletion and the PyPI-side revocation as separate actions, the PyPI-side revocation is the one that gets silently skipped (it requires a different login/UI than the GitHub repo settings the rest of this migration touches).

**Phase to address:** The final, post-proof cleanup step of the migration — strictly ordered after Pitfall 4's proof is gathered, and split into its own two checkable sub-items (GitHub secret deletion; PyPI token revocation) rather than one.

---

### Pitfall 8: Version/tag mistakes specific to a rollback, if the OIDC exchange fails on the real tag

**What goes wrong:** If `v0.9.7`'s tag push fails at the `Publish to PyPI` step (wrong registration, PyPI outage, etc.), the natural instinct is to fix the registration and "just re-run" — but PyPI's upload API permanently and irrevocably rejects re-uploading **a filename that has ever existed** for a project, even if the previous attempt technically failed partway (confirmed independently by `pypi/warehouse#6872`, `pypa/gh-action-pypi-publish` discussion #105, and multiple Stack Overflow reports). Concretely for typsphinx:
- **Deleting and re-pushing the same `v0.9.7` git tag does not help** — PyPI's rejection is keyed on the *distribution filenames* (`typsphinx-0.9.7-py3-none-any.whl`, `typsphinx-0.9.7.tar.gz`), which are derived from the version in `pyproject.toml`, not from the git tag string. Re-tagging `v0.9.7` and re-running produces the *same* filenames and the *same* rejection, unless whatever partial upload happened is confirmed truly absent (which `pypa/gh-action-pypi-publish`'s own maintainer confirms cannot be relied on — "even if you delete them, it won't let you").
- **This is not hypothetical risk-modeling for this project** — typsphinx already has a standing, deliberate pattern of exactly this outcome: 0.9.1 and 0.9.3–0.9.5 are permanently unclaimed on PyPI because their milestones were completed but not published (for unrelated reasons), and the project's own rollback plan for *this* migration explicitly reuses that same pattern: "restore `password:` and re-tag as 0.9.8, leaving 0.9.7 unclaimed."
- **The correct rollback is therefore already the right shape** — bump to a new version (`0.9.8`), not attempt to force `0.9.7` through a second time. The one thing worth being deliberate about: `pyproject.toml`, `uv.lock`, and `README.md` version references (the milestone's own listed sync requirement) must move together to `0.9.8`, and the `## [0.9.8]` CHANGELOG section is a *new* section, not an edit of the abandoned `## [0.9.7]` one — otherwise the CHANGELOG gate (`Verify CHANGELOG has a section for this version`, `:72-79`) fails for the wrong reason during the retry.

**Prevention:** Pre-commit to "bump and re-tag, never force-retry the same version" as the sole rollback strategy before pushing the real tag, exactly as the milestone's own **Key context** already states. The only new information from this research is confirming *why* re-tagging the same version cannot work (PyPI's filename-uniqueness is permanent, not a git-tag-level concern), so nobody wastes time trying to delete/recreate the `v0.9.7` tag as a "fix."

**Phase to address:** Documented already as the rollback plan; no phase work needed beyond making sure whoever executes the real tag push has this rollback plan (bump to 0.9.8, do not retry 0.9.7) in hand *before* pushing, not improvised after a failure.

---

### Pitfall 9: `--skip-existing` / `skip-existing: true` is not configured, and should not be added as a "fix" for Pitfall 8

**What goes wrong:** A common workaround people reach for after hitting "File already exists" is adding `skip-existing: true` to the publish step, which makes the action treat an already-uploaded filename as a silent success instead of a hard failure (originally requested in `pypa/gh-action-pypi-publish#16` for legitimate matrix-build race conditions). For a single-job, non-matrix publish like typsphinx's `publish-pypi`, adding this would be actively harmful here: it would mask a *real* problem (e.g., a bug that causes the workflow to attempt re-publishing an already-successful version) as a clean, green run — directly undermining the Pitfall 4 principle that green CI must not be mistaken for proof.

**How to avoid:** Do not add `skip-existing`/`verify-metadata: false` or similar "make failures quieter" options as part of this migration. `release.yml`'s `publish-pypi` job is single-job, tag-triggered, version-gated by `Verify version matches pyproject.toml` (`:60-70`) — there is no legitimate matrix-race scenario here that `skip-existing` would be solving, only a way to hide the Pitfall 8 failure mode instead of surfacing it.

**Phase to address:** A negative constraint on the workflow-edit phase (ATT-01) — worth stating explicitly so a reviewer doesn't suggest adding it as a defensive measure.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|--------------------|-----------------|------------------|
| Registering the Trusted Publisher without a GitHub environment name (leaving it blank) | Slightly less PyPI-side form filling | Loses the ability to require manual approval / branch restriction at the PyPI-registration level — any workflow named `release.yml` in the repo could publish, not just runs that clear the `pypi` environment's gate | Never for this project — `release.yml` already declares `environment: pypi` (`:131-132`); the registration must name it to keep that gate meaningful |
| Adding `skip-existing: true` to quiet Pitfall 8/9 failures | Fewer "annoying" red runs | Silently converts a real duplicate-publish bug into a false-green run (see Pitfall 9) | Only ever acceptable for a genuine multi-job/matrix race, which `publish-pypi` does not have |
| Writing `attestations: true` explicitly in the workflow after this fix | Feels like "making the fix visible" | Restates the action's own default, and is exactly the kind of misleading-but-harmless addition the project's own todo explicitly warns against (it "would restate the current state and invite the same misreading this todo exists to correct") | Never — leave it as the implicit default |
| Deleting `PYPI_API_TOKEN` from GitHub secrets in the same commit/PR that removes `password:` | One fewer follow-up PR | Removes the rollback path before the fix is proven on a real tag (Pitfall 7, Pitfall 4) | Never — must be a separate, later action gated on proof |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|--------------------|
| PyPI Trusted Publisher registration form | Typing repo/owner/workflow/environment from memory instead of reading them off the actual `release.yml` and repo settings | Copy the four fields directly from the file and the repo's own GitHub URL at registration time |
| `pypa/gh-action-pypi-publish@release/v1` (floating tag) | Assuming a floating tag guarantees "latest and therefore attestation-capable" forever | It does — `@release/v1` currently resolves ahead of the v1.11.0 attestations-on-by-default line — but re-confirm this hasn't regressed if the action is ever repinned to a fixed SHA for supply-chain hardening reasons in a future milestone |
| GitHub Environment `pypi` (manual approval) | Assuming approval delay risks OIDC/PyPI-token expiry | It does not — the token is requested and exchanged only after approval clears (Pitfall 6); the real risk at that point is approving a run you haven't re-checked, not a timing race |
| `publish-testpypi` job (`TEST_PYPI_API_TOKEN`) | Treating it as "the same problem, deferred" and touching it anyway | It is explicitly out of scope this milestone (different secret, different gate — alpha/beta/rc only) — leave it alone |
| `workflow_dispatch` trigger on the same workflow | Assuming a manual dispatch run is a safe way to "test" Trusted Publishing before the real tag | `publish-pypi` has no `if:` gate, so a manual dispatch still hits **production** PyPI with whatever version is in `pyproject.toml` at that ref — it moves the real-tag risk earlier, it does not create a safe rehearsal |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Deleting the GitHub `PYPI_API_TOKEN` secret without revoking the underlying token on PyPI | The token remains valid indefinitely on PyPI's side; anyone who captured it earlier (log leak, compromised fork, local copy) can still use it | Revoke on PyPI's account/project token page as a separate, explicit step (Pitfall 7) |
| Registering the Trusted Publisher with no GitHub environment, or registering `environment: pypi` on PyPI but then editing the workflow later to run the publish step outside that environment | Any run of `release.yml` (not just approved, environment-gated ones) can mint a PyPI-scoped token | Keep the `environment: pypi` block on the `publish-pypi` job in lockstep with the PyPI-side registration; treat removing/renaming the environment block as a change that also requires re-registering on PyPI |
| Treating a successful, green `publish-pypi` run as proof attestations are attached | Attestations can be silently absent for at least 7 independent reasons (Pitfall 5) while the upload itself still succeeds | Verify the PyPI attestation badge directly, not CI's exit code |

## "Looks Done But Isn't" Checklist

- [ ] **`password:` removed from `publish-pypi`:** Often "done" is read as "the grep for `password:` in that step returns nothing" — verify additionally that no annotation reading `disabling Trusted Publishing` appears on the actual tag-push run (Pitfall 4).
- [ ] **PyPI Trusted Publisher registered:** Often assumed done because "I filled out a form" — verify the four fields (owner, repo, workflow filename, environment) were read off the real file, not typed from memory, and that registration happened on the *existing* `typsphinx` project's own Publishing page, not the account-level pending-publisher page (Pitfalls 1–2).
- [ ] **Attestations attached:** Often assumed done because "the upload succeeded" — verify the PyPI project page shows a Provenance/attestation badge for the specific uploaded files of 0.9.7 (Pitfall 4, item 2).
- [ ] **`PYPI_API_TOKEN` retired:** Often treated as one action ("delete the secret") — verify it is actually two: GitHub secret deletion *and* PyPI-side token revocation, in that order, and only after proof (Pitfall 7).
- [ ] **Rollback plan for a failed real-tag publish:** Often assumed to be "delete and re-push the tag" — verify the plan is actually "bump to 0.9.8 and re-tag," because PyPI permanently rejects re-uploading the same filenames regardless of git tag state (Pitfall 8).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|------------------|
| Registration mismatch (Pitfalls 1–3) causes the real tag's `publish-pypi` to fail | LOW | Fix the PyPI-side registration field(s), re-run the same failed workflow run (no code change, no new tag needed — the git tag and built artifacts are still valid, only the PyPI-side config was wrong) |
| Attestations silently absent despite a successful upload (Pitfall 5) discovered *after* the fact | MEDIUM | PyPI does not support retroactively attaching attestations to an already-uploaded file; the version is stuck without provenance. Recovery is bumping to the next version and re-publishing correctly configured — the affected version stays live but unattested, same as v0.9.6 today |
| OIDC exchange fails outright on the real tag for an unresolved reason | HIGH | Restore `password: ${{ secrets.PYPI_API_TOKEN }}` (requires the secret not yet deleted, per Pitfall 7's ordering), re-tag as the next version per Pitfall 8, and investigate the Trusted Publishing failure out-of-band before the next attempt |
| `PYPI_API_TOKEN` deleted from GitHub too early and a rollback is needed | HIGH | Generate a brand-new PyPI API token under time pressure, add it as a new GitHub secret, restore `password:` — strictly worse than having kept the old one, motivating the strict ordering in Pitfall 7 |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|--------------------|----------------|
| 1. Workflow filename / environment name mismatch | Pre-tag PyPI-side registration step (owner-performed, before `password:` is removed/tagged) | Registration fields read directly from `release.yml:131-144` and the repo's GitHub URL, not memory |
| 2. Wrong registration flow (pending vs. existing-project) | Same pre-tag registration step | Registration happened via the existing `typsphinx` project's own Publishing settings page |
| 3. Repository rename/fork leaves stale registration | Not this milestone — flag as a standing note for any future rename | N/A this milestone |
| 4. "Looks correct but unexercised" | The real-tag-push phase, as its own explicit gate before declaring the milestone done | Both: annotation absence on the run, AND the PyPI attestation badge — neither alone |
| 5. Attestations silently absent (7 causes) | Row 1 = the `release.yml` edit phase (ATT-01); rows 2–7 = already structurally avoided, confirm at the same verification gate as Pitfall 4 | PyPI attestation badge for the 0.9.7 files specifically |
| 6. Environment approval / OIDC timing | Operational note for the real-tag-push phase | Approver available promptly; approver re-confirms the run's commit/tag before clicking approve |
| 7. Secret retirement sequencing | Final cleanup phase, strictly after proof | Two separate, explicit sub-steps: GitHub secret deletion, PyPI token revocation |
| 8. Rollback tag/version mistakes | Documented rollback plan, referenced before the real tag is pushed | Rollback plan says "bump to 0.9.8," not "re-tag 0.9.7" |
| 9. `skip-existing` masking real failures | Negative constraint on the `release.yml` edit phase | `skip-existing`/`verify-metadata: false` not present in the diff |

## Sources

**Official / primary (HIGH confidence):**
- [PyPI Docs — Publishing with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher) — workflow shape, OIDC exchange mechanics, `environment:` field
- [PyPI Docs — Adding a Trusted Publisher to an Existing PyPI Project](https://docs.pypi.org/trusted-publishers/adding-a-publisher) — registration flow for an already-published project (this project's exact situation)
- [PyPI Docs — Troubleshooting](https://docs.pypi.org/trusted-publishers/troubleshooting) — `invalid-publisher`/`invalid-pending-publisher` causes, including the repository-rename case (Pitfall 3) and the environment-mismatch case (Pitfall 1)
- [PyPI Docs — Security Model and Considerations](https://docs.pypi.org/trusted-publishers/security-model) — 15-minute short-lived token expiry, required-reviewers recommendation
- [pypa/gh-action-pypi-publish README](https://github.com/pypa/gh-action-pypi-publish) — attestations default-on since v1.11.0, reusable-workflow unsupported note, "trusted publishing cannot be tested in CI" note
- [warehouse/docs — Creating a PyPI Project with a Trusted Publisher](https://github.com/pypi/warehouse/blob/main/docs/user/trusted-publishers/creating-a-project-through-oidc.md) — pending-publisher vs. existing-project distinction (Pitfall 2)

**This project's own record (HIGH confidence, directly read):**
- `.github/workflows/release.yml` (measured 2026-09-23)
- `.planning/todos/pending/2026-09-22-release-yml-uses-a-pypi-api-token-so-trusted-publishing-and.md` — the v0.9.6 annotation text verbatim, this project's own measured prerequisite table
- `.planning/PROJECT.md` — v0.9.7 milestone scope, REL-04 precedent, 0.9.1/0.9.3–0.9.5 unclaimed-version precedent

**Cross-checked community reports (MEDIUM confidence, corroborated across ≥2 independent sources):**
- [pypa/gh-action-pypi-publish#283](https://github.com/pypa/gh-action-pypi-publish/issues/283) and [langchain-ai/langchain#27765](https://github.com/langchain-ai/langchain/pull/27765) — attestation verification failure from reusable-workflow / mismatched-artifact scenarios
- [pypa/gh-action-pypi-publish#256](https://github.com/pypa/gh-action-pypi-publish/issues/256) — "not actually files" attestation failure
- [pypi/warehouse#6872](https://github.com/pypi/warehouse/issues/6872) and [pypa/gh-action-pypi-publish Discussion #105](https://github.com/pypa/gh-action-pypi-publish/discussions/105) — permanent rejection of re-uploaded filenames, maintainer confirmation ("even if you delete them, it won't let you")
- [pypa/gh-action-pypi-publish#16](https://github.com/pypa/gh-action-pypi-publish/issues/16) — origin of `skip-existing`, matrix-race use case
- [malloryai/malloryapi#9](https://github.com/malloryai/malloryapi/pull/9) — pinned-old-action-version metadata rejection
- [Nesbitt — GitHub Actions security in Python packages (2026-05-25)](https://nesbitt.io/2026/05/25/github-actions-security-in-python-packages.html) — ecosystem-wide adoption rate of Trusted Publishing (~22% of `gh-action-pypi-publish` users), recommended hardening shape

**Single-source, labelled LOW confidence (used only for illustrative detail, not as a standalone claim):**
- [docs.bswen.com migration walkthrough](https://docs.bswen.com/blog/2026-04-02-pypi-trusted-publishing-setup) — the "5 mistakes" framing and the GitHub-secret-vs-PyPI-revocation distinction (Pitfall 7); corroborated in spirit by the official security-model doc's "review Trusted Publishers as part of offboarding" note, but the specific mistake enumeration itself is one blog's own account
- [snarky.ca — How to publish to PyPI using GitHub Actions securely](https://snarky.ca/how-to-publish-to-pypi-using-github-actions-securely) — required-reviewers rationale, single-author opinion piece
- [Reddit r/learnpython — pypi.org error on creating Trusted Publisher](https://www.reddit.com/r/learnpython/comments/1d1fiel/pypiorg_error_on_creating_trusted_publisher) — anecdotal confirmation of the pending-publisher project-name mismatch error text

---
*Pitfalls research for: PyPI Trusted Publishing migration (existing published project, token → OIDC)*
*Researched: 2026-09-23*
