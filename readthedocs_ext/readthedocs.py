# -*- coding: utf-8 -*-

from __future__ import absolute_import

import codecs
import json
import os
import re
import types
from distutils.version import LooseVersion

import sphinx
from sphinx import package_dir
from sphinx.builders.html import (DirectoryHTMLBuilder, SingleFileHTMLBuilder,
                                  StandaloneHTMLBuilder)
from sphinx.util.console import bold


from .embed import EmbedDirective
from .mixins import BuilderMixin

try:
    # Avaliable from Sphinx 1.6
    from sphinx.util.logging import getLogger
except ImportError:
    from logging import getLogger

log = getLogger(__name__)

DEFAULT_STATIC_URL = 'https://assets.readthedocs.org/static/'
ONLINE_BUILDERS = [
    'readthedocs', 'readthedocsdirhtml', 'readthedocssinglehtml'
]
# Only run JSON output once during HTML build
# This saves resources and keeps filepaths correct,
# because singlehtml filepaths are different
JSON_BUILDERS = [
    'html', 'dirhtml',
    'readthedocs', 'readthedocsdirhtml'
]

# Whitelist keys that we want to output
# to the json artifacts.
JSON_KEYS = [
    'body',
    'title',
    'sourcename',
    'current_page_name',
    'toc',
    'page_source_suffix',
]


def finalize_media(app):
    """Point media files at our media server."""

    if (app.builder.name == 'readthedocssinglehtmllocalmedia' or
            app.builder.format != 'html' or
            not hasattr(app.builder, 'script_files')):
        return  # Use local media for downloadable files
    # Pull project data from conf.py if it exists
    context = app.builder.config.html_context
    STATIC_URL = context.get('STATIC_URL', DEFAULT_STATIC_URL)
    js_file = '{}javascript/readthedocs-doc-embed.js'.format(STATIC_URL)
    if sphinx.version_info < (1, 8):
        app.builder.script_files.append(js_file)
    else:
        app.add_js_file(js_file)


def update_body(app, pagename, templatename, context, doctree):
    """
    Add Read the Docs content to Sphinx body content.

    This is the most reliable way to inject our content into the page.
    """

    STATIC_URL = context.get('STATIC_URL', DEFAULT_STATIC_URL)
    if app.builder.name == 'readthedocssinglehtmllocalmedia':
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            theme_css = '_static/css/theme.css'
        else:
            theme_css = '_static/css/badge_only.css'
    elif app.builder.name in ONLINE_BUILDERS:
        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            theme_css = '%scss/sphinx_rtd_theme.css' % STATIC_URL
        else:
            theme_css = '%scss/badge_only.css' % STATIC_URL
    else:
        # Only insert on our HTML builds
        return

    inject_css = True

    # Starting at v0.4.0 of the sphinx theme, the theme CSS should not be injected
    # This decouples the theme CSS (which is versioned independently) from readthedocs.org
    if theme_css.endswith('sphinx_rtd_theme.css'):
        try:
            import sphinx_rtd_theme
            inject_css = LooseVersion(sphinx_rtd_theme.__version__) < LooseVersion('0.4.0')
        except ImportError:
            pass

    if inject_css and theme_css not in app.builder.css_files:
        if sphinx.version_info < (1, 8):
            app.builder.css_files.insert(0, theme_css)
        else:
            app.add_css_file(theme_css)

    # This is monkey patched on the signal because we can't know what the user
    # has done with their `app.builder.templates` before now.

    if (
        app.builder.name in ONLINE_BUILDERS and not
        hasattr(app.builder.templates.render, '_patched')
    ):
        # Janky monkey patch of template rendering to add our content
        old_render = app.builder.templates.render

        def rtd_render(self, template, render_context):
            """
            A decorator that renders the content with the users template renderer,
            then adds the Read the Docs HTML content at the end of body.
            """
            # Render Read the Docs content
            template_context = render_context.copy()
            template_context['rtd_css_url'] = '{}css/readthedocs-doc-embed.css'.format(STATIC_URL)
            template_context['rtd_analytics_url'] = '{}javascript/readthedocs-analytics.js'.format(
                STATIC_URL,
            )
            source = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '_templates',
                'readthedocs-insert.html.tmpl'
            )
            templ = open(source).read()
            rtd_content = app.builder.templates.render_string(templ, template_context)

            # Handle original render function
            content = old_render(template, render_context)
            end_body = content.lower().find('</head>')

            # Insert our content at the end of the body.
            if end_body != -1:
                content = content[:end_body] + rtd_content + "\n" + content[end_body:]
            else:
                log.debug("File doesn't look like HTML. Skipping RTD content addition")

            return content

        rtd_render._patched = True
        app.builder.templates.render = types.MethodType(rtd_render,
                                                        app.builder.templates)


def generate_json_artifacts(app, pagename, templatename, context, doctree):
    """
    Generate JSON artifacts for each page.

    This way we can skip generating this in other build step.
    """
    if app.builder.name not in JSON_BUILDERS:
        return
    try:
        # We need to get the output directory where the docs are built
        # _build/json.
        build_json = os.path.abspath(
            os.path.join(app.outdir, '..', 'json')
        )
        outjson = os.path.join(build_json, pagename + '.fjson')
        outdir = os.path.dirname(outjson)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        with open(outjson, 'w+') as json_file:
            to_context = {
                key: context.get(key, '')
                for key in JSON_KEYS
            }
            json.dump(to_context, json_file, indent=4)
    except TypeError:
        log.exception(
            'Fail to encode JSON for page {page}'.format(page=outjson)
        )
    except IOError:
        log.exception(
            'Fail to save JSON output for page {page}'.format(page=outjson)
        )
    except Exception:
        log.exception(
            'Failure in JSON search dump for page {page}'.format(page=outjson)
        )


