#!/usr/bin/env python
'''
 Feature IEM summary data!
'''
import cgi
import datetime

import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

def get_data(network, sts, ets, stations=[]):
    ''' Go fetch data please '''
    s = ("station,network,valid,precip_in\n")
    if len(stations) == 1:
        stations.append( 'ZZZZZ' )
    cursor.execute("""SELECT station, network, valid, phour from 
        hourly WHERE
        valid >= %s and valid < %s and network = %s and station in %s
        ORDER by valid ASC""",
        (sts, ets, network, tuple(stations)))
    for row in cursor:
        s += "%s,%s,%s,%s\n" % (row[0], row[1], row[2], row[3]) 
    
    return s


if __name__ == '__main__':
    ''' run rabbit run '''
    form = cgi.FieldStorage()
    sts = datetime.date( int(form.getfirst('year1')), 
                         int(form.getfirst('month1')),
                         int(form.getfirst('day1')) )
    ets = datetime.date( int(form.getfirst('year2')), 
                         int(form.getfirst('month2')),
                         int(form.getfirst('day2')) )
    
    print 'Content-type: text/plain\n'
    stations = form.getlist('station[]')
    network = form.getfirst('network')[:12]
    print get_data(network, sts, ets, stations=stations)