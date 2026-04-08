"""Export the current forecast as a CSV for downstream usage."""

import numpy as np
from pyiem.util import ncopen


def main():
    """Go Main Go."""
    with (
        ncopen("/mesonet/data/iemre/gfs_current.nc") as nc,
        open("gfs.csv", "w") as fh,
    ):
        fh.write(
            "latitude,longitude,"
            "day1_soil_moisture_depth_i,"
            "day1_soil_temperature_depth_i,"
            "day1_air_temperature_max,day1_air_temperature_min,"
            "day1_precipitation,"
            "day2_soil_moisture_depth_i,"
            "day2_soil_temperature_depth_i,"
            "day2_air_temperature_max,day2_air_temperature_min,"
            "day2_precipitation,source,depth\n"
            ""
        )
        sm = nc.variables["soil_moisture"]
        st = nc.variables["tsoil"]  # K
        maxt = nc.variables["high_tmpk"]
        mint = nc.variables["low_tmpk"]
        precip = nc.variables["p01d"]  # mm
        for j in range(nc.dimensions["lat"].size):
            lat = nc.variables["lat"][j]
            if lat < 32 or lat > 45:
                continue
            for i in range(nc.dimensions["lon"].size):
                lon = nc.variables["lon"][i]
                if lon < -100 or lon > -80:
                    continue
                smval = sm[1, j, i]
                stval = st[1, j, i]
                if np.ma.is_masked(smval) or np.ma.is_masked(stval):
                    continue
                fh.write(
                    f"{lat:.2f},"
                    f"{lon:.2f},"
                    f"{smval:.2f},"
                    f"{(st[1, j, i] - 273.15):.2f},"
                    f"{(maxt[1, j, i] - 273.15):.2f},"
                    f"{(mint[1, j, i] - 273.15):.2f},"
                    f"{(precip[1, j, i] / 10.0):.2f},"
                    f"{sm[2, j, i]:.2f},"
                    f"{(st[2, j, i] - 273.15):.2f},"
                    f"{(maxt[2, j, i] - 273.15):.2f},"
                    f"{(mint[2, j, i] - 273.15):.2f},"
                    f"{(precip[2, j, i] / 10.0):.2f},"
                    f"GFS,0-10cm\n"
                )


if __name__ == "__main__":
    main()
