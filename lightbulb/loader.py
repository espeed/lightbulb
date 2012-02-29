from source import Source

class Loader(object):

    def __init__(self, graph, changelog, config):
        self.graph = graph
        self.changelog = changelog
        self.config = config
        self.source = Source(self.config)

    def save(self):
        log = self.changelog.get()
        for filename in log:
            status, timestamp = log[filename]
            print status, filename, timestamp
            #data = self.builder.get_context(filename)
            #entry = self.graph.entries.create(data)
            #print entry.eid, entry.map()
          
    def update_all(self):
        for source_file in self.source.get_all_files():
            data = self.source.get_data(source_file)
            # TODO: if fragment exists...
            entry = self.graph.entries.save(data)
            print entry.eid, entry.map()

    def get_last_updated(self):
        # Get the lightbulb metadata node for entries
        meta = self.graph.lightbulb.get_or_create(name="entries")        
        return meta.get('last_updated')
       
    def set_last_updated(self, last_updated):
        # Get the lightbulb metadata node for entries
        meta = self.graph.lightbulb.get_or_create(name="entries")
        meta.last_updated = last_updated
        meta.save()


