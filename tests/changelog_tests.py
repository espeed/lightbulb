# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import unittest
from collections import OrderedDict

from lightbulb import Config, Path, ChangeLog
from lightbulb.utils import execute
from lightbulb.setup import Setup

module_abspath = os.path.abspath(__file__)

working_dir = os.path.dirname(module_abspath)
git_dir = "%s/.git" % working_dir
project_folder = "blog"
working_etc = "%s/etc" % working_dir

changelog_abspath = "%s/etc/changelog.pickle" % working_dir

def remove_git_repo(changelog_abspath):
    # Remove test repo and changelog
    execute("rm -rf %s" % git_dir)
    execute("rm %s" % changelog_abspath)


class ChangeLogTestCase(unittest.TestCase):

    def setUp(self):
        # Make sure we're not going to clobber someone's existing repo
        remove_git_repo(changelog_abspath)

        os.putenv("GIT_DIR", git_dir)
        os.putenv("GIT_WORK_TREE", working_dir) 
        execute("git init")

        setup = Setup(project_folder, working_dir, git_dir)
        setup.run()
        
        self.config = Config(working_dir)
        self.path = Path(self.config)

        self.changelog = ChangeLog(working_etc)
        self.changelog.initialize(self.config)
    

    def test_init(self):
        assert working_dir == self.path.get_working_dir()
        assert git_dir == self.path.get_git_dir()
        assert changelog_abspath == self.path.get_changelog_abspath()

        path = "%s/etc/changelog.pickle" % working_dir
        assert self.changelog.path.get_changelog_abspath() == path

    def test_get(self):
        data = self.changelog.data

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

        dataB = self.changelog.data
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
        self.changelog._execute("rm -rf %s" % git_dir)
        self.changelog._execute("rm %s" % changelog_abspath)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChangeLogTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
