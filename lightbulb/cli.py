#!/usr/bin/env python

import os
import argparse
from lightbulb import Config, Command
from lightbulb.config import copy_etc


def setup():
    destination_dir = os.path.abspath("etc")
    copy_etc(destination_dir)

def main():  
    parser = argparse.ArgumentParser()
    parser.add_argument('command_name')
    parser.add_argument('command_args', nargs='*')
    args = parser.parse_args()

    command_name = args.command_name
    command_args = args.command_args

    if command_name == "setup":
        return setup()

    config = Config()
    command = Command(config)

    command.execute(command_name, command_args)


if __name__ == "__main__":
    main()
