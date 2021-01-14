import unittest
from textwrap import dedent

import pytest
from sphinx import version_info

from .util import build_output, sphinx_build


class LanguageIntegrationTests(unittest.TestCase):

    def _run_test(self, test_dir, test_file, test_string, builder='html', assert_in=True):
        with build_output(test_dir, test_file, builder) as data:
            if not isinstance(test_string, list):
                test_strings = [test_string]
            else:
                test_strings = test_string
            for string in test_strings:
                if assert_in:
                    self.assertIn(string, data)
                else:
                    self.assertNotIn(string, data)


class IntegrationTests(LanguageIntegrationTests):

    def test_integration(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            'Hey there friend!',
            builder='html',
        )

    def test_media_integration(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            'assets.readthedocs.org',
            builder='html',
        )

    def test_included_js(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            ['readthedocs-analytics.js', 'readthedocs-doc-embed.js'],
            builder='html',
        )

    def test_included_data(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            'id="READTHEDOCS_DATA"',
            builder='html',
        )

    def test_searchtools_is_patched(self):
        with build_output('pyexample', '_build/html/_static/searchtools.js',
                          builder='html') as data:
            self.assertNotIn('Search.init();', data)
            self.assertIn('Search initialization removed for Read the Docs', data)

    def test_generate_json_artifacts(self):
        self._run_test(
            'pyexample-json',
            '_build/json/index.fjson',
            [
                'current_page_name', 'title', 'body',
                'toc', 'sourcename', 'page_source_suffix',
            ],
        )

    def test_generate_json_domain_artifacts(self):
        self._run_test(
            'pyexample-json',
            '_build/json/readthedocs-sphinx-domain-names.json',
            [
                # types
                '"js:class": "class"',
                # pages
                '"index.html": "index"',
                # paths
                '"index.html": "index.rst"',
                # titles
                '"index.html": "Welcome to pyexample',
            ],
        )

    def test_escape_js_vars(self):
        with build_output('pyexample', '_build/html/escape\' this js.html',
                          builder='html') as data:
            self.assertNotIn('escape \' this js', data)
            self.assertIn('escape\\u0027 this js', data)

        with build_output('pyexample', '_build/html/index.html', builder='html') as data:
            self.assertNotIn("malic''ious", data)
            self.assertIn('malic\\u0027\\u0027ious', data)

    def test_escape_canonical_url(self):
        self._run_test(
            'pyexample',
            '_build/html/index.html',
            '<link rel="canonical" href="https://example.com/&#34;" />',
            builder='html',
        )

    @pytest.mark.skipif(version_info < (1, 8), reason='Requires sphinx>=1.8')
    def test_canonical_url(self):
        self._run_test(
            'pyexample-json',
            '_build/html/index.html',
            'Always link to the latest version, as canonical.',
            builder='html',
            assert_in=False,
        )

        self._run_test(
            'pyexample-json',
            '_build/html/index.html',
            '<link rel="canonical" href="https://example.com/index.html" />',
            builder='html',
        )

    def test_version_warning(self):
        self._run_test(
            'pr-example',
            '_build/html/index.html',
            # This paragraph can have a "last" class in old versions of sphinx
            # <p class="last">
            '>This page '
            '<a class="reference external" href="https://readthedocs.org/projects/docs/builds/12759474/">'
            'was created </a>'
            'from a pull request '
            '(<a class="reference external" href="https://github.com/readthedocs/readthedocs.org/pull/7826">'
            '#123</a>).</p>',
            builder='html',
        )
