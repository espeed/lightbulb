import os
import sys

from .builder import Builder
from .config import Config


def main():
    if len(sys.argv) not in (1, 2):
        print >> sys.stderr, 'usage: lightbulb <folder>'

    if len(sys.argv) >= 2:
        folder = sys.argv[2]
    else:
        folder = os.getcwd()

    config = Config(folder)
    builder = Builder(config)

    builder.run()



