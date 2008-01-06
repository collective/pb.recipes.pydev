import os
import zc.recipe.egg

class PyDev(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        wd = self.buildout['buildout']['directory']

        self._fpath = self.options.get('pydevproject_path',
                                       os.path.join(wd, '.pydevproject'))
        self._python = options.get('target_python', 'python2.4')
        self._extra_paths = options.get('extra_paths', '').split('\n')
        self._app_eggs = filter(None, options['eggs'].split('\n'))

    def install(self):
        egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)
        egg_names, ws = egg.working_set(self._app_eggs)
        egg_paths = ws.entries + self._extra_paths
        egg_paths = [p for p in egg_paths if p.strip() != '']   #strip empty paths

        _dev = self.buildout['buildout'].get('develop', './')
        _dir = self.buildout['buildout']['directory']

        src_paths = []
        #XXX: stupid way of determining src folders, should replace
        #source folders should be relative to workspace
        #we assume the buildout is run directly in the project, in the workspace
        #example path:
        #/home/me/workspace/MyProject/src
        for p in _dev.splitlines():
            #XXX: probably it won't work with multiple dev paths, especially
            #if they're placed outside the current project. Solutions??
            if not p.endswith('src'):
                p = os.path.join(_dir, p, './src')
                p = os.path.normpath(p)
            if p in egg_paths:
                #take out this project's src folder from the egg paths
                egg_paths.pop(egg_paths.index(p))
            src_paths.append(p)

        #we need a path that is "relative" to the workspace location
        #in Eclipse it will look like:
        #/MyProject/src
        #we assume these are the last two elements in the path
        _res = []
        for p in src_paths:
            buf = []
            while True:
                frags = os.path.split(p)
                buf.append(frags[1])
                p = frags[0]
                if (len(p) == 0) or (p == os.path.sep):
                    break
            buf.reverse()
            _res.append('/%s' % '/'.join(buf[-2:]))  #XXX: is / ok as path separator for Eclipse??

        src_paths = _res

        pydev_paths = '\n'.join(['<path>%s</path>' % p for p in egg_paths])
        src_paths = '\n'.join(['<path>%s</path>' % p for p in src_paths])

        content = template % {'paths':pydev_paths,
                              'target_python':self._python,
                              'src_path':src_paths
                             }

        f = open(self._fpath, 'w')
        f.write(content)
        f.close()
        return self._fpath

    update = install

template = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?eclipse-pydev version="1.0"?>
<pydev_project>
<pydev_pathproperty name="org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH">
%(paths)s
</pydev_pathproperty>
<pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">
%(src_path)s
</pydev_pathproperty>
<pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">%(target_python)s</pydev_property>
</pydev_project>
"""
