---
created: 2026-08-11
title: "`ruff` cannot run on this NixOS machine at all: `.venv/bin/ruff` is a generic-linux ELF the stub loader rejects, and no other `ruff` exists on PATH"
area: toolchain, nixos
resolves_phase: null
severity: warning
source: 45.2 discussion (2026-08-10) D-03, reconfirmed live by 45.2-01 Step 1 and 45.2-04 Step 6
files:

  - flake.nix (candidate fix site)

audit_acknowledged:
  milestone: v0.9.1
  at: 2026-08-29
---

## Problem

`ruff check .` — a command `CLAUDE.md` documents as standard, and one of `tox -e lint`'s two
commands — has never actually run on this machine. Measured (45.2-01-TOOLCHAIN-EVIDENCE.md Step 1,
reproduced live):

```
$ file /home/yuta/Documents/typsphinx/.venv/bin/ruff
.../ruff: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked,
interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, ..., stripped

$ /home/yuta/Documents/typsphinx/.venv/bin/ruff --version
Could not start dynamically linked executable: /home/yuta/Documents/typsphinx/.venv/bin/ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
EXIT CODE: 127

$ command -v ruff
(nothing -- no ruff resolves anywhere outside the venv)
```

`.venv/bin/ruff` is a generic-linux ELF whose interpreter (`/lib64/ld-linux-x86-64.so.2`) does not
exist on NixOS outside a `nix-ld` shim, so it dies immediately with the stub-loader rejection. This
is the same root-cause family (`uv`/`uvx` shared it before Phase 45.2's fix) but has no equivalent
repair: `ruff` is `pyproject.toml`'s own dev-extra dependency, always resolved from PyPI as a
compiled wheel, with no package-substitution route analogous to `tox-uv` -> `tox-uv-bare`.

Post-Phase-45.2 (45.2-04-TOOLCHAIN-EVIDENCE.md Step 6): `tox -e lint` now correctly provisions
`extras = dev` and `black --check .` genuinely executes and passes ("All done! ... 502 files would
be left unchanged."). `ruff check .` is then reached and executes, but fails identically to the raw
invocation above -- `.tox/lint/bin/ruff` is the same generic-linux ELF as `.venv/bin/ruff` was,
because the tox environment installs the identical wheel from the identical lockfile. Fixing the
provisioning defect (D-02) does not and cannot fix this one.

CI is unaffected: `nixpkgs` is irrelevant on GitHub's Linux runners, which have a working `ruff`,
confirmed green across every 45.2-05 CI dispatch (`45.2-TOOLCHAIN-EVIDENCE.md` Step 8).

## Candidate repairs (all NixOS-local; none attempted here)

1. **`pkgs.ruff` in `flake.nix`'s devShell** — `nixpkgs#ruff` is `0.15.14`, inside the project's
   `ruff>=0.15,<0.16` floor (`pyproject.toml` line 40), so a version-compatible nix-store build is
   available today. This would put a working `ruff` on `PATH` outside any venv, the same way the
   nix-store `uv` already sits on `PATH` (resolved via `shutil.which`, not `.venv/bin`).

2. **`patchelf` on the `.venv`/`.tox` wheel-installed `ruff` binary**, rewriting its interpreter to
   point at the nix-store glibc dynamic linker instead of the generic `/lib64/ld-linux-x86-64.so.2`.
   Would need to run after every `uv sync`/`tox` provisioning step (a hook, not a one-shot fix).

3. **System `nix-ld`** — a NixOS module that makes the standard `/lib64/ld-linux-x86-64.so.2` path
   resolve to a real, generic-linux-compatible loader machine-wide, fixing this class of defect for
   every generic-linux binary (not just `ruff`), at the cost of a system-level (not project-level)
   configuration change outside this repository's control.

D-03/D-18 route this out of Phase 45.2 deliberately: every repair above is NixOS-local, the exact
category D-18 already declined when it rejected `TOX_UV_PATH` in favor of the portable
`tox-uv`/`deps` fix this phase applied instead. This todo files the defect; it does not propose
which repair to take.

## Related defect discovered alongside (Phase 45.2 Plan 02): `tox -e py312` is also unrunnable here

Same root cause, different binary. `tox config -e py312,lint,type,cov` exits non-zero specifically
on the `py312` leg: this NixOS devShell has no local Python 3.12 interpreter (`flake.nix` provides
only `pkgs.python3`, which resolves to 3.13 in the current nixpkgs channel), and `uv`'s own
auto-download of a missing interpreter fetches a generic-linux glibc build that hits the identical
stub-loader rejection this todo's main defect describes. Verified the underlying `extras = dev`
provisioning fix itself is sound by substituting `py313` (locally available):
`tox config -e py313,lint,type,cov` exits 0. Not fixed here for the same reason as `ruff` above --
every local repair (a nix-provided `py312`, `patchelf`, `nix-ld`) is NixOS-local. CI is unaffected:
GitHub's Linux runners install real `py312`/`py313` interpreters via `astral-sh/setup-uv`'s
`uv python install`, confirmed green (`Test Python 3.12 on ubuntu-latest`) in every Phase 45.2 CI
dispatch.

## Natural companion

`SEED-003` (`.planning/seeds/SEED-003-tox-dependency-groups-per-env.md`) -- splitting the `dev`
extra into finer-grained PEP 735 dependency groups would not fix either defect above (both are
about the specific `ruff`/`uv`-family binaries being generic-linux wheels, not about which
environment installs which tool), but any future work touching `tox.ini`'s per-environment tooling
declarations should read both together.

## Acceptance

- `ruff check .` (and `tox -e lint`'s `ruff` command) runs to completion on this NixOS machine,
  producing real lint output rather than the stub-loader rejection.

- `tox -e py312` (and the full `env_list`) runs to completion on this NixOS machine with a real
  Python 3.12 interpreter, not an auto-downloaded generic-linux build.

- Neither repair regresses CI, which already has working `ruff`/`py312` today.

## 2026-08-22 evidence — this milestone's re-measurement, KEPT OPEN (owner decision, Phase 57)

Recorded inside Phase 57 plan `57-09`'s isolated git worktree
(`worktree-agent-a4512207ecf0821b3`), after `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync
--extra dev` provisioned this worktree's own `.venv` fresh. Every command below was run live in
this session, moments before this annotation was written.

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-22T07:02:11Z

$ file .venv/bin/ruff
.venv/bin/ruff: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked,
interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=ca2c631a338418e6129fa7e04e290477442b8489, stripped

$ uv run ruff --version
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld

$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
EXIT CODE: 127

$ ls -la /lib64/ld-linux-x86-64.so.2
lrwxrwxrwx 1 root root 77  8月 22 14:59 /lib64/ld-linux-x86-64.so.2 -> /nix/store/af76y16gym2y1adsx1gv66lxk6rl9aql-stub-ld-x86_64-unknown-linux-musl
```

**The failure signature quoted in this record's own `## Problem` section DOES reproduce on this
machine as of today** — not "no longer reproduces" as an earlier session's discussion (2026-08-16,
recorded in `57-CONTEXT.md`'s AMENDED D-13 block) anticipated finding. That earlier session
measured `uv run ruff check .` → `All checks passed!`, exit 0, `ruff 0.15.20`, in a different
`.venv` (not a freshly `uv sync`-provisioned worktree venv). Today, in this freshly provisioned
worktree, the identical stub-loader rejection from this record's original `## Problem` section
(`Could not start dynamically linked executable`, `/lib64/ld-linux-x86-64.so.2` resolving to a
`stub-ld` package) reproduces byte-for-byte against the exact same `.venv/bin/ruff` ELF shape.

No commit is known to explain either the 2026-08-16 disappearance or this 2026-08-22 recurrence —
the condition flips with the environment (which venv, which moment the NixOS store's `/lib64`
symlink target resolves to), not with any change to this repository's own tree. This is precisely
why the owner decided during this milestone (57-CONTEXT.md AMENDED D-13) to annotate this record
with evidence and **keep it in `pending/`** rather than close it: closing it after the 2026-08-16
green measurement would have erased the record, and this very session's flip back to RED — inside
the same milestone, seven days later — is the recurrence that decision anticipated. The owner's
decision to keep this record open is reaffirmed by this session's own measurement, not merely
repeated from an earlier session's prose.

The durable, intentional fix `## Acceptance` above asks for (`pkgs.ruff` in `flake.nix`'s devShell,
`patchelf`, or system `nix-ld`) is unaffected by either measurement and remains undone — CI is
still SC#3's lint/type authority for this reason (`57-CONTEXT.md` D-13's surviving conclusion, only
its now-doubly-falsified premise "ruff cannot run on this machine at all" has been shown to be a
sometimes-true, environment-dependent statement rather than an always-true one).

**Record disposition (Phase 57, plan `57-09`):** this record's existence in `.planning/todos/pending/`
was confirmed by `ls -1 .planning/todos/pending/ | grep ruff-generic-linux-elf-unrunnable-on-nixos`
(directory listing, not a content grep) and its absence from `.planning/todos/completed/` was
confirmed the same way. It stays in `pending/`. Neither the frontmatter's `severity` nor this
file's `## Acceptance` section was altered by this annotation.
