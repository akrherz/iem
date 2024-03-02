"""Dump baseline file as CSV, with GDD computed"""

import datetime
import glob
import os

import pyiem.meteorology as met
from metpy.units import units


def main():
    """Go Main Go"""
    os.chdir("baseline")
    for fn in glob.glob("*.met"):
        location = fn[:-4]
        with (
            open(f"{location}.csv", "w", encoding="ascii") as fh,
            open(fn, encoding="ascii") as fhh,
        ):
            fh.write("date,high[F],low[F],precip[inch],gdd[F]\n")
            for line in fhh:
                line = line.strip()
                if (
                    not line.startswith("2012")
                    and not line.startswith("2015")
                    and not line.startswith("2016")
                ):
                    continue
                tokens = line.split()
                valid = datetime.date(
                    int(tokens[0]), 1, 1
                ) + datetime.timedelta(days=int(tokens[1]) - 1)
                high = units("degC") * float(tokens[3])
                low = units("degC") * float(tokens[4])
                gdd = met.gdd(high, low, 50, 86)
                precip = units("millimeter") * float(tokens[5])
                fh.write(
                    f"{valid:%Y-%m-%d},{high.to('degF').m:.1f},"
                    f"{low.to('degF').m:.1f},{precip.to('inch').m:.2f},"
                    f"{gdd:.1f}\n"
                )


if __name__ == "__main__":
    main()
