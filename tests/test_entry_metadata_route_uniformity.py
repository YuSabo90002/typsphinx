"""
D-03's four-route uniformity, measured (Phase 44.2, SC#2 continuation / the
generalized-identity invariant): for every supported config shape, the title
and author that reach the template are the ones the resolved entry carries.

Each config is written into ``tmp_path`` (mirroring
``tests/test_config_template_mapping.py``'s idiom), never into a checked-in
fixture directory, so the repo's ``conf.py`` census (which plan 03 measures)
is unperturbed by this module.

**A measured correction to this module's own starting assumption (recorded
here rather than silently worked around, per this phase's own "measured,
not assumed" convention):** on the package-alone route (A4), leaving
``typst_template_mapping`` completely UNSET does NOT apply
``DEFAULT_PARAMETER_MAPPING`` -- ``TemplateEngine.__init__`` special-cases
"package set + mapping is None" to an EMPTY ``self.parameter_mapping``
(``template_engine.py``'s own D-05 docstring: "on the package-only path,
only pass what the user explicitly mapped"). Measured directly this
session: a package-alone build with NO ``typst_template_mapping`` at all
emits a bare ``#show: project.with()`` with ZERO arguments -- no title, no
author, nothing. D-03's "already reaches A1-A4 today" claim holds only once
``typst_template_mapping`` is EXPLICITLY set to include ``"project"``/
``"author"`` (which is exactly what every real package-alone user of this
extension already does -- see the package-alone config gate fixture that
pins BUG-A/B/C/E/F for CONF-02/CONF-03, which always sets an explicit
mapping). A4's config below therefore sets an EXPLICIT mapping equal to
``DEFAULT_PARAMETER_MAPPING``'s own contents (``project``->``title``,
``author``->``authors``, ``release``->``date``) rather than leaving the
setting unset -- this is what makes "author" an active mapping key on this
route, matching this module's own docstring claim, and is what the D-03
uniformity property actually requires on this route.

Phase 47 migration (R2, ``47-EXPECTED-STRUCTURE.md``): template application
(the entry title/author this module asserts) lives exclusively on the
WRAPPER file since the content/wrapper split, so every route reads its
resolved wrapper (``master.typ``) instead of the docname content file
(``index.typ``). Every config's ``typst_documents`` target was also
renamed from the identity ``'index'`` to ``'master'`` -- an identity target
is a BLD-03 self-collision: the wrapper write would silently overwrite the
docname's own content file at the same path, which happened to leave this
module's OLD ``index.typ``-reading assertions passing by accident (they
were reading the overwritten wrapper without knowing it), not because the
route was genuinely uniform through the correct file.
"""

FIXTURE_TEMPLATE_MARKER = "// A2-ROUTE-UNIFORMITY-SRCDIR-SHADOW-MARKER"

BUNDLED_BASE_TYP = """\
#let project(
  title: "",
  authors: (),
  date: none,
  toctree_maxdepth: 2,
  toctree_numbered: false,
  toctree_caption: "Contents",
  papersize: "a4",
  fontsize: 11pt,
  lang: "en",
  body
) = {
  set document(title: title, author: authors)
  body
}
"""


def test_route_a1_bundled_default_template_carries_entry_values(make_app, tmp_path):
    """A1: nothing configured -- the bundled default template is used, and
    the entry's own title/author reach the emitted master; config.project/
    config.author do not."""
    srcdir = tmp_path / "srcdir"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Config Project Must Not Win A1'
author = 'Config Author Must Not Win A1'
release = '1.0.0'

typst_documents = [
    ('index', 'master', 'Entry Title A1', 'Entry Author A1'),
]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n\nContent\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    content = (app.outdir / "master.typ").read_text(encoding="utf-8")

    assert 'title: "Entry Title A1"' in content
    assert 'authors: ("Entry Author A1",)' in content
    assert "Config Project Must Not Win A1" not in content
    assert "Config Author Must Not Win A1" not in content


def test_route_a2_srcdir_shadow_template_carries_entry_values(make_app, tmp_path):
    """A2: a <srcdir>/_typst/base.typ shadow (Phase 54, D-14 -- the
    shadow's source-side location moved from <srcdir>/base.typ into its
    own subdirectory so the resolved template's parent is a genuine
    bundle, never srcdir itself), nothing else configured -- the entry
    values still reach the emitted master, AND the marker unique to the
    srcdir-written template appears in the copied bundle at
    <outdir>/_template/typst/base.typ (OUT-04), proving the shadow file
    (not the bundled default) was the template actually used."""
    srcdir = tmp_path / "srcdir"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Config Project Must Not Win A2'
author = 'Config Author Must Not Win A2'
release = '1.0.0'

