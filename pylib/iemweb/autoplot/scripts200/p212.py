"""
This plot presents the daily climatology range of a sounding
variable along with a given year's values.

<p>The Storm Prediction Center website has a
<a href="https://www.spc.noaa.gov/exper/soundingclimo/">
very similiar tool</a> that you may want to check out.</p>

<p>The max and min monthly values are labeled within the plot.</p>

<p>If you select to plot both 00 and 12 UTC, the climatology is computed
seperately at 00 and 12 UTC.  The chart gets more noisey when doing so.</p>
"""

import datetime

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, mm2inch
from sqlalchemy import text

PDICT = {"00": "00 UTC", "12": "12 UTC", "both": "00 + 12 UTC"}
PDICT3 = {
    "tmpc": "Air Temperature (°C)",
    "dwpc": "Dew Point (°C)",
    "el_agl_m": "Equalibrium Level (m AGL)",
    "el_pressure_hpa": "Equalibrium Pressure (hPa)",
    "el_tmpc": "Equalibrium Level Temperature (°C)",
    "height": "Height (m)",
    "lcl_agl_m": "Lifted Condensation Level (m AGL)",
    "lcl_pressure_hpa": "Lifted Condensation Level (hPa)",
    "lcl_tmpc": "Lifted Condensation Level Temperature (°C)",
    "lfc_agl_m": "Lifted of Free Convection (m AGL)",
    "lfc_pressure_hpa": "Lifted of Free Convection (hPa)",
    "lfc_tmpc": "Lifted of Free Convection Temperature (°C)",
    "mlcape_jkg": "Mixed Layer (100hPa) CAPE (J/kg)",
    "mlcin_jkg": "Mixed Layer (100hPa) CIN (J/kg)",
    "mucape_jkg": "Most Unstable CAPE (J/kg)",
    "mucin_jkg": "Most Unstable CIN (J/kg)",
    "pwater_mm": "Precipitable Water (mm)",
    "pwater_in": "Precipitable Water (inch)",
    "shear_sfc_1km_smps": "Shear 0-1km AGL Magnitude (m/s)",
    "shear_sfc_3km_smps": "Shear 0-3km AGL Magnitude (m/s)",
    "shear_sfc_6km_smps": "Shear 0-6km AGL Magnitude (m/s)",
    "srh_sfc_1km_neg": "Storm Relative Helicity Negative (0-1km) (m2/s2)",
    "srh_sfc_1km_pos": "Storm Relative Helicity Positive (0-1km) (m2/s2)",
    "srh_sfc_1km_total": "Storm Relative Helicity Total (0-1km) (m2/s2)",
    "srh_sfc_3km_neg": "Storm Relative Helicity Negative (0-3km) (m2/s2)",
    "srh_sfc_3km_pos": "Storm Relative Helicity Positive (0-3km) (m2/s2)",
    "srh_sfc_3km_total": "Storm Relative Helicity Total (0-3km) (m2/s2)",
    "sbcape_jkg": "Surface Based CAPE (J/kg)",
    "sbcin_jkg": "Surface Based CIN (J/kg)",
    "sweat_index": "Sweat Index",
    "total_totals": "Total Totals (°C)",
    "smps": "Wind Speed (mps)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["highcharts"] = True
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="RAOB",
            default="_OAX",
            label="Select Station:",
        ),
        dict(
            type="year",
            min=1946,
            default=datetime.date.today().year,
            name="year",
            label="Year to Plot",
        ),
        dict(
            type="select",
            name="hour",
            default="00",
            options=PDICT,
            label="Which Routine Sounding:",
        ),
        dict(
            type="select",
            name="var",
            default="tmpc",
            options=PDICT3,
            label="Which Sounding Variable to Plot:",
        ),
        dict(
            type="int",
            name="level",
            default=500,
            label="Which Pressure (hPa) level:",
        ),
    ]
    return desc


