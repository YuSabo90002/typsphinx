# Phase 46, Plan 05 — REL-04 In-Phase Precondition Evidence

**Recorded:** 2026-08-11T04:29:21Z, inside a worktree-agent worktree for this plan
(`worktree-agent-aa78f6244a8f98fe4`).

REL-04 requires the GitHub Release body to be the curated `## [X.Y.Z]` CHANGELOG section rather than
a `git log --pretty` commit dump, **proven by a real tag push whose `create-release` job runs to
completion**. Phase 46 is prep-only (no tag, no PyPI, no GitHub Release), so this plan cannot
discharge that acceptance evidence — only `/gsd-complete-milestone` can generate it. What follows is
this phase's **in-phase share**: verifying the two preconditions that determine whether the next real
tag push has any chance of succeeding, without taking any irreversible action.

Provisioning note: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` was run in this
worktree before any command below; every Python invocation below runs through `uv run`.

---

## Precondition 1 — the create-release job carries the uv setup

### Verbatim transcript, `.github/workflows/release.yml` lines 156-200

```
156:      # This job runs `uv run python scripts/extract_changelog_section.py` in
157:      # the "Generate release notes" step below, so it needs uv on PATH like
158:      # the validate and build jobs do. Omitting these two steps is exactly
159:      # what failed the first real v0.7.0 tag push (`uv: command not found`,
160:      # run 30848860064) -- the job had never needed uv before REL-04 wired the
161:      # extractor into it.
162:      - name: Install uv
163:        uses: astral-sh/setup-uv@v7
164:        with:
165:          version: "latest"
166:
167:      - name: Set up Python
168:        run: uv python install 3.12
169:
170:      - name: Download build artifacts
171:        uses: actions/download-artifact@v8
172:        with:
173:          name: dist-packages
174:          path: dist/
175:
176:      # Same `env:`-not-interpolation invariant as the validate job above.
177:      - name: Extract version from tag
178:        id: version
179:        env:
180:          EVENT_NAME: ${{ github.event_name }}
181:          INPUT_TAG: ${{ github.event.inputs.tag }}
182:        run: |
183:          if [ "$EVENT_NAME" == "workflow_dispatch" ]; then
184:            TAG="$INPUT_TAG"
185:          else
186:            TAG="${GITHUB_REF#refs/tags/}"
187:          fi
188:          echo "tag=$TAG" >> $GITHUB_OUTPUT
189:
190:      - name: Generate release notes
191:        id: notes
192:        env:
193:          TAG: ${{ steps.version.outputs.tag }}
194:        run: |
195:          # Curated release-notes body, sourced from CHANGELOG.md's own
196:          # `## [X.Y.Z]` section (REL-04) -- not a `git log` commit dump.
197:          uv run python scripts/extract_changelog_section.py "${TAG#v}" > release_notes.md
198:
199:          echo "" >> release_notes.md
200:          echo "## Installation" >> release_notes.md
```

**Confirmed by direct transcription (not eyeballed from memory):** the `Install uv` step
(`astral-sh/setup-uv@v7`) at line 162 and the `Set up Python` step (`uv python install 3.12`) at
line 167 both sit inside the `create-release` job, ahead of the `Generate release notes` step's
`uv run python scripts/extract_changelog_section.py "${TAG#v}" > release_notes.md` call at line 197.
This is the exact fix for the `uv: command not found` (exit 127) failure that killed release run
`30848860064` on the first real `v0.7.0` tag push — the inline comment at lines 156-161 names that
run explicitly.

### This phase changed nothing in the file

```
$ git diff origin/main..HEAD -- .github/workflows/release.yml
(no output, exit 0)
```

Empty. Unlike Invariant 3 of `46-SC4-INVARIANTS.md` (which measures `typsphinx/`, a directory every
prior phase in this milestone legitimately touched), `.github/workflows/release.yml` has never been
edited by any phase in this milestone — so `origin/main..HEAD` correctly reads as empty here, with no
reference-point caveat needed. Confirmed no milestone phase, including this one, has modified this
file since `origin/main`.

This also preserves the file's own stated security invariant: every GitHub Actions expression in this
job is passed through `env:` (see lines 179-181 and 192-193 above) rather than interpolated directly
into a `run:` block — the standard mitigation against a maliciously crafted tag name executing shell
in a job holding `contents: write`. Because the file is unchanged, that invariant is unchanged too.

---

## Precondition 2 — the extractor runs against the real section

### Exercise 1 — basic invocation

```
$ uv run python scripts/extract_changelog_section.py 0.7.1
This release closes the gap between what typsphinx's documentation promises and what a `conf.py`
actually gets: `typst_documents` now resolves to a working default instead of silently producing
nothing, an explicit entry's title and author finally reach the rendered document, and the
published custom-template parameter contract matches what typsphinx actually passes. Several
rendering-structure defects in tables, figures, and toctree-driven heading nesting are also
repaired. Because several of these fixes tighten previously-loose configuration handling, **this
patch release can break a working configuration** -- read the `### Changed` and `### Removed`
sections below, and see the "Migrating from 0.7.0 to 0.7.1" guide in the published documentation
for the exact rewrite each breaking change needs.

### Added
... [74 more lines: Added / Changed / Fixed / Removed / Verified sections] ...
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.

