from beaker.cache import Cache as BeakerCache


class Cache(object):

    def __init__(self, namespace="lightbulb"):
        self._cache = BeakerCache(namespace)

    def get(self, key, **kwds):
        return self._cache.get(key, **kwds)

    def put(self, key, value, **kwds):
        return self._cache.put(key, value, **kwds)
        
    def remove(self, key, **kwds):
        return self._cache.remove(key, **kwds)

    def clear(self):
        return self._cache.clear()



