# -*- coding: utf-8 -*-
import os
from collections import defaultdict

from sphinx.builders.html import StandaloneHTMLBuilder, DirectoryHTMLBuilder, SingleFileHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.console import bold

from .comments import backend, translator, directive
from .embed import EmbedDirective

MEDIA_MAPPING = {
    "_static/jquery.js": "%sjavascript/jquery/jquery-2.0.3.min.js",
    "_static/underscore.js": "%sjavascript/underscore.js",
    "_static/doctools.js": "%sjavascript/doctools.js",
}

STATIC_FILES = [
    'sphinxweb.css',
    'jquery.pageslide.css',
    'jquery.pageslide.js',
]


def copy_media(app, exception):
    if app.builder.name == 'readthedocs' and not exception:
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

    if 'comments' in app.builder.name and not exception:
        for file in STATIC_FILES:
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
            ctx['websupport2_base_url'] = app.builder.config.websupport2_base_url
            ctx['websupport2_static_url'] = app.builder.config.websupport2_static_url
            copy_static_entry(source, dest_dir, app.builder, ctx)
            app.info('done')


def finalize_media(builder, local=False):
    # Pull project data from conf.py if it exists
    context = builder.config.html_context
    MEDIA_URL = context.get('MEDIA_URL', 'https://media.readthedocs.org/')

    # Put in our media files instead of putting them in the docs.
    for index, file in enumerate(builder.script_files):
        if file in MEDIA_MAPPING.keys():
            builder.script_files[index] = MEDIA_MAPPING[file] % MEDIA_URL
            if file == "_static/jquery.js":
                builder.script_files.insert(
                    index + 1, "%sjavascript/jquery/jquery-migrate-1.2.1.min.js" % MEDIA_URL)

    if local:
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            builder.css_files.insert(0, '_static/css/theme.css')
        else:
            builder.css_files.insert(0, '_static/css/badge_only.css')
    else:
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            builder.css_files.insert(
                0, '%scss/sphinx_rtd_theme.css' % MEDIA_URL)
        else:
            builder.css_files.insert(0, '%scss/badge_only.css' % MEDIA_URL)

    # Analytics codes
    # builder.script_files.append('_static/readthedocs-data.js')
    # builder.script_files.append('_static/readthedocs-dynamic-include.js')
    # We include the media servers version here so we can update rtd.js across all
    # documentation without rebuilding every one.
    # If this script is embedded in each build,
    # then updating the file across all docs is basically impossible.
    builder.script_files.append(
        '%sjavascript/readthedocs-doc-embed.js' % MEDIA_URL)
    builder.css_files.append('%scss/readthedocs-doc-embed.css' % MEDIA_URL)


def finalize_comment_media(builder):
    # Pull project data from conf.py if it exists
    builder.storage = backend.WebStorage(builder=builder)
    builder.page_hash_mapping = defaultdict(list)
    builder.metadata_mapping = defaultdict(list)
    try:
        builder.comment_metadata = builder.storage.get_project_metadata(
            builder.config.html_context['slug'])['results']
        for obj in builder.comment_metadata:
            builder.metadata_mapping[obj['node']['page']].append(obj['node'])
    except:
        builder.comment_metadata = {}

    context = builder.config.html_context
    MEDIA_URL = context.get('MEDIA_URL', 'https://media.readthedocs.org/')

    # add our custom bits
    builder.script_files.append('_static/jquery.pageslide.js')
    # builder.script_files.append('_static/websupport2-bundle.js')
    builder.script_files.append(
        '%sjavascript/websupport2-bundle.js' % MEDIA_URL)
    builder.css_files.append('_static/websupport2.css')
    builder.css_files.append('_static/sphinxweb.css')
    builder.css_files.append('_static/jquery.pageslide.css')


class ReadtheDocsBuilder(StandaloneHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocs'

    def init(self):
        StandaloneHTMLBuilder.init(self)
        finalize_media(self)


class ReadtheDocsBuilderComments(StandaloneHTMLBuilder):

    """
    Comment Builders.

    Sets the translator class, which handles adding a content-specific hash to each text node object.
    """
    name = 'readthedocs-comments'
    versioning_method = 'commentable'

    def init(self):
        StandaloneHTMLBuilder.init(self)
        finalize_media(self)
        finalize_comment_media(self)

    def init_translator_class(self):
        self.translator_class = translator.UUIDTranslator


class ReadtheDocsDirectoryHTMLBuilder(DirectoryHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocsdirhtml'

    def init(self):
        DirectoryHTMLBuilder.init(self)
        finalize_media(self)


class ReadtheDocsDirectoryHTMLBuilderComments(DirectoryHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocsdirhtml-comments'
    versioning_method = 'commentable'

    def init(self):
        DirectoryHTMLBuilder.init(self)
        finalize_media(self)
        finalize_comment_media(self)

    def init_translator_class(self):
        self.translator_class = translator.UUIDTranslator


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

    # Comments
    # app.connect('env-updated', add_comments_to_doctree)
    app.add_directive(
        'comment-configure', directive.CommentConfigurationDirective)
    app.add_builder(ReadtheDocsBuilderComments)
    app.add_builder(ReadtheDocsDirectoryHTMLBuilderComments)
    app.add_config_value(
        'websupport2_base_url', 'http://localhost:8000/websupport', 'html')
    app.add_config_value(
        'websupport2_static_url', 'http://localhost:8000/static', 'html')

    # Embed
    app.add_directive('readthedocs-embed', EmbedDirective)
    app.add_config_value('readthedocs_embed_project', '', 'html')
    app.add_config_value('readthedocs_embed_version', '', 'html')
    app.add_config_value('readthedocs_embed_doc', '', 'html')

    return {}
