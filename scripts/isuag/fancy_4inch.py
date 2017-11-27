"""
Generates the nice 4inch soil temperature plot by county
"""
# stdlib
import datetime
import sys

# thirdparty
import numpy as np
from scipy.interpolate import NearestNDInterpolator
import matplotlib.cm as cm
import psycopg2.extras

# pyiem
from pyiem.plot import MapPlot
from pyiem.datatypes import temperature
from pyiem.tracker import loadqc
from pyiem.network import Table
from pyiem.util import get_dbconn


def sampler(xaxis, yaxis, vals, x, y):
    """This is a hack"""
    i = 0
    while xaxis[i] < x:
        i += 1
    j = 0
    while yaxis[j] < y:
        j += 1
    return vals[i, j]


def main(argv):
    """Go Main Go"""
    nt = Table("ISUSM")
    qdict = loadqc()

    idbconn = get_dbconn('isuag', user='nobody')
    icursor = idbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    pdbconn = get_dbconn('postgis', user='nobody')
    pcursor = pdbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    day_ago = int(argv[1])
    ts = datetime.datetime.now() - datetime.timedelta(days=day_ago)

    # Query out the data
    soil_obs = []
    lats = []
    lons = []
    icursor.execute("""
        SELECT station, tsoil_c_avg_qc from sm_daily
        where valid = '%s' and tsoil_c_avg_qc > -40
        and station not in ('AHTI4', 'FRUI4')
    """ % (ts.strftime("%Y-%m-%d"), ))
    for row in icursor:
        stid = row['station']
        if qdict.get(stid, {}).get('soil4', False):
            # print '%s was QCd out' % (stid,)
            continue
        soil_obs.append(temperature(row['tsoil_c_avg_qc'], 'C').value('F'))
        lats.append(nt.sts[stid]['lat'])
        lons.append(nt.sts[stid]['lon'])

    if len(lats) < 5:
        print(("isuag/fancy_4inch found %s obs for %s"
               ) % (len(lats), ts.strftime("%Y-%m-%d")))
        return

    # Grid it
    # numxout = 40
    # numyout = 40
    # xmin = min(lons) - 2.
    # ymin = min(lats) - 2.
    # xmax = max(lons) + 2.
    # ymax = max(lats) + 2.
    # xc = (xmax-xmin)/(numxout-1)
    # yc = (ymax-ymin)/(numyout-1)

    # xo = xmin + xc * np.arange(0, numxout)
    # yo = ymin + yc * np.arange(0, numyout)

    # analysis = griddata((lons, lats), soil_obs, (xo, yo) )
    # rbfi = Rbf(lons, lats, soil_obs, function='cubic')
    # analysis = rbfi(xo, yo)
    nn = NearestNDInterpolator((lons, lats), np.array(soil_obs))
    # analysis = nn(xo, yo)

    # Query out centroids of counties...
    pcursor.execute("""SELECT ST_x(ST_centroid(the_geom)) as lon,
        ST_y(ST_centroid(the_geom)) as lat
        from uscounties WHERE state_name = 'Iowa'
    """)
    clons = []
    clats = []
    for row in pcursor:
        clats.append(row['lat'])
        clons.append(row['lon'])

    cobs = nn(clons, clats)

    mp = MapPlot(sector='iowa',
                 title=("Iowa Average 4 inch Soil Temperatures %s"
                        ) % (ts.strftime("%b %d %Y"), ),
                 subtitle=("Based on gridded analysis (black numbers) of "
                           "ISUSM network observations (red numbers)"))
    mp.contourf(clons, clats, cobs, np.arange(10, 101, 5),
                cmap=cm.get_cmap('jet'),
                units=r'$^\circ$F')
    mp.plot_values(lons, lats, soil_obs, fmt='%.0f', color='r', labelbuffer=5)
    mp.plot_values(clons, clats, cobs, fmt='%.0f', textsize=11, labelbuffer=5)
    # for lo, la, ob in zip(clons, clats, cobs):
    #    xi, yi = m.map(lo, la)
    #    txt = m.ax.text(xi, yi, "%.0f" % (ob,))
    mp.drawcounties()
    routes = "a" if day_ago >= 4 else "ac"
    pqstr = ("plot %s %s0000 soilt_day%s.png isuag_county_4inch_soil.png png"
             ) % (routes, ts.strftime("%Y%m%d"), day_ago)
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == '__main__':
    main(sys.argv)
