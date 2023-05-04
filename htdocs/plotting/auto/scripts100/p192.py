"""Generates analysis maps of ASOS station data."""
import datetime

import numpy as np
import pandas as pd
import pytz
from metpy.calc import apparent_temperature
from metpy.units import units
from pyiem import reference
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc

PDICT = {"cwa": "Plot by NWS Forecast Office", "state": "Plot by State"}
PDICT2 = {"vsby": "Visibility", "feel": "Feels Like Temperature"}


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
        valid = ctx["valid"].replace(tzinfo=pytz.utc)
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                """
            WITH mystation as (
                select id, st_x(geom) as lon, st_y(geom) as lat,
                state, wfo from stations
                where network ~* 'ASOS' and
                ST_contains(ST_geomfromtext(
                    'SRID=4326;POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))
                            '), geom)
            )
            SELECT station, vsby, tmpf, dwpf, sknt, state, wfo, lat, lon, relh,
            abs(extract(epoch from (%s - valid))) as tdiff from
            alldata a JOIN mystation m on (a.station = m.id)
            WHERE a.valid between %s and %s ORDER by tdiff ASC
            """,
                conn,
                params=(
                    bnds[0] - buf,
                    bnds[1] - buf,
                    bnds[0] - buf,
                    bnds[3] + buf,
                    bnds[2] + buf,
                    bnds[3] + buf,
                    bnds[2] + buf,
                    bnds[1] - buf,
                    bnds[0] - buf,
                    bnds[1] - buf,
                    valid,
                    valid - datetime.timedelta(minutes=30),
                    valid + datetime.timedelta(minutes=30),
                ),
            )
        df = df.groupby("station").first()
    else:
        valid = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        with get_sqlalchemy_conn("iem") as conn:
            df = pd.read_sql(
                """
                SELECT state, wfo, tmpf, dwpf, sknt, relh,
        id, network, vsby, ST_x(geom) as lon, ST_y(geom) as lat
        FROM
        current c JOIN stations s ON (s.iemid = c.iemid)
        WHERE s.network ~* 'ASOS' and s.country = 'US' and
        valid + '80 minutes'::interval > now() and
        vsby >= 0 and vsby <= 10 and
        ST_contains(ST_geomfromtext(
            'SRID=4326;POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))'), geom)
            """,
                conn,
                params=(
                    bnds[0] - buf,
                    bnds[1] - buf,
                    bnds[0] - buf,
                    bnds[3] + buf,
                    bnds[2] + buf,
                    bnds[3] + buf,
                    bnds[2] + buf,
                    bnds[1] - buf,
                    bnds[0] - buf,
                    bnds[1] - buf,
                ),
            )
    return df, valid


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx["v"]

    if ctx["t"] == "state":
        bnds = reference.state_bounds[ctx["state"]]
        title = reference.state_names[ctx["state"]]
    else:
        bnds = reference.wfo_bounds[ctx["wfo"]]
        title = f"NWS CWA {ctx['_sname']}"
    df, valid = get_df(ctx, bnds)
    if df.empty:
        raise NoDataFound("No data was found for your query")
    mp = MapPlot(
        apctx=ctx,
        sector=("state" if ctx["t"] == "state" else "cwa"),
        state=ctx["state"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="white",
        title=f"{PDICT2[ctx['v']]} for {title}",
        subtitle=f"Map valid: {valid:%d %b %Y %H:%M} UTC",
        nocaption=True,
        titlefontsize=16,
    )
    ramp = None
    if varname == "vsby":
        ramp = np.array([0.01, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 9.9])
        valunit = "miles"
    else:  # feel
        valunit = "F"
        df["feel"] = (
            apparent_temperature(
                df["tmpf"].values * units("degF"),
                df["relh"].values * units("percent"),
                df["sknt"].values * units("knots"),
                mask_undefined=False,
            )
            .to(units("degF"))
            .m
        )
        df = df[pd.notna(df["feel"])]
    if df.empty:
        raise ValueError("No Data Found")
    # Data QC, cough
    if ctx.get("above"):
        df = df[df[varname] < ctx["above"]]
    if ctx.get("below"):
        df = df[df[varname] > ctx["below"]]
    # with QC done, we compute ramps
    if varname != "vsby":
        ramp = np.linspace(
            df[varname].min() - 5, df[varname].max() + 5, 10, dtype="i"
        )
    mp.contourf(
        df["lon"].values,
        df["lat"].values,
        df[varname].values,
        ramp,
        units=valunit,
        cmap=get_cmap(ctx["cmap"]),
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
    mp.drawcounties()
    if ctx["t"] == "cwa":
        mp.draw_cwas()

    return mp.fig, df


if __name__ == "__main__":
    plotter({"v": "feel", "valid": "2021-09-08 1500"})
