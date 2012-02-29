# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

import os
import sys
import uuid
import datetime
from string import Template

from .builder import Builder
from .config import Config


def get_template(template_path):
    fin = open(template_path, "r")
    text = fin.read().decode('utf-8')  # source_text
    return Template(text)

def create_new_file():

    # TODO: parse out docid, maybe sign docid

    filename = "another-test.rst"    

    docid = uuid.uuid4().hex
    author = "james"
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    params = dict(docid=docid, author=author, date=date)

    template_path = "template.rst"
    template = get_template(template_path)
    content = template.substitute(params)

    source_path = "source/%s" % filename
    fout = open(source_path, "w")
    fout.writelines(content)

    fout.close()


def main():
    if len(sys.argv) not in (1, 2, 3):
        print >> sys.stderr, 'usage: lightbulb <action> <folder>'

    if len(sys.argv) >= 2:
        action = sys.argv[1]
    else:
        action = 'build'

    if len(sys.argv) >= 3:
        folder = sys.argv[2]
    else:
        folder = os.getcwd()

    if action not in ('build', 'serve'):
        print >> sys.stderr, 'unknown action', action

    
    config = Config(folder)
    builder = Builder(config)

    builder.run()



