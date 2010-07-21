# A bit smarter database connection thingy

import pg, os

def connect(name):
    """
    Connect to an iemdatabase with given name
    """
    dbhost = "iemdb"
    if os.environ["USER"] == "akrherz":
        dbhost = "localhost"
    return pg.connect(name, dbhost)
