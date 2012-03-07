import os
import sys
import uuid
import getpass
import datetime
import subprocess

from config import Config, Path
from engine import Writer
from utils import get_template

# emacs server

class Command(object):

    def __init__(self, config):
        self.config = config
        self.path = Path(config)
        self.writer = Writer(config)
    
    def execute(self, command_name, command_args):
        command = getattr(self, command_name)
        return command(*command_args)

    def edit(self, filename):
        editor = self.config.editor
        source_path = self.new(filename)
        process = "%s %s" % (editor, source_path)
        return subprocess.call(process.split())
    
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
        author = self.config.author or getpass.getuser()

        params = dict(docid=docid, author=author, date=date)
        
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
        

    def _write_file(self, file_path, content):
        with open(file_path, "w") as fout:
            fout.write(content.encode('utf-8') + '\n')


    def _make_dir(self, path):
        # mkpath
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            print "Creating dir:   %s" % dirname
            os.makedirs(dirname)


