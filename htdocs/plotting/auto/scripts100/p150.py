"""sounding stuff"""
import calendar

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.exceptions import NoDataFound

PDICT = {"00": "00 UTC", "12": "12 UTC"}
PDICT2 = {
    "none": "No Comparison Limit (All Soundings)",
    "month": "Month of the Selected Profile",
}
PDICT3 = dict(
    [
        ("tmpc", "Air Temperature (C)"),
        ("dwpc", "Dew Point (C)"),
        ("hght", "Height (m)"),
        ("smps", "Wind Speed (mps)"),
    ]
)
PDICT4 = {
    "same": "Compare against soundings for same hour",
    "all": "Compare against soundings at any hour",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """
    This plot presents percentiles of observations from
    a given sounding profile against the long term record for the site. These
    percentiles are computed against all other soundings for the valid hour of
    the profile of interest.  For example, a 00 UTC sounding is only compared
    against other 00 UTC soundings for the given month or for the period of
    record.

    <br /><br />The 'Select Station' option provides some 'virtual' stations
    that are spliced together archives of close by stations.  For some
    locations, the place that the sounding is made has moved over the years.

    <br /><br />A process runs at 3:10 and 15:10z each day to ingest the
    current 0 and 12z soundings respectively.  You may not find the current
    day's sounding if running this application prior to those ingest times.
    """
    today = utc()
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="RAOB",
            default="_OAX",
            label="Select Station:",
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            min="1946/01/01",
            max=today.strftime("%Y/%m/%d"),
            label="Date of the Sounding:",
        ),
        dict(
            type="select",
            name="hour",
            default="00",
            options=PDICT,
            label="Which Sounding from Above Date:",
        ),
        dict(
            type="select",
            name="which",
            default="month",
            options=PDICT2,
            label="Compare this sounding against (dates):",
        ),
        dict(
            type="select",
            name="h",
            default="same",
            options=PDICT4,
            label="Compare this sounding against (hour):",
        ),
        dict(
            type="select",
            name="var",
            default="tmpc",
            options=PDICT3,
            label="Which Sounding Variable to Plot:",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    if station not in ctx["_nt"].sts:  # This is needed.
        raise NoDataFound("Unknown station metadata.")
    varname = ctx["var"]
    ts = ctx["date"]
    hour = int(ctx["hour"])
    ts = utc(ts.year, ts.month, ts.day, hour)
    which = ctx["which"]
    vlimit = ""
    if which == "month":
        vlimit = (" and extract(month from f.valid) = %s ") % (ts.month,)
    name = ctx["_nt"].sts[station]["name"]
    stations = [station]
    if station.startswith("_"):
        name = ctx["_nt"].sts[station]["name"].split("--")[0]
        stations = (
            ctx["_nt"].sts[station]["name"].split("--")[1].strip().split(" ")
        )
    pgconn = get_dbconn("raob")

    hrlimit = f"and extract(hour from f.valid at time zone 'UTC') = {hour} "
    if ctx["h"] == "ALL":
        hrlimit = ""
    df = read_sql(
        f"""
    with data as (
        select f.valid,
        p.pressure, count(*) OVER (PARTITION by p.pressure),
        min(valid at time zone 'UTC') OVER () as min_valid,
        max(valid at time zone 'UTC') OVER () as max_valid,
        p.tmpc,
        rank() OVER (PARTITION by p.pressure ORDER by p.tmpc ASC) as tmpc_rank,
        min(p.tmpc) OVER (PARTITION by p.pressure) as tmpc_min,
        max(p.tmpc) OVER (PARTITION by p.pressure) as tmpc_max,
        p.dwpc,
        rank() OVER (PARTITION by p.pressure ORDER by p.dwpc ASC) as dwpc_rank,
        min(p.dwpc) OVER (PARTITION by p.pressure) as dwpc_min,
        max(p.dwpc) OVER (PARTITION by p.pressure) as dwpc_max,
        p.height as hght,
        rank() OVER (
            PARTITION by p.pressure ORDER by p.height ASC) as hght_rank,
        min(p.height) OVER (PARTITION by p.pressure) as hght_min,
        max(p.height) OVER (PARTITION by p.pressure) as hght_max,
        p.smps,
        rank() OVER (PARTITION by p.pressure ORDER by p.smps ASC) as smps_rank,
        min(p.smps) OVER (PARTITION by p.pressure) as smps_min,
        max(p.smps) OVER (PARTITION by p.pressure) as smps_max
        from raob_flights f JOIN raob_profile p on (f.fid = p.fid)
        WHERE f.station in %s {hrlimit} {vlimit}
        and p.pressure in (925, 850, 700, 500, 400, 300, 250, 200,
        150, 100, 70, 50, 10))

    select * from data where valid = %s ORDER by pressure DESC
    """,
        pgconn,
        params=(tuple(stations), ts),
        index_col="pressure",
    )
    if df.empty:
        raise NoDataFound(
            ("Sounding for %s was not found!")
            % (ts.strftime("%Y-%m-%d %H:%M"),)
        )
    df = df.drop("valid", axis=1)
    for key in PDICT3.keys():
        df[key + "_percentile"] = df[key + "_rank"] / df["count"] * 100.0
        # manual hackery to get 0 and 100th percentile
        df.loc[df[key] == df[key + "_max"], key + "_percentile"] = 100.0
        df.loc[df[key] == df[key + "_min"], key + "_percentile"] = 0.0

    title = "%s %s %s Sounding" % (
        station,
        name,
        ts.strftime("%Y/%m/%d %H UTC"),
    )
    subtitle = "(%s-%s) Percentile Ranks (%s) for %s at %s" % (
        pd.Timestamp(df.iloc[0]["min_valid"]).year,
        pd.Timestamp(df.iloc[0]["max_valid"]).year,
        ("All Year" if which == "none" else calendar.month_name[ts.month]),
        PDICT3[varname],
        "Any Hour" if ctx["h"] == "all" else f"{hour} UTC",
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.75, 0.78])
    bars = ax.barh(
        range(len(df.index)), df[varname + "_percentile"], align="center"
    )
    y2labels = []
    fmt = "%.1f" if varname not in ["hght"] else "%.0f"
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_width() + 1,
            i,
            "%.1f" % (mybar.get_width(),),
            va="center",
            bbox=dict(color="white"),
        )
        y2labels.append(
            (fmt + " (" + fmt + " " + fmt + ")")
            % (
                df.iloc[i][varname],
                df.iloc[i][varname + "_min"],
                df.iloc[i][varname + "_max"],
            )
        )
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(["%.0f" % (a,) for a in df.index.values])
    ax.set_ylim(-0.5, len(df.index) - 0.5)
    ax.set_xlabel("Percentile [100 = highest]")
    ax.set_ylabel("Mandatory Pressure Level (hPa)")
    ax.grid(True)
    ax.set_xticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_xlim(0, 110)
    ax.text(1.02, 1, "Ob  (Min  Max)", transform=ax.transAxes)

    ax2 = ax.twinx()
    ax2.set_ylim(-0.5, len(df.index) - 0.5)
    ax2.set_yticks(range(len(df.index)))
    ax2.set_yticklabels(y2labels)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
