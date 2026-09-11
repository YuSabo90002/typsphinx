# Phase 64 Plan 03 Task 2 — NIX-08 Environment and Locale Evidence

## Definitions (written before measuring)

These definitions are written and committed before any locale probe in this file runs, so that a
MASKS or INCONCLUSIVE result cannot be reclassified after seeing the data (T-64-13).

- **The known class:** tests whose outcome depends on the process locale. Historically, Sphinx
  localizes a warning's BODY text under the maintainer's `LANG=ja_JP.UTF-8` while CI runs English.
  Phase 52 re-anchored `tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics` on the
  never-localized `file:line: WARNING:` prefix and the bracketed diagnostic tag, via
  `_locale_invariant_anchors()`.

- **Matrix:** the warning body Sphinx emits for one fixed scratch document that is outside any
  toctree, captured four ways:
  - **H-ja:** host, maintainer environment, via the worktree's absolute `.venv/bin/python -m
    sphinx` (an absolute path, so no shim is involved)
  - **H-C:** host, with `LC_ALL=C LANG=C LANGUAGE=C`
  - **S-ja:** through the `sphinx-build` shim, maintainer environment
  - **S-C:** through the shim, with `LC_ALL=C LANG=C LANGUAGE=C` set by the caller

  All four runs start from inside the worktree, so the shim's walk finds this worktree's `.venv`.
  All four use the same Sphinx.

- **Control:** H-ja ≠ H-C, meaning the locale axis actually changes Sphinx's text on the host. If
  H-ja = H-C, the finding is **INCONCLUSIVE**: record it and do not classify.

- **REPRODUCES:** the control holds, S-ja = H-ja and S-C = H-C. Through the shim, the locale axis
  behaves exactly as on the host. So the class exists through the shim exactly as it does on the
  host: invisible under ja_JP.UTF-8, surfaced by the `LC_ALL=C` pre-check.

- **MASKS:** the control holds, and S-ja ≠ H-ja or S-C ≠ H-C. The shim changes what the locale axis
  shows, so a shim run cannot stand in for a host run when reasoning about the class. Record which
  cell diverged and in which direction. Per CONTEXT § Specific Ideas, masking is a legitimate
  finding and is written as such.

- **INCONCLUSIVE:** the control does not hold (H-ja = H-C) — the locale axis does not change
  Sphinx's text on the host at all under this fixture, so REPRODUCES/MASKS cannot be evaluated.
  Recorded and not classified further.

## Measured shape

The genuine D-09 shape: this Claude Code session's own inherited PATH, launched after 64-01's
`flake.nix` merged, running inside the nested worktree
`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa549e5cc51035b0c`. `command -v sphinx-build`
and `command -v pytest` both resolve to `/nix/store/…` paths whose bodies contain
`typsphinx-fhs-run`, and this worktree's `.venv` exists (provisioned by Task 1's `env -u
VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`).

## An unanticipated finding, stated before the measurements that depend on it

**This worktree's own `.venv/bin/python` cannot execute directly on the host at all.** Measured:

```
$ .venv/bin/python -c "..."
Could not start dynamically linked executable: .venv/bin/python
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

`file` on the symlink target confirms why: this worktree's fresh `uv sync --extra dev` downloaded
uv's own managed CPython build (`~/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin/python3.14`,
interpreter `/lib64/ld-linux-x86-64.so.2`, which `readlink -f` resolves to the `stub-ld` package
that deliberately refuses execution) — the identical RED-reproduction class Phase 64-01 already
proved for `.venv/bin/ruff` in a freshly provisioned worktree (`64-FLAKE-EVIDENCE.md`'s RED
section). By contrast, the main checkout's `.venv/bin/python` is a symlink to
`/nix/store/…-python3-3.13.13/bin/python3` — a nix-native binary that runs directly, unshimmed,
because that venv was built against `pkgs.python3` on `PATH` rather than a downloaded manylinux
CPython. This divergence between the main checkout's long-lived `.venv` and a genuinely fresh
worktree `.venv` is exactly the "main-tree measurement can never detect the hazard" lesson D-04
already states (PROJECT.md's Phase 57 lesson).

**Consequence for this task's "host leg":** NIX-08's plan text describes H-ja/H-C as running
"via the worktree's absolute `.venv/bin/python -m sphinx`" — literally impossible for *this*
worktree's own binary, since it cannot execute at all without the sandbox. **Substitution used,
documented here rather than silently:** the main checkout's `.venv/bin/python` — confirmed to run
directly and unshimmed on this same host, and confirmed to carry the identical `sphinx==9.1.0` pin
this worktree's own `uv sync` also installed (both draw from the same `uv.lock`; this milestone
makes no product-code changes) — serves as the genuine "host, unshimmed" leg for both the locale
mechanics probe below and the four-cell matrix's H-ja/H-C cells. `sphinx-build` itself (the shim,
S-ja/S-C) is unaffected and uses this worktree's own `.venv` throughout, exactly as D-09 measures
it. The scratch document under test in the four-cell matrix is a bare `-b dummy` build (no
`typsphinx` extension invoked), so the substitution changes only which CPython build executes
Sphinx, not which Sphinx version or which extension surface is exercised.

