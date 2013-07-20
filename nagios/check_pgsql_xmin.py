"""
Return the maximum xmin in the database 
"""
import os
import sys
import stat
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

def check():
    icursor.execute("""
    SELECT datname, age(datfrozenxid) FROM pg_database
    ORDER by age DESC LIMIT 1
    """)
    row = icursor.fetchone()

    return row
    
if __name__ == '__main__':
    dbname, count = check()
    if count < 201000000:
        print 'OK - %s %s |count=%s;201000000;215000000;220000000' % (count, 
                                                            dbname, count)
        sys.exit(0)
    elif count < 215000000:
        print 'WARNING - %s %s |count=%s;201000000;215000000;220000000' % (count, 
                                                            dbname, count)
        sys.exit(1)
    else:
        print 'CRITICAL - %s %s |count=%s;201000000;215000000;220000000' % (count, 
                                                            dbname, count)
        sys.exit(2)