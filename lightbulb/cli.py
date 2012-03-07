#!/usr/bin/env python

import os
import sys
import argparse
import getpass

from lightbulb import Config, Command
from lightbulb.config import copy_etc
from lightbulb.utils import get_template

def setup(command_args):
    working_dir = get_working_dir(command_args)
    destination_dir = os.path.abspath("etc")
    copy_etc(destination_dir)
    yaml_abspath = "%s/lightbulb.yaml" % destination_dir
    template = get_template(yaml_abspath)
    params = dict()
    params['working_dir'] = working_dir
    params['repo_dir'] = "%s/.git" % working_dir
    params['project_folder'] = get_project_folder(working_dir)
    params['author'] = getpass.getuser()
    content = template.substitute(params)
    with open(yaml_abspath, "w") as fout:
        fout.write(content.encode('utf-8') + '\n')
    print 
    print "Double check the generated config file etc/lightbulb.yaml ..."
    print
    print open(yaml_abspath,"rb").read()

def get_project_folder(working_dir):
    project_dir = os.getcwd()
    start = working_dir
    return os.path.relpath(project_dir, start)


def get_working_dir(command_args):
    try:
        working_dir = command_args[0]
        return os.path.abspath(working_dir)
    except:
        print
        print "The lightbulb setup util needs to know two things to generate the config file: "
        print 
        print "1. Your Git working directory (usually the parent of .git)."
        print "2. Project folder (usually the ./blog subdirectory in the working directory)."
        print
        print "Run setup from within the project folder, and pass the working_dir as an arg."
        print 
        print "Usage: lightbulb setup /path/to/working_dir"
        print
        sys.exit(1)
        

def main():  
    parser = argparse.ArgumentParser()
    parser.add_argument('command_name')
    parser.add_argument('command_args', nargs='*')
    args = parser.parse_args()

    command_name = args.command_name
    command_args = args.command_args

    if command_name == "setup":
        return setup(command_args)

    config = Config()
    command = Command(config)

    command.execute(command_name, command_args)


if __name__ == "__main__":
    main()
