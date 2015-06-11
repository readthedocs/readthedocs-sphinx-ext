import codecs
try:
    from setuptools import setup, find_packages
    extra_setup = dict(
        install_requires=['requests', 'nilsimsa>=0.3.7'],
    )
except ImportError:
    from distutils.core import setup
    extra_setup = {}

setup(
    name='readthedocs-sphinx-ext',
    version='0.5.4',
    author='Eric Holscher',
    author_email='eric@ericholscher.com',
    url='http://github.com/ericholscher/readthedocs-sphinx-ext',
    license='BSD',
    description='Improved Client for Sphinx.',
    package_dir={'': '.'},
    packages=find_packages('.'),
    long_description=codecs.open("README.rst", "r", "utf-8").read(),
    # trying to add files...
    include_package_data=True,
    package_data={
        '': ['_static/*.js', '_static/*.js_t', '_static/*.css'],
    },
    **extra_setup
)
