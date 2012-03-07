# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import sys
import yaml
import distutils.dir_util


def copy_etc(destination_dir):
    current_dir = os.path.dirname(__file__)
    source_dir = "%s/etc" % current_dir
    for filename in distutils.dir_util.copy_tree(source_dir, destination_dir, verbose=True):
        print "Creating file: %s" % filename
        

class Config(object):
    """Blog engine configuration."""
    
    def __init__(self, working_dir=None, repo_dir=None, yaml_file=None):
        
        yaml_map = self._open_yaml(yaml_file)
        
        #: Blog author
        self.author = yaml_map['author']

        #: Full path to the working directory managed by the Git repo
        self.working_dir = working_dir or yaml_map['working_dir'] or os.getcwd()

        #: Full path to the Git repo directory. Defaults to working_dir/.git
        self.repo_dir = repo_dir or yaml_map['repo_dir'] or "%s/.git" % self.working_dir

        #: Project folder, relative to the working directory
        self.project_folder = yaml_map["project_folder"] 

        #: Source/read folder, relative to the project folder
        self.source_folder = yaml_map["source_folder"]

        #: Fragment/write folder, relative to the project folder
        self.fragment_folder = yaml_map["fragment_folder"]

        # Changlog file name, relative to the working directory
        self.changelog_name = yaml_map["changelog_name"]
        
        #: Docutils writer
        self.writer_name = yaml_map['writer_name']

        #: Source file extension 
        self.source_ext = yaml_map["source_ext"]

    def _open_yaml(self, yaml_file=None):
        try:
            filename = yaml_file or "%s/etc/lightbulb.yaml" % os.getcwd()
            fin = open(filename)
            yaml_map = yaml.load(fin)
            return yaml_map
        except IOError as e:
            print "Couldn't find lightbulb config file: ./etc/lightbulb.yaml."
            print "To create it, run:  lightbulb setup" 
            sys.exit(1)


class Path(object):
    
    def __init__(self, config):
        self.config = config
    
    # Top-level directories

    def get_working_dir(self):
        return self.config.working_dir

    def get_repo_dir(self):
        return self.config.repo_dir

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

    # Changelog

    def get_changelog_abspath(self):
        # Changelog should go in working dir because it may manage multiple projects
        return os.path.join(self.config.working_dir, self.config.changelog_name)

