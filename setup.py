"""
Lightbulb
---------

A Git-Powered, Neo4j-Backed Python Blog Engine for Heroku.

"""
import sys
from setuptools import Command, setup, find_packages

#from ez_setup import use_setuptools
#use_setuptools()

class run_audit(Command):
    """Audits source code using PyFlakes for following issues:
       - Names which are used but not defined or used before they are defined.
       - Names which are redefined without having been used.
    """
    description = "Audit source code with PyFlakes"
    user_options = []

    def initialize_options(self):
        all = None

    def finalize_options(self):
        pass

    def run(self):
        import os, sys
        try:
            import pyflakes.scripts.pyflakes as flakes
        except ImportError:
            print("Audit requires PyFlakes installed in your system.")
            sys.exit(-1)

        dirs = ['lightbulb', 'tests']
        # Add example directories
        #for dir in ['blog',]:
        #    dirs.append(os.path.join('examples', dir))
        # TODO: Add test subdirectories
        warns = 0
        for dir in dirs:
            for filename in os.listdir(dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    warns += flakes.checkPath(os.path.join(dir, filename))
        if warns > 0:
            print(("Audit finished with total %d warnings." % warns))
        else:
            print("No problems found in sourcecode.")

# Run tests from inside the tests dir
def run_tests():
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
    from lightbulb_tests import suite
    return suite()

setup (
    name = 'lightbulb',
    version = '0.1d',
    url = 'http://bulbflow.com',
    license = 'BSD',
    author = 'James Thornton',
    author_email = 'james@jamesthornton.com',
    description = 'A Git-Powered, Neo4j-Backed Blog Engine for Heroku.',
    long_description = __doc__,
    keywords = "blog engine graph database DB persistence framework rexster gremlin cypher neo4j orientdb",   
    packages = find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
#    install_requires=['docutils', 'pygments', 'beaker', 'bulbs', 'pyyaml', 'ez_setup', 'titlecase'],
    install_requires=['docutils', 'pygments', 'beaker', 'bulbs', 'pyyaml'],

    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        ],
    cmdclass={'audit': run_audit},
    test_suite='__main__.run_tests',
    entry_points = {
        'console_scripts': ['lightbulb = lightbulb.command:main'],
    },
)
