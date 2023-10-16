"""Serve Time Motion Location Vectors."""
import datetime
import math
import re
from io import StringIO
from zoneinfo import ZoneInfo

from pyiem.util import get_dbconnc, utc
from pyiem.webutil import iemapp

LOLA = re.compile(r"(?P<lon>[0-9\.\-]+) (?P<lat>[0-9\.\-]+)")
SQLISO = "YYYY-MM-DDThh24:MI:SSZ"


def extrapolate(lon, lat, distance, drct):
    """Fun."""
    lon2 = lon + (
        (distance * math.cos(math.radians(270.0 - drct)))
        / (111325.0 * math.cos(math.radians(lat)))
    )
    lat2 = lat + ((distance * math.sin(math.radians(270.0 - drct))) / 111325.0)
    return lon2, lat2


def gentext(sio, row, grversion):
    """Turn the database row into placefile worthy text."""
    smps = row["tml_sknt"] * 0.5144
    drct = row["tml_direction"]
    tml_valid = row["tml_valid"].astimezone(ZoneInfo("UTC"))
    duration = (row["polygon_end"] - row["tml_valid"]).total_seconds()
    distance = smps * duration
    lats = []
    lons = []
    time_range = ""
    if grversion >= 1.5:
        time_range = f"TimeRange: {row['iso_begin']} {row['iso_end']}\n"
    if row["lat"] is not None:
        lons.append(row["lon"])
        lats.append(row["lat"])
        # Point events are represented by lines
        lon2, lat2 = extrapolate(row["lon"], row["lat"], distance, drct)
        sio.write(
            f"Color: 255 255 0\n{time_range}"
            f"Line: 2,0,\"NWS Warning Track ({row['wfo']}-{row['phenomena']}"
            f"-{row['eventid']})\\n"
            f"{drct:.0f}/{row['tml_sknt']:.0f}\"\n"
            f"{row['lat']:.4f},{row['lon']:.4f}\n"
            f"{lat2:.4f},{lon2:.4f}\n"
            "End:\n"
        )
    elif row["line"] is not None:
        # Lines are shown as three sets of lines.
        for token in LOLA.findall(row["line"]):
            lons.append(float(token[0]))
            lats.append(float(token[1]))
        for seconds in [0, duration / 2.0, duration]:
            valid = tml_valid + datetime.timedelta(seconds=seconds)
            ts = valid.strftime("%H%Mz")
            sio.write(
                f"Color: 255 255 0\n{time_range}"
                f'Line: 2,0,"NWS Warning Track @{ts}'
                f"({row['wfo']}-{row['phenomena']}"
                f"-{row['eventid']})\\n"
                f"{drct:.0f}/{row['tml_sknt']:.0f}\"\n"
            )
            for lon, lat in zip(lons, lats):
                lon2, lat2 = extrapolate(lon, lat, seconds * smps, drct)
                sio.write(f"{lat2:.4f},{lon2:.4f}\n")
            sio.write("End:\n")

    # Now we place places along the track.
    sio.write("Color: 255 255 255\nThreshold:10\n\n")
    for lon, lat in zip(lons, lats):
        for minute in range(0, int(duration / 60.0) + 1):
            valid = tml_valid + datetime.timedelta(minutes=minute)
            ts = valid.strftime("%H%Mz")
            lon2, lat2 = extrapolate(lon, lat, smps * minute * 60, drct)
            sio.write(f"Place: {lat2:.4f},{lon2:.4f},{ts}\n")
    sio.write("Threshold: 999\n")


@iemapp()
def application(environ, start_response):
    """Our WSGI service."""
    grversion = float(environ.get("version", 1.0))
    is_all = "all" in environ
    phenoms = ["TO", "SV"] if is_all else ["TO"]
    pgconn, cursor = get_dbconnc("postgis")
    valid = utc()
    refresh = 60
    if "valid" in environ:
        # pylint: disable=no-value-for-parameter
        valid = datetime.datetime.strptime(
            environ.get("valid")[:16], "%Y-%m-%dT%H:%M"
        ).replace(tzinfo=ZoneInfo("UTC"))
        refresh = 86400
    t1 = valid
    t2 = valid
    tmlabel = valid.strftime("%H%Mz")
    if grversion >= 1.5 or "valid" in environ:
        # Pull larger window of data to support TimeRange
        t1 = valid - datetime.timedelta(hours=2)
        t2 = valid + datetime.timedelta(hours=2)
        tmlabel = valid.strftime("%b %d %Y %H%Mz")
    cursor.execute(
        f"""SELECT ST_x(tml_geom) as lon, ST_y(tml_geom) as lat,
        ST_AsText(tml_geom_line) as line,
        tml_valid, tml_direction, tml_sknt,
        polygon_begin, polygon_end, eventid, wfo, phenomena,
        to_char(polygon_begin at time zone 'UTC', '{SQLISO}') as iso_begin,
        to_char(polygon_end at time zone 'UTC', '{SQLISO}') as iso_end
        from sbw_{valid.year} WHERE polygon_end > %s and
        polygon_begin < %s and phenomena = ANY(%s)
        and tml_direction is not null and status != 'CAN' and
        polygon_end > polygon_begin""",
        (t1, t2, phenoms),
    )
    sio = StringIO()
    label = "TOR+SVR" if is_all else "TOR"
    sio.write(
        f"RefreshSeconds: {refresh}\n"
        "Threshold: 999\n"
        f"Title: NWS {label} @{tmlabel} Warning Time-Mot-Loc\n"
        'Font: 1, 11, 1, "Courier New"\n\n'
    )
    for row in cursor:
        gentext(sio, row, grversion)
    pgconn.close()
    start_response("200 OK", [("Content-type", "text/plain")])
    return [sio.getvalue().encode("utf-8")]
