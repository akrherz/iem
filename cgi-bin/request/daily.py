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
    s = "station,day,max_temp_f,min_temp_f,max_dewpoint_f,min_dewpoint_f\n"
    if len(stations) == 1:
        stations.append( 'ZZZZZ' )
    cursor.execute("""SELECT id, day, max_tmpf, min_tmpf, max_dwpf, min_dwpf 
        from summary s JOIN stations t on (t.iemid = s.iemid) WHERE
        s.day >= %s and s.day < %s and t.network = %s and t.id in %s""",
        (sts, ets, network, tuple(stations)))
    for row in cursor:
        s += "%s,%s,%s,%s,%s,%s\n" % (row[0], row[1], row[2], row[3], row[4],
                                      row[5]) 
    
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