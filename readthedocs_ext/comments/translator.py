# -*- coding: utf-8 -*-

# From sphinx.writers.websupport

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
        return True
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
        self.update_hash(node, builder=self.builder)
        if node.attributes['ids']:
            self.body.append('<span id="%s"></span>'
                             % node.attributes['ids'][0])
        node.attributes['ids'] = ['%s' % hasher.hash_node(node)]
        node.attributes['classes'].append(self.comment_class)

    def update_hash(self, node, builder):
        """
        Take a node and compare it against existing hashes for this page.
        """
        hash_obj = hasher.hash_node(node, obj=True)
        hash_digest = hasher.hash_node(node)
        nodes = builder.storage.get_metadata(builder.current_docname)
        hash_list = nodes.keys()
        if hash_digest not in hash_list:
            match = hasher.compare_hash(hash_obj, hash_list)
            if match:
                resp = builder.storage.update_node(old_hash=match, new_hash=hasher.hash_node(node), commit='foobar')
            # else:
            #     resp = builder.storage.add_node(id=hasher.hash_node(node),
            #                                     document=builder.current_docname,
            #                                     source=node.rawsource or node.astext())

            return resp
        return None
