"""Create a hybrid maize dump file"""
from __future__ import print_function
import datetime
import subprocess

import dropbox
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import speed
from pyiem.util import get_properties, get_dbconn

SITES = ["ames", "nashua", "sutherland", "crawfordsville", "lewis"]
XREF = ["BOOI4", "NASI4", "CAMI4", "CRFI4", "OKLI4"]


def main():
    """Go Main Go"""
    nt = NetworkTable("ISUSM")
    ipgconn = get_dbconn("iem", user="nobody")
    icursor = ipgconn.cursor()
    props = get_properties()
    dbx = dropbox.Dropbox(props.get("dropbox.token"))
    today = datetime.date.today()
    for i, site in enumerate(SITES):
        # Need to figure out this year's data
        thisyear = {}
        # get values from latest yieldfx dump
        for line in open("/mesonet/share/pickup/yieldfx/%s.met" % (site,)):
            line = line.strip()
            if not line.startswith("2016"):
                continue
            tokens = line.split()
            valid = datetime.date(int(tokens[0]), 1, 1) + datetime.timedelta(
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
        and day >= '2016-01-01' ORDER by day ASC"""
        )
        for row in icursor:
            if row[1] is None or row[2] is None:
                continue
            thisyear[row[0].strftime("%m%d")]["windspeed"] = speed(
                row[1], "KTS"
            ).value("MPS")
            thisyear[row[0].strftime("%m%d")]["rh"] = row[2]

        fn = "%s_HM_%s.wth" % (site, today.strftime("%Y%m%d"))
        fh = open(fn, "w")
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
        sts = datetime.date(2016, 1, 1)
        ets = today
        now = sts
        while now < ets:
            idx = now.strftime("%m%d")
            row = [now, None, None, None, None, None, None]
            for j, key in enumerate(
                ["radn", "maxt", "mint", "rh", "rain", "windspeed"]
            ):
                row[j + 1] = thisyear[idx][key]
            fh.write(
                ("%s\t%4s\t%.3f\t%.1f\t%.1f\t%.0f\t%.1f\t%.1f\r\n")
                % (
                    row[0].year,
                    int(row[0].strftime("%j")),
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    speed(row[6], "MPS").value("KMH"),
                )
            )
            now += datetime.timedelta(days=1)
        fh.close()
        try:
            dbx.files_upload(
                open(fn, "rb").read(),
                "/Hybrid-Maize-Metfiles/%s" % (fn,),
                mode=dropbox.files.WriteMode.overwrite,
            )
            subprocess.call(
                ("mv %s /mesonet/share/pickup/yieldfx/%s.wth") % (fn, site),
                shell=True,
            )
        except Exception as exp:
            print("fail")
            print(exp)


if __name__ == "__main__":
    main()
