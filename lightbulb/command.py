#!/usr/bin/env python

import os
import sys
import uuid
import shutil
import getpass
import datetime
import subprocess
import argparse
from titlecase import titlecase

from config import Config, Path
from setup import setup, generate_bulbsconf
from engine import Parser, Writer, Loader
from utils import get_template, get_working_dir


# Valid commands: setup, new, edit, init, build, update, bulbsconf
# TODO: dotemacs

class Command(object):



    def __init__(self, config, graph):
        self.config = config
        self.graph = graph
        self.path = Path(config)
        self.parser = Parser(config)
        self.writer = Writer(config)
        self.loader = Loader(config, graph)

    # Public methods
       
    def new(self, filename):
        # TODO: parse out docid, maybe sign docid

        try:
            assert filename.endswith(self.config.source_ext)
        except AssertionError as e:
            print "File name must end with %s" % self.config.source_ext
            sys.exit(1)

        source_dir = self.path.get_source_dir()
        source_abspath = "%s/%s" % (source_dir, filename)
        content = self._build_initial_source(filename)

        print "Creating file:  %s" % source_abspath
        self._create_file(source_abspath, content)

        return source_abspath

    def edit(self, filename):
        # Open new file in the editor specified in the yaml config file
        editor = self.config.editor
        source_path = self.new(filename)
        process = "%s %s" % (editor, source_path)
        return subprocess.call(process.split())

    def init(self):
        # Make sure author is pre-loaded in the database
        data = dict(username=self.config.username, name=self.config.name)
        author = self.graph.people.get_or_create("username", self.config.username, data)

    def build(self):
        # Create HTML fragments
        self.writer.run()

    def update(self):
        # Update blog entries
        self.loader.update_entries()

    # Execute one of the above methods

    def _execute(self, command_name, command_args):
        command = getattr(self, command_name)
        return command(*command_args)

    # Private methods

    def _create_file(self, source_abspath, content):
        self._make_dir(source_abspath)
        with open(source_abspath, "w") as fout:
            fout.writelines(content)
                                     
    def _build_initial_source(self, filename):
        # generat the source from template
        template_path = self.path.get_rst_template_path()
        template = get_template(template_path)
        params = self._get_params(filename)
        source = template.substitute(params)
        return source

    def _get_params(self, filename):
        # Get template params
        docid = uuid.uuid4().hex
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        username = self.config.username or getpass.getuser()
        title = self._get_title(filename)
        params = dict(title=title, docid=docid, author=username, date=date)
        return params

    def _get_title(self, filename):
        stub = os.path.splitext(filename)[0]
        word_list = stub.split(self.config.separator)
        words = " ".join(word_list)
        title = titlecase(words)
        return title

    def _write_file(self, file_path, content):
        with open(file_path, "w") as fout:
            fout.write(content.encode('utf-8') + '\n')

    def _make_dir(self, path):
        # mkpath
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            print "Creating dir:   %s" % dirname
            os.makedirs(dirname)


def main():  
    parser = argparse.ArgumentParser()
    parser.add_argument('command_name')
    parser.add_argument('command_args', nargs='*')
    args = parser.parse_args()

    command_name = args.command_name
    command_args = args.command_args

    if command_name == "setup":
        generate_bulbsconf()
        return setup(command_args)

    if command_name == "bulbsconf":
        return generate_bulbsconf()

    config = Config()
    
    # try to import graph from the local bulbsconf if it exists
    path = config.working_dir
    sys.path.insert(0, path)
    from bulbsconf import graph

    command = Command(config, graph)
    command._execute(command_name, command_args)


if __name__ == "__main__":
    main()
