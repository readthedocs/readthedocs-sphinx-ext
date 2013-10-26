# -*- coding: utf-8 -*-
import os

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.console import bold

MEDIA_MAPPING = {
    "_static/jquery.js": "%sjavascript/jquery/jquery-2.0.3.min.js",
    "_static/underscore.js": "%sjavascript/underscore.js",
    "_static/doctools.js": "%sjavascript/doctools.js",
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
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocs'
    #versioning_method = 'commentable'
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
        for index, file in enumerate(self.script_files):
            if file in MEDIA_MAPPING.keys():
                self.script_files[index] = MEDIA_MAPPING[file] % context['MEDIA_URL']
                if file == "_static/jquery.js":
                    self.script_files.insert(index+1, "%sjavascript/jquery/jquery-migrate-1.2.1.min.js" % context['MEDIA_URL'])

        if context.has_key('html_theme') and context['html_theme'] == 'sphinx_rtd_theme':
            self.css_files.append('%scss/sphinx_rtd_theme.css' % context['MEDIA_URL'])
        else:
            self.css_files.append('%scss/badge_only.css' % context['MEDIA_URL'])

        # Analytics codes
        self.script_files.append('_static/readthedocs-ext.js')
        self.script_files.append('%sjavascript/analytics.js' % context['MEDIA_URL'])

        # We include the media servers version here so we can update rtd.js across all
        # documentation without rebuilding every one. 
        # If this script is embedded in each build, 
        # then updating the file across all docs is basically impossible.
        self.script_files.append('%sjavascript/readthedocs-doc-embed.js' % context['MEDIA_URL'])
        self.css_files.append('%scss/readthedocs-doc-embed.css' % context['MEDIA_URL'])

def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.connect('build-finished', copy_media)
