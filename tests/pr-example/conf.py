# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

extensions = ['readthedocs_ext.external_version_warning']

source_suffix = '.rst'
master_doc = 'index'
project = 'pyexample'
copyright = '2021, readthedocs'
author = 'readthedocs'
version = '0.1'
release = '0.1'
language = 'en'
exclude_patterns = ['_build']
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'pyexampledoc'

html_context = {
    'slug': 'test-slug',
    'commit': 'deadd00d',
    'current_version': '123',
}

readthedocs_vcs_url = 'https://github.com/readthedocs/readthedocs.org/pull/7826'
readthedocs_build_url = 'https://readthedocs.org/projects/docs/builds/12759474/'
