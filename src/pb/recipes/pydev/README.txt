pb.recipes.pydev
================

Author: Tiberiu Ichim, tibi@pixelblaster.ro

WARNING: this recipe overwrites the .pydevproject file with a simplistic version,
make a backup or fix/extend the recipe to properly handle the file. For the
moment, it does everything I need.

    >>> import os

This recipe is about generating a `.pydevproject` file, which is used by Eclipse
and PyDev to hold a list of folders which hold Python packages (for code
completition, auto-import and so on). The idea is to fill this file with paths
pointing to the used egg folders. Although this recipe is written with a zope3
instance in mind, it can probably be used for any other scenario.

A full recipe would include the following options:

	>>> write(sample_buildout, 'buildout.cfg',
	... """
	... [buildout]
	... parts = pydev
	...
	... [pydev]
	... recipe = pb.recipes.pydev
	... pydevproject_path = ${buildout:directory}/.pydevproject_test
	... extra_paths = /something/else
	... target_python = python2.4
	... eggs = pb.recipes.pydev
	... """)
	
We need a working .pydevproject file. This recipe won't generate a new one. 
I'll use this project's project file for testing.

    >>> fc = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    ... <?eclipse-pydev version="1.0"?>
    ... <pydev_project>
    ... <pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">
    ... <path>/pb.recipes.pydev/src</path>
    ... </pydev_pathproperty>
    ... <pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">python 2.4</pydev_property>
    ... <pydev_pathproperty name="org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH">
    ... <path>/home/tibi/workspace3.3/pb.recipes.pydev/eggs/zc.buildout-1.0.0b31-py2.4.egg</path>
    ... <path>/home/tibi/workspace3.3/pb.recipes.pydev/eggs/zc.recipe.egg-1.0.0-py2.4.egg</path>
    ... </pydev_pathproperty>
    ... </pydev_project>"""
    >>> pf_path = os.path.join(sample_buildout, '.pydevproject_test')
    >>> f = open(pf_path, 'w')
    >>> f.write(fc)
    >>> f.close()

Now we can run the buildout
	
	>>> print system(buildout) #doctest: +NORMALIZE_WHITESPACE
	Installing pydev.

Let's verify the written `.pydevproject_test` file, the `extra_paths` option

	>>> import os
	>>> data = open(os.path.join(sample_buildout, '.pydevproject_test')).read()
	>>> '<path>/something/else</path>' in data
	True

We have placed in the `eggs` option this recipe's egg, but this can be anything,
(and it should be your developing application's egg name, as declared in your
`setup.py`). The `pb.recipes.pydev` egg depends on `zc.recipe.egg`,
`zc.buildout` and `setuptools`, let's see if all these were included.

XXX: this test assumes *nix paths, probably the same with a Windows path, as we
only take path fragment length into consideration

    >>> code_path = __file__[:len(__file__) -
    ...                          len('/src/pb/recipes/pydev/README.txt')]
    >>> pydev_egg_src = os.path.join(code_path, 'src')
    >>> ('<path>%s</path>' % pydev_egg_src) in data
    True
    >>> ('<path>%s/eggs/zc.recipe.egg' % code_path) in data
    True
    >>> ('<path>%s/eggs/zc.buildout' % sample_buildout) in data
    True
    >>> ('<path>%s/eggs/setuptools' % sample_buildout) in data
    True
    >>>

Almost all options of this recipe for the buildout.cfg are optional. The only
one required is the `eggs` option. A sample zope3 instance buildout, with the
pydev recipe could be something like this:

[buildout]
develop = .
parts = instance pydev

[sample-app]
recipe = zc.zope3recipes:app
eggs = something [app, third_party]

[pydev]
recipe = pb.recipes.pydev
eggs = ${sample-app:eggs}