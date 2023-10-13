"""Support download of ASOS 1 minute data."""
import datetime
from io import StringIO
from zoneinfo import ZoneInfo

from paste.request import parse_formvars
from pyiem.util import get_dbconnc

SAMPLING = {
    "1min": 1,
    "5min": 5,
    "10min": 10,
    "20min": 20,
    "1hour": 60,
}
DELIM = {"space": " ", "comma": ",", "tab": "\t", ",": ","}


def get_time(form, tz):
    """Figure out the timestamp."""
    sts = datetime.datetime(
        int(form.get("year1")),
        int(form.get("month1")),
        int(form.get("day1")),
        int(form.get("hour1")),
        int(form.get("minute1")),
        tzinfo=ZoneInfo(tz),
    )
    ets = datetime.datetime(
        int(form.get("year2")),
        int(form.get("month2")),
        int(form.get("day2")),
        int(form.get("hour2")),
        int(form.get("minute2")),
        tzinfo=ZoneInfo(tz),
    )
    return sts, ets


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


def application(environ, start_response):
    """Handle mod_wsgi request."""
    form = parse_formvars(environ)
    stations = form.getall("station")
    if not stations:  # legacy php
        stations = form.getall("station[]")
    delim = DELIM[form.get("delim", "comma")]
    sample = SAMPLING[form.get("sample", "1min")]
    what = form.get("what", "dl")
    tz = form.get("tz", "UTC")
    # legacy
    if tz == "CST6CDT":
        tz = "America/Chicago"
    sts, ets = get_time(form, tz)
    varnames = form.getall("vars")
    if not varnames:  # legacy php
        varnames = form.getall("vars[]")
    pgconn, cursor = get_dbconnc("asos1min")
    cursor.execute(
        """
        select *,
        to_char(valid at time zone %s, 'YYYY-MM-DD hh24:MI') as local_valid
        from alldata_1minute
        where station = ANY(%s) and
        valid >= %s and valid < %s and
        extract(minute from valid) %% %s = 0 ORDER by station, valid
        """,
        (tz, stations, sts, ets, sample),
    )
    headers = []
    if what == "download":
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-Disposition", "attachment; filename=changeme.txt")
        )
    else:
        headers.append(("Content-type", "text/plain"))
    start_response("200 OK", headers)

    sio = StringIO()
    prefixes = compute_prefixes(sio, form, delim, stations, tz)

    sio.write(delim.join(varnames) + "\n")
    rowfmt = delim.join([f"%({var})s" for var in varnames])
    for row in cursor:
        sio.write(prefixes[row["station"]])
        sio.write(f"{row['local_valid']}{delim}")
        sio.write((rowfmt % row).replace("None", "M"))
        sio.write("\n")
    pgconn.close()

    return [sio.getvalue().encode("ascii")]
