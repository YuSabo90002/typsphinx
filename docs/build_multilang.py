#!/usr/bin/env python3
"""Multi-language documentation build script for typsphinx.

This script builds English and Japanese versions of the documentation
and organizes them for GitHub Pages deployment.
"""

import os
import shutil
import subprocess
from pathlib import Path

# Configuration
DOCS_DIR = Path(__file__).parent
SOURCE_DIR = DOCS_DIR / "source"
BUILD_DIR = DOCS_DIR / "_build"
MULTILANG_DIR = BUILD_DIR / "multilang"

LANGUAGES = {
    "en": "English",
    "ja": "日本語",
}


def clean_build_dir():
    """Clean the multilang build directory."""
    print(f"Cleaning build directory: {MULTILANG_DIR}")
    if MULTILANG_DIR.exists():
        shutil.rmtree(MULTILANG_DIR)
    MULTILANG_DIR.mkdir(parents=True, exist_ok=True)
    print("✓ Build directory cleaned\n")


def build_language(lang_code):
    """Build documentation for a specific language."""
    print(f"{'='*70}")
    print(f"Building {LANGUAGES[lang_code]} ({lang_code}) documentation")
    print(f"{'='*70}\n")

    output_dir = MULTILANG_DIR / lang_code

    # Set language environment variable
    env = os.environ.copy()
    env["SPHINX_LANGUAGE"] = lang_code

    # Build HTML
    cmd = [
        "sphinx-build",
        "-b",
        "html",
        "-D",
        f"language={lang_code}",
        str(SOURCE_DIR),
        str(output_dir),
    ]

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)

    # Print only warnings and errors
    if result.stderr:
        for line in result.stderr.split("\n"):
            if (
                "WARNING" in line
                or "ERROR" in line
                or "warning" in line
                or "error" in line
            ):
                print(line)

    print(f"\n✓ {LANGUAGES[lang_code]} build complete: {output_dir}\n")


def create_redirect_page():
    """Create root index.html that redirects to English version with language detection."""
    redirect_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link rel="canonical" href="https://yusabo90002.github.io/typsphinx/en/index.html">
    <title>typsphinx Documentation</title>
    <script>
      // Smart language detection with session storage
      (function() {
        // Check if user already visited a language page in this session
        var visitedLang = sessionStorage.getItem('typsphinx_lang');

        // If user explicitly visited a language page, don't redirect again
        if (visitedLang) {
          return;
        }

        // Otherwise, detect browser language and redirect
        var lang = navigator.language || navigator.userLanguage;
        if (lang && lang.startsWith('ja')) {
          window.location.href = './ja/index.html';
        } else {
          window.location.href = './en/index.html';
        }
      })();
    </script>
  </head>
  <body>
    <h1>typsphinx Documentation</h1>
    <p>Redirecting to documentation...</p>
    <ul>
      <li><a href="./en/index.html">English Documentation</a></li>
      <li><a href="./ja/index.html">日本語ドキュメント</a></li>
    </ul>
  </body>
</html>
"""

    index_file = MULTILANG_DIR / "index.html"
    index_file.write_text(redirect_html, encoding="utf-8")
    print(f"✓ Created redirect page: {index_file}\n")


def create_nojekyll():
    """Create .nojekyll file for GitHub Pages."""
    nojekyll_file = MULTILANG_DIR / ".nojekyll"
    nojekyll_file.touch()
    print(f"✓ Created .nojekyll file: {nojekyll_file}\n")


def print_summary():
    """Print build summary."""
    print(f"\n{'='*70}")
    print("✓ Multi-language build complete!")
    print(f"{'='*70}\n")
    print(f"Output directory: {MULTILANG_DIR}\n")
    print("Language versions:")
    for lang_code, lang_name in LANGUAGES.items():
        lang_dir = MULTILANG_DIR / lang_code
        if lang_dir.exists():
            file_count = sum(1 for _ in lang_dir.rglob("*.html"))
            print(
                f"  - {lang_name:10s} ({lang_code}): {lang_dir} ({file_count} HTML files)"
            )

    print(f"\nRedirect page: {MULTILANG_DIR / 'index.html'}")
    print("\nTo test locally, run:")
    print(f"  cd {MULTILANG_DIR} && python -m http.server 8000")
    print("  Then visit: http://localhost:8000\n")


def main():
    """Main build process."""
    print(f"{'='*70}")
    print("typsphinx Multi-language Documentation Build")
    print(f"{'='*70}\n")

    # Clean build directory
    clean_build_dir()

    # Build each language
    for lang_code in LANGUAGES:
        try:
            build_language(lang_code)
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Error building {LANGUAGES[lang_code]} ({lang_code}):")
            print(f"  {e}")
            if e.stderr:
                print(f"\nError output:\n{e.stderr}")
            return 1

    # Create redirect page
    create_redirect_page()

    # Create .nojekyll
    create_nojekyll()

    # Print summary
    print_summary()

    return 0


if __name__ == "__main__":
    exit(main())
