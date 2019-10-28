"""
 Generate a Weather Central Formatted file of ASOS/AWOS Precip
"""

import os
import subprocess
import datetime

import psycopg2.extras
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable

IEM = get_dbconn("iem", user="nobody")
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
COOP = get_dbconn("coop", user="nobody")
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
nt = NetworkTable(("IA_ASOS", "AWOS"))


def compute_climate(sts, ets):
    sql = """
        SELECT station, sum(gdd50) as cgdd,
        sum(precip) as crain from climate WHERE valid >= '2000-%s' and
        valid < '2000-%s' and gdd50 is not null GROUP by station
    """ % (
        sts.strftime("%m-%d"),
        ets.strftime("%m-%d"),
    )
    ccursor.execute(sql)
    data = {}
    for row in ccursor:
        data[row[0]] = row
    return data


def compute_obs():
    """ Compute the GS values given a start/end time and networks to look at
    """
    sql = """
SELECT
  s.id, ST_x(s.geom) as lon, ST_y(s.geom) as lat,
  sum(CASE WHEN
   day = 'TODAY'::date and pday > 0
   THEN pday ELSE 0 END) as p01,
  sum(CASE WHEN
   day IN ('TODAY'::date,'YESTERDAY'::date) and pday > 0
   THEN pday ELSE 0 END) as p02,
  sum(CASE WHEN
    pday > 0
   THEN pday ELSE 0 END) as p03
FROM
  summary_%s c, stations s
WHERE
  s.network in ('IA_ASOS', 'AWOS') and
  s.iemid = c.iemid and
  day IN ('TODAY'::date,'YESTERDAY'::date, 'TODAY'::date - '2 days'::interval)
GROUP by s.id, lon, lat
    """ % (
        datetime.date.today().year,
    )
    icursor.execute(sql)
    data = {}
    for row in icursor:
        data[row["id"]] = row
    return data


def main():
    output = open("/tmp/wxc_airport_precip.txt", "w")
    output.write(
        """Weather Central 001d0300 Surface Data TimeStamp=%s
   6
   4 Station
   6 TODAY RAIN
   6 DAY2 RAIN
   6 DAY3 RAIN
   6 Lat
   8 Lon
"""
        % (datetime.datetime.utcnow().strftime("%Y.%m.%d.%H%M"),)
    )
    data = compute_obs()
    for sid in data:
        output.write(
            ("K%s %6.2f %6.2f %6.2f %6.3f %8.3f\n")
            % (
                sid,
                data[sid]["p01"],
                data[sid]["p02"],
                data[sid]["p03"],
                data[sid]["lat"],
                data[sid]["lon"],
            )
        )
    output.close()

    pqstr = "data c 000000000000 wxc/wxc_airport_precip.txt bogus text"
    cmd = ("/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_airport_precip.txt") % (
        pqstr,
    )
    subprocess.call(cmd, shell=True)
    os.remove("/tmp/wxc_airport_precip.txt")


if __name__ == "__main__":
    main()
