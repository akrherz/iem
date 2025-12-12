"""Generate current plot of Temperature"""

from datetime import datetime

import pandas as pd
from metpy.calc import altimeter_to_station_pressure, wet_bulb_temperature
from metpy.units import units
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot
from pyiem.util import utc


def get_df():
    """Get my data"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper("""
        SELECT s.id as station, s.network, tmpf, dwpf, alti, elevation,
        ST_x(s.geom) as lon, ST_y(s.geom) as lat
        FROM current c, stations s
        WHERE s.network ~* 'ASOS' and s.country = 'US' and
        s.state not in ('HI', 'AK') and
        s.iemid = c.iemid and
        (valid + '30 minutes'::interval) > now() and
        tmpf >= -50 and tmpf < 140
        """),
            conn,
            index_col="station",
        )
    return df


def main():
    """GO!"""
    now = datetime.now()

    df = get_df()
    df["wetbulb"] = (
        wet_bulb_temperature(
            altimeter_to_station_pressure(
                df["alti"].values * units.inHg,
                df["elevation"].values * units.meter,
            ),
            df["tmpf"].values * units.degF,
            df["dwpf"].values * units.degF,
        )
        .to(units.degF)
        .magnitude
    )
    rng = range(-30, 120, 2)

    title = {
        "tmpf": "Air Temperature",
        "wetbulb": "Wet Bulb Temperature",
    }
    for sector in ["iowa", "midwest", "conus"]:
        for varname in ["tmpf", "wetbulb"]:
            mp = MapPlot(
                axisbg="white",
                sector=sector,
                title=f"{sector.capitalize()} 2 meter {title[varname]}",
                subtitle=now.strftime("%d %b %Y %-I:%M %p"),
            )
            mp.contourf(
                df["lon"].values,
                df["lat"].values,
                df[varname].values,
                rng,
                clevstride=5,
                units="F",
            )
            mp.plot_values(
                df["lon"].values,
                df["lat"].values,
                df[varname].values,
                fmt="%.0f",
            )
            if sector == "iowa":
                mp.drawcounties()
            pqstr = (
                f"plot ac {utc():%Y%m%d%H}00 {sector}_tmpf.png "
                f"{sector}_{varname}_{utc():%H}.png png"
            )
            mp.postprocess(view=False, pqstr=pqstr)
            mp.close()


if __name__ == "__main__":
    main()
