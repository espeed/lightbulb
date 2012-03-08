import re
import os
import time

from config import Path
from utils import execute
from pickledb import PickleDB

# not using JSON because we want to maintain order in the dict
class ChangeLog(PickleDB):

    db_name = "changelog"

    def initialize(self, config):
        self.config = config
        self.path = Path(config)
        assert self.db_abspath == self.path.get_changelog_abspath()

    def update(self):
        # File exists so go ahead and read/write to the changlog
        if self.exists() is False:
            print "CHANGELOG NOT FOUND: Will add/update all entries in database on push."
            # Remove the old changelog from git so it doesn't persist on the server
            self._remove_changelog()
            return 
        
        diff = self._get_diff()   
        if not diff:
            return

        self._write_diff(diff)
        self._display()
        
        return self.data

    def _display(self):
        print "CHANGELOG"
        for filename in self.data:
            status, timestamp = self.data[filename]
            print timestamp, status, filename 
        print
        
    def _write_diff(self, diff):
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
                self.data.pop(filename, None)
                self.data[filename] = (status, timestamp)
        self.write()

        # Add the changelog to git now that it has been updated.
        self._add_changelog()

        return self.data

    def _current_timestamp(self):
        return int(time.time())

    def _split_diff(self, diff):
        lines = [line.split('\t') for line in diff.strip().split('\n')]
        return lines

    def _get_diff(self):
        # git diff is NOT sorted by modified time
        #command = "git diff --cached --name-only"
        git_dir = self.path.get_git_dir()
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
        # Setting Git env vars to ensure proper paths when running outside of working dir
        os.putenv("GIT_DIR", self.path.get_git_dir())
        os.putenv("GIT_WORK_TREE", self.path.get_working_dir()) 
        return execute(command)
