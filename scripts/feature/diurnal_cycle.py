import numpy
total = numpy.zeros( (12,24), 'f')
cnt = numpy.zeros( (12,24), 'f')

import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor.execute("SET TIME ZONE 'GMT'")

acursor.execute("""SELECT a.valid + '10 minutes'::interval, a.tmpf - b.min from
    (SELECT valid, tmpf, date(valid) as d from alldata 
     WHERE station = 'AMW' and tmpf is not null) as a,
    (SELECT date(valid + '10 minutes'::interval) as d, max(tmpf), min(tmpf) from alldata
     WHERE station = 'AMW' and tmpf is not null GROUP by d) as b 
    WHERE b.d = a.d""")

for row in acursor:
    total[ row[0].month-1, row[0].hour-1] += row[1]
    cnt[ row[0].month-1, row[0].hour-1] += 1.0
    
print 'HR %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s ' % ('JAN', 'FEB',
                                        'MAR', 'APR', 'MAY', 'JUN', 'JUL',
                                        'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
for hr in range(24):
    print '%02i %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f ' % (
        hr, total[0,hr] / cnt[0,hr], total[1,hr] / cnt[1,hr], total[2,hr] / cnt[2,hr],
        total[3,hr] / cnt[3,hr], total[4,hr] / cnt[4,hr], total[5,hr] / cnt[5,hr],
        total[6,hr] / cnt[6,hr], total[7,hr] / cnt[7,hr], total[8,hr] / cnt[8,hr],
        total[9,hr] / cnt[9,hr], total[10,hr] / cnt[10,hr], total[11,hr] / cnt[11,hr] )
    