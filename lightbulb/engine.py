# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
from datetime import datetime
from fnmatch import fnmatch

import docutils
import docutils.core
from docutils.parsers.rst import directives
from directives.pygments_code_block_directive import CodeBlock

from config import Path
from changelog import ChangeLog
from model import cache

# Use Git's low-level plumbing commands for scripting, not the high-level porcelain commands
# See http://schacon.github.com/git/git.html
# http://stackoverflow.com/questions/2657935/checking-for-a-dirty-index-or-untracked-files-with-git

# Unless --cached is given, work tree is needed

# Register the code block directive
directives.register_directive("code", CodeBlock)

# container directive
# rst: supports class attributes and id attribute (markdown requires you to drop down into HTML)
# extensible: ReStructuredText is extensible (you can add your own "directives"). 
# http://stackoverflow.com/questions/34276/markdown-versus-restructuredtext
# https://en.wikipedia.org/wiki/Lightweight_markup_language

# See Sphinx image/figure anchor points...
# http://packages.python.org/an_example_pypi_project/sphinx.html

class Parser(object):
    """Parse ReStructuredText source files."""

    def __init__(self, config):
        self.config = config
        self.path = Path(config)
        #self.source_dir = "%s/%s" % (config.project_dir, config.source_folder)

    def get_fragment(self, source_abspath):
        source = self.get_document_source(source_abspath)
        parts = self.get_document_parts(source) 
        return parts['fragment']

    def get_data(self, source_abspath):
        source = self.get_document_source(source_abspath)
        parts = self.get_document_parts(source) 

        data = dict()
        data['title'] = parts['title']
        data['subtitle'] = parts['subtitle']
        data['fragment'] = parts['fragment']
        
        # Extra metadata: docid, author, date, tags
        meta = self._get_metadata(source, source_abspath) 
        data.update(meta)  

        # Derived parts: slug, fragment_path, source_path 
        slug = self.get_slug(source_abspath)
        data['slug'] = slug
        data['fragment_path'] = self.path.get_fragment_path(source_abspath)
        data['source_path'] = self.path.get_source_path(source_abspath)

        return data

    def get_document_source(self, source_abspath):
        def_source = self.get_substitution_definitions()
        doc_source = self.read_source_file(source_abspath)
        source = "\n".join([def_source, doc_source])
        return source
                
    def get_document_parts(self, source):
        # http://docutils.sourceforge.net/docs/api/publisher.html#publish-parts-details
        writer_name = self.config.writer_name
        settings = dict(initial_header_level=2) # do we need this?
        options = dict(source=source, writer_name=writer_name, settings_overrides=settings)
        parts = docutils.core.publish_parts(**options)
        return parts
    
    def get_substitution_definitions(self):
        # Standard substitution definitions
        # http://docutils.sourceforge.net/docs/ref/rst/definitions.html
        module_abspath = os.path.abspath(__file__)
        module_dir = os.path.dirname(module_abspath)
        source = self.read_source_file("%s/etc/substitutions.rst" % module_dir)
        return source

    def read_source_file(self, file_path):
        fin = open(file_path, "r")
        source = fin.read().decode('utf-8')
        return source       

    def get_slug(self, source_abspath):
        start = self.path.get_source_dir()
        #relative_path = file_name.rpartition(source_dir)[-1].lstrip("/") 
        relative_path = os.path.relpath(source_abspath, start)
        slug = os.path.splitext(relative_path)[0]
        return slug

    def _get_metadata(self, source, source_abspath):
        doctree = docutils.core.publish_doctree(source)
        docinfo = doctree.traverse(docutils.nodes.docinfo)
        try:
            meta = self._process_standard_fields(docinfo)
            meta = self._process_custom_fields(meta)
        except IndexError:
            print "ERROR: Source file is missing data: %s" % source_abspath
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
        source_dir = self.path.get_source_dir()
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                # Ignore pattern: emacs autosave files. TODO: generalize this
                if fnmatch(filename, "*.rst") and not fnmatch(filename, "*.#*"):
                    source_abspath = os.path.join(root, filename)
                    yield source_abspath


class Writer(object):
    """Write HTML fragments generated by docutils parser."""

    def __init__(self, config):
        #self.config = config
        self.path = Path(config)
        self.parser = Parser(config)

    def run(self):
        for source_abspath in self.parser.get_all_files():
            print source_abspath 
            fragment = self.parser.get_fragment(source_abspath)
            fragment_abspath = self.path.get_fragment_abspath(source_abspath)
            self.write_fragment(fragment, fragment_abspath)
        print "Done."

    def write_fragment(self, fragment, fragment_abspath):
        with self.open_fragment_file(fragment_abspath) as fout:
            fout.write(fragment.encode('utf-8') + '\n')
 
    def open_fragment_file(self, fragment_abspath):
        self.make_fragment_dir(fragment_abspath)
        return open(fragment_abspath, "w")

    def make_fragment_dir(self, fragment_abspath):
        fragment_dir = os.path.dirname(fragment_abspath)
        if not os.path.isdir(fragment_dir):
            os.makedirs(fragment_dir)


class Loader(object):
    """Load blog entries into Neo4j."""

    def __init__(self, config, graph):
        #self.changelog = ChangeLog(config)
        self.path = Path(config)

        changelog_dir = self.path.get_working_etc()
        self.changelog = ChangeLog(changelog_dir)
        self.changelog.initialize(config)

        self.parser = Parser(config)
        self.graph = graph

    def changelog_exists(self):
        return self.changelog.exists()

    def update_entries(self):
        if self.changelog_exists():
            print "UPDATING CHANGED"
            self.update_changed_entries()
        else:
            print "UPDATING ALL"
            self.update_all_entries()

    def update_all_entries(self):
        for source_abspath in self.parser.get_all_files():
            self.update_entry(source_abspath)

    def update_changed_entries(self):
        update_count = 0

        data = self.changelog.data

        if data is None:
            return update_count

        last_updated = self.get_last_updated()

        # Data is an OrderedDict, most recent changes last
        for source_path in reversed(data):
            status, timestamp = data[source_path]
            if self.old_timestamp(timestamp, last_updated):
                break
            source_abspath = self.path.get_source_abspath(source_path)
            update_count += self.update_entry(source_abspath)

        return update_count

    def old_timestamp(self, timestamp, last_updated):
        # Timestamps with a time before the last_updated time 
        # were updated during the previous push
        return (timestamp <= last_updated)
        
    def update_entry(self, source_abspath):
        data = self.parser.get_data(source_abspath)
        fragment_abspath = self.path.get_fragment_abspath(source_abspath)
        if os.path.exists(fragment_abspath) is False:
            print "WARNING: Fragment Not Found", fragment_abspath
            return False
        # TODO: remove entry if fragment doesn't exist
        entry = self.graph.entries.save(data)
        return True

    def set_last_updated(self, last_updated):
        # Metadata methods are Neo4j-only right now
        self.graph.set_metadata("entries:last_updated", last_updated)

    def get_last_updated(self):
        # Metadata methods are Neo4j-only right now
        result = self.graph.get_metadata("entries:last_updated")
        last_updated = result.raw
        return last_updated
        


