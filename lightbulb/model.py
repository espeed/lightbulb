# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from logging import DEBUG
from beaker.cache import Cache as BeakerCache

from bulbs.neo4jserver import Graph as Neo4jGraph
from bulbs.model import Node, NodeProxy, Relationship, build_data
from bulbs.property import String, Integer, DateTime
from bulbs.utils import extract, get_file_path


cache = BeakerCache("lightbulb")


# Relationships

class Author(Relationship):

    label = "author"


class Tagged(Relationship):

    label = "tagged"


# Nodes

class Person(Node):

    element_type = "person"

    # unique, index (assume all index, and index=False)

    name =  String(nullable=False)
    username = String(nullable=False)  


class Topic(Node):
    
    element_type = "topic"

    name = String(nullable=False)


# Sepcial model for storing metadata        
class Meta(Node):
    
    element_type = "lightbulb_meta"
    
    last_updated = DateTime()


class Entry(Node):
    
    element_type = "blog_entry"
    
    title = String(nullable=False)
    subtitle = String()
    docid = String(nullable=False)
    slug = String(nullable=False)
    date = DateTime(nullable=False) 
    source_path = String(nullable=False) 
    fragment_path = String(nullable=False)  
    view_count = Integer(default=0, nullable=False)
    
    @classmethod 
    def get_proxy_class(cls):
        return EntryProxy

    def _save(self, _data, kwds):
        script = self._client.scripts.get('save_blog_entry')
        params = self._get_params(_data, kwds)
        result = self._client.gremlin(script, params).one()        
        self._initialize(result)

    def _get_params(self, _data, kwds):
        params = dict()

        # Get the property data, regardless of how it was entered
        data = build_data(_data, kwds)

        # Author
        author = data.pop('author')
        params['author_id'] = cache.get("username:%s" % author)
        
        # Topic Tags
        tags = (tag.strip() for tag in data.pop('tags').split(','))
        topic_bundles = []
        for topic_name in tags:
            bundle = Topic(self._client).get_bundle(name=topic_name)
            topic_bundles.append(bundle)
        params['topic_bundles'] = topic_bundles

        # Entry
        # clean off any extra kwds that aren't defined as an Entry Property
        desired_keys = self.get_property_keys()
        data = extract(desired_keys, data)
        params['entry_bundle'] = self.get_bundle(data)
        
        return params


class EntryProxy(NodeProxy):
    
    def save(self, _data=None, **kwds):
        node = self.element_class(self.client)
        node._save(_data, kwds)
        return node

    # Undefine standard methods; use save() instead.
    def create(self, _data=None, **kwds):
        return NotImplementedError

    def update(self, _id, _data=None, **kwds):
        return NotImplementedError


class Graph(Neo4jGraph):
    
    def __init__(self, config=None):
        super(Graph, self).__init__(config)
        
        # Node Proxies
        self.people = self.build_proxy(Person)
        self.entries = self.build_proxy(Entry)
        self.topics = self.build_proxy(Topic)
        self.lightbulb = self.build_proxy(Meta)

        # Relationship Proxies
        self.tagged = self.build_proxy(Tagged)
        self.author = self.build_proxy(Author)
        
        # Add our custom Gremlin-Groovy scripts
        scripts_file = get_file_path(__file__, "gremlin.groovy")
        self.scripts.update(scripts_file)

