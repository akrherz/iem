"""Extract HRRR radiation data for storage with COOP data.

Run once at 10 PM to snag calendar day stations. (RUN_50_AFTER.sh)
Run again with RUN_NOON.sh when the regular estimator runs
"""
import datetime
import os
import sys

import pytz
import pyproj
import numpy as np
import pygrib
from pyiem.util import get_dbconn, utc, logger

LOG = logger()
P4326 = pyproj.Proj("epsg:4326")
LCC = pyproj.Proj(
    (
        "+lon_0=-97.5 +y_0=0.0 +R=6367470. +proj=lcc +x_0=0.0"
        " +units=m +lat_2=38.5 +lat_1=38.5 +lat_0=38.5"
    )
)

SWITCH_DATE = utc(2014, 10, 10, 20)


def run(ts):
    """Process data for this timestamp"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    total = None
    xaxis = None
    yaxis = None
    for hr in range(5, 23):  # Only need 5 AM to 10 PM for solar
        utcts = ts.replace(hour=hr).astimezone(pytz.UTC)
        fn = utcts.strftime(
            (
                "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                "hrrr.t%Hz.3kmf00.grib2"
            )
        )
        if not os.path.isfile(fn):
            continue
        grbs = pygrib.open(fn)
        try:
            if utcts >= SWITCH_DATE:
                grb = grbs.select(name="Downward short-wave radiation flux")
            else:
                grb = grbs.select(parameterNumber=192)
        except ValueError:
            # Don't complain about 10 PM file, which may not be complete yet
            if utcts.hour not in [3, 4]:
                LOG.info("%s had no solar rad", fn)
            continue
        if not grb:
            LOG.info("Could not find SWDOWN in HRR %s", fn)
            continue
        g = grb[0]
        if total is None:
            total = g.values
            lat1 = g["latitudeOfFirstGridPointInDegrees"]
            lon1 = g["longitudeOfFirstGridPointInDegrees"]
            llcrnrx, llcrnry = LCC(lon1, lat1)
            nx = g["Nx"]
            ny = g["Ny"]
            dx = g["DxInMetres"]
            dy = g["DyInMetres"]
            xaxis = llcrnrx + dx * np.arange(nx)
            yaxis = llcrnry + dy * np.arange(ny)
        else:
            total += g.values

    if total is None:
        LOG.info("No HRRR data for %s", ts.strftime("%d %b %Y"))
        return

    # Total is the sum of the hourly values
    # We want MJ day-1 m-2
    total = (total * 3600.0) / 1000000.0

    cursor.execute(
        """
        SELECT station, ST_x(geom), ST_y(geom), temp24_hour from
        alldata a JOIN stations t on
        (a.station = t.id) where day = %s and network ~* 'CLIMATE'
        """,
        (ts.strftime("%Y-%m-%d"),),
    )
    for row in cursor:
        (x, y) = LCC(row[1], row[2])
        i = np.digitize([x], xaxis)[0]
        j = np.digitize([y], yaxis)[0]

        rad_mj = float(total[j, i])

        if rad_mj < 0:
            LOG.info("WHOA! Negative RAD: %.2f, station: %s", rad_mj, row[0])
            continue
        # if our station is 12z, then this day's data goes into 'tomorrow'
        # if our station is not, then this day is today
        date2 = ts.strftime("%Y-%m-%d")
        if row[3] in range(4, 13):
            date2 = (ts + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        cursor2.execute(
            """
            UPDATE alldata_"""
            + row[0][:2]
            + """ SET hrrr_srad = %s WHERE
            day = %s and station = %s
        """,
            (rad_mj, date2, row[0]),
        )
    cursor.close()
    cursor2.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """ Do Something"""
    if len(argv) == 4:
        sts = utc(int(argv[1]), int(argv[2]), int(argv[3]), 12, 0)
        sts = sts.astimezone(pytz.timezone("America/Chicago"))
        run(sts)

    elif len(argv) == 3:
        # Run for a given month!
        sts = utc(int(argv[1]), int(argv[2]), 1, 12, 0)
        # run for last date of previous month as well
        sts = sts.astimezone(pytz.timezone("America/Chicago"))
        sts = sts - datetime.timedelta(days=1)
        ets = sts + datetime.timedelta(days=45)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            run(now)
            now += datetime.timedelta(days=1)
    else:
        LOG.info("ERROR: call with hrrr_solarrad.py <YYYY> <mm> <dd>")


if __name__ == "__main__":
    # run main() run
    main(sys.argv)
