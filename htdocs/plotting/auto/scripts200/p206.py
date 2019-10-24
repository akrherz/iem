"""Map of Daily Summaries."""
import datetime
from collections import OrderedDict

import numpy as np
import pandas as pd
import geopandas as gpd
from pandas.io.sql import read_sql
from pyiem import reference
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'cwa': 'Plot by NWS Forecast Office',
         'state': 'Plot by State'}
PDICT2 = OrderedDict((
    ('max_tmpf', 'Max Air Temperature [F]'),
    ('min_tmpf', 'Min Air Temperature [F]'),
    ('max_gust', 'Peak Wind Gust [MPH]'),
    ('max_sknt', 'Peak Wind Gust [MPH]'),
))
VARUNITS = {
    'max_tmpf': 'F',
    'min_tmpf': 'F',
    'max_gust': 'mph',
    'max_sknt': 'knots',
}
PDICT3 = {
    'both': 'Plot and Contour Values',
    'plot': 'Only Plot Values',
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 600
    desc['description'] = """Generates analysis maps of ASOS/AWOS
    station data for a given date."""
    now = datetime.datetime.now()
    desc['arguments'] = [
        dict(type='select', name='t', default='state', options=PDICT,
             label='Select plot extent type:'),
        dict(type='networkselect', name='wfo', network='WFO',
             default='DMX', label='Select WFO: (ignored if plotting state)'),
        dict(type='state', name='state',
             default='IA', label='Select State: (ignored if plotting wfo)'),
        dict(type='select', name='v', default='max_gust', options=PDICT2,
             label='Select statistic to plot:'),
        dict(type='select', name='p', default='both', options=PDICT3,
             label='Plot or Countour values (for non interactive map):'),
        dict(
            type='float', name='above', optional=True, default=9999,
            label='Remove any plotted values above threshold:'
        ),
        dict(
            type='float', name='below', optional=True, default=-9999,
            label='Remove any plotted values below threshold:'
        ),
        dict(type='date', name='day',
             default=now.strftime("%Y/%m/%d"),
             label='Date', min="1926/01/01"),
        dict(type='cmap', name='cmap', default='viridis', label='Color Ramp:'),
    ]
    return desc


def get_df(ctx, buf=2.25):
    """Figure out what data we need to fetch here"""
    if ctx['t'] == 'state':
        bnds = reference.state_bounds[ctx['state']]
        ctx['title'] = reference.state_names[ctx['state']]
    else:
        bnds = reference.wfo_bounds[ctx['wfo']]
        ctx['title'] = "NWS CWA %s [%s]" % (
            ctx['_nt'].sts[ctx['wfo']]['name'], ctx['wfo'])
    dbconn = get_dbconn("iem")
    df = read_sql("""
        WITH mystation as (
            select id, st_x(geom) as lon, st_y(geom) as lat,
            state, wfo, iemid from stations
            where (network ~* 'ASOS' or network = 'AWOS') and
            ST_contains(ST_geomfromtext(
                'SRID=4326;POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))'),
                geom)
        )
        SELECT s.day, s.max_tmpf, s.min_tmpf,
        max_sknt * 1.15 as max_sknt,
        max_gust * 1.15 as max_gust, t.id as station, t.lat, t.lon,
        t.wfo, t.state from
        summary s JOIN mystation t on (s.iemid = t.iemid)
        WHERE s.day = %s
    """, dbconn, params=(
        bnds[0] - buf, bnds[1] - buf,
        bnds[0] - buf, bnds[3] + buf,
        bnds[2] + buf, bnds[3] + buf,
        bnds[2] + buf, bnds[1] - buf,
        bnds[0] - buf, bnds[1] - buf,
        ctx['day']))
    if df.empty:
        raise NoDataFound("No Data Found.")
    df = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df['lon'], df['lat']))

    return df[pd.notnull(df[ctx['v']])]


def mapbox(fdict):
    """mapbox interface output."""
    ctx = get_autoplot_context(fdict, get_description())
    df = get_df(ctx)
    df['val'] = df[ctx['v']].round(2)
    df['color'] = '#000000'
    geojson = df[['station', 'val', 'geometry', 'color']].to_json()
    return """

    var ap_geodata = """ + geojson + """;

    map.addLayer({
        "id": "points",
        "type": "symbol",
        "source": {
            "type": "geojson",
            "data": ap_geodata
        },
        "paint": {
            "text-color": {"type": "identity", "property": "color"},
            "text-halo-color": "#FFFFFF",
            "text-halo-width": 4
        },
        "layout": {
            "text-field": "{val}",
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-offset": [0, 0.6],
            "text-anchor": "top"
        }
    });
    """


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx['v']

    df = get_df(ctx)
    if df.empty:
        raise NoDataFound("No data was found for your query")
    mp = MapPlot(
        sector=('state' if ctx['t'] == 'state' else 'cwa'),
        state=ctx['state'],
        cwa=(ctx['wfo'] if len(ctx['wfo']) == 3 else ctx['wfo'][1:]),
        axisbg='white',
        title='%s for %s on %s' % (PDICT2[ctx['v']], ctx['title'], ctx['day']),
        nocaption=True,
        titlefontsize=16)
    ramp = None
    cmap = plt.get_cmap(ctx['cmap'])
    extend = 'both'
    if varname in ['max_gust', 'max_sknt']:
        extend = 'max'
        ramp = np.arange(0, 40, 4)
        ramp = np.append(ramp, np.arange(40, 80, 10))
        ramp = np.append(ramp, np.arange(80, 120, 20))
    # Data QC, cough
    if ctx.get('above'):
        df = df[df[varname] < ctx['above']]
    if ctx.get('below'):
        df = df[df[varname] > ctx['below']]
    # with QC done, we compute ramps
    if ramp is None:
        ramp = np.linspace(
            df[varname].min() - 5, df[varname].max() + 5, 10, dtype='i')

    if ctx['p'] == 'both':
        mp.contourf(
            df['lon'].values, df['lat'].values, df[varname].values, ramp,
            units=VARUNITS[varname], cmap=cmap, spacing='proportional',
            extend=extend)
    if ctx['t'] == 'state':
        df2 = df[df[ctx['t']] == ctx[ctx['t']]]
    else:
        df2 = df[df['wfo'] == ctx['wfo']]

    mp.plot_values(
        df2['lon'].values, df2['lat'].values,
        df2[varname].values, '%.1f', labelbuffer=10
    )
    mp.drawcounties()
    if ctx['t'] == 'cwa':
        mp.draw_cwas()

    return mp.fig, df


if __name__ == '__main__':
    plotter(dict(v='feel'))
