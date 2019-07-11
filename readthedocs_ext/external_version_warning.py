from docutils import nodes

try:
    # Avaliable from Sphinx 1.6
    from sphinx.util.logging import getLogger
except ImportError:
    from logging import getLogger

log = getLogger(__name__)


def process_external_version_warning_banner(app, doctree, fromdocname):
    """
    Add warning banner for external versions in every page.

    If the version type is external this will show a warning banner
    at the top of each page of the documentation.
    """
    for document in doctree.traverse(nodes.document):
        text = 'This Documentation was created from pull/merge request.'
        prose = nodes.paragraph(text, text)
        warning = nodes.warning(prose, prose)
        document.insert(0, warning)


def setup(app):
    app.connect('doctree-resolved', process_external_version_warning_banner)
