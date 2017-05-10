import os
import shutil
import codecs
from contextlib import contextmanager

from sphinx.application import Sphinx


@contextmanager
def sphinx_build(test_dir, builder='html'):
    os.chdir('tests/{0}'.format(test_dir))
    try:
        app = Sphinx(
            srcdir='.',
            confdir='.',
            outdir='_build/{0}'.format(builder),
            doctreedir='_build/.doctrees',
            buildername=builder,
        )
        app.build(force_all=True)
        yield app
    finally:
        shutil.rmtree('_build')
        os.chdir('../..')


@contextmanager
def build_output(src, path, builder='html'):
    with sphinx_build(src, builder):
        with codecs.open(path, 'r', 'utf-8') as h:
            data = h.read().strip()
            yield data
