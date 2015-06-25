# BSD Licensed, Copyright (c) 2006-2010 TileCache Contributors

from TileCache.Cache import Cache
import time
import memcache


class Memcached(Cache):

    def __init__(self, servers=['127.0.0.1:11211'], **kwargs):
        Cache.__init__(self, **kwargs)
        if type(servers) is str:
            servers = map(str.strip, servers.split(","))
        self.cache = memcache.Client(servers, debug=0)
        self.timeout = int(kwargs.get('timeout', 0))

    def getKey(self, tile):
        return "/".join(map(str, [tile.layer.name, tile.x, tile.y, tile.z]))

    def get(self, tile):
        key = self.getKey(tile)
        tile.data = self.cache.get(key)
        return tile.data

    def set(self, tile, data):
        if self.readonly:
            return data
        key = self.getKey(tile)
        self.cache.set(key, data, self.timeout)
        return data

    def delete(self, tile):
        key = self.getKey(tile)
        self.cache.delete(key)

    def attemptLock(self, tile):
        return self.cache.add(self.getLockName(tile), "0",
                              time.time() + self.timeout)

    def unlock(self, tile):
        self.cache.delete(self.getLockName(tile))
