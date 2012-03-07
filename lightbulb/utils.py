# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import re
import os
import sys
import uuid
import getpass
import datetime
from unicodedata import normalize
from string import Template

#
# Utils for creating new blog entry source files.
#

def get_template(template_path):
    fin = open(template_path, "r")
    text = fin.read().decode('utf-8')  # source_text
    return Template(text)

def create_new_file(filename):

    # TODO: parse out docid, maybe sign docid

    docid = uuid.uuid4().hex
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    params = dict(docid=docid, author=author, date=date)

    template_path = "etc/template.rst"
    template = get_template(template_path)
    content = template.substitute(params)

    source_path = "source/%s" % filename
    fout = open(source_path, "w")
    fout.writelines(content)

    fout.close()

#
# Util for creating URL slugs (from http://flask.pocoo.org/snippets/5/)
#

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

