# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import docutils
import docutils.core
from datetime import datetime
from fnmatch import fnmatch

# Lightbulb: A Git-Powered, Neo4j-Backed Python Blog Engine for Heroku


class Config(object):
    
    def __init__(self, project_folder=None):
        self.project_folder = project_folder or os.getcwd()
        self.source_folder = "source"
        self.build_folder = "build"
        self.timezone = "America/Chicago"


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


class Builder(object):
    def __init__(self, config):
        self.source = Source(config)
        self.fragment = Fragment(config)


    def build(self, source_path, build_path):
        key = self.fragment.is_new(build_path) and 'A' or 'U'
        data = self.source.get_data(source_path)
        fragment = data['fragment']
        with self.fragment.open_destination_file(build_path) as fout:
            fout.write(fragment.encode('utf-8') + '\n')
        print key, build_path
        return data

    def run(self):
        for source_file in self.source.get_all_files():
            print source_file
            slug = self.source.get_slug(source_file)
            build_path = self.fragment.get_build_path(slug)
            if self.fragment.needs_build(source_file, build_path):
                self.build(source_file, build_path)
        print "Done."
        

class Loader(object):

    def __init__(self, graph, changelog, config):
        self.graph = graph
        self.changelog = changelog
        self.config = config
        self.source = Source(self.config)

    def save(self):
        log = self.changelog.get()
        for filename in log:
            status, timestamp = log[filename]
            print status, filename, timestamp
            #data = self.builder.get_context(filename)
            #entry = self.graph.entries.create(data)
            #print entry.eid, entry.map()
          
    def update_all(self):
        for source_file in self.source.get_all_files():
            data = self.source.get_data(source_file)
            # TODO: if fragment exists...
            entry = self.graph.entries.save(data)
            print entry.eid, entry.map()

    def get_last_updated(self):
        # Get the lightbulb metadata node for entries
        meta = self.graph.lightbulb.get_or_create(name="entries")        
        return meta.get('last_updated')
       
    def set_last_updated(self, last_updated):
        # Get the lightbulb metadata node for entries
        meta = self.graph.lightbulb.get_or_create(name="entries")
        meta.last_updated = last_updated
        meta.save()

