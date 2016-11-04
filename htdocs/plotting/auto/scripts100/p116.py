import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime

PDICT = {'cdd': 'Cooling Degree Days',
         'hdd': 'Heating Degree Days'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['report'] = True
    d['description'] = """ """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', options=PDICT, default='cdd', name='var',
             label='Select Variable'),
    ]
    return d


def plotter(fdict):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

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
    sum(case when snow >= 0.1 then 1 else 0 end) as snow_days,
    sum(gddxx(40,86,high,low)) as gdd40,
    sum(gddxx(48,86,high,low)) as gdd48,
    sum(gddxx(50,86,high,low)) as gdd50,
    sum(gddxx(52,86,high,low)) as gdd52
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

    return None, df, res

if __name__ == '__main__':
    plotter(dict())