## Environment measurement

Wrapper path extracted from the `ruff` shim body:
`FHS="$(grep -oE '/nix/store/[^ "]+/bin/typsphinx-fhs-run' "$(command -v ruff)" | head -1)"` →
`/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run/bin/typsphinx-fhs-run`.

### a. Environment-name diff (`env | cut -d= -f1 | sort` vs. `"$FHS" /usr/bin/env | cut -d= -f1 | sort`)

Names only, per T-64-10:

- **Added (in sandbox, not host):** `ACLOCAL_PATH`, `GST_PLUGIN_SYSTEM_PATH_1_0`,
  `NIX_CFLAGS_LINK`, `PKG_CONFIG_PATH`, `TZDIR`
- **Removed (in host, not sandbox):** none (the sole `comm` output line was the empty-name
  artifact of the input having a trailing blank line, not a real variable)

### b. Allowlisted values (host-side vs. inside)

Per T-64-10, only these names carry a value in this evidence file; every other variable in the
diff above is name-only.

| Variable | Host | Sandbox |
|----------|------|---------|
| `HOME` | `/home/yuta` | `/home/yuta` |
| `TMPDIR` | *(unset)* | *(unset)* |
| `LANG` | `ja_JP.UTF-8` | `ja_JP.UTF-8` |
| `LANGUAGE` | *(unset)* | *(unset)* |
| `LC_ALL` | *(unset)* | *(unset)* |
| `LC_MESSAGES` | *(unset)* | *(unset)* |
| `LOCALE_ARCHIVE` | `/run/current-system/sw/lib/locale/locale-archive` | `/run/current-system/sw/lib/locale/locale-archive` |
| `TZ` | *(unset)* | *(unset)* |
| `PWD` | `<worktree root>` | `<worktree root>` |
| `VIRTUAL_ENV` | *(unset)* | *(unset)* |
| `UV_PROJECT_ENVIRONMENT` | *(unset)* | *(unset)* |
| `PATH` (first 4 entries) | `bubblewrap/bin:socat/bin:nodejs-24.16.0/bin:pnpm-11.9.0/bin:` | `/run/wrappers/bin:/usr/bin:/usr/sbin:bubblewrap/bin:` |

`<worktree root>` = `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa549e5cc51035b0c`.
`PATH` entries above are elided to their nix-store package name for readability; the sandbox's
first three entries (`/run/wrappers/bin`, `/usr/bin`, `/usr/sbin`) are the FHS's own `/etc/profile`
prefix (sourced before `runScript` runs, matching the researched nixpkgs mechanism); from the
fourth entry on, the sandbox's `PATH` continues with the same host-derived entries the caller had.

### c. Caller-set probe variable (space + non-ASCII)

```
$ NIX08_PROBE='a b 日本' "$FHS" /bin/sh -c 'printf "NIX08_PROBE=[%s]\n" "$NIX08_PROBE"'
NIX08_PROBE=[a b 日本]
```

The value, including the embedded space and the non-ASCII `日本` word, survives intact inside.

### d. D-06's load-bearing passthrough case

```
$ VIRTUAL_ENV=/nix08-probe UV_PROJECT_ENVIRONMENT=/nix08-probe \
    env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT "$FHS" /usr/bin/env \
    | grep -cE '^(VIRTUAL_ENV|UV_PROJECT_ENVIRONMENT)='
0
```

