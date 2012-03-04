import unittest

from changelog_tests import suite as changelog_suite
from engine_tests import suite as engine_suite


def suite():
    # This requires Neo4j Server is running
    
    suite = unittest.TestSuite()

    suite.addTest(changelog_suite())
    suite.addTest(engine_suite())

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
