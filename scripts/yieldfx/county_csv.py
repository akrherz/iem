"""Here we are, dumping CSV."""

import datetime
import os
import subprocess

import numpy as np
import pandas as pd
from pyiem.util import ncopen


def process(df, ncfn, south, west):
    """Do some extraction."""
    fn1 = f"/mesonet/share/pickup/yieldfx/baseline/{ncfn}"
    fn2 = f"/mesonet/share/pickup/yieldfx/2019/{ncfn}"
    if not os.path.isfile(fn1) or not os.path.isfile(fn2):
        print("Missing %s or %s" % (fn1, fn2))
        return

    with ncopen(fn1) as nc:
        with ncopen(fn2) as nc2019:
            for _, row in df.iterrows():
                if row["State"] not in [
                    "nd",
                    "sd",
                    "ne",
                    "ks",
                    "mo",
                    "ia",
                    "mn",
                    "wi",
                    "il",
                    "in",
                    "ky",
                    "oh",
                    "mi",
                ]:
                    continue
                i = int((row["long"] - west) / 0.1250)
                j = int((row["lat"] - south) / 0.1250)
                nc_prcp = nc.variables["prcp"][:, j, i]
                nc_tmax = nc.variables["tmax"][:, j, i]
                nc_tmin = nc.variables["tmin"][:, j, i]
                nc_srad = nc.variables["srad"][:, j, i]
                nc2019_prcp = nc2019.variables["prcp"][:, j, i]
                nc2019_tmax = nc2019.variables["tmax"][:, j, i]
                nc2019_tmin = nc2019.variables["tmin"][:, j, i]
                nc2019_srad = nc2019.variables["srad"][:, j, i]

                with open(
                    (
                        "/mesonet/share/pickup/yieldfx/county/"
                        "%s_%s_%.4f_%.4f.csv"
                    )
                    % (
                        row["State"].replace(" ", "_"),
                        row["County"].replace(" ", "_"),
                        0 - row["long"],
                        row["lat"],
                    ),
                    "w",
                ) as fp:
                    fp.write(
                        "year,yday,prcp (mm/day),srad (W/m^2),tmax (deg c),"
                        "tmin (deg c)\n"
                    )
                    base = datetime.date(1980, 1, 1)
                    for tstep, days in enumerate(nc.variables["time"]):
                        ts = base + datetime.timedelta(days=int(days))
                        fp.write(
                            "%s,%s,%.3f,%.3f,%.3f,%.3f\n"
                            % (
                                ts.year,
                                int(ts.strftime("%j")),
                                nc_prcp[tstep],
                                nc_srad[tstep] * 1e6 / 86400.0,
                                nc_tmax[tstep],
                                nc_tmin[tstep],
                            )
                        )
                    base = datetime.date(2019, 1, 1)
                    for tstep, days in enumerate(nc2019.variables["time"]):
                        ts = base + datetime.timedelta(days=int(days))
                        fp.write(
                            "%s,%s,%.3f,%.3f,%.3f,%.3f\n"
                            % (
                                ts.year,
                                int(ts.strftime("%j")),
                                nc2019_prcp[tstep],
                                nc2019_srad[tstep] * 1e6 / 86400.0,
                                nc2019_tmax[tstep],
                                nc2019_tmin[tstep],
                            )
                        )


def main():
    """Go Main Go."""
    df = pd.read_csv("counties.csv", header=0)
    for west in np.arange(-104, -80, 2):
        east = west + 2.0
        for south in np.arange(36, 50, 2):
            north = south + 2.0
            ncfn = "clim_%04i_%04i.tile.nc4" % (
                (90 - south) / 2,
                (180 - (0 - west)) / 2 + 1,
            )
            df2 = df[
                (df["lat"] >= south)
                & (df["lat"] < north)
                & (df["long"] >= west)
                & (df["long"] < east)
            ]
            if df2.empty:
                continue
            process(df2, ncfn, south, west)

    os.chdir("/mesonet/share/pickup/yieldfx")
    subprocess.call("zip -q -r counties.zip county", shell=True)


if __name__ == "__main__":
    main()
