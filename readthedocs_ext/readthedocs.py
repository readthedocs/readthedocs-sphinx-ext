# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os

from sphinx.builders.html import StandaloneHTMLBuilder, DirectoryHTMLBuilder, SingleFileHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.console import bold

from .comments.builder import (finalize_comment_media, ReadtheDocsBuilderComments,
                               ReadtheDocsDirectoryHTMLBuilderComments)
from .comments.directive import CommentConfigurationDirective
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

HAS_MONKEYPATCH = False


def finalize_media(app):
    """ Point media files at our media server. """

    if app.builder.name == 'readthedocssinglehtmllocalmedia' or app.builder.format != 'html':
        return  # Use local media for downloadable files
    # Pull project data from conf.py if it exists
    builder = app.builder
    context = builder.config.html_context
    MEDIA_URL = context.get('MEDIA_URL', 'https://media.readthedocs.org/')

    # Put in our media files instead of putting them in the docs.
    for index, file in enumerate(builder.script_files):
        if file in MEDIA_MAPPING.keys():
            builder.script_files[index] = MEDIA_MAPPING[file] % MEDIA_URL
            if file == "_static/jquery.js":
                builder.script_files.insert(
                    index + 1, "%sjavascript/jquery/jquery-migrate-1.2.1.min.js" % MEDIA_URL)


def update_body(app, pagename, templatename, context, doctree):
    """
    Add Read the Docs content to Sphinx body content.

    This is the most reliable way to inject our content into the page.
    """

    MEDIA_URL = context.get('MEDIA_URL', 'https://media.readthedocs.org/')
    if app.builder.name == 'readthedocssinglehtmllocalmedia':
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            theme_css = '_static/css/theme.css'
        else:
            theme_css = '_static/css/badge_only.css'
    elif app.builder.name == 'readthedocs':
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            theme_css = '%scss/sphinx_rtd_theme.css' % MEDIA_URL
        else:
            theme_css = '%scss/badge_only.css' % MEDIA_URL
    else:
        # Only insert on our HTML builds
        return

    template_context = context.copy()
    template_context['theme_css'] = theme_css
    template_context['rtd_js_url'] = '%sjavascript/readthedocs-doc-embed.js' % MEDIA_URL
    template_context['rtd_css_url'] = '%scss/readthedocs-doc-embed.css' % MEDIA_URL
    source = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '_templates',
        'readthedocs-insert.html.tmpl'
    )
    templ = open(source).read()
    rtd_content = app.builder.templates.render_string(templ, template_context)

    # This is monkey patched on the signal because we can't know what the user
    # has done with their `app.builder.templates` before now.

    global HAS_MONKEYPATCH

    if not HAS_MONKEYPATCH:
        # Janky monkey patch of template rendering to add our content
        old_render = app.builder.templates.render

        def rtd_render(template, context):
            """
            A decorator that renders the content with the users template renderer,
            then adds the Read the Docs HTML content at the end of body.
            """
            content = old_render(template, context)
            end_body = content.lower().find('</body>')
            if end_body != -1:
                # Insert our content at the end of the body.
                content = content[:end_body] + rtd_content + content[end_body:]
            else:
                app.debug("File doesn't look like HTML. Skipping RTD content addition")
            return content

        app.builder.templates.render = rtd_render
        HAS_MONKEYPATCH = True


def copy_media(app, exception):
    """ Move our dynamically generated files after build. """
    if app.builder.name == 'readthedocs' and not exception:
        for file in ['readthedocs-dynamic-include.js_t', 'readthedocs-data.js_t',
                     'searchtools.js_t']:
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
            if app.builder.indexer is not None:
                ctx.update(app.builder.indexer.context_for_searchtool())
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


class ReadtheDocsBuilder(StandaloneHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocs'


class ReadtheDocsDirectoryHTMLBuilder(DirectoryHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocsdirhtml'


class ReadtheDocsSingleFileHTMLBuilder(SingleFileHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocssinglehtml'


class ReadtheDocsSingleFileHTMLBuilderLocalMedia(SingleFileHTMLBuilder):

    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocssinglehtmllocalmedia'


def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.add_builder(ReadtheDocsDirectoryHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilderLocalMedia)
    app.connect('builder-inited', finalize_media)
    app.connect('builder-inited', finalize_comment_media)
    app.connect('html-page-context', update_body)
    app.connect('build-finished', copy_media)

    # Comments
    # app.connect('env-updated', add_comments_to_doctree)
    app.add_directive(
        'comment-configure', CommentConfigurationDirective)
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
