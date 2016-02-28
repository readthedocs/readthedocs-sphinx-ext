import os
import shutil
import unittest
import io

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
            with io.open(test_file, encoding="utf-8") as fin:
                text = fin.read().strip()
                self.assertIn(test_string, text)
        finally:
            shutil.rmtree('_build')
            os.chdir('../..')


class IntegrationTests(LanguageIntegrationTests):

    def test_integration(self):
        self._run_test(
            'pyexample',
            '_build/readthedocs/index.html',
            'Hey there friend!',
            builder='readthedocs',
        )

    def test_media_integration(self):
        self._run_test(
            'pyexample',
            '_build/readthedocs/index.html',
            'media.readthedocs.org',
            builder='readthedocs',
        )

    def test_included_js(self):
        self._run_test(
            'pyexample',
            '_build/readthedocs/index.html',
            'readthedocs-dynamic-include.js',
            builder='readthedocs',
        )