def get_data(ctx):
    """Get the data for what was choosen."""
    station = ctx["station"]
    if station not in ctx["_nt"].sts:  # This is needed.
        raise NoDataFound("Unknown station metadata.")
    stations = [station]
    name = ctx["_nt"].sts[station]["name"]
    if station.startswith("_"):
        name = ctx["_nt"].sts[station]["name"].split("--")[0]
        stations = (
            ctx["_nt"].sts[station]["name"].split("--")[1].strip().split(" ")
        )
    varname = ctx["var"]
    varname_final = ctx["var"]
    if varname == "pwater_in":
        varname = "pwater_mm"
    level = ctx["level"]
    params = {
        "stations": stations,
        "level": level,
    }
    hour = ctx["hour"]
    hrlimiter = "and extract(hour from f.valid at time zone 'UTC') in (0, 12)"
    if hour != "both":
        hrlimiter = "and extract(hour from f.valid at time zone 'UTC') = :hour"
        params["hour"] = int(hour)
    if varname in ["tmpc", "dwpc", "height", "smps"]:
        ctx["leveltitle"] = f" @ {level} hPa"
        with get_sqlalchemy_conn("raob") as conn:
            dfin = pd.read_sql(
                text(
                    "select "
                    "extract(year from f.valid at time zone 'UTC')::int "
                    "as year, f.valid at time zone 'UTC' as utc_valid, "
                    f"{varname} from raob_profile p JOIN raob_flights f on "
                    "(p.fid = f.fid) WHERE f.station = ANY(:stations) "
                    f"{hrlimiter} and p.pressure = :level  "
                    f"and {varname} is not null ORDER by valid ASC"
                ),
                conn,
                params=params,
                index_col="utc_valid",
            )
            if not dfin.empty:
                # Drop duplicates :(
                dfin = dfin.groupby("utc_valid").first()
    else:
        ctx["leveltitle"] = ""
        with get_sqlalchemy_conn("raob") as conn:
            dfin = pd.read_sql(
                text(
                    "select "
                    "extract(year from valid at time zone 'UTC')::int "
                    "as year, valid at time zone 'UTC' as utc_valid, "
                    f"{varname} from raob_flights f WHERE "
                    "station = ANY(:stations) "
                    f"{hrlimiter} and {varname} is not null ORDER by valid ASC"
                ),
                conn,
                params=params,
                index_col="utc_valid",
            )
    if dfin.empty:
        raise NoDataFound("No Data Found.")
    if varname_final == "pwater_in":
        dfin["pwater_in"] = mm2inch(dfin["pwater_mm"])
    dfin["sday"] = dfin.index.strftime("%m%d%H")
    # Drop leapday if this year does not have it.
    try:
        datetime.date(ctx["year"], 2, 29)
    except ValueError:
        dfin = dfin[dfin["sday"].str.slice(0, 4) != "0229"]
    # create the climatology dataframe
    df = dfin[["sday", ctx["var"]]].groupby("sday").describe()
    # Merge in this year's obs
    df[f"{ctx['var']}_{ctx['year']}"] = dfin[
        dfin["year"] == ctx["year"]
    ].set_index("sday")[ctx["var"]]
    # Merge in the year of max value
    mx = (
        dfin.sort_values(ctx["var"], ascending=False)
        .drop_duplicates("sday")
        .set_index("sday")
    )
    df[f"{ctx['var']}_max_year"] = mx["year"]
    # Merge in the year of max value
    mx = (
        dfin.sort_values(ctx["var"], ascending=True)
        .drop_duplicates("sday")
        .set_index("sday")
    )
    df[f"{ctx['var']}_min_year"] = mx["year"]

    # Create a utc_valid column for later usage
    df["utc_valid"] = pd.to_datetime(
        str(ctx["year"]) + df.index,
        format="%Y%m%d%H",
    ).tz_localize("UTC")
    ctx["df"] = df
    ctx["dfin"] = dfin

    label = "00 + 12 UTC" if hour == "both" else f"{int(hour):02.0f} UTC"
    ctx["title"] = (
        f"{station} {name} {label} Sounding "
        f"({dfin['year'].index[0]:%Y-%m-%d %H}z - "
        f"{dfin['year'].index[-1]:%Y-%m-%d %H}z)\n"
        f"{PDICT3[varname]} {ctx['leveltitle']}"
    )


