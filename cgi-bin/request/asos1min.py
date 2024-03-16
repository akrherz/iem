""".. title:: ASOS 1 Minute Data Request

Documentation for /cgi-bin/request/asos1min.py
----------------------------------------------

This service provides the ASOS 1 minute data provided by NCEI and is not the
"one minute data" via MADIS.  There is an availability delay of about 24 hours
due to the way NCEI collects the data from the ASOS sites.

CGI Parameters
~~~~~~~~~~~~~~

The term ``multi`` in the parameter description means that the parameter can
be specified multiple times.  You can either do this by specifying the key
and value pair multiple times or specifying the value as a comma separated
value.  For example, `station=KAMW&station=KDSM` is the same as
`station=KAMW,KDSM`.

- `delim` (optional) - The delimiter to use in the output, defaults to comma.
- `gis` (optional) - Should GIS information be included in the output, defaults
    to no.  The options are `yes` and `no`.
- `station` (required,multi) - The station identifier(s) to request data for.
- `sample` (optional) - The sampling period to request data for, defaults to
    1 minute.  The options are `1min`, `5min`, `10min`, `20min`, and `1hour`.
- `tz` (optional) - The timezone to report the data in, defaults to UTC. This
    value should be a valid timezone identifier like ``America/Chicago``.
- `what` (optional) - The output format, defaults to `download`.  The options
    are `download` and `view`.
- `vars` (required,multi) - The variable(s) to request data for.
- `{year,month,day,hour,min}1` (required) - The start timestamp for the data
    in the timezone provided by ``tz``.
- `{year,month,day,hour,min}2` (required) - The end timestamp for the data in
    the timezone provided by ``tz``.

"""

from io import StringIO

from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import ensure_list, iemapp

SAMPLING = {
    "1min": 1,
    "5min": 5,
    "10min": 10,
    "20min": 20,
    "1hour": 60,
}
DELIM = {"space": " ", "comma": ",", "tab": "\t", ",": ","}


def get_station_metadata(eviron, stations) -> dict:
    """build a dictionary."""
    cursor = eviron["iemdb.mesosite.cursor"]
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
    for station in stations:
        if station not in res:
            raise IncompleteWebRequest(f"Unknown station provided: {station}")
    return res


def compute_prefixes(sio, environ, delim, stations, tz) -> dict:
    """"""
    station_meta = get_station_metadata(environ, stations)
    gis = environ.get("gis", "no")
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


@iemapp(iemdb=["asos1min", "mesosite"], iemdb_cursor="blah", help=__doc__)
def application(environ, start_response):
    """Handle mod_wsgi request."""
    stations = ensure_list(environ, "station")
    if not stations:  # legacy php
        stations = ensure_list(environ, "station[]")
    if not stations:
        raise IncompleteWebRequest("No station= was specified in request.")
    if "sts" not in environ:
        raise IncompleteWebRequest("Insufficient start timestamp variables.")
    # Ensure we have uppercase stations
    stations = [s.upper() for s in stations]
    delim = DELIM.get(environ.get("delim", "comma"))
    if delim is None:
        raise IncompleteWebRequest(
            f"Unknown delimiter specified, please choose one of {DELIM.keys()}"
        )
    sample = SAMPLING[environ.get("sample", "1min")]
    what = environ.get("what", "dl")
    tz = environ.get("tz", "UTC")
    varnames = ensure_list(environ, "vars")
    if not varnames:  # legacy php
        varnames = ensure_list(environ, "vars[]")
    if not varnames:
        raise IncompleteWebRequest("No vars= was specified in request.")
    cursor = environ["iemdb.asos1min.cursor"]
    # get a list of columns we have in the alldata_1minute table
    cursor.execute(
        "select column_name from information_schema.columns where "
        "table_name = 'alldata_1minute' ORDER by column_name"
    )
    columns = []
    for row in cursor:
        columns.append(row["column_name"])
    # cross check varnames now
    for varname in varnames:
        if varname not in columns:
            raise IncompleteWebRequest(
                f"Unknown variable {varname} specified in request."
            )
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

    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
