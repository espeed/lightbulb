# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import unittest
from collections import OrderedDict

from lightbulb import Config, Path, ChangeLog

# Defaults
LOG_NAME = "changelog.pickle"
SOURCE_PATH = "source/"
SOURCE_EXT = ".rst"

module_abspath = os.path.abspath(__file__)
working_dir = os.path.dirname(module_abspath)
repo_dir = os.path.join(working_dir, ".git") 

config = Config(working_dir)
path = Path(config)
changelog_abspath = path.get_changelog_abspath()

class ChangeLogTestCase(unittest.TestCase):

    def setUp(self):
        os.putenv("GIT_DIR", path.get_repo_dir())
        os.putenv("GIT_WORK_TREE", path.get_working_dir()) 

        # Make sure we're not going to clobber someone's existing repo
        assert not os.path.isdir(repo_dir)
        assert not os.path.exists(changelog_abspath)
        
        # Specifying working dir so we don't clobber an actual repo
        self.changelog = ChangeLog(config)
        self.changelog._execute("git init")
        
    def test_init(self):
        path = "%s/changelog.pickle" % working_dir
        assert self.changelog.path.get_changelog_abspath() == path

    def test_get(self):
        data = self.changelog.get()

        assert isinstance(data, OrderedDict)
        assert len(data) == 0
        
    def test_update(self):
        data = self.changelog.update()
        assert data is None
        
        self.changelog._execute("touch %s" % changelog_abspath)
        self.changelog._execute("git add .")
        self.changelog._execute("git commit -m test commit")
        
        dataA = self.changelog.update()
        assert isinstance(dataA, OrderedDict)

        dataB = self.changelog.get()
        assert isinstance(dataB, OrderedDict)

        assert dataA == dataB
        assert len(dataB) > 1
        
        status, timestamp = dataB['blog/source/lightbulb.rst']
        assert status == 'A'
        assert type(timestamp) == int

        status, timestamp = dataB['blog/source/another-file.rst']
        assert status == 'A'
        assert type(timestamp) == int

    def tearDown(self):
        # Remove the repo we created in setUp
        self.changelog._execute("rm -rf %s" % repo_dir)
        self.changelog._execute("rm %s" % changelog_abspath)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChangeLogTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
