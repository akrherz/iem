"""Process CoCoRaHS Stations!"""

import datetime
import sys
from zoneinfo import ZoneInfo

import requests
from pyiem.observation import Observation
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconnc, logger, utc

LOG = logger()


def safeP(v):
    """hack"""
    v = v.strip()
    if v == "T":
        return TRACE_VALUE
    if v == "NA":
        return -99
    return float(v)


def main(daysago):
    """Go Main Go"""
    dbconn, cursor = get_dbconnc("iem")

    now = datetime.datetime.now() - datetime.timedelta(days=daysago)

    lts = utc().astimezone(ZoneInfo("America/Chicago"))

    state = sys.argv[1]

    url = (
        "http://data.cocorahs.org/Cocorahs/export/exportreports.aspx"
        f"?ReportType=Daily&dtf=1&Format=CSV&State={state}&"
        f"ReportDateType=date&Date={now:%m/%d/%Y}&TimesInGMT=False"
    )
    try:
        data = (
            requests.get(url, timeout=30).content.decode("ascii").split("\r\n")
        )
    except Exception as exp:
        LOG.exception(exp)
        return

    # Process Header
    header = {}
    h = data[0].split(",")
    for i, _h in enumerate(h):
        header[_h] = i

    if "StationNumber" not in header:
        return

    for row in data[1:]:
        cols = row.split(",")
        if len(cols) < 4:
            continue
        sid = cols[header["StationNumber"]].strip()

        t = (
            cols[header["ObservationDate"]]
            + " "
            + cols[header["ObservationTime"]].strip()
        )
        ts = datetime.datetime.strptime(t, "%Y-%m-%d %I:%M %p")
        lts = lts.replace(
            year=ts.year,
            month=ts.month,
            day=ts.day,
            hour=ts.hour,
            minute=ts.minute,
        )
        iem = Observation(sid, f"{state}COCORAHS", lts)
        iem.data["coop_valid"] = lts
        iem.data["pday"] = safeP(cols[header["TotalPrecipAmt"]])
        if cols[header["NewSnowDepth"]].strip() != "NA":
            iem.data["snow"] = safeP(cols[header["NewSnowDepth"]])
        if cols[header["TotalSnowDepth"]].strip() != "NA":
            iem.data["snowd"] = safeP(cols[header["TotalSnowDepth"]])
        iem.save(cursor)
        del iem

    cursor.close()
    dbconn.commit()


def frontend():
    """Do Logic."""
    main(0)
    if datetime.datetime.now().hour == 1:
        for offset in range(1, 15):
            main(offset)


if __name__ == "__main__":
    frontend()
