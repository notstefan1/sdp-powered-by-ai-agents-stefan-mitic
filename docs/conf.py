"""Sphinx configuration file."""

# -- Project information -----------------------------------------------------
project = "Social Network Platform"
copyright = "2026, Stefan Mitic"
author = "Stefan Mitic"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx_new_tab_link",
]

new_tab_link_show_external_link_icon = True

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"

html_theme_options = {
    "source_repository": "https://github.com/notstefan1/sdp-powered-by-ai-agents-stefan-mitic",
    "source_branch": "main",
    "source_directory": "docs/",
}

html_title = "Social Network Platform"
html_show_sphinx = False

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]
