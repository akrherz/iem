"""Monthly precip in text format"""
import datetime
import calendar

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

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
    desc = dict()
    desc['data'] = True
    desc['report'] = True
    desc['description'] = """This reports presents simple monthy and yearly
    summary statistics.  The <i>WYEAR</i> column denotes the 'Water Year'
    total, which is defined for the period between 1 Oct and 30 Sep. For
    example, the 2009 <i>WYEAR</i> value represents the period between
    1 Oct 2008 and 30 Sep 2009, the 2009 water year."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station', network='IACLIMATE'),
        dict(type="select", name="var", default="precip",
             label="Select variable:", options=PDICT),
    ]
    return desc


def myformat(val, precision):
    """Nice"""
    if val is None:
        return ' ****'
    fmt = "%%5.%sf" % (precision, )
    return fmt % val


def p(df, year, month, varname, precision):
    """Lazy request of data"""
    try:
        val = df.at[(year, month), varname]
    except Exception as _:
        return ' ****'
    if pd.isna(val):
        return ' ****'
    fmt = "%%5.%sf" % (precision, )
    return fmt % val


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')

    station = fdict.get('station', 'IA0200').upper()
    varname = fdict.get('var', 'precip')

    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2], ))
    today = datetime.date.today().replace(day=1)

    df = read_sql("""
    SELECT year, month,
    case when month in (10, 11, 12) then year + 1 else year end as water_year,
    sum(precip) as precip,
    avg(high) as avg_high, avg(low) as avg_low,
    avg((high+low)/2.) as avg_temp from """+table+""" WHERE
    station = %s and day < %s
    GROUP by year, water_year, month
    ORDER by year ASC, month ASC
    """, pgconn, params=(station, today), index_col=None)

    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        "# Report Generated: %s\n"
        "# Climate Record: %s -> %s, "
        "WYEAR column is Water Year Oct 1 - Sep 30\n"
        "# Site Information: [%s] %s\n"
        "# Contact Information: "
        "Daryl Herzmann akrherz@iastate.edu 515.294.5978\n"
        ) % (datetime.date.today().strftime("%d %b %Y"),
             nt.sts[station]['archive_begin'].date(),
             datetime.date.today(), station,
             nt.sts[station]['name'])
    res += ("# %s\n"
            "YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   "
            "OCT   NOV   DEC   ANN WYEAR\n") % (LABELS[varname], )

    years = df['year'].unique()
    years.sort()
    grouped = df.set_index(['year', 'month'])
    yrsum = df.groupby('year')[varname].sum()
    wyrsum = df.groupby('water_year')[varname].sum()
    yrmean = df.groupby('year')[varname].mean()
    wyrmean = df.groupby('water_year')[varname].mean()

    prec = 2 if varname == 'precip' else 0
    for year in years:
        yrtot = yrsum[year]
        wyrtot = wyrsum.get(year, 0)
        if varname != 'precip':
            yrtot = yrmean[year]
            wyrtot = wyrmean.get(year, 0)
        res += ("%s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s%6s\n") % (
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
                                   p(grouped, year, 12, varname, prec),
                                   myformat(yrtot, 2), myformat(wyrtot, 2))
    yrtot = yrmean.mean() if varname != 'precip' else yrsum.mean()
    wyrtot = wyrmean.mean() if varname != 'precip' else wyrsum.mean()
    res += ("MEAN%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f"
            "%6.2f%6.2f%6.2f%6.2f\n") % (
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
        yrtot, wyrtot)

    # create a better resulting dataframe
    resdf = pd.DataFrame(index=years)
    resdf.index.name = 'YEAR'
    for i, month_abbr in enumerate(calendar.month_abbr):
        if i == 0:
            continue
        resdf[month_abbr.upper()] = df[df['month'] == i
                                       ].set_index('year')[varname]
    resdf['ANN'] = yrmean if varname != 'precip' else yrsum
    resdf['WATER YEAR'] = wyrmean if varname != 'precip' else wyrsum

    return None, resdf, res


if __name__ == '__main__':
    plotter(dict(station='IN0784'))
