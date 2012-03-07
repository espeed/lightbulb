import os
import sys
import uuid
import getpass
import datetime
from string import Template

from config import Config, Path
from engine import Writer

# emacs server

class Command(object):

    def __init__(self, config):
        self.config = config
        self.path = Path(config)
        self.writer = Writer(config)
    
    def execute(self, command_name, command_args):
        command = getattr(self, command_name)
        return command(*command_args)

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
        
        template_path = "template.rst"
        template = self._get_template(template_path)
        content = template.substitute(params)

        source_path = "source/%s" % filename

        self._make_dir(source_path)

        print "Creating file:  %s" % source_path
        fout = open(source_path, "w")
        fout.writelines(content)

        fout.close()

    def _write_file(self, file_path, content):
        with open(file_path, "w") as fout:
            fout.write(content.encode('utf-8') + '\n')


    def _make_dir(self, path):
        # mkpath
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            print "Creating dir:   %s" % dirname
            os.makedirs(dirname)


    def _get_template(self, template_path):
        fin = open(template_path, "r")
        text = fin.read().decode('utf-8')  # source_text
        return Template(text)
