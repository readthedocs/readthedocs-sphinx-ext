# -*- coding: utf-8 -*-
import os

from django.template import Template, Context
from docutils.io import StringOutput
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import copy_static_entry
from sphinx.util.osutil import relative_uri
from sphinx.util.console import bold

#from .translation import RTDTranslator

MEDIA_MAPPING = {
    "_static/jquery.js": "%sjavascript/jquery/jquery-2.0.3.min.js",
    "_static/underscore.js": "%sjavascript/underscore.js",
    "_static/doctools.js": "%sjavascript/doctools.js",
}

def copy_media(app, exception):
    if app.builder.name != 'readthedocs' or exception:
        return
    for file in ['readthedocs-ext.js_t']:
        app.info(bold('Copying %s... ' % file), nonl=True)
        dest_dir = os.path.join(app.builder.outdir, '_static')
        source = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            '_static', 
            file
        )
        ctx = app.builder.globalcontext
        copy_static_entry(source, dest_dir, app.builder, ctx)
        app.info('done')


READ_THE_DOCS_BODY = """
    <!-- RTD Injected Body -->

    <script type="text/javascript" src="https://media.readthedocs.org/javascript/readthedocs-doc-embed.js"></script>

    <script type="text/javascript">
      // This is included here because other places don't have access to the pagename variable.
      var READTHEDOCS_DATA = {
        project: "{{ slug }}",
        version: "{{ current_version }}",
        page: "{{ pagename }}",
        theme: "{{ html_theme }}"
      }
      // Old variables
      var doc_version = "{{ current_version }}";
      var doc_slug = "{{ slug }}";
      var page_name = "{{ pagename }}";
      var html_theme = "{{ html_theme }}";
    </script>    

    <!-- RTD Analytics Code -->
    <!-- Included in the header because you don't have a footer block. -->
    <script type="text/javascript">
      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-17997319-1']);
      _gaq.push(['_trackPageview']);

      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();
    </script>
    <!-- End RTD Analytics Code -->
    <!-- End RTD Injected Body -->
"""

class ReadtheDocsBuilder(StandaloneHTMLBuilder):
    """
    Adds specific media files to script_files and css_files.
    """
    name = 'readthedocs'
    #versioning_method = 'commentable'
    slug = None
    version = None

    # Comment this out for now, but have it in case we need to edit element behavior
    #def init_translator_class(self):
        #self.translator_class = RTDTranslator

    def init(self):
        StandaloneHTMLBuilder.init(self)

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
        self.script_files.append('%sjavascript/readthedocs-doc-embed.js' % context['MEDIA_URL'])
        self.css_files.append('%scss/readthedocs-doc-embed.css' % context['MEDIA_URL'])

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
            html = Template(READ_THE_DOCS_BODY).render(context)
            body += html
        except Exception:
            # Don't error on RTD code
            pass 
        # End RTD Additions
        metatags = self.docwriter.clean_meta

        ctx = self.get_doc_context(docname, body, metatags)
        self.handle_page(docname, ctx, event_arg=doctree)

def setup(app):
    app.add_builder(ReadtheDocsBuilder)
    app.connect('build-finished', copy_media)
