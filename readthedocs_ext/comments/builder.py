from __future__ import absolute_import

from collections import defaultdict

from sphinx.builders.html import StandaloneHTMLBuilder, DirectoryHTMLBuilder

from . import backend, translator
from ..mixins import BuilderMixin


def finalize_comment_media(app):

    if 'comments' not in app.builder.name:
        return
    builder = app.builder
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


class CommentsBuilderMixin(BuilderMixin):

    static_readthedocs_files = [
        'sphinxweb.css',
        'jquery.pageslide.css',
        'jquery.pageslide.js',
    ]

    def get_static_readthedocs_context(self):
        ctx = super(CommentsBuilderMixin, self).get_static_readthedocs_context()
        ctx['websupport2_base_url'] = self.config.websupport2_base_url
        ctx['websupport2_static_url'] = self.config.websupport2_static_url
        return ctx


class ReadtheDocsBuilderComments(CommentsBuilderMixin, StandaloneHTMLBuilder):

    """
    Comment Builders.

    Sets the translator class,
    which handles adding a content-specific hash to each text node object.
    """
    name = 'readthedocs-comments'
    versioning_method = 'commentable'

    def init(self):
        StandaloneHTMLBuilder.init(self)

    def init_translator_class(self):
        self.translator_class = translator.UUIDTranslator


class ReadtheDocsDirectoryHTMLBuilderComments(CommentsBuilderMixin, DirectoryHTMLBuilder):

    """ Adds specific media files to script_files and css_files. """
    name = 'readthedocsdirhtml-comments'
    versioning_method = 'commentable'

    def init(self):
        DirectoryHTMLBuilder.init(self)
        finalize_comment_media(self)

    def init_translator_class(self):
        self.translator_class = translator.UUIDTranslator
