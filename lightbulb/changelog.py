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

# Defaults
LOG_NAME = "changelog.pickle"
SOURCE_PATH = "source/"
SOURCE_EXT = ".rst"


class ChangeLog(object):
    """Blog entry change log. Updated upon Git commits."""

    def __init__(self, log_name=None, source_path=None, source_ext=None):
        # TODO: make sure log goes in project dir
        self.log_name = log_name = LOG_NAME
        self.source_path = source_path or SOURCE_PATH
        self.source_ext = source_ext or SOURCE_EXT

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
        if not os.path.isfile(self.log_name):
            print "CHANGELOG NOT FOUND - WILL ADD/UPDATE ALL ENTRIES IN DATABASE ON PUSH"
            # Remove the old changelog from git so it doesn't persist on the server
            self._remove_changelog()
            return False
        return True

    def _read(self):
        with open(self.log_name, "r") as fin:
            # changelog data is an OrderedDict
            data = pickle.load(fin)   
            #items = sorted(files.items(), key=itemgetter(1,1))
        return data
        
    def _write(self, data, diff):
        for status, filename in self._split_diff(diff):
            if re.search(self.source_path, filename) and filename.endswith(self.source_ext):
                # Git diff is NOT sorted by modified time.
                # We need it ordered by time so use timestamp instead
                timestamp = self._current_timestamp()
                # remove it from the dict and add it back so more recent entries are always last
                data.pop(filename, None)
                data[filename] = (status, timestamp)
                    
        # not using JSON because we want to maintain order in the dict
        with open(self.log_name, "w") as fout:
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
        command = "git diff --cached --name-status"
        return self._execute(command)

    def _add_changelog(self):
        # Add the changelog to git after it has been updated.
        command = "git add %s" % self.log_name
        self._execute(command)

    def _remove_changelog(self):
        # Doing this so the old changelog doesn't persist on the server
        command = "git rm %s" % self.log_name
        print self._execute(command)
        
    def _execute(self, command):
        # TODO: Will Popen work with Heroku single-process instances? It looks like it does.
        pipe = Popen(command, shell=True, cwd=".", stdout=PIPE, stderr=PIPE )
        (out, error) = pipe.communicate()
        pipe.wait()
        return out


