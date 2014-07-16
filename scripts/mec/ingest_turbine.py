'''
'''
import datetime
import subprocess
import psycopg2
import os

dbconn = psycopg2.connect(database='mec', host='192.168.0.23')
cursor = dbconn.cursor()

cursor.execute("""
  SELECT id, unitnumber from turbines
""")
xref = {}
for row in cursor:
    xref[ row[1] ] = row[0]

cols = {
 'Power': 'power',
 'Blade Picth': 'pitch',
 'Yaw': 'yaw',
 'Wind Speed': 'windspeed'
}

def do(turbine):
    data = {}
    fn = 'original_zips/PomeroyTurbine%s.csv' % (turbine,)
    if not os.path.isfile(fn):
        print 'Could not find %s, skipping' % (fn,)
        return
    turbineid = xref["%s" % (turbine,)]
    for i, line in enumerate(open(fn)):
        tokens = line.split(",")
        if i == 0:
            tokens[0] = tokens[0].replace('\xef\xbb\xbf', '')
        try:
            fmt = ' %m/%d/%Y %I:%M:%S %p'
            if len(tokens[1]) < 12:
                fmt = ' %m/%d/%Y'
            ts = datetime.datetime.strptime(tokens[1], fmt)
            if not data.has_key(ts):
                data[ts] = {}
            data[ts][ cols.get(tokens[0] ) ] = float(tokens[2])
        except Exception, exp:
            print '%s linenum %s fails %s %s!' % (fn, i, line.strip(), exp)

    print "%s (%s) had %s lines of data" % (fn, turbineid, i)

    o = open('insert.sql', 'w')
    o.write("COPY turbine_data_%s FROM STDIN WITH null 'null';\n" % (turbine,))

    for ts in data.keys():
        o.write( "\t".join( [str(x) for x in [turbineid, ts.strftime("%Y-%m-%d %H:%M:%S"),
          data[ts].get('power', 'null'), data[ts].get('pitch', 'null'),
          data[ts].get('yaw', 'null'), str(data[ts].get('windspeed', 'null'))+
          '\n' ]] ) )

    o.write('\.\n')
    o.close()

    subprocess.call("psql -f insert.sql -h 192.168.0.23 mec", shell=True)

for i in range(151,221):
    do(i)
