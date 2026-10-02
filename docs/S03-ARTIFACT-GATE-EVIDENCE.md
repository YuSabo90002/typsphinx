# S03 — Artifact-gate falsifiability evidence: the HTML gate goes RED without `dot`

This file is the measurement record for M002/S03/T04. The milestone criterion it
discharges is that *"the artifact gate goes RED when `dot` is unavailable,
demonstrated by MEASUREMENT rather than asserted"*. A gate that has only ever
been observed GREEN is not known to detect anything; what follows is the record
of it observed failing, and then observed GREEN again on a byte-identical tree.

The gate under test is `tests/test_graphviz_docs_gate.py`'s third class,
`TestDogfoodedDiagramHTMLBuild` (shipped by T01–T03). It performs a real
`sphinx-build -b html` of typsphinx's own `docs/source` tree and asserts, on the
built `user_guide/diagrams.html`, both that the dogfooded `.. graphviz::`
rendered to a real on-disk PNG **and** that the raw DOT source never reaches the
reader as page text.

**Method — remove the dependency, never mutate the assertion.** No test
assertion, no `docs/source/user_guide/diagrams.rst`, no `flake.nix` and nothing
under `typsphinx/` was edited for this measurement, and nothing was uninstalled.
Every RED was produced by changing only `PATH` for the duration of one command.
This is the same pattern S02 used for the fail-open defect; see
`docs/S02-LOCAL-PARITY-EVIDENCE.md`.

## Measurement environment

| Item | Value |
|---|---|
| Date | 2026-10-03 |
| Checkout | git worktree `.gsd-worktrees/M002` (`.git` is a file) |
| Shell route | `nix develop --no-write-lock-file ./.#default --command bash -c '…'` |
| Python | 3.14.4 (worktree-local `.venv`, uv-managed CPython) |
| pytest | 9.1.1 |
| Sphinx | 8.2.3 |
| Graphviz | 12.2.1 (`dot - graphviz version 12.2.1 (0)`) |
| `dot` resolves to | `/nix/store/d5nx177j7n96jmd38x9fpankrpkp5szj-graphviz-12.2.1/bin/dot` |
| Host locale | Japanese (`LANG` passed through the FHS sandbox unchanged) |

**Why the devShell is mandatory here.** `direnv` never loads inside a git
worktree, so the authorised route is the explicit `nix develop …` command above.
Ambient `shutil.which("dot")` in this worktree **outside** that shell is `None`
— measured. Running the gate there SKIPS the whole class; that skip is neither a
pass nor a RED demonstration, and must not be read as either.

## GREEN / RED side by side

Both columns are a clean `-b html` build of the same unmodified `docs/source`
into a fresh output directory. The only difference between them is whether a
usable `dot` is reachable on `PATH`.

| Subject of assertion | GREEN (`dot` present) | RED (`dot` unreachable) |
|---|---|---|
| `sphinx-build -b html` exit code | 0 | 0 *(fails open — see below)* |
| `class="graphviz"` occurrences | **2** | **0** |
| `<img src>` matching `graphviz-<sha1>.png` | **1** | **0** |
| `_images/graphviz-*.png` files on disk | **1** | **0** |
| `<object` occurrences (pins png format) | 0 | 0 |
| visible text contains `digraph dogfood {` | **0** | **1** |
| raw markup contains `digraph dogfood {` | 0 | 1 |
| visible text contains `Vorthaneglim` | **0** | **1** |
| raw markup contains `Vorthaneglim` | 1 *(the `:alt:` text)* | 1 |

The bolded rows are exactly the subjects T01 and T02 wrote assertions over, and
every one of them moves in the direction that breaks its assertion. Note the
exit code does **not** move: the build still succeeds. That fail-open behaviour
is the whole reason an artifact-level gate was needed instead of relying on the
build's own exit status.

`Vorthaneglim` has inverted polarity in HTML relative to the PDF: in a correct
page the node labels are pixels inside the PNG and appear only inside the
`<img alt="…">` attribute (raw 1 / visible 0); their appearance in *visible*
text means the DOT source leaked onto the page.

## Which RED route was used

Both a **pytest-level** RED and an **artifact-level** RED were obtained. The
pytest failures are the primary evidence; the artifact table above is the
corroborating detail.

The obstacle the plan anticipated is real: the fixture skips on
`shutil.which("dot") is None`, which is correct production behaviour but is not
a RED demonstration. So the skip guard — and only the skip guard — was bypassed
by putting a stub named `dot` first on `PATH` and filtering the real Graphviz
`bin` directory out of it (derived with `dirname "$(command -v dot)"`). `PATH`
was never blanked, so `uv` and `python` stayed reachable. **Two different stubs
were tried, and they are not equivalent** — which is the main finding of this
task.

### Route A — stub that exists and exits 1 → PARTIAL RED

A `/bin/sh` stub printing to stderr and exiting 1. `shutil.which("dot")` found
it, so the class ran instead of skipping.

```
which(dot) = /tmp/t04_red_XXXXXX/bin/dot
stub returncode = 1
uv run pytest tests/test_graphviz_docs_gate.py -q
  → 1 failed, 19 passed
  FAILED …::TestDogfoodedDiagramHTMLBuild::test_page_carries_a_graphviz_img_backed_by_a_real_png
     AssertionError: assert 0 >= 1   # html.count('class="graphviz"')
```

