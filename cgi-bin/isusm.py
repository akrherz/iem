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

def get_currents():
    ''' Return dict of current values '''
    dbconn = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
    cursor = dbconn.cursor()
    data = {}
    cursor.execute("""
    SELECT station, valid, tair_c_avg from sm_hourly where
    valid = (SELECT max(valid) from sm_hourly where valid < now() and
    valid > now() - '24 hours'::interval)
    """)
    for row in cursor:
        data[ row[0] ] = {'airtemp': temperature(row[2], 'C'),
                          'valid': row[1]}
    
    cursor.close()
    dbconn.close()
    return data

def plot(data):
    ''' Actually plot this data '''
    nt = network.Table("ISUSM")
    lats = []
    lons = []
    vals = []
    valid = None
    for sid in data.keys():
        lats.append( nt.sts[sid]['lat'] )
        lons.append( nt.sts[sid]['lon'] )
        vals.append( data[sid]['airtemp'].value("F") )
        valid = data[sid]['valid']

    m = MapPlot(sector='iowa', title='ISU Soil Moisture Network Current Air Temp F',
                subtitle='valid %s' % (valid.strftime("%-d %B %Y %I:%M %p"),),
                figsize=(8,6))
    m.plot_values(lons, lats, vals, '%.1f')
    m.drawcounties()
    m.postprocess(web=True)

if __name__ == '__main__':
    ''' Do something '''
    data = get_currents()
    plot(data)