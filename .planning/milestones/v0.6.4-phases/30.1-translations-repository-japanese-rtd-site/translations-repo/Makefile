# Locale-tooling entry point for typsphinx-doc-translations (D-12 arrival
# half). This file lives at the REPOSITORY ROOT, not inside a docs/
# subdirectory -- the translations repository has no docs/ of its own; the
# documentation source lives in the `typsphinx` submodule.
#
# Adapted from typsphinx's own docs/Makefile gettext/locale-update targets,
# with two deliberate differences documented at each target below.

SPHINXBUILD  ?= sphinx-build
SUBMODULE    = typsphinx
SOURCEDIR    = $(SUBMODULE)/docs/source
BUILDDIR     = $(SUBMODULE)/docs/_build
LOCALEDIR    = locale
LANGUAGE     = ja

.PHONY: help locale-update locale-stat

# Put it first so that "make" without an argument prints this, matching
# typsphinx's own docs/Makefile convention.
help:
	@echo "Available targets:"
	@echo "  locale-update  Regenerate .pot from the submodule's current"
	@echo "                 English source and merge into $(LOCALEDIR)/$(LANGUAGE)/"
	@echo "  locale-stat    Print translation coverage for $(LOCALEDIR)/$(LANGUAGE)/"

# D-12 arrival-half entry point: .pot regeneration + sphinx-intl merge,
# driven from the submodule's source rather than a local docs/ tree.
#
# -d/--locale-dir is required here and is ABSENT from typsphinx's own
# docs/Makefile locale-update target -- there, conf.py's locale_dirs
# already points at the right place because the command runs from inside
# docs/. Here the command runs from the translations-repository root and
# the catalogs live outside the submodule entirely, so sphinx-intl has no
# other way to find them.
locale-update:
	@$(SPHINXBUILD) -M gettext $(SOURCEDIR) $(BUILDDIR)
	sphinx-intl update -p $(BUILDDIR)/gettext -d $(LOCALEDIR) -l $(LANGUAGE)
	@echo "Locale updated. Translation files are in $(LOCALEDIR)/$(LANGUAGE)/LC_MESSAGES/."

# Coverage readout without running a build -- lets a translator see how
# much work remains before touching anything. Measured baseline
# 2026-07-26: 257/1058 msgids translated (24.3%), with api/index,
# contributing, changelog and user_guide/templates at zero coverage.
locale-stat:
	sphinx-intl stat -d $(LOCALEDIR) -l $(LANGUAGE)

# Deliberately no locale-init target: typsphinx's own docs/Makefile
# locale-init and locale-update targets have byte-identical bodies (the
# distinction between "first run" and "update" never actually existed
# there), so collapsing them into locale-update alone loses no behavior.
#
# Deliberately no html / html-ja / multilang / serve-multilang target:
# this repository does not build documentation locally -- RTD's ja project
# is the only builder, and a local HTML target here would be a second,
# undogfooded path with no consumer.
#
# Deliberately no catch-all "%: Makefile" rule: typsphinx's own
# docs/Makefile has one because it proxies Sphinx's full -M surface; this
# file exposes exactly two verbs (locale-update, locale-stat) and a silent
# fall-through to sphinx-build would be a footgun, not a convenience.
