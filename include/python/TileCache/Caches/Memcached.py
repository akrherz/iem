"""Memcached Caching Provider
BSD Licensed, Copyright (c) 2006-2010 TileCache Contributors
"""
import time

from six import string_types
import memcache
from TileCache.Cache import Cache


class Memcached(Cache):
    """Implements a cache"""

    def __init__(self, servers="127.0.0.1:11211", **kwargs):
        """Constructor"""
        Cache.__init__(self, **kwargs)
        if isinstance(servers, string_types):
            servers = [s.strip() for s in servers.split(",")]
        self.cache = memcache.Client(servers, debug=0)
        self.timeout = int(kwargs.get("timeout", 0))

    def getKey(self, tile):
        """Get the key for this tile"""
        return "/".join(map(str, [tile.layer.name, tile.x, tile.y, tile.z]))

    def get(self, tile):
        """Get the cache data"""
        key = self.getKey(tile)
        tile.data = self.cache.get(key)
        return tile.data

    def set(self, tile, data):
        """Set the cache data"""
        if self.readonly:
            return data
        key = self.getKey(tile)
        self.cache.set(key, data, self.timeout)
        return data

    def delete(self, tile):
        """Delete a tile from the cache"""
        key = self.getKey(tile)
        self.cache.delete(key)

    def attemptLock(self, tile):
        """Attempt to lock the cache for a tile"""
        return self.cache.add(
            self.getLockName(tile), "0", time.time() + self.timeout
        )

    def unlock(self, tile):
        """Attempt to unlock the cache for a tile"""
        self.cache.delete(self.getLockName(tile))
