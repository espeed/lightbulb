#!/usr/bin/env python

import os
import sys
import argparse
import shutil

from lightbulb import Config, Command
from lightbulb.utils import get_working_dir

from setup import setup

# Valid commands: setup, new, edit, init, build, update, confbulbs
    
def confbulbs():
    filename = "confbulbs.py" 
    module_dir = os.path.dirname(__file__)
    confbulbs = os.path.join(module_dir, filename)
    working_dir = get_working_dir()
    dst = os.path.join(working_dir, filename)
    print "Creating file: %s" % dst
    return shutil.copyfile(confbulbs, dst)

def main():  
    parser = argparse.ArgumentParser()
    parser.add_argument('command_name')
    parser.add_argument('command_args', nargs='*')
    args = parser.parse_args()

    command_name = args.command_name
    command_args = args.command_args

    if command_name == "setup":
        confbulbs()
        return setup(command_args)

    if command_name == "confbulbs":
        return confbulbs()
        
    path = os.getcwd()
    sys.path.append(path)
    from confbulbs import graph

    config = Config()
    command = Command(config, graph)

    command.execute(command_name, command_args)


if __name__ == "__main__":
    main()
