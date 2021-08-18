"""Plot Time Series for Sounding Parameter."""
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"00": "00 UTC", "12": "12 UTC"}
PDICT3 = dict(
    [
        ("tmpc", "Air Temperature (C)"),
        ("dwpc", "Dew Point (C)"),
        ("el_agl_m", "Equalibrium Level (m AGL)"),
        ("el_pressure_hpa", "Equalibrium Pressure (hPa)"),
        ("el_tmpc", "Equalibrium Level Temperature (C)"),
        ("height", "Height (m)"),
        ("lcl_agl_m", "Lifted Condensation Level (m AGL)"),
        ("lcl_pressure_hpa", "Lifted Condensation Level (hPa)"),
        ("lcl_tmpc", "Lifted Condensation Level Temperature (C)"),
        ("lfc_agl_m", "Lifted of Free Convection (m AGL)"),
        ("lfc_pressure_hpa", "Lifted of Free Convection (hPa)"),
        ("lfc_tmpc", "Lifted of Free Convection Temperature (C)"),
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
        ("total_totals", "Total Totals (C)"),
        ("smps", "Wind Speed (mps)"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
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
    pgconn = get_dbconn("raob")
    if varname in ["tmpc", "dwpc", "height", "smps"]:
        ctx["leveltitle"] = f" @ {level} hPa"
        dfin = read_sql(
            "select extract(year from f.valid at time zone 'UTC') as year, "
            "to_char(f.valid at time zone 'UTC', 'mmdd') as sday, "
            f"{varname} from raob_profile p JOIN raob_flights f on "
            "(p.fid = f.fid) WHERE f.station in %s and p.pressure = %s and "
            "extract(hour from f.valid at time zone 'UTC') = %s and "
            f"{varname} is not null ORDER by valid ASC",
            pgconn,
            params=(tuple(stations), level, hour),
            index_col=None,
        )
    else:
        ctx["leveltitle"] = ""
        dfin = read_sql(
            "select extract(year from valid at time zone 'UTC') as year, "
            "to_char(valid at time zone 'UTC', 'mmdd') as sday, "
            f"{varname} from raob_flights WHERE station in %s and "
            "extract(hour from valid at time zone 'UTC') = %s and "
            f"{varname} is not null ORDER by valid ASC",
            pgconn,
            params=(tuple(stations), hour),
        )
    if dfin.empty:
        raise NoDataFound("No Data Found.")
    # Drop leapday if this year does not have it.
    try:
        datetime.date(ctx["year"], 2, 29)
    except ValueError:
        dfin = dfin[dfin["sday"] != "0229"]
    # Create a timestamp for this year
    dfin["date"] = pd.to_datetime(
        str(ctx["year"]) + dfin["sday"].astype(str), format="%Y%m%d"
    )
    # create the climatology dataframe
    df = dfin[["date", ctx["var"]]].groupby("date").describe()
    # Merge in this year's obs
    df[f"{ctx['var']}_{ctx['year']}"] = dfin[
        dfin["year"] == ctx["year"]
    ].set_index("date")[ctx["var"]]
    ctx["df"] = df

    ctx["title"] = "%s %s %02i UTC Sounding\n%s %s" % (
        station,
        name,
        hour,
        PDICT3[varname],
        ctx["leveltitle"],
    )


def highcharts(fdict):
    """Make highcharts output."""
    ctx = get_autoplot_context(fdict, get_description())
    get_data(ctx)
    ticks = (ctx["df"].index.astype("int64") // 1e6).tolist()
    j = dict()
    j["title"] = dict(text=ctx["title"])
    j["exporting"] = {"enabled": True}
    j["chart"] = {"zoomType": "x"}
    j["plotOptions"] = {"line": {"turboThreshold": 0}}
    j["xAxis"] = dict(type="datetime")
    j["yAxis"] = dict(title=dict(text=PDICT3[ctx["var"]]))
    units = PDICT3[ctx["var"]].split()[-1]
    j["tooltip"] = {
        "crosshairs": True,
        "shared": True,
        "valueSuffix": f" {units}",
        "valueDecimals": 2,
    }

    myyearcol = f"{ctx['var']}_{ctx['year']}"
    j["series"] = [
        {
            "name": PDICT3[ctx["var"]],
            "data": list(zip(ticks, ctx["df"][myyearcol].values.tolist())),
            "zIndex": 3,
            "color": "#FF0000",
            "lineWidth": 2,
            "marker": {"enabled": False},
            "type": "line",
        },
        {
            "name": "Average",
            "data": list(
                zip(ticks, ctx["df"][ctx["var"], "mean"].values.tolist())
            ),
            "zIndex": 2,
            "color": "#000000",
            "lineWidth": 2,
            "marker": {"enabled": False},
            "type": "line",
        },
        {
            "name": "Range",
            "data": list(
                zip(
                    ticks,
                    ctx["df"][ctx["var"], "min"].values.tolist(),
                    ctx["df"][ctx["var"], "max"].values.tolist(),
                )
            ),
            "type": "arearange",
            "lineWidth": 0,
            "linkedTo": ":previous",
            "color": "#ADD8E6",
            "fillOpacity": 0.3,
            "zIndex": 0,
        },
        {
            "name": "25-75 %tile",
            "data": list(
                zip(
                    ticks,
                    ctx["df"][ctx["var"], "25%"].values.tolist(),
                    ctx["df"][ctx["var"], "75%"].values.tolist(),
                )
            ),
            "type": "arearange",
            "lineWidth": 0,
            "linkedTo": ":previous",
            "color": "#D2B48C",
            "fillOpacity": 0.3,
            "zIndex": 0,
        },
    ]

    return j


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    get_data(ctx)
    df = ctx["df"]
    fig, ax = plt.subplots(1, 1)
    colname = f"{ctx['var']}_{ctx['year']}"
    x = df.index.values
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
    ax.legend()
    ax.set_ylabel(PDICT3[ctx["var"]])
    plt.gcf().text(0.5, 0.9, ctx["title"], ha="center", va="bottom")
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="KABR", var="tmpc", level=500))