Zero lines: the `env -u` unsets survive into the sandbox. This is the mechanism CLAUDE.md's
mandatory worktree-provisioning idiom (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
--extra dev`) depends on.

### e. TMPDIR

- Unset in this session (confirmed above, matching the planning-time measurement).
- `TMPDIR=<scratch dir> "$FHS" /bin/sh -c 'printf %s "$TMPDIR"'` printed the identical scratch
  directory path passed in (`/tmp/tmp.CNhP0MRYFJ` in this run) — passthrough confirmed.
- `stat -c '%d %i' /tmp` matched exactly host-side and inside: `41 256` both times — `/tmp` is
  bound, not private, consistent with `buildFHSEnv`'s `privateTmp = false` default.

### f. `$HOME`

Identical host-side and inside (`/home/yuta` both times). `ls "$HOME/.cache/typst/packages/preview"`
inside listed all nine cached `@preview` packages (`charged-ieee`, `codly`, `codly-languages`,
`fontawesome`, `gentle-clues`, `linguify`, `mitex`, `modern-cv`, `xarrow`) — the warm cache is fully
reachable from inside the sandbox.

### g. `/etc`

`"$FHS" /bin/sh -c 'ls -la /etc'` inside shows symlinks into `/.host-etc` for: `alsa`, `bashrc`,
`fonts`, `group`, `hosts`, `localtime`, `machine-id`, `nix`, `nsswitch.conf`, `os-release`,
`passwd`, `pki`, `profiles`, `resolv.conf`, `shadow`, `shells`, `static`, `sudoers`, `zoneinfo`, and
`ssl/certs` (via `/etc/ssl` → a real directory containing a `certs -> /.host-etc/ssl/certs`
symlink). Entries served from the FHS closure itself (not `/.host-etc`): `login.defs`, `mtab`,
`profile`, `rpc`, plus the real `ld.so.cache`/`ld.so.conf` files and the `pam.d`/`profile.d`
directories. This matches the researched nixpkgs `etcBindEntries` list closely, with `resolv.conf`,
`nsswitch.conf`, `hosts`, `passwd`, `group`, `localtime`, `zoneinfo`, `ssl/certs` and `pki` all
present as expected; a distinct top-level `ca-certificates` entry was not observed in this listing
(the host's certificate trust is reached via `ssl/certs` and `pki`).

Loader path: host-side, `readlink -f /lib64/ld-linux-x86-64.so.2` resolves to
`/nix/store/4fg6jxqcrn62v8azwp18wxnckmvslgpy-stub-ld-x86_64-unknown-linux-musl` — the deliberate
refusal stub. Inside the sandbox, the same path resolves to
`/nix/store/8kvxvr3pmsypxiypq4g8zy13glnfr7nx-glibc-2.42-67/lib/ld-linux-x86-64.so.2` — a real,
working glibc dynamic loader. This is the entire mechanism the FHS wrapper exists to provide.

### h. Locale mechanics

Host leg (main checkout's `.venv/bin/python`, per the documented substitution above):

```
$ /home/yuta/Documents/typsphinx/.venv/bin/python -c "import locale,sys,os; ..."
ja_JP.UTF-8
('ja_JP', 'UTF-8')
utf-8
True
```

Sandbox leg (`uv run python -c "..."`, through the `uv` shim, this worktree's own environment):

```
$ uv run python -c "import locale,sys,os; ..."
ja_JP.UTF-8
('ja_JP', 'UTF-8')
utf-8
True
```

Identical on both legs: `setlocale(LC_ALL, '')` returns `ja_JP.UTF-8`, `getlocale(LC_MESSAGES)`
returns `('ja_JP', 'UTF-8')`, `sys.stdout.encoding` is `utf-8`, and `LOCALE_ARCHIVE` both is set and
exists (`/run/current-system/sw/lib/locale/locale-archive`, `os.path.exists(...)` → `True`) inside —
closing RESEARCH Assumption A1.

### Four one-sentence statements

- **`$HOME`** passes through the sandbox completely unchanged (`/home/yuta` both host-side and
  inside, and the maintainer's `~/.cache/typst` package cache is fully reachable from inside).
- **`TMPDIR`** passes through unchanged when the caller sets it, and `/tmp` itself is the same
  bind-mounted filesystem host-side and inside (identical device/inode), not a private tmpfs.
- **`/etc`** is a curated overlay: the security- and locale-relevant host files (`resolv.conf`,
  `nsswitch.conf`, `hosts`, `passwd`, `group`, `localtime`, `zoneinfo`, `ssl/certs`, `pki`) are
  symlinked in from the real host `/etc` via `/.host-etc`, while a handful of FHS-specific files
  (`login.defs`, `mtab`, `profile`, `rpc`) come from the sandbox's own closure — passthrough for
  the entries that matter, not a blank slate.
- **The locale** passes through unchanged: `LANG=ja_JP.UTF-8` is identical host-side and inside,
  `LOCALE_ARCHIVE` is set and reachable inside, and Sphinx's own locale-dependent warning text
  (measured next) is identical between a genuine host run and a through-shim run.

## Four-cell matrix

Scratch Sphinx project (`conf.py` with only `project = "nix08"`, an `index.rst` title page, and an
`orphan-probe.rst` title page referenced from no toctree) built four times with `-b dummy`, from
inside the worktree root, into four separate scratch output directories, all outside the
repository. The `orphan-probe.rst … WARNING:` line from each cell's stderr, verbatim:

| Cell | Command | Warning line |
|------|---------|---------------|
| H-ja | `/home/yuta/Documents/typsphinx/.venv/bin/python -m sphinx -b dummy <src> <out>` (maintainer `LANG=ja_JP.UTF-8`, main-checkout python per the documented substitution) | `<src>/orphan-probe.rst: WARNING: ドキュメントはどの toctree にも含まれていません [toc.not_included]` |
| H-C | same, prefixed `LC_ALL=C LANG=C LANGUAGE=C` | `<src>/orphan-probe.rst: WARNING: document isn't included in any toctree [toc.not_included]` |
| S-ja | `sphinx-build -b dummy <src> <out>` (through the shim, maintainer `LANG=ja_JP.UTF-8`) | `<src>/orphan-probe.rst: WARNING: ドキュメントはどの toctree にも含まれていません [toc.not_included]` |
| S-C | same, prefixed `LC_ALL=C LANG=C LANGUAGE=C` | `<src>/orphan-probe.rst: WARNING: document isn't included in any toctree [toc.not_included]` |

**Control:** H-ja ≠ H-C (Japanese vs. English warning body) — the locale axis genuinely changes
Sphinx's text on the host for this fixture. The control holds.

**S-ja = H-ja and S-C = H-C** — through the shim, the locale axis behaves exactly as it does on the
host.

**Finding:** REPRODUCES

The scratch project and all four output directories were removed after this step.

## Targeted test nodes (D-08 — not the full suite)

Through the `pytest` shim, `tests/test_state_guard_shapes_gate.py -k TestNoLostDiagnostics -q`:

```
$ pytest tests/test_state_guard_shapes_gate.py -k TestNoLostDiagnostics -q
======================= 7 passed, 11 deselected in 4.11s =======================
```

The same command prefixed `LC_ALL=C LANG=C LANGUAGE=C`:

```
$ LC_ALL=C LANG=C LANGUAGE=C pytest tests/test_state_guard_shapes_gate.py -k TestNoLostDiagnostics -q
======================= 7 passed, 11 deselected in 3.83s =======================
```

Both pass, 7/7, under both locales through the shim. `_locale_invariant_anchors()`'s Phase 52
anchoring keeps the historical instance fixed regardless of which locale the shim's caller sets.

## Consequence (for Phase 68, DOC-19 / DOC-21)

The sandbox reproduces the repository's known locale-dependent warning-text behaviour exactly as
the host does — it neither hides nor introduces a divergence. The maintainer's existing
`LC_ALL=C`-prefixed pre-check (run before dispatching to CI, to catch a warning whose body text is
locale-dependent before English-locale CI sees it) continues to do its job unchanged through the
`sphinx-build` shim: a warning that would surface in English under `LC_ALL=C` on a bare host run
surfaces identically when run through the shim, and the reverse holds for the maintainer's ordinary
`ja_JP.UTF-8` session. This phase makes no behavioural change — no locale variable is pinned in any
shim, and `flake.nix` is untouched by this task.
