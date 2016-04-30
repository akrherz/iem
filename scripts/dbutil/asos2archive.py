"""
 Dump ASOS observations into the long term archive...

 Database partitioning is now based on the UTC day, so we need to make sure
 we are not inserting where we should not be...

 This script copies from the iem->current_log database table to the asos
 database.  This data is a result of the pyWWA/metar_parser.py process

 We run in two modes, once every hour to copy over the Iowa data and once
 at midnight to copy the previous UTC's days worth of METAR data over

"""
import datetime
import sys
import pytz
import psycopg2.extras

ASOS = psycopg2.connect(database='asos', host='iemdb')
IEM = psycopg2.connect(database='iem', host='iemdb')
acursor = ASOS.cursor()
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Set ourselves back one hour as when we run at 10 after as we don't
# want to miss data when we run at 00:10 UTC
utc = datetime.datetime.utcnow() - datetime.timedelta(minutes=60)
utc = utc.replace(tzinfo=pytz.timezone("UTC"), minute=59, second=0,
                  microsecond=0)

sts = utc.replace(hour=0, minute=0)

# Option 1 is to run for 'today' and for Iowa data
if len(sys.argv) > 1:
    ets = utc
    networks = "(network = 'IA_ASOS' or network = 'AWOS')"
# Option 2 is to run for 'yesterday' and for the entire archive
else:
    sts = sts.replace(minute=0) - datetime.timedelta(days=1)
    ets = sts.replace(hour=23, minute=59)
    networks = "(network ~* 'ASOS' or network ~* 'AWOS')"

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE valid >= '%s' and valid <= '%s'" % (sts.year,
                                                                 sts, ets)
acursor.execute(sql)

# delete dups from current_log
icursor.execute("""
with data as (
    select c.oid,
    row_number() OVER (PARTITION by c.iemid, valid ORDER by length(raw) ASC)
    from current_log c JOIN stations t on (c.iemid = t.iemid)
    where network ~* 'ASOS' and valid >= %s and valid <= %s)

 DELETE from current_log c USING data d WHERE c.oid = d.oid
 and d.row_number > 1""", (sts, ets))
icursor.close()
IEM.commit()
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Get obs from Access
sql = """SELECT c.*, t.network, t.id from
    current_log c JOIN stations t on (t.iemid = c.iemid) WHERE
    valid >= %s and valid <= %s and """+networks+"""
    """
args = (sts, ets)
icursor.execute(sql, args)
for row in icursor:
    sql = """INSERT into t""" + repr(sts.year) + """ (station, valid, tmpf,
    dwpf, drct, sknt,  alti, p01i, gust, vsby, skyc1, skyc2, skyc3, skyc4,
    skyl1, skyl2, skyl3, skyl4, metar, p03i, p06i, p24i, max_tmpf_6hr,
    min_tmpf_6hr, max_tmpf_24hr, min_tmpf_24hr, mslp, presentwx)
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    args = (row['id'], row['valid'], row['tmpf'],
            row['dwpf'], row['drct'], row['sknt'], row['alti'],
            row['phour'], row['gust'], row['vsby'], row['skyc1'], row['skyc2'],
            row['skyc3'], row['skyc4'], row['skyl1'], row['skyl2'],
            row['skyl3'], row['skyl4'], row['raw'], row['p03i'], row['p06i'],
            row['p24i'], row['max_tmpf_6hr'], row['min_tmpf_6hr'],
            row['max_tmpf_24hr'], row['min_tmpf_24hr'], row['mslp'],
            row['presentwx'])

    acursor.execute(sql, args)

if icursor.rowcount == 0:
    print '%s - %s Nothing done for asos2archive.py?' % (sts, ets)

icursor.close()
IEM.commit()
ASOS.commit()
ASOS.close()
IEM.close()
