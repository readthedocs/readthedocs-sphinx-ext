# -*- coding: utf-8 -*-

from collections import defaultdict
import json

from docutils import nodes
from sphinx.writers.html import HTMLTranslator

import hasher

# Between 128 and -128, the higher the number, the closer the strings are
LENGTH_LIMIT = 30
NILSIMSA_LIMIT = 70


def is_commentable(node):
    """
    Determine if a node is commentable.

    Node shortcuts::

        index = node.parent.index(node)
        parent = node.parent
        document = node.document
        text = node.astext()
        source = node.rawsource

    """
    if len(node.astext()) < LENGTH_LIMIT:
        return False
    if node.tagname in ['title']:
        return False
    if node.tagname in ['paragraph']:
        # More info
        # http://www.slideshare.net/doughellmann/better-documentation-through-automation-creating-docutils-sphinx-extensions Slide 75
        # https://www.youtube.com/watch?v=8vwtgMkqE9o
        if node.parent and node.parent.parent and node.parent.parent.parent:
            if node.parent.parent.parent.tagname == 'tbody':
                # Don't comment table contents
                return False
        return True

    return False


class UUIDTranslator(HTMLTranslator):

    """
    Our custom HTML translator.

    """

    def __init__(self, builder, *args, **kwargs):
        HTMLTranslator.__init__(self, builder, *args, **kwargs)
        self.comment_class = 'sphinx-has-comment'

    def dispatch_visit(self, node):
        if is_commentable(node):
            self.handle_visit_commentable(node)
        HTMLTranslator.dispatch_visit(self, node)

    def handle_visit_commentable(self, node):
        # We will place the node in the HTML id attribute. If the node
        # already has an id (for indexing purposes) put an empty
        # span with the existing id directly before this node's HTML.
        hash_digest = self.update_hash(node, builder=self.builder)
        if node.attributes['ids']:
            self.body.append('<span id="%s"></span>'
                             % node.attributes['ids'][0])
        node.attributes['ids'] = ['%s' % hash_digest]
        node.attributes['classes'].append(self.comment_class)

        # for obj in self.builder.comment_metadata:
        #     if obj['node']['current_hash'] == hash_digest:
        #         print "ADDING COMMEWNT"
        #         comment = "[COMMENT] %s: %s" % (obj['user'], obj['text'])
        #         node.insert(-1, nodes.paragraph(comment, comment))

    def update_hash(self, node, builder):
        """
        Take a node and compare it against existing hashes for this page.
        """
        hash_obj = hasher.hash_node(node, obj=True)
        hash_digest = hasher.hash_node(node)
        builder.page_hash_mapping[builder.current_docname].append(hash_digest)
        hash_list = [obj['current_hash'] for obj in builder.metadata_mapping[builder.current_docname]]
        if hash_digest not in hash_list:
            match = hasher.compare_hash(hash_obj, hash_list)
            if match:
                builder.storage.update_node(old_hash=match, new_hash=hasher.hash_node(node), commit='foobar')
                return hash_digest
            # else:
            #     resp = builder.storage.add_node(id=hasher.hash_node(node),
            #                                     document=builder.current_docname,
            #                                     source=node.rawsource or node.astext())

        return hash_digest
