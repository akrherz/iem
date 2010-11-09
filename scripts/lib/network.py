# Class to hold metadata about a network

import iemdb
import psycopg2.extras

class Table(object):

    def __init__(self, network):
        """
        Construct with either a single network, or list of networks
        """
        self.sts = {}
        
        dbconn = iemdb.connect('mesosite', bypass=True)
        cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if type(network) == type("A"):
            network = [network,]
        for n in network:
            cursor.execute("""SELECT *, x(geom) as lon, y(geom) as lat
                from stations WHERE network = %s""", (n,))
            for row in cursor:
             
                self.sts[ row['id'] ] = row
        cursor.close()
        dbconn.close()
