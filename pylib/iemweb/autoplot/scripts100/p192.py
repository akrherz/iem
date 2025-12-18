"""Generates analysis maps of ASOS station data."""

from datetime import timedelta, timezone

import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap, to_hex
from metpy.calc import altimeter_to_station_pressure, wet_bulb_temperature
from metpy.units import units
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import utc

PDICT = {
    "cwa": "Plot by NWS Forecast Office",
    "state": "Plot by State",
    "conus": "Plot for Contiguous US",
}
PDICT2 = {
    "vsby": "Visibility",
    "feel": "Feels Like Temperature",
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "sknt": "Wind Speed",
    "relh": "Relative Humidity",
    "wetbulb": "Wet Bulb Temperature (You pick colors)",
    "wetbulb_awips": "Wet Bulb Temperature (AWIPS Color Scale)",
}
UNITS = {
    "vsby": "miles",
    "feel": "°F",
    "tmpf": "°F",
    "dwpf": "°F",
    "sknt": "kts",
    "relh": "%",
    "wetbulb": "°F",
    "wetbulb_awips": "°F",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 600, "data": True}
    utcnow = utc()
    desc["arguments"] = [
        dict(
            type="select",
            name="t",
            default="state",
            options=PDICT,
            label="Select plot extent type:",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO: (ignored if plotting state)",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State: (ignored if plotting wfo)",
        ),
        dict(
            type="select",
            name="v",
            default="vsby",
            options=PDICT2,
            label="Select statistic to plot:",
        ),
        dict(
            type="float",
            name="above",
            optional=True,
            default=9999,
            label="Remove any plotted values above threshold:",
        ),
        dict(
            type="float",
            name="below",
            optional=True,
            default=-9999,
            label="Remove any plotted values below threshold:",
        ),
        dict(
            type="datetime",
            name="valid",
            default=utcnow.strftime("%Y/%m/%d %H00"),
            label="Valid Analysis Time (UTC)",
            optional=True,
            min="1986/01/01 0000",
        ),
        dict(type="cmap", name="cmap", default="gray", label="Color Ramp:"),
    ]
    return desc


