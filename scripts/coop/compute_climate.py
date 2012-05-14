# Computes the Climatology and fills out the table!
import mx.DateTime
import iemdb
import psycopg2.extras
import network
import sys
nt = network.Table(("IACLIMATE", "MNCLIMATE", "NDCLIMATE", "SDCLIMATE",
  "NECLIMATE", "KSCLIMATE", "MOCLIMATE", "ILCLIMATE", "WICLIMATE",
  "MICLIMATE", "INCLIMATE", "OHCLIMATE", "KYCLIMATE"))
COOP = iemdb.connect('coop')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
ccursor2 = COOP.cursor()
THISYEAR = mx.DateTime.now().year
META = {
    'climate51' : {'sts': mx.DateTime.DateTime(1951,1,1), 
                   'ets': mx.DateTime.DateTime(THISYEAR,1,1)},
    'climate71' : {'sts': mx.DateTime.DateTime(1971,1,1), 
                   'ets': mx.DateTime.DateTime(2001,1,1)},
    'climate' : {'sts': mx.DateTime.DateTime(1893,1,1), 
                   'ets': mx.DateTime.DateTime(THISYEAR,1,1)},
    'climate81' : {'sts': mx.DateTime.DateTime(1981,1,1), 
                   'ets': mx.DateTime.DateTime(2011,1,1)}       
}

def daily_averages(table):
    """
    Compute and Save the simple daily averages
    """
    for st in ['nd','sd','ne','ks','mo','ia','mn','wi','il','in','oh','mi','ky']:
        print 'Computing Daily Averages for state:', st
        sql = """
    SELECT '2000-'|| to_char(day, 'MM-DD') as d, station, 
    avg(high) as avg_high, avg(low) as avg_low,
    max(high) as max_high, min(high) as min_high,
    max(low) as max_low, min(low) as min_low,
    max(precip) as max_precip, avg(precip) as precip,
    avg(snow) as snow, count(*) as years,
    avg( gdd50(high,low) ) as gdd50, avg( sdd86(high,low) ) as sdd86,
    max( high - low) as max_range, min(high - low) as min_range
    from alldata_%s WHERE day >= '%s' and day < '%s' 
    GROUP by d, station
    """ % (st, META[table]['sts'].strftime("%Y-%m-%d"), 
		META[table]['ets'].strftime("%Y-%m-%d") )
        ccursor.execute(sql)
        for row in ccursor:
            id = row['station']
            if not id.upper() in nt.sts.keys():
                continue
            sql = """DELETE from %s WHERE station = '%s' and valid = '%s' """ % (
                        table, id, row['d'])
            ccursor2.execute(sql)
            sql = """ INSERT into """+ table +""" (station, valid, high, low, precip, snow,
        max_high, max_low, min_high, min_low, max_precip, years, gdd50, sdd86, max_range,
        min_range) VALUES ('%(station)s', '%(d)s', %(avg_high)s, %(avg_low)s, %(precip)s,
        %(snow)s, %(max_high)s, %(max_low)s, %(min_high)s, %(min_low)s, %(max_precip)s,
        %(years)s, %(gdd50)s, %(sdd86)s, %(max_range)s, %(min_range)s)""" % row
            ccursor2.execute(sql)

        COOP.commit()

def do_date(table, row, col, agg_col):
    sql = """
    SELECT year from alldata_%s where station = '%s' and %s = %s and sday = '%s'
    and day >= '%s' and day < '%s'
    ORDER by year ASC
    """ % (row['station'][:2].lower(), row['station'], col, row[agg_col], 
           row['valid'].strftime("%m%d"),
           META[table]['sts'].strftime("%Y-%m-%d"), 
           META[table]['ets'].strftime("%Y-%m-%d"))
    ccursor2.execute(sql)
    row2 = ccursor2.fetchone()
    if row2 is not None:
        sql = """ UPDATE %s SET %s_yr = %s WHERE station = '%s' and valid = '%s' """ % (
                    table, agg_col, row2[0], row['station'], row['valid'])
        ccursor2.execute(sql)

def set_daily_extremes(table):
    sql = """
    SELECT * from %s 
    """ % (table,)
    ccursor.execute(sql)
    for row in ccursor:
        do_date(table, row, 'high', 'max_high')
        do_date(table, row, 'high', 'min_high')
        do_date(table, row, 'low', 'max_low')
        do_date(table, row, 'low', 'min_low')
        do_date(table, row, 'precip', 'max_precip')
        COOP.commit()
       
#daily_averages(sys.argv[1])
set_daily_extremes(sys.argv[1])
COOP.commit()
ccursor.close()
ccursor2.close()
