"""
Harry Hillaker kindly provides a monthly file of his QC'd COOP observations
This script processes them into something we can insert into the IEM database
"""
import sys
import re
import datetime
import string
import psycopg2
import pandas as pd

pgconn = psycopg2.connect(database='coop', host='iemdb')
cursor = pgconn.cursor()

"""
This is not good, but necessary.  We translate some sites into others, so to
maintain a long term record.
"""
stconv = {'IA6199': 'IA6200',  # Oelwein
          'IA3288': 'IA3290',  # Glenwood
          'IA4963': 'IA8266',  # Lowden becomes Tipton
          'IA7892': 'IA4049',  # Stanley becomes Independence
          'IA0214': 'IA0213',  # Anamosa
          'IA2041': 'IA3980',  # Dakota City becomes Humboldt
          }

year = int(sys.argv[1])
month = int(sys.argv[2])


def f(val):
    return float(val) if val is not None else None

fn = "/mesonet/data/harry/%s/SCIA%s%02i.txt" % (year, str(year)[2:], month)
print "Processing File: ", fn

lines = open(fn, 'r').readlines()

rows = []
hits = 0
misses = 0
for linenum, line in enumerate(lines):
    tokens = re.split(",", line.replace('"', ""))
    if len(tokens) < 15 or len(tokens[2]) != 4:
        misses += 1
        continue
    if len(tokens[0]) == 0 or tokens[2] == 'YR' or tokens[0] == 'YR':
        continue
    stid = tokens[0]
    dbid = "%s%04.0f" % ("IA", int(stid))
    dbid = stconv.get(dbid, dbid)
    yr = int(tokens[2])
    mo = int(tokens[3])
    dy = int(tokens[4])
    hi = string.strip(tokens[6])
    lo = string.strip(tokens[8])
    pr = string.strip(tokens[12])
    sf = string.strip(tokens[14])
    sd = string.strip(tokens[16])
    if pr == "T":
        pr = 0.0001
    if sf == "T":
        sf = 0.0001
    if sd == "T":
        sd = 0.0001
    if sf == "M":
        sf = ""
    if sd == "M":
        sd = ""
    if hi == "M":
        hi = ""
    if lo == "M":
        lo = ""
    if pr in ["M", "C", "*", "?"]:
        pr = None
    if sf in ["M", "C", "*", "?"]:
        sf = None

    if sf == "":
        sf = 0
    if sd == "":
        sd = 0
    if pr == "":
        pr = 0
    if hi == "":
        hi = None
    if lo == "":
        lo = None

    try:
        ts = datetime.date(yr, mo, dy)
    except:
        print("timefail yr:%s mo:%s dy:%s linenum:%s" % (yr, mo, dy, linenum))
        sys.exit()
    cursor.execute("""SELECT high, low, precip, snow, snowd from alldata_ia
    WHERE station = %s and day = %s""", (dbid, ts))
    if cursor.rowcount == 0:
        print("ERROR: missing %s %s" % (dbid, ts))
        cursor.execute("""INSERT INTO alldata_ia
            (station, day, sday, year, month)
            VALUES (%s, %s, %s, %s, %s)
            """, (dbid, ts, ts.strftime("%m%d"), ts.year, ts.month))
    else:
        row = cursor.fetchone()
        rows.append(dict(ehi=row[0], hi=f(hi), elo=row[1], lo=f(lo),
                         epr=row[2], pr=f(pr), esf=row[3], sf=f(sf),
                         esd=row[4], sd=f(sd), day=ts, station=dbid))

    cursor.execute("""
        UPDATE alldata_ia SET high = %s, low= %s, precip = %s, snow = %s,
        snowd = %s WHERE station = %s and day = %s RETURNING high
        """, (hi, lo, pr, sf, sd, dbid, ts))
    if cursor.rowcount != 1:
        print("ERROR: update not==1, %s %s cnt:%s" % (dbid, ts,
                                                      cursor.rowcount))
    hits += 1

print '    got %s good lines %s bad lines' % (hits, misses)

print(('V %5s %5s %5s %5s %6s %6s %4s %6s %6s %4s'
       ) % ('Est', 'HH', 'Bias', 'STD', '+Dif', 'station', 'date', '-Dif',
            'station', 'date'))
df = pd.DataFrame(rows)
details = ""
for v in ['hi', 'lo', 'pr', 'sf', 'sd']:
    df['diff_'+v] = df['e'+v] - df[v]
    sortdesc = df.sort('diff_'+v, ascending=False)
    smax = sortdesc.index[0]
    sortasc = df.sort('diff_'+v, ascending=True)
    smin = sortasc.index[0]

    print(("%s %5.2f %5.2f %5.2f %5.2f %6.2f %6s %8s %6.2f %6s %8s"
           ) % (v, df['e'+v].mean(), df[v].mean(),
                df['e'+v].mean() - df[v].mean(), df['diff_'+v].std(),
                df['diff_'+v][smax], df['station'][smax],
                df['day'][smax].strftime("%m%d"), df['diff_'+v][smin],
                df['station'][smin], df['day'][smin].strftime("%m%d"))
          )
    details += "---------------------------------------------------\n"
    for i in sortdesc.index[:5]:
        details += ("%s %s %s %6.2f -> %6.2f (%6.2f)\n"
                    ) % (v, df['station'][i], df['day'][i].strftime("%m%d"),
                         df['e'+v][i], df[v][i], df['diff_'+v][i])
    for i in sortasc.index[:5]:
        details += ("%s %s %s %6.2f -> %6.2f (%6.2f)\n"
                    ) % (v, df['station'][i], df['day'][i].strftime("%m%d"),
                         df['e'+v][i], df[v][i], df['diff_'+v][i])

print details


cursor.close()
pgconn.commit()
