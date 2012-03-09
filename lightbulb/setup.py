import os
import sys
import pwd
import shutil
import getpass
import distutils.dir_util
from string import Template

from config import Registry
from utils import get_template, get_working_dir, get_git_dir


class Setup(object):

    yaml_file = "lightbulb.yaml"

    def __init__(self, project_folder, working_dir, git_dir):
        self.project_folder = project_folder
        self.working_dir = working_dir
        self.git_dir = git_dir

    def run(self):
        self.copy_etc()
        template = self.get_template()
        params = self.get_params()
        content = template.substitute(params)

        self.write_yaml_file(content)
        self.write_registry_file()

    def copy_etc(self):
        module_dir = os.path.dirname(__file__)
        source_dir = "%s/etc" % module_dir
        destination_dir = self.get_project_etc()
        for filename in distutils.dir_util.copy_tree(source_dir, destination_dir):
            print "Creating file: %s" % filename

    def get_project_etc(self):
        return os.path.join(self.working_dir, self.project_folder, "etc")         

    def get_template(self):
        yaml_abspath = self.get_yaml_abspath()
        return get_template(yaml_abspath)

    def get_yaml_abspath(self):
        project_etc = self.get_project_etc()
        return os.path.join(project_etc, self.yaml_file)

    def get_params(self):
        username = getpass.getuser()
        user = pwd.getpwnam(username)
        name = user.pw_gecos
        params = dict(name=name, username=username)
        return params
        
    def write_yaml_file(self, content):
        yaml_abspath = self.get_yaml_abspath()
        with open(yaml_abspath, "w") as fout:
            fout.write(content.encode('utf-8') + '\n')
        
    def write_registry_file(self):
        # making project_folder relative in case top-level directory is moved
        working_etc = self.get_working_etc()
        if not os.path.isdir(working_etc):
            print "Creating dir:  %s" % working_etc
            distutils.dir_util.mkpath(working_etc)
        registry = Registry(working_etc)
        registry_abspath = os.path.join(working_etc, "registry.pickle")
        print "Creating file: %s" % registry_abspath 
        registry.put("project_folder", self.project_folder) 
        
    def get_working_etc(self):
        return os.path.join(self.working_dir, "etc")         

    def display_results(self):
        # TODO: print working_dir, git_dir, project_folder
        yaml_abspath = self.get_yaml_abspath()
        print 
        print "Double check the config file generated at %s ..." % yaml_abspath
        print
        print open(yaml_abspath,"rb").read()


#
# Setup Utils
#

def setup(command_args):
    try:
        project_folder = command_args[0]
    except:
        print
        print "The lightbulb setup util needs to know two things to generate the config file: "
        print 
        print "1. Your Git working directory (usually the parent of the .git dir)."
        print "2. Project folder (usually the blog subdirectory in the working directory)."
        print
        print "Run setup from the Git working directory, and pass the project folder as an arg."
        print 
        print "Example: lightbulb setup blog"
        print
        sys.exit(1)
        
    working_dir = get_working_dir()
    git_dir = get_git_dir()

    setup = Setup(project_folder, working_dir, git_dir)
    setup.run()
    setup.display_results()


def generate_bulbsconf():
    # Create the default Bulbs config in the working directory
    filename = "bulbsconf.py" 
    module_dir = os.path.dirname(__file__)
    working_dir = get_working_dir()
    src = os.path.join(module_dir, filename)
    dst = os.path.join(working_dir, filename)
    print "Creating file: %s" % dst
    return shutil.copyfile(src, dst)
