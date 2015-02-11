"""Create an analysis of LSR snowfall reports
"""
import numpy as np
from pyiem.plot import MapPlot
import pyiem.reference as reference
import datetime
import unittest
import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()


def run(basets, endts, view):
    """Generate this plot for the given basets"""
    vals = []
    valmask = []
    lats = []
    lons = []

    pcursor.execute("""SELECT state,
        max(magnitude) as val, ST_x(geom) as lon, ST_y(geom) as lat
        from lsrs WHERE type in ('S') and magnitude >= 0 and
        valid > %s and valid < %s GROUP by state, lon, lat""", (basets, endts))
    for row in pcursor:
        vals.append(row[1])
        lats.append(row[3])
        lons.append(row[2])
        valmask.append(row[0] in ['IA', ])

    # Now, we need to add in zeros, lets say we are looking at a .25 degree box
    mybuffer = 1.0
    for lat in np.arange(reference.MW_SOUTH, reference.MW_NORTH, mybuffer):
        for lon in np.arange(reference.MW_WEST, reference.MW_EAST, mybuffer):
            found = False
            for j in range(len(lats)):
                if (lats[j] > (lat-(mybuffer/2.)) and
                    lats[j] < (lat+(mybuffer/2.)) and
                    lons[j] > (lon-(mybuffer/2.)) and
                    lons[j] < (lon+(mybuffer/2.))):
                    found = True
            if not found:
                lats.append(lat)
                lons.append(lon)
                valmask.append(False)
                vals.append(0)

    rng = [0.01, 0.1, 0.25, 0.5, 1, 2, 3, 5, 7, 9, 11, 13, 15, 17]

    m = MapPlot(sector='iowa', axisbg='white',
                title="Local Storm Report Snowfall Total Analysis",
                subtitle=("Reports past 12 hours: %s"
                          "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    m.contourf(lons, lats, vals, rng)
    m.drawcounties()
    m.plot_values(lons, lats, vals, fmt='%.1f', valmask=valmask)
    pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
    m.postprocess(view=view, pqstr=pqstr)
    m.close()

    # slightly different title to help uniqueness
    m = MapPlot(sector='iowa', axisbg='white',
                title="Local Storm Report Snowfall Total Analysis",
                subtitle=("Reports valid over past 12 hours: %s"
                          "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    m.contourf(lons, lats, vals, rng)
    m.drawcounties()
    pqstr = "plot c 000000000000 lsr_snowfall_nv.png bogus png"
    m.postprocess(view=view, pqstr=pqstr)
    m.close()

    m = MapPlot(sector='midwest', axisbg='white',
                title="Local Storm Report Snowfall Total Analysis",
                subtitle=("Reports past 12 hours: %s"
                          "" % (endts.strftime("%d %b %Y %I:%M %p"), )))
    m.contourf(lons, lats, vals, rng)
    pqstr = "plot c 000000000000 mw_lsr_snowfall.png bogus png"
    m.postprocess(view=view, pqstr=pqstr)
    m.close()


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
