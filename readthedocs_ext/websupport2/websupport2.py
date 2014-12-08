# -*- coding: utf-8 -*-
# from sphinx.builders.websupport

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.console import bold
from translator import UUIDTranslator
from backend import WebStorage

import os

STATIC_FILES = [
    'websupport2.css', 
    'websupport2-bundle.js_t', 
    'sphinxweb.css',
    'jquery.pageslide.css',
    'jquery.pageslide.js',
]

def copy_media(app, exception):
    if app.builder.name != 'websupport2' or exception:
        return
    for file in STATIC_FILES:
        app.info(bold('Copying %s... ' % file), nonl=True)
        dest_dir = os.path.join(app.builder.outdir, '_static')
        source = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            '_static', 
            file
        )
        ctx = app.builder.globalcontext
        ctx['websupport2_base_url'] = app.builder.config.websupport2_base_url
        ctx['websupport2_static_url'] = app.builder.config.websupport2_static_url
        copy_static_entry(source, dest_dir, app.builder, ctx)
        app.info('done')


class Websupport2Builder(StandaloneHTMLBuilder):
    """
    Builds documents for the web support package.
    """
    name = 'websupport2'
    versioning_method = 'commentable'
    slug = None
    version = None

    def init(self):
        StandaloneHTMLBuilder.init(self)

        # Pull project data from conf.py if it exists
        context = self.config.html_context
        if context.has_key('current_version'):
            self.version = context['current_version']
        if context.has_key('slug'):
            self.project = context['slug']

        self.storage = WebStorage(builder=self)

        # add our custom bits
        self.script_files.append('_static/jquery.pageslide.js')
        self.script_files.append('_static/websupport2-bundle.js')
        self.css_files.append('_static/websupport2.css')
        self.css_files.append('_static/sphinxweb.css')
        self.css_files.append('_static/jquery.pageslide.css')

    def init_translator_class(self):
        self.translator_class = UUIDTranslator

def setup(app):
    app.add_builder(Websupport2Builder)
    app.connect('build-finished', copy_media)
    app.add_config_value('websupport2_base_url', 'http://localhost:8000/websupport', 'html')
    app.add_config_value('websupport2_static_url', 'http://localhost:8000/static', 'html')
