"""Here we are, dumping CSV."""
import datetime
import os
import subprocess

import numpy as np
import pandas as pd
from pyiem.util import ncopen


def process(df, ncfn, south, west):
    """Do some extraction."""
    fn1 = "/mesonet/share/pickup/yieldfx/baseline/%s" % (ncfn, )
    fn2 = "/mesonet/share/pickup/yieldfx/2019/%s" % (ncfn, )
    if not os.path.isfile(fn1) or not os.path.isfile(fn2):
        print("Missing %s or %s" % (fn1, fn2))
        return

    nc = ncopen(fn1)
    nc2019 = ncopen(fn2)
    for _, row in df.iterrows():
        i = int((row['long'] - west) / 0.1250)
        j = int((row['lat'] - south) / 0.1250)
        nc_prcp = nc.variables['prcp'][:, j, i]
        nc_tmax = nc.variables['tmax'][:, j, i]
        nc_tmin = nc.variables['tmin'][:, j, i]
        nc_srad = nc.variables['srad'][:, j, i]
        nc2019_prcp = nc2019.variables['prcp'][:, j, i]
        nc2019_tmax = nc2019.variables['tmax'][:, j, i]
        nc2019_tmin = nc2019.variables['tmin'][:, j, i]
        nc2019_srad = nc2019.variables['srad'][:, j, i]

        fp = open(
            '/mesonet/share/pickup/yieldfx/county/%s_%s_%.4f_%.4f.csv' % (
            row['State'].replace(" ", "_"),
            row['County'].replace(" ", "_"), 0 - row['long'], row['lat']), 'w')
        fp.write(
            "year,yday,prcp (mm/day),srad (W/m^2),tmax (deg c),tmin (deg c)\n")
        base = datetime.date(1980, 1, 1)
        for tstep, days in enumerate(nc.variables['time']):
            ts = base + datetime.timedelta(days=int(days))
            fp.write("%s,%s,%.3f,%.3f,%.3f,%.3f\n" % (
                ts.year, int(ts.strftime("%j")), nc_prcp[tstep],
                nc_srad[tstep] * 1e6 / 86400., nc_tmax[tstep], nc_tmin[tstep]))
        base = datetime.date(2019, 1, 1)
        for tstep, days in enumerate(nc2019.variables['time']):
            ts = base + datetime.timedelta(days=int(days))
            fp.write("%s,%s,%.3f,%.3f,%.3f,%.3f\n" % (
                ts.year, int(ts.strftime("%j")), nc2019_prcp[tstep],
                nc2019_srad[tstep] * 1e6 / 86400.,
                nc2019_tmax[tstep], nc2019_tmin[tstep]))
        fp.close()

    nc.close()
    nc2019.close()


def main():
    """Go Main Go."""
    df = pd.read_csv('counties.csv', header=0)
    for west in np.arange(-104, -80, 2):
        east = west + 2.
        for south in np.arange(36, 50, 2):
            north = south + 2.
            ncfn = "clim_%04i_%04i.tile.nc4" % (
                (90 - south) / 2, (180 - (0 - west)) / 2 + 1
            )
            df2 = df[
                (df['lat'] >= south) & (df['lat'] < north) &
                (df['long'] >= west) & (df['long'] < east)]
            if df2.empty:
                continue
            process(df2, ncfn, south, west)

    os.chdir("/mesonet/share/pickup/yieldfx")
    subprocess.call("zip -q -r counties.zip county", shell=True)


if __name__ == '__main__':
    main()
