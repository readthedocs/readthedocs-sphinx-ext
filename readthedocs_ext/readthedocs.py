# -*- coding: utf-8 -*-
import os

from sphinx.builders.html import StandaloneHTMLBuilder, DirectoryHTMLBuilder, SingleFileHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.console import bold

from .embed import EmbedDirective


MEDIA_MAPPING = {
    "_static/jquery.js": "%sjavascript/jquery/jquery-2.0.3.min.js",
    "_static/underscore.js": "%sjavascript/underscore.js",
    "_static/doctools.js": "%sjavascript/doctools.js",
}


def copy_media(app, exception):
    if app.builder.name != 'readthedocs' or exception:
        return
    for file in ['readthedocs-dynamic-include.js_t', 'readthedocs-data.js_t']:
        app.info(bold('Copying %s... ' % file), nonl=True)
        dest_dir = os.path.join(app.builder.outdir, '_static')
        source = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '_static',
            file
        )
        try:
            ctx = app.builder.globalcontext
        except AttributeError:
            ctx = {}
        copy_static_entry(source, dest_dir, app.builder, ctx)
        app.info('done')


def finalize_media(builder, local=False):
    # Pull project data from conf.py if it exists
    context = builder.config.html_context

    # Put in our media files instead of putting them in the docs.
    for index, file in enumerate(builder.script_files):
        if file in MEDIA_MAPPING.keys():
            builder.script_files[index] = MEDIA_MAPPING[file] % context['MEDIA_URL']
            if file == "_static/jquery.js":
                builder.script_files.insert(index + 1, "%sjavascript/jquery/jquery-migrate-1.2.1.min.js" % context['MEDIA_URL'])

    if local:
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            builder.css_files.append('_static/css/theme.css')
        else:
            builder.css_files.append('_static/css/badge_only.css')
    else:
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            builder.css_files.append('%scss/sphinx_rtd_theme.css' % context['MEDIA_URL'])
        else:
            builder.css_files.append('%scss/badge_only.css' % context['MEDIA_URL'])

    # Analytics codes
    # builder.script_files.append('_static/readthedocs-data.js')
    # builder.script_files.append('_static/readthedocs-dynamic-include.js')
    # We include the media servers version here so we can update rtd.js across all
    # documentation without rebuilding every one.
    # If this script is embedded in each build,
    # then updating the file across all docs is basically impossible.
    builder.script_files.append('%sjavascript/readthedocs-doc-embed.js' % context['MEDIA_URL'])
    builder.css_files.append('%scss/readthedocs-doc-embed.css' % context['MEDIA_URL'])


class ReadtheDocsBuilder(StandaloneHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocs'

    def init(self):
        StandaloneHTMLBuilder.init(self)
        finalize_media(self)


class ReadtheDocsDirectoryHTMLBuilder(DirectoryHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocsdirhtml'

    def init(self):
        DirectoryHTMLBuilder.init(self)
        finalize_media(self)


class ReadtheDocsSingleFileHTMLBuilder(SingleFileHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocssinglehtml'

    def init(self):
        SingleFileHTMLBuilder.init(self)
        finalize_media(self)


class ReadtheDocsSingleFileHTMLBuilderLocalMedia(SingleFileHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocssinglehtmllocalmedia'

    def init(self):
        SingleFileHTMLBuilder.init(self)
        finalize_media(self, local=True)


def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.add_builder(ReadtheDocsDirectoryHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilderLocalMedia)
    app.connect('build-finished', copy_media)
    # Embed
    app.add_directive('readthedocs-embed', EmbedDirective)
    app.add_config_value('readthedocs_embed_project', '', 'html')
    app.add_config_value('readthedocs_embed_version', '', 'html')
    app.add_config_value('readthedocs_embed_doc', '', 'html')

    return app
