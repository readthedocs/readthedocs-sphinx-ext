import os
import shutil
import unittest

from sphinx.application import Sphinx


class LanguageIntegrationTests(unittest.TestCase):

    def _run_test(self, test_dir, test_file, test_string):
        os.chdir('tests/{0}'.format(test_dir))
        try:
            app = Sphinx(
                srcdir='.',
                confdir='.',
                outdir='_build/text',
                doctreedir='_build/.doctrees',
                buildername='text',
            )
            app.build(force_all=True)
            with open(test_file) as fin:
                text = fin.read().strip()
                self.assertIn(test_string, text)
        finally:
            shutil.rmtree('_build')
            os.chdir('../..')


class PythonTests(LanguageIntegrationTests):

    def test_integration(self):
        self._run_test(
            'pyexample',
            '_build/text/index.txt',
            'Hey there friend!'
        )
