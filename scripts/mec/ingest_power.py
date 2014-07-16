'''
'''
import datetime
import subprocess
import os

cols = {
 'Total Power': 'power',
 'Turbines Online': 'online_cnt',
}
data = {}

def do(fn):
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

    print "%s had %s lines of data" % (fn, i)

do('original_zips/ISU-PomeroyParkData.csv')
do('original_zips/ISU-PomeroyParkPower.csv')

def c(val):
    if val is None or val == 'null':
        return 'null'
    return int(val)

o = open('insert2.sql', 'w')
o.write("COPY farm_data FROM STDIN WITH null 'null';\n")

for ts in data.keys():
    o.write( "\t".join( [str(x) for x in [1, ts.strftime("%Y-%m-%d %H:%M:%S"),
          c(data[ts].get('online_cnt', 'null')), 
          str(data[ts].get('power', 'null'))+'\n' ]] ) )

o.write('\.\n')
o.close()

subprocess.call("psql -f insert2.sql -h 192.168.0.23 mec", shell=True)

