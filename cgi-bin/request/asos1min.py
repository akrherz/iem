"""Support download of ASOS 1 minute data."""
from io import StringIO

from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconnc
from pyiem.webutil import iemapp

SAMPLING = {
    "1min": 1,
    "5min": 5,
    "10min": 10,
    "20min": 20,
    "1hour": 60,
}
DELIM = {"space": " ", "comma": ",", "tab": "\t", ",": ","}


def get_station_metadata(stations) -> dict:
    """build a dictionary."""
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        """
        SELECT id, name, round(ST_x(geom)::numeric, 4) as lon,
        round(ST_y(geom)::numeric, 4) as lat from stations
        where id = ANY(%s) and network ~* 'ASOS'
    """,
        (stations,),
    )
    res = {}
    for row in cursor:
        res[row["id"]] = dict(name=row["name"], lon=row["lon"], lat=row["lat"])
    pgconn.close()
    return res


def compute_prefixes(sio, form, delim, stations, tz) -> dict:
    """"""
    station_meta = get_station_metadata(stations)
    gis = form.get("gis", "no")
    prefixes = {}
    if gis == "yes":
        sio.write(
            delim.join(
                ["station", "station_name", "lat", "lon", f"valid({tz})", ""]
            )
        )
        for station in stations:
            prefixes[station] = (
                delim.join(
                    [
                        station,
                        station_meta[station]["name"].replace(delim, "_"),
                        str(station_meta[station]["lat"]),
                        str(station_meta[station]["lon"]),
                    ]
                )
                + delim
            )
    else:
        sio.write(delim.join(["station", "station_name", f"valid({tz})", ""]))
        for station in stations:
            prefixes[station] = (
                delim.join(
                    [
                        station,
                        station_meta[station]["name"].replace(delim, "_"),
                    ]
                )
                + delim
            )
    return prefixes


@iemapp()
def application(environ, start_response):
    """Handle mod_wsgi request."""
    stations = environ.get("station", [])
    if not stations:  # legacy php
        stations = environ.get("station[]", [])
    # Ensure stations is a list
    if isinstance(stations, str):
        stations = [stations]
    if not stations:
        raise IncompleteWebRequest("No station= was specified in request.")
    delim = DELIM[environ.get("delim", "comma")]
    sample = SAMPLING[environ.get("sample", "1min")]
    what = environ.get("what", "dl")
    tz = environ.get("tz", "UTC")
    varnames = environ.get("vars", [])
    if not varnames:  # legacy php
        varnames = environ.get("vars[]", [])
    if isinstance(varnames, str):
        varnames = [varnames]
    if not varnames:
        raise IncompleteWebRequest("No vars= was specified in request.")
    pgconn, cursor = get_dbconnc("asos1min")
    cursor.execute(
        """
        select *,
        to_char(valid at time zone %s, 'YYYY-MM-DD hh24:MI') as local_valid
        from alldata_1minute
        where station = ANY(%s) and valid >= %s and valid < %s and
        extract(minute from valid) %% %s = 0 ORDER by station, valid
        """,
        (tz, stations, environ["sts"], environ["ets"], sample),
    )
    headers = []
    if what == "download":
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-Disposition", "attachment; filename=changeme.txt")
        )
    else:
        headers.append(("Content-type", "text/plain"))

    sio = StringIO()
    prefixes = compute_prefixes(sio, environ, delim, stations, tz)

    sio.write(delim.join(varnames) + "\n")
    rowfmt = delim.join([f"%({var})s" for var in varnames])
    for row in cursor:
        sio.write(prefixes[row["station"]])
        sio.write(f"{row['local_valid']}{delim}")
        sio.write((rowfmt % row).replace("None", "M"))
        sio.write("\n")
    pgconn.close()

    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