Only the *presence* half reddened. The three absence assertions still passed,
because this route emits **nothing at all** for the diagram rather than leaking
its source.

### Route B — stub whose exec fails (bogus shebang) → FULL RED

A stub whose only line is `#!/nonexistent/t04-no-such-interpreter`, `chmod +x`.
`shutil.which` is satisfied (the file is executable), but the child's `execve`
fails:

```
which(dot) = /tmp/t04_red2_XXXXXX/bin/dot
child exec raises OSError: FileNotFoundError 2 No such file or directory

uv run pytest tests/test_graphviz_docs_gate.py -q
  → 4 failed, 16 passed
  FAILED …::test_page_carries_a_graphviz_img_backed_by_a_real_png
  FAILED …::test_raw_dot_source_is_not_visible_page_text
  FAILED …::test_raw_dot_source_is_absent_from_the_raw_markup_too
  FAILED …::test_node_labels_are_not_visible_page_text
```

All four rendering-dependent assertions in the class fail as real pytest
failures, in both directions, with no assertion edited. `test_html_build_succeeds`
and `test_png_output_format_is_pinned` correctly keep passing: the build does
exit 0 and there is still no `<object>`.

### Why the two routes differ — measured in upstream source, not inferred

`sphinx/ext/graphviz.py` has two distinct failure paths, and only one of them
reproduces the reported defect:

* **`except CalledProcessError` → `raise GraphvizError`.** `render_dot_html`
  catches it, warns, and raises `nodes.SkipNode` — the node contributes nothing
  to the page. This is Route A, and it is *not* the shape users reported.
* **`except OSError` → warn once, then `return None, None`.** Back in
  `render_dot_html`, `if fname is None: self.body.append(self.encode(code))`
  appends the DOT source to the page body as bare text. This is Route B, and it
  is the real-world shape: a *missing* binary, not a broken one.

Measured markup from the Route B page confirms the leaked text is unwrapped —
no `<pre>`, no tag of its own — sitting directly between the `<figure>` and its
`<figcaption>`:

```html
<figure class="align-default" id="id1">
digraph dogfood {
    &quot;Vorthaneglim&quot; -&gt; &quot;Pellucidrane&quot;;
}<figcaption>
<p><span class="caption-text">Thessomantic dogfood pipeline</span>…
```

This is why T02's primary absence assertion is written over **tag-stripped
visible text**: the leak is not inside any element that a markup-shaped check
would naturally look at, and the `&quot;` entities mean the raw bytes do not
match a naive search for the quoted labels either.

### Locale note, incidentally confirming a T01/T03 design decision

With `dot` genuinely absent the build's warning arrived localised:

```
WARNING: dot コマンド 'dot' は実行できません (graphviz 出力のために必要です)。graphviz_dot の設定を確認してください
```

This is direct confirmation that Class 3 is right to assert `returncode == 0`
only and to gate neither warning count nor warning text — an English-text
assertion would have passed in CI and failed on this machine.

## Restored GREEN

`PATH` restored (stub directories deleted; `dot` back to the Graphviz 12.2.1
store path), same command, same tree:

```
uv run pytest tests/test_graphviz_docs_gate.py -q
  → 20 passed in 7.27s      (0 skipped — the class ran, it did not skip)
```

Identical to the pre-RED baseline recorded at the top of this measurement
(`20 passed in 7.24s`, 20 collected, 0 skipped). The tree is restored
byte-identically: `git status --porcelain` filtered to everything outside
`.gsd/` is empty.

## Regression controls held

| Control | Command | Result |
|---|---|---|
| Gate module baseline | `uv run pytest tests/test_graphviz_docs_gate.py -q` | 20 passed, 0 skipped |
| Combined gate suite | `uv run pytest tests/test_graphviz_docs_gate.py tests/test_readthedocs_config.py -q` | 27 passed (20 + 7) |
| Config gate untouched | `git diff --stat -- tests/test_readthedocs_config.py` | empty (rc 0) |
| Typst route untouched | `git diff --stat main -- typsphinx/` | empty (rc 0) — the milestone's control |
| Working tree clean | `git status --porcelain` outside `.gsd/` | empty |

`typsphinx/` being byte-identical to `main` is the load-bearing control for the
milestone: this defect and its gate live entirely in docs configuration and test
code, and the Typst conversion path was never touched.

## What this evidence does NOT cover

* **The published Read the Docs page.** Everything above is a *local* build.
  That the fix reaches the actually-published HTML is S04's job, not this file's.
* **The Japanese site.** R022 (the `ja` translation site) is deferred and was
  not built or inspected here.
* **CI detection of the original defect.** Stated plainly because it is a
  recorded milestone decision rather than a defect to fix: GitHub Actions'
  `ubuntu-latest` image preinstalls `dot`, so in CI this class renders a real
  PNG and passes — it would have passed unchanged throughout the entire original
  outage, which was a missing Graphviz on the *Read the Docs* builder. What
  Class 3 durably guards is docs-**source** regression (the directive being
  removed, renamed, or demoted to a literal block). The environment-independent
  half is `tests/test_readthedocs_config.py`, which asserts `graphviz` is in
  `.readthedocs.yaml`'s `build.apt_packages` and needs no build at all.
  Detection is split across the two gates on purpose.
* **Route B as a production scenario.** The bogus-shebang stub is a measurement
  instrument for forcing the skip guard open, not a condition any real builder
  is in. The condition real builders hit is plain absence, which is the
  artifact-level column of the table above.
