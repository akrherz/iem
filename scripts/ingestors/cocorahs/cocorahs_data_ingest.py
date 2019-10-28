""" Process CoCoRaHS Stations!"""
import sys
import datetime

import pytz
import requests
from pyiem.observation import Observation
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn


def safeP(v):
    """hack"""
    v = v.strip()
    if v == "T":
        return TRACE_VALUE
    if v == "NA":
        return -99
    return float(v)


def main():
    """Go Main Go"""
    dbconn = get_dbconn("iem")
    cursor = dbconn.cursor()

    now = datetime.datetime.now() - datetime.timedelta(hours=3)

    lts = datetime.datetime.utcnow()
    lts = lts.replace(tzinfo=pytz.utc)
    lts = lts.astimezone(pytz.timezone("America/Chicago"))

    state = sys.argv[1]

    url = (
        "http://data.cocorahs.org/Cocorahs/export/exportreports.aspx"
        "?ReportType=Daily&dtf=1&Format=CSV&State=%s&"
        "ReportDateType=timestamp&Date=%s&TimesInGMT=False"
    ) % (state, now.strftime("%m/%d/%Y%%20%H:00%%20%P"))
    data = requests.get(url, timeout=30).content.decode("ascii").split("\r\n")

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

        t = "%s %s" % (
            cols[header["ObservationDate"]],
            cols[header["ObservationTime"]].strip(),
        )
        ts = datetime.datetime.strptime(t, "%Y-%m-%d %I:%M %p")
        lts = lts.replace(
            year=ts.year,
            month=ts.month,
            day=ts.day,
            hour=ts.hour,
            minute=ts.minute,
        )
        iem = Observation(sid, "%sCOCORAHS" % (state,), lts)
        iem.data["pday"] = safeP(cols[header["TotalPrecipAmt"]])
        if cols[header["NewSnowDepth"]].strip() != "NA":
            iem.data["snow"] = safeP(cols[header["NewSnowDepth"]])
        if cols[header["TotalSnowDepth"]].strip() != "NA":
            iem.data["snowd"] = safeP(cols[header["TotalSnowDepth"]])
        iem.save(cursor)
        del iem

    cursor.close()
    dbconn.commit()


if __name__ == "__main__":
    main()