def get_highcharts(ctx: dict) -> str:
    """Make highcharts output."""
    get_data(ctx)
    df = ctx["df"]
    df["ticks"] = df["utc_valid"].astype("int64") // 1e6
    units = PDICT3[ctx["var"]].split()[-1].replace("(", "").replace(")", "")
    myyearcol = f"{ctx['var']}_{ctx['year']}"
    title = ctx["title"].replace("\n", "\\n")
    tc = ("ticks", "")
    mx = df[f"{ctx['var']}_max_year"]
    mn = df[f"{ctx['var']}_min_year"]
    containername = ctx["_e"]
    res = f"""
    var max_years = {mx.values.tolist()};
    var min_years = {mn.values.tolist()};

Highcharts.chart("{containername}", {{
        title: {{
            text: "{title}"
        }},
        exporting: {{
            enabled: true
        }},
        chart: {{
            zoomType: 'x',
        }},
        plotOptions: {{
            line: {{
                turboThreshold: 0,
            }}
        }},
        xAxis: {{
            type: 'datetime'
        }},
        yAxis: {{
            title: {{
                text: "{PDICT3[ctx['var']]}"
            }}
        }},
        tooltip: {{
            crosshairs: true,
            shared: true,
            valueSuffix: ' {units}',
            valueDecimals: 2
        }},
        series: [
            {{
                name: "{' '.join(PDICT3[ctx["var"]].split()[:-1])}",
                data: {
                    df[["ticks", myyearcol]]
                    .replace({np.nan: None})
                    .values
                    .tolist()
                },
                zIndex: 3,
                color: "#FF0000",
                lineWidth: 2,
                marker: {{
                    enabled: false
                }},
                type: 'line'
            }}, {{
                name: "Average",
                data: {
                    df[[tc, (ctx["var"], "mean")]]
                    .replace({np.nan: None})
                    .values
                    .tolist()
                },
                zIndex: 2,
                color: "#000000",
                lineWidth: 2,
                marker: {{
                    enabled: false
                }},
                type: 'line'
            }}, {{
                name: "Range",
                data: {
                    df[[tc, (ctx["var"], "min"), (ctx["var"], "max")]]
                    .replace({np.nan: None})
                    .values
                    .tolist()
                },
                type: "arearange",
                lineWidth: 0,
                linkedTo: ":previous",
                color: "#ADD8E6",
                fillOpacity: 0.3,
                zIndex: 0,
                tooltip: {{
                    pointFormatter: function() {{
                        var s = '<span style="color:' + this.color +
                            '">\u25cf</span> '+
                            this.series.name + ': <b>' + this.low + ' (' +
                            min_years[this.index] +') to ' + this.high + ' ('+
                            max_years[this.index] +')</b><br/>';
                        return s;
                    }}
                }}
            }}, {{
                name: "25-75 %tile",
                data: {
                    df[[tc, (ctx["var"], "25%"), (ctx["var"], "75%")]]
                    .replace({np.nan: None})
                    .values
                    .tolist()
                },
                type: "arearange",
                lineWidth: 0,
                linkedTo: ":previous",
                color: "#D2B48C",
                fillOpacity: 0.3,
                zIndex: 0
            }}
        ]
    }});
    """
    return res.replace("None", "null")


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    get_data(ctx)
    df = ctx["df"]
    fig, ax = figure_axes(apctx=ctx, title=ctx["title"])
    ax.set_position([0.1, 0.1, 0.88, 0.8])
    colname = f"{ctx['var']}_{ctx['year']}"
    x = df["utc_valid"].values
    ax.plot(x, df[colname].values, label=str(ctx["year"]), zorder=4, color="r")
    ax.fill_between(
        x,
        df[ctx["var"], "min"].values,
        df[ctx["var"], "max"].values,
        zorder=1,
        color="lightblue",
    )
    ax.fill_between(
        x,
        df[ctx["var"], "25%"].values,
        df[ctx["var"], "75%"].values,
        zorder=2,
        color="tan",
        label="25-75 %tile",
    )
    ax.plot(x, df[ctx["var"], "mean"].values, color="k", zorder=3, label="Avg")
    # buffer out the yaxis some more
    maxval = ctx["dfin"][ctx["var"]].max()
    minval = ctx["dfin"][ctx["var"]].min()
    drange = maxval - minval
    ax.set_ylim(minval - drange * 0.1, maxval + drange * 0.1)
    dy = drange * 0.01

    minmax = (
        ctx["dfin"]
        .loc[:, ctx["var"]]
        .groupby(lambda idx_: idx_.month)
        .agg(["max", "idxmax", "min", "idxmin"])
    )
    for month, row in minmax.iterrows():
        sts = datetime.date(ctx["year"], int(month), 1)
        ets = (sts + datetime.timedelta(days=35)).replace(day=1)
        ax.plot([sts, ets], [row["max"], row["max"]], zorder=3, color="b")
        ax.text(
            sts + datetime.timedelta(days=15),
            row["max"] + dy,
            f"{row['idxmax'].year}\n"
            f"{row['idxmax']:%-m/%-d %H}z\n{row['max']:.2f}",
            ha="center",
            bbox=dict(color="white", alpha=0.5),
        )
        # Values near zero are very likely irrelevant
        if abs(row["min"] - 0) < 0.001:
            continue
        ax.plot([sts, ets], [row["min"], row["min"]], zorder=3, color="b")
        ax.text(
            sts + datetime.timedelta(days=15),
            row["min"] - dy,
            f"{row['idxmin'].year}\n"
            f"{row['idxmin']:%-m/%-d %H}z\n{row['min']:.2f}",
            ha="center",
            va="top",
            bbox=dict(color="white", alpha=0.5),
        )
    ax.legend()
    ax.set_ylabel(PDICT3[ctx["var"]])
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.set_xlabel(f"Day of {ctx['year']}")
    ax.set_xlim(x[0], x[-1])

    return fig, df
