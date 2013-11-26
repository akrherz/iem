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
import decimal

# http://stackoverflow.com/questions/1960516/python-json-serialize-a-decimal-object
class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)

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
        res['results'].append( dict(row) )

    return res

if __name__ == '__main__':
    sys.stdout.write("Content-type: text/plain\r\n")
    if os.environ['REQUEST_METHOD'] == 'GET':
        try:
            res = main()
            sys.stdout.write("\r\n")
            sys.stdout.write( json.dumps(res, cls=DecimalEncoder) )
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