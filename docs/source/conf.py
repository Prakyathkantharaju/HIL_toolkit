# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys

sys.path.insert(0, os.path.abspath("../.."))





# project = 'HIL'
# copyright = '2022, Prakyath Kantharaju'
# author = 'Prakyath Kantharaju'
# release = '0.0.1'

# # -- General configuration ---------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = [ 'sphinx.ext.napoleon', 'myst_parser',     'sphinx.ext.duration',
#     'sphinx.ext.doctest',
#     'sphinx.ext.autodoc' ]

# templates_path = ['_templates']
# exclude_patterns = []

# napoleon_google_docstring = False


# # -- Options for HTML output -------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']

# source_suffix = {
#     '.rst': 'restructuredtext',
#     '.txt': 'markdown',
#     '.md': 'markdown',
# }

# # html_theme_options = {
# #     # 'analytics_id': 'G-XXXXXXXXXX',  #  Provided by Google in your dashboard
# #     'analytics_anonymize_ip': False,
# #     'logo_only': False,
# #     'display_version': True,
# #     'prev_next_buttons_location': 'bottom',
# #     'style_external_links': False,
# #     'vcs_pageview_mode': '',
# #     'style_nav_header_background': 'white',
# #     # Toc options
# #     'collapse_navigation': True,
# #     'sticky_navigation': True,
# #     'navigation_depth': 4,
# #     'includehidden': True,
# #     'titles_only': False
# # }

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
    "sphinxemoji.sphinxemoji",
    "sphinx_copybutton",
    "myst_nb",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]

# Ignore duplicated sections warning
suppress_warnings = ["epub.duplicated_toc_entry"]
nitpicky = False  # Set to True to get all warnings about crosslinks

# Prefix document path to section labels, to use:
# `path/to/file:heading` instead of just `heading`
autosectionlabel_prefix_document = True

# -- Options for autodoc -------------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = False
napoleon_use_ivar = False
napoleon_use_rtype = False
add_module_names = False  # If true, the current module name will be prepended to all description

# -- Options for ipython directive  ----------------------------------------

# Doesn't work?
# ipython_promptin = ">"  # "In [%d]:"
# ipython_promptout = ">"  # "Out [%d]:"

# -- Options for myst_nb ---------------------------------------------------
nb_execution_mode = "force"
nb_execution_raise_on_error = True

# googleanalytics_id = "G-DVXSEGN5M9"


# NumPyDoc configuration -----------------------------------------------------

# -- Options for HTML output -------------------------------------------------

# html_favicon = "img/icon.ico"
# html_logo = "img/neurokit.png"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_book_theme"

# https://sphinx-book-theme.readthedocs.io/en/latest/customize/index.html
html_theme_options = {
    "repository_url": "https://127.0.0.1:6006",
    "repository_branch": "dev",  # TODO: remove this before merging
    "use_repository_button": True,
    "use_issues_button": True,
    "path_to_docs": "docs/",
    "use_edit_page_button": True,
    "logo_only": True,
    "show_toc_level": 1,
}