def get_df(ctx, bnds, buf=2.25):
    """Figure out what data we need to fetch here"""
    if ctx.get("valid"):
        valid = ctx["valid"].replace(tzinfo=timezone.utc)
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                sql_helper("""
            WITH mystation as (
                select id, st_x(geom) as lon, st_y(geom) as lat,
                state, wfo, elevation from stations
                where network ~* 'ASOS' and
                ST_contains(
                    ST_MakeEnvelope(:west, :south, :east, :north, 4326),
                    geom)
            )
            SELECT station, vsby, tmpf, dwpf, sknt, state, wfo, lat, lon, relh,
            feel, elevation, alti,
            abs(extract(epoch from (:valid - valid))) as tdiff from
            alldata a JOIN mystation m on (a.station = m.id)
            WHERE a.valid between :sts and :ets ORDER by tdiff ASC
            """),
                conn,
                params={
                    "west": bnds[0] - buf,
                    "south": bnds[1] - buf,
                    "east": bnds[2] + buf,
                    "north": bnds[3] + buf,
                    "valid": valid,
                    "sts": valid - timedelta(minutes=30),
                    "ets": valid + timedelta(minutes=30),
                },
            )
        df = df.groupby("station").first()
    else:
        valid = utc()
        with get_sqlalchemy_conn("iem") as conn:
            df = pd.read_sql(
                sql_helper("""
                SELECT state, wfo, tmpf, dwpf, sknt, relh, feel,
        id, network, vsby, ST_x(geom) as lon, ST_y(geom) as lat,
        elevation, alti
        FROM
        current c JOIN stations s ON (s.iemid = c.iemid)
        WHERE s.network ~* 'ASOS' and s.country = 'US' and
        valid + '80 minutes'::interval > now() and
        vsby >= 0 and vsby <= 10 and
        ST_contains(
            ST_MakeEnvelope(:west, :south, :east, :north, 4326), geom)
            """),
                conn,
                params={
                    "west": bnds[0] - buf,
                    "south": bnds[1] - buf,
                    "east": bnds[2] + buf,
                    "north": bnds[3] + buf,
                },
            )
    if df.empty:
        raise NoDataFound("Database query found no results.")
    if ctx["v"].startswith("wetbulb"):
        # somewhat expensive, so we only do when necessary
        df[ctx["v"]] = (
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
    return df.dropna(subset=[ctx["v"]]), valid


def plotter(ctx: dict):
    """Go"""
    varname = ctx["v"]

    if ctx["t"] == "state":
        bnds = reference.state_bounds[ctx["state"]]
        title = reference.state_names[ctx["state"]]
    elif ctx["t"] == "conus":
        bnds = reference.SECTORS["conus"]
        title = "Contiguous United States"
    else:
        bnds = reference.wfo_bounds[ctx["wfo"]]
        title = f"NWS CWA {ctx['_sname']}"
    df, valid = get_df(ctx, bnds)
    mp = MapPlot(
        apctx=ctx,
        sector=ctx["t"],
        state=ctx["state"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="white",
        title=f"{PDICT2[ctx['v']].split('(')[0]} for {title}",
        subtitle=f"Map valid: {valid:%d %b %Y %H:%M} UTC",
        nocaption=True,
        titlefontsize=16,
    )
    ramp = None
    if varname == "vsby":
        ramp = np.array([0.01, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 9.9])
    # Data QC, cough
    if ctx.get("above"):
        df = df[df[varname] < ctx["above"]]
    if ctx.get("below"):
        df = df[df[varname] > ctx["below"]]
    if df.empty:
        raise NoDataFound("No data found after applying thresholds")
    # with QC done, we compute ramps
    if varname != "vsby":
        ramp = np.linspace(
            df[varname].min() - 5, df[varname].max() + 5, 10, dtype="i"
        )
    cmap = get_cmap(ctx["cmap"])
    if varname == "wetbulb_awips":
        # approximately what AWIPS is using
        cmap_obj = get_cmap("jet")
        ramp = np.linspace(22, 56, 34 * 4 + 1)
        pinks = ["#ff99f5", "#ff7fff", "#f66bff"]
        pink_start = 33.2
        pink_end = 35.2
        n_pinks = len(pinks)
        # Convert the colormap to a list of hex colors
        color_list = [
            to_hex(cmap_obj(i / (len(ramp) - 1))) for i in range(len(ramp))
        ]
        # Find indices in ramp that cover the pink range
        idx_start = np.searchsorted(ramp, pink_start, side="left")
        idx_end = np.searchsorted(ramp, pink_end, side="right")
        n_indices = idx_end - idx_start
        if n_indices > 0:
            # Spread each pink over about a third of the pink range
            seg_len = n_indices // n_pinks
            for i in range(n_pinks):
                seg_start = idx_start + i * seg_len
                # Last segment takes the remainder
                seg_end = (
                    idx_start + (i + 1) * seg_len
                    if i < n_pinks - 1
                    else idx_end
                )
                for idx in range(seg_start, seg_end):
                    color_list[idx] = pinks[i]
        cmap = ListedColormap(color_list)
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            ramp,
            units=UNITS[varname],
            cmap=cmap,
            clevstride=10,
            iline=False,
        )
    else:
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            ramp,
            units=UNITS[varname],
            cmap=cmap,
        )
    if ctx["t"] == "state":
        df2 = df[df["state"] == ctx["state"]]
    else:
        df2 = df[df["wfo"] == ctx["wfo"]]

    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        df2[varname].values,
        "%.1f",
        labelbuffer=10,
    )
    if ctx["t"] != "conus":
        mp.drawcounties()
    if ctx["t"] == "cwa":
        mp.draw_cwas()

    return mp.fig, df
