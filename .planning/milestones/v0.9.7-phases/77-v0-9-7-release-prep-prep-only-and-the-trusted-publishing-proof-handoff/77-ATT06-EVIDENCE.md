# Phase 77 — ATT-06 Evidence (rollback recorded before any v0.9.7 tag)

## Head check and provisioning

Command: `date -u +%FT%TZ`
```
2026-09-28T13:09:46Z
```

Command: `pwd -P`
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9cf7dde6a8321350
```

Command: `test -f .git; echo "exit:$?"`
```
exit:0
```

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`
```
exit:0
```

BASE_77_03 = 3984b231e30fbb76ba156d2f9b2abe475231bccf
SCRATCH_77_03 = /tmp/p7703.ZqqrdO

## Measured basis in release.yml

Command: `grep -n "^  publish-pypi:\|^  build:\|^  create-release:" .github/workflows/release.yml`
```
93:  build:
127:  publish-pypi:
145:  create-release:
```

Command: `grep -n "needs: build\|needs: \[build, publish-pypi\]\|retention-days: 7\|name: pypi\|- name: Publish to PyPI\|uses: pypa/gh-action-pypi-publish@release/v1" .github/workflows/release.yml`
```
124:          retention-days: 7
129:    needs: build
132:      name: pypi
141:      - name: Publish to PyPI
142:        uses: pypa/gh-action-pypi-publish@release/v1
147:    needs: [build, publish-pypi]
220:    needs: build
240:        uses: pypa/gh-action-pypi-publish@release/v1
```

`publish-pypi:` (release.yml:127) runs `needs: build` (release.yml:129) with no `if:` anywhere in
the job body (release.yml:127-142, confirmed by reading the full job below) — so every `v*` tag
that reaches this job reaches production PyPI. `create-release:` (release.yml:145) needs
`[build, publish-pypi]` (release.yml:147) with no `if:` override either.

Full job body read (`sed -n '127,148p' .github/workflows/release.yml`), confirming no `if:` line
in either job:
```
  publish-pypi:
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/typsphinx
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v8
        with:
          name: dist-packages
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1

  # Create GitHub Release
  create-release:
    name: Create GitHub Release
    needs: [build, publish-pypi]
    runs-on: ubuntu-latest
```

RETENTION_DAYS = 7
PUBLISH_USES_LINE = 142

The line immediately above `PUBLISH_USES_LINE` (release.yml:141) is
`      - name: Publish to PyPI`, confirmed above.

Command: `gh api repos/YuSabo90002/typsphinx/environments/pypi --jq '[.protection_rules[] | .type] | join("|")'`
```
required_reviewers|wait_timer
```

Command: `gh api repos/YuSabo90002/typsphinx/environments/pypi --jq '.protection_rules[] | select(.type=="wait_timer") | .wait_timer'`
```
15
```
PYPI_ENV_WAIT_TIMER = 15

The two lines `efde71a9` removed (`git show efde71a9 -- .github/workflows/release.yml`):
```
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

## The commit that adds the rollback section

Command: `git rev-parse HEAD` (run immediately after committing `77-HANDOFF.md` alone)
```
fe4e87638220ec8c7574f73050e336e0fe28110b
```
ROLLBACK_COMMIT_SHA = fe4e87638220ec8c7574f73050e336e0fe28110b

Command: `git show --name-only --format=%s fe4e87638220ec8c7574f73050e336e0fe28110b`
```
docs(77-03): record ATT-06 rollback procedure inside 77-HANDOFF.md

