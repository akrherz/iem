import psycopg2
import calendar
import numpy as np
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['nass'] = True
    d['description'] = """This chart presents harvest or planting progress."""
    d['arguments'] = [
        dict(type='state', name='state', default='IA',
             label='Select State:')
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    state = fdict.get('state', 'IA')[:2]

    df = read_sql("""
        select year, week_ending, num_value from nass_quickstats
        where commodity_desc = 'CORN' and statisticcat_desc = 'PROGRESS'
        and unit_desc = 'PCT HARVESTED' and state_alpha = %s and
        util_practice_desc = 'GRAIN'
        ORDER by week_ending ASC
    """, pgconn, params=(state,), index_col=None)
    if len(df.index) == 0:
        return "ERROR: No data found!"
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
        ax.text(idx[0], year, "X", va='center', zorder=2)

    cmap = cm.get_cmap('jet')
    res = ax.imshow(data, extent=[1, 367, lastyear + 0.5, year0 - 0.5],
                    aspect='auto',
                    interpolation='none', cmap=cmap)
    fig.colorbar(res)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(200, 360)
    ax.set_ylim(lastyear + 0.5, year0 - 0.5)
    ax.grid(True)
    lastweek = df['week_ending'].max()
    ax.set_xlabel("X denotes %s value of %.0f%%" % (
                        lastweek.strftime("%d %b %Y"), dlast))
    ax.set_title(("USDA NASS %i-%i %s Corn Harvest Progress\n"
                  "Daily Linear Interpolated Values Between Weekly Reports"
                  ) % (year0, lastyear, state))

    return fig, df

if __name__ == '__main__':
    plotter(dict())
