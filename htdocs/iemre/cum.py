"""Fun."""
import datetime
import json
import os
import zipfile

import numpy as np
import shapefile
from paste.request import parse_formvars
from pyiem import iemre
from pyiem.util import convert_value, get_dbconn, ncopen


def application(environ, start_response):
    """Go main go"""
    os.chdir("/tmp")

    form = parse_formvars(environ)
    ts0 = datetime.datetime.strptime(form.get("date0"), "%Y-%m-%d")
    ts1 = datetime.datetime.strptime(form.get("date1"), "%Y-%m-%d")
    base = int(form.get("base", 50))
    ceil = int(form.get("ceil", 86))
    # Make sure we aren't in the future
    tsend = datetime.date.today()
    if ts1.date() >= tsend:
        ts1 = tsend - datetime.timedelta(days=1)
        ts1 = datetime.datetime(ts1.year, ts1.month, ts1.day)
    fmt = form.get("format")

    offset0 = iemre.daily_offset(ts0)
    offset1 = iemre.daily_offset(ts1)

    with ncopen(iemre.get_daily_ncname(ts0.year)) as nc:
        # 2-D precipitation, inches
        precip = np.sum(
            nc.variables["p01d"][offset0:offset1, :, :] / 25.4, axis=0
        )

        # GDD
        H = convert_value(
            nc.variables["high_tmpk"][offset0:offset1], "degK", "degF"
        )
        H = np.where(H < base, base, H)
        H = np.where(H > ceil, ceil, H)
        L = convert_value(
            nc.variables["low_tmpk"][offset0:offset1], "degK", "degF"
        )
        L = np.where(L < base, base, L)
        gdd = np.sum((H + L) / 2.0 - base, axis=0)

    if fmt == "json":
        # For example: 19013
        ugc = "IAC" + form.get("county")[2:]
        # Go figure out where this is!
        postgis = get_dbconn("postgis")
        pcursor = postgis.cursor()
        pcursor.execute(
            "SELECT ST_x(ST_Centroid(geom)), ST_y(ST_Centroid(geom)) "
            "from ugcs WHERE ugc = %s and end_ts is null",
            (ugc,),
        )
        row = pcursor.fetchone()
        lat = row[1]
        lon = row[0]
        (i, j) = iemre.find_ij(lon, lat)
        myGDD = gdd[j, i]
        myPrecip = precip[j, i]
        res = {"data": []}
        res["data"].append(
            {
                "gdd": f"{myGDD:.0f}",
                "precip": f"{myPrecip:.1f}",
                "latitude": f"{lat:.4f}",
                "longitude": f"{lon:.4f}",
            }
        )
        headers = [("Content-type", "application/json")]
        start_response("200 OK", headers)
        return [json.dumps(res).encode("ascii")]

    # Time to create the shapefiles
    basefn = f"iemre_{ts0:%Y%m%d}_{ts1:%Y%m%d}"
    w = shapefile.Writer(basefn)
    w.field("GDD", "F", 10, 2)
    w.field("PREC_IN", "F", 10, 2)

    for x in iemre.XAXIS:
        for y in iemre.YAXIS:
            w.poly(
                [
                    [
                        (x, y),
                        (x, y + iemre.DY),
                        (x + iemre.DX, y + iemre.DY),
                        (x + iemre.DX, y),
                        (x, y),
                    ]
                ]
            )

    for i in range(len(iemre.XAXIS)):
        for j in range(len(iemre.YAXIS)):
            w.record(gdd[j, i], precip[j, i])
    w.close()
    # Create zip file, send it back to the clients
    with zipfile.ZipFile(f"{basefn}.zip", "w", zipfile.ZIP_DEFLATED) as zfp:
        for suffix in ["shp", "shx", "dbf", "prj"]:
            zfp.write(f"{basefn}.{suffix}")
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="ascii") as fh:
            zfp.writestr(f"{basefn}.prj", fh.read())

    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={basefn}.zip"),
    ]
    start_response("200 OK", headers)
    with open(f"{basefn}.zip", "rb") as fh:
        content = fh.read()
    for suffix in ["zip", "shp", "shx", "dbf", "prj"]:
        os.unlink(f"{basefn}.{suffix}")

    return [content]
