"""Plot or Harvest Progress"""
import calendar
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from matplotlib import cm
from matplotlib import ticker
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict([
    ('PCT PLANTED', 'Planting'),
    ('PCT EMERGED', 'Emerged'),
    ('PCT DENTED', 'Percent Dented'),
    ('PCT COLORING', 'Percent Coloring'),
    ('PCT SETTING PODS', 'Percent Setting Pods'),
    ('PCT DROPPING LEAVES', 'Percent Dropping Leaves'),
    ('PCT HARVESTED', 'Harvest (Grain)')
])
PDICT2 = OrderedDict([('CORN', 'Corn'),
                      ('SOYBEANS', 'Soybean')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['nass'] = True
    desc['description'] = """This chart presents the crop progress by year.
    The most recent value for the current year is denoted on each of the
    previous years on record.
    """
    desc['arguments'] = [
        dict(type='state', name='state', default='IA',
             label='Select State:'),
        dict(type='select', name='unit_desc', default='PCT HARVESTED',
             options=PDICT, label='Which Operation?'),
        dict(type='select', name='commodity_desc', default='CORN',
             options=PDICT2, label='Which Crop?'),
        dict(type='cmap', name='cmap', default='jet', label='Color Ramp:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx['state'][:2]
    unit_desc = ctx['unit_desc'].upper()
    commodity_desc = ctx['commodity_desc'].upper()

    util_practice_desc = ('GRAIN' if (unit_desc == 'PCT HARVESTED' and
                                      commodity_desc == 'CORN')
                          else 'ALL UTILIZATION PRACTICES')

    df = read_sql("""
        select year, week_ending, num_value,
        extract(doy from week_ending)::int as day_of_year from nass_quickstats
        where commodity_desc = %s and statisticcat_desc = 'PROGRESS'
        and unit_desc = %s and state_alpha = %s and
        util_practice_desc = %s and num_value is not null
        ORDER by week_ending ASC
    """, pgconn, params=(commodity_desc, unit_desc, state, util_practice_desc),
                  index_col=None)
    if df.empty:
        raise NoDataFound("ERROR: No data found!")
    df['yeari'] = df['year'] - df['year'].min()

    (fig, ax) = plt.subplots(1, 1)

    year0 = int(df['year'].min())
    lastyear = int(df['year'].max())
    data = np.ma.ones((df['yeari'].max() + 1, 366), 'f') * -1
    data.mask = np.where(data == -1, True, False)

    lastrow = None
    for _, row in df.iterrows():
        if lastrow is None:
            lastrow = row
            continue

        date = row["week_ending"]
        ldate = lastrow["week_ending"]
        val = int(row['num_value'])
        lval = int(lastrow['num_value'])
        d0 = int(ldate.strftime("%j"))
        d1 = int(date.strftime("%j"))
        if ldate.year == date.year:
            delta = (val - lval) / float(d1-d0)
            for i, jday in enumerate(range(d0, d1+1)):
                data[date.year - year0, jday] = lval + i * delta
        else:
            data[ldate.year - year0, d0:] = 100

        lastrow = row

    dlast = np.max(data[-1, :])
    for year in range(year0, lastyear):
        idx = np.digitize([dlast, ], data[year - year0, :])
        ax.text(idx[0], year, "X", va='center', zorder=2, color='white')

    cmap = cm.get_cmap(ctx['cmap'])
    res = ax.imshow(data, extent=[1, 367, lastyear + 0.5, year0 - 0.5],
                    aspect='auto',
                    interpolation='none', cmap=cmap)
    fig.colorbar(res)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    # We need to compute the domain of this plot
    maxv = np.max(data, 0)
    minv = np.min(data, 0)
    ax.set_xlim(np.argmax(maxv > 0) - 7, np.argmax(minv > 99) + 7)
    ax.set_ylim(lastyear + 0.5, year0 - 0.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True)
    lastweek = df['week_ending'].max()
    ax.set_xlabel("X denotes %s value of %.0f%%" % (
                        lastweek.strftime("%d %b %Y"), dlast))
    ax.set_title(("USDA NASS %i-%i %s %s %s Progress\n"
                  "Daily Linear Interpolated Values Between Weekly Reports"
                  ) % (year0, lastyear, state, PDICT2.get(commodity_desc),
                       PDICT.get(unit_desc)))

    return fig, df


if __name__ == '__main__':
    plotter(dict(unit_desc='PCT DENTED'))
