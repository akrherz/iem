import iemdb
import math
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
import network

nt = network.Table("IA_ASOS")

ids = nt.sts.keys()
ids.sort()
for sid in ids:
    acursor.execute("""select extract(year from valid + '4 months'::interval) as yr, sum(valid - lag) from (select valid, lag(valid) OVER (ORDER by valid ASC), tmpf from alldata where station = '%s') as foo WHERE tmpf <= 0 GROUP by yr ORDER by yr DESC""" % (sid,))
    d2014 = -99
    maxval = 0
    maxyear = 0
    minyear = 9999
    lmaxval = 0
    lmaxyear = 9999
    for row in acursor:
        delta = (row[1].days * 86400. + row[1].seconds) / 3600.0 
        if row[0] < minyear:
            minyear = row[0]
        if delta > maxval and row[0] < 2014:
            maxval = delta
            maxyear = row[0]
        if row[0] == 2014:
            d2014 = delta
        elif delta > d2014 and lmaxval == 0:
            lmaxval = delta
            lmaxyear = row[0]
        

    print "%s %-14.14s %.0f  %4.0f  [%3.0f %.0f-%.0f] [%3.0f  %.0f-%.0f]" % (sid, nt.sts[sid]['name'],
        minyear, d2014, lmaxval, lmaxyear-1, lmaxyear, maxval, maxyear-1, maxyear)
