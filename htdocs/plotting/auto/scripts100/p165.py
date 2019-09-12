"""Map of dates"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot.geoplot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT3 = {
    'contour': 'Contour + Plot Values',
    'values': 'Plot Values Only'}
PDICT2 = OrderedDict((
    ('spring_below', 'Last Spring Date Below'),
    ('high_above', 'First Date of Year At or Above'),
    ('fall_below', 'First Fall Date Below'),
))

MONTH_DOMAIN = {
    'spring_below': range(1, 7),
    'fall_below': range(1, 12),
    'high_above': range(1, 12),
}
SQLOPT = {
    'spring_below': " low < %s ",
    'high_above': " high >= %s ",
    'fall_below': " low < %s ",
}
YRGP = {
    'spring_below': "year",
    'high_above': "year",
    'fall_below': "winter_year",
}
ORDER = {
    'spring_below': "DESC",
    'fall_below': "ASC",
    "high_above": "ASC",
}
USEDOY = {
    'spring_below': "doy",
    "high_above": "doy",
    'fall_below': "winter_doy",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """
    This app generates a map showing either an explicit year's first or last
    date or the given percentile (observed
    frequency) date over all available years of a given temperature threshold.
    Sadly, this app can only plot one state's worth of data at a time.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='state', name='sector', default='IA',
             label='Select State:'),
        dict(type='select', name='var', default='spring_below',
             label='Select Plot Type:', options=PDICT2),
        dict(type='select', name='popt', default='contour',
             label='Plot Display Options:', options=PDICT3),
        dict(type='year', name='year',
             default=today.year,
             label='Year:', min=1893),
        dict(type='int', name='threshold',
             default=32,
             label='Temperature Threshold (F):'),
        dict(
            type="int", value=50, optional=True, name="p",
            label="Plot date of given observed frequency (%): [optional]"
        ),
        dict(type='cmap', name='cmap', default='BrBG', label='Color Ramp:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    sector = ctx['sector']
    if len(sector) != 2:
        raise NoDataFound("Sorry, this app doesn't support multi-state plots.")
    varname = ctx['var']
    year = ctx['year']
    popt = ctx['popt']
    threshold = ctx['threshold']
    table = "alldata_%s" % (sector,)
    nt = NetworkTable("%sCLIMATE" % (sector, ))
    df = read_sql("""
        -- get the domain of data
        WITH events as (
            SELECT
            station, month,
            case when month < 7 then year - 1 else year end as winter_year,
            year,
            extract(doy from day) as doy,
            day
            from """ + table + """
            WHERE """ + SQLOPT[varname] + """ and
            month in %s and
            substr(station, 3, 4) != '0000'
            and substr(station, 3, 1) not in ('C', 'T')
        ), agg as (
            SELECT station, winter_year, year, doy, day,
            case when month < 7 then doy + 366 else doy end as winter_doy,
            rank() OVER (
                PARTITION by """ + YRGP[varname] + """, station
                ORDER by day """ + ORDER[varname] + """)
            from events)
        select * from agg where rank = 1
        """, pgconn, params=(
            threshold, tuple(MONTH_DOMAIN[varname]), ), index_col='station')

    doy = USEDOY[varname]

    def f(val):
        """Make a pretty date."""
        base = datetime.date(2000, 1, 1)
        date = base + datetime.timedelta(days=int(val))
        return date.strftime("%-m/%-d")

    if ctx.get('p') is None:
        df2 = df[df[YRGP[varname]] == year].copy()
        title = r"%s %s %s$^\circ$F" % (year, PDICT2[varname], threshold)
        df2['pdate'] = df2['day'].apply(lambda x: x.strftime("%-m/%-d"))
    else:
        df2 = df[[doy, ]].groupby('station').quantile(ctx['p'] / 100.).copy()
        title = r"%.0f Percentile Date of %s %s$^\circ$F" % (
            ctx['p'], PDICT2[varname], threshold)
        df2['pdate'] = df2[doy].apply(f)
    if df2.empty:
        raise NoDataFound("No Data was found")
    for station in df2.index.values:
        if station not in nt.sts:
            continue
        df2.at[station, 'lat'] = nt.sts[station]['lat']
        df2.at[station, 'lon'] = nt.sts[station]['lon']

    mp = MapPlot(
        sector='state',
        state=ctx['sector'],
        continental_color='white', nocaption=True,
        title=title,
        subtitle='based on NWS COOP and IEM Daily Estimates')
    levs = np.linspace(
        df2[doy].min() - 3, df2[doy].max() + 3, 7, dtype='i')
    levlables = list(map(f, levs))
    if popt == 'contour':
        mp.contourf(
            df2['lon'], df2['lat'], df2[doy], levs,
            clevlabels=levlables, cmap=ctx['cmap'])
    mp.plot_values(df2['lon'], df2['lat'], df2['pdate'], labelbuffer=5)
    mp.drawcounties()

    return mp.fig, df[['year', 'winter_doy', 'doy']]


if __name__ == '__main__':
    plotter(dict(var='fall_below'))
