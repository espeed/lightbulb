#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from lightbulb.changelog import ChangeLog

# To have multiple pre-commit hook files, see...
# http://zgp.org/~dmarti/tips/git-multiple-post-receive-hooks/
    
LOG_NAME = "changelog.pickle"
SOURCE_PATH = "source/"
SOURCE_EXT = ".rst"

changelog = ChangeLog(LOG_NAME, SOURCE_PATH, SOURCE_EXT)

if __name__ == '__main__':
    changelog.update()



