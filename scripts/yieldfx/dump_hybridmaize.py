"""Create a hybrid maize dump file.

Called from RUN_12Z.sh
"""

import subprocess
from datetime import date, timedelta

from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, logger

LOG = logger()
SITES = ["ames", "nashua", "sutherland", "crawfordsville", "lewis"]
XREF = ["BOOI4", "NASI4", "CAMI4", "CRFI4", "OKLI4"]
DIRPATH = "/mesonet/share/pickup/yieldfx"


def main():
    """Go Main Go"""
    nt = NetworkTable("ISUSM")
    ipgconn = get_dbconn("iem")
    icursor = ipgconn.cursor()
    today = date.today()
    for i, site in enumerate(SITES):
        # Need to figure out this year's data
        thisyear = {}
        # get values from latest yieldfx dump
        with open(f"{DIRPATH}/{site}.met", encoding="utf-8") as fh:
            for line_in in fh:
                line = line_in.strip()
                if not line.startswith("2016"):
                    continue
                tokens = line.split()
                valid = date(int(tokens[0]), 1, 1) + timedelta(
                    days=int(tokens[1]) - 1
                )
                if valid >= today:
                    break
                thisyear[valid.strftime("%m%d")] = {
                    "radn": float(tokens[2]),
                    "maxt": float(tokens[3]),
                    "mint": float(tokens[4]),
                    "rain": float(tokens[5]),
                    "windspeed": None,
                    "rh": None,
                }
        # Supplement with DSM data
        icursor.execute(
            """
        select day, avg_sknt, avg_rh from summary where iemid = 37004
        and day >= '2021-09-01' ORDER by day ASC"""
        )
        for row in icursor:
            if row[1] is None or row[2] is None:
                continue
            thisyear[row[0].strftime("%m%d")]["windspeed"] = convert_value(
                row[1], "knot", "meter / second"
            )
            thisyear[row[0].strftime("%m%d")]["rh"] = row[2]

        fn = f"{site}_HM_{today:%Y%m%d}.wth"
        with open(fn, "w", encoding="ascii") as fh:
            fh.write(
                """\
%s        IA   Lat.(deg)= %.2f  Long.(deg)=%.2f  Elev.(m)=%.0f.\r
%.2f (Lat.)\r
year    day     Solar   T-High  T-Low   RelHum  Precip  WndSpd\r
                MJ/m2   oC      oC      %%       mm      km/hr\r
"""
                % (
                    site.upper(),
                    nt.sts[XREF[i]]["lat"],
                    nt.sts[XREF[i]]["lon"],
                    nt.sts[XREF[i]]["lat"],
                    nt.sts[XREF[i]]["elevation"],
                )
            )

            # Get the baseline obs
            sts = date(2021, 9, 1)
            ets = today
            now = sts
            while now < ets:
                idx = now.strftime("%m%d")
                ws = convert_value(
                    thisyear[idx]["windspeed"],
                    "meter / second",
                    "kilometer / hour",
                )
                fh.write(
                    f"{now:%Y}\t"
                    f"{now.timetuple().tm_yday:4.0f}\t"
                    f"{thisyear[idx]['radn']:.3f}\t"
                    f"{thisyear[idx]['maxt']:.1f}\t"
                    f"{thisyear[idx]['mint']:.1f}\t"
                    f"{thisyear[idx]['rh']:.0f}\t"
                    f"{thisyear[idx]['rain']:.1f}\t"
                    f"{ws:.1f}\r\n"
                )
                now += timedelta(days=1)
        try:
            subprocess.call(
                ["mv", fn, f"/mesonet/share/pickup/yieldfx/{site}.wth"],
            )
        except Exception as exp:
            LOG.exception(exp)


if __name__ == "__main__":
    main()
