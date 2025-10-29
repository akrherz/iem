"""
This plot presents the daily frequency of the
first station having a higher value than the second station.
"""

import calendar

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure_axes

PDICT = {
    "precip": "Precipitation",
    "avgt": "Average Temperature",
    "high": "High Temperature",
    "low": "Low Temperature",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="station",
            name="station1",
            default="IATAME",
            label="Select Station #1:",
            network="IACLIMATE",
        ),
        dict(
            type="station",
            name="station2",
            default="IATDSM",
            label="Select Station #2:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="pvar",
            default="high",
            options=PDICT,
            label="Which variable to plot?",
        ),
        dict(
            type="float",
            name="mag",
            default="1",
            label="By how much warmer [F] or wetter [inch]",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station1 = ctx["station1"]
    station2 = ctx["station2"]
    mag = ctx["mag"]
    pvar = ctx["pvar"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        WITH obs1 as (
            SELECT day, high, low, precip, (high+low)/2. as avgt from
            alldata WHERE station = :station1),
        obs2 as (
            SELECT day, high, low, precip, (high+low)/2. as avgt from
            alldata WHERE station = :station2)

        SELECT extract(doy from o.day) as doy, count(*),
        sum(case when o.high >= (t.high::numeric + :mag) then 1 else 0 end)
            as high_hits,
        sum(case when o.low >= (t.low::numeric + :mag) then 1 else 0 end)
            as low_hits,
        sum(case when o.precip >= (t.precip + :mag) then 1 else 0 end)
        as precip_hits,
        sum(case when o.avgt >= (t.avgt::numeric + :mag) then 1 else 0 end)
            as avgt_hits
        from obs1 o JOIN obs2 t on (o.day = t.day) GROUP by doy
        ORDER by doy ASC
        """),
            conn,
            params={"station1": station1, "station2": station2, "mag": mag},
            index_col="doy",
        )
    for _v in ["high", "low", "avgt", "precip"]:
        df[f"{_v}_freq[%]"] = df[f"{_v}_hits"] / df["count"] * 100.0

    (fig, ax) = figure_axes(apctx=ctx)

    ax.bar(df.index.values, df[pvar + "_freq[%]"], fc="r", ec="r")
    ax.axhline(df[pvar + "_freq[%]"].mean())
    ax.grid(True)
    ax.set_ylabel(
        ("Percentage [%%], Ave: %.1f%%") % (df[pvar + "_freq[%]"].mean(),)
    )
    v = int(mag) if pvar != "precip" else round(mag, 2)
    units = " inch" if pvar == "precip" else "°F"
    ax.set_title(
        ("%s [%s] Daily %s\n%s+%s %s Than %s [%s]")
        % (
            ctx["_nt1"].sts[station1]["name"],
            station1,
            PDICT[pvar],
            v,
            units,
            "Warmer" if pvar != "precip" else "Wetter",
            ctx["_nt2"].sts[station2]["name"],
            station2,
        )
    )
    ax.set_xlim(0, 366)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig, df
