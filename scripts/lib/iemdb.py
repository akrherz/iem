
import os
import psycopg2

def connect(dbname, bypass=False, dbhost='iemdb'):
    """
    Generate a psycopg2 database connection
    """
    dbuser = os.environ.get('USER', 'nobody')
    if dbuser == 'akrherz' and not bypass:
        return psycopg2.connect(database=dbname)
    if dbuser == 'akrherz' and bypass:
        dbuser = 'nobody'
        dbhost = 'mesonet.agron.iastate.edu'
    return psycopg2.connect(database=dbname, host=dbhost, user=dbuser)
