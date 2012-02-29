from source import Source
from fragment import Fragment


class Builder(object):
    def __init__(self, config):
        self.source = Source(config)
        self.fragment = Fragment(config)


    def build(self, source_path, build_path):
        key = self.fragment.is_new(build_path) and 'A' or 'U'
        data = self.source.get_data(source_path)
        fragment = data['fragment']
        with self.fragment.open_destination_file(build_path) as fout:
            fout.write(fragment.encode('utf-8') + '\n')
        print key, build_path
        return data

    def run(self):
        for source_file in self.source.get_all_files():
            print source_file
            slug = self.source.get_slug(source_file)
            build_path = self.fragment.get_build_path(slug)
            if self.fragment.needs_build(source_file, build_path):
                self.build(source_file, build_path)
        print "Done."
        
