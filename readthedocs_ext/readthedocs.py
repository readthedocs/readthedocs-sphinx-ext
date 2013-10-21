# -*- coding: utf-8 -*-
import os

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.console import bold

from .translator import UUIDTranslator

MEDIA_MAPPING = {
    "_static/jquery.js": "{{ MEDIA_URL }}javascript/jquery.js",
    "_static/underscore.js": "{{ MEDIA_URL }}javascript/underscore.js",
    "_static/doctools.js": "{{ MEDIA_URL }}javascript/doctools.js",
}

def copy_media(app, exception):
    if app.builder.name != 'readthedocs' or exception:
        return
    for file in ['readthedocs-ext.js_t']:
        app.info(bold('Copying %s... ' % file), nonl=True)
        dest_dir = os.path.join(app.builder.outdir, '_static')
        source = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            '_static', 
            file
        )
        ctx = app.builder.globalcontext
        copy_static_entry(source, dest_dir, app.builder, ctx)
        app.info('done')


class ReadtheDocsBuilder(StandaloneHTMLBuilder):
    """
    Builds documents for the web support package.
    """
    name = 'readthedocs'
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

        # Put in our media files instead of putting them in the docs.
        for index, file in enum(self.script_files):
            if file in MEDIA_MAPPING.keys():
                self.script_files[index] = MEDIA_MAPPING[file]
        # add our custom bits
        self.script_files.append('{{ MEDIA_URL }}javascript/readthedocs-ext.js')
        #self.script_files.append('_static/readthedocs-ext.js')

    def init_translator_class(self):
        self.translator_class = UUIDTranslator

def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.connect('build-finished', copy_media)
