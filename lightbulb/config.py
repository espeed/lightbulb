# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import sys
import yaml
import distutils.dir_util

from pickledb import PickleDB
from utils import get_working_dir, get_git_dir



class Registry(PickleDB):
    """Registry is a pickle file stored in working_dir/etc/registy.pickle"""

    db_name = "registry"


class Config(object):
    """
    Blog engine configuration.

    :ivar name: Blog author's full name.
    :ivar username: Blog author's username.
    :ivar working_dir: Full path to the working directory managed by the Git repo.
    :ivar git_dir: Full path to the Git repo directory. Defaults to working_dir/.git
    :ivar project_folder: Project folder, relative to the working directory.
    :ivar source_folder: Source/read folder, relative to the project folder.
    :ivar fragment_folder: Fragment/write folder, relative to the project folder
    :ivar writer_name: Docutils writer.
    :ivar source_ext: Source file extension.
    :ivar editor: Text editor command.

    """
    
    def __init__(self, working_dir=None, git_dir=None):

        self.working_dir = self._get_working_dir(working_dir)
        self.git_dir = self._get_git_dir(git_dir)
        self.project_folder = self._get_project_folder()
        self._config = self._get_config()

    def _is_heroku(self):
        return os.environ.get('NEO4J_REST_URL') is not None        

    def _get_working_dir(self, working_dir):
        if self._is_heroku():
            return os.getcwd()
        return working_dir or get_working_dir()
        
    def _get_git_dir(self, git_dir):
        if self._is_heroku():
            return None
        return git_dir or get_git_dir()        

    def _get_config(self):
        try:
            yaml_abspath = self._get_yaml_abspath()
            fin = open(yaml_abspath)
            yaml_map = yaml.load(fin)
            return yaml_map
        except IOError as e:
            print "Couldn't find lightbulb config file: ./etc/lightbulb.yaml."
            print "To create it, run:  lightbulb setup" 
            sys.exit(1)

    def _get_yaml_abspath(self):
        project_etc = self.get_project_etc()
        return os.path.join(project_etc, "lightbulb.yaml")

    def get_project_etc(self):
        project_folder = self._get_project_folder()
        return os.path.join(self.working_dir, project_folder, "etc")
                    
    def _get_project_folder(self):
        # This is stored relative from working_dir
        registry = self.get_registry()
        project_folder = registry.get("project_folder")
        if project_folder is None:
            print "Project folder not set in working_dir/etc/registry.pickle"
            sys.exit(1)
        return project_folder

    def get_registry(self):
        working_etc = self.get_working_etc()
        file_name = "registry.pickle"
        return Registry(working_etc, "registry.pickle")

    def get_working_etc(self):
        return os.path.join(self.working_dir, "etc")        
        
    def __getattr__(self, name):
        try:
            return self._config[name]
        except:
            raise AttributeError(name)
        

class Path(object):
    
    def __init__(self, config):
        self.config = config
        self.etc_dir = "etc"
    
    # Top-level directories

    def get_working_dir(self):
        return self.config.working_dir

    def get_git_dir(self):
        return self.config.git_dir

    def get_project_dir(self):
        # Full path to the project directory
        return os.path.join(self.config.working_dir, self.config.project_folder)

    def get_source_dir(self):
        # Full path to the source directory
        project_dir = self.get_project_dir()
        return os.path.join(project_dir, self.config.source_folder)

    def get_fragment_dir(self):
        # Full path to the source directory
        project_dir = self.get_project_dir()
        return os.path.join(project_dir, self.config.fragment_folder)

    def get_working_etc(self):
        return os.path.join(self.config.working_dir, self.etc_dir)

    def get_project_etc(self):
        project_dir = self.get_project_dir()
        return os.path.join(project_dir, self.etc_dir)

    # Source file paths
        
    def get_source_abspath(self, file_path):
        # This is coming from changelog as blog/source/test.rst
        return os.path.join(self.config.working_dir, file_path)
            
    def get_source_path(self, source_abspath):
        # Source path is relative to the source folder.
        start = self.get_source_dir()
        return os.path.relpath(source_abspath, start)
        
    # Fragment file paths
        
    def get_fragment_abspath(self, source_abspath):
        fragment_dir = self.get_fragment_dir()
        fragment_path = self.get_fragment_path(source_abspath)
        return os.path.join(fragment_dir, fragment_path)

    def get_fragment_path(self, source_abspath):
        # Fragment path is relative to the fragment folder.

        # /home/james/bulbflow.com/blog/source/2012/hello.rst 
        # => /home/james/bulbflow.com/blog/source/2012, hello.rst
        head_dir, basename = os.path.split(source_abspath)

        # /home/james/bulbflow.com/blog/source/2012 => 2012 
        start = self.get_source_dir()
        fragment_folder = os.path.relpath(head_dir, start)

        # hello.rst => hello
        stub = os.path.splitext(basename)[0]  # remove the ext
        filename = "%s.html" % stub        

        # => 2012/hello.html
        fragment_path = os.path.join(fragment_folder, filename)

        return os.path.normpath(fragment_path)

    # Working Etc

    def get_changelog_abspath(self):
        # Changelog should go in working dir because it may manage multiple projects
        working_etc = self.get_working_etc()
        return os.path.join(working_etc, "changelog.pickle")

    # Project Etc

    def get_rst_template_path(self):
        project_etc = self.get_project_etc()
        return os.path.join(project_etc, "template.rst")
    
