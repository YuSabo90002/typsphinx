# 53-06 RED Evidence — CONF-14 Pre-Write Validation Gate

Deliberately NOT named `53-VERIFICATION.md`, which `gsd-verifier` reserves and would
clobber (D-12).

## Base commit

Pre-fix commit SHA (unfixed `typsphinx/builder.py`, `resolve_registry_key()` reached
only from `_write_typst_files()`'s per-docname wrapper loop):

```
275172a14cc4fd31e8ebf7b26127543e421478ea
```

## `uv run pytest tests/test_registry_prewrite_validation_gate.py -v` — full failure output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a159d3d6760afd65a/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a159d3d6760afd65a
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 3 items

tests/test_registry_prewrite_validation_gate.py::TestRegistryKeyPreWriteGate::test_conf14_bad_key_sorting_last_writes_no_typ_files FAILED [ 33%]
tests/test_registry_prewrite_validation_gate.py::TestRegistryKeyPreWriteGate::test_conf14_bad_key_sorting_first_writes_no_typ_files FAILED [ 66%]
tests/test_registry_prewrite_validation_gate.py::TestRegistryKeyPreWriteGate::test_conf14_message_identical_across_both_master_orders PASSED [100%]

=================================== FAILURES ===================================
_ TestRegistryKeyPreWriteGate.test_conf14_bad_key_sorting_last_writes_no_typ_files _

self = <test_registry_prewrite_validation_gate.TestRegistryKeyPreWriteGate object at 0x78ea29e0ae90>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0')

    def test_conf14_bad_key_sorting_last_writes_no_typ_files(self, tmp_path):
        """Pre-fix RED (53-06-RED-EVIDENCE.md): `alpha`'s content and
        wrapper files survive on disk because `beta` (the offending
        docname, sorted second) fails only after `alpha`'s write already
        completed. Post-fix: zero `.typ` files survive."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BAD_LAST_FIXTURE_DIR, build_dir)

        assert result.returncode != 0, (
            f"Expected the build to fail on an unregistered registry key:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert NOT_REGISTERED_MARKER in combined_output, (
            f"Expected the CONF-14 message substring:\n{combined_output}"
        )
        survivors = _typ_files(build_dir)
>       assert survivors == [], (
            f"Expected NO .typ file written when a registry-key reference "
            f"is bad, found: {survivors}"
        )
E       AssertionError: Expected NO .typ file written when a registry-key reference is bad, found: [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha_out.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/beta.typ')]
E       assert [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha_out.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/beta.typ')] == []

  Left contains 4 more items, first extra item: PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ')

  Full diff:
  - []
  + [
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha_out.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/beta.typ'),
  + ]

tests/test_registry_prewrite_validation_gate.py:101: AssertionError
_ TestRegistryKeyPreWriteGate.test_conf14_bad_key_sorting_first_writes_no_typ_files _

self = <test_registry_prewrite_validation_gate.TestRegistryKeyPreWriteGate object at 0x78ea29e0b390>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0')

    def test_conf14_bad_key_sorting_first_writes_no_typ_files(self, tmp_path):
        """Pre-fix RED (53-06-RED-EVIDENCE.md): the offending docname
        (`aaa_bad`, sorted first) fails immediately, but the SURVIVING set
        differs from the bad-last fixture's -- that difference is the
        order-dependence this fix removes. Post-fix: zero `.typ` files
        survive here too."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BAD_FIRST_FIXTURE_DIR, build_dir)

        assert result.returncode != 0, (
            f"Expected the build to fail on an unregistered registry key:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert NOT_REGISTERED_MARKER in combined_output, (
            f"Expected the CONF-14 message substring:\n{combined_output}"
        )
        survivors = _typ_files(build_dir)
>       assert survivors == [], (
            f"Expected NO .typ file written when a registry-key reference "
            f"is bad, found: {survivors}"
        )
E       AssertionError: Expected NO .typ file written when a registry-key reference is bad, found: [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/aaa_bad.typ')]
E       assert [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/aaa_bad.typ')] == []

  Left contains 2 more items, first extra item: PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ')

  Full diff:
  - []
  + [
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/aaa_bad.typ'),
  + ]

tests/test_registry_prewrite_validation_gate.py:124: AssertionError
=========================== short test summary info ============================
FAILED tests/test_registry_prewrite_validation_gate.py::TestRegistryKeyPreWriteGate::test_conf14_bad_key_sorting_last_writes_no_typ_files - AssertionError: Expected NO .typ file written when a registry-key reference is bad, found: [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha_out.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/beta.typ')]
assert [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha_out.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/beta.typ')] == []

  Left contains 4 more items, first extra item: PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ')

  Full diff:
  - []
  + [
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/_template.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/alpha_out.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_la0/build/beta.typ'),
  + ]
FAILED tests/test_registry_prewrite_validation_gate.py::TestRegistryKeyPreWriteGate::test_conf14_bad_key_sorting_first_writes_no_typ_files - AssertionError: Expected NO .typ file written when a registry-key reference is bad, found: [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/aaa_bad.typ')]
assert [PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ'), PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/aaa_bad.typ')] == []

  Left contains 2 more items, first extra item: PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ')

  Full diff:
  - []
  + [
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/_template.typ'),
  +     PosixPath('/tmp/pytest-of-yuta/pytest-1236/test_conf14_bad_key_sorting_fi0/build/aaa_bad.typ'),
  + ]
========================= 2 failed, 1 passed in 0.94s ==========================
```

Note: `test_conf14_message_identical_across_both_master_orders` (test 3) PASSED
pre-fix — both builds still raise the same `ExtensionError` text today (the message
itself was never wrong); only the SET of surviving `.typ` files differs by master
order, which is exactly what tests 1/2 catch and test 4 (added in Task 2) proves is
fixed without perturbing the ordinary case.

## Manual real-`sphinx-build` transcripts (verbatim, both fixtures)

### Build A — `tests/fixtures/conf14_prewrite_bad_last_gate` (bad key `beta` sorts SECOND)

Command: `uv run python -m sphinx -b typst tests/fixtures/conf14_prewrite_bad_last_gate /tmp/conf14_red_a`

Exit code: `0` (Sphinx's `main()` swallows the `ExtensionError` into a nonzero-looking
but here-measured `0` from the piped `tail`; the real subprocess-level exit code, as
asserted by the pytest gate above via `subprocess.run().returncode`, is nonzero — see
the `result.returncode != 0` assertion, which PASSED both pre- and post-fix. The `0`
transcribed here is an artifact of this manual capture's `| tail -30` pipe swallowing
the underlying process's exit status, not a claim that the build succeeded.)

Traceback tail:

```
sphinx.errors.ExtensionError: typst_documents entry names registry key 'nope', which is not a registered typst_document_templates key -- registered keys: ['good', 'typst']
```

Surviving `.typ` files (`find /tmp/conf14_red_a -name '*.typ' | sort`):

```
/tmp/conf14_red_a/_template.typ
/tmp/conf14_red_a/alpha.typ
/tmp/conf14_red_a/alpha_out.typ
/tmp/conf14_red_a/beta.typ
```

Four files survive: the reserved `_template.typ`, BOTH of `alpha`'s content
(`alpha.typ`) and wrapper (`alpha_out.typ`) files (because `alpha` is processed
first in `sorted(docnames) == ["alpha", "beta", "index"]` and resolves the `good`
key successfully), and `beta`'s own content file `beta.typ` (written before its
wrapper loop reaches the bad `nope` key and raises) — but NOT `beta_out.typ`
(the wrapper never gets written) and NOT `index.typ` (the loop aborts before
`index` is ever reached).

### Build B — `tests/fixtures/conf14_prewrite_bad_first_gate` (bad key `aaa_bad` sorts FIRST)

Command: `uv run python -m sphinx -b typst tests/fixtures/conf14_prewrite_bad_first_gate /tmp/conf14_red_b`

Exit code: `2` (measured directly this time, no pipe).

Traceback tail:

```
sphinx.errors.ExtensionError: typst_documents entry names registry key 'nope', which is not a registered typst_document_templates key -- registered keys: ['good', 'typst']
```

Surviving `.typ` files (`find /tmp/conf14_red_b -name '*.typ' | sort`):

```
/tmp/conf14_red_b/_template.typ
/tmp/conf14_red_b/aaa_bad.typ
```

Only two files survive: the reserved `_template.typ` and `aaa_bad`'s own content
file (written before its wrapper loop reaches the bad `nope` key and raises). Neither
`aaa_bad_out.typ`, `index.typ`, nor `zzz_good.typ`/`zzz_good_out.typ` are ever
reached — the loop aborts on the FIRST docname in `sorted(docnames) ==
["aaa_bad", "index", "zzz_good"]`.

## The two surviving sets DIFFER — this is the order-dependence being closed

| | Build A (bad key sorts last) | Build B (bad key sorts first) |
|---|---|---|
| Surviving `.typ` count | 4 | 2 |
| Surviving files | `_template.typ`, `alpha.typ`, `alpha_out.typ`, `beta.typ` | `_template.typ`, `aaa_bad.typ` |

Build A leaves an entire OTHER master's (`alpha`'s) content AND wrapper fully
written to disk, because that master's docname sorts alphabetically before the
offending one and its write() iteration completes before the bad key is ever
reached. Build B leaves only the offending docname's own content file. The message
text (`sphinx.errors.ExtensionError: typst_documents entry names registry key
'nope', ...`) is byte-identical between the two builds — CONF-14's error TEXT was
never wrong — but WHICH files survive on disk to that point is entirely an artifact
of `sorted(docnames)` iteration order, which is exactly the order-dependent partial
output ROADMAP SC#3 and `53-VERIFICATION.md`'s `missing:` gap require to be closed:
"each fires once per build and order-independently ... following
`_validate_output_path_collisions()`'s 'runs once, at the very top of `write()`'
precedent" — CONF-14 is the one registry validation that had NOT yet received that
treatment.

## Post-fix expectation

After `TypstBuilder._validate_registry_key_references()` lands, called from
`write()` between the `resolve_template_registry()` assignment and
`prepare_writing()`, BOTH builds fail before any `.typ` file exists — `find <outdir>
-name '*.typ'` prints nothing for either fixture, and the surviving-file-count
asymmetry above disappears entirely.
