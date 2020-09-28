"""
TODO: add table listing each forecast's peak and peak time...
"""
import datetime

import pytz
import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

MDICT = {"primary": "Primary Field", "secondary": "Secondary Field"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 3600
    desc[
        "description"
    ] = """This page presents a sphagetti plot of river stage
    and forecasts.  The plot is roughly centered on the date of your choice
    with the plot showing any forecasts made three days prior to the date
    and for one day afterwards.  Sorry that you have to know the station ID
    prior to using this page (will fix at some point).
    """
    utc = datetime.datetime.utcnow()
    desc["arguments"] = [
        dict(
            type="text",
            name="station",
            default="EKDI4",
            label="Enter 5 Char NWSLI Station Code (sorry):",
        ),
        dict(
            type="datetime",
            name="dt",
            default=utc.strftime("%Y/%m/%d %H%M"),
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
    ]
    return desc


def get_context(fdict):
    """Do the common work"""
    pgconn = get_dbconn("hml")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())

    ctx["station"] = ctx["station"].upper()
    station = ctx["station"]
    dt = ctx["dt"]

    # Attempt to get station information
    cursor.execute(
        """
    SELECT name from stations where id = %s and network ~* 'DCP'
    """,
        (station,),
    )
    ctx["name"] = ""
    if cursor.rowcount > 0:
        row = cursor.fetchone()
        ctx["name"] = row[0]

    ctx["fdf"] = read_sql(
        """with fx as (
        select id, issued, primaryname, primaryunits, secondaryname,
        secondaryunits from hml_forecast where station = %s
        and generationtime between %s and %s)
    SELECT f.id,
    f.issued at time zone 'UTC' as issued,
    d.valid at time zone 'UTC' as valid,
    d.primary_value, f.primaryname,
    f.primaryunits, d.secondary_value, f.secondaryname,
    f.secondaryunits from
    hml_forecast_data_"""
        + str(dt.year)
        + """ d JOIN fx f
    on (d.hml_forecast_id = f.id) ORDER by f.id ASC, d.valid ASC
    """,
        pgconn,
        params=(
            station,
            dt - datetime.timedelta(days=3),
            dt + datetime.timedelta(days=1),
        ),
        index_col=None,
    )
    if not ctx["fdf"].empty:
        ctx["fdf"]["valid"] = ctx["fdf"]["valid"].dt.tz_localize(pytz.UTC)
        ctx["fdf"]["issued"] = ctx["fdf"]["issued"].dt.tz_localize(pytz.UTC)
        ctx["primary"] = "%s[%s]" % (
            ctx["fdf"].iloc[0]["primaryname"],
            ctx["fdf"].iloc[0]["primaryunits"],
        )
        ctx["secondary"] = "%s[%s]" % (
            ctx["fdf"].iloc[0]["secondaryname"],
            ctx["fdf"].iloc[0]["secondaryunits"],
        )

        # get obs
        mints = ctx["fdf"]["valid"].min()
        maxts = ctx["fdf"]["valid"].max()
    else:
        mints = dt - datetime.timedelta(days=3)
        maxts = dt + datetime.timedelta(days=3)
    df = read_sql(
        "SELECT valid, h.label, value from hml_observed_data d "
        "JOIN hml_observed_keys h on (d.key = h.id) WHERE station = %s and "
        "valid between %s and %s ORDER by valid ASC",
        pgconn,
        params=(station, mints, maxts),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    ctx["odf"] = df.pivot("valid", "label", "value")
    if not ctx["fdf"].empty:
        ctx["fdf"].reset_index(inplace=True)
        ctx["df"] = pd.merge(
            ctx["fdf"],
            ctx["odf"],
            left_on="valid",
            right_on="valid",
            how="left",
            sort=False,
        )
    ctx["title"] = "[%s] %s" % (ctx["station"], ctx["name"])
    ctx["subtitle"] = ctx["dt"].strftime("%d %b %Y %H:%M UTC")
    if "df" not in ctx or (ctx["df"].empty and not ctx["odf"].empty):
        ctx["primary"] = ctx["odf"].columns[0]
        ctx["secondary"] = ctx["odf"].columns[1]
    return ctx


def highcharts(fdict):
    """generate highcharts"""
    ctx = get_context(fdict)
    if "df" not in ctx:
        raise NoDataFound("No Data Found.")
    df = ctx["df"]
    df["ticks"] = df["valid"].astype(np.int64) // 10 ** 6
    lines = []
    fxs = df["id"].unique()
    for fx in fxs:
        df2 = df[df["id"] == fx]
        issued = df2.iloc[0]["issued"].strftime("%-m/%-d %Hz")
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
    ctx["odf"]["ticks"] = ctx["odf"].index.values.astype(np.int64) // 10 ** 6
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
    return (
        """
$("#ap_container").highcharts({
    global: {useUTC: false},
    title: {text: '"""
        + ctx["title"]
        + """'},
    subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
    chart: {zoomType: 'x'},
    tooltip: {
        shared: true,
        crosshairs: true
    },
    xAxis: {type: 'datetime'},
    yAxis: {title: {text: '"""
        + ctx.get(ctx["var"], "primary")
        + """'}},
    series: ["""
        + series
        + """]
});
    """
    )


def plotter(fdict):
    """ Go """
    ctx = get_context(fdict)
    if "df" not in ctx or (ctx["df"].empty and ctx["odf"].empty):
        raise NoDataFound("No Data Found!")
    df = ctx["df"]
    (fig, ax) = plt.subplots(1, 1, figsize=(10, 6))
    fxs = df["id"].unique()
    for fx in fxs:
        df2 = df[df["id"] == fx]
        issued = df2.iloc[0]["issued"].strftime("%-m/%-d %Hz")
        ax.plot(
            df2["valid"], df2[ctx["var"] + "_value"], zorder=2, label=issued
        )
    if not ctx["odf"].empty:
        ax.plot(
            ctx["odf"].index.values,
            ctx["odf"][ctx[ctx["var"]]],
            lw=2,
            color="k",
            label="Obs",
            zorder=4,
        )
        ax.set_ylabel(ctx[ctx["var"]])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    pos = ax.get_position()
    ax.grid(True)
    ax.set_title("%s\n%s" % (ctx["title"], ctx["subtitle"]))
    ax.set_position([pos.x0, pos.y0, 0.6, 0.8])
    ax.legend(loc=(1.0, 0.0))
    df["issued"] = df["issued"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
    df["valid"] = df["valid"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
    return fig, df


if __name__ == "__main__":
    plotter(dict(station="CIRI2"))