.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-HANDOFF.md
```
ROLLBACK_COMMIT_FILES = .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-HANDOFF.md

Command: `awk '$0=="## Rollback procedure (ATT-06)"{f=1;print;next} f&&/^## /{exit} f' 77-HANDOFF.md | grep -v '^$' | sha256sum` — the same extraction re-run byte-for-byte at HEAD and at the
rollback commit (`git show fe4e87638220ec8c7574f73050e336e0fe28110b:.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-HANDOFF.md`
piped through the identical awk/grep):
```
4406fb65f1bc19b1ebc4682631ab2608f1abde9516418cf3f35c8c5b5901192b
```
ROLLBACK_SECTION_SHA256 = 4406fb65f1bc19b1ebc4682631ab2608f1abde9516418cf3f35c8c5b5901192b

Both readings (at the rollback commit, and at the current HEAD — the same commit, since no
further commits have landed between them) produced the identical digest above.

## No v0.9.7 tag anywhere at that commit

PROBED_AT = 2026-09-28T13:13:39Z

Command: `git rev-parse HEAD`, taken at the same moment
```
fe4e87638220ec8c7574f73050e336e0fe28110b
```
PROBE_HEAD_EQUALS_ROLLBACK_COMMIT = yes

Command: `git tag -l 'v0.9.7'`
```
(empty)
```
LOCAL_V097_AT_ROLLBACK = 0

Command: `git tag -l 'v0.9.6'`
```
v0.9.6
```
LOCAL_V096_AT_ROLLBACK = 1

Command: `LC_ALL=C git ls-remote --tags origin`, transcribed (39 lines; `v0.9.6` entries shown, full
list captured to `/tmp/p7703_tags.txt`):
```
...
8963519d224b82b8a27a807a5b00d6360c929ed0	refs/tags/v0.9.6
6fcc5adb02f5eefffd88ecda5258dca842d1acaa	refs/tags/v0.9.6^{}
```
No `refs/tags/v0.9.7` line appears anywhere in the full output.

Command: `grep -c 'refs/tags/v0\.9\.7' /tmp/p7703_tags.txt`
```
0
```
REMOTE_V097_AT_ROLLBACK = 0

Command: `grep -c 'refs/tags/v0\.9\.6$' /tmp/p7703_tags.txt` (excludes the `^{}` peeled-tag line)
```
1
```
REMOTE_V096_AT_ROLLBACK = 1

Command: `git tag --points-at fe4e87638220ec8c7574f73050e336e0fe28110b`
```
(empty)
```
TAGS_POINTING_AT_ROLLBACK = 0

## The three parts ATT-06 names

`.planning/REQUIREMENTS.md`'s ATT-06 text, quoted verbatim:

> - [ ] **ATT-06**: A rollback procedure is recorded before the tag is pushed, and names: restoring
>       `password:`, bumping to 0.9.8 rather than retrying 0.9.7 (PyPI permanently refuses a
>       re-uploaded filename regardless of git-tag state), and **deleting the failed `v0.9.7` tag both
>       locally and on `origin`** (owner decision, 2026-09-23 — this repository has no precedent: a
>       `git tag -l` measurement shows 0.9.1 and 0.9.3–0.9.5 were never tagged at all, so a pushed tag
>       with no release would be a first).

The section lines that carry each named part, in `77-HANDOFF.md`'s `## Rollback procedure
(ATT-06)`:

- **Restoring `password:`** — `### R4 — Last resort: restore the token credential (D-03,
  owner-gated)`, the fenced `yaml` block holding the two `efde71a9`-removed lines byte-for-byte.
- **Bumping to 0.9.8 rather than retrying 0.9.7** — `### R2 — Leave 0.9.7: delete the tag and
  re-prep as 0.9.8 (D-02)`, "Then re-run release prep as 0.9.8: `pyproject.toml` to `0.9.8`...".
- **Deleting the failed `v0.9.7` tag both locally and on `origin`** — the same `### R2` subsection,
  the `git tag -d v0.9.7` / `git push origin --delete v0.9.7` command pair.
- **The cheaper path tried first** — `### R1 — Same-run re-run (shape 1)`, the same-run
  `gh run rerun <RELEASE_RUN_ID> --failed` inside the 7-day artifact retention window.

Command confirming the restore block's byte identity (rerun of the check the plan's own
`<verify>` performs): the two lines `efde71a9` removed appear adjacent, in the same order, and
byte-exact inside the section's fenced `yaml` block.
```
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```
RESTORE_BLOCK_MATCHES_EFDE71A9 = yes
ATT06_PARTS_PRESENT = yes

## ATT-06 verdict

Every key above holds: `ROLLBACK_COMMIT_SHA` touches only `77-HANDOFF.md`, no local or remote
`v0.9.7` tag exists anywhere at that commit while `v0.9.6` is present as a positive control on
both sides, no tag points at the rollback commit, the section's digest agrees at the commit and at
HEAD, and all three ATT-06 parts plus the cheaper path tried first are present in their settled
form.

ATT06_VERDICT = MET
