import os

class Fragment(object):

    def __init__(self, config):
        self.config = config

    def is_new(self, build_path):
        is_new = not os.path.exists(build_path)        
        return is_new

    def needs_build(self, source_path, build_path):
        if self.is_new(build_path):
            return True
        return os.path.getmtime(build_path) < os.path.getmtime(source_path)

    def make_destination_folder(self, build_path):
        destination_folder = os.path.dirname(build_path)
        if not os.path.isdir(destination_folder):
            os.makedirs(destination_folder)
            
    def open_destination_file(self, build_path, mode="w"):
        self.make_destination_folder(build_path)
        return open(build_path, mode)

    def write(self):
        pass

    def get_build_path(self, slug):
        project_folder = self.config.project_folder
        build_folder = self.config.build_folder
        #print "P", project_folder, build_folder, relative_stub
        build_path = os.path.join(project_folder, build_folder, slug, "index.html")
        return build_path

