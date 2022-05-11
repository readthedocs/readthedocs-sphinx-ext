# -*- coding: utf-8 -*-

from __future__ import absolute_import

import codecs
import json
import os
import re
import types
from datetime import datetime
from distutils.version import LooseVersion

import sphinx
from sphinx import package_dir
from sphinx.util.console import bold


from .embed import EmbedDirective

try:
    # Available from Sphinx 1.6
    from sphinx.util.logging import getLogger
except ImportError:
    from logging import getLogger

try:
    # Available from Sphinx 2.0
    from sphinx.builders.dirhtml import DirectoryHTMLBuilder
    from sphinx.builders.html import StandaloneHTMLBuilder
    from sphinx.builders.singlehtml import SingleFileHTMLBuilder
except ImportError:
    from sphinx.builders.html import (
        DirectoryHTMLBuilder,
        SingleFileHTMLBuilder,
        StandaloneHTMLBuilder,
    )

log = getLogger(__name__)


DEFAULT_STATIC_URL = 'https://assets.readthedocs.org/static/'

# Exclude the SingleHTML builder that is used by RTD to zip up local media
# That builder is never used "online"
ONLINE_BUILDERS = [
    'html',
    'dirhtml',
    'singlehtml',
    # Deprecated builders
    'readthedocs',
    'readthedocsdirhtml',
    'readthedocssinglehtml',
]
# Only run JSON output once during HTML build
# This saves resources and keeps filepaths correct,
# because singlehtml filepaths are different
JSON_BUILDERS = [
    'html',
    'dirhtml',
    'readthedocs',
    'readthedocsdirhtml',
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


def update_body(app, pagename, templatename, context, doctree):
    """
    Add Read the Docs content to Sphinx body content.

    This is the most reliable way to inject our content into the page.
    """
    STATIC_URL = context.get('proxied_static_path', context.get('STATIC_URL', DEFAULT_STATIC_URL))
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
            import sphinx_rtd_theme  # noqa
            inject_css = LooseVersion(sphinx_rtd_theme.__version__) < LooseVersion('0.4.0')
        except ImportError:
            pass

    if inject_css and theme_css not in app.builder.css_files:
        if sphinx.version_info < (1, 8):
            app.builder.css_files.insert(0, theme_css)
        else:
            app.add_css_file(theme_css)

    # Add the Read the Docs embed
    # This *must* come after Sphinx has loaded jQuery as it relies on it.
    # Unless this script is modified to not rely on jQuery (a good goal),
    # it can't just be put into the extrahead
    # in case a theme outputs scripts at the end of the body
    js_file = '{}javascript/readthedocs-doc-embed.js'.format(STATIC_URL)
    if all((
        app.builder.name in ONLINE_BUILDERS,
        hasattr(app.builder, 'script_files'),
        js_file not in app.builder.script_files,
    )):
        if sphinx.version_info < (1, 8):
            app.builder.script_files.append(js_file)
        else:
            kwargs = {'async': 'async'}     # Workaround reserved word in Py3.7
            app.add_js_file(js_file, **kwargs)

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
            ctx = render_context.copy()
            ctx['rtd_data'] = {
                'project': ctx.get('slug', ''),
                'version': ctx.get('version_slug', ''),
                'language': ctx.get('rtd_language', ''),
                'programming_language': ctx.get('programming_language', ''),
                'canonical_url': ctx.get('canonical_url', ''),
                'theme': ctx.get('html_theme', ''),
                'builder': 'sphinx',
                'docroot': ctx.get('conf_py_path', ''),
                'source_suffix': ctx.get('source_suffix', ''),
                'page': ctx.get('pagename', ''),
                'api_host': ctx.get('api_host', ''),
                'commit': ctx.get('commit', ''),
                'ad_free': ctx.get('ad_free', ''),
                'build_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'global_analytics_code': ctx.get('global_analytics_code'),
                'user_analytics_code': ctx.get('user_analytics_code'),
                'subprojects': dict(ctx.get('subprojects', [])),
                'features': {
                    'docsearch_disabled': ctx.get('docsearch_disabled', False),
                },
            }
            if ctx.get('page_source_suffix'):
                ctx['rtd_data']['source_suffix'] = ctx['page_source_suffix']
            if ctx.get('proxied_api_host'):
                ctx['rtd_data']['proxied_api_host'] = ctx['proxied_api_host']
            ctx['rtd_css_url'] = '{}css/readthedocs-doc-embed.css'.format(STATIC_URL)
            ctx['rtd_analytics_url'] = '{}javascript/readthedocs-analytics.js'.format(STATIC_URL)
            source = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '_templates',
                'readthedocs-insert.html.tmpl'
            )
            templ = open(source).read()
            rtd_content = app.builder.templates.render_string(templ, ctx)

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


