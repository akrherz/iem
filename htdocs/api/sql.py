#!/usr/bin/env python
'''
 An attempt to make a RESTful'ish endpoint for direct SQL to iem
 
 Calling:
   /api/sql/database/afos
   /api/sql/database/afos/tables  # Get a description
 
'''
import psycopg2
import psycopg2.extras
import cgi
import json
import sys
import os

def sanitize( sql ):
    ''' Attempt to sanitize the input we get '''
    sql = sql.encode('ascii')
    if sql.find(';') > -1:
        return 'select 1'
    if sql.lower().find('delete') > -1:
        return 'select 1'
    if sql.lower().find('create') > -1:
        return 'select 1'
    return sql 

def main():
    ''' Do Stuff '''
    form = cgi.FieldStorage()
    database = form.getfirst('database')
    sql = sanitize( form.getfirst('sql') )
    res = {'results': [], 'database': database, 'sql': sql}

    dbconn = psycopg2.connect(database=database, user='apiuser', 
                              host='postgresread')
    cursor = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute( sql )
    res['rows'] = cursor.rowcount
    for row in cursor:
        res['results'].append( row )

    return res

if __name__ == '__main__':
    sys.stdout.write("Content-type: text/plain\r\n")
    if os.environ['REQUEST_METHOD'] == 'GET':
        try:
            res = main()
            sys.stdout.write("\r\n")
            sys.stdout.write( json.dumps(res) )
        except Exception, exp:
            sys.stdout.write("Status: 500 Internal Server Error: 500\r\n")
            sys.stdout.write("\r\n")
            sys.stderr.write( os.getenv("QUERY_STRING") )
            sys.stderr.write( repr(exp) )
            sys.stdout.write( json.dumps(
                                    {'ERROR': 'Error Encountered, sorry.'}))
    else:
        # ERRR
        pass