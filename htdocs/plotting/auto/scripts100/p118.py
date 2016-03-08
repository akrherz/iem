import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime

PDICT = {'precip_days': 'Precipitation Days',
         'snow_days': 'Snowfall Days'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['report'] = True
    d['description'] = """ """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='var', options=PDICT,
             label='Select Variable'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200').upper()
    varname = fdict.get('var', 'precip_days')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    df = read_sql("""
    SELECT year, month,
    sum(case when precip >= 0.01 then 1 else 0 end) as precip_days,
    sum(case when snow >= 0.01 then 1 else 0 end) as snow_days
    from """+table+""" WHERE station = %s
    GROUP by year, month
    """, pgconn, params=(station,), index_col=['year', 'month'])

    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# NUMBER OF DAYS WITH PRECIPITATION PER MONTH PER YEAR
# Days with a trace accumulation are not included
YEAR   JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC ANN
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])

    for year in df.index.levels[0]:
        res += "%4i  " % (year,)
        total = 0
        for month in df.index.levels[1]:
            try:
                val = df.at[(year, month), varname]
                total += val
                res += " %3i" % (val, )
            except:
                res += "    "
        res += " %3i\n" % (total, )
    return None, df, res

if __name__ == '__main__':
    plotter(dict())