def remove_search_init(app, exception):
    """
    Remove Sphinx's Search.init() so it can be initialized by Read the Docs.

    RTD needs to call ``Search.init()`` after overriding some of its methods.
    We remove the ``Search.init()`` call from Sphinx to avoid calling it twice.

    - https://github.com/sphinx-doc/sphinx/blob/799385f5558a888d1a143bf703d06b66d6717fe4/sphinx/themes/basic/static/searchtools.js#L527-L529  # noqa
    - https://github.com/sphinx-doc/sphinx/blob/3b01fbe2adf3077cad5c2cf345c6d000d429d7ac/sphinx/themes/basic/static/searchtools.js#L507  # noqa
    """
    if exception:
        return

    searchtools_file = os.path.abspath(
        os.path.join(app.outdir, '_static', 'searchtools.js')
    )

    if os.path.exists(searchtools_file):
        replacement_text = '/* Search initialization removed for Read the Docs */'
        replacement_regex = re.compile(
            r'''
            ^(\$\(document\).ready\(function\s*\(\)\s*{(?:\n|\r\n?)
            \s*Search.init\(\);(?:\n|\r\n?)
            \}\);)
            |
            # Sphinx >=5.0 calls Search.init this way.
            (_ready\(Search.init\);)
            ''',
            (re.MULTILINE | re.VERBOSE)
        )

        log.info(bold('Updating searchtools for Read the Docs search... '), nonl=True)
        with codecs.open(searchtools_file, 'r', encoding='utf-8') as infile:
            data = infile.read()
        with codecs.open(searchtools_file, 'w', encoding='utf-8') as outfile:
            data = replacement_regex.sub(replacement_text, data)
            outfile.write(data)
    else:
        log.warning('Missing searchtools: {}'.format(searchtools_file))


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


class ReadtheDocsBuilder(StandaloneHTMLBuilder):

    """
    Sphinx builder that builds HTML docs.

    Note: This builder is DEPRECATED.
          In the future Read the Docs will use Sphinx's "html" instead.
    """

    name = 'readthedocs'


class ReadtheDocsDirectoryHTMLBuilder(DirectoryHTMLBuilder):

    """
    Sphinx builder that builds docs with clean URLs where each page gets its own directory.

    Note: This builder is DEPRECATED.
          In the future Read the Docs will use Sphinx's "dirhtml" instead.
    """

    name = 'readthedocsdirhtml'


class ReadtheDocsSingleFileHTMLBuilder(SingleFileHTMLBuilder):

    """
    Sphinx builder that builds a single HTML file to be served by Read the Docs.

    This is for users who choose singlehtml as their main output format.
    The downloadable .zip file is the builder below.

    Note: This builder is DEPRECATED.
          In the future Read the Docs will use Sphinx's "singlehtml" instead.
    """

    name = 'readthedocssinglehtml'


class ReadtheDocsSingleFileHTMLBuilderLocalMedia(SingleFileHTMLBuilder):

    """
    Sphinx builder that builds a single HTML file that will be zipped by Read the Docs.

    Read the Docs specific extras are typically not added to this builder
    since it is intended for offline use.
    """

    name = 'readthedocssinglehtmllocalmedia'


def setup(app):
    app.add_builder(ReadtheDocsSingleFileHTMLBuilderLocalMedia)
    app.connect('html-page-context', update_body)
    app.connect('html-page-context', generate_json_artifacts)
    app.connect('build-finished', remove_search_init)
    app.connect('build-finished', dump_sphinx_data)

    # Embed
    app.add_directive('readthedocs-embed', EmbedDirective)
    app.add_config_value('readthedocs_embed_project', '', 'html')
    app.add_config_value('readthedocs_embed_version', '', 'html')
    app.add_config_value('readthedocs_embed_doc', '', 'html')
    app.add_config_value('rtd_generate_json_artifacts', False, 'html')

    # Deprecated builders
    app.add_builder(ReadtheDocsBuilder)
    app.add_builder(ReadtheDocsDirectoryHTMLBuilder)
    app.add_builder(ReadtheDocsSingleFileHTMLBuilder)

    return {
        'parallel_read_safe': True,
    }
