"""Extract 'daily' PRISM precip by HUC6"""
import netCDF4
import geopandas as gpd
import pandas as pd
import datetime
from rasterstats import zonal_stats
from affine import Affine
import numpy as np

AFF = Affine(0.0417, 0., -125., 0., -0.0417, 49.9357)


def do_year(gdf, rows, year):
    nc = netCDF4.Dataset('/mesonet/data/prism/%s_daily.nc' % (year,))
    now = datetime.datetime(year, 1, 1)
    maxv = 0
    for i in range(nc.dimensions['time'].size):
        grid = np.flipud(nc.variables['ppt'][i, :, :])
        zs = zonal_stats(gdf, grid, affine=AFF)
        rows.append(dict(date=now, avg_precip_mm=zs[0]['mean']))
        if zs[0]['mean'] > maxv:
            maxv = zs[0]['mean']
        now += datetime.timedelta(days=1)

    print year, maxv
    nc.close()


def main():
    # Get the HUC6 we are interested in
    gdf = gpd.GeoDataFrame.from_file(("/mesonet/data/gis/static/shape/"
                                      "4326/us/huc6_01.shp"))
    gdf = gdf[gdf['HUC6'] == '070802']
    rows = []
    for yr in range(1981, 2018):
        do_year(gdf, rows, yr)

    df = pd.DataFrame(rows)
    df.to_csv('huc6.txt')

if __name__ == '__main__':
    main()