typst_documents = [
    ('index', 'master', 'Entry Title A2', 'Entry Author A2'),
]
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n\nContent\n")
    shadow_dir = srcdir / "_typst"
    shadow_dir.mkdir()
    (shadow_dir / "base.typ").write_text(
        FIXTURE_TEMPLATE_MARKER + "\n" + BUNDLED_BASE_TYP
    )

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    content = (app.outdir / "master.typ").read_text(encoding="utf-8")

    assert 'title: "Entry Title A2"' in content
    assert 'authors: ("Entry Author A2",)' in content
    assert "Config Project Must Not Win A2" not in content
    assert "Config Author Must Not Win A2" not in content

    template_content = (app.outdir / "_template" / "typst" / "base.typ").read_text(
        encoding="utf-8"
    )
    assert FIXTURE_TEMPLATE_MARKER in template_content, (
        "Expected the srcdir-written base.typ (with its distinguishing "
        "marker) to be the template actually copied into the built-in "
        "key's bundle -- without this, A2 and A1 are indistinguishable "
        "and this route is not really covered."
    )


def test_route_a3_explicit_template_carries_entry_values(make_app, tmp_path):
    """A3: typst_template names a non-default-named file, placed in its
    own subdirectory (Phase 54, A-01: a template resolving directly
    under srcdir's own root -- publishing the source tree as the
    bundle -- is refused; see CONF-17's parent-directory guard applied
    to every resolved key) -- the entry values still reach the emitted
    master."""
    srcdir = tmp_path / "srcdir"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Config Project Must Not Win A3'
author = 'Config Author Must Not Win A3'
release = '1.0.0'

typst_documents = [
    ('index', 'master', 'Entry Title A3', 'Entry Author A3'),
]

typst_template = '_typst/custom_template.typ'
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n\nContent\n")
    template_dir = srcdir / "_typst"
    template_dir.mkdir()
    (template_dir / "custom_template.typ").write_text(
        "// A3-ROUTE-UNIFORMITY-EXPLICIT-TEMPLATE-MARKER\n" + BUNDLED_BASE_TYP
    )

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    content = (app.outdir / "master.typ").read_text(encoding="utf-8")

    assert 'title: "Entry Title A3"' in content
    assert 'authors: ("Entry Author A3",)' in content
    assert "Config Project Must Not Win A3" not in content
    assert "Config Author Must Not Win A3" not in content


def test_route_a4_package_alone_carries_entry_values(make_app, tmp_path):
    """A4: typst_package alone, no typst_template. typst_template_mapping
    is set EXPLICITLY to make "author" an active mapping key (see this
    module's own docstring for the measured reason an unset mapping does
    NOT achieve this on the package route). Mirrors the package-alone
    config gate fixture's package value; does NOT copy that fixture's
    "author"-omitting custom mapping, which exists to pin a different
    property (the mapping loop's own authors-target precedence, covered
    in the entry metadata precedence matrix module instead)."""
    srcdir = tmp_path / "srcdir"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Config Project Must Not Win A4'
author = 'Config Author Must Not Win A4'
release = '1.0.0'

typst_documents = [
    ('index', 'master', 'Entry Title A4', 'Entry Author A4'),
]

typst_package = "@preview/charged-ieee:0.1.4"

typst_template_mapping = {
    'project': 'title',
    'author': 'authors',
    'release': 'date',
}
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n\nContent\n")

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    content = (app.outdir / "master.typ").read_text(encoding="utf-8")

    assert 'title: "Entry Title A4"' in content
    assert 'authors: ("Entry Author A4",)' in content
    assert "Config Project Must Not Win A4" not in content
    assert "Config Author Must Not Win A4" not in content


def test_route_both_configured_collapses_onto_template_and_carries_entry_values(
    make_app, tmp_path
):
    """D-03: typst_package AND typst_template together is NOT a fifth
    route -- the builder warns once and the package is suppressed,
    collapsing onto the template half (A3's shape, including A-01's
    own-subdirectory placement requirement). Entry values must still
    reach the emitted master on this collapsed route -- pinning this
    stops a future reader from re-deriving the routing rule
    independently."""
    srcdir = tmp_path / "srcdir"
    srcdir.mkdir()

    conf_content = """
extensions = ['typsphinx']

project = 'Config Project Must Not Win Collapse'
author = 'Config Author Must Not Win Collapse'
release = '1.0.0'

typst_documents = [
    ('index', 'master', 'Entry Title Collapse', 'Entry Author Collapse'),
]

typst_package = "@preview/charged-ieee:0.1.4"
typst_template = '_typst/custom_template.typ'
"""
    (srcdir / "conf.py").write_text(conf_content)
    (srcdir / "index.rst").write_text("Test\n====\n\nContent\n")
    template_dir = srcdir / "_typst"
    template_dir.mkdir()
    (template_dir / "custom_template.typ").write_text(BUNDLED_BASE_TYP)

    app = make_app(srcdir=srcdir, buildername="typst")
    app.build()

    content = (app.outdir / "master.typ").read_text(encoding="utf-8")

    assert 'title: "Entry Title Collapse"' in content
    assert 'authors: ("Entry Author Collapse",)' in content
    assert "Config Project Must Not Win Collapse" not in content
    assert "Config Author Must Not Win Collapse" not in content

    # The collapse: no bare `#import "@preview/...:..."` package-only import
    # line (that shape belongs to the package-ALONE route, A4) -- the
    # template import shape (root-absolute, OUT-06) wins instead.
    assert '#import "/_template/typst/custom_template.typ": project' in content
    assert '#import "@preview/charged-ieee:0.1.4"\n' not in content
