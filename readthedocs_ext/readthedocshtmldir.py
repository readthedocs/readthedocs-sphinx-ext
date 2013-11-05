# -*- coding: utf-8 -*-

from docutils.io import StringOutput
from sphinx.builders.html import DirectoryHTMLBuilder
from sphinx.util.osutil import relative_uri

from .base import MEDIA_MAPPING, copy_media, READ_THE_DOCS_BODY, USER_ANALYTICS_CODE

class ReadtheDocsBuilder(DirectoryHTMLBuilder):
    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocsdirhtml'
    #versioning_method = 'commentable'
    slug = None
    version = None

    def init(self):
        DirectoryHTMLBuilder.init(self)

        # Pull project data from conf.py if it exists
        context = self.config.html_context
        if 'current_version' in context:
            self.version = context['current_version']
        if 'slug' in context:
            self.project = context['slug']

        # Put in our media files instead of putting them in the docs.
        for index, file in enumerate(self.script_files):
            if file in MEDIA_MAPPING.keys():
                self.script_files[index] = MEDIA_MAPPING[file] % context['MEDIA_URL']
                if file == "_static/jquery.js":
                    self.script_files.insert(index+1, "%sjavascript/jquery/jquery-migrate-1.2.1.min.js" % context['MEDIA_URL'])

        if 'html_theme' in context and context['html_theme'] == 'sphinx_rtd_theme':
            self.css_files.append('%scss/sphinx_rtd_theme.css' % context['MEDIA_URL'])
        else:
            self.css_files.append('%scss/badge_only.css' % context['MEDIA_URL'])

        # Analytics codes
        #self.script_files.append('_static/readthedocs-ext.js')
        #self.script_files.append('%sjavascript/analytics.js' % context['MEDIA_URL'])

        # We include the media servers version here so we can update rtd.js across all
        # documentation without rebuilding every one. 
        # If this script is embedded in each build, 
        # then updating the file across all docs is basically impossible.
        #self.script_files.append('%sjavascript/readthedocs-doc-embed.js' % context['MEDIA_URL'])
        #self.css_files.append('%scss/readthedocs-doc-embed.css' % context['MEDIA_URL'])

    def write_doc(self, docname, doctree):
        """
        Overwrite the body with our own custom body bits.
        """
        destination = StringOutput(encoding='utf-8')
        doctree.settings = self.docsettings

        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        self.imgpath = relative_uri(self.get_target_uri(docname), '_images')
        self.dlpath = relative_uri(self.get_target_uri(docname), '_downloads')
        self.current_docname = docname
        self.docwriter.write(doctree, destination)
        self.docwriter.assemble_parts()
        body = self.docwriter.parts['fragment']
        # RTD Additions
        try:
            context = self.config.html_context
            # Really need a real templating language here
            html = READ_THE_DOCS_BODY % (context['MEDIA_URL'], context['MEDIA_URL'], context['slug'], context['current_version'], docname, context['html_theme'])
            code = context.get('analytics_code')
            if code:
                html += USER_ANALYTICS_CODE % code
            body += html
        except Exception:
            # Don't error on RTD code
            pass
            #raise
        # End RTD Additions
        metatags = self.docwriter.clean_meta

        ctx = self.get_doc_context(docname, body, metatags)
        self.handle_page(docname, ctx, event_arg=doctree)


def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.connect('build-finished', copy_media)
