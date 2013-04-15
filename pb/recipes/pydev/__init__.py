import logging
import os
import shutil
from StringIO import StringIO
from xml.dom import minidom

import zc.recipe.egg


def read_first_line(filepath):
    """Return the first line from file.
    """

    with open(filepath, 'r') as egg_link_file:
        return egg_link_file.read().splitlines()[0].strip()


class PyDev(object):
    """Auto-configure pydev external source path and project source path.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        wd = self.buildout['buildout']['directory']

        self._wd_path = wd
        self._use_sources_path = self.options.get('use_sources_path', False)
        self._buildout_dir_is_source = self.options.get(
                                               'buildout_dir_is_source', False)
        self._remote_path = self.options.get('remote_path', None)
        self._develop_path = os.path.normpath(os.path.join(wd, './src'))

        self._fpath = self.options.get('pydevproject_path',
                                       os.path.join(wd, '.pydevproject'))
        self._backup_path = "%s.bak" % self._fpath
        self._python = options.get('target_python', 'python2.4')
        self._extra_paths = options.get('extra-paths',
                                        options.get('extra_paths', '')
                                        ).split('\n')
        self._app_eggs = filter(None, options['eggs'].split('\n'))
        self.egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)

    def _add_path_nodes(self, document, project_node, name, paths):
        """Add path nodes to the xml document from file .pydevproject.
        """

        nodes = document.getElementsByTagName('pydev_pathproperty')
        prop_nodes = filter(lambda node: (node.getAttribute('name') ==
                            name),
                       nodes
                   )
        for node in prop_nodes:  # delete the PROJECT_EXTERNAL_SOURCE_PATH node
            project_node.removeChild(node)

        ext_node = document.createElement('pydev_pathproperty')
        ext_node.setAttribute('name', name)

        for p in paths:
            node = document.createElement('path')
            node.appendChild(document.createTextNode(p))
            ext_node.appendChild(node)

        project_node.appendChild(ext_node)

    def install(self):
        #egg_names, ws = egg.working_set(self._app_eggs)
        _reqs, ws = self.egg.working_set()
        egg_paths = ws.entries + self._extra_paths
        if self._use_sources_path:
            src_dir = self.buildout['buildout']['develop-eggs-directory']
            for filename in os.listdir(src_dir):
                filepath = os.path.join(src_dir, filename)
                egg_paths.append(read_first_line(filepath))
        egg_paths = [p for p in egg_paths if p.strip() != '']   # strip empty

        # relocate eggs so paths are valid on remote computers e.g.: nfs, smb
        if self._remote_path is not None:
            prefix = self.buildout['buildout']['directory']
            prefix_length = len(prefix)
            egg_paths = [p.startswith(prefix) and
                            '%s%s' % (self._remote_path,
                                      p[prefix_length:]) or p
                         for p in egg_paths]

        # filter develop paths and egg paths
        source_folder_paths = filter(lambda p: p.startswith(
                                                           self._develop_path),
                                     egg_paths)
        if self._buildout_dir_is_source:
            source_folder_paths.append(self._wd_path)
        basepath = os.path.dirname(self.buildout['buildout']['directory'])
        source_folder_paths = [os.path.join(os.path.sep,
                                            os.path.relpath(each, basepath))
                               for each in source_folder_paths]
        egg_paths = filter(lambda p: not p.startswith(self._develop_path),
                           egg_paths)

        if not os.path.exists(self._fpath):
            logging.warning("Could not find .pydevproject file. Ignore this "
                            "message if you're not using Eclipse Pydev")
            return ""

        document = minidom.parse(self._fpath)
        project_node = document.getElementsByTagName('pydev_project')[0]
        self._add_path_nodes(document,
                             project_node,
                             'org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH',
                             egg_paths)
        self._add_path_nodes(document,
                             project_node,
                             'org.python.pydev.PROJECT_SOURCE_PATH',
                             source_folder_paths)

        shutil.copy(self._fpath, self._backup_path)  # make a copy of the file
        open(self._fpath, 'w').write(document.toprettyxml())

        return ""

    update = install
