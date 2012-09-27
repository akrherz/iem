import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import mx.DateTime

sts = mx.DateTime.DateTime(2012,1,1)
ets = mx.DateTime.now()
interval = mx.DateTime.RelativeDateTime(days=14)
now = sts

while now < ets:
    ccursor.execute("""select station, 
    SQRT( sum((dhigh - chigh)^2 + (dlow - clow)^2)/count(*) ) as diff 
    from (select c.station, c.valid, d.high as dhigh, c.high as chigh, 
    d.low as dlow, c.low as clow from ncdc_climate71 c JOIN alldata_ia d 
    on (d.sday = to_char(c.valid, 'mmdd')) WHERE d.station = 'IA2203' 
    and d.day BETWEEN '%s'::date and '%s'::date + '14 days'::interval) as foo 
    GROUP by station ORDER by diff ASC LIMIT 1""" % (now.strftime("%Y-%m-%d"),
                                             now.strftime("%Y-%m-%d")))
    row = ccursor.fetchone()
    ccursor.execute("""SELECT name, state from stations where
    id = '%s'""" % (row[0].upper(),))
    row2 = ccursor.fetchone()
    
    print '%s-%s %s, %s' % (now.strftime("%d %b"),
                     (now + mx.DateTime.RelativeDateTime(days=14)).strftime("%d %b"),
                     row2[0].capitalize(), row2[1])
    
    now += interval