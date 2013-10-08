#!/usr/bin/env python
'''
 Generate various plots for ISUSM data
'''
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
sys.path.insert(0, '/home/akrherz/projects/pyIEM')

import psycopg2
import cgi
import network
from pyiem.datatypes import temperature
from pyiem.plot import MapPlot

CTX = {
    'tmpf': {'title': '2m Air Temperature [F]'},
    'rh': {'title': '2m Air Humidity [%]'},
    'high': {'title': "Today's High Temp [F]"},       
       
       }

def get_currents():
    ''' Return dict of current values '''
    dbconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = dbconn.cursor()
    dbconn2 = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
    cursor2 = dbconn2.cursor()
    data = {}
    cursor.execute("""
    SELECT id, valid, tmpf, relh from current c JOIN stations t on
    (t.iemid = c.iemid) WHERE valid > now() - '3 hours'::interval and
    t.network = 'ISUSM'
    """)
    valid = None
    for row in cursor:
        data[ row[0] ] = {'tmpf': row[2],
                          'rh': row[3],
                          'valid': row[1], 
                          'high': None}
        if valid is None:
            valid = row[1]
    
    # Go get daily values
    cursor2.execute("""SELECT station, tair_c_max from sm_daily
    where valid = %s
    """, (valid,))
    for row in cursor2:
        data[ row[0] ]['high'] = temperature(row[1], 'C').value('F')
        
    cursor.close()
    dbconn.close()
    return data

def plot(data, v):
    ''' Actually plot this data '''
    nt = network.Table("ISUSM")
    lats = []
    lons = []
    vals = []
    valid = None
    for sid in data.keys():
        if data[sid][v] is None:
            continue
        lats.append( nt.sts[sid]['lat'] )
        lons.append( nt.sts[sid]['lon'] )
        vals.append( data[sid][v] )
        valid = data[sid]['valid']

    if valid is None:
        m = MapPlot(sector='iowa', 
                title='ISU Soil Moisture Network :: %s' % (CTX[v]['title'],),
                figsize=(8.0,6.4) )
        m.plot_values([-95,], [41.99], ['No Data Found'], '%s', textsize=30)
        m.postprocess(web=True)
        return

    m = MapPlot(sector='iowa', 
                title='ISU Soil Moisture Network :: %s' % (CTX[v]['title'],),
                subtitle='valid %s' % (valid.strftime("%-d %B %Y %I:%M %p"),),
                figsize=(8.0,6.4))
    m.plot_values(lons, lats, vals, '%.1f')
    m.drawcounties()
    m.postprocess(web=True)

if __name__ == '__main__':
    ''' Do something '''
    form = cgi.FieldStorage()
    v = form.getfirst('v', 'tmpf')
    t = form.getfirst('t', '0')
    data = get_currents()
    plot(data, v)