"""
This page presents a sphagetti plot of river stage
and forecasts.  The plot is roughly centered on the date of your choice
with the plot showing any forecasts made three days prior to the date
and for one day afterwards.  Sorry that you have to know the station ID
prior to using this page (will fix at some point).  Presented timestamps
are hopefully all in the local timezone of the reporting station.  If
you download the data, the timestamps are all in UTC.</p>

<p>For the image format output options, you can optionally control if
forecasts, observations, or both are plotted.  For the Interactive Chart
version, this is controlled by clicking on the legend items which will
hide and show the various lines.
"""

from datetime import timedelta
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

STAGES = "low action bankfull flood moderate major record".split()
COLORS = {
    "action": "#ffff72",
    "flood": "#ffc672",
    "moderate": "#ff7272",
    "major": "#e28eff",
}
MDICT = {"primary": "Primary Field", "secondary": "Secondary Field"}
PDICT = {
    "both": "Plot both observations and forecasts",
    "fx": "Just plot forecasts",
    "obs": "Just plot observations",
}
UTC = ZoneInfo("UTC")


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 3600}
    desc["arguments"] = [
        dict(
            type="text",
            name="station",
            default="GTTI4",
            label="Enter 5 Char NWSLI Station Code (sorry):",
        ),
        dict(
            type="datetime",
            name="dt",
            default=utc().strftime("%Y/%m/%d %H%M"),
            label="Time to center plot at (UTC Time Zone):",
            min="2013/01/01 0000",
        ),
        dict(
            type="select",
            name="var",
            options=MDICT,
            label="Which Variable to Plot:",
            default="primary",
        ),
        dict(
            type="select",
            name="w",
            options=PDICT,
            label="What all to plot:",
            default="both",
        ),
    ]
    return desc


