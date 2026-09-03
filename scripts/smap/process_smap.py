"""Download SMAP data from NASA."""

import warnings

import earthaccess
import numpy as np
import xarray as xr
from pyiem.grid.nav import get_nav
from pyiem.iemre import reproject2iemre
from pyiem.plot import MapPlot, get_cmap
from rasterio.transform import from_bounds

warnings.simplefilter("ignore", FutureWarning)  # earthaccess warns itself


def main():
    """Go Main Go."""
    # Requires ~/.netrc
    earthaccess.login()

    results = earthaccess.search_data(
        short_name="SPL3SMP_E",
        temporal=("2026-09-02T05:00:00", "2026-09-03T05:59:59"),
        bounding_box=(-120.0, 30.0, -100.0, 50.0),
        count=10,
    )
    file_list = earthaccess.download(results, local_path="/mesonet/tmp/")

    ds = xr.open_dataset(file_list[0], group="Soil_Moisture_Retrieval_Data_PM")
    sm_da = ds["soil_moisture_pm"]
    dim_y, dim_x = sm_da.dims
    sm_da = sm_da.rename({dim_y: "y", dim_x: "x"})

    xmin, xmax = -17367530.44, 17367530.44
    ymin, ymax = -7314540.50, 7314540.50

    # Build the Affine transform based on array shape
    height, width = sm_da.shape
    transform = from_bounds(xmin, ymin, xmax, ymax, width, height)

    sm_da = sm_da.rio.write_crs("EPSG:6933")
    sm_da = sm_da.rio.write_transform(transform)
    sm_latlon = sm_da.rio.reproject("EPSG:4326")

    iemre_sm_pm = reproject2iemre(
        sm_latlon[:],
        sm_latlon.rio.transform(),
        sm_latlon.rio.crs,
    )

    mp = MapPlot(
        sector="conus", title="SMAP PM Soil Moisture 2 September 2026"
    )
    nav = get_nav("iemre", "conus")
    mp.imshow(
        iemre_sm_pm,
        nav.affine,
        nav.crs,
        clevs=np.arange(0, 0.51, 0.1),
        extend="neither",
        clip_on=False,
        cmap=get_cmap("rainbow_r"),
        units="cm3/cm3",
    )
    mp.postprocess(filename="test.png")
    mp.close()


if __name__ == "__main__":
    main()
