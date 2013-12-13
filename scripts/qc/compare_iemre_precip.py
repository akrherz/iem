'''
 Look into daily precip coming from IEMRE to compare with other stuff
'''
import urllib2
import json
import network
import datetime

nt = network.Table("NDCLIMATE")
sid = 'ND5988'

data = {}

web = urllib2.urlopen(('http://mesonet.agron.iastate.edu/iemre/multiday/'+
                '2013-05-01/2013-07-01/%s/%s/json') % (nt.sts[sid]['lat'],
                                                       nt.sts[sid]['lon']))
j = json.load(web)

for row in j['data']:
    ts = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
    data[ts.date()] = {'daily_precip_in': float(row['daily_precip_in']),
                       'mrms_precip_in': float(row['mrms_precip_in'])}
    
import psycopg2
COOP = psycopg2.connect(database='coop', host='mesonet.agron.iastate.edu',
                        user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT day, precip from alldata_nd where
 station = %s and day >= '2013-05-01' and day < '2013-07-01' ORDER by day ASC""",
  (sid,))

for row in cursor:
    print '%s %5.2f %5.2f %5.2f' % (row[0], row[1], 
                                    data[row[0]]['daily_precip_in'],
                                    data[row[0]]['mrms_precip_in'])