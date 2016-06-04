"""
Monthly precip something
"""
from pyiem.network import Table as NetworkTable
import datetime
import psycopg2
import subprocess
import os
nt = NetworkTable("IA_COOP")
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

o = open('IEMNWSMPR.txt', 'w')
o.write("IEMNWSMPR\n")
o.write("IOWA ENVIRONMENTAL MESONET\n")
o.write("   NWS COOP STATION MONTH PRECIPITATION TOTALS\n")
o.write("   AS CALCULATED ON THE IEM SERVER ...NOTE THE OBS COUNT...\n")

now = datetime.datetime.now()
goodDay = now.strftime("%Y-%m-%d")
first_day = now.replace(day=1)
last_day = (first_day + datetime.timedelta(days=32)).replace(day=1)

# Now we load climatology
mrain = {}
ccursor.execute("""select station, sum(precip) as rain from climate WHERE
    extract(month from valid) = %s and extract(day from valid) <= %s
    GROUP by station""" % (now.month, now.day))
for row in ccursor:
    mrain[row[0]] = row[1]


o.write("   VALID FOR MONTH OF: %s\n\n" % (now.strftime("%d %B %Y").upper(),))
o.write("%-6s%-24.24s%9s%10s%11s%10s\n" % ('ID', 'STATION', 'REPORTS',
                                           'PREC (IN)', 'CLIMO2DATE', 'DIFF'))

icursor.execute("""
    SELECT id, count(id) as cnt,
    sum(CASE WHEN pday >= 0 THEN pday ELSE 0 END) as prectot
    from summary_""" + str(now.year) + """ s JOIN stations t
    on (t.iemid = s.iemid)
    WHERE day >= %s and day < %s
    and pday >= 0 and t.network = 'IA_COOP' GROUP by id
    """, (first_day, last_day))

d = {}
for row in icursor:
    thisStation = row[0]
    thisPrec = row[2]
    thisCount = row[1]
    if thisStation in nt.sts:
        d[thisStation] = {'prectot': thisPrec, 'cnt': thisCount}
        d[thisStation]["name"] = nt.sts[thisStation]['name']
        d[thisStation]["crain"] = mrain[nt.sts[thisStation]['climate_site']]

keys = d.keys()
keys.sort()

for k in keys:
    o.write(("%-6s%-24.24s%9.0f%10.2f%11.2f%10.2f\n"
             ) % (k, d[k]["name"], d[k]["cnt"], d[k]["prectot"], d[k]["crain"],
                  d[k]["prectot"] - d[k]["crain"]))


o.write(".END\n")
o.close()

subprocess.call(("/home/ldm/bin/pqinsert -p "
                 "'plot c 000000000000 text/IEMNWSMPR.txt bogus txt' "
                 "IEMNWSMPR.txt"), shell=True)

os.unlink("IEMNWSMPR.txt")
