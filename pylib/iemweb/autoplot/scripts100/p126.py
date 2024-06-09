"""
This plot presents one of two metrics indicating
daily humidity levels as reported by a surface weather station. The
first being mixing ratio, which is a measure of the amount of water
vapor in the air.  The second being vapor pressure deficit, which reports
the difference between vapor pressure and saturated vapor pressure.
The vapor pressure calculation shown here makes no accounting for
leaf tempeature. The saturation vapor pressure is computed by the
Tetens formula (Buck, 1981).
"""

import calendar
import datetime

import metpy.calc as mcalc
import pandas as pd
from metpy.units import units
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context

PDICT = {
    "mixing_ratio": "Mixing Ratio [g/kg]",
    "vpd": "Vapor Pressure Deficit [hPa]",
}
PDICT2 = {
    "min": "Minimum",
    "mean": "Mean",
    "max": "Maximum",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Select Year to Plot",
        ),
        dict(
            type="select",
            name="var",
            default="mixing_ratio",
            label="Which Humidity Variable to Compute?",
            options=PDICT,
        ),
        {
            "type": "select",
            "options": PDICT2,
            "default": "mean",
            "label": "Which daily statistic to compute?",
            "name": "agg",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    year = ctx["year"]
    varname = ctx["var"]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            SELECT extract(year from valid) as year,
            coalesce(mslp, alti * 33.8639, 1013.25) as slp,
            extract(doy from valid) as doy, tmpf, dwpf, relh from alldata
            where station = %s and dwpf > -50 and dwpf < 90 and
            tmpf > -50 and tmpf < 120 and valid > '1950-01-01'
            and report_type = 3
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data was found.")
    # saturation vapor pressure
    # Convert sea level pressure to station pressure
    df["pressure"] = mcalc.add_height_to_pressure(
        df["slp"].values * units("millibars"),
        ctx["_nt"].sts[station]["elevation"] * units("m"),
    ).to(units("millibar"))
    # Compute the mixing ratio
    df["mixing_ratio"] = mcalc.mixing_ratio_from_relative_humidity(
        df["pressure"].values * units("millibars"),
        df["tmpf"].values * units("degF"),
        df["relh"].values * units("percent"),
    )
    # Compute the saturation mixing ratio
    df["saturation_mixingratio"] = mcalc.saturation_mixing_ratio(
        df["pressure"].values * units("millibars"),
        df["tmpf"].values * units("degF"),
    )
    df["vapor_pressure"] = mcalc.vapor_pressure(
        df["pressure"].values * units("millibars"),
        df["mixing_ratio"].values * units("kg/kg"),
    ).to(units("kPa"))
    df["saturation_vapor_pressure"] = mcalc.vapor_pressure(
        df["pressure"].values * units("millibars"),
        df["saturation_mixingratio"].values * units("kg/kg"),
    ).to(units("kPa"))
    df["vpd"] = df["saturation_vapor_pressure"] - df["vapor_pressure"]

    daily = (
        df[["year", "doy", varname]]
        .groupby(["year", "doy"])
        .agg(ctx["agg"])
        .reset_index()
    )
    if varname not in daily.columns:
        raise NoDataFound("All data is missing.")
    df2 = daily[["doy", varname]].groupby("doy").describe()

    dyear = df[df["year"] == year]
    df3 = dyear[["doy", varname]].groupby("doy").describe()
    # tricky
    df3[(varname, "diff")] = (
        df3[(varname, ctx["agg"])] - df2[(varname, "mean")]
    )

    title = (
        f"{ctx['_sname']}]:: Daily {PDICT2[ctx['agg']]} "
        f"Surface {PDICT[varname]}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    multiplier = 1000.0 if varname == "mixing_ratio" else 10.0

    ax[0].fill_between(
        df2[(varname, "min")].index.values,
        df2[(varname, "min")].values * multiplier,
        df2[(varname, "max")].values * multiplier,
        color="gray",
    )

    ax[0].plot(
        df2[(varname, "mean")].index.values,
        df2[(varname, "mean")].values * multiplier,
        label="Climatology",
    )
    ax[0].plot(
        df3[(varname, ctx["agg"])].index.values,
        df3[(varname, ctx["agg"])].values * multiplier,
        color="r",
        label=f"{year}",
    )

    lbl = (
        "Mixing Ratio ($g/kg$)"
        if varname == "mixing_ratio"
        else PDICT[varname]
    )
    ax[0].set_ylabel(lbl)
    ax[0].set_xlim(0, 366)
    ax[0].set_ylim(bottom=0)
    ax[0].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].grid(True)
    ax[0].legend(loc=2, fontsize=10)

    cabove = "b" if varname == "mixing_ratio" else "r"
    cbelow = "r" if cabove == "b" else "b"
    rects = ax[1].bar(
        df3[(varname, "diff")].index.values,
        df3[(varname, "diff")].values * multiplier,
        facecolor=cabove,
        edgecolor=cabove,
    )
    for rect in rects:
        if rect.get_height() < 0.0:
            rect.set_facecolor(cbelow)
            rect.set_edgecolor(cbelow)

    plunits = "$g/kg$" if varname == "mixing_ratio" else "hPa"
    ax[1].set_ylabel(f"{year:.0f} Departure ({plunits})")
    ax[1].set_xlim(0, 366)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].grid(True)
    return fig, df3
