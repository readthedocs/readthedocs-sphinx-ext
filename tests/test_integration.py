import os
import shutil
import unittest

from sphinx.application import Sphinx


class LanguageIntegrationTests(unittest.TestCase):

    def _run_test(self, test_dir, test_file, test_string, builder='html'):
        os.chdir('tests/{0}'.format(test_dir))
        try:
            app = Sphinx(
                srcdir='.',
                confdir='.',
                outdir='_build/%s' % builder,
                doctreedir='_build/.doctrees',
                buildername='%s' % builder,
            )
            app.build(force_all=True)
            with open(test_file) as fin:
                text = fin.read().strip()
                self.assertIn(test_string, text)
        finally:
            shutil.rmtree('_build')
            os.chdir('../..')


class IntegrationTests(LanguageIntegrationTests):

    def test_integration(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            'Hey there friend!',
        )

    def test_media_integration(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            'media.readthedocs.org',
        )
