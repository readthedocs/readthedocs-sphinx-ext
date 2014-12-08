# -*- coding: utf-8 -*-
# from sphinx.builders.websupport

from backend import WebStorage


class CommentMixin(object):

    @classmethod
    def init(cls, self):
        # Pull project data from conf.py if it exists
        context = self.config.html_context
        if 'current_version' in context:
            self.version = context['current_version']
        if 'slug' in context:
            self.project = context['slug']

        self.storage = WebStorage(builder=self)

        # add our custom bits
        self.script_files.append('_static/jquery.pageslide.js')
        self.script_files.append('_static/websupport2-bundle.js')
        self.css_files.append('_static/websupport2.css')
        self.css_files.append('_static/sphinxweb.css')
        self.css_files.append('_static/jquery.pageslide.css')
