""" Process the sampled data into the database
"""
import datetime
import subprocess
import os
from pyiem.util import get_dbconn

dbconn = get_dbconn('mec', user='mesonet')
cursor = dbconn.cursor()

cursor.execute("""
  SELECT id, unitnumber from turbines
""")
xref = {}
for row in cursor:
    xref[ row[1] ] = row[0]

cols = {
 'Power': 'power',
 'Blade Pitch': 'pitch',
 'Yaw': 'yaw',
 'Wind Speed': 'windspeed'
}

def do(turbine):
    data = {}
    fn = '/tmp/PomeroyTurbine%s-Sampled.csv' % (turbine,)
    if not os.path.isfile(fn):
        print 'Could not find %s, skipping' % (fn,)
        return
    turbineid = xref["%s" % (turbine,)]
    for i, line in enumerate(open(fn)):
        tokens = line.split(",")
        try:
            fmt = '%m/%d/%Y %I:%M %p'
            ts = datetime.datetime.strptime(tokens[1], fmt)
            if not data.has_key(ts):
                data[ts] = {}
            data[ts][ cols.get(tokens[0] ) ] = float(tokens[2])
        except Exception, exp:
            print '%s linenum %s fails %s %s!' % (fn, i, line.strip(), exp)

    print "%s (%s) had %s lines of data" % (fn, turbineid, i)

    o = open('insert.sql', 'w')
    o.write("COPY tmp FROM STDIN WITH null 'null';\n")

    for ts in data.keys():
        o.write( "\t".join( [str(x) for x in [turbineid, ts.strftime("%Y-%m-%d %H:%M:%S"),
          data[ts].get('power', 'null'), data[ts].get('pitch', 'null'),
          data[ts].get('yaw', 'null'), str(data[ts].get('windspeed', 'null'))+
          '\n' ]] ) )

    o.write('\.\n')
    o.close()

    subprocess.call("psql -f insert.sql -h 127.0.0.1 -p 5555 mec", shell=True)

for i in range(1,2):
    do(i)
