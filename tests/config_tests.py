
class ConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(project_dir)
        
    def test_init(self):
        assert self.config.project_dir == project_dir


        