def dump_sphinx_data(app, exception):
    """
    Dump data that is only in memory during Sphinx build.
    This is mostly used for search indexing.

    This includes:

    * `paths`: A mapping of HTML Filename -> RST file
    * `pages`: A mapping of HTML Filename -> Sphinx Page name
    * `titles`: A mapping of HTML Filename -> Page Title
    * `types`: A mapping of Sphinx Domain type slugs -> human-readable name for that type

    """
    if app.builder.name not in JSON_BUILDERS or exception:
        return
    try:
        types = {}
        titles = {}
        paths = {}
        pages = {}

        for domain_name, domain_obj in app.env.domains.items():
            for type_name, type_obj in domain_obj.object_types.items():
                key = "{}:{}".format(domain_name, type_name)
                types[key] = str(type_obj.lname)

        for page, title in app.env.titles.items():
            page_uri = app.builder.get_target_uri(page)
            titles[page_uri] = title.astext()
            paths[page_uri] = app.env.doc2path(page, base=None)
            pages[page_uri] = page

        to_dump = {
            'types': types,
            'titles': titles,
            'paths': paths,
            'pages': pages,
        }

        # We need to get the output directory where the docs are built
        # _build/json.
        build_json = os.path.abspath(
            os.path.join(app.outdir, '..', 'json')
        )
        outjson = os.path.join(build_json, 'readthedocs-sphinx-domain-names.json')
        with open(outjson, 'w+') as json_file:
            json.dump(to_dump, json_file, indent=4)
    except TypeError:
        log.exception(
            'Fail to encode JSON for object names'
        )
    except IOError:
        log.exception(
            'Fail to save JSON for object names'
        )
    except Exception:
        log.exception(
            'Failure in JSON search dump for object names'
        )


class HtmlBuilderMixin(BuilderMixin):

    static_readthedocs_files = [
        'readthedocs-data.js_t',
        # We patch searchtools and copy it with a special handler
        # 'searchtools.js_t'
    ]

    REPLACEMENT_TEXT = '/* Search initialization removed for Read the Docs */'
    REPLACEMENT_PATTERN = re.compile(
        r'''
        ^\$\(document\).ready\(function\s*\(\)\s*{(?:\n|\r\n?)
        \s*Search.init\(\);(?:\n|\r\n?)
        \}\);
        ''',
        (re.MULTILINE | re.VERBOSE)
    )

    def get_static_readthedocs_context(self):
        ctx = super(HtmlBuilderMixin, self).get_static_readthedocs_context()
        if self.indexer is not None:
            ctx.update(self.indexer.context_for_searchtool())
        return ctx

    def copy_static_readthedocs_files(self):
        super(HtmlBuilderMixin, self).copy_static_readthedocs_files()
        self._copy_searchtools()

    def _copy_searchtools(self, renderer=None):
        """Copy and patch searchtools

        This uses the included Sphinx version's searchtools, but patches it to
        remove automatic initialization. This is a fork of
        ``sphinx.util.fileutil.copy_asset``
        """
        log.info(bold('copying searchtools... '), nonl=True)

        if sphinx.version_info < (1, 8):
            search_js_file = 'searchtools.js_t'
        else:
            search_js_file = 'searchtools.js'
        path_src = os.path.join(
            package_dir, 'themes', 'basic', 'static', search_js_file
        )
        if os.path.exists(path_src):
            path_dest = os.path.join(self.outdir, '_static', 'searchtools.js')
            if renderer is None:
                # Sphinx 1.4 used the renderer from the existing builder, but
                # the pattern for Sphinx 1.5 is to pass in a renderer separate
                # from the builder. This supports both patterns for future
                # compatibility
                if sphinx.version_info < (1, 5):
                    renderer = self.templates
                else:
                    from sphinx.util.template import SphinxRenderer
                    renderer = SphinxRenderer()
            with codecs.open(path_src, 'r', encoding='utf-8') as h_src:
                with codecs.open(path_dest, 'w', encoding='utf-8') as h_dest:
                    data = h_src.read()
                    data = self.REPLACEMENT_PATTERN.sub(self.REPLACEMENT_TEXT, data)
                    h_dest.write(renderer.render_string(
                        data,
                        self.get_static_readthedocs_context()
                    ))
        else:
            log.warning('Missing {}'.format(search_js_file))
        log.info('done')


class ReadtheDocsBuilder(HtmlBuilderMixin, StandaloneHTMLBuilder):
    name = 'readthedocs'


class ReadtheDocsDirectoryHTMLBuilder(HtmlBuilderMixin, DirectoryHTMLBuilder):
    name = 'readthedocsdirhtml'


class ReadtheDocsSingleFileHTMLBuilder(BuilderMixin, SingleFileHTMLBuilder):
    name = 'readthedocssinglehtml'


class ReadtheDocsSingleFileHTMLBuilderLocalMedia(BuilderMixin, SingleFileHTMLBuilder):
    name = 'readthedocssinglehtmllocalmedia'


def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.add_builder(ReadtheDocsDirectoryHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilderLocalMedia)
    app.connect('builder-inited', finalize_media)
    app.connect('html-page-context', update_body)
    app.connect('html-page-context', generate_json_artifacts)
    app.connect('build-finished', dump_sphinx_data)

    # Embed
    app.add_directive('readthedocs-embed', EmbedDirective)
    app.add_config_value('readthedocs_embed_project', '', 'html')
    app.add_config_value('readthedocs_embed_version', '', 'html')
    app.add_config_value('readthedocs_embed_doc', '', 'html')
    app.add_config_value('rtd_generate_json_artifacts', False, 'html')

    return {}
