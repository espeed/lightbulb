# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import re
import os
import sys
from unicodedata import normalize
from subprocess import Popen, PIPE
from string import Template


def get_template(template_path):
    fin = open(template_path, "r")
    text = fin.read().decode('utf-8')  # source_text
    return Template(text)

#
# Subprocess 
#

def execute(command):
    # TODO: Will Popen work with Heroku single-process instances? It looks like it does.
    pipe = Popen(command, shell=True, cwd=".", stdout=PIPE, stderr=PIPE )
    (out, error) = pipe.communicate()
    pipe.wait()
    return out

def get_working_dir():
    working_dir = execute("git rev-parse --show-toplevel").strip()
    validate_git_repo(working_dir)
    return os.path.abspath(working_dir)

def get_git_dir():
    git_dir = execute("git rev-parse --git-dir").strip()
    validate_git_repo(git_dir)
    return os.path.abspath(git_dir)

def validate_git_repo(dirname):
    if dirname == "":
        print "You're not in a Git repo. Create one with:  git init"
        sys.exit(1)


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