$ echo "exit=$?"
exit=0
```

Exit 0, non-empty body written to stdout (78 lines total, spot-checked above — full body captured in
the scratch file used for the checks below).

### Exercise 2 — idempotency

```
$ uv run python scripts/extract_changelog_section.py 0.7.1 > <scratch>/46-05-a.txt
$ uv run python scripts/extract_changelog_section.py 0.7.1 > <scratch>/46-05-b.txt
$ diff <scratch>/46-05-a.txt <scratch>/46-05-b.txt
(no output, exit 0)

$ git tag -l v0.7.1
(no output, before AND after both invocations)

$ git status --porcelain
(no output, before AND after both invocations)
```

Two consecutive invocations produce byte-identical stdout. Neither invocation created a git tag or
changed the working tree in any way — the script only reads `CHANGELOG.md` and writes to stdout.

### Exercise 3 — empty input (no section for the given version)

```
$ uv run python scripts/extract_changelog_section.py 9.9.9 >stdout.txt 2>stderr.txt
$ echo "exit=$?"
exit=1

$ cat stdout.txt
(empty)

$ cat stderr.txt
No '## [9.9.9]' section found in the CHANGELOG. Add a curated entry for this version before releasing.
```

Exits 1, empty stdout, a diagnostic message on stderr. This is the failure the `validate` job relies
on to stop a release before the PyPI upload rather than after it (D-09's ordering: `validate` runs
before `build`/`publish-pypi`/`create-release`).

### Exercise 4 — adjacency (no leakage from the neighbouring `## [0.7.0]` or `## [Unreleased]` sections)

Independent extraction via `awk`, taking the lines strictly between the `## [0.7.1]` heading and the
next line matching `^## \[`, with leading/trailing blank lines stripped identically to the script's
own `.strip("\n").strip()`:

```
$ awk '
/^## \[0\.7\.1\]/ { found=1; next }
found && /^## \[/ { exit }
found { print }
' CHANGELOG.md > awk-raw.txt

$ python -c "from pathlib import Path; p=Path('awk-raw.txt'); Path('awk-stripped.txt').write_text(p.read_text().strip('\n').strip() + '\n')"

$ diff awk-stripped.txt <scratch>/46-05-a.txt
(no output, exit 0)
```

Byte-identical (the one intermediate mismatch during this exercise was a self-inflicted trailing-
newline artifact of `Path.write_text()` not appending a final `\n` after `.strip()` — reconciled by
adding it back for a fair comparison against the script's own `print()`, which always emits a
trailing newline; the underlying section *content* was identical on the very first comparison too).
This proves the extracted body carries **no text from the adjacent `## [0.7.0]` section** (which
`CHANGELOG.md` places immediately after `## [0.7.1]`) and **none from `## [Unreleased]`** (which sits
above it) — the script's purely positional algorithm (first matching heading, terminated by the very
next `## [...]` heading, regardless of name) is verified against an independently-written extraction
that uses no shared code with `scripts/extract_changelog_section.py`.

### Exercise 5 — ordering

The Exercise 4 `diff` exiting 0 already establishes this: `diff` is line-order-sensitive, so a
byte-identical result over multi-line content proves the extracted body's line order matches the
`awk`-extracted source region's line order exactly. Recorded here explicitly, per this plan's
instruction not to leave it implicit, rather than as a separate command — there is no second command
to run that would test ordering independently of content equality.

---

## REL-04 remains open

- **REL-04's acceptance evidence is a real tag push whose `create-release` job runs to completion,
  and only `/gsd-complete-milestone` can generate it.** Nothing above is that tag push — Phase 46 is
  prep-only by design (no tag, no PyPI, no GitHub Release, no PR), and this plan took no irreversible
  action: `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1` were both confirmed empty
  throughout, and `git status --porcelain` showed no change caused by either extractor invocation.

- **Everything recorded above is a precondition, never acceptance.** Precondition 1 confirms the
  workflow fix is present and this phase did not disturb it. Precondition 2 confirms the extractor
  itself behaves correctly (idempotent, fails loudly on a missing section, extracts exactly the
  requested section with no cross-section leakage, preserves line order) against the real
  `## [0.7.1]` section now that it exists. Neither precondition is the thing REL-04 actually requires
  — the `create-release` **job**, running inside GitHub Actions on a real tag push, with its own
  runner environment, its own `astral-sh/setup-uv` action resolution, and its own artifact download
  step, all executing together for the first time against this exact workflow file.

- **v0.7.0 reported this requirement's mechanism as done and the release then failed at exactly this
  job** (`create-release`, run `30848860064`, `uv: command not found`, exit 127) — which is precisely
  why the boundary is drawn here rather than treating "the workflow file looks correct" and "the
  script works when I run it locally" as sufficient evidence. Both were also true before v0.7.0's
  release failed.

- `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` **stays in
  `todos/pending/`** — confirmed present at that path (`test -f` succeeded above) — and is **not**
  filed to `completed/` by this phase.

- `.planning/REQUIREMENTS.md`'s REL-04 row **stays `Pending`** and is **not edited** by this phase —
  confirmed by `git diff --name-only -- .planning/REQUIREMENTS.md` producing no output (D-26 also
  keeps this file untouched for PR #131, for an unrelated reason, but the same "no edit" invariant
  holds here for REL-04's own sake).

**REL-04 closes only when a real tag push runs `create-release` to completion** — that happens, if it
happens, at `/gsd-complete-milestone`. This plan verified the two things that make that outcome more
likely (a correct, undisturbed workflow file; a correct, idempotent, fail-loud extractor script) and
recorded both as preconditions, not as the requirement's discharge.
