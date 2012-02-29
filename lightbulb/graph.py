from logging import DEBUG
from bulbs.neo4jserver import Graph as Neo4jGraph
from bulbs.utils import get_file_path

from cache import Cache
from model import Person, Entry, Topic, Tagged, Author, Meta


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

        
        
