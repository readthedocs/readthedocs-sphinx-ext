import os

import sphinx
from sphinx.util.console import bold

if sphinx.version_info < (1, 5):
    # ``copy_static_entry`` was deprecated in Sphinx 1.5a1
    from sphinx.util import copy_static_entry
else:
    from sphinx.util.fileutil import copy_asset


class BuilderMixin(object):  # pylint: disable=old-style-class

    """Builder mixin class for copying and templating extra static files

    Adds additional script and stylesheet files to the output static files path.
    Template static files are provided a custom context and then copied to the
    new path.
    """

    static_override_files = []

    def get_static_override_context(self):
        return self.globalcontext.copy()

    def copy_static_override_files(self):
        self.app.info(bold('copying static override files... '), nonl=True)
        for filename in self.static_override_files:
            path_dest = os.path.join(self.outdir, '_static')
            path_src = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '_static',
                filename
            )
            ctx = self.get_static_override_context()
            if sphinx.version_info < (1, 5):
                copy_static_entry(
                    path_src,
                    path_dest,
                    self,
                    context=ctx,
                )
            else:
                copy_asset(
                    path_src,
                    path_dest,
                    context=ctx,
                    renderer=self.templates
                )
        self.app.info('done')

    def copy_static_files(self):
        """Copy override files after initial static pass

        This overrides the base builder ``copy_static_files`` method to inject
        custom static files.
        """
        super(BuilderMixin, self).copy_static_files()
        self.copy_static_override_files()
