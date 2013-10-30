# -*- coding: utf-8 -*-

# From sphinx.writers.websupport

from sphinx.writers.html import HTMLTranslator
from sphinx.util.websupport import is_commentable


class RTDTranslator(HTMLTranslator):
    """
    Our custom HTML translator.
    """

    def visit_table(self, node):
        self.body.append('<div class="wy-repsonsive-table">')
        self._table_row_index = 0
        return BaseTranslator.visit_table(self, node)

    def depart_table(self, node):
        self.body.append('</div>')
        return BaseTranslator.depart_table(self, node)
