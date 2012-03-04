# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import time
import shutil
import unittest
import docutils
import docutils.core

from lightbulb import Config, Path, Parser, Writer, Loader, ChangeLog, Graph, cache

module_abspath = os.path.abspath(__file__)
working_dir = os.path.dirname(module_abspath)

project_dir = "%s/blog" % working_dir
source_dir = "%s/source" % project_dir
build_dir = "%s/build" % project_dir

source_abspath = "%s/lightbulb.rst" % source_dir
another_file = "%s/another-file.rst" % source_dir
fragment_abspath = "%s/lightbulb.html" % build_dir
another_abspath = "%s/another-file.html" % build_dir

title = "Lightbulb"
subtitle = "A Git-powered, Neo4j-backed blog engine for Heroku."
excerpt = "connecting things"
docid = "a9f3e47f0535431bb86a41abc38224bc"
author = "james"
date = "2012-02-29"
tags = "neo4j, python, bulbs, heroku"
slug = "lightbulb"

# relative from project folder
fragment_path = "build/%s.html" % slug
source_path = "source/lightbulb.rst"

config = Config(working_dir)
path = Path(config)
changelog_abspath = path.get_changelog_abspath()
repo_dir = path.get_repo_dir()

class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(working_dir)
        self.path = Path(self.config)
        self.parser = Parser(self.config)
    
    def test_init(self):
        assert self.parser.config == self.config
        #assert self.parser.source_dir == source_dir
        
    def test_get_fragment(self):
        fragment = self.parser.get_fragment(source_abspath)
        excerpt = "connecting things"
        assert excerpt in fragment
        
    def test_get_data(self):
        data = self.parser.get_data(source_abspath)
        assert data['title'] == title
        assert data['subtitle'] == subtitle
        assert excerpt in data['fragment'] 
        assert  data['docid'] == docid
        assert  data['author'] == author
        assert  data['date'] == date
        assert  data['tags'] == tags
        assert  data['slug'] == slug
        assert  data['fragment_path'] == fragment_path
        assert  data['source_path'] == source_path
        
    def test_get_document_source(self):
        source = self.parser.get_document_source(source_abspath)
        assert docid in source
        assert excerpt in source

    def test_get_document_parts(self):
        source = self.parser.get_document_source(source_abspath)
        parts = self.parser.get_document_parts(source)

        assert parts['title'] == title
        assert parts['subtitle'] == subtitle
        assert excerpt in parts['fragment'] 
                
    def test_get_substition_defintions(self):
        source = self.parser.get_substitution_definitions()
        assert "isopub" in source
        assert "en dash" in source
        assert "em dash" in source
        
    def test_read_source_file(self):
        source = self.parser.read_source_file(source_abspath)
        assert docid in source
        assert excerpt in source

    def test_get_slug(self):
        slug = self.parser.get_slug(source_abspath)
        assert slug == "lightbulb"

    def test_get_source_dir(self):
        source_dir = self.path.get_source_dir()
        assert source_dir == source_dir
        
    def test_get_source_path(self):
        source_path = self.path.get_source_path(source_abspath)
        assert source_path == "source/lightbulb.rst"

    def test_get_fragment_abspath(self):
        fragment_abspath = self.path.get_fragment_abspath(source_abspath)
        assert fragment_abspath == "%s/lightbulb.html" % build_dir

    def test_get_fragment_path(self):
        fragment_path = self.path.get_fragment_path(source_abspath)
        assert fragment_path == "build/lightbulb.html" 
        
    def test_get_metadata(self):
        source = self.parser.get_document_source(source_abspath)
        meta = self.parser._get_metadata(source, source_abspath)

        assert  meta['docid'] == docid
        assert  meta['author'] == author
        assert  meta['date'] == date
        assert  meta['tags'] == tags

    def test_process_standard_fields(self):
        source = self.parser.get_document_source(source_abspath)
        doctree = docutils.core.publish_doctree(source)
        docinfo = doctree.traverse(docutils.nodes.docinfo)
        meta = self.parser._process_standard_fields(docinfo)

        assert  meta['author'] == author
        assert  meta['date'] == date

    def test_process_custom_fields(self):
        source = self.parser.get_document_source(source_abspath)
        doctree = docutils.core.publish_doctree(source)
        docinfo = doctree.traverse(docutils.nodes.docinfo)
        meta = self.parser._process_standard_fields(docinfo)
        meta = self.parser._process_custom_fields(meta)
        
        assert 'docid' in meta.keys()
        assert 'tags' in meta.keys()

    def test_get_all_files(self):
        source_files = list(self.parser.get_all_files())
        
        assert source_abspath in source_files
        assert another_file in source_files


class WriterTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(working_dir)
        self.writer = Writer(self.config)

    #def test_init(self):
        #assert self.writer.config == self.config

    def test_run(self):
        shutil.rmtree(build_dir, True)
        assert not os.path.isdir(build_dir)

        self.writer.run()

        assert os.path.exists(fragment_abspath)
        assert os.path.exists(another_abspath)

    def test_write_fragment(self):
        shutil.rmtree(build_dir, True)
        assert not os.path.isdir(build_dir)

        fragment = self.writer.parser.get_fragment(source_abspath)
        fragment_abspath = self.writer.path.get_fragment_abspath(source_abspath)

        self.writer.write_fragment(fragment, fragment_abspath)

        assert os.path.exists(fragment_abspath)

        # Do it again so both fragments will exist for loader test
        another_fragment = self.writer.parser.get_fragment(another_file)
        another_fragment_abspath = self.writer.path.get_fragment_abspath(another_file)

        self.writer.write_fragment(another_fragment, another_fragment_abspath)

        assert os.path.exists(another_fragment_abspath)


    def test_make_fragment_dir(self):
        shutil.rmtree(build_dir, True)
        assert not os.path.isdir(build_dir)

        fragment_abspath = self.writer.path.get_fragment_abspath(source_abspath)

        self.writer.make_fragment_dir(fragment_abspath)

        fragment_dir = os.path.dirname(fragment_abspath)
        assert os.path.isdir(fragment_dir)


class LoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.config = Config(working_dir)
        self.changelog = ChangeLog(self.config)
        self.loader = Loader(self.graph, self.changelog, self.config)
        
        data = dict(username="james", name="James Thornton")
        james = self.graph.people.get_or_create("username", "james", data)
        cache.put('username:james', james.eid)        

        self.last_updated = int(time.time())

    def test_init(self):
        eid = cache.get('username:james')
        assert type(eid) == int

    def test_update_all(self):
        self.loader.update_all()

        entry1 = self.graph.entries.index.lookup(slug="lightbulb").next()
        assert entry1.title == title
        assert entry1.subtitle == subtitle

        # TODO: Index lookups like this "anotherdir/another-file" break on Neo4j 
        entry2 = self.graph.entries.index.lookup(slug="another-file").next()
        assert entry2.title == "Another Title"
        assert entry2.subtitle == "Another subtitle here."

    def test_update_changed(self):
        # TMP: Remove test repo and changelog
        self.changelog._execute("rm -rf %s" % repo_dir)
        self.changelog._execute("rm %s" % changelog_abspath)


        # Make sure we're not going to clobber someone's existing repo
        assert not os.path.isdir(repo_dir)
        assert not os.path.exists(changelog_abspath)

        now = int(time.time())
        self.loader.set_last_updated(now)
        time.sleep(2)
        
        # Create test repo and changelog
        self.changelog._execute("git init")
        self.changelog._execute("touch %s" % changelog_abspath)
        self.changelog._execute("git add .")
        
        self.changelog.update()

        self.changelog._execute("git commit -m test commit")

        # Changes need to be made
        update_count = self.loader.update_changed()
        assert update_count == 2

        # Remove test repo and changelog
        self.changelog._execute("rm -rf %s" % repo_dir)
        self.changelog._execute("rm %s" % changelog_abspath)


    def test_no_update(self):
        # TMP: Remove test repo and changelog
        self.changelog._execute("rm -rf %s" % repo_dir)
        self.changelog._execute("rm %s" % changelog_abspath)

        # Make sure we're not going to clobber someone's existing repo
        assert not os.path.isdir(repo_dir)
        assert not os.path.exists(changelog_abspath)

        # Create test repo and changelog
        self.changelog._execute("git init")
        self.changelog._execute("touch %s" % changelog_abspath)
        self.changelog._execute("git add .")

        self.changelog.update()

        self.changelog._execute("git commit -m test commit")

        time.sleep(2)
        now = int(time.time())
        self.loader.set_last_updated(now)

        # Changes need to be made
        update_count = self.loader.update_changed()
        assert update_count == 0

        # Remove test repo and changelog
        self.changelog._execute("rm -rf %s" % repo_dir)
        self.changelog._execute("rm %s" % changelog_abspath)

    def test_set_and_get_last_updated(self):
        self.loader.set_last_updated(self.last_updated)
        last_updated = self.loader.get_last_updated()

        assert last_updated == self.last_updated

def suite():
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(ConfigTestCase))
    suite.addTest(unittest.makeSuite(ParserTestCase))
    suite.addTest(unittest.makeSuite(WriterTestCase))
    suite.addTest(unittest.makeSuite(LoaderTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
