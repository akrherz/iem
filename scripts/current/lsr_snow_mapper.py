"""Create an analysis of LSR snowfall reports"""
from __future__ import print_function
import datetime
import unittest
import warnings

import numpy as np
from pyiem.plot import MapPlot, nwssnow
import pyiem.reference as reference
from pyiem.util import get_dbconn
import pandas as pd
from pandas.io.sql import read_sql

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
    df['used'] = False
    df['textplot'] = True
    df.sort_values(by='val', ascending=False, inplace=True)

    # Now, we need to add in zeros, lets say we are looking at a .25 degree box
    mybuffer = 0.75
    newrows = []
    for lat in np.arange(reference.MW_SOUTH, reference.MW_NORTH, mybuffer):
        for lon in np.arange(reference.MW_WEST, reference.MW_EAST, mybuffer):
            df2 = df[(df['lat'] >= lat) & (df['lat'] < (lat+mybuffer)) &
                     (df['lon'] >= lon) & (df['lon'] < (lon+mybuffer))]
            if df2.empty:
                newrows.append(dict(lon=(lon+mybuffer/2.),
                                    lat=(lat+mybuffer/2.),
                                    val=0, used=True, textplot=False))
                continue
            maxval = df.at[df2.index[0], 'val']
            df.loc[df2[df2['val'] > (maxval * 0.5)].index, 'used'] = True
            df.loc[df2[df2['val'] < (maxval * 0.5)].index, 'textplot'] = False
    dfnew = pd.DataFrame(newrows)
    df = df.append(dfnew)
    cdf = df[df['used']]
    tdf = df[df['textplot']]

    rng = [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]
    cmap = nwssnow()
    mp = MapPlot(sector='iowa', axisbg='white',
                 title="Local Storm Report Snowfall Total Analysis",
                 subtitle=("Reports past 12 hours: %s"
                           "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    if cdf['val'].max() > 0:
        mp.contourf(cdf['lon'].values, cdf['lat'].values, cdf['val'].values,
                    rng, cmap=cmap)
    mp.drawcounties()
    if len(tdf.index) > 0:
        mp.plot_values(tdf['lon'].values, tdf['lat'].values, tdf['val'].values,
                       fmt='%.1f', labelbuffer=5)
    mp.drawcities()
    pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
    mp.postprocess(view=view, pqstr=pqstr)
    mp.close()

    # slightly different title to help uniqueness
    mp = MapPlot(sector='iowa', axisbg='white',
                 title="Local Storm Report Snowfall Total Analysis",
                 subtitle=("Reports valid over past 12 hours: %s"
                           "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    if cdf['val'].max() > 0:
        mp.contourf(cdf['lon'].values, cdf['lat'].values, cdf['val'].values,
                    rng, cmap=cmap)
    mp.drawcounties()
    mp.drawcities()
    pqstr = "plot c 000000000000 lsr_snowfall_nv.png bogus png"
    mp.postprocess(view=view, pqstr=pqstr)
    mp.close()

    mp = MapPlot(sector='midwest', axisbg='white',
                 title="Local Storm Report Snowfall Total Analysis",
                 subtitle=("Reports past 12 hours: %s"
                           "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    if cdf['val'].max() > 0:
        mp.contourf(cdf['lon'].values, cdf['lat'].values, cdf['val'].values,
                    rng, cmap=cmap)
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

    def test_plot(self):
        """ Test a plot"""
        run(datetime.datetime(2015, 2, 1, 0),
            datetime.datetime(2015, 2, 2, 12), True)
