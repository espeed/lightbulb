# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

#
# Bulbs Config
#
from bulbs.neo4jserver import NEO4J_URI
from bulbs.config import Config as BulbsConfig, DEBUG

bulbs_config = BulbsConfig(NEO4J_URI)
bulbs_config.set_logger(DEBUG)
bulbs_config.set_neo4j_heroku()

graph = Graph(bulbs_config)


#
# Lightbulb Stuff
#
from lightbulb import Graph, Config
from lightbulb.utils import cache_author

config = Config()
cache_author(graph, config)

