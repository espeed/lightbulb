#!/usr/bin/env python

import os
import argparse
import getpass

from lightbulb import Config, Command
from lightbulb.config import copy_etc
from lightbulb.utils import get_template

def setup(working_dir):
    working_dir = os.path.abspath(working_dir)
    destination_dir = os.path.abspath("etc")
    copy_etc(destination_dir)
    yaml_abspath = "%s/lightbulb.yaml" % destination_dir
    template = get_template(yaml_abspath)
    params = dict()
    params['working_dir'] = working_dir
    params['repo_dir'] = "%s/.git" % working_dir
    params['project_folder'] = os.path.basename(os.getcwd())
    params['author'] = getpass.getuser()
    content = template.substitute(params)
    with open(yaml_abspath, "w") as fout:
        fout.write(content.encode('utf-8') + '\n')

def main():  
    parser = argparse.ArgumentParser()
    parser.add_argument('command_name')
    parser.add_argument('command_args', nargs='*')
    args = parser.parse_args()

    command_name = args.command_name
    command_args = args.command_args

    if command_name == "setup":
        working_dir = command_args[0]
        print "WORKING DIR", working_dir
        return setup(working_dir)

    config = Config()
    command = Command(config)

    command.execute(command_name, command_args)


if __name__ == "__main__":
    main()
