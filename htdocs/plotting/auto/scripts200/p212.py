"""Plot Time Series for Sounding Parameter."""
import datetime

import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

PDICT = {"00": "00 UTC", "12": "12 UTC"}
PDICT3 = dict(
    [
        ("tmpc", "Air Temperature (°C)"),
        ("dwpc", "Dew Point (°C)"),
        ("el_agl_m", "Equalibrium Level (m AGL)"),
        ("el_pressure_hpa", "Equalibrium Pressure (hPa)"),
        ("el_tmpc", "Equalibrium Level Temperature (°C)"),
        ("height", "Height (m)"),
        ("lcl_agl_m", "Lifted Condensation Level (m AGL)"),
        ("lcl_pressure_hpa", "Lifted Condensation Level (hPa)"),
        ("lcl_tmpc", "Lifted Condensation Level Temperature (°C)"),
        ("lfc_agl_m", "Lifted of Free Convection (m AGL)"),
        ("lfc_pressure_hpa", "Lifted of Free Convection (hPa)"),
        ("lfc_tmpc", "Lifted of Free Convection Temperature (°C)"),
        ("mlcape_jkg", "Mixed Layer (100hPa) CAPE (J/kg)"),
        ("mlcin_jkg", "Mixed Layer (100hPa) CIN (J/kg)"),
        ("mucape_jkg", "Most Unstable CAPE (J/kg)"),
        ("mucin_jkg", "Most Unstable CIN (J/kg)"),
        ("pwater_mm", "Precipitable Water (mm)"),
        ("shear_sfc_1km_smps", "Shear 0-1km AGL Magnitude (m/s)"),
        ("shear_sfc_3km_smps", "Shear 0-3km AGL Magnitude (m/s)"),
        ("shear_sfc_6km_smps", "Shear 0-6km AGL Magnitude (m/s)"),
        (
            "srh_sfc_1km_neg",
            "Storm Relative Helicity Negative (0-1km) (m2/s2)",
        ),
        (
            "srh_sfc_1km_pos",
            "Storm Relative Helicity Positive (0-1km) (m2/s2)",
        ),
        ("srh_sfc_1km_total", "Storm Relative Helicity Total (0-1km) (m2/s2)"),
        (
            "srh_sfc_3km_neg",
            "Storm Relative Helicity Negative (0-3km) (m2/s2)",
        ),
        (
            "srh_sfc_3km_pos",
            "Storm Relative Helicity Positive (0-3km) (m2/s2)",
        ),
        ("srh_sfc_3km_total", "Storm Relative Helicity Total (0-3km) (m2/s2)"),
        ("sbcape_jkg", "Surface Based CAPE (J/kg)"),
        ("sbcin_jkg", "Surface Based CIN (J/kg)"),
        ("sweat_index", "Sweat Index"),
        ("total_totals", "Total Totals (°C)"),
        ("smps", "Wind Speed (mps)"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["highcharts"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents the daily climatology range of a sounding
    variable along with a given year's values.

    <p>The Storm Prediction Center website has a
    <a href="https://www.spc.noaa.gov/exper/soundingclimo/">
    very similiar tool</a> that you may want to check out.</p>
    """
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
    hour = int(ctx["hour"])
    level = ctx["level"]
    if varname in ["tmpc", "dwpc", "height", "smps"]:
        ctx["leveltitle"] = f" @ {level} hPa"
        with get_sqlalchemy_conn("raob") as conn:
            dfin = pd.read_sql(
                text(
                    "select "
                    "extract(year from f.valid at time zone 'UTC')::int "
                    "as year, f.valid at time zone 'UTC' as utc_valid, "
                    f"{varname} from raob_profile p JOIN raob_flights f on "
                    "(p.fid = f.fid) WHERE f.station in :stations "
                    "and p.pressure = :level and "
                    "extract(hour from f.valid at time zone 'UTC') = :hour "
                    f"and {varname} is not null ORDER by valid ASC"
                ),
                conn,
                params={
                    "stations": tuple(stations),
                    "level": level,
                    "hour": hour,
                },
                index_col="utc_valid",
            )
    else:
        ctx["leveltitle"] = ""
        with get_sqlalchemy_conn("raob") as conn:
            dfin = pd.read_sql(
                text(
                    "select "
                    "extract(year from valid at time zone 'UTC')::int "
                    "as year, valid at time zone 'UTC' as utc_valid, "
                    f"{varname} from raob_flights WHERE station in :stations "
                    "and extract(hour from valid at time zone 'UTC') = :hour "
                    f"and {varname} is not null ORDER by valid ASC"
                ),
                conn,
                params={"stations": tuple(stations), "hour": hour},
                index_col="utc_valid",
            )
    if dfin.empty:
        raise NoDataFound("No Data Found.")
    dfin["sday"] = dfin.index.strftime("%m%d")
    # Drop leapday if this year does not have it.
    try:
        datetime.date(ctx["year"], 2, 29)
    except ValueError:
        dfin = dfin[dfin["sday"] != "0229"]
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
        str(ctx["year"]) + df.index + f"{hour:02.0f}",
        format="%Y%m%d%H",
    ).tz_localize("UTC")
    ctx["df"] = df

    ctx["title"] = (
        f"{station} {name} {hour:02.0f} UTC Sounding ({dfin['year'].min()} - "
        f"{dfin['year'].max()})\n"
        f"{PDICT3[varname]} {ctx['leveltitle']}"
    )


def highcharts(fdict):
    """Make highcharts output."""
    ctx = get_autoplot_context(fdict, get_description())
    get_data(ctx)
    df = ctx["df"]
    df["ticks"] = df["utc_valid"].view("int64") // 1e6
    units = PDICT3[ctx["var"]].split()[-1].replace("(", "").replace(")", "")
    myyearcol = f"{ctx['var']}_{ctx['year']}"
    title = ctx["title"].replace("\n", "\\n")
    tc = ("ticks", "")
    mx = df[f"{ctx['var']}_max_year"]
    mn = df[f"{ctx['var']}_min_year"]
    res = f"""
    var max_years = {mx.values.tolist()};
    var min_years = {mn.values.tolist()};

    $("#ap_container").highcharts({{
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
                            '">\u25CF</span> '+
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
    ymax = ax.get_ylim()[1]
    dy = ymax * 0.01
    # Figure out the monthly max values
    mmax = df[ctx["var"], "max"].reset_index()
    mmax["month"] = mmax["sday"].str.slice(0, 2)
    mmax = mmax.drop(columns="sday").groupby("month").max()
    mmax.columns = [
        "max",
    ]
    for month, row in mmax.iterrows():
        sts = datetime.date(ctx["year"], int(month), 1)
        ets = (sts + datetime.timedelta(days=35)).replace(day=1)
        ax.plot([sts, ets], [row["max"], row["max"]], zorder=3, color="b")
        ax.text(
            sts + datetime.timedelta(days=15),
            row["max"] + dy,
            f"{row['max']:.2f}",
            ha="center",
        )

    mmin = df[ctx["var"], "min"].reset_index()
    mmin["month"] = mmin["sday"].str.slice(0, 2)
    mmin = mmin.drop(columns="sday").groupby("month").min()
    mmin.columns = [
        "min",
    ]
    for month, row in mmin.iterrows():
        sts = datetime.date(ctx["year"], int(month), 1)
        ets = (sts + datetime.timedelta(days=35)).replace(day=1)

        ax.plot([sts, ets], [row["min"], row["min"]], zorder=3, color="b")
        ax.text(
            sts + datetime.timedelta(days=15),
            row["min"] - dy,
            f"{row['min']:.2f}",
            ha="center",
            va="top",
        )
    ax.legend()
    ax.set_ylabel(PDICT3[ctx["var"]])
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.set_xlabel(f"Day of {ctx['year']}")

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="KABR", var="tmpc", level=500, hour="12"))
