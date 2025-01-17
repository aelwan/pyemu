# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys
import sphinx_rtd_theme
sys.path.insert(0, os.path.abspath(os.path.join("..","..","pyemu")))
#sys.path.insert(0, os.path.abspath(os.path.join("..","..")))
print(sys.path)
print(os.listdir(os.path.abspath(os.path.join("..",".."))))


# -- Project information -----------------------------------------------------

project = 'pyEMU'
copyright = '2019, pyEMU development team'
author = 'pyEMU development team'

# The full version, including alpha/beta/rc tags
release = '0.9'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'sphinx.ext.todo',
    'sphinx.ext.autosummary'
]

autoclass_content = "both"  # include both class docstring and __init__

autosummary_generate = True  # Make _autosummary files and include them
autosummary_imported_members = True
napoleon_numpy_docstring = False  # Force consistency, leave only Google
#napoleon_use_rtype = False  # More legible

# autodoc_member_order = 'bysource'
add_module_names = True
# Add any paths that contain templates here, relative to this directory.
templates_path = [os.path.join('source','_templates')]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

#master_doc = "index"

# -- Options for HTML output -------------------------------------------------

pygments_style = 'sphinx'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']