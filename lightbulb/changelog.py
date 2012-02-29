import os
import re
import time
import pickle
from subprocess import Popen, PIPE
from collections import OrderedDict

# To have multiple pre-commit hook files, see...
# http://zgp.org/~dmarti/tips/git-multiple-post-receive-hooks/
    
# Defaults
LOG_NAME = "changelog.pickle"
SOURCE_PATH = "source/"
SOURCE_EXT = ".rst"

class ChangeLog(object):

    def __init__(self, log_name=None, source_path=None, source_ext=None):
        self.log_name = log_name = LOG_NAME
        self.source_path = source_path or SOURCE_PATH
        self.source_ext = source_ext or SOURCE_EXT

    def get(self):
        try:
            changelog = self._read()
        except (IOError, EOFError) as e:
            changelog =  OrderedDict()
        return changelog
        
    def update(self):
        # Don't create a changelog unless file exists
        if not os.path.isfile(self.log_name):
            print "CHANGELOG NOT FOUND - WILL ADD/UPDATE ALL ENTRIES IN DATABASE ON PUSH"
            # Remove the old changelog from git so it doesn't persist on the server
            self._remove_changelog()
            return
        # File exists so go ahead and read/write to the changlog
        diff = self._get_diff()   
        changelog = self.get()
        changelog = self._write(changelog, diff)
        self._display(changelog)

    def _read(self):
        with open(self.log_name, "r") as fin:
            # changelog is an OrderedDict
            changelog = pickle.load(fin)   
            #items = sorted(files.items(), key=itemgetter(1,1))
        return changelog
        
    def _write(self, changelog, diff):
        for status, filename in self._split_diff(diff):
            if re.search(self.source_path, filename) and filename.endswith(self.source_ext):
                # Git diff is NOT sorted by modified time.
                # We need it ordered by time so use timestamp instead
                timestamp = self._current_timestamp()
                # remove it from the dict and add it back so more recent entries are always last
                changelog.pop(filename, None)
                changelog[filename] = (status, timestamp)
                    
        # not using JSON because we want to maintain order in the dict
        with open(self.log_name, "w") as fout:
            pickle.dump(changelog, fout)

        # Add the changelog to git now that it has been updated.
        self._add_changelog()

        return changelog

    def _display(self, changelog):
        print "CHANGELOG"
        for filename in changelog:
            status, timestamp = changelog[filename]
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
        return self._execute_git(command)

    def _add_changelog(self):
        # Add the changelog to git after it has been updated.
        command = "git add %s" % self.log_name
        self._execute_git(command)

    def _remove_changelog(self):
        # Doing this so the old changelog doesn't persist on the server
        command = "git rm %s" % self.log_name
        print self._execute_git(command)
        
    def _execute_git(self, command):
        pipe = Popen(command, shell=True, cwd=".", stdout=PIPE, stderr=PIPE )
        (out, error) = pipe.communicate()
        pipe.wait()
        return out


