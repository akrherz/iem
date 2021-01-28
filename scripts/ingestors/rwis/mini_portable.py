"""Process data from the mini and portables """
import datetime

import pytz
import psycopg2.extras
from pyiem.observation import Observation
from pyiem.util import get_dbconn


LOOKUP = {
    "miniExportM1.csv": "RAII4",
    "miniExportM2.csv": "RMYI4",
    "portableExportP1.csv": "RSWI4",
    "portableExportP2.csv": "RAGI4",
    "portableExportP3.csv": "RLMI4",
    # 'portableExportPT.csv': 'ROCI4',
    "portableExportPT.csv": "RRCI4",
    "miniExportIFB.csv": "RIFI4",
}

THRESHOLD = datetime.datetime.utcnow() - datetime.timedelta(minutes=180)
THRESHOLD = THRESHOLD.replace(tzinfo=pytz.UTC)


def processfile(icursor, filename):
    """Process this file"""
    lines = open(
        "/mesonet/data/incoming/rwis/%s" % (filename,), "r"
    ).readlines()
    if len(lines) < 2:
        return
    heading = lines[0].split(",")
    cols = lines[1].split(",")
    data = {}
    if len(cols) < len(heading):
        return
    for i, h in enumerate(heading):
        if cols[i].strip() != "/":
            data[h.strip()] = cols[i].strip()

    nwsli = LOOKUP[filename]
    if filename in ["portableExportP1.csv", "miniExportIFB.csv"]:
        ts = datetime.datetime.strptime(
            data["date_time"][:16], "%Y-%m-%d %H:%M"
        )
    else:
        ts = datetime.datetime.strptime(
            data["date_time"][:-6], "%Y-%m-%d %H:%M"
        )
    ts = ts.replace(tzinfo=pytz.UTC)
    iem = Observation(nwsli, "IA_RWIS", ts)
    if ts.year < 2010:
        print(
            ("rwis/mini_portable.py file: %s bad timestamp: %s" "")
            % (filename, data["date_time"])
        )
        return
    iem.load(icursor)

    # IEM Tracker stuff is missing

    if data.get("wind_speed", "") != "":
        iem.data["sknt"] = float(data["wind_speed"]) * 1.17
    if data.get("sub", "") != "":
        iem.data["rwis_subf"] = float(data["sub"])
    if data.get("air_temp", "") != "":
        iem.data["tmpf"] = float(data["air_temp"])
    if data.get("pave_temp", "") != "":
        iem.data["tsf0"] = float(data["pave_temp"])
    if data.get("pave_temp2", "") != "":
        iem.data["tsf1"] = float(data["pave_temp2"])
    if data.get("press", "") != "":
        iem.data["alti"] = float(data["press"])
    if data.get("wind_dir", "") != "":
        iem.data["drct"] = float(data["wind_dir"])
    iem.save(icursor)


def main():
    """Go main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for k in LOOKUP:
        processfile(icursor, k)

    pgconn.commit()


if __name__ == "__main__":
    main()
