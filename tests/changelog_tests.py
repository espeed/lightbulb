# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

import os
import unittest
from collections import OrderedDict

from lightbulb import ChangeLog

# Defaults
LOG_NAME = "changelog.pickle"
SOURCE_PATH = "source/"
SOURCE_EXT = ".rst"


class ChangeLogTestCase(unittest.TestCase):

    def setUp(self):
        # Make sure we're not going to clobber someone's existing repo
        assert not os.path.isdir(".git")
        assert not os.path.exists("changelog.pickle")

        self.changelog = ChangeLog()
        self.changelog._execute("git init")
        
    def test_init(self):
        assert self.changelog.log_name == LOG_NAME
        assert self.changelog.source_path == SOURCE_PATH
        assert self.changelog.source_ext == SOURCE_EXT

    def test_get(self):
        data = self.changelog.get()

        assert isinstance(data, OrderedDict)
        assert len(data) == 0
        
    def test_update(self):
        data = self.changelog.update()
        assert data is None

        self.changelog._execute("touch changelog.pickle")
        self.changelog._execute("git add .")
        self.changelog._execute("git commit -m test commit")

        
        dataA = self.changelog.update()
        assert isinstance(dataA, OrderedDict)

        dataB = self.changelog.get()
        assert isinstance(dataB, OrderedDict)

        assert dataA == dataB
        assert len(dataB) > 1
        
        status, timestamp = dataB['project/source/lightbulb.rst']
        assert status == 'A'
        assert type(timestamp) == int


        status, timestamp = dataB['project/source/another-file.rst']
        assert status == 'A'
        assert type(timestamp) == int

    def tearDown(self):
        # Remove the repo we created in setUp
        self.changelog._execute("rm -rf .git")

        self.changelog._execute("rm changelog.pickle")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChangeLogTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
