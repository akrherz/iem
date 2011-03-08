# A minimal implementation of an MBTiles-formatted SQLite database 
# cache access mechanism. (No writing, only reading.)
# See:
#  http://mapbox.com/tools/mbtiles 
# for more information on the mbtiles format; it is essentially a single 
# table in a sqlite database with 4 columns:
#  * tile_column
#  * tile_row
#  * zoom_level
#  * tile_data

from TileCache.Cache import Cache
import os
import sqlite3

class MBTiles (Cache):
    def __init__ (self, base = None, ext = None, umask = '002', **kwargs):
        Cache.__init__(self, **kwargs)
        self.basedir = base
        self.ext = ext
        
    def get (self, tile):
        db = sqlite3.connect("%s.%s" % (os.path.join(self.basedir, tile.layer.name), self.ext))
        c = db.cursor()
        c.execute("select tile_data from tiles where tile_column=? and tile_row=? and zoom_level=?", (tile.x, tile.y, tile.z))
        res = c.fetchone()
        if res:
            tile.data = str(res[0])
            return tile.data
        return None
