import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime
import numpy as np

PDICT = {'precip': 'Total Precipitation',
         'avg_high': 'Average High Temperature',
         'avg_low': 'Average Low Temperature',
         'avg_temp': 'Average Monthly Temperature'}

LABELS = {'precip': 'Monthly Liquid Precip Totals [inches] (snow is melted)',
          'avg_high': 'Monthly Average High Temperatures [F]',
          'avg_low': 'Monthly Average Low Temperatures [F]',
          'avg_temp': 'Monthly Average Temperatures [F] (High + low)/2'
          }


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['report'] = True
    d['description'] = """ """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type="select", name="var", default="precip",
             label="Select variable:"),
    ]
    return d


def p(df, year, month, varname, precision):
    try:
        val = df.at[(year, month), varname]
    except:
        return ' ****'
    fmt = "%%5.%sf" % (precision, )
    return fmt % val


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')
    varname = fdict.get('var', 'precip')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    TODAY = datetime.date.today().replace(day=1)

    df = read_sql("""
    SELECT year, month,
    sum(precip) as precip,
    avg(high) as avg_high, avg(low) as avg_low,
    avg((high+low)/2.) as avg_temp from """+table+""" WHERE
    station = %s and day < %s GROUP by year, month
    """, pgconn, params=(station, TODAY), index_col=None)

    res = """\
# IEM Climodat http://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])
    res += """# %s
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN
""" % (LABELS[varname], )

    years = df['year'].unique()
    years.sort()
    grouped = df.set_index(['year', 'month'])
    yrsum = df.groupby('year')[varname].sum()
    yrmean = df.groupby('year')[varname].mean()

    prec = 2 if varname == 'precip' else 0
    for year in years:
        yrtot = yrsum[year]
        if varname != 'precip':
            yrtot = yrmean[year]
        res += ("%s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6.2f\n") % (
                                   year,
                                   p(grouped, year, 1, varname, prec),
                                   p(grouped, year, 2, varname, prec),
                                   p(grouped, year, 3, varname, prec),
                                   p(grouped, year, 4, varname, prec),
                                   p(grouped, year, 5, varname, prec),
                                   p(grouped, year, 6, varname, prec),
                                   p(grouped, year, 7, varname, prec),
                                   p(grouped, year, 8, varname, prec),
                                   p(grouped, year, 9, varname, prec),
                                   p(grouped, year, 10, varname, prec),
                                   p(grouped, year, 11, varname, prec),
                                   p(grouped, year, 12, varname, prec), yrtot)
    yrtot = yrmean.mean() if varname != 'precip' else yrsum.mean()
    res += ("MEAN%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f\n") % (
        df[df['month'] == 1][varname].mean(),
        df[df['month'] == 2][varname].mean(),
        df[df['month'] == 3][varname].mean(),
        df[df['month'] == 4][varname].mean(),
        df[df['month'] == 5][varname].mean(),
        df[df['month'] == 6][varname].mean(),
        df[df['month'] == 7][varname].mean(),
        df[df['month'] == 8][varname].mean(),
        df[df['month'] == 9][varname].mean(),
        df[df['month'] == 10][varname].mean(),
        df[df['month'] == 11][varname].mean(),
        df[df['month'] == 12][varname].mean(),
        yrtot)

    return None, df, res

if __name__ == '__main__':
    plotter(dict())
