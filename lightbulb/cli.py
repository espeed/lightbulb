import os
import sys

from lightbulb.builder import Builder
from lightbulb.config import Config
# local config
#from config import Config

config = Config('http://bulbflow.com')
builder = Builder(config)

def main():
    if len(sys.argv) not in (1, 2, 3):
        print >> sys.stderr, 'usage: lightbulb <action> <folder>'

    if len(sys.argv) >= 2:
        action = sys.argv[1]
    else:
        action = 'build'

    if len(sys.argv) >= 3:
        folder = sys.argv[2]
    else:
        folder = os.getcwd()

    if action not in ('build', 'serve'):
        print >> sys.stderr, 'unknown action', action
    #builder = get_builder(folder)

    if action == 'build':
        builder.run()
    else:
        builder.debug_serve()


main()
