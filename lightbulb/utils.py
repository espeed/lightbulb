# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import sys
from string import Template
from subprocess import Popen, PIPE

from model import cache

def get_template(template_path):
    fin = open(template_path, "r")
    text = fin.read().decode('utf-8')  # source_text
    return Template(text)

def cache_author(graph, config):
    # Store author ID in cache, keyed by username
    cache_key = "username:%s" % config.username
    author = graph.people.index.get_unique("username", config.username)
    cache.put(cache_key, author.eid) if author else None
    return author
    

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


