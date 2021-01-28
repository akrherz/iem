"""Dump baseline file as CSV, with GDD computed"""
import glob
import os
import datetime

from metpy.units import units
import pyiem.meteorology as met


def main():
    """Go Main Go"""
    os.chdir("baseline")
    for fn in glob.glob("*.met"):
        location = fn[:-4]
        output = open("%s.csv" % (location,), "w")
        output.write("date,high[F],low[F],precip[inch],gdd[F]\n")
        for line in open(fn):
            line = line.strip()
            if (
                not line.startswith("2012")
                and not line.startswith("2015")
                and not line.startswith("2016")
            ):
                continue
            tokens = line.split()
            valid = datetime.date(int(tokens[0]), 1, 1) + datetime.timedelta(
                days=int(tokens[1]) - 1
            )
            high = units("degC") * float(tokens[3])
            low = units("degC") * float(tokens[4])
            gdd = met.gdd(high, low, 50, 86)
            precip = units("millimeter") * float(tokens[5])
            output.write(
                ("%s,%.1f,%.1f,%.2f,%.1f\n")
                % (
                    valid.strftime("%Y-%m-%d"),
                    high.to("degF").m,
                    low.to("degF").m,
                    precip.to("inch").m,
                    gdd,
                )
            )
        output.close()


if __name__ == "__main__":
    main()
