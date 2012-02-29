import os
import docutils
import docutils.core
from datetime import datetime
from fnmatch import fnmatch

# Lightbulb: A Git-Powered, Neo4j-Backed Python Blog Engine for Heroku

class Source(object):

    def __init__(self, config):
        self.config = config
        self.source_path = "%s/%s" % (config.project_folder, config.source_folder)
        self.writer_name = 'html4css1'

    def get_data(self, file_name):
        source = self.get_source(file_name)
        parts = self.get_publish_parts(source) 

        data = dict()
        data['title'] = parts['title']
        data['subtitle'] = parts['subtitle']
        data['fragment'] = parts['fragment']
        
        # Extra metadata: docid, author, date, tags
        meta = self._get_metadata(source, file_name) 
        data.update(meta)  

        # Derived parts: slug, fragment_path, source_path 
        slug = self.get_slug(file_name)
        data['slug'] = slug
        data['fragment_path'] = self.get_fragment_path(slug)
        data['source_path'] = file_name

        return data
        
    def get_publish_parts(self, source):
        # http://docutils.sourceforge.net/docs/api/publisher.html#publish-parts-details
        settings = dict(initial_header_level=2) # do we need this?
        options = dict(source=source, writer_name=self.writer_name, settings_overrides=settings)
        parts = docutils.core.publish_parts(**options)
        return parts

    def get_source(self, file_name):
        def_source = self.get_substitution_definitions()
        doc_source = self.read_file(file_name)
        source = "\n".join([def_source, doc_source])
        return source

    def get_substitution_definitions(self):
        # Standard substitution definitions
        # http://docutils.sourceforge.net/docs/ref/rst/definitions.html
        target_filename = "substitutions.rst"
        current_dir = os.path.dirname(__file__)
        file_path = os.path.normpath(os.path.join(current_dir, target_filename))
        source = self.read_file(file_path)
        return source

    def read_file(self,file_name):
        source_file_path = file_name
        fin = open(source_file_path, "r")
        source = fin.read().decode('utf-8')
        return source       

    def get_slug(self, file_name):
        source_dir = self.get_dir()
        relative_path = file_name.rpartition(source_dir)[-1].lstrip("/") 
        slug = os.path.splitext(relative_path)[0]
        return slug

    def get_fragment_path(self, slug):
        project_folder = self.config.project_folder
        build_folder = self.config.build_folder
        build_path = os.path.join(build_folder, slug, "index.html")
        return build_path

    def _get_desination_file(self, file_name):        
        destination_filename = self._get_desired_filename(file_name)
        desination_file = os.path.join(self.config.project_folder,
                                       self.config.get('output_folder'),
                                       self.destination_filename)
        return destination_file

    def _get_desired_filename(self, source_filename):
        folder, basename = os.path.split(source_filename)
        simple_name = os.path.splitext(basename)[0]
        if simple_name == 'index':
            suffix = 'index.html'
        else:
            suffix = os.path.join(simple_name, 'index.html')
        return os.path.join(folder, suffix)

    def _get_metadata(self, document, file_name):
        doctree = docutils.core.publish_doctree(document)
        docinfo = doctree.traverse(docutils.nodes.docinfo)
        try:
            meta = self._process_standard_fields(docinfo)
            meta = self._process_custom_fields(meta)
        except IndexError:
            print "ERROR: Source file is missing data: %s" % file_name
            raise
        for key, value in meta.items():
            meta[key] = value.astext()
        return meta

    def _process_standard_fields(self,docinfo):
        # Standard fields: date, author, etc.
        meta = {}
        for node in docinfo[0].children:
            key = node.tagname.lower()
            value = node.children[0]
            meta[key] = value
        return meta

    def _process_custom_fields(self, meta):
        # http://repo.or.cz/w/wrigit.git/blob/f045e5e7766e767c0b56bcb7a1ba0582a6f4f176:/rst.py
        field = meta['field']
        meta['tags'] = field.parent.children[1]
        meta['docid'] = field.parent.parent.children[0].children[1]
        del meta['field']
        return meta
        
    def get_all_files(self):
        source_dir = self.get_dir()
        for dirpath, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                # Ignore pattern: emacs autosave files. TODO: generalize this
                if fnmatch(filename, "*.rst") and not fnmatch(filename, "*.#*"):
                    source_path = os.path.join(dirpath, filename)
                    yield source_path

    def get_dir(self):
        source_dir = os.path.join(self.config.project_folder, self.config.source_folder)
        return source_dir

    def get_abspath(self, file_name):
        source_path = os.path.join(self.config.project_folder, self.config.source_folder, file_name)
        return source_path
