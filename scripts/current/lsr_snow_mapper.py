"""Create an analysis of LSR snowfall reports"""
from __future__ import print_function
import datetime
import unittest
import warnings

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from scipy.interpolate import Rbf
from pyiem.plot import MapPlot, nwssnow
from pyiem import reference
from pyiem.util import get_dbconn

# Stop whining about missing data for contourf
warnings.filterwarnings("ignore")


def run(basets, endts, view):
    """Generate this plot for the given basets"""
    pgconn = get_dbconn('postgis', user='nobody')

    df = read_sql("""SELECT state,
        max(magnitude) as val, ST_x(geom) as lon, ST_y(geom) as lat
        from lsrs WHERE type in ('S') and magnitude >= 0 and
        valid > %s and valid < %s GROUP by state, lon, lat
        """, pgconn, params=(basets, endts), index_col=None)
    df.sort_values(by='val', ascending=False, inplace=True)
    df['useme'] = False
    # First, we need to filter down the in-bound values to get rid of small
    cellsize = 0.33
    newrows = []
    for lat in np.arange(reference.MW_SOUTH, reference.MW_NORTH,
                         cellsize):
        for lon in np.arange(reference.MW_WEST, reference.MW_EAST,
                             cellsize):
            # Look around this box at 1x
            df2 = df[(df['lat'] >= (lat - cellsize)) &
                     (df['lat'] < (lat + cellsize)) &
                     (df['lon'] >= (lon - cellsize)) &
                     (df['lon'] < (lon + cellsize))]
            if df2.empty:
                # If nothing was found, check 2x
                df3 = df[(df['lat'] >= (lat - cellsize * 2.)) &
                         (df['lat'] < (lat + cellsize * 2.)) &
                         (df['lon'] >= (lon - cellsize * 2.)) &
                         (df['lon'] < (lon + cellsize * 2.))]
                if df3.empty:
                    # If nothing found, place a zero here
                    newrows.append({'lon': lon,
                                    'lat': lat,
                                    'val': 0,
                                    'useme': True,
                                    'state': 'NA'})
                continue
            maxval = df.at[df2.index[0], 'val']
            df.loc[df2[df2['val'] > (maxval * 0.8)].index, 'useme'] = True

    dfall = pd.concat([df, pd.DataFrame(newrows)], ignore_index=True)
    df2 = dfall[dfall['useme']]
    xi = np.arange(reference.MW_WEST, reference.MW_EAST, cellsize)
    yi = np.arange(reference.MW_SOUTH, reference.MW_NORTH, cellsize)
    xi, yi = np.meshgrid(xi, yi)
    gridder = Rbf(df2['lon'].values, df2['lat'].values,
                  pd.to_numeric(df2['val'].values, errors='ignore'),
                  function='thin_plate')
    vals = gridder(xi, yi)
    vals[np.isnan(vals)] = 0

    rng = [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]
    cmap = nwssnow()
    mp = MapPlot(sector='iowa', axisbg='white',
                 title="Local Storm Report Snowfall Total Analysis",
                 subtitle=("Reports past 12 hours: %s"
                           "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    if df['val'].max() > 0:
        mp.contourf(xi, yi, vals, rng, cmap=cmap)
    mp.drawcounties()
    if not df.empty:
        mp.plot_values(df['lon'].values, df['lat'].values, df['val'].values,
                       fmt='%.1f', labelbuffer=2)
    mp.drawcities()
    pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
    mp.postprocess(view=view, pqstr=pqstr)
    mp.close()

    # slightly different title to help uniqueness
    mp = MapPlot(sector='iowa', axisbg='white',
                 title="Local Storm Report Snowfall Total Analysis",
                 subtitle=("Reports valid over past 12 hours: %s"
                           "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    if df['val'].max() > 0:
        mp.contourf(xi, yi, vals, rng, cmap=cmap)
    mp.drawcounties()
    mp.drawcities()
    pqstr = "plot c 000000000000 lsr_snowfall_nv.png bogus png"
    mp.postprocess(view=view, pqstr=pqstr)
    mp.close()

    mp = MapPlot(sector='midwest', axisbg='white',
                 title="Local Storm Report Snowfall Total Analysis",
                 subtitle=("Reports past 12 hours: %s"
                           "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    if df['val'].max() > 0:
        mp.contourf(xi, yi, vals, rng, cmap=cmap)
    mp.drawcities()
    pqstr = "plot c 000000000000 mw_lsr_snowfall.png bogus png"
    mp.postprocess(view=view, pqstr=pqstr)
    mp.close()


def main():
    """Do Something"""
    now = datetime.datetime.now()
    ts = now - datetime.timedelta(hours=12)
    run(ts, now, False)


if __name__ == '__main__':
    main()


class PlotTest(unittest.TestCase):
    """A runable test."""

    def test_plot(self):
        """ Test a plot"""
        run(datetime.datetime(2015, 2, 1, 0),
            datetime.datetime(2015, 2, 2, 12), True)
