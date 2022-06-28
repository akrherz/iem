"""Hourly frequencies."""
import datetime
import calendar

import numpy as np
import pandas as pd
import matplotlib.colors as mpcolors
from pyiem.plot import get_cmap
from pyiem.plot import figure_axes, pretty_bins
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

PDICT = {"above": "At or Above Threshold", "below": "Below Threshold"}
PDICT2 = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temp",
    "feel": "Feels Like Temp",
    "p01i": "Precipitation",
    "relh": "Relative Humidity",
}
UNITS = {
    "tmpf": "F",
    "dwpf": "F",
    "feel": "F",
    "p01i": "inch",
    "relh": "%",
}
PDICT3 = {
    "freq": "Frequency",
    "min_value": "Minimum Value",
    "max_value": "Maximum Value",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["highcharts"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents hourly variable metrics from automated
    stations.  Values are
    partitioned by week of the year to smooth out some of the day to day
    variation.

    <p><strong>Updated 28 Jun 2022</strong>: Partitioning by week is now
    done by taking the day of the year divided by 7 instead of iso-week
    calculation.  This hopefully makes the data presentation more straight
    forward.
    """
    desc["data"] = True
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="tmpf",
            options=PDICT2,
            label="Which Variable:",
        ),
        dict(
            type="select",
            name="w",
            default="freq",
            label="Which statistic to plot:",
            options=PDICT3,
        ),
        dict(
            type="float",
            name="threshold",
            default=32,
            label=(
                "[For Frequency Option] Threshold "
                "(Temperature in F, RH in %, precip in inch)"
            ),
        ),
        dict(
            type="select",
            name="direction",
            default="below",
            label="[For Frequency Option] Threshold direction:",
            options=PDICT,
        ),
        dict(
            optional=True,
            type="date",
            name="sdate",
            default="1900/01/01",
            label="Inclusive Start Local Date (optional):",
        ),
        dict(
            optional=True,
            type="date",
            name="edate",
            default=datetime.date.today().strftime("%Y/%m/%d"),
            label="Exclusive End Local Date (optional):",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def get_df(ctx):
    """Get the dataframe with data."""
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    direction = ctx["direction"]
    varname = ctx["var"]
    mydir = "<" if direction == "below" else ">="
    timelimiter = ""
    if station not in ctx["_nt"].sts:
        raise NoDataFound("Unknown station metadata.")
    tzname = ctx["_nt"].sts[station]["tzname"]
    if ctx.get("sdate"):
        timelimiter += (
            f" and valid at time zone '{tzname}' >= '{ctx['sdate']}'"
        )
    if ctx.get("edate"):
        timelimiter += f" and valid at time zone '{tzname}' < '{ctx['edate']}'"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                f"""
            WITH data as (
                SELECT date(valid at time zone :tzname),
                date_trunc('hour', (valid + '10 minutes'::interval)
                at time zone :tzname) as local_valid,
                max({varname}) as d from alldata WHERE station = :station
                and {varname} is not null {timelimiter}
                and report_type = 2 GROUP by date, local_valid
            )
            SELECT (extract(doy from date) / 7)::int as week,
            extract(hour from local_valid) as hour,
            min(d) as min_value, max(d) as max_value,
            sum(case when d {mydir} :thres then 1 else 0 end),
            count(*),
            min(local_valid)::date as min_valid,
            max(local_valid)::date as max_valid
            from data GROUP by week, hour
            """
            ),
            conn,
            params={"tzname": tzname, "station": station, "thres": threshold},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data found for query")
    # Fill out the frame
    df = (
        df.set_index(["week", "hour"])
        .reindex(
            pd.MultiIndex.from_product(
                [range(53), range(24)],
                names=["week", "hour"],
            )
        )
        .reset_index()
        .assign(
            freq=lambda df_: (df_["sum"] / df["count"] * 100.0)
            .fillna(0)
            .round(1)
        )
    )
    units = r"$^\circ$F" if varname != "relh" else "%"
    if varname == "p01i":
        units = "inch"
    df2 = df[~df["min_valid"].isna()]
    title = f"{PDICT[direction]} {threshold}{units}"
    if ctx["w"] != "freq":
        title = PDICT3[ctx["w"]]
    ctx["title"] = (
        f"{ctx['_sname']}\n"
        f"Hourly {PDICT2[varname]} {title} "
        f"({df2['min_valid'].min():%-d %b %Y}-"
        f"{df2['max_valid'].max():%-d %b %Y})"
    )
    ctx["units"] = "%" if ctx["w"] == "freq" else UNITS[ctx["var"]]
    ctx["ylabel"] = f"{ctx['_nt'].sts[station]['tzname']} Timezone"
    return df


def highcharts(fdict):
    """Do highcharts."""
    ctx = get_autoplot_context(fdict, get_description())
    df = get_df(ctx)
    data = df[["week", "hour", ctx["w"]]].values.tolist()
    xlabels = []
    for dt in pd.date_range("2000/1/1", "2000/12/31", freq="7D"):
        xlabels.append(dt.strftime("%b %-d"))
    ylabels = []
    for dt in pd.date_range("2000/1/1", "2000/1/1 23:59", freq="1H"):
        ylabels.append(dt.strftime("%-I %p"))
    ylabels.append("")  # shrug
    title = ctx["title"].replace(r"$^\circ$", "&deg;").replace("\n", "<br />")

    return f"""
    var units = {repr(ctx['units'])};
    function getPointCategoryName(point, dimension) {{
        var series = point.series,
        isY = dimension === 'y',
        axis = series[isY ? 'yAxis' : 'xAxis'];
        return axis.categories[point[isY ? 'y' : 'x']];
    }}

    Highcharts.chart('ap_container', {{
        chart: {{
            type: 'heatmap',
            zoomType: 'xy'
        }},
        xAxis: {{
            categories: {xlabels}
        }},
        yAxis: {{
            categories: {ylabels},
            min: 0,
            max: 23,
            title: {{
                text: {repr(ctx['ylabel'])}
            }}
        }},
        title: {{
            text: {repr(title)}
        }},
        accessibility: {{
            point: {{
                descriptionFormatter: function (point) {{
                    var ix = point.index + 1,
                        xName = getPointCategoryName(point, 'x'),
                        yName = getPointCategoryName(point, 'y'),
                        val = point.value;
                    return ix + ' ' + xName + ' ' + yName + ', ' + val + '.';
                }}
            }}
        }},
        colorAxis: {{
            min: 0,
            max: {df[ctx['w']].max() + 1},
            minColor: '#FFFFFF',
            maxColor: Highcharts.getOptions().colors[0]
        }},
        legend: {{
            align: 'right',
            layout: 'vertical',
            margin: 0,
            verticalAlign: 'top',
            y: 25,
            symbolHeight: 280
        }},
        tooltip: {{
            formatter: function () {{
                return '<b>' + getPointCategoryName(this.point, 'x') +
                ' @ ' + getPointCategoryName(this.point, 'y') + '</b> ' +
                this.point.value +' '+ units;
            }}
        }},
        series: [{{
            name: 'Sales per employee',
            borderWidth: 1,
            data: {data}
        }}]
    }});
    """


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    data = np.ones((24, 53), "f") * -1
    df = get_df(ctx)
    for _, row in df.iterrows():
        data[int(row["hour"]), int(row["week"])] = row[ctx["w"]]
    data = np.ma.masked_where(data <= 0, data)
    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    (fig, ax) = figure_axes(title=ctx["title"], apctx=ctx)
    cmap = get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    if ctx["w"] == "freq" or ctx["var"] == "relh":
        bins = np.arange(0, 101, 5, dtype="f")
    else:
        bins = pretty_bins(df[ctx["w"]].min(), df[ctx["w"]].max())
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    res = ax.imshow(
        data,
        interpolation="nearest",
        aspect="auto",
        extent=[0, 53, 24, 0],
        cmap=cmap,
        norm=norm,
    )
    fig.colorbar(res, label=ctx["units"], extend="neither")
    ax.grid(True, zorder=11)
    ax.set_xticks(xticks)
    ax.set_ylabel(ctx["ylabel"])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    ax.set_ylim(0, 24)
    ax.set_yticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_yticklabels(
        ["12 AM", "4 AM", "8 AM", "Noon", "4 PM", "8 PM", "Mid"]
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
