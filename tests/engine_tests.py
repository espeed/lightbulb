# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import shutil
import unittest
import docutils
import docutils.core

from lightbulb import Config, Parser, Writer, Loader

current_dir = os.getcwd()
project_dir = "%s/project" % current_dir
source_dir = "%s/source" % project_dir
build_dir = "%s/build" % project_dir
source_abspath = "%s/lightbulb.rst" % source_dir
another_file = "%s/anotherdir/another-file.rst" % source_dir
fragment_abspath = "%s/lightbulb.html" % build_dir
another_abspath = "%s/anotherdir/another-file.html" % build_dir

title = "Lightbulb"
subtitle = "A Git-powered, Neo4j-backed blog engine for Heroku."
excerpt = "connecting things"
docid = "a9f3e47f0535431bb86a41abc38224bc"
author = "james"
date = "2012-02-29"
tags = "neo4j, python, bulbs, heroku"
slug = "lightbulb"
fragment_path = "build/%s.html" % slug
source_path = "source/lightbulb.rst"


class ConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(project_dir)
        
    def test_init(self):
        assert self.config.project_dir == project_dir
        

class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(project_dir)
        self.parser = Parser(self.config)
    
    def test_init(self):
        assert self.parser.config == self.config
        assert self.parser.source_dir == source_dir
        
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
        source_dir = self.parser.get_source_dir()
        assert source_dir == source_dir
        
    def test_get_source_path(self):
        source_path = self.parser.get_source_path(source_abspath)
        assert source_path == "source/lightbulb.rst"

    def test_get_fragment_abspath(self):
        fragment_abspath = self.parser.get_fragment_abspath(source_abspath)
        assert fragment_abspath == "%s/lightbulb.html" % build_dir

    def test_get_fragment_path(self):
        fragment_path = self.parser.get_fragment_path(source_abspath)
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
        self.config = Config(project_dir)
        self.writer = Writer(self.config)

    def test_init(self):
        assert self.writer.config == self.config

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
        fragment_abspath = self.writer.parser.get_fragment_abspath(source_abspath)

        self.writer.write_fragment(fragment, fragment_abspath)

        assert os.path.exists(fragment_abspath)

    def test_make_fragment_dir(self):
        shutil.rmtree(build_dir, True)
        assert not os.path.isdir(build_dir)

        fragment_abspath = self.writer.parser.get_fragment_abspath(source_abspath)

        self.writer.make_fragment_dir(fragment_abspath)

        fragment_dir = os.path.dirname(fragment_abspath)
        assert os.path.isdir(fragment_dir)


class LoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(project_dir)
        self.writer = Writer(self.config)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConfigTestCase))
    suite.addTest(unittest.makeSuite(ParserTestCase))
    suite.addTest(unittest.makeSuite(WriterTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
