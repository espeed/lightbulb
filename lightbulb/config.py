import os

class Config(object):
    
    def __init__(self, project_folder=None):
        self.project_folder = project_folder or os.getcwd()
        self.source_folder = "source"
        self.template_folder = "_templates"
        self.build_folder = "build"
        self.timezone = "America/Chicago"




