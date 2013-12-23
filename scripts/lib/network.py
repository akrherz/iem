# Class to hold metadata about a network

import psycopg2
import psycopg2.extras

class Table(object):

    def __init__(self, network):
        """
        Construct with either a single network, or list of networks
        """
        self.sts = {}
        
        dbconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
        cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if type(network) == type("A"):
            network = [network,]
        for n in network:
            cursor.execute("""SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
                from stations WHERE network = %s ORDER by name ASC""", (n,))
            for row in cursor:
                self.sts[ row['id'] ] = {}
                for key in row.keys():
                    self.sts[ row['id'] ][key] = row[key]
        cursor.close()
        dbconn.close()
