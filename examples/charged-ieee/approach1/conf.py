# Configuration file for charged-ieee example (Approach 1)
# Approach 1: Use typst_template_function dict format and typst_authors (Recommended)


# -- Project information -----------------------------------------------------
project = "Machine Learning Applications in Computer Vision"
copyright = "2025, John Doe"
author = "John Doe"
release = "1.0"

# -- General configuration ---------------------------------------------------
extensions = ["typsphinx"]

# -- Typst output options ----------------------------------------------------
typst_documents = [
    ("index", "paper", project, author, "typst"),
]

# -- Typst Universe package configuration ------------------------------------
# Use charged-ieee template from Typst Universe
typst_package = "@preview/charged-ieee:0.1.4"

# -- Author details configuration (Approach 1 - Recommended) -----------------
# IEEE専用の設定変数
ieee_abstract = """This paper presents novel approaches to machine learning
applications in computer vision. We demonstrate state-of-the-art results on
benchmark datasets and provide comprehensive analysis of our methodology."""

ieee_keywords = [
    "Machine Learning",
    "Computer Vision",
    "Deep Learning",
    "Neural Networks",
]

# 著者の詳細情報（辞書形式）
typst_authors = {
    "John Doe": {
        "department": "Computer Science",
        "organization": "Massachusetts Institute of Technology",
        "location": "Cambridge, MA",
        "email": "john.doe@mit.edu",
    }
}

# テンプレート関数とパラメータの統合設定（辞書形式）
# 通常のPython変数参照で他の設定値を再利用
#
# NOTE: no citation-source ("refs.bib"-style) parameter here. The package-only
# path (typst_package, no typst_template) has no asset-copying mechanism to
# place a supporting file next to the emitted .typ
# (TypstBuilder.copy_template_assets() early-returns when typst_template is
# unset), so a parameter naming such a file would point at a path that never
# resolves. A template parameter naming a file path must refer to a file the
# build itself produces in the output directory.
typst_template_function = {
    "name": "ieee",
    "params": {
        "abstract": ieee_abstract,
        "index-terms": ieee_keywords,
        "paper-size": "a4",
    },
}
