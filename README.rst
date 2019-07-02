Read the Docs Sphinx Extensions
===============================

.. image:: https://img.shields.io/pypi/v/readthedocs-sphinx-ext.svg
   :target: https://pypi.python.org/pypi/readthedocs-sphinx-ext
   :alt: Pypi Version 
.. image:: https://travis-ci.org/readthedocs/readthedocs-sphinx-ext.svg?branch=master
   :target: https://travis-ci.org/readthedocs/readthedocs-sphinx-ext
   :alt: Build Status

This module adds extensions that make Sphinx easier to use.
Some of them require Read the Docs features,
others are just code that we ship and enable during builds on Read the Docs.

We currently ship:

* An extension for building docs like Read the Docs
* ``template-meta`` - Allows users to specify template overrides in per-page context.


Releasing
---------

#. Increment the version in ``setup.py``
#. Tag the release in git: ``git tag $NEW_VERSION``.
#. Push the tag to GitHub: ``git push --tags origin master``
#. Upload the package to PyPI:

    .. code:: bash

        $ rm -rf dist/
        $ python setup.py sdist bdist_wheel
        $ twine upload --sign --identity security@readthedocs.org dist/*
