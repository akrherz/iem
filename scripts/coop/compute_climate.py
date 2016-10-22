"""Computes the Climatology and fills out the table!"""
import datetime
import psycopg2.extras
from pyiem.network import Table as NetworkTable
import sys
from tqdm import tqdm
COOP = psycopg2.connect(database='coop', host='iemdb')

THISYEAR = datetime.date.today().year
META = {
    'climate51': {'sts': datetime.datetime(1951, 1, 1),
                  'ets': datetime.datetime(THISYEAR, 1, 1)},
    'climate71': {'sts': datetime.datetime(1971, 1, 1),
                  'ets': datetime.datetime(2001, 1, 1)},
    'climate': {'sts': datetime.datetime(1893, 1, 1),
                'ets': datetime.datetime(THISYEAR, 1, 1)},
    'climate81': {'sts': datetime.datetime(1981, 1, 1),
                  'ets': datetime.datetime(2011, 1, 1)}
}


def daily_averages(table):
    """
    Compute and Save the simple daily averages
    """
    for st in ['ND', 'SD', 'NE', 'KS', 'MO', 'IA', 'MN', 'WI', 'IL',
               'IN', 'OH', 'MI', 'KY']:
        nt = NetworkTable("%sCLIMATE" % (st,))
        print 'Computing Daily Averages for state: %s' % (st,)
        ccursor = COOP.cursor()
        ccursor.execute("""DELETE from %s WHERE substr(station,1,2) = '%s'
        """ % (table, st))
        print '    removed %s rows from %s' % (ccursor.rowcount, table)
        sql = """
    INSERT into %s (station, valid, high, low,
        max_high, min_high,
        max_low, min_low,
        max_precip, precip,
        snow, years, gdd50, sdd86, hdd65, max_range,
        min_range)
    (SELECT station, ('2000-'|| to_char(day, 'MM-DD'))::date as d,
    avg(high) as avg_high, avg(low) as avg_low,
    max(high) as max_high, min(high) as min_high,
    max(low) as max_low, min(low) as min_low,
    max(precip) as max_precip, avg(precip) as precip,
    avg(snow) as snow, count(*) as years,
    avg( gddxx(50,86,high,low) ) as gdd50, avg( sdd86(high,low) ) as sdd86,
    avg( hdd65(high,low) ) as hdd65,
    max( high - low) as max_range, min(high - low) as min_range
    from alldata_%s WHERE day >= '%s' and day < '%s' and
    precip is not null and high is not null and low is not null
    and station in %s
    GROUP by d, station)
        """ % (table, st, META[table]['sts'].strftime("%Y-%m-%d"),
               META[table]['ets'].strftime("%Y-%m-%d"), tuple(nt.sts.keys()))
        ccursor.execute(sql)
        print '    added %s rows to %s' % (ccursor.rowcount, table)
        ccursor.close()
        COOP.commit()


def do_date(ccursor2, table, row, col, agg_col):
    sql = """
    SELECT year from alldata_%s where station = '%s' and %s = %s
    and sday = '%s'
    and day >= '%s' and day < '%s'
    ORDER by year ASC
    """ % (row['station'][:2], row['station'], col, row[agg_col],
           row['valid'].strftime("%m%d"),
           META[table]['sts'],
           META[table]['ets'])
    ccursor2.execute(sql)
    row2 = ccursor2.fetchone()
    if row2 is None:
        print 'None?', row, col, agg_col
        return 'null'
    return row2[0]


def set_daily_extremes(table):
    sql = """
    SELECT * from %s WHERE max_high_yr is null and max_high is not null
    and min_high_yr is null and min_high is not null
    and max_low_yr is null and max_low is not null
    and min_low_yr is null and min_low is not null
    """ % (table,)
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ccursor.execute(sql)
    ccursor2 = COOP.cursor()
    cnt = 0
    total = ccursor.rowcount
    for row in tqdm(ccursor, total=total):
        data = {}
        data['max_high_yr'] = do_date(ccursor2, table, row, 'high', 'max_high')
        data['min_high_yr'] = do_date(ccursor2, table, row, 'high', 'min_high')
        data['max_low_yr'] = do_date(ccursor2, table, row, 'low', 'max_low')
        data['min_low_yr'] = do_date(ccursor2, table, row, 'low', 'min_low')
        data['max_precip_yr'] = do_date(ccursor2, table, row,
                                        'precip', 'max_precip')
        ccursor2.execute("""UPDATE %s SET max_high_yr = %s, min_high_yr = %s,
        max_low_yr = %s, min_low_yr = %s, max_precip_yr = %s
        WHERE station = '%s' and valid = '%s'""" % (
                                    table, data['max_high_yr'],
                                    data['min_high_yr'], data['max_low_yr'],
                                    data['min_low_yr'], data['max_precip_yr'],
                                    row['station'], row['valid']))
        cnt += 1
        if cnt % 1000 == 0:
            ccursor2.close()
            COOP.commit()
            ccursor2 = COOP.cursor()
    ccursor2.close()
    ccursor.close()
    COOP.commit()

if __name__ == '__main__':
    daily_averages(sys.argv[1])
    set_daily_extremes(sys.argv[1])
