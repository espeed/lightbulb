#!/usr/bin/env python

import os
import sys
import argparse

from lightbulb import Config, Command
from lightbulb.utils import get_working_dir

from setup import setup, confbulbs

# Valid commands: setup, new, edit, init, build, update, confbulbs
    
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
