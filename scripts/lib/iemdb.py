
import os
import psycopg2

def connect(dbname):
    """
    Generate a psycopg2 database connection
    """
    dbhost = 'iemdb'
    if os.environ['USER'] == 'akrherz':
        dbhost = 'localhost'
    return psycopg2.connect(database=dbname, host=dbhost)
