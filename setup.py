#!/usr/bin/env python
from setuptools import setup, find_packages

name = 'pb.recipes.pydev'
entry_points = {'zc.buildout':['default = %s:PyDev' % name]}

setup (
    name='pb.recipes.pydev',
    version='0.1',
    author = "Pixelblaster",
    author_email = "tibi@pixelblaster.ro",
    license = "BSD",
    keywords = "buildout recipe PyDev eclipse",
    url = 'http://svn.plone.org/svn/collective/pb.recipes.pydev/',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['pb', 'pb.recipes'],
    install_requires = ['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        ],
    test_suite = name + '.tests.test_suite',
    entry_points = entry_points,
    zip_safe = True,
    )