# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import re
import time
import pickle
from subprocess import Popen, PIPE
from collections import OrderedDict

from config import Path

class ChangeLog(object):
    """Blog entry change log. Updated upon Git commits."""

    def __init__(self, config):
        self.config = config
        self.path = Path(config)

    def get(self):
        try:
            data = self._read()
        except (IOError, EOFError) as e:
            data =  OrderedDict()
        return data
        
    def update(self):
        # File exists so go ahead and read/write to the changlog
        if self.exists() is False:
            return 
        
        diff = self._get_diff()   
        if not diff:
            return

        data = self.get()
        data = self._write(data, diff)
        self._display(data)
        return data

    def exists(self):
        # Don't create a changelog unless file exists
        changelog_abspath = self.path.get_changelog_abspath()
        if not os.path.isfile(changelog_abspath):
            print "CHANGELOG NOT FOUND - WILL ADD/UPDATE ALL ENTRIES IN DATABASE ON PUSH"
            # Remove the old changelog from git so it doesn't persist on the server
            self._remove_changelog()
            return False
        return True

    def _read(self):
        changelog_abspath = self.path.get_changelog_abspath()
        with open(changelog_abspath, "r") as fin:
            # changelog data is an OrderedDict
            data = pickle.load(fin)   
            #items = sorted(files.items(), key=itemgetter(1,1))
        return data
        
    def _write(self, data, diff):
        source_dir = self.path.get_source_dir()
        start = self.path.get_working_dir()
        source_folder = os.path.relpath(source_dir, start)
        for status, filename in self._split_diff(diff):
            # filter out files that don't include the source_dir
            if re.search(source_folder, filename) and filename.endswith(self.config.source_ext):
                # Git diff is NOT sorted by modified time.
                # We need it ordered by time so use timestamp instead
                timestamp = self._current_timestamp()
                # remove it from the dict and add it back so more recent entries are always last
                data.pop(filename, None)
                data[filename] = (status, timestamp)
                    
        # not using JSON because we want to maintain order in the dict
        changelog_abspath = self.path.get_changelog_abspath()
        with open(changelog_abspath, "w") as fout:
            pickle.dump(data, fout)

        # Add the changelog to git now that it has been updated.
        self._add_changelog()

        return data

    def _display(self, data):
        print "CHANGELOG"
        for filename in data:
            status, timestamp = data[filename]
            print timestamp, status, filename 
        print

    def _current_timestamp(self):
        return int(time.time())

    def _split_diff(self, diff):
        lines = [line.split('\t') for line in diff.strip().split('\n')]
        return lines

    def _get_diff(self):
        # git diff is NOT sorted by modified time
        #command = "git diff --cached --name-only"
        repo_dir = self.path.get_repo_dir()
        working_dir = self.path.get_working_dir()
        command = "git  diff --cached --name-status"
        return self._execute(command)

    def _add_changelog(self):
        # Add the changelog to git after it has been updated.
        command = "git add %s" % self.path.get_changelog_abspath()
        self._execute(command)

    def _remove_changelog(self):
        # Doing this so the old changelog doesn't persist on the server
        command = "git rm %s" % self.path.get_changelog_abspath()
        print self._execute(command)
        
    def _execute(self, command):
        # TODO: Will Popen work with Heroku single-process instances? It looks like it does.
        # Setting Git env vars to ensure proper paths when running outside or working dir
        os.putenv("GIT_DIR", self.path.get_repo_dir())
        os.putenv("GIT_WORK_TREE", self.path.get_working_dir()) 
        pipe = Popen(command, shell=True, cwd=".", stdout=PIPE, stderr=PIPE )
        (out, error) = pipe.communicate()
        pipe.wait()
        return out


