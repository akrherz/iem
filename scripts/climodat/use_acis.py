"""Use data provided by ACIS to replace climodat data."""
import sys
import datetime

import requests
from pyiem.util import get_dbconn, logger
from pyiem.reference import TRACE_VALUE

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnData"


def safe(val):
    """Hack"""
    if val in ['M', 'S']:
        return None
    if val == 'T':
        return TRACE_VALUE
    try:
        return float(val)
    except ValueError:
        LOG.info("failed to convert %s to float, using None", repr(val))


def main(station, acis_station):
    """Do the query and work

    Args:
      station (str): IEM Station identifier ie IA0200
      acis_station (str): the ACIS identifier ie 130197
    """
    table = "alldata_%s" % (station[:2],)
    payload = {"sid": acis_station,
               "sdate": "1850-01-01",
               "edate": datetime.date.today().strftime("%Y-%m-%d"),
               "elems": "maxt,mint,pcpn,snow,snwd"}
    req = requests.post(SERVICE, json=payload)
    j = req.json()
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor()
    for row in j['data']:
        date = row[0]
        (high, low, precip, snow, snowd) = map(safe, row[1:])
        if all([a is None for a in (high, low, precip, snow, snowd)]):
            continue
        cursor.execute("""
            UPDATE """ + table + """ SET high = %s, low = %s, precip = %s,
            snow = %s, snowd = %s WHERE station = %s and day = %s
        """, (high, low, precip, snow, snowd, station, date))
        if cursor.rowcount == 0:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            sday = "%02i%02i" % (date.month, date.day)
            LOG.info("Adding entry for %s", date)
            cursor.execute("""
                INSERT into """ + table + """ (station, day,
                high, low, precip, snow, snowd, sday, year, month, estimated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'f')
            """, (station, date, high, low, precip, snow, snowd, sday,
                  date.year, date.month))
    cursor.close()
    pgconn.commit()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
