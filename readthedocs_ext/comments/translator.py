# -*- coding: utf-8 -*-

# From sphinx.writers.websupport

import uuid
import nilsimsa

from sphinx.writers.html import HTMLTranslator

# Between 128 and -128, the higher the number, the closer the strings are
NILSIMSA_LIMIT = 70


def is_commentable(node):
    if node.tagname in ['title']:
        return True
    if node.tagname in ['paragraph']:
        # More info
        # http://www.slideshare.net/doughellmann/better-documentation-through-automation-creating-docutils-sphinx-extensions Slide 75
        # https://www.youtube.com/watch?v=8vwtgMkqE9o
        if node.parent and node.parent.parent:
            if node.parent.parent.tagname == 'row':
                pass
                #import ipdb; ipdb.set_trace()
        if node.parent and node.parent.parent and node.parent.parent.parent:
            if node.parent.parent.parent.tagname == 'tbody':
                return False
        return True

    return False


class UUIDTranslator(HTMLTranslator):

    """
    Our custom HTML translator.

    index = node.parent.index(node)
    parent = node.parent
    document = node.document
    text = node.astext()
    source = node.rawsource
    """

    def __init__(self, builder, *args, **kwargs):
        HTMLTranslator.__init__(self, builder, *args, **kwargs)
        self.comment_class = 'sphinx-has-comment'

    def dispatch_visit(self, node):
        if is_commentable(node):
            self.handle_visit_commentable(node)
        HTMLTranslator.dispatch_visit(self, node)

    def hash_node(self, node, obj=False):
        source = node.rawsource or node.astext()
        index = node.parent.index(node)

        if obj:
            return nilsimsa.Nilsimsa(source)

        try:
            ret = u'nil-{index}-{hash}'.format(index=index, hash=nilsimsa.Nilsimsa(source).hexdigest())
        except UnicodeEncodeError:
            ret = u'uuid-%s' % str(uuid.uuid1())
        return ret

    def handle_visit_commentable(self, node):
        # We will place the node in the HTML id attribute. If the node
        # already has an id (for indexing purposes) put an empty
        # span with the existing id directly before this node's HTML.
        self.add_db_node(node)
        if node.attributes['ids']:
            self.body.append('<span id="%s"></span>'
                             % node.attributes['ids'][0])
        node.attributes['ids'] = ['%s' % self.hash_node(node)]
        node.attributes['classes'].append(self.comment_class)

    def add_db_node(self, node):
        storage = self.builder.storage
        _hash = self.hash_node(node)
        has_node = storage.has_node(_hash)
        nodes = storage.get_metadata(self.builder.current_docname)
        CLOSE_FOUND = False
        if not has_node:
            for node_hash in nodes.keys():
                if not node_hash.startswith('nil'):
                    continue
                nim_hash = node_hash.split('-')[-1]
                difference = self.hash_node(node, obj=True).compare(nim_hash, True)
                print "Nope: %s %s %s" % (nim_hash, difference, node.rawsource)
                if difference > NILSIMSA_LIMIT:
                    # Node is the same
                    CLOSE_FOUND = True
                    nodes = storage.update_node(old_hash=node_hash, new_hash=_hash, commit='foobar')
                    print "CLOSE: %s %s %s" % (nim_hash, difference, node.rawsource)
                    break
            if not CLOSE_FOUND:
                storage.add_node(id=_hash,
                                 document=self.builder.current_docname,
                                 source=node.rawsource or node.astext())
