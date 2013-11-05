# -*- coding: utf-8 -*-
import os

from sphinx.util import copy_static_entry
from sphinx.util.console import bold

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

USER_ANALYTICS_CODE = """
<!-- User Analytics Code -->
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '%s']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
<!-- End User Analytics Code -->
"""

READ_THE_DOCS_BODY = """
    <!-- RTD Injected Body -->

    <link rel="stylesheet" href="%scss/readthedocs-doc-embed.css" type="text/css" />
    <script type="text/javascript" src="%sjavascript/readthedocs-doc-embed.js"></script>

    <script type="text/javascript">
      // This is included here because other places don't have access to the pagename variable.
      var READTHEDOCS_DATA = {
        project: "%s",
        version: "%s",
        page: "%s",
        theme: "%s",
        docroot: "%s"
      }
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
"""

