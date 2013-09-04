# -*- coding: utf-8 -*-

# From sphinx.writers.websupport

from sphinx.writers.html import HTMLTranslator
from sphinx.util.websupport import is_commentable


class UUIDTranslator(HTMLTranslator):
    """
    Our custom HTML translator.
    """

    def dispatch_visit(self, node):
        if is_commentable(node):
            self.handle_visit_commentable(node)
        HTMLTranslator.dispatch_visit(self, node)

    def handle_visit_commentable(self, node):
        # We will place the node in the HTML id attribute. If the node
        # already has an id (for indexing purposes) put an empty
        # span with the existing id directly before this node's HTML.
        if node.attributes['ids']:
            self.body.append('<span id="%s"></span>'
                             % node.attributes['ids'][0])
        node.attributes['ids'] = ['s%s' % node.uid]
