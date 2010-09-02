
import os
import psycopg2

def connect(dbname, bypass=False):
    """
    Generate a psycopg2 database connection
    """
    dbhost = 'iemdb'
    dbuser = os.environ['USER']
    if dbuser == 'akrherz' and not bypass:
        dbhost = 'localhost'
    if dbuser == 'akrherz' and bypass:
        dbuser = 'nobody'
    return psycopg2.connect(database=dbname, host=dbhost, user=dbuser)
