# Class to hold metadata about a network

import pg

class Table(object):

    def __init__(self, network):
        """
        Construct with either a single network, or list of networks
        """
        self.sts = {}
        dbconn = pg.connect("mesosite", "iemdb", user="nobody")
        if type(network) == type("A"):
            network = [network,]
        for n in network:
            rs = dbconn.query("""SELECT *, x(geom) as lon, y(geom) as lat
                from stations WHERE network = '%s'""" % (n,)).dictresult()
            for i in range(len(rs)):
                self.sts[ rs[i]['id'] ] = rs[i]
