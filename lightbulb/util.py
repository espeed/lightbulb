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

from .engine import Config, Writer

#
# Utils for creating new blog entry source files.
#

def get_template(template_path):
    fin = open(template_path, "r")
    text = fin.read().decode('utf-8')  # source_text
    return Template(text)

def create_new_file(source_file, author):

    # TODO: parse out docid, maybe sign docid

    docid = uuid.uuid4().hex
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    params = dict(docid=docid, author=author, date=date)

    template_path = "template.rst"
    template = get_template(template_path)
    content = template.substitute(params)

    source_path = "source/%s" % source_file
    fout = open(source_path, "w")
    fout.writelines(content)

    fout.close()



