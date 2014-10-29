"""
 Look at the sources saved to the AFOS database and then whine about 
 sources we do not understand!
"""
from pyiem.network import Table as NetworkTable
import psycopg2
import datetime
import pytz

pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

nt = NetworkTable(["WFO", "RFC", "NWS", "NCEP", "CWSU", "WSO"])

def sample(source, ts):
    """ Print out something to look at """
    cursor2.execute("""
    SELECT pil, entered, wmo from products where
    entered >= %s and entered < %s and source = %s
    LIMIT 5
    """, (ts, ts+datetime.timedelta(hours=24), source))
    for row in cursor2:
        uri = 'http://mesonet.agron.iastate.edu/p.php?pid=%s-%s-%s-%s' %(
            (row[1].astimezone(pytz.timezone("UTC")).strftime("%Y%m%d%H%M"),
             source, row[2], row[0]))
        print('    %s' % (uri,))

def look4(ts):
    """ Let us investigate """
    cursor.execute("""SELECT source, count(*) from products
    WHERE entered >= %s and entered < %s and source is not null
    GROUP by source ORDER by count DESC""",
    (ts, ts+datetime.timedelta(hours=24)))
    for row in cursor:
        source = row[0]
        lookup = source[1:] if source[0] == 'K' else source
        if not nt.sts.has_key(lookup):
            print '%s %s' % (row[0], row[1])
            sample(source, ts)

def main():
    """ Go Main Go """
    ts = datetime.datetime.today() - datetime.timedelta(days=1)
    ts = ts.replace(hour=0,minute=0,second=0,microsecond=0)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    
    look4(ts)

if __name__ == '__main__':    
    # go
    main()