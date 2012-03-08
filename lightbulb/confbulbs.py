from bulbs.neo4jserver import NEO4J_URI
from bulbs.config import Config as BulbsConfig, DEBUG
from lightbulb import Graph, Config
from lightbulb.utils import cache_author

#
# Bulbs Config File
#

bulbs_config = BulbsConfig(NEO4J_URI)
bulbs_config.set_logger(DEBUG)
bulbs_config.set_neo4j_heroku()

graph = Graph(bulbs_config)

#
# Lightbulb Stuff
#

cache_author(graph, Config())

