from __future__ import print_function

from collections import defaultdict
from docutils.parsers.rst import Directive


class CommentConfigurationDirective(Directive):

    """
    Allow configuration of comments

    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        docname = env.docname
        if not hasattr(env, 'comment_config_map'):
            env.comment_config_map = defaultdict(set)
        for option in self.arguments:
            print('OPTION %s' % option)
            if option in ['none', 'header', 'paragraph', 'code']:
                env.comment_config_map[docname].add(option)
            else:
                return [self.state.document.reporter.warning(
                    'Invalid option for Comment Configuration: %s' % option, line=self.lineno
                )]
        return []
