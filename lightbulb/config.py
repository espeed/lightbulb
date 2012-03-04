# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os

class Config(object):
    """Blog engine configuration."""
    
    def __init__(self, working_dir=None):
        
        # Full path to the working directory managed by the Git repo
        self.working_dir = working_dir or os.getcwd()

        self.repo_folder = ".git"

        # Project folder, relative to the working directory
        self.project_folder = "blog" 

        # Source and Build folders, relative to the project folder
        self.source_folder = "source"
        self.build_folder = "build"

        self.writer_name = 'html4css1'
        self.source_ext = ".rst"
        self.changelog_name = "changelog.pickle"


class Path(object):
    
    def __init__(self, config):
        self.config = config
    
    # Top-level directories

    def get_working_dir(self):
        return self.config.working_dir

    def get_repo_dir(self):
        return os.path.join(self.config.working_dir, self.config.repo_folder)

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
        # so the start dir needs to be the git repo's working dir, not project_dir
        return os.path.join(self.config.working_dir, file_path)
             
    def get_source_path(self, source_abspath):
        # This is relative to the project folder, at the moment
        start = self.get_project_dir()
        return os.path.relpath(source_abspath, start)
        
    # Fragment file paths
        
    def get_fragment_abspath(self, source_abspath):
        project_dir = self.get_project_dir()
        fragment_path = self.get_fragment_path(source_abspath)
        return os.path.join(project_dir, fragment_path)

    def get_fragment_path(self, source_abspath):
        # This is relative to the project folder, at the moment

        # TODO: more test patterns

        # /project/source/2012/hello.rst => /project/source/2012, hello.rst
        head_dir, basename = os.path.split(source_abspath)

        # /project/source/2012 => 2012 
        #start = self.get_source_dir()
        #fragment_folder = os.path.relpath(head_dir, start)

        # hello.rst ==> hello
        stub = os.path.splitext(basename)[0]  # remove the ext
        filename = "%s.html" % stub        

        # ==> build/2012/hello.html
        #fragment_path = os.path.join(self.config.build_folder, fragment_folder, filename)
        fragment_path = os.path.join(self.config.build_folder, filename)
        return os.path.normpath(fragment_path)


    # Changelog
    def get_changelog_abspath(self):
        # Changelog should go in working dir because it may manage multiple projects
        return os.path.join(self.config.working_dir, self.config.changelog_name)

