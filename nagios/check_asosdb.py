'''
 Measure how fast the ASOS database is responding to queries for data!
'''
import os
import sys
import datetime
import psycopg2
IEM = psycopg2.connect(database='asos', host='iemdb', user='nobody')
icursor = IEM.cursor()

def check():
    year = str(datetime.datetime.now().year)
    icursor.execute("""
    SELECT count(*) from t"""+ year +""" WHERE station = 
    (select id from stations where network ~* 'ASOS' 
    ORDER by random() ASC LIMIT 1)
    """)
    row = icursor.fetchone()

    
if __name__ == '__main__':
    t0 = datetime.datetime.now()
    check()
    t1 = datetime.datetime.now()
    delta = (t1 - t0).seconds + float((t1 - t0).microseconds) / 1000000.0
    if delta < 5:
        print 'OK - %.3f |qtime=%.3f;5;10;15' % (delta, delta)
        sys.exit(0)
    elif delta < 10:
        print 'WARNING - %.3f |qtime=%.3f;5;10;15' % (delta, delta)
        sys.exit(1)
    else:
        print 'CRITICAL - %.3f |qtime=%.3f;5;10;15' % (delta, delta)
        sys.exit(2)