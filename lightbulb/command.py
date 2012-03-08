import os
import sys
import uuid
import getpass
import datetime
import subprocess
import shutil

from config import Config, Path
from engine import Parser, Writer, Loader
from utils import get_template

# emacs server

class Command(object):

    def __init__(self, config, graph):
        self.config = config
        self.graph = graph
        self.path = Path(config)
        self.parser = Parser(config)
        self.writer = Writer(config)
        self.loader = Loader(config, graph)

    # dotemacs
       
    def new(self, filename):
        # TODO: parse out docid, maybe sign docid

        try:
            assert filename.endswith(self.config.source_ext)
        except AssertionError as e:
            print "File name must end with %s" % self.config.source_ext
            sys.exit(1)

        docid = uuid.uuid4().hex
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        username = self.config.username or getpass.getuser()

        params = dict(docid=docid, author=username, date=date)
        
        template_path = self.path.get_rst_template_path()
        template = get_template(template_path)
        content = template.substitute(params)

        source_dir = self.path.get_source_dir()
        source_abspath = "%s/%s" % (source_dir, filename)

        self._make_dir(source_abspath)

        print "Creating file:  %s" % source_abspath
        fout = open(source_abspath, "w")
        fout.writelines(content)

        fout.close()

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

    def execute(self, command_name, command_args):
        command = getattr(self, command_name)
        return command(*command_args)

    def _write_file(self, file_path, content):
        with open(file_path, "w") as fout:
            fout.write(content.encode('utf-8') + '\n')

    def _make_dir(self, path):
        # mkpath
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            print "Creating dir:   %s" % dirname
            os.makedirs(dirname)


