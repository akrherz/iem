from pyiem.network import Table as NetworkTable
import psycopg2
import pandas as pd
from pyiem.datatypes import pressure, temperature
from pyiem.meteorology import heatindex
import urllib2
import datetime
import cStringIO


def two():
    nt = NetworkTable(["IA_ASOS"])
    sids = nt.sts.keys()
    sids.sort()
    for sid in sids:
        print '-------------------------------------------------------------'
        print((' Data Since: %s Station: [%s] %s'
               ) % (nt.sts[sid]['archive_begin'].year, sid,
                    nt.sts[sid]['name']))
        for hrs in range(12, 24*12 + 1, 24):
            uri = ("http://mesonet.agron.iastate.edu/plotting/auto/plot/42/"
                   "zstation:%s::network:IA_ASOS::month:9::dir:above::"
                   "threshold:70::hours:%s::dpi:100.csv") % (sid, hrs)
            data = urllib2.urlopen(uri).read()
            if data.strip() == "":
                continue
            cdata = cStringIO.StringIO()
            cdata.write(data)
            cdata.seek(0)
            df = pd.DataFrame.from_csv(cdata, index_col=False)
            df['total'] = df['days'] * 24 + df['hours']
            mysort = df.sort('total', ascending=False)
            found2015 = False
            for _, row in mysort.iterrows():
                ets = datetime.datetime.strptime(row['end'][:16],
                                                 '%Y-%m-%d %H:%M')
                sts = datetime.datetime.strptime(row['start'][:16],
                                                 '%Y-%m-%d %H:%M')
                if sts.year == 2015:
                    found2015 = True
            if len(df.index) == 1 and found2015:
                continue
            if len(df.index) == 10 and not found2015:
                continue
            maxline = True
            rank = 1
            found2015 = False
            for _, row in mysort.iterrows():
                ets = datetime.datetime.strptime(row['end'][:16],
                                                 '%Y-%m-%d %H:%M')
                sts = datetime.datetime.strptime(row['start'][:16],
                                                 '%Y-%m-%d %H:%M')
                if sts.year == 2015:
                    found2015 = True
                    print(('  %s. %s -> %s  %5.0f hours'
                           ) % (rank, sts.strftime("%d %b %Y %I:%M %p"),
                                ets.strftime("%d %b %Y %I:%M %p"),
                                (ets - sts).total_seconds() / 3600.0))
                    rank += 1
                    continue
                if maxline:
                    print(('  %s. %s -> %s  %5.0f hours'
                           ) % (rank, sts.strftime("%d %b %Y %I:%M %p"),
                                ets.strftime("%d %b %Y %I:%M %p"),
                                (ets - sts).total_seconds() / 3600.0))
                    maxline = False
                rank += 1
            if not found2015:
                print('  -- 2015 not in top 10 for site --')
            break
two()

def one():
    pgconn = psycopg2.connect(database='asos', host='localhost', port=5555,
                              user='nobody')
    cursor = pgconn.cursor()
    nt = NetworkTable(["IA_ASOS", "AWOS"])
    ids = nt.sts.keys()
    ids.sort()

    print """
    <table class="table table-condensed table-striped">
    <thead>
    <tr><th>ID</th><th>Station Name</th><th>3 Sep Peak Heat Index</th>
    <th>Last Highest</th><th>Date</th></tr>
    </thead>
    """

    bah = nt.sts.keys()

    for sid in ids:
        cursor.execute("""
        select valid, tmpf, dwpf from alldata where
        station = %s and extract(month from valid) = 9
        and dwpf is not null and tmpf > 84 and valid > '1990-01-01'
        ORDER by valid DESC
        """, (sid,))

        thisdate = [0, None, None, None]
        for _, row in enumerate(cursor):
            hdx = heatindex(temperature(row[1], 'F'),
                            temperature(row[2], 'F')).value('F')
            if row[0].strftime("%Y%m%d") == '20150903':
                if hdx > thisdate[0]:
                    thisdate = [hdx, row[0], row[1], row[2]]
                continue
            if thisdate[1] is None:
                break
            if hdx >= thisdate[0]:
                bah.remove(sid)
                print(('%s,%s,%.0f,(%.0f/%.0f),%.0f,(%.0f/%.0f),%s'
                       ) % (sid, nt.sts[sid]['name'],
                            thisdate[0], thisdate[2], thisdate[3],
                            hdx, row[1], row[2],
                            row[0].strftime("%d %b %Y %I:%M %p")))
                break
    print 'missed', bah
    print "</table>"
