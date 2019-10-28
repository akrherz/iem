"""
Generate a Weather Central Formatted data file with HVTEC River information
in it!
"""
import re
import os
import subprocess

import psycopg2.extras
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis", user="nobody")
    pcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    svr_dict = {
        "N": "None",
        "0": "Aerial",
        "1": "Minor",
        "2": "Moderate",
        "3": "Major",
        "U": "Unknown",
    }

    fh = open("/tmp/wxc_iemrivers.txt", "w")
    fh.write(
        """Weather Central 001d0300 Surface Data TimeStamp=%s
  10
   5 Station
  64 River Forecast Point
   7 Lat
   7 Lon
   7 Flood Stage
   7 Current Stage
   7 Forecast Stage
  12 Severity
  10 Trend
 128 Forecast Text
"""
        % (utc().strftime("%Y.%m.%d.%H%M"),)
    )

    pcursor.execute(
        """
        select r.*, h.*, ST_x(h.geom) as lon, ST_y(h.geom) as lat
        from hvtec_nwsli h, riverpro r,
        (select distinct hvtec_nwsli from warnings_%s WHERE
         status NOT IN ('EXP','CAN') and phenomena = 'FL' and
         significance = 'W') as foo
        WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli
    """
        % (utc().year,)
    )

    for row in pcursor:
        # nwsli = row['nwsli']
        ft = re.findall(r"([0-9]+\.?[0-9]?)", row["flood_text"])
        if not ft:
            continue
        fstage = float(ft[-1])

        ft = re.findall(r"([0-9]+\.?[0-9]?)", row["stage_text"])
        if not ft:
            continue
        stage = float(ft[-1])

        forecast_text = row["forecast_text"]
        trend = "Unknown"
        if forecast_text.find("FALL ") > 0:
            trend = "Falling"
        if forecast_text.find("RISING ") > 0:
            trend = "Rising"
        if forecast_text.find("RISE ") > 0:
            trend = "Rising"
        ft = re.findall(r"([0-9]+\.?[0-9]?)", forecast_text)
        if not ft:
            ft = [0]
        xstage = float(ft[-1])

        severe = svr_dict.get(row["severity"], "")

        rname = "%s %s %s" % (row["river_name"], row["proximity"], row["name"])
        ftxt = re.sub(r"\s+", " ", row["forecast_text"].strip())
        fh.write(
            (
                "%5s %-64.64s %7.2f %7.2f %7.2f %7.2f %7.2f "
                "%-12.12s %-10.10s %-128.128s\n"
            )
            % (
                row["nwsli"],
                rname,
                row["lat"],
                row["lon"],
                fstage,
                stage,
                xstage,
                severe,
                trend,
                ftxt,
            )
        )

    fh.close()

    pqstr = "data c 000000000000 wxc/wxc_iemrivers.txt bogus text"
    cmd = "/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_iemrivers.txt" % (pqstr,)
    subprocess.call(cmd, shell=True)
    os.remove("/tmp/wxc_iemrivers.txt")


if __name__ == "__main__":
    main()
