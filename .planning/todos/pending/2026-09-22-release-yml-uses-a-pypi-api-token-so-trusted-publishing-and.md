---
created: 2026-09-22T14:00:45.344Z
title: "release.yml publishes with a PyPI API token, so Trusted Publishing is off and the action's default PEP 740 attestations are silently dropped (ATT-01)"
area: ci
severity: minor
files:
  - .github/workflows/release.yml:141-144  # publish-pypi's "Publish to PyPI" step (measured 2026-09-22)
  - .github/workflows/release.yml:241-245  # publish-testpypi's "Publish to TestPyPI" step, same shape
  - .github/workflows/release.yml:13-15    # top-level permissions, already declaring id-token: write
---

## Problem

Surfaced as an annotation on `release.yml` run `35730551619` (the v0.9.6 publish, 2026-09-22),
quoted verbatim:

> The workflow was run with the 'attestations: true' input, but an explicit password was also set,
> disabling Trusted Publishing. As a result, the attestations input is ignored.

**Read the annotation carefully — it names an input the workflow file does not contain.**
`grep -n attestations .github/workflows/release.yml` returns nothing. `attestations: true` is
`pypa/gh-action-pypi-publish`'s own **default**; the annotation reports the effective input, not a
line someone wrote. Anyone picking this up by searching for an `attestations:` line will not find
one. The actual cause is the `password:` key, measured at HEAD `f1cfedf5`:

```yaml
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

That is the whole step. Supplying `password` puts the action on the API-token path, which turns
Trusted Publishing off, and PEP 740 attestations require Trusted Publishing — so the default
`attestations: true` becomes a no-op and the published artifacts carry no provenance attestation.

`publish-testpypi` (`:241-245`) has the identical shape with `TEST_PYPI_API_TOKEN`, so there are
**two** call sites, not one. That job is gated to alpha/beta/rc tags and did not run for v0.9.6.

**Not a release blocker.** The v0.9.6 upload succeeded: PyPI serves the wheel (194,339 B) and the
sdist (860,244 B) for `0.9.6`. What is lost is the provenance attestation and the operational
benefit of not holding a long-lived token in repository secrets at all.

**Most of the prerequisites are already in place** — which is why this is a small workflow change
sitting behind a one-time PyPI-side setup, not a redesign:

| Requirement | State at 2026-09-22 |
|---|---|
| `id-token: write` permission | present at top level (`:13-15`), its comment already reads "Required for PyPI trusted publishing" |
| `environment:` declared on the publish job | present — `pypi`, url `https://pypi.org/p/typsphinx`, with the manual-approval gate |
| `password:` removed from both steps | **not done** |
| Trusted Publisher registered on PyPI | **not done** — the run's annotation links the "create a Trusted Publisher" page for a logged-in package owner |

## Solution

1. **Register the Trusted Publisher on PyPI first**, while logged in as a `typsphinx` owner. The
   publisher is identified by repository owner + repository name + workflow filename
   (`release.yml`) + environment name (`pypi`). Register the TestPyPI publisher too if the
   `publish-testpypi` job is meant to keep working — its environment name is `testpypi`.
2. **Then delete the `password:` line from both steps.** Nothing replaces it: with `id-token:
   write` and the environment already declared, the action mints an OIDC token itself. Leaving the
   secret in place while a Trusted Publisher exists does not help — `password` still wins and
   attestations stay off.
3. **Do not add `attestations: true`.** It is already the default; writing it explicitly would
   restate the current state and invite the same misreading this todo exists to correct.
4. **Prove it on a real tag push, not on the file being correct.** This is the same class as REL-04
   (v0.7.0), which was wrong for a whole milestone because the workflow looked right and had never
   been exercised. The evidence is the next release run showing no "disabling Trusted Publishing"
   annotation, and the PyPI project page showing an attestation for the uploaded files. Until then
   the fix is unproven.
5. **Retire `PYPI_API_TOKEN` from repository secrets only after** a publish has succeeded without
   it — the token is the rollback path if the OIDC exchange fails mid-release.

**Ordering note.** Because the proof only exists at a real tag push, this belongs in a milestone
that publishes. Landing it in a merge-only milestone leaves an unexercised workflow change sitting
on `main`, which is exactly the shape QUA-08 was deferred for.
