"""when are the daily records"""
import calendar

import numpy as np
from pandas.io.sql import read_sql
import matplotlib.colors as mpcolors
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents the year that the present
    day climatology record resides."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='cmap', name='cmap', default='jet', label='Color Ramp:'),
    ]
    return desc


def magic(ax, df, colname, title, ctx):
    """You can do magic"""
    df2 = df[df[colname] == 1]

    ax.text(0, 1.02, title, transform=ax.transAxes)
    ax.set_xlim(0, 367)
    ax.grid(True)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])

    bbox = ax.get_position()
    sideax = plt.axes([bbox.x1 + 0.01, bbox.y0, 0.09, 0.35])
    ylim = [df['year'].min(), df['year'].max()]
    year0 = ylim[0] - (ylim[0] % 10)
    year1 = ylim[1] + (10 - ylim[1] % 10)
    cmap = plt.get_cmap(ctx['cmap'])
    norm = mpcolors.BoundaryNorm(np.arange(year0, year1 + 1, 10), cmap.N)
    ax.scatter(df2['doy'], df2['year'], color=cmap(norm(df2['year'].values)))
    ax.set_yticks(np.arange(year0, year1, 20))
    ax.set_ylim(*ylim)
    cnts, edges = np.histogram(df2['year'].values,
                               np.arange(year0, year1 + 1, 10))
    sideax.barh(edges[:-1], cnts, height=10, align='edge',
                color=cmap(norm(edges[:-1])))
    sideax.set_yticks(np.arange(year0, year1, 20))
    sideax.set_yticklabels([])
    sideax.set_ylim(*ylim)
    sideax.grid(True)
    sideax.set_xlabel("Decade Count")


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']

    table = "alldata_%s" % (station[:2],)

    df = read_sql("""
    WITH data as (
        SELECT sday, day, year,
        rank() OVER (PARTITION by sday ORDER by high DESC) as max_high_rank,
        rank() OVER (PARTITION by sday ORDER by high ASC) as min_high_rank,
        rank() OVER (PARTITION by sday ORDER by low DESC) as max_low_rank,
        rank() OVER (PARTITION by sday ORDER by low ASC) as min_low_rank
        from """ + table + """ WHERE station = %s and high is not null
        and low is not null)
    SELECT *,
    extract(doy from
    ('2000-'||substr(sday, 1, 2)||'-'||substr(sday, 3, 2))::date) as doy
    from data WHERE max_high_rank = 1 or min_high_rank = 1 or
    max_low_rank = 1 or min_low_rank = 1 ORDER by day ASC
    """, pgconn, params=(station, ), index_col=None)
    if df.empty:
        raise NoDataFound("No Data Found.")

    fig = plt.figure(figsize=(12, 6))
    fig.text(0.5, 0.95, ("[%s] %s Year of Daily Records, ties included"
                         ) % (station, ctx['_nt'].sts[station]['name']),
             ha='center', fontsize=16)
    ax = plt.axes([0.04, 0.55, 0.35, 0.35])
    magic(ax, df, 'max_high_rank', 'Maximum High (warm)', ctx)
    ax = plt.axes([0.04, 0.1, 0.35, 0.35])
    magic(ax, df, 'min_high_rank', 'Minimum High (cold)', ctx)
    ax = plt.axes([0.54, 0.55, 0.35, 0.35])
    magic(ax, df, 'max_low_rank', 'Maximum Low (warm)', ctx)
    ax = plt.axes([0.54, 0.1, 0.35, 0.35])
    magic(ax, df, 'min_low_rank', 'Minimum Low (cold)', ctx)

    return plt.gcf(), df


if __name__ == '__main__':
    plotter(dict())
