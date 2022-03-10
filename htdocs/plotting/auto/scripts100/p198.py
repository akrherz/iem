"""Monthly Sounding Averages"""
import datetime

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

PDICT = {"00": "00 UTC", "12": "12 UTC", "ALL": "Any Hour"}
MDICT = dict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("mjj", "May/June/July"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)
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
PDICT4 = {"min": "Minimum", "avg": "Average", "max": "Maximum"}
PDICT5 = {
    "no": "Plot All Available Data",
    "yes": "Only Plot Years with ~75% Data Availability",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents a simple average of a given
    sounding variable of your choice.  If the selected month period crosses
    a calendar year, the year shown is for the January included in the period.

    <br /><br />The 'Select Station' option provides some 'virtual' stations
    that are spliced together archives of close by stations.  For some
    locations, the place that the sounding is made has moved over the years..

    <br /><br />
    <strong>Some derived parameters are a work-in-progress.</strong>
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
            type="select",
            name="hour",
            default="00",
            options=PDICT,
            label="Which Routine Sounding:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="select",
            name="agg",
            default="avg",
            options=PDICT4,
            label="Which Statistical Aggregate to Plot:",
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
        dict(
            type="select",
            name="quorum",
            default="yes",
            options=PDICT5,
            label="Should there be a quorum check before plotting?",
        ),
    ]
    return desc


def compute(dfin, varname):
    """Compute our needed yearly aggregates."""
    if dfin.empty:
        raise NoDataFound("No Data Found")
    # create final DataFrame holding our agg computations
    df = dfin.groupby("year").agg(["min", "mean", "max", "count"]).copy()
    df.columns = df.columns.map("_".join)
    df = df.rename({f"{varname}_mean": f"{varname}_avg"}, axis=1)
    # compute the min and max value timestamps
    for year, df2 in dfin.groupby("year"):
        for agg in ["min", "max"]:
            rows = df2[df2[varname] == df.at[year, f"{varname}_{agg}"]]
            vals = []
            for _i, row in rows.iterrows():
                vals.append(row["utc_valid"].strftime("%Y-%m-%d %H:%M"))
            extra = "" if len(vals) < 5 else ";+ %s more" % (len(vals) - 4,)
            df.at[year, f"{varname}_{agg}_valid"] = "; ".join(vals[:4]) + extra
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    if station not in ctx["_nt"].sts:  # This is needed.
        raise NoDataFound("Unknown station metadata.")
    varname = ctx["var"]
    hour = ctx["hour"]
    if hour != "ALL":
        hour = int(hour)
    month = ctx["month"]
    level = ctx["level"]
    agg = ctx["agg"]
    offset = 0
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
        offset = 32
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "mjj":
        months = [5, 6, 7]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    name = ctx["_nt"].sts[station]["name"]
    stations = [station]
    if station.startswith("_"):
        name = ctx["_nt"].sts[station]["name"].split("--")[0]
        stations = (
            ctx["_nt"].sts[station]["name"].split("--")[1].strip().split(" ")
        )

    hrlimiter = f" extract(hour from f.valid at time zone 'UTC') = {hour} and "
    if hour == "ALL":
        hrlimiter = ""
    yrcol = f"extract(year from f.valid + '{offset:0d} days'::interval)::int"
    if varname in ["tmpc", "dwpc", "height", "smps"]:
        leveltitle = " @ %s hPa" % (level,)
        with get_sqlalchemy_conn("raob") as conn:
            dfin = pd.read_sql(
                text(
                    f"""
                select {yrcol} as year, {varname},
                valid at time zone 'UTC' as utc_valid
                from raob_profile p JOIN raob_flights f on (p.fid = f.fid)
                WHERE f.station in :stations and p.pressure = :level
                and {hrlimiter} extract(month from f.valid) in :months
                and {varname} is not null
            """
                ),
                conn,
                params={
                    "stations": tuple(stations),
                    "level": level,
                    "months": tuple(months),
                },
            )
    else:
        leveltitle = ""
        with get_sqlalchemy_conn("raob") as conn:
            dfin = pd.read_sql(
                text(
                    f"""
                select {yrcol} as year, {varname}, valid at time zone 'UTC'
                as utc_valid from raob_flights f WHERE f.station in :stations
                and {hrlimiter} extract(month from f.valid) in :months and
                {varname} is not null
            """
                ),
                conn,
                params={
                    "stations": tuple(stations),
                    "months": tuple(months),
                },
            )
    df = compute(dfin, varname)
    if ctx["quorum"] == "yes":
        # need quorums
        df = df[df[f"{varname}_count"] > ((len(months) * 28) * 0.75)]
    if df.empty:
        raise NoDataFound("No data was found!")
    colname = f"{varname}_{agg}"
    title = "%s %s %s Sounding" % (
        station,
        name,
        f"{hour:02d} UTC" if hour != "ALL" else PDICT[hour],
    )
    subtitle = "%s %s%s over %s" % (
        PDICT4[agg],
        PDICT3[varname],
        leveltitle,
        MDICT[month],
    )
    fig, ax = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    avgv = df[colname].mean()
    bars = ax.bar(df.index.values, df[colname], align="center")
    for i, _bar in enumerate(bars):
        val = df.iloc[i][colname]
        if val < avgv:
            _bar.set_color("blue")
        else:
            _bar.set_color("red")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    rng = df[colname].max() - df[colname].min()
    ax.set_ylim(df[colname].min() - rng * 0.1, df[colname].max() + rng * 0.1)
    ax.axhline(avgv, color="k")
    ax.text(df.index.values[-1] + 2, avgv, "Avg:\n%.1f" % (avgv,))
    ax.set_xlabel("Year")
    ax.set_ylabel("%s %s%s" % (PDICT4[agg], PDICT3[varname], leveltitle))
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="_CRP", month="mjj", var="mlcape_jkg", agg="avg"))