def add_context(ctx):
    """Do the common work"""

    ctx["station"] = ctx["station"].upper()[:8]
    station = ctx["station"]
    dt = ctx["dt"]

    # Attempt to get station information
    with get_sqlalchemy_conn("hml") as conn:
        df = pd.read_sql(
            "SELECT * from stations where id = %s and network ~* 'DCP'",
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("Could not find metadata for station.")
    row = df.iloc[0]
    cols = ["name", "tzname"]
    cols.extend([f"sigstage_{x}" for x in STAGES])
    for col in cols:
        ctx[col] = row[col]

    with get_sqlalchemy_conn("hml") as conn:
        ctx["fdf"] = pd.read_sql(
            f"""with fx as (
            select id, issued, primaryname, primaryunits, secondaryname,
            secondaryunits from hml_forecast where station = %s
            and generationtime between %s and %s)
        SELECT f.id,
        f.issued at time zone 'UTC' as issued,
        d.valid at time zone 'UTC' as valid,
        d.primary_value, f.primaryname,
        f.primaryunits, d.secondary_value, f.secondaryname,
        f.secondaryunits from
        hml_forecast_data_{dt.year} d JOIN fx f
        on (d.hml_forecast_id = f.id) ORDER by f.id ASC, d.valid ASC
        """,
            conn,
            params=(
                station,
                dt - timedelta(days=3),
                dt + timedelta(days=1),
            ),
            index_col=None,
        )
    if not ctx["fdf"].empty:
        ctx["fdf"]["valid"] = ctx["fdf"]["valid"].dt.tz_localize(UTC)
        ctx["fdf"]["issued"] = ctx["fdf"]["issued"].dt.tz_localize(UTC)
        for lbl in ["primary", "secondary"]:
            ctx[lbl] = (
                f"{ctx['fdf'].iloc[0][lbl + 'name']}"
                f"[{ctx['fdf'].iloc[0][lbl + 'units']}]"
            )

        # get obs
        mints = ctx["fdf"]["valid"].min()
        maxts = ctx["fdf"]["valid"].max()
    else:
        mints = dt - timedelta(days=3)
        maxts = dt + timedelta(days=3)
    with get_sqlalchemy_conn("hml") as conn:
        df = pd.read_sql(
            text("""
            SELECT valid at time zone 'UTC' as valid,
            h.label, value from hml_observed_data d
            JOIN hml_observed_keys h on (d.key = h.id)
            WHERE station = :station and
            valid between :mints and :maxts ORDER by valid ASC
            """),
            conn,
            params={"station": station, "mints": mints, "maxts": maxts},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["valid"] = df["valid"].dt.tz_localize(UTC)
    df = df.groupby(["valid", "label"]).first().reset_index()
    ctx["odf"] = df.pivot(index="valid", columns="label", values="value")
    if ctx["fdf"].empty:
        ctx["df"] = ctx["odf"].reset_index()
    else:
        ctx["fdf"] = ctx["fdf"].reset_index()
        ctx["df"] = pd.merge(
            ctx["fdf"],
            ctx["odf"],
            left_on="valid",
            right_on="valid",
            how="left",
            sort=False,
        )
    ctx["title"] = f"[{ctx['station']}] {ctx['name']}"
    ldt = ctx["dt"].replace(tzinfo=UTC).astimezone(ZoneInfo(ctx["tzname"]))
    ctx["subtitle"] = f"+/- 72 hours around {ldt:%d %b %Y %-I:%M %p %Z}"
    # Attempt to find a column in ft
    for i, col in enumerate(ctx["odf"].columns):
        if col.find("[ft]") > -1:
            ctx["primary"] = ctx["odf"].columns[i]
            break
    for i, col in enumerate(["primary", "secondary"]):
        if col not in ctx and i < len(ctx["odf"].columns):
            ctx[col] = ctx["odf"].columns[i]


def get_highcharts(ctx: dict) -> str:
    """generate highcharts"""
    add_context(ctx)
    if "df" not in ctx:
        raise NoDataFound("No Data Found.")
    df = ctx["df"]
    df["ticks"] = df["valid"].astype(np.int64) // 10**6
    lines = []
    if "id" in df.columns:
        fxs = df["id"].unique()
        for fx in fxs:
            df2 = df[df["id"] == fx]
            issued = (
                df2.iloc[0]["issued"]
                .tz_convert(ZoneInfo(ctx["tzname"]))
                .strftime("%-m/%-d %-I%p %Z")
            )
            v = df2[["ticks", ctx["var"] + "_value"]].to_json(orient="values")
            lines.append(
                """{
                name: '"""
                + issued
                + """',
                type: 'line',
                tooltip: {valueDecimal: 1},
                data: """
                + v
                + """
                }
            """
            )
    ctx["odf"]["ticks"] = ctx["odf"].index.values.view(np.int64) // 10**6
    if ctx["var"] in ctx:
        v = ctx["odf"][["ticks", ctx[ctx["var"]]]].to_json(orient="values")
        lines.append(
            """{
                name: 'Obs',
                type: 'line',
                color: 'black',
                lineWidth: 3,
                tooltip: {valueDecimal: 1},
                data: """
            + v
            + """
                }
        """
        )
    series = ",".join(lines)
    lines = []
    for stage in STAGES:
        val = ctx[f"sigstage_{stage}"]
        if val is None:
            continue
        lines.append(
            f"{{value: {val}, color: '{COLORS.get(stage, 'black')}', "
            "dashStyle: 'shortdash', "
            f"width: 2, label: {{text: '{stage}'}}}}"
        )

    plotlines = ",".join(lines)
    containername = ctx["_e"]
    return (
        """
Highcharts.chart('"""
        + containername
        + """', {
    time: {
        useUTC: false,
        timezone: '"""
        + ctx["tzname"]
        + """'
    },
    title: {text: '"""
        + ctx["title"]
        + """'},
    subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
    chart: {zoomType: 'xy'},
    tooltip: {
        shared: true,
        crosshairs: true,
        xDateFormat: '%d %b %Y %I:%M %p'
    },
    xAxis: {
        title: {text: '"""
        + ctx["tzname"]
        + """ Timezone'},
        type: 'datetime'},
    yAxis: {
        title: {text: '"""
        + ctx.get(ctx["var"], "primary")
        + """'},
        plotLines: ["""
        + plotlines
        + """]
    },
    series: ["""
        + series
        + """]
});
    """
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    add_context(ctx)
    if "df" not in ctx or (ctx["df"].empty and ctx["odf"].empty):
        raise NoDataFound("No Data Found!")
    df = ctx["df"]
    title = "\n".join([ctx["title"], ctx["subtitle"]])
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    if ctx["w"] in ["fx", "both"] and "id" in df.columns:
        fxs = df["id"].unique()
        for fx in fxs:
            df2 = df[df["id"] == fx]
            issued = (
                df2.iloc[0]["issued"]
                .tz_convert(ZoneInfo(ctx["tzname"]))
                .strftime("%-m/%-d %-I%p %Z")
            )
            ax.plot(
                df2["valid"],
                df2[f"{ctx['var']}_value"],
                zorder=2,
                label=issued,
            )
    if (
        ctx["w"] in ["obs", "both"]
        and not ctx["odf"].empty
        and ctx["var"] in ctx
        and ctx[ctx["var"]] in ctx["odf"].columns
    ):
        ax.plot(
            ctx["odf"].index.values,
            ctx["odf"][ctx[ctx["var"]]],
            lw=2,
            color="k",
            label="Obs",
            zorder=4,
        )
        ax.set_ylabel(ctx[ctx["var"]])
    ylim = ax.get_ylim()
    for stage in STAGES:
        val = ctx[f"sigstage_{stage}"]
        if val is None:
            continue
        ax.axhline(
            val,
            linestyle="-.",
            color=COLORS.get(stage, "#000000"),
            label=f"{stage} - {val}",
        )
    ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(
        mdates.AutoDateLocator(tz=ZoneInfo(ctx["tzname"]))
    )
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-d %b\n%Y", tz=ZoneInfo(ctx["tzname"]))
    )
    pos = ax.get_position()
    ax.grid(True)
    ax.set_position([pos.x0, pos.y0, 0.74, 0.8])
    ax.set_xlabel(f"Timestamps in {ctx['tzname']} Timezone")
    ax.legend(loc=(1.0, 0.0))
    fmt = "%Y-%m-%d %H:%M"
    if "issued" in df.columns:
        df["issued"] = df["issued"].apply(lambda x: x.strftime(fmt))
    df["valid"] = df["valid"].apply(lambda x: x.strftime(fmt))
    return fig, df
