import codecs

from setuptools import setup, find_packages

setup(
    name='readthedocs-sphinx-ext',
    version='2.1.7',
    author='Read the Docs, Inc',
    author_email='dev@readthedocs.com',
    url='http://github.com/readthedocs/readthedocs-sphinx-ext',
    license='MIT',
    description='Sphinx extension for Read the Docs overrides',
    install_requires=['requests', 'Jinja2>=2.9'],
    package_dir={'': '.'},
    packages=find_packages('.', exclude=['tests']),
    long_description=codecs.open("README.rst", "r", "utf-8").read(),
    # trying to add files...
    include_package_data=True,
    package_data={
        '': ['_static/*.js', '_static/*.js_t', '_static/*.css', '_templates/*.tmpl'],
    },
)
