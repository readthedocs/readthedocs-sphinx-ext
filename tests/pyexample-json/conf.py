# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

extensions = ['readthedocs_ext.readthedocs']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'pyexample'
copyright = u'2015, readthedocs'
author = u'readthedocs'
version = '0.1'
release = '0.1'
language = 'en'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'pyexampledoc'
html_baseurl = 'https://example.com/'
