import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import numpy as np
import datetime


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['report'] = True
    d['description'] = """ """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
    ]
    return d


def modMonth(stationID, db, monthly, mo1, mo2, mt1, mt2, nt):
    res = ("""\n               %-12s                %-12s
     ****************************  ***************************
 YEAR  40-86  48-86  50-86  52-86   40-86  48-86  50-86  52-86
     ****************************  *************************** \n""") % (mt1,
                                                                         mt2)
    s = nt.sts[stationID]['archive_begin'].year
    e = datetime.date(datetime.date.today().year + 1, 1, 1)
    now = s
    for year in range(s, e.year):
        now = datetime.date(year, 1, 1)
        m1 = now.replace(month=mo1)
        m2 = now.replace(month=mo2)
        if m1 >= e:
            db[m1] = {40: 'M', 48: 'M', 50: 'M', 52: 'M'}
        if m2 >= e:
            db[m2] = {40: 'M', 48: 'M', 50: 'M', 52: 'M'}
        res += ("%5i%7s%7s%7s%7s%7s%7s%7s%7s\n"
                ) % (now.year, db[m1][40], db[m1][48], db[m1][50],
                     db[m1][52], db[m2][40], db[m2][48], db[m2][50],
                     db[m2][52])

    res += ("     ****************************  "
            "****************************\n")
    res += (" MEAN%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n"
            ) % (np.average(monthly[mo1]["40"]),
                 np.average(monthly[mo1]["48"]),
                 np.average(monthly[mo1]["50"]),
                 np.average(monthly[mo1]["52"]),
                 np.average(monthly[mo2]["40"]),
                 np.average(monthly[mo2]["48"]),
                 np.average(monthly[mo2]["50"]),
                 np.average(monthly[mo2]["52"]))
    res += (" STDV%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n"
            ) % (np.std(monthly[mo1]["40"]),
                 np.std(monthly[mo1]["48"]),
                 np.std(monthly[mo1]["50"]),
                 np.std(monthly[mo1]["52"]),
                 np.std(monthly[mo2]["40"]),
                 np.std(monthly[mo2]["48"]),
                 np.std(monthly[mo2]["50"]),
                 np.std(monthly[mo2]["52"]))
    return res


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    df = read_sql("""
    SELECT year, month, sum(precip) as sum_precip,
    avg(high) as avg_high,
    avg(low) as avg_low,
    sum(cdd(high,low,60)) as cdd60,
    sum(cdd(high,low,65)) as cdd65,
    sum(hdd(high,low,60)) as hdd60,
    sum(hdd(high,low,65)) as hdd65,
    sum(case when precip >= 0.01 then 1 else 0 end) as rain_days,
    sum(case when snow >= 0.1 then 1 else 0 end) as snow_days,
    sum(gddxx(40,86,high,low)) as gdd40,
    sum(gddxx(48,86,high,low)) as gdd48,
    sum(gddxx(50,86,high,low)) as gdd50,
    sum(gddxx(52,86,high,low)) as gdd52
     from """+table+""" WHERE station = %s GROUP by year, month
    """, pgconn, params=(station,), index_col=None)

    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])
    res += ("# GROWING DEGREE DAYS FOR 4 BASE TEMPS FOR STATION ID %s\n"
               ) % (station, )

    monthly = [0]*13
    for i in range(13):
        monthly[i] = {'40': [],
                      '48': [],
                      '50': [],
                      '52': []
                      }

    db = {}
    for i, row in df.iterrows():
        ts = datetime.date(int(row['year']), int(row['month']), 1)
        db[ts] = {40: float(row["gdd40"]),
                  48: float(row["gdd48"]),
                  50: float(row["gdd50"]),
                  52: float(row["gdd52"])}
        monthly[ts.month]['40'].append(float(row['gdd40']))
        monthly[ts.month]['48'].append(float(row['gdd48']))
        monthly[ts.month]['50'].append(float(row['gdd50']))
        monthly[ts.month]['52'].append(float(row['gdd52']))

    res += modMonth(station, db, monthly, 3, 4, "MARCH", "APRIL", nt)
    res += modMonth(station, db, monthly, 5, 6, "MAY", "JUNE", nt)
    res += modMonth(station, db, monthly, 7, 8, "JULY", "AUGUST", nt)
    res += modMonth(station, db, monthly, 9, 10, "SEPTEMBER", "OCTOBER", nt)

    return None, df, res

if __name__ == '__main__':
    plotter(dict())
