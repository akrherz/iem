"""Monthly HDD/CDD Totals."""
import datetime

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn

PDICT = {'cdd': 'Cooling Degree Days',
         'hdd': 'Heating Degree Days'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['report'] = True
    desc['description'] = """This chart presents monthly cooling degree days
    or heating degree days for a 20 year period of your choice.  The 20 year
    limit is for plot usability only, the data download has all available
    years contained."""
    y20 = datetime.date.today().year - 19
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station', network='IACLIMATE'),
        dict(type='select', options=PDICT, default='cdd', name='var',
             label='Select Variable'),
        dict(type='year', name='syear', default=y20,
             label='For plotting, year to start 20 years of plot'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import seaborn as sns
    pgconn = get_dbconn('coop')

    station = fdict.get('station', 'IA0200')
    varname = fdict.get('var', 'cdd')

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
    sum(case when snow >= 0.1 then 1 else 0 end) as snow_days
     from """+table+""" WHERE station = %s GROUP by year, month
    """, pgconn, params=(station,), index_col=None)
    df['monthdate'] = df[['year', 'month']].apply(lambda x: datetime.date(x[0],
                                                                          x[1],
                                                                          1),
                                                  axis=1)
    df.set_index('monthdate', inplace=True)

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
""" % (datetime.date.today().strftime("%d %b %Y"),
       nt.sts[station]['archive_begin'].date(), datetime.date.today(), station,
       nt.sts[station]['name'])
    res += """# THESE ARE THE MONTHLY %s (base=65) FOR STATION  %s
YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    \
OCT    NOV    DEC
""" % (PDICT[varname].upper(), station)

    second = """# THESE ARE THE MONTHLY %s (base=60) FOR STATION  %s
YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    \
OCT    NOV    DEC
""" % (
        PDICT[varname].upper(), station)
    minyear = df['year'].min()
    maxyear = df['year'].max()
    for yr in range(minyear, maxyear + 1):
        res += ("%4i" % (yr,))
        second += "%4i" % (yr,)
        for mo in range(1, 13):
            ts = datetime.date(yr, mo, 1)
            if ts not in df.index:
                res += ("%7s" % ("M",))
                second += "%7s" % ("M",)
                continue
            row = df.loc[ts]
            res += ("%7.0f" % (row[varname+"65"],))
            second += "%7.0f" % (row[varname+"60"],)
        res += ("\n")
        second += "\n"

    res += ("MEAN")
    second += "MEAN"
    for mo in range(1, 13):
        df2 = df[df['month'] == mo]
        res += ("%7.0f" % (df2[varname+"65"].mean(), ))
        second += "%7.0f" % (df2[varname+"60"].mean(), )
    res += ("\n")
    second += "\n"
    res += second

    y1 = int(fdict.get('syear', 1990))

    fig, ax = plt.subplots(1, 1, figsize=(8., 6.))
    fig.text(0.5, 0.95, "[%s] %s (%s-%s)" % (station, nt.sts[station]['name'],
                                             y1, y1 + 20), ha='center',
             fontsize=16)
    ax.set_title(r"%s base=60$^\circ$F" % (PDICT[varname], ))
    filtered = df[(df['year'] >= y1) & (df['year'] <= (y1 + 20))]
    df2 = filtered[
        ['month', 'year', varname + '60']
        ].pivot('year', 'month', varname + '60')
    sns.heatmap(df2, annot=True, fmt=".0f", linewidths=.5, ax=ax)

    return fig, df, res


if __name__ == '__main__':
    plotter(dict(syear=1990))
